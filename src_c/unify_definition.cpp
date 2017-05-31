#include <stdio.h>
#include <math.h>
#include "matrix.h"
#include "unify_definition.h"
#include "stroke_export.h"

float getDist(const float a[DIMENTION], const float b[DIMENTION]) {
    float delta = 0;
    float d;
    int i;

    for (i = 0; i < DIMENTION; i++) {
        d = a[i] - b[i];
        delta += d * d;
    }
    return sqrtf(delta);
}

void unifyStroke(float stroke[STROKE_MAX_LENGTH][DIMENTION], float newStroke[SEGMENTATION][DIMENTION], int length) {
    float strokeLengths[STROKE_MAX_LENGTH];
    float step;
    int i, j;
    int newStrokeId = 1;
    float nextLength;
    float * p1;
    float * p2;
    float delta;
    float coeff;

    strokeLengths[0] = 0;

    for (i = 1; i < length; i++) {
        strokeLengths[i] = strokeLengths[i - 1] + getDist(stroke[i - 1], stroke[i]);       
    }

    step = strokeLengths[length - 1] / (SEGMENTATION - 1);

    copyPoint(stroke[0], newStroke[0]);
    copyPoint(stroke[length - 1], newStroke[SEGMENTATION - 1]);

    nextLength = step;

    for (i = 1; i < length; i++) {
        while (strokeLengths[i] > nextLength) {
            p1 = stroke[i - 1];
            p2 = stroke[i];
            delta = strokeLengths[i] - strokeLengths[i - 1];
            coeff = delta == 0 ? 0 : (1 - ((strokeLengths[i] - nextLength) / delta));
            for (j = 0; j < DIMENTION; j++) {
                newStroke[newStrokeId][j] = p1[j] + (p2[j] - p1[j]) * coeff;
            }
            newStrokeId += 1;
            nextLength += step;
        }
    } 

}

float checkStroke(float stroke[SEGMENTATION][DIMENTION], const float description[SEGMENTATION][DIMENTION]) {
    float errors[SEGMENTATION];
    float mean = 0;
    float result = 0;
    float d;
    int i;

    for (i = 0; i < SEGMENTATION; i++) {
        errors[i] = getDist(stroke[i], description[i]);
        mean += errors[i];
    }

    mean /= SEGMENTATION;

    for (i = 0; i < SEGMENTATION; i++) {
        d = errors[i] - mean;
        result += d * d;
    }
    return sqrtf(result / SEGMENTATION);
}

int getStroke(float stroke[STROKE_MAX_LENGTH][DIMENTION], int length) {
    float unifiedStroke[SEGMENTATION][DIMENTION];
    unifyStroke(stroke, unifiedStroke, length);

    exportStroke(unifiedStroke);

    int i;
    float error;
    float min_error = -1;
    float second = -1;
    int strokeId = -1;
    for (i = 0; i < STROKES_COUNT; i++) {
        error = checkStroke(unifiedStroke, STROKES[i]);

        if (min_error < 0) {
            min_error = error;
            strokeId = i;
        } else if (error < min_error) {
            if (second < 0) {
                second = min_error;
            }
            min_error = error;
            strokeId = i;
        } else {
            if (second < 0) {
                second = error;
            }            
        }
    }
    if ((min_error != 0) && ((second / min_error) <= COMPARE_LIMIT)) {
        return -1;
    }
    return strokeId;
}
