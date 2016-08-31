/* 
Color defenitions to use in different modules
*/
#ifndef colors_h
#define colors_h

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

static const Color Colors[MAX_COLOR] = {
    {   0,   0,   0},
    { 255, 255, 255},
    { 255,   0,   0},
    { 255, 165,   0},
    { 255, 255,   0},
    {   0,   0, 255},
    { 127,   0, 255}
};
    
    
#endif
