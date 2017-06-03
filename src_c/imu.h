#ifndef IMU_h
#define IMU_h
#include "knowledge.h"
#include "orientation.h"
#include "ahrsmath.h"

class ImuAnswer
{
public:
    bool active;
    float gyro;
    Vector acc;
    Vector heading;
    ImuAnswer(bool active, float gyro, Vector acc, Vector heading);
};

class IMU {
private:
    Vector aOffset;
    Vector gOffset;
    Vector mOffset;

    float time;

    Orientation orientation;
public:
    IMU();
    void init();
    ImuAnswer calc(const float dt, const Vector acc, const Vector gyro, const Vector mag, int axis);

};

#endif
