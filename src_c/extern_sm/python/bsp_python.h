/* 
Board Support Package.
Module to replace for various platforms.
*/
#ifndef bsp_python_h
#define bsp_python_h
#include <stdint.h>

void RGB_blink_slow(uint8_t Color);

void RGB_blink_fast(uint8_t Color);

void RGB_blink_stop();

void vibro(uint8_t Power);

#endif
