#ifndef UnifyDefinition_h
#define UnifyDefinition_h

#include "strokes.h"

#define STROKE_MAX_LENGTH 256

float getDist(const float a[DIMENTION], const float b[DIMENTION]);
void unifyStroke(float stroke[STROKE_MAX_LENGTH][DIMENTION], float newStroke[SEGMENTATION][DIMENTION], int length);
float checkStroke(float stroke[SEGMENTATION][DIMENTION], const float description[SEGMENTATION][DIMENTION + 1]);
int getStroke(float stroke[STROKE_MAX_LENGTH][DIMENTION], int length, unsigned long access);

#endif
