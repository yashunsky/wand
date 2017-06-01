#include "state_keeper.h"

StateKeeper::StateKeeper() {
    splitterState = NOT_IN_ACTION;
    strokeSet = 0;
    for (int i=0; i<SEGMENTATION; i++) {
        for (int j=0; j<DIMENTION; j++) {
            stroke[i][j] = 0.0;
        }
    }
}

void StateKeeper::setSplitterState(int state) {
    splitterState = state;
}
int StateKeeper::getSplitterState() {
    return splitterState;
}
void StateKeeper::setStroke(float inputStroke[SEGMENTATION][DIMENTION]) {
    strokeSet = 1;
    for (int i=0; i<SEGMENTATION; i++) {
        for (int j=0; j<DIMENTION; j++) {
            stroke[i][j] = inputStroke[i][j];
        }
    } 
}

PyObject * StateKeeper::getStroke() {
    return arrayToPyList(&stroke[0][0], SEGMENTATION, DIMENTION);
}

void StateKeeper::clearStroke() {
    strokeSet = 0;
}

int StateKeeper::isStrokeSet() {
    return strokeSet;
}