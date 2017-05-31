#include "bsp_python.h"
#include <stdio.h>

void RGB_blink_slow(uint8_t Color) {
    printf("RGB_blink_slow(%u);\n", Color);
}

void RGB_blink_fast(uint8_t Color) {
    printf("RGB_blink_fast(%u);\n", Color);
}

void RGB_blink_stop() {
    printf("RGB_blink_stop();\n");
}

void vibro(uint8_t Power) {
    printf("vibro(%u);\n", Power);
}
