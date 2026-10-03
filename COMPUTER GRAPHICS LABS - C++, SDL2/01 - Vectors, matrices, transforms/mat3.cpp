#include<stdio.h>
#include "mat3.h"
#include "vec3.h"

namespace egc {
    mat3& mat3::operator =(const mat3& srcMatrix) {
        for (int i = 0; i < 3; i++)
            for(int j=0; j<3; j++)
            {
                this->at(j, i) = srcMatrix.at(j, i);
            }
        return *this;
    };
    mat3 mat3::operator *(float scalarValue) const {
        mat3 matrix;
        for (int i = 0; i < 3; i++)
            for (int j = 0; j < 3; j++)
            {
               matrix.at(j, i) = this->at(j, i) * scalarValue;
            }
        return matrix;
    }
    mat3 mat3::operator *(const mat3& srcMatrix) const {
        mat3 matrix;
        for (int i = 0; i < 3; i++) {
            for (int j = 0; j < 3; j++) {
                float sum = 0;
                for (int k = 0; k < 3; k++) {
                    sum += (this->at(i, k) * srcMatrix.at(k, j));
                }
                matrix.at(i, j) = sum;
            }
        }
        return matrix;
    }
    vec3 mat3::operator *(const vec3& srcVector) const {
        vec3 result;
        
         result.x = this->at(0, 0) * srcVector.x + this->at(0, 1) * srcVector.y + this->at(0, 2) * srcVector.z;
         result.y = this->at(1, 0) * srcVector.x + this->at(1, 1) * srcVector.y + this->at(1, 2) * srcVector.z;
         result.z = this->at(2, 0) * srcVector.x + this->at(2, 1) * srcVector.y + this->at(2, 2) * srcVector.z;
         return result;
    }
    mat3 mat3::operator +(const mat3& srcMatrix) const {
        mat3 matrix;
        for (int i = 0; i < 3; i++)
            for (int j = 0; j < 3; j++)
            {
                matrix.at(j, i) = this->at(j, i) + srcMatrix.at(i, j);
            }
        return matrix;
    };
    //get element by (row, column)
    float& mat3::at(int i, int j) {
        return this->matrixData[3 * j + i];
    }

    const float& mat3::at(int i, int j) const {
        return this->matrixData[3 * j + i];
    }
    float mat3::determinant() const {
        return this->at(0, 0) * (this->at(1, 1) * this->at(2, 2) - this->at(2, 1) * this->at(1, 2))
            - this->at(0, 1) * (this->at(1, 0) * this->at(2, 2) - this->at(2, 0) * this->at(1, 2))
            + this->at(0, 2) * (this->at(1, 0) * this->at(2, 1) - this->at(2, 0) * this->at(1, 1));
    }
    mat3 mat3::inverse() const {
        mat3 matrix;
        if (this->determinant() == 0)
            return NULL;
        for (int i = 0; i < 3; i++) {
            for (int j = 0; j < 3; j++)
            {
                matrix.at(i, j) = this->at((j + 1) % 3, (i + 1) % 3) * this->at((j + 2) % 3, (i + 2) % 3) - this->at((j + 1) % 3, (i + 2) % 3) * this->at((j + 2) % 3, (i + 1) % 3);
                matrix.at(i, j) = matrix.at(i, j) / this->determinant();
            }
            return matrix;
        }
    }
    mat3 mat3::transpose() const {
        mat3 matrix;
        for (int i=0; i<3; i++)
            for (int j = 0; j < 3; j++)
                matrix.at(i, j) = this->at(j, i);
        return matrix;
    }
}