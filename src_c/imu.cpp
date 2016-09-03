#include "imu.h"
#include "matrix.h"
#include <math.h>
#include <stdio.h>

IMU::IMU() {
    resetCalibration();
}

bool IMU::calc(const float delta, 
               const float accIn[DIMENTION], const float gyroIn[DIMENTION], const float magIn[DIMENTION],
               int axis,
               float * gyroOut, float accOut[DIMENTION], float headingOut[DIMENTION])
{
    float accInner[DIMENTION];
    scaleVec(accInner, accIn, ACCELEROMETER_SCALE);

    if (inCalibration) {
        recalibration(accInner, gyroIn, magIn);
    } else {
        mainLoop(delta, accInner, gyroIn, magIn);
    }

    getGlobalAcceleration(accOut);
    getHeading(axis, headingOut);

    * gyroOut = gyroNorm;

    return inCalibration;
}

void IMU::resetCalibration() {
    inCalibration = true;
    calibrationCounter = 0;
    stacksReady = false;
    magHeading = 0;
    gyroNorm = 0;

    for (int i=0; i<DIMENTION; i++) {
        omegaP[i] = 0;
        omegaI[i] = 0;
        angles[i] = 0;
        acceleration[i] = 0;

        for (int j=0; j<DIMENTION; j++) {
            dcmMatrix[i][j] = i == j ? 1 : 0;
        }
    }

    acceleration[2] = GRAVITY;
}

void IMU::recalibration(const float acc[DIMENTION], const float gyro[DIMENTION], const float mag[DIMENTION]) {
    float gAxis[DIMENTION];

    copyPoint(acc, aStack[calibrationCounter]);
    copyPoint(gyro, gStack[calibrationCounter]);
    calibrationCounter++;

    if (calibrationCounter == CALIBRATION_LENGTH) {
        stacksReady = true;
    }

    calibrationCounter %= CALIBRATION_LENGTH;

    if (!stacksReady) {
        return;
    }

    calcMean(aStack, accelerometerReadingsOffset);
    calcMean(gStack, gyroscopeReadingsOffset);

    float aDeviation = calcDeviation(aStack, accelerometerReadingsOffset);
    float gDeviation = calcDeviation(gStack, gyroscopeReadingsOffset);

    if (( aDeviation > ACCELEROMETER_DIVIATION) || (gDeviation > GYROSCOPE_DIVIATION)) {
        return;
    }

    scaleVec(gAxis, accelerometerReadingsOffset, (float) GRAVITY / norm(accelerometerReadingsOffset));
    subVec(accelerometerReadingsOffset, accelerometerReadingsOffset, gAxis);

    inCalibration = false;
}

void IMU::mainLoop(const float delta, const float accIn[DIMENTION], const float gyroIn[DIMENTION], const float magIn[DIMENTION]) {
    float acc[DIMENTION];
    float gyro[DIMENTION];

    subVec(acc, accIn, accelerometerReadingsOffset);
    subVec(gyro, gyroIn, gyroscopeReadingsOffset);

    copyPoint(acc, acceleration);
    gyroNorm = norm(gyro);

    scaleVec(gyro, gyro, GYRO_GAIN);

    magHeading = compassHeading(magIn);

    updateDcmMatrix(delta, gyro);

    float accelWeight = calculateAccelWeight(acc);

    float errorYaw[DIMENTION];
    float errorRollPitch[DIMENTION];
    calculateError(acc, errorYaw, errorRollPitch);

    driftCorrection(accelWeight, errorYaw, errorRollPitch);

    eulerAngles();
}

void IMU::getGlobalAcceleration(float acc[DIMENTION]) {
    adjustVecT(acc, acceleration, dcmMatrix);
    scaleVec(acc, acc, G_CONST / GRAVITY);
    acc[DIMENTION - 1] -= G_CONST;
}

void IMU::getHeading(int axis, float heading[DIMENTION]) {
    for (int i=0; i<DIMENTION; i++) {
        heading[i] = dcmMatrix[i][axis];
    }

}

void IMU::calcMean(const float data[CALIBRATION_LENGTH][DIMENTION], float mean[DIMENTION]) {
    for (int i=0; i<DIMENTION; i++) {
        float sum = 0;
        for (int j=0; j<CALIBRATION_LENGTH; j++) {
            sum += data[j][i];
        }
        mean[i] = sum / CALIBRATION_LENGTH;
    }
}

