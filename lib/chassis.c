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



#include <Python.h>
#include <string.h>

/**
 * expose the chassis functions into the lua space
 * Also moves the global print function to the 'os' table and
 * replaces print with our logging function at a log level equal to
 * the current chassis minimum log level, so that we always see the
 * output of scripts.
 */


#include <glib.h>

#include "chassis-mainloop.h"
#include "chassis-plugin.h"
#include "chassis-stats.h"

static PyObject *
python_chassis_set_shutdown (PyObject *self, PyObject *args) {
	chassis_set_shutdown();
	Py_RETURN_NONE;
}

/**
 * helper function to set GHashTable key, value pairs in a Lua table
 * assumes to have a table on top of the stack.
 */
static void chassis_stats_setpythonval(gpointer key, gpointer val, gpointer dict) {
    const gchar *name = key;
    const guint value = GPOINTER_TO_UINT(val);
	PyDict_SetItemString((PyObject*)dict, name, PyInt_FromLong(value));
}

/**
 * Expose the plugin stats hashes to Lua for post-processing.
 *
 * Lua parameters: plugin name to fetch stats for (or "chassis" for only getting the global ones)
 *                 might be omitted, then this function gets stats for all plugins, including the chassis
 * Lua return values: nil if the plugin is not loaded
 *                    a table with the stats when given one plugin name
 *                    a table with the plugin names as keys and their values as subtables, the chassis global stats are keyed as "chassis"
 */
static PyObject *
python_chassis_stats(PyObject *self, PyObject *args) {
    const char *plugin_name = NULL;
    chassis *chas = NULL;
    chassis_plugin *plugin = NULL;
    guint i = 0;
    gboolean found_stats = FALSE;

	if(!PyArg_ParseTuple(args, "|s", &plugin_name))
		return NULL;

	PyObject *chas_addr = PySys_GetObject("_chassis_address");
	if(!chas_addr)
		return NULL;
	chas = (chassis*)PyInt_AsLong(chas_addr);

	PyObject *result = PyDict_New();
	if(!result)
		return NULL;

    if (chas && chas->modules) {
        for (i = 0; i < chas->modules->len; i++) {
            plugin = chas->modules->pdata[i];
            if (plugin->stats != NULL && plugin->get_stats != NULL) {
                GHashTable *stats_hash = NULL;

                if (plugin_name == NULL) {
                    /* grab all stats and key them by plugin name */
                    stats_hash = plugin->get_stats(plugin->stats);
                    if (stats_hash != NULL) {
                        found_stats = TRUE;
                    }

					PyObject *dict = PyDict_New();
					if(!dict)
						return NULL;

                    g_hash_table_foreach(stats_hash, chassis_stats_setpythonval, dict);
					PyDict_SetItemString(result, plugin->name, dict);
					Py_DECREF(dict);

                    g_hash_table_destroy(stats_hash);

                } else if (g_ascii_strcasecmp(plugin_name, "chassis") == 0) {
                  /* get the global chassis stats */
                    stats_hash = chassis_stats_get(chas->stats);
                    if (stats_hash == NULL) {
                        found_stats = FALSE;
                        break;
                    }
                    found_stats = TRUE;

					PyObject *dict = PyDict_New();
					if(!dict)
						return NULL;

                    g_hash_table_foreach(stats_hash, chassis_stats_setpythonval, dict);
                    g_hash_table_destroy(stats_hash);
					return dict;
                    //break;
                } else if (g_ascii_strcasecmp(plugin_name, plugin->name) == 0) {
                    /* check for the correct name and get the stats */
                    stats_hash = plugin->get_stats(plugin->stats);
                    if (stats_hash == NULL) {
                        found_stats = FALSE;
                        break;
                    }
                    found_stats = TRUE;

					PyObject *dict = PyDict_New();
					if(!dict)
						return NULL;
                    /* the table to use is already on the stack */
                    g_hash_table_foreach(stats_hash, chassis_stats_setpythonval, dict);
                    g_hash_table_destroy(stats_hash);
					return dict;
                }
            }
        }
    }
    if(!found_stats)
		Py_RETURN_NONE;
    return result;
}

/**
 * Log a message via the chassis log facility instead of using STDOUT.
 * This is more expensive than just printing to STDOUT, but generally logging
 * in a script would be protected by an 'if(debug)' or be important enough to
 * warrant the extra CPU cycles.
 *
 * Lua parameters: loglevel (first), message (second)
 */
