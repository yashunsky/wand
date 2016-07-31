#include <stdio.h>
#include <Python.h>
#include "unify_definition.h"

static void PyListToArray(PyObject * source, float *dest, int width, int height) {
    int i;
    int j;
    PyObject* row;
    for (i = 0; i < width; i++) {
        if (height == 1) {
            dest[i] = (float) PyFloat_AsDouble(PyList_GetItem(source, (Py_ssize_t) i));  
        } else {
            row = PyList_GetItem(source, (Py_ssize_t) i);
            for (j = 0; j < height; j++) {
                dest[i * height + j] = PyFloat_AsDouble(PyList_GetItem(row, (Py_ssize_t) j));
            }
        }
    }
}


static PyObject * arrayToPyList(const float * source, int width, int height) {
    int i, j;
    PyObject * row;
    PyObject * newListObj = PyTuple_New(width);

    for (i = 0; i < width; i++) {
        if (height == 1) {
            PyTuple_SET_ITEM(newListObj, i, PyFloat_FromDouble(source[i]));
        } else {
            row = PyTuple_New(height);
            for (j = 0; j < height; j++) {
                PyTuple_SET_ITEM(row, j, PyFloat_FromDouble(source[i * height +j]));
            }
            PyTuple_SET_ITEM(newListObj, i, row);
        }
    }

    return newListObj;    
}

static PyObject* py_getSegmantation(PyObject* self, PyObject* args) {
    return PyInt_FromLong(SEGMENTATION);
}

static PyObject* py_getStrokeMaxLength(PyObject* self, PyObject* args) {
    return PyInt_FromLong(STROKE_MAX_LENGTH);
}

static PyObject* py_getDist(PyObject* self, PyObject* args) {
    float a[DIMENTION];
    float b[DIMENTION];

    PyObject * aObj;
    PyObject * bObj;
    PyArg_ParseTuple(args, "O!O!", &PyList_Type, &aObj, &PyList_Type, &bObj);

    PyListToArray(aObj, &a[0], DIMENTION, 1);
    PyListToArray(bObj, &b[0], DIMENTION, 1);

    return PyFloat_FromDouble((double) getDist(a, b));
}

static PyObject* py_unifyStroke(PyObject* self, PyObject* args) {
    float stroke[STROKE_MAX_LENGTH][DIMENTION];
    float newStroke[SEGMENTATION][DIMENTION];
    int length;
    
    PyObject * strokeObj;

    PyArg_ParseTuple(args, "O!i", &PyList_Type, &strokeObj, &length);

    PyListToArray(strokeObj, &stroke[0][0], STROKE_MAX_LENGTH, DIMENTION);

    unifyStroke(stroke, newStroke, length);

    return arrayToPyList(&newStroke[0][0], SEGMENTATION, DIMENTION);
}

static PyObject* py_checkStroke(PyObject* self, PyObject* args) {
    float stroke[SEGMENTATION][DIMENTION];
    float description[SEGMENTATION][DIMENTION + 1];
    
    PyObject * strokeObj;
    PyObject * descriptionObj;

    PyArg_ParseTuple(args, "O!O!", &PyList_Type, &strokeObj, &PyList_Type, &descriptionObj);

    PyListToArray(strokeObj, &stroke[0][0], SEGMENTATION, DIMENTION);
    PyListToArray(descriptionObj, &description[0][0], SEGMENTATION, DIMENTION + 1);

    return PyFloat_FromDouble((double) checkStroke(stroke, description));
}

static PyObject* py_getStroke(PyObject* self, PyObject* args) {
    float stroke[STROKE_MAX_LENGTH][DIMENTION];
    int length;    
    unsigned long access;

    PyObject * strokeObj;

    PyObject * accessObject;

    PyArg_ParseTuple(args, "O!ik", &PyList_Type, &strokeObj, &length, &access);

    PyListToArray(strokeObj, &stroke[0][0], STROKE_MAX_LENGTH, DIMENTION);

    return PyInt_FromLong(getStroke(stroke, length, access));
}

static PyMethodDef c_methods[] = {
    {"get_segmentation", py_getSegmantation, METH_VARARGS},
    {"get_stroke_max_length", py_getStrokeMaxLength, METH_VARARGS},
    {"get_dist", py_getDist, METH_VARARGS},
    {"unify_stroke", py_unifyStroke, METH_VARARGS},
    {"check_stroke", py_checkStroke, METH_VARARGS},
    {"get_stroke", py_getStroke, METH_VARARGS},
    {NULL, NULL}
};

PyMODINIT_FUNC initc_wrap(void) {
    (void) Py_InitModule("c_wrap", c_methods);
}
