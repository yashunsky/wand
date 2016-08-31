/* Additional entities for convenience
*/
#ifndef service_h
#define service_h

#define     ARRAY_SIZE(foo) (sizeof(foo)/sizeof(foo[0]))

#include <stdint.h>
#include "generation_light.h"
#include "colors.h"

/* Keystroke-signal aliases to use with printf */
typedef struct KeyStroke_ {
   uint8_t          Com;      // Command
   char const      *Alias;    // Sting name for command
   uint8_t          Key;      // Keyboard symbol
} KeyStroke;

static const KeyStroke KeyStrokes[] = {
{    CHARGE_SIG,         "CHARGE",           '`'    },
{    THROW_SIG,          "THROW",            '1'    },
{    PUNCH_SIG,          "PUNCH",            '2'    },
{    LIFT_SIG,           "LIFT",             '3'    },
{    WARP_SIG,           "WARP",             '4'    },
{    BARRIER_SIG,        "BARRIER",          '5'    },
{    CLEANSE_SIG,        "CLEANSE",          '6'    },
{    SINGULAR_SIG,       "SINGULAR",         '7'    },
{    SONG_SIG,           "SONG",             '8'    },
{    RELEASE_SIG,        "RELEASE",          '9'    },
{    PWR_RELEASE_SIG,    "PWR_RELEASE",      '0'    },

{    PUNCH_PILL_SIG,             "PUNCH_PILL",               'p'    },
{    PUNCH_PWR_PILL_SIG,         "PUNCH_PWR_PILL",           'P'    },
{    LIFT_PILL_SIG,              "LIFT_PILL",                'l'    },
{    LIFT_PWR_PILL_SIG,          "LIFT_PWR_PILL",            'L'    },
{    WARP_PILL_SIG,              "WARP_PILL",                'w'    },
{    WARP_PWR_PILL_SIG,          "WARP_PWR_PILL",            'W'    },
{    CLEANSE_PILL_SIG,           "CLEANSE_PILL",             'c'    },
{    BARRIER_PILL_SIG,           "BARRIER_PILL",             'b'    },
{    SINGULARITY_PILL_SIG,       "SINGULARITY_PILL",         'S'    },
{    SONG_PILL_SIG,              "SONG_PILL",                's'    },
{    DEFAULT_PILL_SIG,           "DEFAULT_PILL",             'd'    },
{    MAX_PILL_SIG,               "MAX_PILL",                 'M'    },

                
{    TERMINATE_SIG,          "TERMINATE",            0x1B   }

};


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