float IMU::calcDeviation(const float data[CALIBRATION_LENGTH][DIMENTION], const float mean[DIMENTION]) {
    float maxDeviation = 0;

    for (int i=0; i<DIMENTION; i++) {
        float sum = 0;
        for (int j=0; j<CALIBRATION_LENGTH; j++) {
            float delta = data[j][i] - mean[i];
            sum += delta * delta;
        }
        float deviation = sqrtf(sum / (CALIBRATION_LENGTH));
        if (deviation > maxDeviation) {
            maxDeviation = deviation;
        }
    }

    return maxDeviation;
}

float IMU::compassHeading(const float mag[DIMENTION]) {
    float cosRoll = cosf(angles[0]);
    float sinRoll = sinf(angles[0]);
    float cosPitch = cosf(angles[1]);
    float sinPitch = sinf(angles[1]);

    float magnetsNorm[DIMENTION];

    float magX, magY;

    for (int i=0; i<DIMENTION; i++) {
        magnetsNorm[i] = ((mag[i] - MAGNETS_BOUNDARIES[0][i]) / (MAGNETS_BOUNDARIES[1][i] - MAGNETS_BOUNDARIES[0][i])) - MAGNETS_OFFSET;
    }

    magX = (magnetsNorm[0] * cosPitch + magnetsNorm[1] * sinRoll * sinPitch + magnetsNorm[2] * cosRoll * sinPitch);
    magY = (magnetsNorm[1] * cosRoll - magnetsNorm[2] * sinRoll);

    return atan2f(-magY, magX);
}

void IMU::updateDcmMatrix(const float delta, const float gyro[DIMENTION]) {
    float omega[DIMENTION];
    addVec(omega, omegaI, omegaP);
    addVec(omega, omega, gyro);
    scaleVec(omega, omega, delta);

    float updateMatrix[DIMENTION][DIMENTION] =
        {{        1, -omega[2],  omega[1]},
         { omega[2],         1, -omega[0]},
         {-omega[1],  omega[0],         1}};

    multiply(dcmMatrix, dcmMatrix, updateMatrix);

    float temporary[DIMENTION][DIMENTION];
    float error = -dot(dcmMatrix[0], dcmMatrix[1]) * 0.5;

    scaleVec(temporary[0], dcmMatrix[1], error);
    addVec(temporary[0], temporary[0], dcmMatrix[0]);

    scaleVec(temporary[1], dcmMatrix[0], error);
    addVec(temporary[1], temporary[1], dcmMatrix[1]);

    cross(temporary[2], temporary[0], temporary[1]);

    for (int i=0; i<DIMENTION; i++) {
        renorm(dcmMatrix[i], temporary[i]);
    }
}

float IMU::calculateAccelWeight(const float acc[DIMENTION]) {
    float accelMagnitude = norm(acc) / GRAVITY;
    float accelWeight = 1 - 2 * fabs(1 - accelMagnitude);

    if (accelWeight < 0) {return 0;}
    if (accelWeight > 1) {return 1;}
    return accelWeight;
}

void IMU::calculateError(const float acc[DIMENTION], float errorYaw[DIMENTION], float errorRollPitch[DIMENTION]) {
    float magHeadingX = cosf(magHeading);
    float magHeadingY = sinf(magHeading);
    float errorCourse = ((dcmMatrix[0][0] * magHeadingY) - (dcmMatrix[1][0] * magHeadingX));

    scaleVec(errorYaw, dcmMatrix[2], errorCourse);
    cross(errorRollPitch, acc, dcmMatrix[2]);
}

void IMU::driftCorrection(float accelWeight, float errorYaw[DIMENTION], float errorRollPitch[DIMENTION]) {
    float scaledOmegaP[DIMENTION];
    float scaledOmegaI[DIMENTION];

    float additionalOmegaI[DIMENTION];

    scaleVec(scaledOmegaP, errorYaw, KP_YAW);
    scaleVec(omegaP, errorRollPitch, KP_ROLLPITCH * accelWeight);
    addVec(omegaP, omegaP, scaledOmegaP);

    scaleVec(scaledOmegaI, errorYaw, KI_YAW); 
    scaleVec(additionalOmegaI, errorRollPitch, KI_ROLLPITCH * accelWeight);

    addVec(omegaI, omegaI, additionalOmegaI);
    addVec(omegaI, omegaI, scaledOmegaI);    
}

void IMU::eulerAngles() {
    angles[0] = atan2f(dcmMatrix[2][1], dcmMatrix[2][2]);
    angles[1] = -asinf(dcmMatrix[2][0]);
    angles[2] = atan2f(dcmMatrix[1][0], dcmMatrix[0][0]);
}

void IMU::renorm(float vr[DIMENTION], const float v[DIMENTION]) {
    float coeff = 0.5 * (3 - dot(v, v));
    scaleVec(vr, v, coeff);
}