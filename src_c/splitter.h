#ifndef Splitter_h
#define Splitter_h

#include "knowledge.h"
#include "filter.h"
#include "imu.h"
#include "ahrsmath.h"

class Splitter {
private:
    int strokeLength;
    Matrix M;
    Vector positionsRange[2];
    Vector position;
    Vector speed;
    int timer;
    Filter filter;

    void resetSize();
    void processSize(const Vector accel, const float delta);

public:
    Vector buffer[STROKE_MAX_LENGTH];

    Splitter();
    int setIMUData(const float delta, const ImuAnswer imuAnswer);

};
#endif
