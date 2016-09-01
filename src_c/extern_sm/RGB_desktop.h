/* 
Module to emulate RGB functions.
*/
#ifndef RGB_desktop_h
#define RGB_desktop_h
#include <stdint.h>
#include <stdio.h>
#include <windows.h>        // For color print in Win console
#include "colors.h"
#include "service.h"

int     BlinkOn;
int     BlinkPhase;
uint8_t BlinkTimer;
uint8_t BlinkColor;
COORD   BlinkCoord, OldCursCoord;

HANDLE  hConsole;
CONSOLE_SCREEN_BUFFER_INFO consoleInfo;
uint16_t SavedAttr;

void RGB_blink_slow(uint8_t Color);

void RGB_blink_fast(uint8_t Color);

void RGB_blink_stop();

//Only for Windows blink implementation
void RGB_blink_toggle();

#endif
