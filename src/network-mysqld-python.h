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

#ifndef _NETWORK_MYSQLD_PYTHON_H
#define _NETWORK_MYSQLD_PYTHON_H


#include <Python.h>

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include "network-mysqld.h"
#include "network-injection.h"
#include "network-mysqld-lua.h"


int network_mysqld_python_initialize(chassis_plugin_config*);

struct network_mysqld_con_python_injection {
	network_injection_queue *queries;	/**< An ordered list of queries we want to have executed. */
	int sent_resultset;					/**< Flag to make sure we send only one result back to the client. */
};

typedef struct {
	struct network_mysqld_con_python_injection injected;	/**< A list of queries to send to the backend.*/

	PyObject *proxy;

	network_backend_t *backend;
	int backend_ndx;               /**< [python] index into the backend-array */

	gboolean connection_close;     /**< [python] set by the python code to close a connection */

	struct timeval interval;       /**< The interval to be used for evt_timer, currently unused. */
	struct event evt_timer;        /**< The event structure used to implement the timer callback, currently unused. */

	gboolean is_reconnecting;      /**< if true, critical messages concerning failed connect() calls are suppressed, as they are expected errors */
} network_mysqld_con_python_t;


network_mysqld_con_python_t *network_mysqld_con_python_new(void);

typedef network_mysqld_lua_stmt_ret network_mysqld_python_stmt_ret;

int network_connection_pool_python_add_connection(network_mysqld_con *con);

void network_mysqld_con_python_free(network_mysqld_con_python_t *st);

network_socket *network_connection_pool_python_swap(network_mysqld_con *con, int backend_ndx);

int network_mysqld_con_python_handle_proxy_response(network_mysqld_con *, PyObject *);

#endif
