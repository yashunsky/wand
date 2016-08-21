/*****************************************************************************
* Model: generation_light_ownFW.qm
* File:  ./generation_light.h
*
* This code has been generated by QM tool (see state-machine.com/qm).
* DO NOT EDIT THIS FILE MANUALLY. All your changes will be lost.
*
* This program is open source software: you can redistribute it and/or
* modify it under the terms of the GNU General Public License as published
* by the Free Software Foundation.
*
* This program is distributed in the hope that it will be useful, but
* WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
* or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
* for more details.
*****************************************************************************/
/*${.::generation_light.h} .................................................*/
#ifndef generation_h
#define generation_h

#include <stdint.h>
#include "qpc.h"    /* include own framework */

#define BSP_TICKS_PER_SEC 100

extern int DebugSM;

enum PlayerSignals {
    TICK_SEC_SIG = Q_USER_SIG,
    CHARGE_SIG,
    SONG_SIG,        /* indirect effects */
    SINGULAR_SIG,
    BARRIER_SIG,


    THROW_SIG,       /* direct effects */
    PUNCH_SIG,
    LIFT_SIG,
    WARP_SIG,
    CLEANSE_SIG,
    RELEASE_SIG,
    PWR_RELEASE_SIG,


    TERMINATE_SIG /* terminate the application */
};

/*${SMs::Hand} .............................................................*/
typedef struct {
/* protected: */
    QHsm super;

/* private: */
    int8_t Abilities;
    uint16_t Timer;
    uint8_t Color;

    uint8_t fbColor;
    uint16_t fbBlinkOn;
    uint16_t fbBlinkOff;
    uint8_t fbVibro;

} Hand;

extern QHsm * const the_hand; /* opaque pointer to the player HSM */

/*${SMs::Hand_ctor} ........................................................*/
void Hand_ctor(QHsm * const me);

void getState(QHsm * const me, uint8_t *color, uint16_t *blinkOn, uint16_t *blinkOff, uint8_t *vibro);

#endif /* generation_h */
