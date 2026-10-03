// OpenCVApplication.cpp : Defines the entry point for the console application.
//

#include "stdafx.h"
#include "common.h"

using namespace std;

vector<Mat_<uchar>> lab2_decompose(Mat_<Vec3b> img) {
	vector<Mat_<uchar>> vect;
	int rows = img.rows; int cols = img.cols;
	Mat_<uchar> R(rows, cols); Mat_<uchar> G(rows, cols); Mat_<uchar> B(rows, cols);

	for (int i = 0; i < rows; i++)
		for (int j = 0; j < cols; j++) {
			Vec3b current = img(i, j);
			B(i, j) = current[0];
			G(i, j) = current[1];
			R(i, j) = current[2];
		}

	vect.push_back(R);
	vect.push_back(G);
	vect.push_back(B);
	return vect;
}

Mat_<uchar> lab2_convertgray(Mat_<Vec3b> img) {
	int rows = img.rows; int cols = img.cols;
	Mat_<uchar> img2(rows, cols);

	for (int i = 0; i < rows; i++)
		for (int j = 0; j < cols; j++) {
			uchar B = img(i, j)[0];
			uchar G = img(i, j)[1];
			uchar R = img(i, j)[2];

			img2(i, j) = (B + G + R) / 3;
		}
	
	return img2;
}

Mat_<uchar> lab2_blackwhite(Mat_<Vec3b> img, uchar treshold) {
	int rows = img.rows; int cols = img.cols;
	Mat_<uchar> img2(rows, cols);

	img2 = lab2_convertgray(img);

	for (int i = 0; i < rows; i++)
		for (int j = 0; j < cols; j++) {
			
			if (img2(i, j) > treshold) img2(i, j) = 255;
			else img2(i, j) = 0;
		}

	return img2;
}

vector<Mat_<uchar>> lab2_getHSV(Mat_<Vec3b> img) {
	vector<Mat_<uchar>> decomposed = lab2_decompose(img);
	Mat_<uchar> R = decomposed[0]; Mat_<uchar> G = decomposed[1]; Mat_<uchar> B = decomposed[2];

	vector<Mat_<uchar>> hsv;
	int rows = img.rows; int cols = img.cols;
	Mat_<uchar> H_img(rows,cols); Mat_<uchar> S_img(rows,cols); Mat_<uchar> V_img(rows,cols);

	for (int i = 0; i < rows; i++)
		for (int j = 0; j < cols; j++) {
			float H, S, V;

			float r = (float)R(i,j) / 255.0f;
			float g = (float)G(i, j) / 255.0f;
			float b = (float)B(i, j) / 255.0f;

			float M = max(r, g, b);
			float m = min(r, g, b);

			float C = M - m;

			V = M;

			if (V != 0.0f) S = C / V;
			else S = 0.0f;

			if (C != 0.0f) {
				if (M == r) H = 60.0f * (g - b) / C;
				if (M == g) H = 120.0f + 60.0f * (b - r) / C;
				if (M == b) H = 240.0f + 60.0f * (r - g) / C;
			}
			else {
				H = 0.0f;
				if (H < 0.0f) H = H + 360.0f;
			}

			float H_norm = H * 255.0f / 360.0f; H_img(i,j) = (uchar)H_norm;
			float S_norm = S * 255.0f; S_img(i, j) = (uchar)S_norm;
			float V_norm = V * 255.0f; V_img(i, j) = (uchar)V_norm;

		}
	hsv.push_back(H_img);
	hsv.push_back(S_img);
	hsv.push_back(V_img);
	return hsv;
}

Mat_<Vec3b> lab2_toHSV(Mat_<Vec3b> img) {
	vector<Mat_<uchar>> decomposed = lab2_getHSV(img);
	Mat_<uchar> H = decomposed[0]; Mat_<uchar> S = decomposed[1]; Mat_<uchar> V = decomposed[2];

	int rows = img.rows; int cols = img.cols;
	Mat_<Vec3b> img2(rows,cols);

	for (int i = 0; i < rows; i++)
		for (int j = 0; j < cols; j++) {
			uchar h = H(i, j); uchar s = S(i, j); uchar v = V(i, j);
			img2(i, j) = Vec3b(h, s, v);
		}
	return img2;
}

Mat_<Vec3b> lab2_toRGB(Mat_<Vec3b> imgHSV) {
	int rows = imgHSV.rows; int cols = imgHSV.cols;
	Mat_<Vec3b> img2(rows, cols);
	
	cvtColor(imgHSV, img2, COLOR_HSV2BGR_FULL);

	return img2;
}

bool isInside(Mat img, int i, int j) {
	int rows = img.rows; int cols = img.cols;

	if (0 <= i && i < rows && 0 <= j && j < cols) return true;
	else return false;
}

int main() {
	Mat_<Vec3b> img = imread("Images/Lena_24bits.bmp");
	vector<Mat_<uchar>> decomposed = lab2_decompose(img);
	Mat_<uchar> converted = lab2_convertgray(img);
	Mat_<uchar> blackwhite = lab2_blackwhite(img, 128);
	vector<Mat_<uchar>> hsv = lab2_getHSV(img);
	Mat_<Vec3b> imgHSV = lab2_toHSV(img);
	Mat_<Vec3b> imgRGB = lab2_toRGB(imgHSV);

	imshow("Original", img);
	imshow("Red", decomposed[0]);
	imshow("Green", decomposed[1]);
	imshow("Blue", decomposed[2]);
	imshow("Converted", converted);
	imshow("Black n White", blackwhite);
	imshow("H", hsv[0]);
	imshow("S", hsv[1]);
	imshow("V", hsv[2]);
	imshow("HSV", imgHSV);
	imshow("From HSV to RGB", imgRGB);

	cout << isInside(img, 6, 6);

	waitKey();
	return 0;
}