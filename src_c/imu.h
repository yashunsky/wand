/*
This module is refactoring of the following libraries:
https://github.com/pololu/minimu-9-ahrs-arduino

Original header:
MinIMU-9-Arduino-AHRS
Pololu MinIMU-9 + Arduino AHRS (Attitude and Heading Reference System)
Copyright (c) 2011 Pololu Corporation.
http://www.pololu.com/
MinIMU-9-Arduino-AHRS is based on sf9domahrs by Doug Weibel and Jose Julio:
http://code.google.com/p/sf9domahrs/
sf9domahrs is based on ArduIMU v1.5 by Jordi Munoz and
William Premerlani, Jose
Julio and Doug Weibel:
http://code.google.com/p/ardu-imu/
MinIMU-9-Arduino-AHRS is free software: you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
MinIMU-9-Arduino-AHRS is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License
for more details.
You should have received a copy of the GNU Lesser General Public License
along with MinIMU-9-Arduino-AHRS. If not, see <http://www.gnu.org/licenses/>.
*/

#ifndef IMU_h
#define IMU_h
#include "knowledge.h"

#define GRAVITY 256
#define G_CONST 9.81
#define GYRO_GAIN 0.0012217304763960308
#define KP_ROLLPITCH 0.02
#define KI_ROLLPITCH 0.00002
#define KP_YAW 1.2
#define KI_YAW 0.00002
#define ACCELEROMETER_SCALE 0.0625
#define MAGNETS_OFFSET 0.5

#define CALIBRATION_LENGTH 32

#define ACCELEROMETER_DIVIATION 2
#define GYROSCOPE_DIVIATION 16

class IMU {
private:
    float gyroscopeReadingsOffset[DIMENTION];
    float accelerometerReadingsOffset[DIMENTION];

    float magHeading;

    float omegaP[DIMENTION];
    float omegaI[DIMENTION];
    float angles[DIMENTION]; // roll, pitch, yaw 

    float dcmMatrix[DIMENTION][DIMENTION];

    bool inCalibration;

    float acceleration[DIMENTION];
    float gyroNorm;

    float aStack[CALIBRATION_LENGTH][DIMENTION];
    float gStack[CALIBRATION_LENGTH][DIMENTION];    

    int calibrationCounter;
    bool stacksReady;

    void recalibration(const float acc[DIMENTION], const float gyro[DIMENTION], const float mag[DIMENTION]);
    void mainLoop(const float delta, const float accIn[DIMENTION], const float gyroIn[DIMENTION], const float magIn[DIMENTION]);
    void getGlobalAcceleration(float acc[DIMENTION]);
    void getHeading(int axis, float heading[DIMENTION]);

    void calcMean(const float data[CALIBRATION_LENGTH][DIMENTION], float mean[DIMENTION]);
    float calcDeviation(const float data[CALIBRATION_LENGTH][DIMENTION], const float mean[DIMENTION]);

    float compassHeading(const float mag[DIMENTION]);

    void updateDcmMatrix(const float delta, const float gyro[DIMENTION]);
    float calculateAccelWeight(const float acc[DIMENTION]);
    void calculateError(const float acc[DIMENTION], float errorYaw[DIMENTION], float errorRollPitch[DIMENTION]);

    void driftCorrection(float accelWeight, float errorYaw[DIMENTION], float errorRollPitch[DIMENTION]);
    void eulerAngles();

    void renorm(float vr[DIMENTION], const float v[DIMENTION]);


public:
    IMU();
    bool calc(const float delta, 
              const float accIn[DIMENTION], const float gyroIn[DIMENTION], const float magIn[DIMENTION],
              int axis,
              float * gyroOut, float accOut[DIMENTION], float headingOut[DIMENTION]);
    void resetCalibration();

};
#endif
