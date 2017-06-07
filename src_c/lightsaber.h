#ifndef Lightsaber_h
#define Lightsaber_h

#include "imu.h"
#include "filter.h"

# define AXIS_X 0

# define GYRO_EDGE 1
# define SPEED_IN 100.0
# define SPEED_OUT -1000.0
# define LEVEL_MIN 1
# define LEVEL_MAX 60

# define ACC_EDGE 10
# define ACC_TIMEOUT 0.5


class Lightsaber {
private:
    IMU imu;
    Filter filter;
    int calibrationDone;
    float hum;
    int axis;
    float accTimeout;

public:
    Lightsaber();
    void init();
    void setData(const float dt, const Vector acc, const Vector gyro, const Vector mag);
};
#endif
