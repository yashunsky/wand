#include "state_machine.h"
#include "ahrsmath.h"
#include "calibration.h"

StateMachine::StateMachine(int axis) {
    this->axis = axis;
    calibrationDone = 0;
}

void StateMachine::init() {
   imu.init(); 
}


int StateMachine::setData(const float dt, const Vector acc, const Vector gyro, const Vector mag){

    ImuAnswer answer = imu.calc(dt, acc, gyro, mag, axis);

    if (!answer.active) {
        return CALIBRATION;
    }
    if (calibrationDone == 0) {
        onCalibrationDone();
        calibrationDone = 1;
    }
    return splitter.setIMUData(dt, answer) + STATES_OFFSET;
}
