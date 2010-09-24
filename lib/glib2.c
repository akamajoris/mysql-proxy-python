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
