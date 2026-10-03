// OpenCVApplication.cpp : Defines the entry point for the console application.
//

#include "stdafx.h"
#include "common.h"
#include <fstream>

using namespace std;

bool is_inside(Mat img, int i, int j) {
	int rows = img.rows; int cols = img.cols;

	if (0 <= i && i < rows && 0 <= j && j < cols) return true;
	else return false;
}

String outline_string(vector<pair<int, int>> outline) {
	String result;
	for (int i = 0; i < outline.size(); i++) {
		result.append(to_string(outline[i].first));
		result.append(",");
		result.append(to_string(outline[i].second));
		result.append(" ");
	}
	return result;
}

void outline(Mat_<uchar> img) {
	vector<pair<int, int>> outline;
	vector<int> directions;
	vector<int> derivative;

	for (int i = 0; i < img.rows; i++)
		for (int j = 0; j < img.cols; j++) {
			if (img(i, j) == 0) {
				outline.push_back(pair<int, int>(i, j));
				i = img.rows;
				j = img.cols;
			}
		}
	
	int di[8] = { 0,-1,-1,-1,0,1,1,1 };
	int dj[8] = { 1,1,0,-1,-1,-1,0,1 };
	int dir = 7;

	while (true) {
		if (dir % 2 == 0) dir = (dir + 7) % 8;
		if (dir % 2 != 0) dir = (dir + 6) % 8;

		for (int k = 0; k < 8; k++) {
			int d = (dir + k) % 8;

			int i2 = outline.back().first + di[d];
			int j2 = outline.back().second + dj[d];

			if (is_inside(img, i2, j2) && img(i2, j2) == 0) {
				outline.push_back(pair<int, int>(i2, j2));
				directions.push_back(d);
				dir = d;
				break;
			}
		}

		if (outline.size() > 2 && outline[0] == outline[outline.size() - 2] && outline[1] == outline[outline.size() - 1])
			break;
	}

	for (int i = 0; i < (directions.size() - 1); i++) {
		derivative.push_back((directions[i + 1] - directions[i] + 8) % 8);
	}

	Mat_<uchar> img2(img.rows, img.cols);
	img2.setTo(255);
	for (int i = 0; i < outline.size(); i++) {
		img2(outline[i].first, outline[i].second) = 0;
	}

	std::stringstream result;
	std::copy(directions.begin(), directions.end(), std::ostream_iterator<int>(result, " "));
	cout << result.str() << endl;

	std::copy(derivative.begin(), derivative.end(), std::ostream_iterator<int>(result, " "));
	cout << result.str() << endl;

	cout << outline_string(outline);
	imshow("Original", img);
	imshow("Outline", img2);
}

void reconstruct(Mat_<uchar> img) {
	std::ifstream f("Images/reconstruct.txt");

	int di[8] = { 0, -1, -1, -1,  0,  1, 1, 1 };
	int dj[8] = { 1,  1,  0, -1, -1, -1, 0, 1 };

	int i, j, size;
	f >> i >> j >> size;

	for (int k = 0; k < size; k++) {
		int dir;
		f >> dir;

		img(i, j) = 0;
		i += di[dir];
		j += dj[dir];
	}

	f.close();
	imshow("Reconstructed image", img);
}

int main() {

	Mat_<uchar> img = imread("Images/triangle_up.bmp", 0);
	Mat_<uchar> img2 = imread("Images/gray_background.bmp", 0);

	outline(img);
	reconstruct(img2);

	waitKey();
	return 0;
}