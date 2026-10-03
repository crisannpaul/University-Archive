#include "stdafx.h"
#include "common.h"

bool is_inside(Mat img, int i, int j) {
	int rows = img.rows; int cols = img.cols;

	if (0 <= i && i < rows && 0 <= j && j < cols) return true;
	else return false;
}

Mat_<uchar> dilatare(Mat_<uchar> img, Mat_<uchar> matStruct) {
	Mat_<uchar> imgOut = img.clone();
	for (int i = 0; i < img.rows; i++) {
		for (int j = 0; j < img.cols; j++) {
			if (img(i, j) == 0) {
				for (int n = 0; n < matStruct.rows; n++) {
					for (int v = 0; v < matStruct.cols; v++) {
						if (matStruct(n, v) == 0) {
							int i2 = i + n - matStruct.rows / 2;
							int j2 = j + v - matStruct.cols / 2;
							if (is_inside(imgOut, i2, j2))
								imgOut(i2, j2) = 0;
						}
					}
				}
			}
		}
	}
	return imgOut;
}
Mat_<uchar> erodare(Mat_<uchar> img, Mat_<uchar> matStruct) {
	Mat_<uchar> imgOut = img.clone();
	for (int i = 0; i < img.rows; i++) {
		for (int j = 0; j < img.cols; j++) {
			if (img(i, j) == 0) {
				for (int n = 0; n < matStruct.rows; n++) {
					for (int v = 0; v < matStruct.cols; v++) {
						int i2 = i + n - matStruct.rows / 2;
						int j2 = j + v - matStruct.cols / 2;
						if (matStruct(n, v) == 0 && img(i2, j2) == 255) {
							imgOut(i, j) = 255;
							n = matStruct.rows;
							v = matStruct.cols;
						}
					}
				}
			}
		}
	}
	return imgOut;
}

int main()
{
	Mat_<uchar> B(3, 3); B.setTo(255);
	B(0, 1) = 0; B(1, 0) = 0; 
	B(2, 1) = 0; B(1, 2) = 0;
	B(1, 1) = 0;

	Mat_<uchar> A_dil = imread("Images/1_Dilate/gay.bmp", 0);
	Mat_<uchar> A_erod = imread("Images/2_Erode/mon1_gray.bmp", 0);

	imshow("Original Dilate", A_dil);
	imshow("Original Erode", A_erod);
	imshow("Dilate", dilatare(A_dil, B));
	imshow("Erode", erodare(A_erod, B));
	
	waitKey();
	return 0;
}