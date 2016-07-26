#include <Python.h>
#include <stdbool.h>

volatile static float accel[3] = {0.0, 0.0, 0.0};
volatile static float heading[3] = {0.0, 0.0, 1.0};
volatile static bool inCalibration = true;



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

static PyObject * arrayToPyList(volatile float * source, int width, int height) {
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

static PyObject* py_calc(PyObject* self, PyObject* args) {
    float inputData[10];

    PyObject * inputObj;

    PyArg_ParseTuple(args, "O!", &PyList_Type, &inputObj);

    PyListToArray(inputObj, &inputData[0], 10, 1);

    float dt = inputData[0];
    float ax = inputData[1];
    float ay = inputData[2];
    float az = inputData[3];
    float mx = inputData[4];
    float my = inputData[5];
    float mz = inputData[6];
    float gx = inputData[7];
    float gy = inputData[8];
    float gz = inputData[9];

    /* magic */

    accel[0] += 0.01;

    /* magic */

    PyObject * accelObj = arrayToPyList(&accel[0], 3, 1);
    PyObject * headingObj = arrayToPyList(&heading[0], 3, 1);;

    PyObject * result = PyTuple_New(3);

    PyTuple_SET_ITEM(result, 0, PyBool_FromLong((long) inCalibration));
    PyTuple_SET_ITEM(result, 1, accelObj);
    PyTuple_SET_ITEM(result, 2, headingObj);
    return result;
}

static PyMethodDef c_methods[] = {
    {"calc", py_calc, METH_VARARGS},
    {NULL, NULL}
};

PyMODINIT_FUNC initc_wrap_imu(void) {
    (void) Py_InitModule("c_wrap_imu", c_methods);
}