static PyObject * log_levels = NULL;
static int init_log_levels(void){
	log_levels = PyDict_New();
#define ADD_LOG_LEVEL(name, level) \
	PyObject *level_ ## level = PyInt_FromLong(level);\
	if(!level_ ## level)\
		return -1;\
	PyDict_SetItemString(log_levels, #name, level_ ## level);\
	Py_DECREF(level_ ## level);

	ADD_LOG_LEVEL(error, 0)
	ADD_LOG_LEVEL(critical, 1)
	ADD_LOG_LEVEL(warning, 2)
	ADD_LOG_LEVEL(message, 3)
	ADD_LOG_LEVEL(info, 4)
	ADD_LOG_LEVEL(debug, 5)
#undef ADD_LOG_LEVEL
	return 0;
}

static PyObject *
python_chassis_log(PyObject *self, PyObject *args) {
	const char *level, *message;
	if(!log_levels && init_log_levels())
		return NULL;
	if(!PyArg_ParseTuple(args, "ss", &level, &message))
		return NULL;
	static const int log_level_values[] = {G_LOG_LEVEL_ERROR, G_LOG_LEVEL_CRITICAL,
        G_LOG_LEVEL_WARNING, G_LOG_LEVEL_MESSAGE,
        G_LOG_LEVEL_INFO, G_LOG_LEVEL_DEBUG};
	PyObject *lvl = PyString_FromString(level);
	if(!lvl)
		return NULL;
	PyObject *option_obj = PyDict_GetItemString(log_levels, level);
	if(!option_obj){
		PyErr_Format(PyExc_KeyError, "dict has not key named %s", level);
		return NULL;
	}
	assert(PyInt_Check(option_obj));
	int option = PyInt_AsLong(option_obj);

	/* try to get some information about who logs this message */
    g_log(G_LOG_DOMAIN, log_level_values[option], "%s", message);
	Py_RETURN_NONE;
}

#define CHASSIS_PYTHON_LOG(level)\
static PyObject *\
python_chassis_log_ ## level(PyObject *self, PyObject *args){\
	const char *message;\
	if(!PyArg_ParseTuple(args, "s", &message))\
		return NULL;\
	g_log(G_LOG_DOMAIN, G_LOG_LEVEL_ ## level, "%s", message);\
	return 0;\
}

CHASSIS_PYTHON_LOG(ERROR)
CHASSIS_PYTHON_LOG(CRITICAL)
CHASSIS_PYTHON_LOG(WARNING)
CHASSIS_PYTHON_LOG(MESSAGE)
CHASSIS_PYTHON_LOG(INFO)
CHASSIS_PYTHON_LOG(DEBUG)

#undef CHASSIS_PYTHON_LOG


static PyObject *
python_g_mem_profile(PyObject *self, PyObject *args) {
	g_mem_profile();
	Py_RETURN_NONE;
}

#define CHASSIS_PYTHON_LOG_FUNC(level, LEVEL) {#level, (PyCFunction)python_chassis_log_ ## LEVEL, METH_VARARGS, ""}

static PyMethodDef chassis_methods[] = {
	{"set_shutdown", (PyCFunction)python_chassis_set_shutdown, METH_NOARGS, ""},
	{"log", (PyCFunction)python_chassis_log, METH_VARARGS, ""},
/* we don't really want g_error being exposed, since it abort()s */
    CHASSIS_PYTHON_LOG_FUNC(error, ERROR),
    CHASSIS_PYTHON_LOG_FUNC(critical, CRITICAL),
    CHASSIS_PYTHON_LOG_FUNC(warning, WARNING),
    CHASSIS_PYTHON_LOG_FUNC(message, MESSAGE),
    CHASSIS_PYTHON_LOG_FUNC(info, INFO),
    CHASSIS_PYTHON_LOG_FUNC(debug, DEBUG),
/* to get the stats of a plugin, exposed as a table */
    {"get_stats", (PyCFunction)python_chassis_stats, METH_VARARGS, ""},
    {"mem_profile", (PyCFunction)python_g_mem_profile, METH_NOARGS, ""},
	{NULL, NULL},
};

#undef CHASSIS_PYTHON_LOG_FUNC

#ifndef PyMODINIC_FUNC
#define PyMODINIC_FUNC void
#endif

PyMODINIT_FUNC initchassis(void){
	Py_InitModule("chassis", chassis_methods);
}
