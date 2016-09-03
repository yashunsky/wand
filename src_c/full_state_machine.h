#ifndef FullStateMachine_h
#define FullStateMachine_h

#include <stdint.h>

#include "state_machine.h"
#include "extern_sm/generation_light.h"

#define EXTERN_TICK_MS 1000

const uint8_t SIG_MAP[11] =  {
    CHARGE_SIG,
    THROW_SIG,
    PUNCH_SIG,
    LIFT_SIG,
    WARP_SIG,
    BARRIER_SIG,
    CLEANSE_SIG,
    SINGULAR_SIG,
    SONG_SIG,
    RELEASE_SIG,
    PWR_RELEASE_SIG
};

class FullStateMachine {
private:
    StateMachine innerMachine;
    uint16_t innerTimer;
public:

    FullStateMachine(int axis);
    bool setData(const float delta, 
        const float acc[DIMENTION], const float gyro[DIMENTION], const float mag[DIMENTION]);

    void resetCalibration();
};
#endif
