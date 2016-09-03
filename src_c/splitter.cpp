#include "splitter.h"
#include "matrix.h"
#include "filter.h"
#include "unify_definition.h"
#include <stdio.h>

Splitter::Splitter() {
    strokeLength = -1;
    filter = Filter();
}

void Splitter::resetSize() {
    int i,j;
    for (i=0; i<DIMENTION; i++) {
        for (j=0; j<2; j++){ 
            positionsRange[j][i] = 0;
        }
        position[i] = 0;
        speed[i] = 0;
    }
}

void Splitter::processSize(const float accel[DIMENTION], const float delta) {
    float at[DIMENTION];
    float at2[DIMENTION];
    float vt[DIMENTION];
    float deltaP[DIMENTION];

    scaleVec(at, accel, delta);
    scaleVec(at2, accel, (delta * delta) / 2);

    addVec(speed, speed, at);

    scaleVec(vt, speed, delta);

    addVec(deltaP, vt, at2);

    addVec(position, position, deltaP);

    adjustRange(positionsRange, position);    
}

int Splitter::setIMUData(const float delta, const float gyro, const float accel[DIMENTION], const float heading[DIMENTION]) {
    float dimention;
    float dimentionVec[DIMENTION];
    float newPoint[DIMENTION];
    float x[DIMENTION];
    float y[DIMENTION];
    float z[DIMENTION];
    float yNorm;

    int result = -1;

    processSize(filter.setInput(accel, delta), delta);

    if (gyro > GYRO_MIN) {
        timer = GYRO_TIMEOUT;
        if (strokeLength == 0) {
            y[0] = heading[0];
            y[1] = heading[1];
            y[2] = 0;
            
            z[0] = 0;
            z[1] = 0;
            z[2] = 1;

            yNorm = norm(y);

            if (yNorm != 0) {
                scaleVec(y, y, 1 / yNorm);
            } else {
                return -1;
            }

            cross(x, y, z);
            normInplace(x);

            copyPoint(x, M[0]);
            copyPoint(y, M[1]);
            copyPoint(z, M[2]);

            resetSize();
        }

        adjustVec(newPoint, M, heading);
        copyPoint(newPoint, buffer[strokeLength]);
        strokeLength += 1;
        if (strokeLength > STROKE_MAX_LENGTH) {
            strokeLength = STROKE_MAX_LENGTH + 1;
        }
    } else {
        timer--;
        if (timer == 0) {
            subVec(dimentionVec, positionsRange[1], positionsRange[0]);
            dimention = norm(dimentionVec);  

            if ((MIN_STROKE_LENGTH < strokeLength) && (strokeLength <= STROKE_MAX_LENGTH) && (dimention > MIN_DIMENTION)) {
                result = getStroke(buffer, strokeLength);
            }
            strokeLength = 0;
        } else if (timer < 0) {
            timer = -1;
        }
    }

    return result;
}
