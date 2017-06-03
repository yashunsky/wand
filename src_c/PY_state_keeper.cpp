#include "state_keeper.h"

StateKeeper::StateKeeper() {
    splitterState = NOT_IN_ACTION;
    strokeSet = 0;
    for (int i=0; i<SEGMENTATION; i++) {
        stroke[i] = Vector();
    }
    color = 0;
    blinkSpeed = 0;
    vibro = 0;
}

void StateKeeper::setSplitterState(int state) {
    splitterState = state;
}
int StateKeeper::getSplitterState() {
    return splitterState;
}
void StateKeeper::setStroke(Vector inputStroke[SEGMENTATION]) {
    strokeSet = 1;
    for (int i=0; i<SEGMENTATION; i++) {
        stroke[i] = inputStroke[i];
    } 
}

PyObject * StateKeeper::getStroke() {
    PyObject * newListObj = PyTuple_New(SEGMENTATION);
    for (int i=0; i<SEGMENTATION; i++) {
        PyTuple_SET_ITEM(newListObj, i, vectorToPyList(stroke[i]));
    }
    return newListObj;
}

void StateKeeper::clearStroke() {
    strokeSet = 0;
}

int StateKeeper::isStrokeSet() {
    return strokeSet;
}

void StateKeeper::setColor(int color) {
    this->color = color;
}

int StateKeeper::getColor() {
    return color;
}

void StateKeeper::setBlinkSpeed(int speed) {
    blinkSpeed = speed;
}

int StateKeeper::getBlinkSpeed() {
    return blinkSpeed;
}

void StateKeeper::setVibro(int vibro) {
    this->vibro = vibro;
}

int StateKeeper::getVibro() {
    return vibro;
}
