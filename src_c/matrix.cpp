#include <math.h>
#include "matrix.h"

void copyPoint(const float source[DIMENTION], float dest[DIMENTION]) {
    int i;
    for (i = 0; i < DIMENTION; i++) {
        dest[i] = source[i];
    }    
}

void addVec(float vr[DIMENTION], const float v1[DIMENTION], const float v2[DIMENTION]) {
    int i;
    for (i=0; i<DIMENTION; i++) {
        vr[i] = v1[i] + v2[i]; 
    }  
}

void subVec(float vr[DIMENTION], const float v1[DIMENTION], const float v2[DIMENTION]) {
    int i;
    for (i=0; i<DIMENTION; i++) {
        vr[i] = v1[i] - v2[i]; 
    }  
}

void scaleVec(float vr[DIMENTION], const float v[DIMENTION], const float k) {
    int i;
    for (i=0; i<DIMENTION; i++) {
        vr[i] = v[i] * k; 
    }  
}

float norm(const float v[DIMENTION]) {
    int i;
    float sum = 0;
    for (i=0; i<DIMENTION; i++) {
        sum += v[i] * v[i];
    }
    return sqrt(sum);
}

void normInplace(float v[DIMENTION]) {
    scaleVec(v, v, 1.0 / norm(v));
}

float dot(const float v1[DIMENTION], const float v2[DIMENTION]) {
    int i;
    float sum = 0;
    for (i=0; i<DIMENTION; i++) {
        sum += v1[i] * v2[i];
    }
    return sum;
}

void cross(float vr[3], const float v1[3], const float v2[3]) {
    vr[0] = v1[1] * v2[2] - v1[2] * v2[1];
    vr[1] = - (v1[0] * v2[2] - v1[2] * v1[0]);
    vr[2] = v1[0] * v2[1] - v1[1] * v2[0];
}

void adjustRange(float range[2][DIMENTION], const float position[DIMENTION]) {
    int i;
    for (i=0; i<DIMENTION; i++) {
        range[0][i] = fminf(range[0][i], position[i]);
        range[1][i] = fmaxf(range[1][i], position[i]);
    }
}

void adjustVec(float vr[DIMENTION], const float m[DIMENTION][DIMENTION], const float v[DIMENTION]) {
    int i;
    float sum;
    for (i=0; i<DIMENTION; i++) {
        vr[i] = dot(m[i], v);
    }
}
