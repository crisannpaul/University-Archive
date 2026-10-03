#include "vec4.h"

namespace egc {
    vec4& vec4::operator =(const vec4& srcVector) {
        this->x = srcVector.x;
        this->y = srcVector.y;
        this->z = srcVector.z;
        this->w = srcVector.w;
        return *this;
    }
    vec4 vec4::operator +(const vec4& srcVector) const {
        vec4 temp;
        temp.x = this->x + srcVector.x;
        temp.y = this->y + srcVector.y;
        temp.z = this->z + srcVector.z;
        temp.w = this->w + srcVector.w;
        return temp;
    }
    vec4& vec4::operator +=(const vec4& srcVector) {
        x = x + srcVector.x;
        y = y + srcVector.y;
        z = z + srcVector.z;
        w = w + srcVector.w;
        return *this;
        }
    vec4 vec4::operator *(float scalarValue) const {
        vec4 temp;
        temp.x = this->x * scalarValue;
        temp.y = this->y * scalarValue;
        temp.z = this->z * scalarValue;
        temp.w = this->w * scalarValue;
        return temp;
        }
    vec4 vec4::operator -(const vec4& srcVector) const {
        vec4 temp;
        temp.x = this->x - srcVector.x;
        temp.y = this->y - srcVector.y;
        temp.z = this->z - srcVector.z;
        temp.w = this->w - srcVector.w;
        return temp;
        }
    vec4& vec4::operator -=(const vec4& srcVector) {
        x = x - srcVector.x;
        y = y - srcVector.y;
        z = z - srcVector.z;
        w = w - srcVector.w;
        return *this;
        }
    vec4 vec4::operator -() const {
        vec4 temp;
        temp.x = -this->x;
        temp.y = -this->y;
        temp.z = -this->z;
        temp.w = -this->w;
        return temp;
        }
    float vec4::length() const {
        return sqrt(this->x * this->x + this->y * this->y + this->z * this->z + this->w * this->w);
        }
    vec4& vec4::normalize() {
        float l = this->length();
        this->x = this->x / l;
        this->y = this->y / l;
        this->z = this->z / l;
        this->w = this->w / l;
        return *this;
        }
}