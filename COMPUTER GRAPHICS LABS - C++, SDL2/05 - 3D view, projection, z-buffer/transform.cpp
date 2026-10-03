#include "transform.h"
namespace egc {
	mat3 translate(const vec2 translateArray)
	{
		mat3 translationMatrix;
		translationMatrix.at(0, 2) = translateArray.x;
		translationMatrix.at(1, 2) = translateArray.y;
		return translationMatrix;
	}
	mat3 translate(float tx, float ty)
	{
		mat3 translationMatrix;
		translationMatrix.at(0, 2) = tx;
		translationMatrix.at(1, 2) = ty;
		return translationMatrix;
	}
	mat3 scale(const vec2 scaleArray)
	{
		mat3 scaleMatrix;
		scaleMatrix.at(0, 0) = scaleArray.x;
		scaleMatrix.at(1, 1) = scaleArray.y;
		return scaleMatrix;
	}
	mat3 scale(float sx, float sy)
	{
		mat3 scaleMatrix;
		scaleMatrix.at(0, 0) = sx;
		scaleMatrix.at(1, 1) = sy;
		return scaleMatrix;
	}
	mat3 rotate(float angle)
	{
		mat3 rotationMatrix;
		const float rad = angle * PI / 180;
		rotationMatrix.at(0, 0) = std::cos(angle * rad);
		rotationMatrix.at(0, 1) = std::sin(angle * rad) * -1;
		rotationMatrix.at(1, 0) = std::sin(angle * rad);
		rotationMatrix.at(1, 1) = std::cos(angle * rad);
		return rotationMatrix;
	}
	mat4 translate(const vec3 translateArray)
	{
		mat4 translationMatrix;
		translationMatrix.at(0, 3) = translateArray.x;
		translationMatrix.at(1, 3) = translateArray.y;
		translationMatrix.at(2, 3) = translateArray.z;
		return translationMatrix;
	}
	mat4 translate(float tx, float ty, float tz)
	{
		mat4 translationMatrix;
		translationMatrix.at(0, 3) = tx;
		translationMatrix.at(1, 3) = ty;
		translationMatrix.at(2, 3) = tz;
		return translationMatrix;
	}
	mat4 scale(const vec3 scaleArray)
	{
		mat4 scaleMatrix;
		scaleMatrix.at(0, 0) = scaleArray.x;
		scaleMatrix.at(1, 1) = scaleArray.y;
		scaleMatrix.at(2, 2) = scaleArray.z;
		return scaleMatrix;
	}
	mat4 scale(float sx, float sy, float sz)
	{
		mat4 scaleMatrix;
		scaleMatrix.at(0, 0) = sx;
		scaleMatrix.at(1, 1) = sy;
		scaleMatrix.at(2, 2) = sz;
		return scaleMatrix;
	}
	mat4 rotateX(float angle)
	{
		mat4 rotationMatrix;
		float rad = PI / 180;
		rotationMatrix.at(1, 1) = std::cos(angle * rad);
		rotationMatrix.at(1, 2) = std::sin(angle * rad) * -1;
		rotationMatrix.at(2, 1) = std::sin(angle * rad);
		rotationMatrix.at(2, 2) = std::cos(angle * rad);
		return rotationMatrix;
	}
	mat4 rotateY(float angle)
	{
		mat4 rotationMatrix;
		float rad = PI / 180;
		rotationMatrix.at(0, 0) = std::cos(angle * rad);
		rotationMatrix.at(0, 2) = std::sin(angle * rad);
		rotationMatrix.at(2, 0) = std::sin(angle * rad) * -1;
		rotationMatrix.at(2, 2) = std::cos(angle * rad);
		return rotationMatrix;
	}
	mat4 rotateZ(float angle)
	{
		mat4 rotationMatrix;
		float rad = PI / 180;
		rotationMatrix.at(0, 0) = std::cos(angle * rad);
		rotationMatrix.at(0, 1) = std::sin(angle * rad) * -1;
		rotationMatrix.at(1, 0) = std::sin(angle * rad);
		rotationMatrix.at(1, 1) = std::cos(angle * rad);
		return rotationMatrix;
	}
}