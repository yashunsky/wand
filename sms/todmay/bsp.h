/*
Board support package. Platform depended code goes from here.
*/
#pragma once

#define OFF     0

void RGB_blink_slow(uint8_t Color);

void RGB_blink_fast(uint8_t Color);

void RGB_blink_stop();

void vibro(uint8_t Power);
