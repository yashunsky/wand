#include "orientation.h"

#include <math.h>

static inline float square(float x)
{
  return x * x;
}

void Orientation::update(float proportionalCoefficient,
                         float integralCoefficient,
                         float timeDelta,
                         Vector acceleration,
                         Vector angularVelocity,
                         Vector magneticField)
{
  float doubledProportionalCoefficient = proportionalCoefficient +
                                         proportionalCoefficient;
  float doubledIntegralCoefficient = integralCoefficient +
                                     integralCoefficient;

  Vector halfOfMeasuredError(0.0f, 0.0f, 0.0f);

  float aa = quaternion_.a * quaternion_.a;
  float ab = quaternion_.a * quaternion_.b;
  float ac = quaternion_.a * quaternion_.c;
  float ad = quaternion_.a * quaternion_.d;
  float bb = quaternion_.b * quaternion_.b;
  float bc = quaternion_.b * quaternion_.c;
  float bd = quaternion_.b * quaternion_.d;
  float cc = quaternion_.c * quaternion_.c;
  float cd = quaternion_.c * quaternion_.d;
  float dd = quaternion_.d * quaternion_.d;

  if ((acceleration.x != 0.0f) ||
      (acceleration.y != 0.0f) ||
      (acceleration.z != 0.0f)) {
    Vector measuredAcceleration = acceleration;
    measuredAcceleration.normalize();

    Vector halfOfEstimatedAcceleration =
      Vector(bd - ac, ab + cd, aa + dd - 0.5f);

    halfOfMeasuredError += crossProduct(measuredAcceleration,
                                        halfOfEstimatedAcceleration);
  }
/*
  if ((magneticField.x != 0.0f) ||
      (magneticField.y != 0.0f) ||
      (magneticField.z != 0.0f)) {
    Vector measuredMagneticField = magneticField;
    measuredMagneticField.normalize();

    Vector halfOfEstimatedMagneticField =
      Vector(0.5f - cc - dd, bc - ad, ac + bd) *
      sqrt(square(dotProduct(measuredMagneticField,
                             Vector(0.5f - cc - dd, bc - ad, ac + bd))) +
           square(dotProduct(measuredMagneticField,
                             Vector(bc + ad, 0.5f - bb - dd, cd - ab))));
    halfOfEstimatedMagneticField +=
      Vector(bd - ac, ab + cd, 0.5f - bb - cc) *
      dotProduct(measuredMagneticField,
                 Vector(bd - ac, ab + cd, 0.5f - bb - cc));
    halfOfEstimatedMagneticField += halfOfEstimatedMagneticField;

    halfOfMeasuredError += crossProduct(measuredMagneticField,
                                        halfOfEstimatedMagneticField);
  }
*/
  Vector correctedAngularVelocity = angularVelocity;

  correctedAngularVelocity += halfOfMeasuredError *
                              doubledProportionalCoefficient;

  if (doubledIntegralCoefficient > 0.0f) {
    integralFeedback_ += prevHalfOfMeasuredError_ * timeDelta;
    correctedAngularVelocity += doubledIntegralCoefficient *
                                integralFeedback_;
    prevHalfOfMeasuredError_ = halfOfMeasuredError;
  } else {
    integralFeedback_ = Vector(0.0f, 0.0f, 0.0f);
  }

  quaternion_ += quaternion_ *
                 (correctedAngularVelocity * (0.5f * timeDelta));

  quaternion_.normalize();
}
