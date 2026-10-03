// OpenCVApplication.cpp : Defines the entry point for the co
// nsole application.
//

#include "stdafx.h"
#include "common.h"

using namespace std;

Mat_<float> H_builder(char* str) {
	if (strcmp(str, "Mean") == 0) {
		Mat_<float> H(3, 3);
		H(0, 0) = 1; H(0, 1) = 1; H(0, 2) = 1;
		H(1, 0) = 1; H(1, 1) = 1; H(1, 2) = 1;
		H(2, 0) = 1; H(2, 1) = 1; H(2, 2) = 1;
		return H;
	} 
	if (strcmp(str, "Gaussian") == 0) {
		Mat_<float> H(3, 3);
		H(0, 0) = 1; H(0, 1) = 2; H(0, 2) = 1;
		H(1, 0) = 2; H(1, 1) = 4; H(1, 2) = 2;
		H(2, 0) = 1; H(2, 1) = 2; H(2, 2) = 1;
		return H;
	}
	if (strcmp(str, "Low-Pass") == 0) {
		Mat_<float> H(3, 7);
		H(0, 0) = -1; H(0, 1) = -1; H(0, 2) = -1; H(0, 3) = 0; H(0, 4) = 1; H(0, 5) = 1; H(0, 6) = 1;
		H(1, 0) = -1; H(1, 1) = -1; H(1, 2) = -1; H(1, 3) = 0; H(1, 4) = 1; H(1, 5) = 1; H(1, 6) = 1;
		H(2, 0) = -1; H(2, 1) = -1; H(2, 2) = -1; H(2, 3) = 0; H(2, 4) = 1; H(2, 5) = 1; H(2, 6) = 1;
		return H;
	}
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
					if(is_inside(src, i + u - H.rows / 2, j + v - H.cols / 2)) {
						val += H(u, v) * src(i + u - H.rows / 2, j + v - H.cols / 2);
					}
				}
			}
			conv(i, j) = val;
		}
	}

	return conv;
}

Mat_<uchar> normalize(Mat_<float> conv, Mat_<float> H) {
	Mat_<uchar> img(conv.rows, conv.cols);
	img.setTo(0);
	float sum_pos = 0.0f; 
	float sum_neg = 0.0f;

	for (int u = 0; u < H.rows; u++) {
		for (int v = 0; v < H.cols; v++) {
			if (H(u, v) > 0.0f) sum_pos += H(u, v);
			if (H(u, v) < 0.0f) sum_neg += H(u, v);
		}
	}

	float xmax = 255 * sum_pos;
	float xmin = 255 * sum_neg;

	for (int i = 0; i < conv.rows; i++) {
		for (int j = 0; j < conv.cols; j++) {
			img(i, j) = ((conv(i, j) - xmin) / (xmax - xmin)) * 255;
		}
	}

	return img;
}

void centering_transform(Mat_<uchar> img) {
	for (int i = 0; i < img.rows; i++) {
		for (int j = 0; j < img.cols; j++) {
			img(i, j) = ((i + j) & 1) ? -img(i, j) : img(i, j);
		}
	}
}

