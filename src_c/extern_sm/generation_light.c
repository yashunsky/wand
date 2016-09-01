/*****************************************************************************
* Model: generation_light_biotics.qm
* File:  ./generation_light.c
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
/*${.::generation_light.c} .................................................*/
#include "qpc.h"
#include "generation_light.h"
#include "service.h"
#include "biotics.h"
#include "bsp.h"                   // Change for different platforms

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

//Q_DEFINE_THIS_FILE

int DebugSM = 1;

/*${SMs::Biotics} ..........................................................*/
typedef struct {
/* protected: */
    QHsm super;

/* private: */
    int8_t Abilities;
    uint16_t Timer;
    uint8_t Color;

/* public: */
    int8_t Signal;
} Biotics;

/* protected: */
static QState Biotics_initial(Biotics * const me, QEvt const * const e);
static QState Biotics_active(Biotics * const me, QEvt const * const e);
static QState Biotics_charged(Biotics * const me, QEvt const * const e);
static QState Biotics_song(Biotics * const me, QEvt const * const e);
static QState Biotics_ready(Biotics * const me, QEvt const * const e);
static QState Biotics_cast_direct(Biotics * const me, QEvt const * const e);
static QState Biotics_release(Biotics * const me, QEvt const * const e);
static QState Biotics_singularity(Biotics * const me, QEvt const * const e);
static QState Biotics_barrier(Biotics * const me, QEvt const * const e);
static QState Biotics_pwr_release(Biotics * const me, QEvt const * const e);
static QState Biotics_throw(Biotics * const me, QEvt const * const e);
static QState Biotics_cleanse(Biotics * const me, QEvt const * const e);
static QState Biotics_final(Biotics * const me, QEvt const * const e);


static Biotics biotics; /* the only instance of the Biotics class */


/*${SMs::Hand} .............................................................*/
typedef struct {
/* protected: */
    QHsm super;
} Hand;

/* protected: */
static QState Hand_initial(Hand * const me, QEvt const * const e);
static QState Hand_able(Hand * const me, QEvt const * const e);


static Hand hand; /* the only instance of the Biotics class */

/* global-scope definitions -----------------------------------------*/
QHsm * const the_biotics = (QHsm *)&biotics;       /* the opaque pointer */
QHsm * const the_hand = (QHsm *)&hand;       /* the opaque pointer */

