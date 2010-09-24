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

/**
 * expose the chassis functions into the lua space
 */


#include <Python.h>
#include "object.h"

#include "network-mysqld-proto.h"
#include "network-mysqld-packet.h"
#include "network-mysqld-masterinfo.h"
#include "glib-ext.h"


#define C(x) x, sizeof(x) - 1
#define S(x) x->str, x->len

static PyObject *
python_proto_get_err_packet(PyObject *self, PyObject *args){
	int packet_len;
	const char* packet_str;
	if(!PyArg_ParseTuple(args, "s#", &packet_str, &packet_len))
		return NULL;
	network_mysqld_err_packet_t *err_packet;
	network_packet packet;
	GString s;
	int err = 0;
	s.str = (char *)packet_str;
	s.len = packet_len;
	packet.data = &s;
	packet.offset = 0;

	err_packet = network_mysqld_err_packet_new();

	err = err || network_mysqld_proto_get_err_packet(&packet, err_packet);
	if (err) {
		network_mysqld_err_packet_free(err_packet);
		PyErr_SetString(PyExc_ValueError, "network_mysqld_proto_get_err_packet() failed");
		return NULL;
	}

	PyObject *result = Spain_New();
	if(!result)
		return NULL;

#define PYTHON_EXPORT_STR(x, y) \
	PyObject *s_ ## y = PyString_FromString(x->y->str);\
	if(!s_ ## y){\
		Py_DECREF(result);\
		network_mysqld_err_packet_free(err_packet);\
		return NULL;\
	}\
	PyObject_SetAttrString(result, #y, s_ ## y);\
	Py_DECREF(s_ ## y);

#define PYTHON_EXPORT_INT(x, y) \
	PyObject *s_ ## y = PyInt_FromLong(x->y);\
	if(!s_ ## y){\
		Py_DECREF(result);\
		network_mysqld_err_packet_free(err_packet);\
		return NULL;\
	}\
	PyObject_SetAttrString(result, #y, s_ ## y);\
	Py_DECREF(s_ ## y);

	PYTHON_EXPORT_STR(err_packet, errmsg)
	PYTHON_EXPORT_STR(err_packet, sqlstate)
	PYTHON_EXPORT_INT(err_packet, errcode)

	network_mysqld_err_packet_free(err_packet);
	return result;
}


static PyObject *
python_proto_append_challenge_packet (PyObject *self, PyObject *args) {
	GString *packet;
	network_mysqld_auth_challenge *auth_challenge;

	PyObject *dict;
	if(!PyArg_ParseTuple(args, "O!", &PyDict_Type, &dict))
		return NULL;

	auth_challenge = network_mysqld_auth_challenge_new();

#define PYTHON_IMPORT_INT(x, y) \
	PyObject *v_ ## y = PyDict_GetItemString(dict, #y);\
	if(v_ ## y){\
		if(PyInt_Check(v_ ## y))\
			x->y = PyInt_AsLong(v_ ## y);\
		else{\
			PyErr_SetString(PyExc_ValueError, #x "." #y "must be an int");\
			Py_DECREF(v_ ## y);\
			return NULL;\
		}\
	}

#define PYTHON_IMPORT_STR(x, y) \
	PyObject *v_ ## y = PyDict_GetItemString(dict, #y);\
	if(v_ ## y){\
		if(PyString_Check(v_ ## y)){\
			int len;\
			char *str;\
			PyString_AsStringAndSize(v_ ## y, &str, &len);\
			g_string_assign_len(x->y, str, len);\
		} else{\
			PyErr_SetString(PyExc_ValueError, #x "." #y "must be an string");\
			Py_DECREF(v_ ## y);\
			return NULL;\
		}\
	}

	PYTHON_IMPORT_INT(auth_challenge, protocol_version);
	PYTHON_IMPORT_INT(auth_challenge, server_version);
	PYTHON_IMPORT_INT(auth_challenge, thread_id);
	PYTHON_IMPORT_INT(auth_challenge, capabilities);
	PYTHON_IMPORT_INT(auth_challenge, charset);
	PYTHON_IMPORT_INT(auth_challenge, server_status);

	PYTHON_IMPORT_STR(auth_challenge, challenge);

//#undef PYTHON_IMPORT_INT
//#undef PYTHON_IMPORT_STR

	packet = g_string_new(NULL);
	network_mysqld_proto_append_auth_challenge(packet, auth_challenge);

	network_mysqld_auth_challenge_free(auth_challenge);
	PyObject *res = PyString_FromStringAndSize(S(packet));
	if(!res)
		return NULL;
	g_string_free(packet, TRUE);
	return res;
}

static PyObject *
python_proto_append_response_packet (PyObject *self, PyObject *args) {
	GString *packet;
	network_mysqld_auth_response *auth_response;

	PyObject *dict;
	if(!PyArg_ParseTuple(args, "O!", &PyDict_Type, &dict))
		return NULL;

	packet = g_string_new(NULL);
	auth_response = network_mysqld_auth_response_new();

	PYTHON_IMPORT_INT(auth_response, capabilities);
	PYTHON_IMPORT_INT(auth_response, max_packet_size);
	PYTHON_IMPORT_INT(auth_response, charset);

	PYTHON_IMPORT_STR(auth_response, username);
	PYTHON_IMPORT_STR(auth_response, response);
	PYTHON_IMPORT_STR(auth_response, database);

	if (network_mysqld_proto_append_auth_response(packet, auth_response)) {
		network_mysqld_auth_response_free(auth_response);
		g_string_free(packet, TRUE);
		PyErr_SetString(PyExc_ValueError, "to_response_packet() failed");
		return NULL;
	}

	network_mysqld_auth_response_free(auth_response);
	PyObject *result = PyString_FromStringAndSize(S(packet));
	g_string_free(packet, TRUE);
	return result;
}

static PyMethodDef proto_methods[] = {
	{"from_err_packet", python_proto_get_err_packet, METH_VARARGS, ""},
	{"to_challenge_packet", python_proto_append_challenge_packet, METH_VARARGS, ""},
	{"to_response_packet", python_proto_append_response_packet, METH_VARARGS, ""},
	{0},
};

#ifndef PyMODINIC_FUNC
#define PyMODINIC_FUNC void
#endif

PyMODINIT_FUNC initproto(void){
	if(init_objects())
		return;
	Py_InitModule("mysql.proto", proto_methods);
}
