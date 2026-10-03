#include "mat4.h"
#include "mat3.h"

namespace egc {
	mat4& mat4::operator=(const mat4& srcMatrix)
	{
		for (int i = 0; i < 16; i++) {
			this->matrixData[i] = srcMatrix.matrixData[i];
		}
		return *this;
	}
	mat4 mat4::operator*(float scalarValue) const
	{
		mat4 temp;
		for (int i = 0; i < 4; i++)
			for (int j = 0; j < 4; j++)
				temp.at(i, j) = this->at(i, j) * scalarValue;
		return temp;
	}
	mat4 mat4::operator*(const mat4& srcMatrix) const
	{
		mat4 temp;
		for (int i = 0; i < 4; i++)
			for (int j = 0; j < 4; j++) {
				temp.at(i, j) = 0;
				for (int m = 0; m < 4; m++)
					temp.at(i, j) += this->at(i, m) * srcMatrix.at(m, j);
			}
		return temp;
	}
	vec4 mat4::operator*(const vec4& srcVector) const
	{
		vec4 temp;
		temp.x = this->at(0, 0) * srcVector.x + this->at(0, 1) * srcVector.y + this->at(0, 2) * srcVector.z + this->at(0, 3) * srcVector.w;
		temp.y = this->at(1, 0) * srcVector.x + this->at(1, 1) * srcVector.y + this->at(1, 2) * srcVector.z + this->at(1, 3) * srcVector.w;
		temp.z = this->at(2, 0) * srcVector.x + this->at(2, 1) * srcVector.y + this->at(2, 2) * srcVector.z + this->at(2, 3) * srcVector.w;
		temp.w = this->at(3, 0) * srcVector.x + this->at(3, 1) * srcVector.y + this->at(3, 2) * srcVector.z + this->at(3, 3) * srcVector.w;
		return temp;
	}
	mat4 mat4::operator+(const mat4& srcMatrix) const
	{
		mat4 temp;
		for (int i = 0; i < 4; i++)
			for (int j = 0; j < 4; j++)
				temp.at(i, j) = this->at(i, j) + srcMatrix.at(i, j);
		return temp;
	}
	float& mat4::at(int i, int j)
	{
		return this->matrixData[i + 4 * j];
	}
	const float& mat4::at(int i, int j) const
	{
		return this->matrixData[i + 4 * j]; // float f = a.at(2.3);
	}
	float mat4::determinant() const
	{
		float D = 0.0f;
		mat3 temp;
		int sign = 1;

		for (int k = 0; k < 4; k++) {
			int i = 0, j = 0;
			for (int row = 1; row < 4; row++)
				for (int col = 0; col < 4; col++)
					if (col != k) {
						temp.at(i, j++) = this->at(row, col);
						if (j == 3) {
							j = 0;
							i++;
						}
					}

			D += sign * this->at(0, k) * temp.determinant();
			sign = -sign;
		}

		return D;
	}

