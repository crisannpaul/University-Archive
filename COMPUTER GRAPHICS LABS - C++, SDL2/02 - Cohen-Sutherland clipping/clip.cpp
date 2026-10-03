#include "clip.h"

namespace egc {

	std::vector<int> computeCSCode(std::vector<vec3> clipWindow, const vec3 p) {
		std::vector<int> code = { 0,0,0,0 };
		int xMin = INT_MAX;
		int xMax = INT_MIN;
		int yMin = INT_MAX;
		int yMax = INT_MIN;
		//TO DO - compute the code for the point given as argument
		for (int i = 0; i < 4; i++) {
			if (xMin > clipWindow[i].x) {
				xMin = clipWindow[i].x;
			}
			if (xMax < clipWindow[i].x) {
				xMax = clipWindow[i].x;
			}
			if (yMin > clipWindow[i].y) {
				yMin = clipWindow[i].y;
			}
			if (yMax < clipWindow[i].y) {
				yMax = clipWindow[i].y;
			}
		}

		if (p.x < xMin) {
			code[3] = 1;
		}
		else if (p.x > xMax) {
			code[2] = 1;
		}
		if (p.y < yMin) {
			code[0] = 1;
		}
		else if (p.y > yMax) {
			code[1] = 1;
		}


		return code;
	}


	std::vector<int> getCoords(std::vector<vec3> clipWindow) {
		std::vector<int> code = { 0,0,0,0 };
		int xMin = INT_MAX;
		int xMax = INT_MIN;
		int yMin = INT_MAX;
		int yMax = INT_MIN;
		//TO DO - compute the code for the point given as argument
		for (int i = 0; i < 4; i++) {
			if (xMin > clipWindow[i].x) {
				xMin = clipWindow[i].x;
			}
			if (xMax < clipWindow[i].x) {
				xMax = clipWindow[i].x;
			}
			if (yMin > clipWindow[i].y) {
				yMin = clipWindow[i].y;
			}
			if (yMax < clipWindow[i].y) {
				yMax = clipWindow[i].y;
			}
		}
		code[0] = xMin;
		code[1] = xMax;
		code[2] = yMin;
		code[3] = yMax;
		return code;

	}
	bool simpleRejection(std::vector<int> cod1, std::vector<int> cod2) {
		//TO DO - write the code to determine if the two input codes represent 
		//points in the SIMPLE REJECTION case
		for (int i = 0; i < 4; i++) {
			if (cod1[i] == cod2[i] && cod1[i] == 1) {
				return true;
			}
		}

		return false;
	}

	bool simpleAcceptance(std::vector<int> cod1, std::vector<int> cod2) {
		//TO DO - write the code to determine if the two input codes represent 
		//points in the SIMPLE ACCEPTANCE case
		for (int i = 0; i < 4; i++) {
			if (cod1[i] != 0 || cod2[i] != 0) {
				return false;
			}
		}
		return true;
	}
	bool displayArea(std::vector<int> cod) {
		for (int i = 0; i < 4; i++) {
			std::cout << cod[i] << " ";
			if (cod[i] != 0) {
				return false;
			}
		}
		return true;
	}

	//function returns -1 if the line segment cannot be clipped
	int lineClip_CohenSutherland(std::vector<vec3> clipWindow, vec3& p1, vec3& p2) {
		//TO DO - implement the Cohen-Sutherland line clipping algorithm - consult the laboratory work
		std::vector<int>coords = getCoords(clipWindow);
		std::cout << "A intrat in functi\n";
		bool finished = false;
		while (finished != true) {
			std::vector<int>cod1 = computeCSCode(clipWindow, p1);
			std::vector<int>cod2 = computeCSCode(clipWindow, p2);
			bool respins = simpleRejection(cod1, cod2);
			if (respins) {

				finished = true;
				return -1;
			}
			else {
				std::cout << "display\n";
				bool display = simpleAcceptance(cod1, cod2);
				if (display) {
					finished = true;
					return 0;
				}
				else {
					if (displayArea(cod1)) {
						cod1.swap(cod2);
						vec3 aux = p1;
						p1 = p2;
						p2 = aux;
					}
					if (cod1[0] == 1 && p2.y != p1.y) {
						p1.x = p1.x + (p2.x - p1.x) * (coords[2] - p1.y) / (p2.y - p1.y);
						p1.y = coords[2];
					}
					else if (cod1[1] == 1 && p2.y != p1.y) {
						p1.x = p1.x + (p2.x - p1.x) * (coords[3] - p1.y) / (p2.y - p1.y);
						p1.y = coords[3];
					}
					else if (cod1[2] == 1 && p2.x != p1.x) {
						p1.y = p1.y + (p2.y - p1.y) * (coords[1] - p1.x) / (p2.x - p1.x);
						p1.x = coords[1];
					}
					else if (cod1[3] == 1 && p2.x != p1.x) {
						p1.y = p1.y + (p2.y - p1.y) * (coords[0] - p1.x) / (p2.x - p1.x);
						p1.x = coords[0];
					}
				}

			}
		}
	}
}