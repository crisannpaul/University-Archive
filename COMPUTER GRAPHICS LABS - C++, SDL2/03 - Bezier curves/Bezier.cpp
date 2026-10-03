#include "Bezier.h"
#include "math.h"
#include <vector>

//Return the value of P(t), where t is in [0,1]
vec2 getParametricPoint(float t, vec2 p0, vec2 p1) {
	//P(t) = (1 - t)*P0 + t*P1
	vec2 point;

	point = p0 * (1 - t) + p1 * t;
	return point;
}

//Paint the pixels that are on the line P0P1
void drawParametricLinePoints(vec2 p0, vec2 p1, SDL_Renderer* renderer) {
	//Hint: To paint a single pixel, you can use the function: SDL_RenderDrawPoint(renderer, x, y)
	for (float t = 0; t <= 1; t += 0.001f)
	{
		vec2 tmp = getParametricPoint(t, p0, p1);
		SDL_RenderDrawPoint(renderer, (int)tmp.x, (int)tmp.y);
	}
}

//Return the value of B(t), where t is in [0,1]. The value of B(t) is computed by taking into account all the 
//controll points contained within the input vecto
vec2 getBezierPoint(std::vector<vec2> controlPoints, float t) {
	vec2 point;

	if (controlPoints.size() == 2)
	{
		point = controlPoints.at(0) * (1 - t) + controlPoints.at(1) * t;
		return point;
	}
	std::vector<vec2> BN, BN1;

	for (int i = 0; i < controlPoints.size() - 1; i++)
		BN.push_back(controlPoints.at(i));

	for (int i = 1; i < controlPoints.size(); i++)
		BN1.push_back(controlPoints.at(i));

	point = getBezierPoint(BN, t) * (1 - t) + getBezierPoint(BN1, t)*t;

	return point;
}

//Paint the pixels that are on the Bezier curve defined by the given control points
void drawBezierPoints(std::vector<vec2> controlPoints, SDL_Renderer* renderer) {
	for (float t = 0; t <= 1; t += 0.001f) {
		vec2 tmp = getBezierPoint(controlPoints, t);
		SDL_RenderDrawPoint(renderer, (int)tmp.x, (int)tmp.y);
	}
}
