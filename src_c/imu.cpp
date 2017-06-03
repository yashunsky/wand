#include "imu.h"
#include "calibration.h"
#include <math.h>

ImuAnswer::ImuAnswer (bool active, float gyro, Vector acc, Vector heading) {
    this->active = active;
    this->gyro = gyro;
    this->acc = acc;
    this->heading = heading;
}

IMU::IMU() {
    aOffset = Vector();
    gOffset = Vector();
    mOffset = Vector(); 
    time = 0;  
}

void IMU::init() {
    this->aOffset = getAOffset();
    this->gOffset = getGOffset();
    this->mOffset = getMOffset(); 
    this->time = 0;     
}

ImuAnswer IMU::calc(const float dt, const Vector acc, const Vector gyro, const Vector mag, int axis)
{
    Vector aIn = (acc - aOffset) * ACC_SCALE;
    Vector gIn = (gyro - gOffset) * GYRO_SCALE;
    Vector mIn = (mag - mOffset);

    time += dt;

    bool inCalibration = time < INIT_EDGE;

    float kp = inCalibration ? KP_INIT : KP_WORK;
    float ki = inCalibration ? KI_INIT : KI_WORK;

    orientation.update(kp, ki, dt, aIn, gIn, mIn);

    Matrix M = orientation.quaternion().toMatrix();

    Vector heading = M.T()[axis];

    Vector aOut = aIn * M - Vector(0.0, 0.0, G_CONST);

    return ImuAnswer(!inCalibration, gIn.norm(), aOut, heading);
}
