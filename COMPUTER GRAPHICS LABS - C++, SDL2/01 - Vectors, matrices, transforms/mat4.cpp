#include <stdio.h>
#include "mat4.h"
namespace egc {
	float& mat4::at(int i, int j) {
		return matrixData[i + j * 4];
	}
	const float& mat4::at(int i, int j) const {
		return matrixData[i + j * 4];
	}
	mat4& mat4::operator =(const mat4& srcMatrix) {
		for (int i = 0; i < 4; i++)
			for (int j = 0; j < 4; j++)
			{
				this->at(i, j) = srcMatrix.at(i, j);
			}
		return *this;

	}
	mat4 mat4::operator *(float scalarValue) const {
		mat4 rezultat;
		for (int i = 0; i < 4; i++)
			for (int j = 0; j < 4; j++) {
				rezultat.at(i, j) = this->at(i, j) * scalarValue;
			}
		return rezultat;
	}
	mat4 mat4::operator *(const mat4& srcMatrix) const {
		mat4 m4;
		for (int i = 0; i < 4; ++i) {
			for (int j = 0; j < 4; ++j) {
				m4.at(i, j) = 0;
				for (int k = 0; k < 4; ++k) {
					m4.at(i, j) += this->at(i, k) * srcMatrix.at(k, j);
				}
			}
		}
		return m4;
	}

	vec4 mat4::operator *(const vec4& srcVector) const {
		vec4 rezultat;
		float suma = 0;
		for (int i = 0; i < 4; i++) {
			suma = 0;
			for (int j = 0; j < 4; j++) {
				suma = suma + this->at(0, j) * srcVector.x;

			}
			rezultat.x = suma;
			suma = 0;
			for (int j = 0; j < 4; j++) {
				suma = suma + this->at(1, j) * srcVector.y;

			}
			rezultat.y = suma;
			suma = 0;
			for (int j = 0; j < 4; j++) {
				suma = suma + this->at(2, j) * srcVector.z;

			}
			rezultat.z = suma;

			suma = 0;
			for (int j = 0; j < 4; j++) {
				suma = suma + this->at(3, j) * srcVector.w;

			}
			rezultat.w = suma;
		}
		return rezultat;

	}

	mat4 mat4::operator +(const mat4& srcMatrix) const {
		mat4 rezultat;
		for (int i = 0; i < 4; i++)
			for (int j = 0; j < 4; j++) {
				rezultat.at(i, j) = this->at(i, j) + srcMatrix.at(i, j);
			}
		return rezultat;
	}

	float mat4::determinant() const {
		mat4 rez;
			float c, det = 1;
			rez = *this;

			for (int i = 0; i < 4; i++) {
				for (int k = i + 1; k < 4; k++) {
					
						c = rez.at(k, i) / rez.at(i, i);
						for (int j = i; j < 4; j++)
							rez.at(k, j) -= c * rez.at(i, j);
					
				}
			}
			for (int i = 0; i < 4; i++)
				det *= rez.at(i,i);

		return det;
	}

	

	mat4 mat4::inverse() const {
		mat4 inverseMatrix;
		mat4 tempMatrix;
		mat4 adjMatrix;
		int sign = 1;
		for (int i = 0; i < 4; i++) {
			for (int j = 0; j < 4; j++) {
				int k1 = 0;
				int k2 = 0;
				for (int row = 0; row < 4; row++) {
					for (int col = 0; col < 4; col++)
					{
						if (row != i && col != j)
						{
							tempMatrix.at(k1, k2++) = this->at(row, col);
							if (k2 == 3) {
								k2 = 0;
								k1++;
							}
						}
					}
				}
				sign = (i + j) % 2 == 0 ? 1 : -1;
				adjMatrix.at(j, i) = sign * tempMatrix.determinant();
			}
		}

		for (int i = 0; i < 4; i++)
		{
			for (int j = 0; j < 4; j++)
			{
				inverseMatrix.at(i, j) = adjMatrix.at(i, j) / determinant();
			}
		}
		return inverseMatrix;
	}
	mat4 mat4::transpose() const {
		mat4 transpusa;
		for (int i = 0; i < 4; i++)
			for (int j = 0; j < 4; j++) {
				transpusa.at(i, j) = this->at(j, i);
			}
		return transpusa;
	}

}