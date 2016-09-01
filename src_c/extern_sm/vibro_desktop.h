/* 
Module to emulate vibro functions.
*/
#ifndef vibro_desktop_h
#define vibro_desktop_h
#include <stdint.h>

#define OFF 0
void vibro(uint8_t Power) {
    printf("vibro(%u);", Power);
}

#endif
