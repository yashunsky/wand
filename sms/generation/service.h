/* Additional entities for convenience
*/
#ifndef service_h
#define service_h

#define     ARRAY_SIZE(foo) (sizeof(foo)/sizeof(foo[0]))

#include <stdint.h>
#include "bsp.h"
#include "generation_light.h"
#include "colors.h"

/* Keystroke-signal aliases to use with printf */
typedef struct KeyStroke_ {
   uint8_t          Com;      // Command
   char const      *Alias;    // Sting name for command
   uint8_t          Key;      // Keyboard symbol
} KeyStroke;

extern const KeyStroke KeyStrokes[];    // Definition moved to C file, otherwise
                                        // won't compile

/* Colors section */

#define ANSI_COLOR_RED     "\x1b[31m"
#define ANSI_COLOR_GREEN   "\x1b[32m"
#define ANSI_COLOR_YELLOW  "\x1b[33m"
#define ANSI_COLOR_BLUE    "\x1b[34m"
#define ANSI_COLOR_MAGENTA "\x1b[35m"
#define ANSI_COLOR_CYAN    "\x1b[36m"
#define ANSI_COLOR_WHITE   "\x1b[1m\x1b[37m"
#define ANSI_COLOR_RESET   "\x1b[0m"

typedef struct ColorName_ {
   uint8_t          Num;      // Color number
   char const      *Name;     // Color name
   uint16_t         WinColor; // Color for terminal
} ColorName;

static const ColorName ColorNames[] = {
{    BLANK,     "BLANK" ,   0x08},
{    WHITE,     "WHITE" ,   0x0F},
{    RED,       "RED"   ,   0x0C},
{    ORANGE,    "ORANGE",   0xCE},
{    YELLOW,    "YELLOW",   0x0E},
{    GREEN,     "GREEN",    0x0A},
{    BLUE,      "BLUE",     0x09},
{    VIOLET,    "VIOLET",   0x0D}
};

#endif
