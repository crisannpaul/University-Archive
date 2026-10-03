#include "mat3.h"

namespace egc {
    mat3& mat3::operator =(const mat3& srcMatrix) {
        for (int i = 0; i < 9; i++) {
            this->matrixData[i] = srcMatrix.matrixData[i];
        }
        return *this;
    }
    mat3 mat3::operator *(float scalarValue) const {
        mat3 temp;
        for (int i = 0; i < 3;i++) 
            for (int j = 0; j < 3;j++) {
                temp.at(i, j) = this->at(i, j) * scalarValue;
            }
        return temp;
    }
    mat3 mat3::operator *(const mat3& srcMatrix) const {
        mat3 temp;
        for (int i = 0; i < 3;i++)
            for (int j = 0; j < 3;j++) {
                temp.at(i, j) = 0;
                for (int m = 0; m < 3;m++)
                    temp.at(i, j) += this->at(i, m) * srcMatrix.at(m, j);
            }
        return temp;
    }
    vec3 mat3::operator *(const vec3& srcVector) const {
        vec3 temp;
        temp.x = this->at(0, 0) * srcVector.x + this->at(0, 1) * srcVector.y + this->at(0, 2) * srcVector.z;
        temp.y = this->at(1, 0) * srcVector.x + this->at(1, 1) * srcVector.y + this->at(1, 2) * srcVector.z;
        temp.z = this->at(2, 0) * srcVector.x + this->at(2, 1) * srcVector.y + this->at(2, 2) * srcVector.z;
        return temp;
    }
    mat3 mat3::operator +(const mat3& srcMatrix) const {
        mat3 temp;
        for (int i = 0; i < 3; i++) 
            for (int j = 0; j < 3; j++) {
                temp.at(i, j) = this->at(i, j) + srcMatrix.at(i, j);
            }
        return temp;
    }
    //get element by (row, column)
    float& mat3::at(int i, int j) { //setter
        return this->matrixData[i + 3 * j]; // a.at(2,3) = 5;
    }
    const float& mat3::at(int i, int j) const {
        return this->matrixData[i + 3 * j]; // float f = a.at(2.3);
    }//getter
    float mat3::determinant() const {
        float temp = 0;
        temp  = this->at(0, 0) * this->at(1, 1) * this->at(2, 2);
        temp += this->at(1, 0) * this->at(2, 1) * this->at(0, 2);
        temp += this->at(2, 0) * this->at(0, 1) * this->at(1, 2);

        temp -= this->at(0, 2) * this->at(1, 1) * this->at(2, 0);
        temp -= this->at(0, 0) * this->at(2, 1) * this->at(1, 2);
        temp -= this->at(1, 0) * this->at(0, 1) * this->at(2, 2);
        return temp;
    }
    mat3 mat3::inverse() const {
        mat3 matInverse;
        mat3 matTranspose = this->transpose();
        float det = this->determinant();
        if (det == 0)
            return mat3();

        for (int i = 0; i < 3; i++)
            for (int j = 0; j < 3; j++) {
                matInverse.at(i, j) = ( this->at((j+1) % 3, (i+1) % 3) * this->at((j + 2) % 3, (i + 2) % 3) - this->at((j + 1) % 3, (i + 2) % 3) * this->at((j + 2) % 3, (i + 1) % 3) );
            }
        matInverse = matInverse * (1 / det);
        return matInverse;
    }
    mat3 mat3::transpose() const {
        mat3 temp;
        for (int i = 0; i < 3; i++)
            for (int j = 0; j < 3; j++)
                temp.at(i, j) = this->at(j, i);
        return temp;
    }
}