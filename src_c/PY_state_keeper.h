#ifndef StateKeeper_h
#define StateKeeper_h

#include "wrap_utils.h"
#include "knowledge.h"

class StateKeeper {
private:
    int splitterState;
    PyObject * stroke;

public:
    StateKeeper();
    void setSplitterState(int state);
    int getSplitterState();
    void setStroke(float inputStroke[SEGMENTATION][DIMENTION]);
    PyObject * getStroke();
    void clearStroke();
};
#endif
