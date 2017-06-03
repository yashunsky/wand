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
    int calibrationDone;

public:
    StateMachine(int axis);
    void init();
    int setData(const float dt, const Vector acc, const Vector gyro, const Vector mag);
};
#endif
