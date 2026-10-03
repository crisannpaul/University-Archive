#include "zbuffer.h"

namespace egc {

	float fAB(float x, float y, const std::vector<egc::vec4>& triangleVertices)
	{
		return (triangleVertices.at(2).y - triangleVertices.at(1).y) * x + (triangleVertices.at(1).x - triangleVertices.at(2).x) * y + triangleVertices.at(2).x * triangleVertices.at(1).y - triangleVertices.at(1).x * triangleVertices.at(2).y;
	}

	float fBC(float x, float y, const std::vector<egc::vec4>& triangleVertices)
	{
		return (triangleVertices.at(1).y - triangleVertices.at(0).y) * x + (triangleVertices.at(0).x - triangleVertices.at(1).x) * y + triangleVertices.at(1).x * triangleVertices.at(0).y - triangleVertices.at(0).x * triangleVertices.at(1).y;
	}

	float fCA(float x, float y, const std::vector<egc::vec4>& triangleVertices)
	{
		return (triangleVertices.at(0).y - triangleVertices.at(2).y) * x + (triangleVertices.at(2).x - triangleVertices.at(0).x) * y + triangleVertices.at(0).x * triangleVertices.at(2).y - triangleVertices.at(2).x * triangleVertices.at(0).y;
	}

	void computeAlphaBetaGamma(const std::vector<egc::vec4>& triangleVertices, vec2 pixel, float& alpha, float& beta, float& gamma)
	{
		//TO DO - Compute alfa, beta and gamma => we use the function's input parameters as the return mechanism
		//Store the final results in the input parameters

		alpha = fBC(pixel.x, pixel.y, triangleVertices) / fBC(triangleVertices.at(2).x, triangleVertices.at(2).y, triangleVertices);
		beta = fCA(pixel.x, pixel.y, triangleVertices) / fCA(triangleVertices.at(1).x, triangleVertices.at(1).y, triangleVertices);
		gamma = 1 - alpha - beta;
	}

	void drawTriangleInZBuffer(std::vector<egc::vec4> triangle, float depthBuffer[WINDOW_HEIGHT][WINDOW_WIDTH], float& zmin, float& zmax) {

		//TO DO  -  implement the "drawing" of the triangle inside the depth buffer
		//The buffer has the same dimension as the screen - use it to fill in not the pixel color of each pixel in the triangel - but the pixel depth (Z component)
		//So you are going to fill in the Z of each pixel inside the triangle - use the algorithm from last week to access the inside of the triangle

		//While you compute the z for each pixel, you can also determine the zmin and zmax values ===> from all the points of the rabbit 
		//zmin and zmax are the minimum and maximum Z values FROM ALL THE VERICES OF THE RABBIT
		int xmin = triangle.at(0).x;
		int ymin = triangle.at(0).y;
		int xmax = triangle.at(0).x;
		int ymax = triangle.at(0).y;
		zmin = triangle.at(0).z;
		zmax = triangle.at(0).z;
		float alpha, beta, gamma;

		for (vec4 vertices : triangle) {
			if (xmax < vertices.x) {
				xmax = vertices.x;
			}
			else if (xmin > vertices.x) {
				xmin = vertices.x;
			}

			if (ymax < vertices.y) {
				ymax = vertices.y;
			}
			else if (ymin > vertices.y) {
				ymin = vertices.y;
			}

			if (zmin > vertices.z) {
				zmin = vertices.z;
			}
			else if (zmax < vertices.z) {
				zmax = vertices.z;
			}
		}

		for (int x = xmin; x <= xmax; x++) {
			for (int y = ymin; y <= ymax; y++) {
				vec2 pixel = vec2(x, y);
				computeAlphaBetaGamma(triangle, pixel, alpha, beta, gamma);
				if (alpha > 0 && alpha < 1 && beta > 0 && beta < 1 && gamma > 0 && gamma < 1) {
					float z = alpha * triangle.at(0).z;
					depthBuffer[x][y] = zmin;
				}
			}
		}


	}
}
