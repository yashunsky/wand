#ifndef StateMachine_h
#define StateMachine_h

#include "knowledge.h"
#include "imu.h"
#include "splitter.h"

class StateMachine {
private:
    int axis;
    IMU imu;
    Splitter splitter;

public:
    StateMachine(int axis);
    int setData(const float delta, 
        const float accIn[DIMENTION], const float gyroIn[DIMENTION], const float magIn[DIMENTION],
        const unsigned long access);

};
#endif