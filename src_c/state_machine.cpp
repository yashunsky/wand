#include "state_machine.h"
#include "ahrsmath.h"
#include "calibration.h"

StateMachine::StateMachine(int axis) {
    this->axis = axis;
}

void StateMachine::init() {
   imu.init(); 
}


int StateMachine::setData(const float dt, const Vector acc, const Vector gyro, const Vector mag){

    ImuAnswer answer = imu.calc(dt, acc, gyro, mag, axis);

    if (!answer.active) {
        return CALIBRATION;
    }
    onCalibrationDone();
    return splitter.setIMUData(dt, answer) + STATES_OFFSET;
}
