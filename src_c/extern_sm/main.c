/*****************************************************************************
* Product: History Example, Win32
* Last updated for version 5.6.0
* Last updated on  2015-12-18
*
*                    Q u a n t u m     L e a P s
*                    ---------------------------
*                    innovating embedded systems
*
* Copyright (C) Quantum Leaps, LLC. All rights reserved.
*
* This program is open source software: you can redistribute it and/or
* modify it under the terms of the GNU General Public License as published
* by the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*
* Alternatively, this program may be distributed and modified under the
* terms of Quantum Leaps commercial licenses, which expressly supersede
* the GNU General Public License and are specifically designed for
* licensees interested in retaining the proprietary status of their code.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program. If not, see <http://www.gnu.org/licenses/>.
*
* Contact information:
* http://www.state-machine.com
* mailto:info@state-machine.com
*****************************************************************************/

//#define DEBUG_SM                // Printing states  

//#include "qep_port.h"
//#include "qassert.h"
#include <conio.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>


#include "bsp.h"
#include "RGB_desktop.h"
#include "generation_light.h"
#include "service.h"
#include "biotics.h"

/*..........................................................................*/
    
int main() {
    uint8_t     i;                                      // Universal counter
    printf("GENERATION Light State Machines\n");
    #ifdef DEBUG_SM
        printf("DEBUG_SM enabled\n\r");
    #endif
    #ifdef DESKTOP
        printf("Desktop version\n\r");
    #endif
    //for (i = 0; i < ARRAY_SIZE(KeyStrokes) - 1;i++)     // Exluding ESC
    for (i = 0; i < (TERMINATE_SIG - Q_USER_SIG) - 1;i++)     // Exluding ESC
        printf("%18s - '%c'\n\r", KeyStrokes[i].Alias, KeyStrokes[i].Key);
    printf("Press ESC to quit...\n");

      /* instantiate the HSM and trigger the initial transition */

    Biotics_ctor();
    QMSM_INIT(the_biotics, (QEvt *)0);
    Hand_ctor();
    QMSM_INIT(the_hand, (QEvt *)0);
    QEvt e;
    uint8_t c;
    //e.sig = MAX_PILL_SIG;
    //QMSM_DISPATCH(the_hand,  &e);
    for (;;) {
        static int tickCtr = 1;
        char const *msg = (char *)0;

        usleep(100000);

        if (kbhit()) {
            c = (uint8_t)_getch();     /* read one character from the console */
            printf("%c: ", c);
            //for (i = 0; i < ARRAY_SIZE(KeyStrokes);i++) {
            for (i = 0; i < (TERMINATE_SIG - Q_USER_SIG); i++) {
                if (c ==    KeyStrokes[i].Key) {
                    e.sig = KeyStrokes[i].Com;
                    msg = c;
                    break;
                }
            }
        }
        else if (--tickCtr == 0) { /* time for the tick? */
            tickCtr = 10;
            e.sig = TICK_SEC_SIG;
            msg = "TICK";
            }
        if (BlinkOn) {
            if (tickCtr % BlinkTimer == 0) RGB_blink_toggle();
        }
        if (msg != (char *)0) {
                                 /* dispatch the event into the state machine */
            QState r;
            r = QMSM_DISPATCH(the_biotics,  &e);
            QMSM_DISPATCH(the_hand,  &e);
            #ifdef DEBUG
                printf("returned: %u\n\r", r);
            #endif    
            if (msg != "TICK") {
                printf("\n");
                //BlinkCoord.Y--;   // FAR manager console needs this
            }
        }
    }
    return 0;
}
/*..........................................................................*/
void Q_onAssert(char const * const file, int line) {
    fprintf(stderr, "Assertion failed in %s, line %d", file, line);
    _exit(-1);
}
