/* LICENSE BEGIN

Copyright (c) 2010 Ysj.Ray

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

 LICENSE END */


#include "pyproxy-plugin.h"
#include "network-mysqld-python.h"
#include "pytypes.h"

#ifdef HAVE_SYS_FILIO_H
/**
 * required for FIONREAD on solaris
 */
#include <sys/filio.h>
#endif

#include <mysql.h>
#include <mysqld_error.h>
#include <stdio.h>
#include <stdarg.h>
#include <assert.h>

#ifndef _WIN32
#include <sys/ioctl.h>

#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#define ioctlsocket ioctl
#endif

#include <errno.h>
#include "glib-ext.h"

#include "network-mysqld.h"
#include "network-mysqld-packet.h"
#include "chassis-event-thread.h"
#include "network-conn-pool.h"
#include "network-conn-pool-lua.h"

#define MAX_PATH_LENGTH 1024


#define C(x) x, sizeof(x) - 1


/**
  * Most function return 0 on success, -1 on error.
  */

extern PyObject *proxy_constants;

int network_mysqld_python_initialize(chassis_plugin_config *config){
    PyObject *path = PySys_GetObject("path");

    if(!config->python_script){
		g_message("No avalible python script.");
		return 0;
	}

	if(init_python_types()){
		PyErr_Print();
		PyErr_Clear();
		return -1;
	}
	//TODO
	//Here initialize globals object and the builtin proxy object.

    PyObject *script = PyString_FromString(config->python_script);
    PyObject *split_path = PyObject_CallMethod(script, "rsplit", "si", "/", 1);
    Py_DECREF(script);

    Py_ssize_t length = PyList_GET_SIZE(split_path);
    assert(length == 2);
    PyList_Append(path, PyList_GetItem(split_path, 0));

    {
		// Add current dir to sys.path.
		char path_buf[MAX_PATH_LENGTH];
		char* result = getcwd(path_buf, MAX_PATH_LENGTH);
		if(result){
			PyObject *curr_path = PyString_FromString(path_buf);
			g_message("Add %s to sys.path\n", path_buf);
			PyList_Append(path, curr_path);
			Py_DECREF(curr_path);
		}
		else{
			g_critical("Script file path is too long! Max length is %d\n", MAX_PATH_LENGTH);
			return -1;
		}
	}

	{
		//Now load the script
		PyObject *file_name = PyList_GetItem(split_path, length - 1);
		PyObject *split_file_name= PyObject_CallMethod(file_name, "split",
					"si", ".", 1);
		PyObject *mod_name = PyList_GetItem(split_file_name, 0);
		PyObject *script_mod = PyImport_Import(mod_name);
		if(!script_mod){
			PyObject *exc_type = PyErr_Occurred();
			if(exc_type){
				PyErr_Print();
				PyErr_Clear();
			}
			else{
				g_critical("Unknown error occurred while importing script %s\n",
							PyString_AsString(mod_name));
			}
			return -1;
		}
		config->proxy_funcs = g_new0(pyproxy_functions, 1);
		if(!config->proxy_funcs){
			g_critical("No memory avaible for alloc proxy functions!\n");
			return -1;
		}

		//Load the script hook function to config->proxy_methods.
#define LOAD_FUNC(func) \
		config->proxy_funcs->func = NULL;\
		if(PyObject_HasAttrString(script_mod, #func)){\
			PyObject *fun = PyObject_GetAttrString(script_mod, #func);\
			if(PyCallable_Check(fun)){\
				config->proxy_funcs->func = fun;\
			}\
			else{\
				PyObject *func_name = PyObject_Str(mod_name);\
				g_message("Load %s.%s failed: object %s is not callable!\n", \
					PyString_AsString(func_name), #func, #func);\
				Py_DECREF(func_name);\
			}\
		}

		LOAD_FUNC(init)
		LOAD_FUNC(connect_server)
		LOAD_FUNC(read_handshake)
		LOAD_FUNC(read_auth)
		LOAD_FUNC(read_auth_result)
		LOAD_FUNC(read_query)
		LOAD_FUNC(read_query_result)
		LOAD_FUNC(disconnect_client)

		Py_DECREF(script_mod);
		Py_DECREF(split_file_name);
	}

    Py_DECREF(split_path);
	return 0;
}


network_mysqld_con_python_t *network_mysqld_con_python_new() {
	network_mysqld_con_python_t *st;

	st = g_new0(network_mysqld_con_python_t, 1);

	st->injected.queries = network_injection_queue_new();

	return st;
}

/**
 * handle the events of a idling server connection in the pool 
 *
 * make sure we know about connection close from the server side
 * - wait_timeout
 */
static void network_mysqld_con_idle_handle(int event_fd, short events, void *user_data) {
	network_connection_pool_entry *pool_entry = user_data;
	network_connection_pool *pool             = pool_entry->pool;

	if (events == EV_READ) {
		int b = -1;

		/**
		 * @todo we have to handle the case that the server really sent use something
		 *        up to now we just ignore it
		 */
		if (ioctlsocket(event_fd, FIONREAD, &b)) {
			g_critical("ioctl(%d, FIONREAD, ...) failed: %s", event_fd, g_strerror(errno));
		} else if (b != 0) {
			g_critical("ioctl(%d, FIONREAD, ...) said there is something to read, oops: %d", event_fd, b);
		} else {
			/* the server decided the close the connection (wait_timeout, crash, ... )
			 *
			 * remove us from the connection pool and close the connection */
		
			network_connection_pool_remove(pool, pool_entry);
		}
	}
}

int network_connection_pool_python_add_connection(network_mysqld_con *con) {
	network_connection_pool_entry *pool_entry = NULL;
	network_mysqld_con_python_t *st = con->plugin_con_state;

	/* con-server is already disconnected, got out */
	if (!con->server) return 0;

	/* the server connection is still authed */
	con->server->is_authed = 1;

	/* insert the server socket into the connection pool */
	pool_entry = network_connection_pool_add(st->backend->pool, con->server);

	event_set(&(con->server->event), con->server->fd, EV_READ, network_mysqld_con_idle_handle, pool_entry);
	chassis_event_add_local(con->srv, &(con->server->event)); /* add a event, but stay in the same thread */

	st->backend->connected_clients--;
	st->backend = NULL;
	st->backend_ndx = -1;

	con->server = NULL;

	return 0;
}


void network_mysqld_con_python_free(network_mysqld_con_python_t *st) {
	if (!st) return;

	network_injection_queue_free(st->injected.queries);

	if(st->globals){
		Py_DECREF(st->globals);
	}

	g_free(st);
}


network_socket *network_connection_pool_python_swap(network_mysqld_con *con, int backend_ndx) {
	network_backend_t *backend = NULL;
	network_socket *send_sock;
	network_mysqld_con_python_t *st = con->plugin_con_state;
	chassis_private *g = con->srv->priv;
	GString empty_username = { "", 0, 0 };

	/*
	 * we can only change to another backend if the backend is already
	 * in the connection pool and connected
	 */

	backend = network_backends_get(g->backends, backend_ndx);
	if (!backend) return NULL;


	/**
	 * get a connection from the pool which matches our basic requirements
	 * - username has to match
	 * - default_db should match
	 */

#ifdef DEBUG_CONN_POOL
	g_debug("%s: (swap) check if we have a connection for this user in the pool '%s'", G_STRLOC, con->client->username->str);
#endif
	if (NULL == (send_sock = network_connection_pool_get(backend->pool, 
					con->client->response ? con->client->response->username : &empty_username,
					con->client->default_db))) {
		/**
		 * no connections in the pool
		 */
		st->backend_ndx = -1;
		return NULL;
	}

	/* the backend is up and cool, take and move the current backend into the pool */
#ifdef DEBUG_CONN_POOL
	g_debug("%s: (swap) added the previous connection to the pool", G_STRLOC);
#endif
	network_connection_pool_python_add_connection(con);

	/* connect to the new backend */
	st->backend = backend;
	st->backend->connected_clients++;
	st->backend_ndx = backend_ndx;

	return send_sock;
}


static MYSQL_FIELD *create_field(PyObject *item){
	assert(item);
	// each item should be a two-size tuple or list.
	if(!PySequence_Check(item) || PySequence_Size(item) != 2){
		PyErr_FormatObject(PyExc_ValueError, "field item %s should be a two-size "
				"sequence.", item);
		return NULL;
	}
	PyObject *item_type = PySequence_GetItem(item, 1);
	PyObject *item_name = PySequence_GetItem(item, 0);
	if(!item_type || !PyInt_Check(item_type)){
		PyErr_SetString(PyExc_ValueError, "field type should be a int");
		Py_XDECREF(item_type);
		return NULL;
	}
	if(!item_name || !PyString_Check(item_name)){
		PyErr_SetString(PyExc_ValueError, "field name should be a string");
		Py_XDECREF(item_name);
		return NULL;
	}
	MYSQL_FIELD *field = network_mysqld_proto_fielddef_new();
	//TODO check the type value.
	field->type = PyInt_AsLong(item_type);
	field->name = g_strdup(PyString_AsString(item_name));
	field->flags = PRI_KEY_FLAG;
	field->length = 32;

	Py_DECREF(item_type);
	Py_DECREF(item_name);
	return field;
}


static GPtrArray *create_fields(PyObject *resultset){
	assert(resultset);
	if(!PyDict_Check(resultset)){
		PyErr_SetString(PyExc_ValueError, "response.resultset must be a dict");
		return NULL;
	}
	PyObject *res_fields = PyDict_GetItemString(resultset, "fields");
	if(!res_fields){
		PyErr_SetString(PyExc_KeyError, "resultset has no key named 'fields'!");
		return NULL;
	}
	if(!PySequence_Check(res_fields)){
		PyErr_SetString(PyExc_ValueError, "proxy.response.resultset.fields should be eigher a "
					"list or a tuple");
		return NULL;
	}
	GPtrArray *fields = network_mysqld_proto_fielddefs_new();
	int i;
	for(i = 0; i < PySequence_Size(res_fields); i++){
		PyObject *item = PySequence_GetItem(res_fields, i);
		if(!item){
			network_mysqld_proto_fielddefs_free(fields);
			g_critical("Create item failed");
			return NULL;
		}
		MYSQL_FIELD *field = create_field(item);
		Py_DECREF(item);

		if(!field){
			network_mysqld_proto_fielddefs_free(fields);
			g_critical("Create fields failed");
			return NULL;
		}
		g_ptr_array_add(fields, field);
	}
	return fields;
}


static void g_ptr_array_clear(GPtrArray *array){
	int i;
	for(i = 0; i < array->len; i++){
		if(array->pdata[i])
			g_free(array->pdata[i]);
	}
	g_ptr_array_free(array, TRUE);
}

static void g_ptr_array_clear_r(GPtrArray *array){
	int i;
	for(i = 0; i < array->len; i++){
		if(array->pdata[i])
			g_ptr_array_clear(array->pdata[i]);
	}
	g_ptr_array_free(array, TRUE);
}

static GPtrArray *create_row(PyObject *item){
	assert(item);
	GPtrArray *row = g_ptr_array_new();
	if(!row)
		return NULL;
	int i;
	for(i = 0; i < PySequence_Size(item); i++){
		PyObject *elem = PySequence_GetItem(item, i);
		if(!elem)
			goto failed;
		/*
		if(!PySequence_Check(elem)){
			PyErr_SetString(PyExc_ValueError, "proxy.response.resultset.rows' items should "
						"be eigher lists or tuples");
			Py_DECREF(elem);
			goto failed;
		}
		*/
		PyObject *elem_str = PyObject_Str(elem);
		Py_DECREF(elem);
		if(!elem_str)
			goto failed;
		g_ptr_array_add(row, g_strdup(PyString_AsString(elem_str)));
		Py_DECREF(elem_str);
	}
	return row;

failed:
	g_ptr_array_clear(row);
	return NULL;
}

static GPtrArray *create_rows(PyObject *resultset){
	assert(resultset);
	//Now the resultset has been checked in create_fields.
	PyObject *res_rows = PyDict_GetItemString(resultset, "rows");
	if(!res_rows)
		return NULL;
	if(!PySequence_Check(res_rows)){
		PyErr_SetString(PyExc_ValueError, "proxy.response.resultset.rows .."
					" should be a sequence");
		return NULL;
	}
	GPtrArray *rows = g_ptr_array_new();
	int i = 0;
	for(i = 0; i < PySequence_Size(res_rows); i++){
		PyObject *item = PySequence_GetItem(res_rows, i);
		if(!item)
			goto failed;
		if(!PySequence_Check(item)){
			PyErr_SetString(PyExc_ValueError, "proxy.response.resultset.rows' "
						"items should be sequences");
			Py_DECREF(item);
			goto failed;
		}
		GPtrArray *row = create_row(item);
		Py_DECREF(item);
		if(!row)
			goto failed;
		g_ptr_array_add(rows, row);
	}
	return rows;

failed:
	g_ptr_array_clear_r(rows);
	return NULL;
}

/**
 * Handle the proxy.response to con.
 * proxy.response
 *   .type can be either ERR, OK or RAW
 *   .resultset (in case of OK)
 *     .fields
 *     .rows
 *   .errmsg (in case of ERR)
 *   .packet (in case of nil)
 *  Note: if error occurred, should set the error string.
 */
int network_mysqld_con_python_handle_proxy_response(network_mysqld_con *con, PyObject *proxy){
	assert(proxy);
	//network_mysqld_con_python_t *st = con->plugin_con_state;

	PyObject *response = PyObject_GetAttrString(proxy, "response");
	//Note: the response is fetched through the tp_getset, and is a new reference.
	assert(response);
	Py_DECREF(response);

	PyObject *res_type = PyObject_GetAttrString(response, "type");
	if(!res_type){
		network_mysqld_con_send_error(con->client, C("Cannot get proxy.response.type"));
		return -1;
	}
	int res_type_int = PyInt_AsLong(res_type);
	Py_DECREF(res_type);

	switch(res_type_int){
	case MYSQLD_PACKET_OK:{
		PyObject *resultset = PyObject_GetAttrString(response, "resultset");
		if(!resultset){
			PyErr_Clear();
			guint64 affected_rows = 0;
			guint64 insert_id = 0;

			PyObject *ar = PyObject_GetAttrString(response, "affected_rows");
			if(!ar)
				PyErr_Clear();
			else if(PyLong_Check(ar))
				affected_rows = PyLong_AsLong(ar);
			else if(PyInt_Check(ar))
				affected_rows = PyInt_AsLong(ar);
			Py_XDECREF(ar);

			PyObject *ii = PyObject_GetAttrString(response, "insert_id");
			if(!ii)
				PyErr_Clear();
			else if(PyLong_Check(ii))
				insert_id = PyLong_AsLong(ii);
			else if(PyInt_Check(ii))
				insert_id = PyInt_AsLong(ii);
			Py_XDECREF(ii);

			network_mysqld_con_send_ok_full(con->client, affected_rows, insert_id, 0x0002, 0);
		}
		else{
			Py_DECREF(resultset);

			/*
			PyObject *fs = PyObject_GetAttrString(resultset, "fields");
			PyObject *rs = PyObject_GetAttrString(resultset, "rows");
			PyObject *fss = PyObject_Str(fs);
			PyObject *rss = PyObject_Str(rs);
			g_critical("Get resultset:%s, %s", PyString_AsString(fss), PyString_AsString(rss));
			Py_DECREF(fss);
			Py_DECREF(rss);
			Py_DECREF(fs);
			Py_DECREF(rs);
			*/

			GPtrArray *fields = create_fields(resultset);
			if(!fields){
				network_mysqld_con_send_error(con->client, C("Cannot get proxy.response.resultset.fields!"));
				PyErr_Print();
				PyErr_Clear();
				return -1;
			}
			if(fields->len <= 0){
				network_mysqld_con_send_error(con->client, C("Size of proxy.response.resultset.fields is 0"));
				network_mysqld_proto_fielddefs_free(fields);
				return -1;
			}
			GPtrArray *rows = create_rows(resultset);
			if(!rows){
				network_mysqld_con_send_error(con->client, C("Cannot get proxy.response.resultset.rows"));
				PyErr_Print();
				network_mysqld_proto_fielddefs_free(fields);
				return -1;
			}

			network_mysqld_con_send_resultset(con->client, fields, rows);

			/*
			g_critical("ROOOOOOOOOOOws:");
			guint j;
			for(j = 0; j < rows->len; j++){
				GPtrArray *row = rows->pdata[j];
				guint k;
				for(k = 0; k < row->len; k++)
					g_critical("\t%s", row[k]);
			}
			*/

			if (fields) {
				network_mysqld_proto_fielddefs_free(fields);
				fields = NULL;
			}

			if (rows) {
				guint i;
				for (i = 0; i < rows->len; i++) {
					GPtrArray *row = rows->pdata[i];
					guint j;
					for (j = 0; j < row->len; j++)
						if (row->pdata[j])
							g_free(row->pdata[j]);
					g_ptr_array_free(row, TRUE);
				}
				g_ptr_array_free(rows, TRUE);
				rows = NULL;
			}
		}
		break;}

	case MYSQLD_PACKET_ERR:{
		gint errcode = ER_UNKNOWN_ERROR;
		/** let's call ourself Dynamic SQL ... 07000 is "dynamic SQL error" */
		const gchar *sqlstate = "07000";
		gchar *errmsg = NULL;

		PyObject *err_code = PyObject_GetAttrString(response, "errcode");
		if(!err_code){
			//Here use the default error code: ER_UNKNOWN_ERROR
			PyErr_Clear();
			//network_mysqld_con_send_error(con->client, C("Unknown proxy.response.errcode"));
			//g_message("proxy.response.errcode is unknown!");
			//return -1;
		}
		else{
			errcode = PyInt_AsLong(err_code);
			Py_DECREF(err_code);
		}

		PyObject *sql_state = PyObject_GetAttrString(response, "sqlstate");
		if(!sql_state){
			//Here use the default sql state: 07000
			PyErr_Clear();
			//network_mysqld_con_send_error(con->client, C("Unknown proxy.response.sqlstate"));
			//g_message("proxy.response.sqlstate is unknown!");
			//return -1;
		}
		else{
			sqlstate = PyString_AsString(sql_state);
			Py_DECREF(sql_state);
		}

		PyObject *err_msg = PyObject_GetAttrString(response, "errmsg");
		if(!err_msg){
			PyErr_Clear();
			network_mysqld_con_send_error(con->client, C("(python) proxy.response.errmsg is nil"));
		}
		else{
			errmsg = PyString_AsString(err_msg);
			Py_DECREF(err_msg);
			network_mysqld_con_send_error_full(con->client, errmsg, strlen(errmsg), errcode, sqlstate);
		}

	    break;}

	case MYSQLD_PACKET_RAW:{
		PyObject *packets = PyObject_GetAttrString(response, "packets");
		if(!packets){
			//g_critical("No response.packets");
			goto queue_reset;
		}

		int i;
		for(i = 0; i < PySequence_Size(packets); i++){
			PyObject *item = PySequence_GetItem(packets, i);
			//If invalid items doesn't influces valid ones before them.
			if(!item)
				goto queue_reset;
			if(!PyString_Check(item)){
				PyErr_SetString(PyExc_ValueError, "proxy.response.packets' "
							"items should be strings.");
				Py_DECREF(item);
				Py_DECREF(packets);
				goto queue_reset;
			}

			/*
			g_critical("Now get packets:len=%d", PyString_Size(item));
			int k;
			for(k = 0; k < PyString_Size(item); k++)
				g_critical("%d: %d", k, PyString_AsString(item)[k]);
			*/

			network_mysqld_queue_append(con->client, con->client->send_queue,
						PyString_AsString(item), PyString_Size(item));
			Py_DECREF(item);
		}
		Py_DECREF(packets);
queue_reset:
		network_mysqld_queue_reset(con->client); /* reset the packet-id checks */
		break;}
	default:
		g_critical("Now the response type is unknown: %d", res_type_int);
		return -1;
	}
	return 0;
}
