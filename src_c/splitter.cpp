#include "splitter.h"
#include "matrix.h"
#include "filter.h"
#include "unify_definition.h"
#include "stroke_export.h"
#include "split_state_export.h"
#include <math.h>
#include <stdio.h>



Splitter::Splitter() {
    strokeLength = -1;
    filter = Filter();
}

void Splitter::resetSize() {
    int j;
    for (j=0; j<2; j++){ 
        positionsRange[j] = Vector();
    }
    position = Vector();
    speed = Vector();
}

void Splitter::processSize(const Vector accel, const float delta) {
    Vector at;
    Vector at2;
    Vector vt;
    Vector deltaP;

    at = accel * delta;
    at2 = accel * (delta * delta / 2);

    speed += at;

    vt = speed * delta;

    deltaP = vt + at2;

    position += deltaP;

    positionsRange[0].x = fminf(positionsRange[0].x, position.x);
    positionsRange[1].x = fmaxf(positionsRange[1].x, position.x);

    positionsRange[0].y = fminf(positionsRange[0].y, position.y);
    positionsRange[1].y = fmaxf(positionsRange[1].y, position.y);

    positionsRange[0].z = fminf(positionsRange[0].z, position.z);
    positionsRange[1].z = fmaxf(positionsRange[1].z, position.z);   
}

int Splitter::setIMUData(const float delta, const ImuAnswer answer) {

    float dimention;
    float yNorm;

    Vector x;
    Vector y;
    Vector z;

    int result = -1;

    processSize(filter.setInput(answer.acc, delta), delta);

    if (answer.gyro > GYRO_MIN) {
        exportSplitState(IN_ACTION);
        timer = GYRO_TIMEOUT;
        if (strokeLength == 0) {
            y = Vector(answer.heading.x, answer.heading.y, 0);
            z = Vector(0.0, 0.0, 1.0);

            yNorm = y.norm2();

            if (yNorm != 0) {
                y *= 1 / yNorm;
            } else {
                return -1;
            }

            x = crossProduct(y, z);
            x.normalize2();

            M = Matrix(x, y, z);

            resetSize();
        }

        buffer[strokeLength] = answer.heading * M;

        strokeLength += 1;
        if (strokeLength > STROKE_MAX_LENGTH) {
            strokeLength = STROKE_MAX_LENGTH + 1;
        }
    } else {
        timer--;
        if (timer == 0) {

            dimention = (positionsRange[1] - positionsRange[0]).norm2();  

            //printf("%f\n", dimention);

            if (MIN_STROKE_LENGTH > strokeLength) {
                exportSplitState(TOO_SHORT);
            } else if (strokeLength >= STROKE_MAX_LENGTH) {
                exportSplitState(TOO_LONG);
            } else if (dimention < MIN_DIMENTION) {
                exportSplitState(TOO_SMALL);
            } else {
                result = getStroke(buffer, strokeLength);              
            }

            strokeLength = 0;
        } else if (timer < 0) {
            exportSplitState(NOT_IN_ACTION);
            timer = -1;
        }
    }

    return result;
}
