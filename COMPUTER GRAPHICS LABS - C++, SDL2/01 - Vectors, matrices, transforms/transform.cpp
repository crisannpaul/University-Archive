#include"transform.h"
#include "vec2.h"
#include "vec3.h"
#include "mat3.h"
#include "mat4.h"
#include<math.h>


namespace egc {
    ///const double PI = atan(1.0) * 4;

    //transformation matrices in 2D
    mat3 translate(const vec2 translateArray) 
    {
        mat3 rezult;
        rezult.at(0, 0) = 1;
        rezult.at(0, 1) = 0;
        rezult.at(0, 2) = translateArray.x;
        rezult.at(1, 0) = 0;
        rezult.at(1, 1) = 1;
        rezult.at(1, 2) = translateArray.y;
        rezult.at(2, 0) = 0;
        rezult.at(2, 1) = 0;
        rezult.at(2, 2) = 1;
        return rezult;
    }
    mat3 translate(float tx, float ty) {
        mat3 rezult;
        rezult.at(0, 0) = 1;
        rezult.at(0, 1) = 0;
        rezult.at(0, 2) = tx;
        rezult.at(1, 0) = 0;
        rezult.at(1, 1) = 1;
        rezult.at(1, 2) = ty;
        rezult.at(2, 0) = 0;
        rezult.at(2, 1) = 0;
        rezult.at(2, 2) = 1;
        return rezult;
    }

    mat3 scale(const vec2 scaleArray) {
        mat3 rezult;
        rezult.at(0, 0) = scaleArray.x;
        rezult.at(0, 1) = 0;
        rezult.at(0, 2) = 0;
        rezult.at(1, 0) = 0;
        rezult.at(1, 1) = scaleArray.y;
        rezult.at(1, 2) = 0;
        rezult.at(2, 0) = 0;
        rezult.at(2, 1) = 0;
        rezult.at(2, 2) = 1;
        return rezult;
    }
    mat3 scale(float sx, float sy) {
        mat3 rezult;
        rezult.at(0, 0) = sx;
        rezult.at(0, 1) = 0;
        rezult.at(0, 2) = 0;
        rezult.at(1, 0) = 0;
        rezult.at(1, 1) = sy;
        rezult.at(1, 2) = 0;
        rezult.at(2, 0) = 0;
        rezult.at(2, 1) = 0;
        rezult.at(2, 2) = 1;
        return rezult;
    }

    mat3 rotate(float angle) {
        double rad = angle * (PI / 180);

        mat3 rezult;
        rezult.at(0, 0) = cos(rad);
        rezult.at(0, 1) = -sin(rad);
        rezult.at(0, 2) = 0;
        rezult.at(1, 0) = sin(rad);
        rezult.at(1, 1) = cos(rad);
        rezult.at(1, 2) = 0;
        rezult.at(2, 0) = 0;
        rezult.at(2, 1) = 0;
        rezult.at(2, 2) = 1;
        return rezult;
    }

    //transformation matrices in 3D
    mat4 translate(const vec3 translateArray){
        mat4 rezult;
        rezult.at(0, 0) = 1;
        rezult.at(0, 1) = 0;
        rezult.at(0, 2) = 0;
        rezult.at(0, 3) = translateArray.x;
        rezult.at(1, 0) = 0;
        rezult.at(1, 1) = 1;
        rezult.at(1, 2) = 0;
        rezult.at(1, 3) = translateArray.y;
        rezult.at(2, 0) = 0;
        rezult.at(2, 1) = 0;
        rezult.at(2, 2) = 1;
        rezult.at(2, 3) = translateArray.z;
        rezult.at(3, 0) = 0;
        rezult.at(3, 1) = 0;
        rezult.at(3, 2) = 0;
        rezult.at(3, 3) = 1;
        return rezult;
    };

    mat4 translate(float tx, float ty, float tz) {
        mat4 rezult;
        rezult.at(0, 0) = 1;
        rezult.at(0, 1) = 0;
        rezult.at(0, 2) = 0;
        rezult.at(0, 3) = tx;
        rezult.at(1, 0) = 0;
        rezult.at(1, 1) = 1;
        rezult.at(1, 2) = 0;
        rezult.at(1, 3) = ty;
        rezult.at(2, 0) = 0;
        rezult.at(2, 1) = 0;
        rezult.at(2, 2) = 1;
        rezult.at(2, 3) = tz;
        rezult.at(3, 0) = 0;
        rezult.at(3, 1) = 0;
        rezult.at(3, 2) = 0;
        rezult.at(3, 3) = 1;
        return rezult;
    };

