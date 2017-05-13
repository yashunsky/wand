#ifndef TagunilOrientation_h
#define TagunilOrientation_h

#include <stdint.h>

#include "ahrsmath.h"

class Orientation
{
  public:
    Orientation() :
      quaternion_(1.0f, 0.0f, 0.0f, 0.0f),
      integralFeedback_(0.0f, 0.0f, 0.0f),
      prevHalfOfMeasuredError_(0.0f, 0.0f, 0.0f)
    {
    }

    void update(float proportionalCoefficient,
                float integralCoefficient,
                float timeDelta,
                Vector acceleration,
                Vector angularVelocity,
                Vector magneticField);

    Quaternion quaternion()
    {
        return quaternion_;
    }

  private:
    Quaternion quaternion_;
    Vector integralFeedback_;
    Vector prevHalfOfMeasuredError_;
};

#endif
