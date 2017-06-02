#ifndef FullStateMachine_h
#define FullStateMachine_h

#include <stdint.h>

#include "state_machine.h"
#include "generation_light.h"
#include "sigmap.h"

#define EXTERN_TICK_MS 1000

class FullStateMachine {
private:
    StateMachine innerMachine;
    uint16_t innerTimer;
public:

    FullStateMachine(int axis);
    bool setData(const float delta, 
        const float acc[DIMENTION], const float gyro[DIMENTION], const float mag[DIMENTION]);
};
#endif
