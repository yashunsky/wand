#include <stdio.h>
#include <Python.h>
#include "splitter.h"
#include "unify_definition.h"
#include "imu.h"
#include "state_machine.h"

#include <stdint.h>
#include "extern_sm/generation_light.h"
#include "extern_sm/service.h"

#include "full_state_machine.h"

static Splitter splitter = Splitter();
static IMU imu = IMU();
static StateMachine SM1 = StateMachine(0);
static StateMachine SM2 = StateMachine(0);
static StateMachine SMZ = StateMachine(2);

static FullStateMachine FSM[2] = {FullStateMachine(0), FullStateMachine(0)};

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


static PyObject* py_setIMUData(PyObject* self, PyObject* args) {
    int result;
    float delta;
    float gyro;
    float accel[DIMENTION];
    float heading[DIMENTION];
    unsigned long access;

    PyObject * accelObj;
    PyObject * headingObj;

    PyArg_ParseTuple(args, "ffO!O!k", &delta, &gyro, &PyList_Type, &accelObj, &PyList_Type, &headingObj, &access);

    PyListToArray(accelObj, &accel[0], DIMENTION, 1);

    PyListToArray(headingObj, &heading[0], DIMENTION, 1);

    result = splitter.setIMUData(delta, gyro, accel, heading, access);

    return PyInt_FromLong(result);
}

static PyObject* py_setSensorData(PyObject* self, PyObject* args) {
    float delta;
    float acc[DIMENTION];
    float gyro[DIMENTION];
    float mag[DIMENTION];
    int axis;

    PyObject * accObj;
    PyObject * gyroObj;
    PyObject * magObj;

    bool outInClaibration;
    float outGyro;
    float outAcc[DIMENTION];
    float outHeading[DIMENTION];    

    PyArg_ParseTuple(args, "fO!O!O!i", &delta, &PyList_Type, &accObj, &PyList_Type, &gyroObj, &PyList_Type, &magObj, &axis);

    PyListToArray(accObj, &acc[0], DIMENTION, 1);
    PyListToArray(gyroObj, &gyro[0], DIMENTION, 1);
    PyListToArray(magObj, &mag[0], DIMENTION, 1);

    outInClaibration = imu.calc(delta, acc, gyro, mag, axis, &outGyro, outAcc, outHeading);

    PyObject * outAccObj = arrayToPyList(outAcc, DIMENTION, 1);
    PyObject * outHeadingObj = arrayToPyList(outHeading, DIMENTION, 1);
    
    PyObject * result = PyTuple_New(4);
    PyTuple_SET_ITEM(result, 0, PyBool_FromLong(outInClaibration ? 1 : 0));
    PyTuple_SET_ITEM(result, 1, PyFloat_FromDouble(outGyro));
    PyTuple_SET_ITEM(result, 2, outAccObj);
    PyTuple_SET_ITEM(result, 3, outHeadingObj);

    return result;
}


static PyObject* py_setSMData(PyObject* self, PyObject* args) {
    float delta;
    float acc[DIMENTION];
    float gyro[DIMENTION];
    float mag[DIMENTION];
    int dest;
    unsigned long access;

    PyObject * accObj;
    PyObject * gyroObj;
    PyObject * magObj;   

    PyArg_ParseTuple(args, "ifO!O!O!k", &dest, &delta, &PyList_Type, &accObj, &PyList_Type, &gyroObj, &PyList_Type, &magObj, &access);

    PyListToArray(accObj, &acc[0], DIMENTION, 1);
    PyListToArray(gyroObj, &gyro[0], DIMENTION, 1);
    PyListToArray(magObj, &mag[0], DIMENTION, 1);

    StateMachine * sm;

    switch (dest) {
        case 0: sm = &SM1; break;
        case 1: sm = &SM2; break;
        default: sm = &SMZ; break;
    }

    return PyInt_FromLong(sm->setData(delta, acc, gyro, mag, access));
}

static PyObject* py_setSignal(PyObject* self, PyObject* args) {
  int sig;
  PyArg_ParseTuple(args, "i", &sig);

  QEvt e;

  e.sig = (uint8_t) sig;
  QMSM_DISPATCH(the_hand, &e);

  uint8_t color, blink, vibro;

  getState(the_hand, &color, &blink, &vibro);

  PyObject * result = PyTuple_New(3);
  PyTuple_SET_ITEM(result, 0, PyInt_FromLong(color));
  PyTuple_SET_ITEM(result, 1, PyInt_FromLong(blink));
  PyTuple_SET_ITEM(result, 2, PyInt_FromLong(vibro));

  return result;  
}

static PyObject* py_getQ_USER_SIG(PyObject* self, PyObject* args) {
  return PyInt_FromLong(Q_USER_SIG);
}

static PyObject* py_setFSMData(PyObject* self, PyObject* args) {
    float delta;
    float acc[DIMENTION];
    float gyro[DIMENTION];
    float mag[DIMENTION];
    int dest;
    unsigned long access;

    PyObject * accObj;
    PyObject * gyroObj;
    PyObject * magObj;   

    PyArg_ParseTuple(args, "ifO!O!O!k", &dest, &delta, &PyList_Type, &accObj, &PyList_Type, &gyroObj, &PyList_Type, &magObj, &access);

    PyListToArray(accObj, &acc[0], DIMENTION, 1);
    PyListToArray(gyroObj, &gyro[0], DIMENTION, 1);
    PyListToArray(magObj, &mag[0], DIMENTION, 1);

    uint8_t color, blink, vibro;

    dest = dest > 1 ? 1 : 0;

    FSM[dest].setData(delta, acc, gyro, mag, access, &color, &blink, &vibro);

    PyObject * result = PyTuple_New(3);
    PyTuple_SET_ITEM(result, 0, PyInt_FromLong(color));
    PyTuple_SET_ITEM(result, 1, PyInt_FromLong(blink));
    PyTuple_SET_ITEM(result, 2, PyInt_FromLong(vibro));

    return result;     
}

static PyMethodDef c_methods[] = {    
    {"get_segmentation", py_getSegmantation, METH_VARARGS},
    {"get_stroke_max_length", py_getStrokeMaxLength, METH_VARARGS},
    {"get_dist", py_getDist, METH_VARARGS},
    {"unify_stroke", py_unifyStroke, METH_VARARGS},
    {"check_stroke", py_checkStroke, METH_VARARGS},
    {"get_stroke", py_getStroke, METH_VARARGS},
    {"set_imu_data", py_setIMUData, METH_VARARGS},
    {"set_sensor_data", py_setSensorData, METH_VARARGS},
    {"set_sm_data", py_setSMData, METH_VARARGS},
    {"set_fsm_data", py_setFSMData, METH_VARARGS},    
    {"set_signal", py_setSignal, METH_VARARGS},
    {"get_q_user_sig", py_getQ_USER_SIG, METH_VARARGS},
    {NULL, NULL}
};

extern "C" {
    PyMODINIT_FUNC initc_wrap(void) {
        DebugSM = 0;
        Hand_ctor(the_hand);
        (void) Py_InitModule("c_wrap", c_methods);
    }
}
