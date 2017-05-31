#ifndef WrapUtils_h
#define WrapUtils_h

#include <Python.h>

void PyListToArray(PyObject * source, float *dest, int width, int height);
PyObject * arrayToPyList(const float * source, int width, int height);

#endif