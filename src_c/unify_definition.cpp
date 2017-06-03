#include <stdio.h>
#include <math.h>
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

float getDist(const Vector a, const Vector b) {
    return (a - b).norm2();
}

void unifyStroke(Vector stroke[STROKE_MAX_LENGTH], Vector newStroke[SEGMENTATION], int length) {
    float strokeLengths[STROKE_MAX_LENGTH];
    float step;
    int i, j;
    int newStrokeId = 1;
    float nextLength;
    Vector p1;
    Vector p2;
    float delta;
    float coeff;

    strokeLengths[0] = 0;

    for (i = 1; i < length; i++) {
        strokeLengths[i] = strokeLengths[i - 1] + getDist(stroke[i - 1], stroke[i]);       
    }

    step = strokeLengths[length - 1] / (SEGMENTATION - 1);

    newStroke[0] = stroke[0];
    newStroke[SEGMENTATION - 1] = stroke[length - 1];

    nextLength = step;

    for (i = 1; i < length; i++) {
        while (strokeLengths[i] > nextLength) {
            p1 = stroke[i - 1];
            p2 = stroke[i];
            delta = strokeLengths[i] - strokeLengths[i - 1];
            coeff = delta == 0 ? 0 : (1 - ((strokeLengths[i] - nextLength) / delta));

            newStroke[newStrokeId] = p1 + (p2 - p1) * coeff;

            newStrokeId += 1;
            nextLength += step;
        }
    } 

}



float checkStroke(Vector stroke[SEGMENTATION], const Vector description[SEGMENTATION]) {
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

int getStroke(Vector stroke[STROKE_MAX_LENGTH], int length) {

    Vector unifiedStroke[SEGMENTATION];

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
