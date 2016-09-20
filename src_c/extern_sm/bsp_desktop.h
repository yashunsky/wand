/* 
Board Support Package.
Module to replace for various platforms.
*/
#ifndef bsp_desktop_h
#define bsp_desktop_h

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#include "vibro_desktop.h"
#include "RGB_desktop.h"

#define DESKTOP

#ifdef DESKTOP
    #include "generation_light.h"
    enum DesktopSignal {
        TERMINATE_SIG = LAST_USER_SIG + 1 /* terminate the application */
    };
#endif

#endif
