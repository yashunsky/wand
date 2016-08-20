/* Additional entities for convenience
*/
#ifndef service_h
#define service_h

#define     ARRAY_SIZE(foo) (sizeof(foo)/sizeof(foo[0]))

#include <stdint.h>
#include "generation_light.h"

/* Keystroke-signal aliases to use with printf */
typedef struct KeyStroke_ {
   uint8_t          Com;      // Command
   char const      *Alias;    // Sting name for command
   uint8_t          Key;      // Keyboard symbol
} KeyStroke;

static const KeyStroke KeyStrokes[] = {
{    CHARGE_SIG,         "CHARGE",           'q'    },
{    SONG_SIG,           "SONG",             'w'    },
{    SINGULAR_SIG,       "SINGULAR",         'e'    },
{    BARRIER_SIG,        "BARRIER",          'r'    },
{    CLEANSE_SIG,        "CLEANSE",          'f'    },
                
{    THROW_SIG,          "THROW",            't'    },
{    PUNCH_SIG,          "PUNCH",            'y'    },
{    LIFT_SIG,           "LIFT",             'u'    },
{    WARP_SIG,           "WARP",             'i'    },
{    RELEASE_SIG,        "RELEASE",          'o'    },
{    PWR_RELEASE_SIG,    "PWR_RELEASE",      'p'    },

                
{    TERMINATE_SIG,          "TERMINATE",            0x1B   }

};


/* Colors section */
enum Colors {
    BLANK,
    WHITE,
    RED,
    ORANGE,
    YELLOW,
    GREEN,
    VIOLET
};

typedef struct Color_ {
   uint8_t          Num;      // Color number
   char const      *Name;     // Color name
} Color;

static const Color ColorNames[] = {
{    BLANK,     "BLANK" },
{    WHITE,     "WHITE" },
{    RED,       "RED"   },
{    ORANGE,    "ORANGE"},
{    YELLOW,    "YELLOW"},
{    GREEN,     "GREEN"},
{    VIOLET,    "VIOLET"}
};

#endif
