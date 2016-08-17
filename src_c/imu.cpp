#include "imu.h"
#include "matrix.h"
#include <math.h>

IMU::IMU() {
    magHeading = 0;
    inCalibration = true;
    calibrationCounter = 0;
    stacksReady = false;
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

    if ((calcDeviation(aStack, accelerometerReadingsOffset) > ACCELEROMETER_DIVIATION) 
            || (calcDeviation(gStack, gyroscopeReadingsOffset) > GYROSCOPE_DIVIATION))
    {
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

    updateDcmMatrix(gyro);

    float accelWeight = calculateAccelWeight(acc);
    float errorYaw, errorRollPitch;
    calculateError(acc, &errorYaw, &errorRollPitch);
    driftCorrection(accelWeight, errorYaw, errorRollPitch);
    eulerAngles();
}

void IMU::getGlobalAcceleration(float acc[DIMENTION]) {

}

void IMU::getHeading(int axis, float heading[DIMENTION]) {

}

void IMU::calcMean(const float data[CALIBRATION_LENGTH][DIMENTION], float mean[DIMENTION]) {

}

float IMU::calcDeviation(const float data[CALIBRATION_LENGTH][DIMENTION], const float mean[DIMENTION]) {
    return 0;
}

float IMU::compassHeading(const float mag[DIMENTION]) {
    float cosRoll = cos(angles[0]);
    float sinRoll = sin(angles[0]);
    float cosPitch = cos(angles[1]);
    float sinPitch = sin(angles[1]);

    float magnetsNorm[DIMENTION];

    float magX, magY;

    for (int i=0; i<DIMENTION; i++) {
        magnetsNorm[i] = ((mag[i] - MAGNETS_BOUNDARIES[0][i]) / (MAGNETS_BOUNDARIES[1][i] - MAGNETS_BOUNDARIES[0][i])) - MAGNETS_OFFSET;
    }

    magX = (magnetsNorm[0] * cosPitch + magnetsNorm[1] * sinRoll * sinPitch + magnetsNorm[2] * cosRoll * sinPitch);
    magY = (magnetsNorm[1] * cosRoll - magnetsNorm[2] * sinRoll);

    return atan2(-magY, magX);
}

void IMU::updateDcmMatrix(const float gyro[DIMENTION]) {
    //     self.dcm_matrix = self.normalize(self.dcm_matrix)
}

float IMU::calculateAccelWeight(const float acc[DIMENTION]) {
    return 0;
}

void IMU::calculateError(const float acc[DIMENTION], float * errorYaw, float * errorRollPitch) {

}

void IMU::driftCorrection(float accelWeight, float errorYaw, float errorRollPitch) {

}

void IMU::eulerAngles() {

}