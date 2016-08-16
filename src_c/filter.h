#ifndef Filter_h
#define Filter_h

#include "knowledge.h"

class Filter {
  float output[DIMENTION];

public:
  Filter();
  float* setInput(const float value[DIMENTION], const float delta);
};

#endif


