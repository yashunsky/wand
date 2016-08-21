#include "full_state_machine.h"
#include "extern_sm/service.h"
#include "extern_sm/generation_light.h"
#include "knowledge.h"
#include <stdio.h>

FullStateMachine::FullStateMachine(int axis) : innerMachine(axis) {
    externMachine = (QHsm *)&externMachineStruct;
    Hand_ctor(externMachine);

    innerTimer = 0;    
}

void FullStateMachine::setData(const float delta,
    const float acc[DIMENTION], const float gyro[DIMENTION], const float mag[DIMENTION], 
    const unsigned long access, uint8_t * color, uint16_t * blinkOn, uint16_t * blinkOff, uint8_t * vibro)
{
    int innerState = innerMachine.setData(delta, acc, gyro, mag, access);

    if (innerState == CALIBRATION) {
        * color = VIOLET + 1;
        * blinkOn = 1000;
        * blinkOff = 0;        
        * vibro = 0;
    } else {
        QEvt e;
        if (innerState > IDLE) {
            e.sig = SIG_MAP[innerState - STATES_OFFSET];
            QMSM_DISPATCH(externMachine, &e);
        }

        innerTimer += (uint16_t) (delta * 1000);
        if (innerTimer > EXTERN_TICK_MS) {
            e.sig = TICK_SEC_SIG;
            QMSM_DISPATCH(externMachine, &e);
        }

        innerTimer %= EXTERN_TICK_MS;

        getState(externMachine, color, blinkOn, blinkOff, vibro);        
    }
}
