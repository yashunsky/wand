#include "filter.h"
#include "matrix.h"

Filter::Filter() {
    int i;
    for (i=0; i<DIMENTION; i++) {
        output[i] = 0;
    }
}

float* Filter::setInput(const float value[DIMENTION], const float delta) {
    int i;
    for (i=0; i<DIMENTION; i++) {
        output[i] = output[i] + (value[i] - output[i]) * delta / ACCELERATION_TIME_CONST;
    }
    return output;    
}
