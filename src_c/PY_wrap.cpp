#include <stdio.h>
#include <Python.h>
#include "splitter.h"
#include "unify_definition.h"
#include "imu.h"
#include "state_machine.h"

#include <stdint.h>
#include "generation_light.h"

#include "full_state_machine.h"

#include "orientation.h"

#include "calibration.h"
#include "stroke_export.h"
#include "split_state_export.h"
#include "wrap_utils.h"
#include "state_keeper.h"
#include "bsp.h"
#include "lightsaber_out.h"
#include "lightsaber.h"

static Splitter splitter = Splitter();
static IMU imu = IMU();
static StateMachine SM = StateMachine(0);
static StateKeeper SK = StateKeeper();

static FullStateMachine FSM = FullStateMachine(0);

static Orientation O = Orientation();

static Lightsaber LS = Lightsaber();

static int hum = 0;

void boom(int level) {
    printf("BOOM! %d\n", level);
}
void setHumLevel(int level) {
    hum = level;
}

void RGB_blink_slow(uint8_t Color) {
    SK.setColor((int) Color);
    SK.setBlinkSpeed(1);
}

void RGB_blink_fast(uint8_t Color) {
    SK.setColor((int) Color);
    SK.setBlinkSpeed(2);
}

void RGB_blink_stop() {
    SK.setBlinkSpeed(0);
}

void vibro(uint8_t Power) {
    SK.setVibro((int) Power);
}


void exportStroke(Vector stroke[SEGMENTATION]) {
    SK.setStroke(stroke);
}

void exportSplitState(int state) {
    SK.setSplitterState(state);        
}

static PyObject* py_getSegmantation(PyObject* self, PyObject* args) {
    return PyInt_FromLong(SEGMENTATION);
}

static PyObject* py_getStrokeMaxLength(PyObject* self, PyObject* args) {
    return PyInt_FromLong(STROKE_MAX_LENGTH);
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

    float outGyro;
    float outAcc[DIMENTION];
    float outHeading[DIMENTION];    

    PyArg_ParseTuple(args, "fO!O!O!i", &delta, &PyList_Type, &accObj, &PyList_Type, &gyroObj, &PyList_Type, &magObj, &axis);

    Vector a = PyListToVector(accObj);
    Vector g = PyListToVector(gyroObj);
    Vector m = PyListToVector(magObj);

    ImuAnswer answer = imu.calc(delta, a, g, m, axis);

    int inactive = answer.active ? 0 : 1;

    outGyro = answer.gyro;

    PyObject * outAccObj = vectorToPyList(answer.acc);
    PyObject * outHeadingObj = vectorToPyList(answer.heading);
    
    PyObject * result = PyTuple_New(4);
    PyTuple_SET_ITEM(result, 0, PyBool_FromLong(inactive));
    PyTuple_SET_ITEM(result, 1, PyFloat_FromDouble(outGyro));
    PyTuple_SET_ITEM(result, 2, outAccObj);
    PyTuple_SET_ITEM(result, 3, outHeadingObj);

    return result;
}


static PyObject* py_setSMData(PyObject* self, PyObject* args) {
    float delta;

    PyObject * accObj;
    PyObject * gyroObj;
    PyObject * magObj;   

    PyArg_ParseTuple(args, "fO!O!O!", &delta, &PyList_Type, &accObj, &PyList_Type, &gyroObj, &PyList_Type, &magObj);

    Vector a = PyListToVector(accObj);
    Vector g = PyListToVector(gyroObj);
    Vector m = PyListToVector(magObj);

    SK.clearStroke();

    PyObject * result = PyTuple_New(3);
    PyTuple_SET_ITEM(result, 0, PyInt_FromLong(SM.setData(delta, a, g, m)));

    PyTuple_SET_ITEM(result, 1, PyInt_FromLong(SK.getSplitterState()));
    
    if (SK.isStrokeSet() != 0) {
        PyTuple_SET_ITEM(result, 2, SK.getStroke());
    } else {
        PyTuple_SET_ITEM(result, 2, PyInt_FromLong(0));
    }

    return result;
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

    PyObject * accObj;
    PyObject * gyroObj;
    PyObject * magObj;   

    PyArg_ParseTuple(args, "fO!O!O!", &delta, &PyList_Type, &accObj, &PyList_Type, &gyroObj, &PyList_Type, &magObj);

    Vector a = PyListToVector(accObj);
    Vector g = PyListToVector(gyroObj);
    Vector m = PyListToVector(magObj);

    bool active = FSM.setData(delta, a, g, m);

    PyObject * result = PyTuple_New(4);

    PyTuple_SET_ITEM(result, 0, PyBool_FromLong(active));
    PyTuple_SET_ITEM(result, 1, PyInt_FromLong(SK.getColor()));
    PyTuple_SET_ITEM(result, 2, PyInt_FromLong(SK.getBlinkSpeed()));
    PyTuple_SET_ITEM(result, 3, PyInt_FromLong(SK.getVibro()));

   return result;     
}


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

static PyObject* py_setLightsaberData(PyObject* self, PyObject* args) {
    float delta;

    PyObject * accObj;
    PyObject * gyroObj;
    PyObject * magObj;   

    PyArg_ParseTuple(args, "fO!O!O!", &delta, &PyList_Type, &accObj, &PyList_Type, &gyroObj, &PyList_Type, &magObj);

    Vector a = PyListToVector(accObj);
    Vector g = PyListToVector(gyroObj);
    Vector m = PyListToVector(magObj);

    LS.setData(delta, a, g, m);

    return PyInt_FromLong(hum);
}


static PyMethodDef c_methods[] = {    
    {"set_sensor_data", py_setSensorData, METH_VARARGS},
    {"set_sm_data", py_setSMData, METH_VARARGS},
    {"set_fsm_data", py_setFSMData, METH_VARARGS},    
    {"set_signal", py_setSignal, METH_VARARGS},
    {"get_q_user_sig", py_getQ_USER_SIG, METH_VARARGS},
    {"mahony", py_mahony, METH_VARARGS},
    {"set_lightsaber_data", py_setLightsaberData, METH_VARARGS},
    {NULL, NULL}
};

extern "C" {
    PyMODINIT_FUNC initc_wrap(void) {

        imu.init();
        SM.init();
        FSM.init();
        LS.init();

        Biotics_ctor();
        QMSM_INIT(the_biotics, (QEvt *)0);
        Hand_ctor();
        QMSM_INIT(the_hand, (QEvt *)0);

        QEvt e;

        e.sig = MAX_PILL_SIG;

        QMSM_DISPATCH(the_hand, &e);

        e.sig = MAX_PILL_SIG;

        QMSM_DISPATCH(the_hand, &e);             
       
        (void) Py_InitModule("c_wrap", c_methods);
    }
}
