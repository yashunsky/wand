/** 
Module BIO - all about Biotics
**/
#ifndef biotics_h
#define biotics_h

#include <stdint.h>
#include "colors.h"
#include "bitmasks.h"
#include "generation_light.h"

typedef uint16_t BIOStore;

typedef struct BIO_Abil_ {
    BIOStore   Abilities;      
    BIOStore   Power;       // Power abilities
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

void BIO_init(void);
void BIO_set_default(void);
void BIO_set_max(void);

#endif

