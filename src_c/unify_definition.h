#ifndef UnifyDefinition_h
#define UnifyDefinition_h

#define SEGMENTATION 32
#define STROKE_MAX_LENGTH 256
#define DIMENTION 3

float getDist(float a[DIMENTION], float b[DIMENTION]);
void unify_stroke(float stroke[STROKE_MAX_LENGTH][DIMENTION], float newStroke[SEGMENTATION][DIMENTION], int length);
float checkStroke(float stroke[SEGMENTATION][DIMENTION], float description[SEGMENTATION][DIMENTION + 1]);

#endif