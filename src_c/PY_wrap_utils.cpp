#include "wrap_utils.h"
#include <Python.h>

void PyListToArray(PyObject * source, float *dest, int width, int height) {
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


PyObject * arrayToPyList(const float * source, int width, int height) {
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

float getItem(PyObject * source, short i) {
    return (float) PyFloat_AsDouble(PyList_GetItem(source, (Py_ssize_t) i)); 
}

Vector PyListToVector(PyObject * source) {
    return Vector(getItem(source, 0), getItem(source, 1), getItem(source, 2));
}

PyObject * vectorToPyList(Vector v) {
    PyObject * newResultObj = PyTuple_New(3); 
    PyTuple_SET_ITEM(newResultObj, 0, PyFloat_FromDouble(v.x));   
    PyTuple_SET_ITEM(newResultObj, 1, PyFloat_FromDouble(v.y));   
    PyTuple_SET_ITEM(newResultObj, 2, PyFloat_FromDouble(v.z));   
    return newResultObj;
}