    mat4 scale(const vec3 scaleArray) {
        mat4 rezult;
        rezult.at(0, 0) = scaleArray.x;
        rezult.at(0, 1) = 0;
        rezult.at(0, 2) = 0;
        rezult.at(0, 3) = 0;
        rezult.at(1, 0) = 0;
        rezult.at(1, 1) = scaleArray.y;
        rezult.at(1, 2) = 0;
        rezult.at(1, 3) = 0;
        rezult.at(2, 0) = 0;
        rezult.at(2, 1) = 0;
        rezult.at(2, 2) = scaleArray.z;
        rezult.at(2, 3) = 0;
        rezult.at(3, 0) = 0;
        rezult.at(3, 1) = 0;
        rezult.at(3, 2) = 0;
        rezult.at(3, 3) = 1;
        return rezult;
    };
    mat4 scale(float sx, float sy, float sz) {
        mat4 rezult;
        rezult.at(0, 0) = sx;
        rezult.at(0, 1) = 0;
        rezult.at(0, 2) = 0;
        rezult.at(0, 3) = 0;
        rezult.at(1, 0) = 0;
        rezult.at(1, 1) = sy;
        rezult.at(1, 2) = 0;
        rezult.at(1, 3) = 0;
        rezult.at(2, 0) = 0;
        rezult.at(2, 1) = 0;
        rezult.at(2, 2) = sz;
        rezult.at(2, 3) = 0;
        rezult.at(3, 0) = 0;
        rezult.at(3, 1) = 0;
        rezult.at(3, 2) = 0;
        rezult.at(3, 3) = 1;
        return rezult;
    };

    mat4 rotateX(float angle) {

        double rad = angle * (PI / 180);

        mat4 rezult;
        rezult.at(0, 0) = 1;
        rezult.at(0, 1) = 0;
        rezult.at(0, 2) = 0;
        rezult.at(0, 3) = 0;
        rezult.at(1, 0) = 0;
        rezult.at(1, 1) = cos(rad);
        rezult.at(1, 2) = -sin(rad);
        rezult.at(1, 3) = 0;
        rezult.at(2, 0) = 0;
        rezult.at(2, 1) = sin(rad);
        rezult.at(2, 2) = cos(rad);
        rezult.at(2, 3) = 0;
        rezult.at(3, 0) = 0;
        rezult.at(3, 1) = 0;
        rezult.at(3, 2) = 0;
        rezult.at(3, 3) = 1;
        return rezult;
    };
    mat4 rotateY(float angle) {
        double rad = angle * (PI / 180);

        mat4 rezult;
        rezult.at(0, 0) = cos(rad);
        rezult.at(0, 1) = 0;
        rezult.at(0, 2) = sin(rad);
        rezult.at(0, 3) = 0;
        rezult.at(1, 0) = 0;
        rezult.at(1, 1) = 1;
        rezult.at(1, 2) = 0;
        rezult.at(1, 3) = 0;
        rezult.at(2, 0) = -sin(rad);
        rezult.at(2, 1) = 0;
        rezult.at(2, 2) = cos(rad);
        rezult.at(2, 3) = 0;
        rezult.at(3, 0) = 0;
        rezult.at(3, 1) = 0;
        rezult.at(3, 2) = 0;
        rezult.at(3, 3) = 1;
        return rezult;
    };
    mat4 rotateZ(float angle) {
        double rad = angle * (PI / 180);

        mat4 rezult;
        rezult.at(0, 0) = cos(rad);
        rezult.at(0, 1) = -sin(rad);
        rezult.at(0, 2) = 0;
        rezult.at(0, 3) = 0;
        rezult.at(1, 0) = sin(rad);
        rezult.at(1, 1) = cos(rad);
        rezult.at(1, 2) = 0;
        rezult.at(1, 3) = 0;
        rezult.at(2, 0) = 0;
        rezult.at(2, 1) = 0;
        rezult.at(2, 2) = 1;
        rezult.at(2, 3) = 0;
        rezult.at(3, 0) = 0;
        rezult.at(3, 1) = 0;
        rezult.at(3, 2) = 0;
        rezult.at(3, 3) = 1;
        return rezult;
    };
}
