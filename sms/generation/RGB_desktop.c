#include "RGB_desktop.h"

void RGB_blink_slow(uint8_t Color) {
    //#ifdef HANDLE
 
        
        hConsole = GetStdHandle(STD_OUTPUT_HANDLE);
        if (BlinkOn) {
            BlinkPhase = 0;
            RGB_blink_toggle();
        }
        GetConsoleScreenBufferInfo(hConsole, &consoleInfo);
        SavedAttr = consoleInfo.wAttributes;
        OldCursCoord = consoleInfo.dwCursorPosition;
        
    //#endif
        printf("blink_slow(");
        SetConsoleTextAttribute(hConsole, ColorNames[Color].WinColor);
        GetConsoleScreenBufferInfo(hConsole, &consoleInfo);
        BlinkCoord = consoleInfo.dwCursorPosition;
        printf("%s", ColorNames[Color].Name);
        SetConsoleTextAttribute(hConsole, SavedAttr);
        printf(");");
        BlinkOn = 1;
        BlinkPhase = 1;
        BlinkColor = Color;
        BlinkTimer = 5; //100ms
}

void RGB_blink_fast(uint8_t Color) {
        hConsole = GetStdHandle(STD_OUTPUT_HANDLE);
        if (BlinkOn) {
            BlinkPhase = 0;
            RGB_blink_toggle();
        }
        GetConsoleScreenBufferInfo(hConsole, &consoleInfo);
        SavedAttr = consoleInfo.wAttributes;
        OldCursCoord = consoleInfo.dwCursorPosition;
        
    //#endif
        printf("blink_fast(");
        SetConsoleTextAttribute(hConsole, ColorNames[Color].WinColor);
        GetConsoleScreenBufferInfo(hConsole, &consoleInfo);
        BlinkCoord = consoleInfo.dwCursorPosition;
        printf("%s", ColorNames[Color].Name);
        SetConsoleTextAttribute(hConsole, SavedAttr);
        printf(");");
        BlinkOn = 1;
        BlinkPhase = 1;
        BlinkColor = Color;
        BlinkTimer = 2; //100ms
}

void RGB_blink_stop() {
    BlinkPhase = 0;
    if (BlinkOn) RGB_blink_toggle();
    printf("blink_stop();");
    BlinkOn = 0;
}

//Only for Windows blink implementation
void RGB_blink_toggle() {
    GetConsoleScreenBufferInfo(hConsole, &consoleInfo);
    OldCursCoord = consoleInfo.dwCursorPosition;
    SetConsoleCursorPosition(hConsole, BlinkCoord);
    if (!BlinkPhase) {
        SetConsoleTextAttribute(hConsole, ColorNames[BlinkColor].WinColor);
    }
    else {
        SetConsoleTextAttribute(hConsole, 0x00);
    }
    printf("%s", ColorNames[BlinkColor].Name);
    BlinkPhase ^= 1; // Invert Phase
    SetConsoleCursorPosition(hConsole, OldCursCoord);
    SetConsoleTextAttribute(hConsole, SavedAttr);
    //printf("Phase: %u;", BlinkPhase);
}
