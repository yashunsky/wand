#ifndef Filter_h
#define Filter_h

#include "knowledge.h"
#include "ahrsmath.h"

class Filter {
  Vector output;

public:
  Filter();
  Vector setInput(const Vector value, const float delta);
};

#endif


