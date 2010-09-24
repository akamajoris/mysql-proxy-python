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


#ifndef _PYPROXY_PLUGIN_H
#define	_PYPROXY_PLUGIN_H

#include <Python.h>

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <glib.h>

#include "network-mysqld.h"


typedef struct _pyproxy_functions {
	PyObject *init;
	PyObject *connect_server;
	PyObject *read_handshake;
	PyObject *read_auth;
	PyObject *read_auth_result;
	PyObject *read_query;
	PyObject *read_query_result;
	PyObject *send_query_result;
	PyObject *disconnect_client;
} pyproxy_functions;

struct chassis_plugin_config {
	gchar *address;                   /**< listening address of the proxy */

	gchar **backend_addresses;        /**< read-write backends */
	gchar **read_only_backend_addresses; /**< read-only  backends */

	gint fix_bug_25371;               /**< suppress the second ERR packet of bug #25371 */

	gint profiling;                   /**< skips the execution of the read_query() function */

	gchar *python_script;                /**< script to load at the start the connection */

	gint pool_change_user;            /**< don't reset the connection, when a connection is taken from the pool
					       - this safes a round-trip, but we also don't cleanup the connection
					       - another name could be "fast-pool-connect", but that's too friendly
					       */

	gint start_proxy;

	network_mysqld_con *listen_con;

	pyproxy_functions *proxy_funcs;

	void* python_dynalib_handle;
};


#endif	/* _PYPROXY_PLUGIN_H */

