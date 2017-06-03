#include "filter.h"

Filter::Filter() {
    output = Vector();
}

Vector Filter::setInput(const Vector value, const float delta) {
    output += (value - output) * (delta / ACCELERATION_TIME_CONST);
    return output;    
}
