 

/**
 * expose the chassis functions into the lua space
 */

#include <Python.h>
#include "object.h"

#include "network-mysqld-proto.h"
#include "network-mysqld-packet.h"
#include "glib-ext.h"


#define S(x) x->str, x->len


static PyObject *
python_password_hash(PyObject *self, PyObject *args) {
	size_t password_len;
	const char *password;
	if(!PyArg_ParseTuple(args, "s#", &password, &password_len))
		return NULL;
	GString *response;

	response = g_string_new(NULL);
	network_mysqld_proto_password_hash(response, password, password_len);

	PyObject *result = PyString_FromStringAndSize(S(response));

	g_string_free(response, TRUE);

	return result;
}

static PyObject *
python_password_scramble(PyObject *self, PyObject *args){
	size_t challenge_len;
	const char *challenge;
	size_t hashed_password_len;
	const char *hashed_password;
	if(!PyArg_ParseTuple(args, "s#s#", &challenge, &challenge_len,
					&hashed_password, &hashed_password_len))
		return NULL;
	GString *response;

	response = g_string_new(NULL);
	network_mysqld_proto_password_scramble(response,
			challenge, challenge_len,
			hashed_password, hashed_password_len);

	PyObject *result = PyString_FromStringAndSize(S(response));

	g_string_free(response, TRUE);

	return result;
}

static PyObject *
python_password_unscramble(PyObject *self, PyObject *args) {
	size_t challenge_len;
	const char *challenge;
	size_t response_len;
	const char *response;
	size_t dbl_hashed_password_len;
	const char *dbl_hashed_password;

	if(!PyArg_ParseTuple(args, "s#s#s#", &challenge, &challenge_len, &response,
					&response_len, &dbl_hashed_password, &dbl_hashed_password_len))
		return NULL;

	GString *hashed_password = g_string_new(NULL);

	network_mysqld_proto_password_unscramble(
			hashed_password,
			challenge, challenge_len,
			response, response_len,
			dbl_hashed_password, dbl_hashed_password_len);

	PyObject *result = PyString_FromStringAndSize(S(hashed_password));
	g_string_free(hashed_password, TRUE);
	return result;
}


static PyObject *
python_password_check(PyObject *self, PyObject *args) {
	size_t challenge_len;
	const char *challenge;
	size_t response_len;
	const char *response;
	size_t dbl_hashed_password_len;
	const char *dbl_hashed_password;

	if(!PyArg_ParseTuple(args, "s#s#s#", &challenge, &challenge_len, &response,
					&response_len, &dbl_hashed_password, &dbl_hashed_password_len))
		return NULL;

	int result = network_mysqld_proto_password_check(
			challenge, challenge_len,
			response, response_len,
			dbl_hashed_password, dbl_hashed_password_len);

	return PyInt_FromLong(result);
}


static PyMethodDef password_methods[] = {
	{"hash", python_password_hash, METH_VARARGS, ""},
	{"scramble", python_password_scramble, METH_VARARGS, ""},
	{"unscramble", python_password_unscramble, METH_VARARGS, ""},
	{"check", python_password_check, METH_VARARGS, ""},
};

#ifndef PyMODINIC_FUNC
#define PyMODINIC_FUNC void
#endif

PyMODINIT_FUNC initpassword(void){
	if(init_objects())
		return;
	Py_InitModule("mysql.password", password_methods);
}