	mat4 mat4::inverse() const
	{
		float const* m = this->matrixData;
		float inv[16], det = this->determinant();

		if (det == 0.0f)
			return nullptr;

		inv[0] = m[5] * m[10] * m[15] -
			m[5] * m[11] * m[14] -
			m[9] * m[6] * m[15] +
			m[9] * m[7] * m[14] +
			m[13] * m[6] * m[11] -
			m[13] * m[7] * m[10];

		inv[4] = -m[4] * m[10] * m[15] +
			m[4] * m[11] * m[14] +
			m[8] * m[6] * m[15] -
			m[8] * m[7] * m[14] -
			m[12] * m[6] * m[11] +
			m[12] * m[7] * m[10];

		inv[8] = m[4] * m[9] * m[15] -
			m[4] * m[11] * m[13] -
			m[8] * m[5] * m[15] +
			m[8] * m[7] * m[13] +
			m[12] * m[5] * m[11] -
			m[12] * m[7] * m[9];

		inv[12] = -m[4] * m[9] * m[14] +
			m[4] * m[10] * m[13] +
			m[8] * m[5] * m[14] -
			m[8] * m[6] * m[13] -
			m[12] * m[5] * m[10] +
			m[12] * m[6] * m[9];

		inv[1] = -m[1] * m[10] * m[15] +
			m[1] * m[11] * m[14] +
			m[9] * m[2] * m[15] -
			m[9] * m[3] * m[14] -
			m[13] * m[2] * m[11] +
			m[13] * m[3] * m[10];

		inv[5] = m[0] * m[10] * m[15] -
			m[0] * m[11] * m[14] -
			m[8] * m[2] * m[15] +
			m[8] * m[3] * m[14] +
			m[12] * m[2] * m[11] -
			m[12] * m[3] * m[10];

		inv[9] = -m[0] * m[9] * m[15] +
			m[0] * m[11] * m[13] +
			m[8] * m[1] * m[15] -
			m[8] * m[3] * m[13] -
			m[12] * m[1] * m[11] +
			m[12] * m[3] * m[9];

		inv[13] = m[0] * m[9] * m[14] -
			m[0] * m[10] * m[13] -
			m[8] * m[1] * m[14] +
			m[8] * m[2] * m[13] +
			m[12] * m[1] * m[10] -
			m[12] * m[2] * m[9];

		inv[2] = m[1] * m[6] * m[15] -
			m[1] * m[7] * m[14] -
			m[5] * m[2] * m[15] +
			m[5] * m[3] * m[14] +
			m[13] * m[2] * m[7] -
			m[13] * m[3] * m[6];

		inv[6] = -m[0] * m[6] * m[15] +
			m[0] * m[7] * m[14] +
			m[4] * m[2] * m[15] -
			m[4] * m[3] * m[14] -
			m[12] * m[2] * m[7] +
			m[12] * m[3] * m[6];

		inv[10] = m[0] * m[5] * m[15] -
			m[0] * m[7] * m[13] -
			m[4] * m[1] * m[15] +
			m[4] * m[3] * m[13] +
			m[12] * m[1] * m[7] -
			m[12] * m[3] * m[5];

		inv[14] = -m[0] * m[5] * m[14] +
			m[0] * m[6] * m[13] +
			m[4] * m[1] * m[14] -
			m[4] * m[2] * m[13] -
			m[12] * m[1] * m[6] +
			m[12] * m[2] * m[5];

		inv[3] = -m[1] * m[6] * m[11] +
			m[1] * m[7] * m[10] +
			m[5] * m[2] * m[11] -
			m[5] * m[3] * m[10] -
			m[9] * m[2] * m[7] +
			m[9] * m[3] * m[6];

		inv[7] = m[0] * m[6] * m[11] -
			m[0] * m[7] * m[10] -
			m[4] * m[2] * m[11] +
			m[4] * m[3] * m[10] +
			m[8] * m[2] * m[7] -
			m[8] * m[3] * m[6];

		inv[11] = -m[0] * m[5] * m[11] +
			m[0] * m[7] * m[9] +
			m[4] * m[1] * m[11] -
			m[4] * m[3] * m[9] -
			m[8] * m[1] * m[7] +
			m[8] * m[3] * m[5];

		inv[15] = m[0] * m[5] * m[10] -
			m[0] * m[6] * m[9] -
			m[4] * m[1] * m[10] +
			m[4] * m[2] * m[9] +
			m[8] * m[1] * m[6] -
			m[8] * m[2] * m[5];

		mat4 invOut;
		for (int i = 0; i < 16; i++)
			invOut.matrixData[i] = inv[i] / det;

		return invOut;
	}
	mat4 mat4::transpose() const
	{
		mat4 temp;
		for (int i = 0; i < 4; i++)
			for (int j = 0; j < 4; j++)
				temp.at(i, j) = this->at(j, i);
		return temp;
	}

}