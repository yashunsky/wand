#ifndef StateKeeper_h
#define StateKeeper_h

#include "wrap_utils.h"
#include "knowledge.h"

class StateKeeper {
private:
    int splitterState;
    float stroke[SEGMENTATION][DIMENTION];
    int strokeSet;
    int color;
    int blinkSpeed;
    int vibro;

public:
    StateKeeper();
    void setSplitterState(int state);
    int getSplitterState();
    void setStroke(float inputStroke[SEGMENTATION][DIMENTION]);
    PyObject * getStroke();
    void clearStroke();
    int isStrokeSet();

    void setColor(int color);
    int getColor();
    void setBlinkSpeed(int speed);
    int getBlinkSpeed();
    void setVibro(int vibro);
    int getVibro();
};
#endif
