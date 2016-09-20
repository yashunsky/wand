/** 
Module BIO - all about Biotics
**/
#ifndef biotics_h
#define biotics_h

#include <stdint.h>
#include "colors.h"
#include "bitmasks.h"
#include "generation_light.h"

typedef uint16_t BIO_Store;
typedef uint16_t BIO_TO;


typedef struct BIO_Abil_ {
    BIO_Store   Abilities;      
    BIO_Store   Power;       // Power abilities
    BIO_TO      TO_Short_s;
    BIO_TO      TO_Long_s;
} BIO_Abil;

extern BIO_Abil BIO, BIO_Default, BIO_Max;

// Variable macro to set BIO, depends on signal enum
#define BIO_ENABLE(abil_, ...) \
        (SET_BIT(BIO##__VA_ARGS__.Abilities, abil_##_SIG - FIRST_ABILITY))
#define BIO_DISABLE(abil_, ...) \
        (CLEAR_BIT(BIO##__VA_ARGS__.Abilities, abil_##_SIG - FIRST_ABILITY))
#define BIO_PWR_ENABLE(abil_, ...) \
        (SET_BIT(BIO##__VA_ARGS__.Power, abil_##_SIG - FIRST_ABILITY))
#define BIO_PWR_DISABLE(abil_, ...) \
        (CLEAR_BIT(BIO##__VA_ARGS__.Power, abil_##_SIG - FIRST_ABILITY))
#define BIO_IS_ABLE(abil_)     (CHECK_BIT(BIO.Abilities, abil_ - FIRST_ABILITY))
#define BIO_IS_PWR_ABLE(abil_) (CHECK_BIT(BIO.Power, abil_ - FIRST_ABILITY))

#define BIO_SET_TO(to_) (me->Timer = BIO.TO_##to_##_s + 1)
            // 0 bit is used as "Enable timer" flag in TICK_SEC evt, so +1
        
// Ability - color correspondence. Depends on signal enum.
static const uint8_t BIO_AbilitiesColors[LAST_ABILITY] = {
    WHITE,
    RED,
    YELLOW,
    VIOLET,
    GREEN,
    GREEN,
    WHITE,
    ORANGE
};

void BIO_init(void);    // Public functions
void BIO_set_to_short(uint8_t TimeOut);     
void BIO_set_to_long(uint8_t TimeOut);

void BIO_set_default(void);
void BIO_set_max(void);

#endif

