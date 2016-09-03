#ifndef Splitter_h
#define Splitter_h

#include "knowledge.h"
#include "filter.h"

class Splitter {
private:
    int strokeLength;
    float M[DIMENTION][DIMENTION];
    float positionsRange[2][DIMENTION];
    float position[DIMENTION];
    float speed[DIMENTION];
    int timer;
    Filter filter;

    void resetSize();
    void processSize(const float accel[DIMENTION], const float delta);

public:
    float buffer[STROKE_MAX_LENGTH][DIMENTION];

    Splitter();
    int setIMUData(const float delta, const float gyro, const float accel[DIMENTION], const float heading[DIMENTION]);

};
#endif
