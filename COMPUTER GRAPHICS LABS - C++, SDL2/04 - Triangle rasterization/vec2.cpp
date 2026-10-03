#include <stdio.h>
#include "vec2.h"

namespace egc {

    vec2& vec2::operator =(const vec2& srcVector) {
        this->x = srcVector.x;
        this->y = srcVector.y;

        return *this;
    }
    vec2 vec2::operator +(const vec2& srcVector) const {
        return vec2(this->x + srcVector.x, this->y + srcVector.y);
    }

    vec2& vec2::operator +=(const vec2& srcVector) {
        this->x += srcVector.x;
        this->y += srcVector.y;
        
        return *this;
    }
    vec2 vec2::operator *(float scalarValue) const {
        return vec2(this->x * scalarValue, this->y * scalarValue);
    }
    vec2 vec2::operator -(const vec2& srcVector) const {
        return vec2(this->x - srcVector.x, this->y - srcVector.y);
    }
    vec2& vec2::operator -=(const vec2& srcVector) {
        this->x -= srcVector.x;
        this->y -= srcVector.y;

        return *this;
    }
    vec2 vec2::operator -() const {
        return vec2(this->x * (-1), this->y * (-1));
    }
    float vec2::length() const {
        return sqrt(this->x * this->x + this->y * this->y);
    }
    vec2& vec2::normalize() {
        float length = this->length();
        this->x = this->x / length;
        this->y = this->y / length;

        return *this;
    }

    float dotProduct(const vec2& v1, const vec2& v2) {
        return v1.x * v2.x + v1.y * v2.y;
    }
}