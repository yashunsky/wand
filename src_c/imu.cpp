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
    Vector aIn = (Vector(accIn[0], accIn[1], accIn[2]) - aOffset) * ACC_SCALE;
    Vector gIn = (Vector(gyroIn[0], gyroIn[1], gyroIn[2]) - gOffset) * GYRO_SCALE;
    Vector mIn = (Vector(magIn[0], magIn[1], magIn[2]) - mOffset);

    *gyroOut = gIn.norm();

    time += dt;

    bool inCalibration = time < INIT_EDGE;

    float kp = inCalibration ? KP_INIT : KP_WORK;
    float ki = inCalibration ? KI_INIT : KI_WORK;

    orientation.update(kp, ki, dt, aIn, gIn, mIn);

    Matrix M = orientation.quaternion().toMatrix();

    Vector heading = M.T()[axis];

    Vector aOut = aIn * M - Vector(0.0, 0.0, G_CONST);

    headingOut[0] = heading.x;
    headingOut[1] = heading.y;
    headingOut[2] = heading.z;

    accOut[0] = aOut.x;
    accOut[1] = aOut.y;
    accOut[2] = aOut.z;

    return inCalibration;
}