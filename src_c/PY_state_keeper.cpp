#include "state_keeper.h"

StateKeeper::StateKeeper() {
    splitterState = NOT_IN_ACTION;
    stroke = NULL;
}

void StateKeeper::setSplitterState(int state) {
    splitterState = state;
}
int StateKeeper::getSplitterState() {
    return splitterState;
}
void StateKeeper::setStroke(float inputStroke[SEGMENTATION][DIMENTION]) {
    stroke = arrayToPyList(&inputStroke[0][0], SEGMENTATION, DIMENTION);
}

PyObject * StateKeeper::getStroke() {
    return stroke;
}

void StateKeeper::clearStroke() {
    if (stroke != NULL) {
        Py_DECREF(stroke);
    }
    stroke = NULL;
}
