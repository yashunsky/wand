#include "full_state_machine.h"
#include "extern_sm/service.h"
#include "extern_sm/generation_light.h"
#include "knowledge.h"
#include <stdio.h>

FullStateMachine::FullStateMachine(int axis) : innerMachine(axis) {
    innerTimer = 0;    
}

bool FullStateMachine::setData(const float delta,
    const float acc[DIMENTION], const float gyro[DIMENTION], const float mag[DIMENTION])
{
    int innerState = innerMachine.setData(delta, acc, gyro, mag);

    if (innerState == CALIBRATION) {
        return false;
    } else {
        QEvt e;
        if (innerState > IDLE) {
            e.sig = SIG_MAP[innerState - STATES_OFFSET];
            QMSM_DISPATCH(the_hand, &e);
        }

        innerTimer += (uint16_t) (delta * 1000);
        if (innerTimer > EXTERN_TICK_MS) {
            e.sig = TICK_SEC_SIG;
            QMSM_DISPATCH(the_hand, &e);
        }

        innerTimer %= EXTERN_TICK_MS;    
    }
    return true;
}

void FullStateMachine::resetCalibration() {
    innerMachine.resetCalibration();
}
