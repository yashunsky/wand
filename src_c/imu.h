#ifndef IMU_h
#define IMU_h
#include "knowledge.h"
#include "orientation.h"
#include "ahrsmath.h"

class IMU {
private:
    Vector aOffset;
    Vector gOffset;
    Vector mOffset;

    float time;

    Orientation orientation;
public:
    IMU(const Vector aOffset, const Vector gOffset, const Vector mOffset);
    bool calc(const float dt, 
              const float accIn[DIMENTION], const float gyroIn[DIMENTION], const float magIn[DIMENTION],
              int axis,
              float * gyroOut, float accOut[DIMENTION], float headingOut[DIMENTION]);

};
#endif