Mat generic_frequency_domain_filter(Mat_<uchar> src, string transform, int R) {
	Mat srcf;
	src.convertTo(srcf, CV_32FC1);

	centering_transform(srcf);

	Mat fourier;
	dft(srcf, fourier, DFT_COMPLEX_OUTPUT);

	Mat channels[] = { Mat::zeros(src.size(), CV_32F), Mat::zeros(src.size(), CV_32F) };
	split(fourier, channels); // channels[0] = Re(DFT(I)), channels[1] = Im(DFT(I))

	Mat mag, phi;
	magnitude(channels[0], channels[1], mag);
	phase(channels[0], channels[1], phi);

	int rows = mag.rows, cols = mag.cols;
	float maxVal1 = 0, maxVal2 = 0;
	Mat_<float> norm_mag(rows, cols);
	Mat_<float> norm_phi(rows, cols);
	for (int i = 0; i < rows; i++) {
		for (int j = 0; j < cols; j++) {
			norm_mag(i, j) = log(mag.at<float>(i, j) + 1.0);
			norm_phi(i, j) = log(phi.at<float>(i, j) + 1.0);

			if (norm_mag(i, j) > maxVal1) {
				maxVal1 = norm_mag(i, j);
			}

			if (norm_phi(i, j) > maxVal2) {
				maxVal2 = norm_phi(i, j);
			}
		}
	}
	imshow("Magnitude", norm_mag / maxVal1);
	imshow("Phase", norm_phi / maxVal2);

	//aici inserați operații de filtrare aplicate pe coeficienții Fourier
	int height = src.rows, width = src.cols;
	if (transform == "Low-Pass") {
		for (int i = 0; i < height; i++) {
			for (int j = 0; j < width; j++) {
				float sum = pow((height / 2 - i), 2) + pow((width / 2 - j), 2);
				float R2 = pow(R, 2);

				if (sum > R2) {
					channels[0].at<float>(i, j) = 0;
					channels[1].at<float>(i, j) = 0;
				}
			}
		}
	}
	if (transform == "High-Pass") {
		for (int i = 0; i < height; i++) {
			for (int j = 0; j < width; j++) {
				float sum = pow((height / 2 - i), 2) + pow((width / 2 - j), 2);
				float R2 = pow(R, 2);

				if (sum <= R2) {
					channels[0].at<float>(i, j) = 0;
					channels[1].at<float>(i, j) = 0;
				}
			}
		}
	}
	if (transform == "Gaussian Low-Pass") {
		for (int i = 0; i < height; i++) {
			for (int j = 0; j < width; j++) {
				float exponent = pow((height / 2 - i), 2) + pow((width / 2 - j), 2);
				exponent /= pow(R, 2);
				exponent = -exponent;

				channels[0].at<float>(i, j) *= exp(exponent);
				channels[1].at<float>(i, j) *= exp(exponent);
			}
		}
	}
	if (transform == "Gaussian High-Pass") {
		for (int i = 0; i < height; i++) {
			for (int j = 0; j < width; j++) {
				float exponent = pow((height / 2 - i), 2) + pow((width / 2 - j), 2);
				exponent /= pow(R, 2);
				exponent = -exponent;

				channels[0].at<float>(i, j) *= (1 - exp(exponent));
				channels[1].at<float>(i, j) *= (1 - exp(exponent));
			}
		}
	}

	Mat dst, dstf;
	merge(channels, 2, fourier);
	dft(fourier, dstf, DFT_INVERSE | DFT_REAL_OUTPUT | DFT_SCALE);
	centering_transform(dstf);
	normalize(dstf, dst, 0, 255, NORM_MINMAX, CV_8UC1);
	//dstf.convertTo(dst, CV_8UC1);
	return dst;
}



int main()
{
	Mat_<uchar> img = imread("Images/cameraman.bmp", IMREAD_GRAYSCALE);

	// PART I
	/*Mat_<float> H = H_builder("Mean");

	imshow("Original", img);	
	imshow("Mean", normalize(convolution(img, H), H));

	H = H_builder("Gaussian");
	imshow("Gaussian", normalize(convolution(img, H), H));

	H = H_builder("Low-Pass");
	imshow("Low-Pass", normalize(convolution(img, H), H));*/

	// PART II
	//Mat img2 = generic_frequency_domain_filter(img, "Low-Pass", 20);
	imshow("Nimic", generic_frequency_domain_filter(img, "Nimic", 20));
	imshow("Low Pass", generic_frequency_domain_filter(img, "Low-Pass", 20));
	imshow("High Pass", generic_frequency_domain_filter(img, "High-Pass", 20));
	imshow("Gaussian Low Pass", generic_frequency_domain_filter(img, "Gaussian Low-Pass", 20));
	imshow("Gaussian High Pass", generic_frequency_domain_filter(img, "Gaussian High-Pass", 20));


	waitKey();
	return 0;
}