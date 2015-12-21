#include <Python.h>
#include "MadgwickAHRS/MadgwickAHRS.h"

static PyObject* py_update_ahrs(PyObject* self, PyObject* args)
{
    float gx, gy, gz, ax, ay, az, mx, my, mz;
    PyArg_ParseTuple(args, "fffffffff", &gx, &gy, &gz, &ax, &ay, &az, &mx, &my, &mz);
    MadgwickAHRSupdate(gx, gy, gz, ax, ay, az, mx, my, mz);
    return Py_BuildValue("(ffff)", q0, q1, q2, q3);
}

static PyMethodDef myModule_methods[] = {
    {"update_ahrs", py_update_ahrs, METH_VARARGS},
    {NULL, NULL}
};

PyMODINIT_FUNC initimu(void)
{
    (void) Py_InitModule("imu", myModule_methods);
}
