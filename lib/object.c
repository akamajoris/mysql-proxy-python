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
#include "structmember.h"

#include <glib.h>

typedef struct {
    PyObject_HEAD
    PyObject *dict;
} Spain;


static int
Spain_init(Spain *self, PyObject *args, PyObject *kwds)
{
    return 0;
}

static PyObject *
Spain_new(PyTypeObject *type, PyObject *args, PyObject *kwds){
    Spain *spain = (Spain*)type->tp_alloc(type, 0);
    if(spain){
        spain->dict = PyDict_New();
        if(!spain->dict){
            Py_DECREF(spain);
            return NULL;
        }
    }
    return (PyObject*)spain;
}

static void
Spain_dealloc(Spain* self){
    Py_DECREF(self->dict);
    self->ob_type->tp_free((PyObject*)self);
}

PyTypeObject SpainType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "spain.Spain",             /*tp_name*/
    sizeof(Spain),             /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)Spain_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    PyObject_GenericGetAttr,                         /*tp_getattro*/
    PyObject_GenericSetAttr,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "Spain objects",           /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    0,             /* tp_methods */
    0,             /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    offsetof(Spain, dict),                         /* tp_dictoffset */
    (initproc)Spain_init,      /* tp_init */
    0,                         /* tp_alloc */
    Spain_new,                 /* tp_new */
};

/*
static PyMethodDef spain_methods[] = {
    {NULL}
};

#ifndef PyMODINIC_FUNC
#define PyMODINIC_FUNC void
#endif


PyMODINIC_FUNC
initspain(void){
    if(PyType_Ready(&SpainType) < 0)
        return;
    PyObject *m = Py_InitModule3("spain", spain_methods, "");
    if(!m)
        return;
    Py_INCREF(&SpainType);
    PyModule_AddObject(m, "Spain", (PyObject*)&SpainType);
}
*/

PyObject *
Spain_New(void){
    Spain *s = PyObject_New(Spain, &SpainType);
    if(!s)
        return NULL;
    s->dict = PyDict_New();
    if(!s->dict)
        return NULL;
    return (PyObject*)s;
}

int init_objects(void){
    if(PyType_Ready(&SpainType) < 0)
        return -1;
    return 0;
}