/*${SMs::Biotics_ctor} .....................................................*/
void Biotics_ctor(void) {
    Biotics *me = &biotics;
    QHsm_ctor(&me->super, Q_STATE_CAST(&Biotics_initial));


}
/*${SMs::Biotics} ..........................................................*/
/*${SMs::Biotics::SM} ......................................................*/
static QState Biotics_initial(Biotics * const me, QEvt const * const e) {
    /* ${SMs::Biotics::SM::initial} */
    (void)e; /* avoid compiler warning */
    me->Timer = 0;

    return Q_TRAN(&Biotics_ready);
}
/*${SMs::Biotics::SM::active} ..............................................*/
static QState Biotics_active(Biotics * const me, QEvt const * const e) {
    QState status_;
    switch (e->sig) {
        /* ${SMs::Biotics::SM::active} */
        case Q_ENTRY_SIG: {
            if (DebugSM) {
                printf("Hand active;");
            }

            status_ = Q_HANDLED();
            break;
        }
        /* ${SMs::Biotics::SM::active::TICK_SEC} */
        case TICK_SEC_SIG: {
            if (me->Timer > 0) {
                if (DebugSM) {
                    printf("%us", me->Timer-1);
                }
                me->Timer--;
            }
            /* ${SMs::Biotics::SM::active::TICK_SEC::[me->Timer==1]} */
            if (me->Timer == 1) {
                me->Timer = 0;
                status_ = Q_TRAN(&Biotics_ready);
            }
            /* ${SMs::Biotics::SM::active::TICK_SEC::[else]} */
            else {
                status_ = Q_HANDLED();
            }
            break;
        }
        /* ${SMs::Biotics::SM::active::TERMINATE} */
        case TERMINATE_SIG: {
            status_ = Q_TRAN(&Biotics_final);
            break;
        }
        /* ${SMs::Biotics::SM::active::CHARGE} */
        case CHARGE_SIG: {
            status_ = Q_TRAN(&Biotics_charged);
            break;
        }
        default: {
            status_ = Q_SUPER(&QHsm_top);
            break;
        }
    }
    return status_;
}
/*${SMs::Biotics::SM::active::charged} .....................................*/
static QState Biotics_charged(Biotics * const me, QEvt const * const e) {
    QState status_;
    switch (e->sig) {
        /* ${SMs::Biotics::SM::active::charged} */
        case Q_ENTRY_SIG: {
            if (DebugSM) {
                printf("charged;");
            }
            me->Timer = 3 + 1;
            vibro(30);
            status_ = Q_HANDLED();
            break;
        }
        /* ${SMs::Biotics::SM::active::charged::SONG} */
        case SONG_SIG: {
            /* ${SMs::Biotics::SM::active::charged::SONG::[BIO_IS_ABLE(e->sig)]} */
            if (BIO_IS_ABLE(e->sig)) {
                status_ = Q_TRAN(&Biotics_song);
            }
            else {
                status_ = Q_UNHANDLED();
            }
            break;
        }
        /* ${SMs::Biotics::SM::active::charged::THROW} */
        case THROW_SIG: {
            me->Signal = e->sig;
            status_ = Q_TRAN(&Biotics_throw);
            break;
        }
        /* ${SMs::Biotics::SM::active::charged::PUNCH} */
        case PUNCH_SIG: {
            me->Signal = e->sig;
            /* ${SMs::Biotics::SM::active::charged::PUNCH::[BIO_IS_ABLE(me->Signal)]} */
            if (BIO_IS_ABLE(me->Signal)) {
                status_ = Q_TRAN(&Biotics_cast_direct);
            }
            else {
                status_ = Q_UNHANDLED();
            }
            break;
        }
        /* ${SMs::Biotics::SM::active::charged::LIFT} */
        case LIFT_SIG: {
            me->Signal = e->sig;
            /* ${SMs::Biotics::SM::active::charged::LIFT::[BIO_IS_ABLE(me->Signal)]} */
            if (BIO_IS_ABLE(me->Signal)) {
                status_ = Q_TRAN(&Biotics_cast_direct);
            }
            else {
                status_ = Q_UNHANDLED();
            }
            break;
        }
        /* ${SMs::Biotics::SM::active::charged::WARP} */
        case WARP_SIG: {
            me->Signal = e->sig;
            /* ${SMs::Biotics::SM::active::charged::WARP::[BIO_IS_ABLE(me->Signal)]} */
            if (BIO_IS_ABLE(me->Signal)) {
                status_ = Q_TRAN(&Biotics_cast_direct);
            }
            else {
                status_ = Q_UNHANDLED();
            }
            break;
        }
        /* ${SMs::Biotics::SM::active::charged::SINGULAR} */
        case SINGULAR_SIG: {
            /* ${SMs::Biotics::SM::active::charged::SINGULAR::[BIO_IS_ABLE(e->sig)]} */
            if (BIO_IS_ABLE(e->sig)) {
                status_ = Q_TRAN(&Biotics_singularity);
            }
            else {
                status_ = Q_UNHANDLED();
            }
            break;
        }
        /* ${SMs::Biotics::SM::active::charged::BARRIER} */
        case BARRIER_SIG: {
            /* ${SMs::Biotics::SM::active::charged::BARRIER::[BIO_IS_ABLE(e->sig)]} */
            if (BIO_IS_ABLE(e->sig)) {
                status_ = Q_TRAN(&Biotics_barrier);
            }
            else {
                status_ = Q_UNHANDLED();
            }
            break;
        }
        /* ${SMs::Biotics::SM::active::charged::CLEANSE} */
        case CLEANSE_SIG: {
            me->Signal = e->sig;
            /* ${SMs::Biotics::SM::active::charged::CLEANSE::[BIO_IS_PWR_ABLE(me->Signal)]} */
            if (BIO_IS_PWR_ABLE(me->Signal)) {
                status_ = Q_TRAN(&Biotics_cleanse);
            }
            else {
                status_ = Q_UNHANDLED();
            }
            break;
        }
        default: {
            status_ = Q_SUPER(&Biotics_active);
            break;
        }
    }
    return status_;
}
/*${SMs::Biotics::SM::active::song} ........................................*/
static QState Biotics_song(Biotics * const me, QEvt const * const e) {
    QState status_;
    switch (e->sig) {
        /* ${SMs::Biotics::SM::active::song} */
        case Q_ENTRY_SIG: {
            if (DebugSM) {
                printf("song;");
            }
            me->Timer = 5 + 1;
            vibro(100);
            RGB_blink_fast(ORANGE);
            status_ = Q_HANDLED();
            break;
        }
        default: {
            status_ = Q_SUPER(&Biotics_active);
            break;
        }
    }
    return status_;
}
/*${SMs::Biotics::SM::active::ready} .......................................*/
static QState Biotics_ready(Biotics * const me, QEvt const * const e) {
    QState status_;
    switch (e->sig) {
        /* ${SMs::Biotics::SM::active::ready} */
        case Q_ENTRY_SIG: {
            if (DebugSM) {
                printf("Biotics ready;");
            }
            vibro(OFF);
            RGB_blink_stop();
            me->Color = BLANK;
            status_ = Q_HANDLED();
            break;
        }
        /* ${SMs::Biotics::SM::active::ready::CHARGE} */
        case CHARGE_SIG: {
            status_ = Q_TRAN(&Biotics_charged);
            break;
        }
        default: {
            status_ = Q_SUPER(&Biotics_active);
            break;
        }
    }
    return status_;
}
/*${SMs::Biotics::SM::active::cast_direct} .................................*/
static QState Biotics_cast_direct(Biotics * const me, QEvt const * const e) {
    QState status_;
    switch (e->sig) {
        /* ${SMs::Biotics::SM::active::cast_direct} */
        case Q_ENTRY_SIG: {
            if (DebugSM) {
                printf("cast_direct;");
            }
            me->Timer = 3 + 1;
            vibro(60);
            status_ = Q_HANDLED();
            break;
        }
        /* ${SMs::Biotics::SM::active::cast_direct::RELEASE} */
        case RELEASE_SIG: {
            status_ = Q_TRAN(&Biotics_release);
            break;
        }
        /* ${SMs::Biotics::SM::active::cast_direct::PWR_RELEASE} */
        case PWR_RELEASE_SIG: {
            /* ${SMs::Biotics::SM::active::cast_direct::PWR_RELEASE::[BIO_IS_PWR_ABLE(me->Signal)]} */
            if (BIO_IS_PWR_ABLE(me->Signal)) {
                status_ = Q_TRAN(&Biotics_pwr_release);
            }
            else {
                status_ = Q_UNHANDLED();
            }
            break;
        }
        default: {
            status_ = Q_SUPER(&Biotics_active);
            break;
        }
    }
    return status_;
}
/*${SMs::Biotics::SM::active::release} .....................................*/
static QState Biotics_release(Biotics * const me, QEvt const * const e) {
    QState status_;
    switch (e->sig) {
        /* ${SMs::Biotics::SM::active::release} */
        case Q_ENTRY_SIG: {
            if (DebugSM) {
                printf("released;");
            }
            me->Timer = 5 + 1;
            vibro(100);
            me->Color = BIO_AbilitiesColors[me->Signal-FIRST_ABILITY];
            RGB_blink_slow(me->Color);
            status_ = Q_HANDLED();
            break;
        }
        default: {
            status_ = Q_SUPER(&Biotics_active);
            break;
        }
    }
    return status_;
}
/*${SMs::Biotics::SM::active::singularity} .................................*/
static QState Biotics_singularity(Biotics * const me, QEvt const * const e) {
    QState status_;
    switch (e->sig) {
        /* ${SMs::Biotics::SM::active::singularity} */
        case Q_ENTRY_SIG: {
            if (DebugSM) {
                printf("singularity;");
            }
            me->Timer = 5 + 1;
            RGB_blink_fast(WHITE);
            vibro(100);
            status_ = Q_HANDLED();
            break;
        }
        default: {
            status_ = Q_SUPER(&Biotics_active);
            break;
        }
    }
    return status_;
}
/*${SMs::Biotics::SM::active::barrier} .....................................*/
static QState Biotics_barrier(Biotics * const me, QEvt const * const e) {
    QState status_;
    switch (e->sig) {
        /* ${SMs::Biotics::SM::active::barrier} */
        case Q_ENTRY_SIG: {
            if (DebugSM) {
                printf("barrier;");
            }
            me->Timer = 5 + 1;
            vibro(100);
            RGB_blink_slow(GREEN);
            status_ = Q_HANDLED();
            break;
        }
        default: {
            status_ = Q_SUPER(&Biotics_active);
            break;
        }
    }
    return status_;
}
/*${SMs::Biotics::SM::active::pwr_release} .................................*/
static QState Biotics_pwr_release(Biotics * const me, QEvt const * const e) {
    QState status_;
    switch (e->sig) {
        /* ${SMs::Biotics::SM::active::pwr_release} */
        case Q_ENTRY_SIG: {
            if (DebugSM) {
                printf("pwr_released;");
            }
            me->Timer = 5 + 1;
            vibro(100);
            me->Color = BIO_AbilitiesColors[me->Signal - FIRST_ABILITY];
            RGB_blink_fast(me->Color);
            status_ = Q_HANDLED();
            break;
        }
        default: {
            status_ = Q_SUPER(&Biotics_active);
            break;
        }
    }
    return status_;
}
/*${SMs::Biotics::SM::active::throw} .......................................*/
static QState Biotics_throw(Biotics * const me, QEvt const * const e) {
    QState status_;
    switch (e->sig) {
        /* ${SMs::Biotics::SM::active::throw} */
        case Q_ENTRY_SIG: {
            if (DebugSM) {
                printf("throw;");
            }
            me->Timer = 3 + 1;
            vibro(60);

            status_ = Q_HANDLED();
            break;
        }
        /* ${SMs::Biotics::SM::active::throw::RELEASE} */
        case RELEASE_SIG: {
            /* ${SMs::Biotics::SM::active::throw::RELEASE::[BIO_IS_ABLE(me->Signal)]} */
            if (BIO_IS_ABLE(me->Signal)) {
                status_ = Q_TRAN(&Biotics_release);
            }
            else {
                status_ = Q_UNHANDLED();
            }
            break;
        }
        default: {
            status_ = Q_SUPER(&Biotics_active);
            break;
        }
    }
    return status_;
}
/*${SMs::Biotics::SM::active::cleanse} .....................................*/
static QState Biotics_cleanse(Biotics * const me, QEvt const * const e) {
    QState status_;
    switch (e->sig) {
        /* ${SMs::Biotics::SM::active::cleanse} */
        case Q_ENTRY_SIG: {
            if (DebugSM) {
                printf("cleanse;");
            }
            me->Timer = 3 + 1;
            vibro(60);

            status_ = Q_HANDLED();
            break;
        }
        /* ${SMs::Biotics::SM::active::cleanse::PWR_RELEASE} */
        case PWR_RELEASE_SIG: {
            status_ = Q_TRAN(&Biotics_pwr_release);
            break;
        }
        default: {
            status_ = Q_SUPER(&Biotics_active);
            break;
        }
    }
    return status_;
}
/*${SMs::Biotics::SM::final} ...............................................*/
static QState Biotics_final(Biotics * const me, QEvt const * const e) {
    QState status_;
    switch (e->sig) {
        /* ${SMs::Biotics::SM::final} */
        case Q_ENTRY_SIG: {
            printf("\nBye! Bye!\n");
            exit(0);
            status_ = Q_HANDLED();
            break;
        }
        default: {
            status_ = Q_SUPER(&QHsm_top);
            break;
        }
    }
    return status_;
}


