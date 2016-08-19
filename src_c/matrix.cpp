#include <math.h>
#include "matrix.h"

void copyPoint(const float source[DIMENTION], float dest[DIMENTION]) {
    for (int i = 0; i < DIMENTION; i++) {
        dest[i] = source[i];
    }    
}

void addVec(float vr[DIMENTION], const float v1[DIMENTION], const float v2[DIMENTION]) {
    for (int i=0; i<DIMENTION; i++) {
        vr[i] = v1[i] + v2[i]; 
    }  
}

void subVec(float vr[DIMENTION], const float v1[DIMENTION], const float v2[DIMENTION]) {
    for (int i=0; i<DIMENTION; i++) {
        vr[i] = v1[i] - v2[i]; 
    }  
}

void scaleVec(float vr[DIMENTION], const float v[DIMENTION], const float k) {
    for (int i=0; i<DIMENTION; i++) {
        vr[i] = v[i] * k; 
    }  
}

float norm(const float v[DIMENTION]) {
    float sum = 0;
    for (int i=0; i<DIMENTION; i++) {
        sum += v[i] * v[i];
    }
    return sqrt(sum);
}

void normInplace(float v[DIMENTION]) {
    scaleVec(v, v, 1.0 / norm(v));
}

float dot(const float v1[DIMENTION], const float v2[DIMENTION]) {
    float sum = 0;
    for (int i=0; i<DIMENTION; i++) {
        sum += v1[i] * v2[i];
    }
    return sum;
}

void cross(float vr[3], const float v1[3], const float v2[3]) {
    vr[0] = v1[1] * v2[2] - v1[2] * v2[1];
    vr[1] = - (v1[0] * v2[2] - v1[2] * v2[0]);
    vr[2] = v1[0] * v2[1] - v1[1] * v2[0];
}

void adjustRange(float range[2][DIMENTION], const float position[DIMENTION]) {
    for (int i=0; i<DIMENTION; i++) {
        range[0][i] = fminf(range[0][i], position[i]);
        range[1][i] = fmaxf(range[1][i], position[i]);
    }
}

void adjustVec(float vr[DIMENTION], const float m[DIMENTION][DIMENTION], const float v[DIMENTION]) {
    for (int i=0; i<DIMENTION; i++) {
        vr[i] = dot(m[i], v);
    }
}

void adjustVecT(float vr[DIMENTION], const float v[DIMENTION], const float m[DIMENTION][DIMENTION]) {
    for (int i=0; i<DIMENTION; i++) {
        vr[i] = 0;
        for (int j=0; j<DIMENTION; j++) {
            vr[i] += m[i][j] * v[j];   
        }
    }
}

void multiply(float mr[DIMENTION][DIMENTION], const float m1[DIMENTION][DIMENTION], const float m2[DIMENTION][DIMENTION]) {
    for (int i=0; i<DIMENTION; i++) {
        for (int j=0; j<DIMENTION; j++) {
            float sum = 0;
            for (int k=0; k<DIMENTION; k++) {
                sum += m1[i][k] * m2[k][j];
            }
            mr[i][j] = sum;
        }
    }
}
