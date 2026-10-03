#include "vec3.h"

namespace egc {
    vec3& vec3::operator =(const vec3& srcVector) {
        this->x = srcVector.x;
        this->y = srcVector.y;
        this->z = srcVector.z;
        return *this;
    }
    vec3 vec3::operator +(const vec3& srcVector) const {
        vec3 temp;
        temp.x = this->x + srcVector.x;
        temp.y = this->y + srcVector.y;
        temp.z = this->z + srcVector.z;
        return temp;
    }
    vec3& vec3::operator +=(const vec3& srcVector) {
        x = x + srcVector.x;
        y = y + srcVector.y;
        z = z + srcVector.z;
        return *this;
    }
    vec3 vec3::operator *(float scalarValue) const {
        vec3 temp;
        temp.x = this->x * scalarValue;
        temp.y = this->y * scalarValue;
        temp.z = this->z * scalarValue;
        return temp;
    }
    vec3 vec3::operator -(const vec3& srcVector) const {
        vec3 temp;
        temp.x = this->x - srcVector.x;
        temp.y = this->y - srcVector.y;
        temp.z = this->z - srcVector.z;
        return temp;
    }
    vec3& vec3::operator -=(const vec3& srcVector) {
        x = x - srcVector.x;
        y = y - srcVector.y;
        z = z - srcVector.z;
        return *this;
    }
    vec3 vec3::operator -() const {
        vec3 temp;
        temp.x = -this->x;
        temp.y = -this->y;
        temp.z = -this->z;
        return temp;
    }
    float vec3::length() const {
        return sqrt(this->x * this->x + this->y * this->y + this->z * this->z);
    }
    vec3& vec3::normalize() {
        float l = this->length();
        this->x = this->x / l;
        this->y = this->y / l;
        this->z = this->z / l;
        return *this;
    }
    float dotProduct(const vec3& v1, const vec3& v2) {
        return v1.x * v2.x + v1.y * v2.y + v1.z * v2.z;
    }
    vec3 crossProduct(const vec3& v1, const vec3& v2) {
        vec3 temp;
        temp.x = v1.y * v2.z - v1.z * v2.y;
        temp.y = v1.z * v2.x - v1.x * v2.z;
        temp.z = v1.x * v2.y - v1.y * v2.x;
        return temp;
    }
}