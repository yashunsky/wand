#ifndef IMU_h
#define IMU_h
#include "knowledge.h"

#define GRAVITY 256
#define G 9.81
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

    void updateDcmMatrix(const float gyro[DIMENTION]);
    float calculateAccelWeight(const float acc[DIMENTION]);
    void calculateError(const float acc[DIMENTION], float * errorYaw, float * errorRollPitch);

    void driftCorrection(float accelWeight, float errorYaw, float errorRollPitch);
    void eulerAngles();


public:
    IMU();
    bool calc(const float delta, 
              const float accIn[DIMENTION], const float gyroIn[DIMENTION], const float magIn[DIMENTION],
              int axis,
              float * gyroOut, float accOut[DIMENTION], float headingOut[DIMENTION]);

};
#endif