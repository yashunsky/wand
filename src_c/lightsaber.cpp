#include "lightsaber.h"
#include "lightsaber_out.h"
#include "calibration.h"

Lightsaber::Lightsaber() {
    axis = AXIS_X;
    hum = LEVEL_MIN ;
    calibrationDone = 0;
    filter = Filter();
    accTimeout = ACC_TIMEOUT;
}

void Lightsaber::init() {
   imu.init(); 
}


void Lightsaber::setData(const float dt, const Vector acc, const Vector gyro, const Vector mag){

    if (dt > 1) {
        return;
    }

    ImuAnswer answer = imu.calc(dt, acc, gyro, mag, axis);

    float a = filter.setInput(answer.acc, dt).norm();
    float g = answer.gyro;

    float speed = g > GYRO_EDGE ? SPEED_IN : SPEED_OUT;

    hum += speed * dt;

    if (a > ACC_EDGE and accTimeout <= 0) {
        boom(int(a - ACC_EDGE));
        accTimeout = ACC_TIMEOUT;
    }

    if (accTimeout > 0) {
        accTimeout -= dt;
    }

    if (hum > LEVEL_MAX) {
        hum = LEVEL_MAX;
    } else if (hum < LEVEL_MIN) {
        hum = LEVEL_MIN;
    }

    setHumLevel(int(hum));

    if (calibrationDone == 0) {
        onCalibrationDone();
        calibrationDone = 1;
    }
}
