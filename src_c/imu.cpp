#include "imu.h"
#include "matrix.h"
#include <math.h>
#include <stdio.h>

IMU::IMU(const Vector aOffset, const Vector gOffset, const Vector mOffset) {
    this->aOffset = aOffset;
    this->gOffset = gOffset;
    this->mOffset = mOffset; 
    this->time = 0;  
}

bool IMU::calc(const float dt, 
               const float accIn[DIMENTION], const float gyroIn[DIMENTION], const float magIn[DIMENTION],
               int axis,
               float * gyroOut, float accOut[DIMENTION], float headingOut[DIMENTION])
{
    Vector aIn = (Vector(*accIn) - aOffset);
    Vector gIn = (Vector(*gyroIn) - gOffset) * GYRO_SCALE;
    Vector mIn = (Vector(*magIn) - mOffset) * ACC_SCALE;

    *gyroOut = gIn.norm();

    time += dt;

    bool inCalibration = time > INIT_EDGE;

    float kp = inCalibration ? KP_WORK : KP_INIT;
    float ki = inCalibration ? KI_WORK : KI_INIT;

    orientation.update(kp, ki, dt, aIn, gIn, mIn);

    Matrix M = orientation.quaternion().toMatrix();

    Vector heading = M.T()[axis];

    Vector aOut = aIn * M - Vector(0.0, G_CONST, 0.0);

    headingOut[0] = heading.x;
    headingOut[1] = heading.y;
    headingOut[2] = heading.z;

    accOut[0] = aOut.x;
    accOut[1] = aOut.y;
    accOut[2] = aOut.z;

    return inCalibration;
}