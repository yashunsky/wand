#ifndef UnifyDefinition_h
#define UnifyDefinition_h

#include "knowledge.h"
#include "ahrsmath.h"

float getDist(const float a[DIMENTION], const float b[DIMENTION]);
void unifyStroke(Vector stroke[STROKE_MAX_LENGTH], Vector newStroke[SEGMENTATION], int length);
float checkStroke(float stroke[SEGMENTATION][DIMENTION], const float description[SEGMENTATION][DIMENTION]);
int getStroke(float stroke[STROKE_MAX_LENGTH][DIMENTION], int length);

#endif
