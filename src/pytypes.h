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

#ifndef _PYTYPES_H
#define _PYTYPES_H


#include <Python.h>
#include "structmember.h"

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include "network-mysqld.h"
#include "network-conn-pool.h"
#include "chassis-plugin.h"
#include "network-socket.h"
#include "network-backend.h"
#include "network-address.h"
#include "network-injection.h"

int PyErr_FormatObject(PyObject *exception, const char *format, ...);

int init_python_types(void);

typedef struct _proxy Proxy;
typedef struct _connection Connection;
typedef struct _globals Globals;
typedef struct _response Response;
typedef struct _users Users;
typedef struct _config Config;
typedef struct _socket Socket;
typedef struct _backend Backend;
typedef struct _address Address;
typedef struct _connection_pool ConnectionPool;
typedef struct _queue Queue;
typedef struct _response_resultset ResponseResultset;
typedef struct _injection_resultset InjectionResultset;
typedef struct _auth Auth;
typedef struct _injection Injection;
typedef struct _proxy_field ProxyField;
typedef struct _flags Flags;
typedef struct _proxy_rows ProxyRows;
typedef struct _proxy_row_iter ProxyRowIter;
typedef struct _backends Backends;
typedef struct _queries Queries;

struct _proxy{
	PyObject_HEAD
	network_mysqld_con *con;
	PyObject *connection;
	PyObject *response;
	PyObject *globals;
	PyObject *queries;
};

struct _queue{
	PyObject_HEAD
	GQueue *queue;
};

struct _users{
	PyObject_HEAD
	network_connection_pool *pool;
};

struct _connection_pool{
	PyObject_HEAD
	network_connection_pool *pool;
	PyObject *users;
};

struct _backend{
	PyObject_HEAD
	network_backend_t *backend;
	PyObject *dst;
	PyObject *pool;
};

struct _address{
	PyObject_HEAD
	network_address *address;
};

struct _config{
	PyObject_HEAD
	chassis_plugin_config *config;
	PyObject *backend_addresses;
	PyObject *read_only_backend_addresses;
	PyObject *dict;
};

struct _globals{
	PyObject_HEAD
	PyObject *backends;
	PyObject *config;
	PyObject *dict;
};

struct _connection{
	PyObject_HEAD
	network_mysqld_con *con;
	PyObject *client;
	PyObject *server;
};

struct _socket{
	PyObject_HEAD
	network_socket *socket;
};

struct _response {
	PyObject_HEAD
	PyObject *dict;
};

struct _response_resultset{
	PyObject_HEAD
	PyObject *fields;
	PyObject *rows;
};

struct _auth {
	PyObject_HEAD
	PyObject *packet;
};

struct _injection {
	PyObject_HEAD
	injection *inj;
};

struct _injection_resultset {
	PyObject_HEAD
	proxy_resultset_t *res;
};

struct _proxy_field {
	PyObject_HEAD
	MYSQL_FIELD *field;
};

struct _flags {
	PyObject_HEAD
	guint16 status;
};

struct _proxy_rows {
	PyObject_HEAD
	proxy_resultset_t *res;
};

struct _proxy_row_iter {
	PyObject_HEAD
	proxy_resultset_t *res;
};

struct _backends {
	PyObject_HEAD
	network_backends_t *backends;
};

struct _queries {
	PyObject_HEAD
	network_injection_queue *queries;
};

#define Proxy_Check(op) PyObject_TypeCheck(op, &Proxy_Type)
#define Queue_Check(op) PyObject_TypeCheck(op, &Queue_Type)
#define Users_Check(op) PyObject_TypeCheck(op, &Users_Type)
#define ConnectionPool_Check(op) PyObject_TypeCheck(op, &ConnectionPool_Type)
#define Backend_Check(op) PyObject_TypeCheck(op, &Backend_Type)
#define Address_Check(op) PyObject_TypeCheck(op, &Address_Type)
#define Config_Check(op) PyObject_TypeCheck(op, &Config_Type)
#define Globals_Check(op) PyObject_TypeCheck(op, &Globals_Type)
#define Socket_Check(op) PyObject_TypeCheck(op, &Socket_Type)
#define Connection_Check(op) PyObject_TypeCheck(op, &Connection_Type)
#define ResponseResultset_Check(op) PyObject_TypeCheck(op, &ResponseResultset_Type)
#define Auth_Check(op) PyObject_TypeCheck(op, &Auth_Type)
#define Injection_Check(op) PyObject_TypeCheck(op, &Injection_Type)
#define InjectionResultset_Check(op) PyObject_TypeCheck(op, &InjectionResultset_Type)
#define ProxyField_Check(op) PyObject_TypeCheck(op, &ProxyField_Type)
#define Flags_Check(op) PyObject_TypeCheck(op, &Flags_Type)
#define ProxyRow_Check(op) PyObject_TypeCheck(op, &ProxyRow_Type)
#define ProxyRowIter_Check(op) PyObject_TypeCheck(op, &ProxyRowIter_Type)
#define Backends_Check(op) PyObject_TypeCheck(op, &Backends_Type)
#define Queries_Check(op) Queries_TypeCheck(op, &Queries_Type)


PyObject *Proxy_New(network_mysqld_con *con);
PyObject *Globals_New(chassis_plugin_config* config, network_backends_t *backends);
PyObject *Response_New(void);
PyObject *Users_New(network_connection_pool *pool);
PyObject *Config_New(chassis_plugin_config *config);
PyObject *Socket_New(network_socket *socket);
PyObject *Backend_New(network_backend_t *backend);
PyObject *Address_New(network_address *addr);
PyObject *ConnectionPool_New(network_connection_pool *pool);
PyObject *Queue_New(GQueue *queue);
PyObject *ResponseResultset_New(PyObject *fields, PyObject *rows);
PyObject *Connection_New(network_mysqld_con *con);
PyObject *Auth_New(const char* packet, int len);
PyObject *Injection_New(injection *inj);
PyObject *InjectionResultset_New(proxy_resultset_t *res);
PyObject *ProxyField_New(MYSQL_FIELD *field);
PyObject *Flags_New(guint16 status);
PyObject *ProxyRows_New(proxy_resultset_t *res);
PyObject *ProxyRowIter_New(proxy_resultset_t *res);
PyObject *Backends_New(network_backends_t *backends);
PyObject *Queries_New(network_injection_queue *queries);


#define PROXY_VERSION "0.7.0"

#endif
