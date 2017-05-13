#include <stdio.h>
#include <Python.h>
#include "splitter.h"
#include "unify_definition.h"
#include "imu.h"
#include "state_machine.h"

#include <stdint.h>
#include "extern_sm/generation_light.h"

#include "full_state_machine.h"

#include "orientation.h"

// static Splitter splitter = Splitter();
// static IMU imu = IMU();
// static StateMachine SM1 = StateMachine(0);
// static StateMachine SM2 = StateMachine(0);
// static StateMachine SMZ = StateMachine(2);

//static FullStateMachine FSM = FullStateMachine(0);

static Orientation O = Orientation();

/*static void PyListToArray(PyObject * source, float *dest, int width, int height) {
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
    float description[SEGMENTATION][DIMENTION];
    
    PyObject * strokeObj;
    PyObject * descriptionObj;

    PyArg_ParseTuple(args, "O!O!", &PyList_Type, &strokeObj, &PyList_Type, &descriptionObj);

    PyListToArray(strokeObj, &stroke[0][0], SEGMENTATION, DIMENTION);
    PyListToArray(descriptionObj, &description[0][0], SEGMENTATION, DIMENTION);

    return PyFloat_FromDouble((double) checkStroke(stroke, description));
}

static PyObject* py_getStroke(PyObject* self, PyObject* args) {
    float stroke[STROKE_MAX_LENGTH][DIMENTION];
    int length;    
    unsigned long access;

    PyObject * strokeObj;

    PyArg_ParseTuple(args, "O!i", &PyList_Type, &strokeObj, &length);

    PyListToArray(strokeObj, &stroke[0][0], STROKE_MAX_LENGTH, DIMENTION);

    return PyInt_FromLong(getStroke(stroke, length));
}


static PyObject* py_setIMUData(PyObject* self, PyObject* args) {
    int result;
    float delta;
    float gyro;
    float accel[DIMENTION];
    float heading[DIMENTION];

    PyObject * accelObj;
    PyObject * headingObj;

    PyArg_ParseTuple(args, "ffO!O!", &delta, &gyro, &PyList_Type, &accelObj, &PyList_Type, &headingObj);

    PyListToArray(accelObj, &accel[0], DIMENTION, 1);

    PyListToArray(headingObj, &heading[0], DIMENTION, 1);

    result = splitter.setIMUData(delta, gyro, accel, heading);

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

    PyObject * accObj;
    PyObject * gyroObj;
    PyObject * magObj;   

    PyArg_ParseTuple(args, "ifO!O!O!", &dest, &delta, &PyList_Type, &accObj, &PyList_Type, &gyroObj, &PyList_Type, &magObj);

    PyListToArray(accObj, &acc[0], DIMENTION, 1);
    PyListToArray(gyroObj, &gyro[0], DIMENTION, 1);
    PyListToArray(magObj, &mag[0], DIMENTION, 1);

    StateMachine * sm;

    switch (dest) {
        case 0: sm = &SM1; break;
        case 1: sm = &SM2; break;
        default: sm = &SMZ; break;
    }

    return PyInt_FromLong(sm->setData(delta, acc, gyro, mag));
}

static PyObject* py_setSignal(PyObject* self, PyObject* args) {
  int sig;
  PyArg_ParseTuple(args, "i", &sig);

  QEvt e;

  e.sig = (uint8_t) sig;
  QMSM_DISPATCH(the_hand, &e);

  uint8_t color, vibro;
  uint16_t blinkOn, blinkOff;

  // getState(the_hand, &color, &blinkOn, &blinkOff, &vibro);

  PyObject * result = PyTuple_New(4);
  PyTuple_SET_ITEM(result, 0, PyInt_FromLong(color));
  PyTuple_SET_ITEM(result, 1, PyInt_FromLong(blinkOn));
  PyTuple_SET_ITEM(result, 2, PyInt_FromLong(blinkOff));
  PyTuple_SET_ITEM(result, 3, PyInt_FromLong(vibro));

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

    PyObject * accObj;
    PyObject * gyroObj;
    PyObject * magObj;   

    PyArg_ParseTuple(args, "fO!O!O!", &delta, &PyList_Type, &accObj, &PyList_Type, &gyroObj, &PyList_Type, &magObj);

    PyListToArray(accObj, &acc[0], DIMENTION, 1);
    PyListToArray(gyroObj, &gyro[0], DIMENTION, 1);
    PyListToArray(magObj, &mag[0], DIMENTION, 1);

    bool inClaibration = FSM.setData(delta, acc, gyro, mag);

    PyObject * result = PyBool_FromLong(inClaibration ? 1 : 0);

    return result;     
}
*/

static PyObject* py_mahony(PyObject* self, PyObject* args) {
    float kp, ki, dt, gx, gy, gz, ax, ay, az, mx, my, mz;

    PyArg_ParseTuple(args, "ffffffffffff", &kp, &ki, &dt, &gx, &gy, &gz, &ax, &ay, &az, &mx, &my, &mz);

    O.update(kp, ki, dt, Vector(ax, ay, az), Vector(gx, gy, gz), Vector(mx, my, mz));

    Quaternion q = O.quaternion();

    PyObject * result = PyTuple_New(4);
    PyTuple_SET_ITEM(result, 0, PyFloat_FromDouble(q.a));
    PyTuple_SET_ITEM(result, 1, PyFloat_FromDouble(q.b));
    PyTuple_SET_ITEM(result, 2, PyFloat_FromDouble(q.c));
    PyTuple_SET_ITEM(result, 3, PyFloat_FromDouble(q.d));

    return result;
}

static PyMethodDef c_methods[] = {    
/*    {"get_segmentation", py_getSegmantation, METH_VARARGS},
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
*/  {"mahony", py_mahony, METH_VARARGS},



    {NULL, NULL}
};

extern "C" {
    PyMODINIT_FUNC initc_wrap(void) {
/*        QEvt e;

        e.sig = MAX_PILL_SIG;
        QMSM_DISPATCH(the_hand, &e);        
*/        
        (void) Py_InitModule("c_wrap", c_methods);
    }
}
