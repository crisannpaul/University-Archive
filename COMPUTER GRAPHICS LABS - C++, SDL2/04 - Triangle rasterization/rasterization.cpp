#include "rasterization.h"

namespace egc {

	void computeAlphaBetaGamma(const std::vector<egc::vec4>& triangleVertices, vec2 pixel, float& alpha, float& beta, float& gamma) 
	{
		//TO DO - Compute alfa, beta and gamma => we use the function's input parameters as the return mechanism
		//Store the final results in the input parameters

		float xa = triangleVertices.at(0).x;
		float ya = triangleVertices.at(0).y;
		float xb = triangleVertices.at(1).x;
		float yb = triangleVertices.at(1).y;
		float xc = triangleVertices.at(2).x;
		float yc = triangleVertices.at(2).y;

		float x = pixel.x;
		float y = pixel.y;

		float Fbcx = (yb - yc) * x + (xc - xb) * y + xb * xc - xc * yb;
		float Fbcp = (yb - yc) * xa + (xc - xb) * ya + xb * xc - xc * yb;
		float Facx = (ya - yc) * x + (xc - xa) * y + xa * xc - xa * yc;
		float Facp = (ya - yc) * xb + (xc - xa) * yb + xa * xc - xa * yc;

		alpha = Fbcx / Fbcp;
		beta = Facx / Facp;
		gamma = 1 - alpha - beta;

	}

	std::vector<egc::vec2> findBoundingBox(const std::vector<egc::vec4> triangleVertices) {
		std::vector<egc::vec2> boundingBox;
		float xmin = FLT_MAX;
		float ymin = FLT_MAX;
		float ymax = FLT_MIN;
		float xmax = FLT_MIN;
		for(int i = 0; i < triangleVertices.size(); i++) {
			if (triangleVertices.at(i).x > xmax) xmax = triangleVertices.at(i).x;
			if (triangleVertices.at(i).x < xmin) xmin = triangleVertices.at(i).x;
			if (triangleVertices.at(i).y > ymax) ymax = triangleVertices.at(i).y;
			if (triangleVertices.at(i).y < ymin) ymin = triangleVertices.at(i).y;
		}
		vec2 min;
		min.x = xmin;
		min.y = ymin;
		vec2 max;
		max.x = xmax;
		max.y = ymax;
		boundingBox.push_back(min);
		boundingBox.push_back(max);

		return boundingBox;
	}

	void rasterizeTriangle(SDL_Renderer* renderer, const std::vector<egc::vec4>& triangleVertices, const std::vector<egc::vec4>& triangleColors) {
		//TO DO - Implement the triangle rasterization algorithm

		std::vector<egc::vec2> boundingBox = findBoundingBox(triangleVertices);
		for (int i = 0; i < boundingBox.size(); i++) {
			float alpha, beta, gamma;
			computeAlphaBetaGamma(triangleVertices, boundingBox.at(i), alpha, beta, gamma);

			if (0 < alpha && alpha < 1 && 0 < beta && beta < 1 && 0 < gamma && gamma < 1) {
				vec4 color;
				color = triangleColors.at(0) * alpha + triangleColors.at(1) * beta + triangleColors.at(2) * gamma;
				SDL_RenderDrawPoint(renderer, boundingBox.at(i).x, boundingBox.at(i).y);
			}
		}
	}
}