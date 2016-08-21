#ifndef FullStateMachine_h
#define FullStateMachine_h

#include <stdint.h>

#include "state_machine.h"
#include "extern_sm/generation_light.h"

#define EXTERN_TICK_MS 1000

const uint8_t SIG_MAP[11] =  {
    CHARGE_SIG,
    SONG_SIG,
    SINGULAR_SIG,
    BARRIER_SIG,
    THROW_SIG,
    PUNCH_SIG,
    LIFT_SIG,
    WARP_SIG,
    CLEANSE_SIG,
    RELEASE_SIG,
    PWR_RELEASE_SIG
};

class FullStateMachine {
private:
    StateMachine innerMachine;
    Hand externMachineStruct;
    QHsm * externMachine;
    uint16_t innerTimer;
public:

    FullStateMachine(int axis);
    void setData(const float delta, 
        const float acc[DIMENTION], const float gyro[DIMENTION], const float mag[DIMENTION],
        const unsigned long access, uint8_t * color, uint16_t * blinkOn, uint16_t * blinkOff, uint8_t * vibro);

};
#endif