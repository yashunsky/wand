#include "state_machine.h"
#include "ahrsmath.h"
#include "calibration.h"

StateMachine::StateMachine(int axis) : imu(getAOffset(), getGOffset(), getGOffset()){
    this->axis = axis;
}


int StateMachine::setData(const float dt, const Vector acc, const Vector gyro, const Vector mag){

    ImuAnswer answer = imu.calc(dt, acc, gyro, mag, axis);

    if (!answer.active) {
        return CALIBRATION;
    }

    return splitter.setIMUData(dt, answer) + STATES_OFFSET;
}
