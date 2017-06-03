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
    int setData(const float dt, const Vector acc, const Vector gyro, const Vector mag);
};
#endif
