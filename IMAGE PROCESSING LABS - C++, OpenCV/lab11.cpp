#include "stdafx.h"
#include "common.h"

using namespace std;

Mat_<float> H_builder(char* str) {
	if (strcmp(str, "SobelX") == 0) {
		Mat_<float> H(3, 3);
		H(0, 0) = -1; H(0, 1) = 0; H(0, 2) = 1;
		H(1, 0) = -2; H(1, 1) = 0; H(1, 2) = 2;
		H(2, 0) = -1; H(2, 1) = 0; H(2, 2) = 1;
		return H;
	}
	if (strcmp(str, "SobelY") == 0) {
		Mat_<float> H(3, 3);
		H(0, 0) = 1; H(0, 1) = 2; H(0, 2) = 1;
		H(1, 0) = 0; H(1, 1) = 0; H(1, 2) = 0;
		H(2, 0) = -1; H(2, 1) = -2; H(2, 2) = -1;
		return H;
	}
	/*if (strcmp(str, "Low-Pass") == 0) {
		Mat_<float> H(3, 7);
		H(0, 0) = -1; H(0, 1) = -1; H(0, 2) = -1; H(0, 3) = 0; H(0, 4) = 1; H(0, 5) = 1; H(0, 6) = 1;
		H(1, 0) = -1; H(1, 1) = -1; H(1, 2) = -1; H(1, 3) = 0; H(1, 4) = 1; H(1, 5) = 1; H(1, 6) = 1;
		H(2, 0) = -1; H(2, 1) = -1; H(2, 2) = -1; H(2, 3) = 0; H(2, 4) = 1; H(2, 5) = 1; H(2, 6) = 1;
		return H;
	}*/
}

bool is_inside(Mat img, int i, int j) {
	int rows = img.rows; int cols = img.cols;

	if (0 <= i && i < rows && 0 <= j && j < cols) return true;
	else return false;
}

Mat_<float> convolution(Mat_<uchar> src, Mat_<float> H) {
	Mat_<float> conv(src.rows, src.cols);
	conv.setTo(0);

	for (int i = 0; i < src.rows; i++) {
		for (int j = 0; j < src.cols; j++) {

			float val = 0.0f;
			for (int u = 0; u < H.rows; u++) {
				for (int v = 0; v < H.cols; v++) {
					if (is_inside(src, i + u - H.rows / 2, j + v - H.cols / 2)) {
						val += H(u, v) * src(i + u - H.rows / 2, j + v - H.cols / 2);
					}
				}
			}
			conv(i, j) = val;
		}
	}

	return conv;
}

Mat_<float> get_module(Mat_<uchar> src) {
	Mat_<float> module(src.rows, src.cols);
	Mat_<float> dx = convolution(src, H_builder("SobelX"));
	Mat_<float> dy = convolution(src, H_builder("SobelY"));

	for (int i = 0; i < src.rows; i++) {
		for (int j = 0; j < src.cols; j++) {
			module(i, j) = sqrt(pow(dx(i, j), 2) + pow(dy(i, j), 2));
		}
	}

	//module = (module / (4 * sqrt(2)) / 255);
	return module;
}

Mat_<float> get_direction(Mat_<uchar> src) {
	Mat_<float> direction(src.rows, src.cols);
	Mat_<float> dx = convolution(src, H_builder("SobelX"));
	Mat_<float> dy = convolution(src, H_builder("SobelY"));

	for (int i = 0; i < src.rows; i++) {
		for (int j = 0; j < src.cols; j++) {
			direction(i, j) = atan2(dy(i, j), dx(i, j));
		}
	}
	return direction;
}

Mat_<float> get_angle(Mat_<uchar> src) {
	Mat_<int> Q(src.rows, src.cols);
	Mat_<float> dx = convolution(src, H_builder("SobelX"));
	Mat_<float> dy = convolution(src, H_builder("SobelY"));
	float ang;

	for (int i = 0; i < src.rows; i++) {
		for (int j = 0; j < src.cols; j++) {
			ang = atan2(dy(i, j), dx(i, j));

			if (ang < 0) {
				ang += 2.0f * PI;
			}

			Q(i, j) = (int)round(ang * 8.0f / (2 * PI)) % 8;
		}
	}
	return Q;
}


int di[8] = { 0,-1,-1,-1,0,1,1,1 };
int dj[8] = { 1,1,0,-1,-1,-1,0,1 };
Mat_<float> edge(Mat_<uchar> src) {
	Mat_<float> module = get_module(src);
	Mat_<float> edge_img = module.clone();
	Mat_<int> Q = get_angle(src);

	for (int i = 0; i < src.rows; i++) {
		for (int j = 0; j < src.cols; j++) {
			if (is_inside(module, i + di[Q(i,j)], j + dj[Q(i,j)]) && is_inside(module, i - di[Q(i, j)], j - dj[Q(i, j)])) {
				if (module(i, j) <= module(i + di[Q(i, j)], j + dj[Q(i, j)]) || module(i, j) <= module(i - di[Q(i, j)], j - dj[Q(i, j)])) {
					edge_img(i, j) = 0;
				}
			}
		}
	}
	return edge_img;
}

Mat_<uchar> result(Mat_<uchar> img) {
	Mat_<float> module = get_module(img);
	Mat_<uchar> result(img.rows, img.cols);

	for (int i = 0; i < img.rows; i++)
		for (int j = 0; j < img.cols; j++)
		{
			if (module(i, j) < 100)
				result(i, j) = 0;
			if (module(i, j) >= 100 && module(i, j) <= 500)
				result(i, j) = 128;
			if (module(i, j) > 500)
				result(i, j) = 255;
		}
	return result;
}


int main()
{	
	Mat_<uchar> src = imread("Images/cameraman.bmp", 0);

	Mat_<float> dx(src.rows, src.cols);
	dx = convolution(src, H_builder("SobelX"));

	Mat_<float> dy(src.rows, src.cols);
	dy = convolution(src, H_builder("SobelY"));

	Mat_<float> module(src.rows, src.cols);
	module = get_module(src);
	
	Mat_<float> edge_img(src.rows, src.cols);
	edge_img = edge(src);

	Mat_<uchar> res = result(src);

	imshow("Dx", abs(dx) / 255);
	imshow("Dy", abs(dy) / 255);
	imshow("Module", abs(module) / 255);
	imshow("Edge", abs(edge_img) / 255);
	imshow("Result", res);

	waitKey();
	return 0;
}