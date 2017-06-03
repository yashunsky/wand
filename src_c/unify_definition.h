#ifndef UnifyDefinition_h
#define UnifyDefinition_h

#include "knowledge.h"
#include "ahrsmath.h"

void unifyStroke(Vector stroke[STROKE_MAX_LENGTH], Vector newStroke[SEGMENTATION], int length);
float checkStroke(Vector stroke[SEGMENTATION], const Vector description[SEGMENTATION]);
int getStroke(Vector stroke[STROKE_MAX_LENGTH], int length);

#endif
