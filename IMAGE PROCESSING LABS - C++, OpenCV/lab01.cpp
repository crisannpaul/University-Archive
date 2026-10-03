// OpenCVApplication.cpp : Defines the entry point for the console application.
//

#include "stdafx.h"
#include <cmath>
#include "common.h"

using namespace std;

void lab1_createimg() {
	Mat img(200, 300, CV_8UC1);
	img.setTo(150);
	imshow("Window", img);
	waitKey();
}

void lab1_openimg() {
	char fname[100];
	while (openFileDlg(fname)) {
		Mat img = imread(fname, IMREAD_GRAYSCALE);
		imshow("Window", img);
		waitKey();
	}
}

void lab1_negative() {
	Mat_<uchar> img = imread("Images/cameraman.bmp", 0);
	for(int i = 0; i < img.rows; i++)
		for (int j = 0; j < img.cols; j++) {
			img(i, j) = 255 - img(i, j);
		}
	imshow("Negativ", img);
	waitKey();
}


void lab1_aditive(int add) {
	Mat_<uchar> img = imread("Images/cameraman.bmp", 0);
	for (int i = 0; i < img.rows; i++)
		for (int j = 0; j < img.cols; j++) {
			int new_color = img(i, j) + add;
			if (new_color > 255)
				new_color = 255;
			if (new_color < 0)
				new_color = 0;
			img(i, j) = (uchar)new_color;
		}
	imshow("Add", img);
	waitKey();
}

void lab1_multiplicative(float mul) {
	Mat_<uchar> img = imread("Images/cameraman.bmp", 0);
	for (int i = 0; i < img.rows; i++)
		for (int j = 0; j < img.cols; j++) {
			int new_color = (int)((float)img(i, j) * mul) % 255;
			img(i, j) = (uchar)new_color;
		}
	imshow("Mul", img);
	waitKey();
}

void lab1_4colors() {
	Vec3b WHITE = Vec3b(255, 255, 255);
	Vec3b RED = Vec3b(0, 0, 255);
	Vec3b GREEN = Vec3b(0, 255, 0);
	Vec3b YELLOW = Vec3b(0, 255, 255);


	Mat_<Vec3b> img(256, 256);
	for (int i = 0; i < img.rows; i++)
		for (int j = 0; j < img.cols; j++) {
			if (i <= 128 && j <= 128) {
				img(i, j) = WHITE;
			}
			if (i <= 128 && j >= 128) {
				img(i, j) = RED;
			}
			if (i >= 128 && j <= 128) {
				img(i, j) = GREEN;
			}
			if (i >= 128 && j >= 128) {
				img(i, j) = YELLOW;
			}
		}
	imshow("4 Colors", img);
	waitKey();
}

void lab1_inv() {
	float vals[9] = { -1, 2, 3, 4, 5, 6, -7, 8, 9 };
	Mat_<float> M(3, 3, vals);
	
	cout << M << endl;

	Mat_<float> M_Inv = M.inv();

	cout << M_Inv << endl;
}

void lab1_transform() {
	Mat_<uchar> img1 = imread("Images/Lena.png", 0);
	Mat_<uchar> img2 = imread("Images/Bird.png", 0);

	while (true) {
		for (int i = 0; i < img1.rows; i++)
			for (int j = 0; j < img1.cols; j++) {
				if (img1(i, j) < img2(i, j)) {
					img1(i, j) = img1(i, j) + 1;
				}
				if (img1(i, j) > img2(i, j)) {
					img1(i, j) = img1(i, j) - 1;
				}
			}
		imshow("Transform", img1);
		waitKey();
	}
}

int main() {
	//lab1_4colors();
	//lab1_aditive(-300);
	//lab1_multiplicative(1.2);
	//lab1_negative();
	//lab1_inv();
	lab1_transform();
	
	return 0;
}