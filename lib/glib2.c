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
#include <glib.h>

static PyObject *
python_g_usleep (PyObject *self, PyObject *args) {
	int ms = 0;
	if(!PyArg_ParseTuple(args, "i", &ms))
		return NULL;
	g_usleep(ms);
	Py_RETURN_NONE;
}

static PyObject *
python_g_checksum_md5 (PyObject *self, PyObject *args) {
	size_t str_len = 0;
	const char *str = NULL;
	if(!PyArg_ParseTuple(args, "s#", &str, &str_len))
		return NULL;
	GChecksum *cs;

	cs = g_checksum_new(G_CHECKSUM_MD5);

	g_checksum_update(cs, (guchar *)str, str_len);

	PyObject *css = PyString_FromString(g_checksum_get_string(cs));

	g_checksum_free(cs);

	return css;
}

static PyMethodDef glib2_methods[] = {
	{"usleep", python_g_usleep, METH_VARARGS, ""},
	{"md5", python_g_checksum_md5, METH_VARARGS, ""},
	{NULL, NULL},
};

#ifndef PyMODINIC_FUNC
#define PyMODINIC_FUNC void
#endif

PyMODINIT_FUNC initglib2(void){
	Py_InitModule("glib2", glib2_methods);
}
