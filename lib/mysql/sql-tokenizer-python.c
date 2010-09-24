#include "object.h"

#include "lua-env.h"
#include "glib-ext.h"

#define C(x) x, sizeof(x) - 1
#define S(x) x->str, x->len

#include "sql-tokenizer.h"

/**
 * split the SQL query into a stream of tokens
 */
static PyObject *
proxy_tokenize(PyObject *self, PyObject *args) {
	size_t str_len = 0;
	const char *str = NULL;
	if(!PyArg_ParseTuple(args, "s#", &str, &str_len))
		return NULL;
	GPtrArray *tokens = sql_tokens_new();

	sql_tokenizer(tokens, str, str_len);

	PyObject *result = PyTuple_New(tokens->len);
	if(!result)
		return NULL;
	int i;
	for(i = 0; i < tokens->len; i++){
		sql_token *t = (sql_token*)tokens->pdata[i];
		PyObject *token = Spain_New();
		if(!token){
			Py_DECREF(result);
			return NULL;
		}
		PyObject *text = PyString_FromStringAndSize(S(t->text));
		PyObject_SetAttrString(token, "text", text);
		Py_DECREF(text);

		PyObject *token_name = PyString_FromString(sql_token_get_name(t->token_id));
		PyObject_SetAttrString(token, "token_name", token_name);
		Py_DECREF(token_name);

		PyObject *token_id = PyInt_FromLong(t->token_id);
		PyObject_SetAttrString(token, "token_id", token_id);
		Py_DECREF(token_id);

		PyTuple_SetItem(result, i, token);
	}
	return result;
}

static PyMethodDef tokenizer_methods[] = {
	{"tokenize", (PyCFunction)proxy_tokenize, METH_VARARGS, "tokenize a sql statement"},
	{NULL, NULL},
};


PyMODINIT_FUNC inittokenizer(void){
	Py_InitModule("tokenizer", tokenizer_methods);
}