/*${SMs::Hand_ctor} ........................................................*/
void Hand_ctor(void) {
    Hand *me = &hand;
    QHsm_ctor(&me->super, Q_STATE_CAST(&Hand_initial));


}
/*${SMs::Hand} .............................................................*/
/*${SMs::Hand::SM} .........................................................*/
static QState Hand_initial(Hand * const me, QEvt const * const e) {
    /* ${SMs::Hand::SM::initial} */
    (void)e; /* avoid compiler warning */
    BIO_init();
    return Q_TRAN(&Hand_able);
}
/*${SMs::Hand::SM::able} ...................................................*/
static QState Hand_able(Hand * const me, QEvt const * const e) {
    QState status_;
    switch (e->sig) {
        /* ${SMs::Hand::SM::able} */
        case Q_ENTRY_SIG: {
            if (DebugSM) printf("Hand able;");
            status_ = Q_HANDLED();
            break;
        }
        /* ${SMs::Hand::SM::able::PUNCH_PILL} */
        case PUNCH_PILL_SIG: {
            BIO_ENABLE(PUNCH);
            status_ = Q_HANDLED();
            break;
        }
        /* ${SMs::Hand::SM::able::PUNCH_PWR_PILL} */
        case PUNCH_PWR_PILL_SIG: {
            BIO_PWR_ENABLE(PUNCH);
            status_ = Q_HANDLED();
            break;
        }
        /* ${SMs::Hand::SM::able::LIFT_PILL} */
        case LIFT_PILL_SIG: {
            BIO_ENABLE(LIFT);
            status_ = Q_HANDLED();
            break;
        }
        /* ${SMs::Hand::SM::able::MAX_PILL} */
        case MAX_PILL_SIG: {
            BIO_set_max();
            status_ = Q_HANDLED();
            break;
        }
        /* ${SMs::Hand::SM::able::LIFT_PWR_PILL} */
        case LIFT_PWR_PILL_SIG: {
            BIO_PWR_ENABLE(LIFT);
            status_ = Q_HANDLED();
            break;
        }
        /* ${SMs::Hand::SM::able::WARP_PILL} */
        case WARP_PILL_SIG: {
            BIO_ENABLE(WARP);
            status_ = Q_HANDLED();
            break;
        }
        /* ${SMs::Hand::SM::able::WARP_PWR_PILL} */
        case WARP_PWR_PILL_SIG: {
            BIO_PWR_ENABLE(WARP);
            status_ = Q_HANDLED();
            break;
        }
        /* ${SMs::Hand::SM::able::CLEANSE_PILL} */
        case CLEANSE_PILL_SIG: {
            BIO_PWR_ENABLE(CLEANSE);
            status_ = Q_HANDLED();
            break;
        }
        /* ${SMs::Hand::SM::able::BARRIER_PILL} */
        case BARRIER_PILL_SIG: {
            BIO_ENABLE(BARRIER);
            status_ = Q_HANDLED();
            break;
        }
        /* ${SMs::Hand::SM::able::SINGULARITY_PILL} */
        case SINGULARITY_PILL_SIG: {
            BIO_ENABLE(SINGULAR);
            status_ = Q_HANDLED();
            break;
        }
        /* ${SMs::Hand::SM::able::SONG_PILL} */
        case SONG_PILL_SIG: {
            BIO_ENABLE(SONG);
            status_ = Q_HANDLED();
            break;
        }
        /* ${SMs::Hand::SM::able::DEFAULT_PILL} */
        case DEFAULT_PILL_SIG: {
            BIO_set_default();
            status_ = Q_HANDLED();
            break;
        }
        default: {
            status_ = Q_SUPER(&QHsm_top);
            break;
        }
    }
    return status_;
}


