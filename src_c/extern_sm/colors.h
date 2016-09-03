/* 
Color defenitions to use in different modules
*/
#ifndef colors_h
#define colors_h

#include <stdint.h>

enum ColorsNum {
    BLANK,
    WHITE,
    RED,
    ORANGE,
    YELLOW,
    GREEN,
    BLUE,
    VIOLET,
    MAX_COLOR
};

typedef struct Color_ {
    uint8_t R;
    uint8_t G;
    uint8_t B;
} Color;

extern const Color Colors[MAX_COLOR];
    
    
#endif
