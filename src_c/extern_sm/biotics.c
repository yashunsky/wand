#include "biotics.h"

BIO_Abil BIO, BIO_Default, BIO_Max;

void BIO_init(void) {
    BIO_ENABLE(THROW, _Default);
    BIO_ENABLE(THROW);
}

void BIO_set_default() {
    BIO.Abilities   = BIO_Default.Abilities;
    BIO.Power       = BIO_Default.Power;
}

void BIO_set_max() {
    BIO_Max.Abilities   = 0xFFFF;
    BIO_Max.Power       = 0xFFFF;
    BIO.Abilities   = BIO_Max.Abilities;
    BIO.Power       = BIO_Max.Power;
}

