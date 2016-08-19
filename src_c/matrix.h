#ifndef Matrix_h
#define Matrix_h

#include "knowledge.h"

void copyPoint(const float source[DIMENTION], float dest[DIMENTION]);
void addVec(float vr[DIMENTION], const float v1[DIMENTION], const float v2[DIMENTION]);
void subVec(float vr[DIMENTION], const float v1[DIMENTION], const float v2[DIMENTION]);
void scaleVec(float vr[DIMENTION], const float v[DIMENTION], const float k);
float norm(const float v[DIMENTION]);
void normInplace(float v[DIMENTION]);
float dot(const float v1[DIMENTION], const float v2[DIMENTION]);
void cross(float vr[DIMENTION], const float v1[DIMENTION], const float v2[DIMENTION]);
void adjustRange(float range[2][DIMENTION], const float position[DIMENTION]);
void adjustVec(float vr[DIMENTION], const float m[DIMENTION][DIMENTION], const float v[DIMENTION]);
void adjustVecT(float vr[DIMENTION], const float v[DIMENTION], const float m[DIMENTION][DIMENTION]);
void multiply(float mr[DIMENTION][DIMENTION], const float m1[DIMENTION][DIMENTION], const float m2[DIMENTION][DIMENTION]);

#endif
