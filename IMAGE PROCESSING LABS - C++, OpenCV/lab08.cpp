#include "stdafx.h"
#include "common.h"
#include <vector>

using namespace std;

vector<int> get_histogram(Mat_<uchar> img) {
	vector<int> hist(256);	

	for (int i = 0; i < img.rows; i++)
		for (int j = 0; j < img.cols; j++) {
			hist[img(i, j)]++;
		}

	return hist;
}

vector<float> get_pdf(Mat_<uchar> img) {
	vector<float> pdf(256);
	vector<int> hist = get_histogram(img);
	float M = img.rows * img.cols;

	for (int i = 0; i < hist.size(); i++) {
		pdf[i] = (float)hist[i] / M;
	}

	return pdf;
}

void display_histogram(Mat_<uchar> img1) {
	vector<int> hist = get_histogram(img1);

	Mat_<uchar> img(256, 300);
	for (int i = 0; i < img.rows; i++)
		for (int j = 0; j < img.cols; j++) {
			img(i, j) = 255;
		}

	vector<int> norm_hist(256);
	int maxim = 0;
	for (int i = 0; i < hist.size(); i++) {
		maxim = max(maxim, hist[i]);
	}

	for (int i = 0; i < hist.size(); i++) {
		norm_hist[i] = (hist[i] * img.cols) / maxim;
	}
	for (int i = 0; i < img.rows; i++)
		for (int j = 0; j < norm_hist[i]; j++) {
			img(i, j) = 0;
		}

	imshow("Histogram", img);
}

float get_mean(Mat_<uchar> img) {
	float mean = 0;
	float M = img.rows * img.cols;
	for (int i = 0; i < img.rows; i++) {
		for (int j = 0; j < img.cols; j++) {
			mean += img(i, j);
		}
	}

	mean = mean / M;
	return mean;
}

float get_stdev(Mat_<uchar> img) {
	float mean = get_mean(img);
	float M = img.rows * img.cols;

	float stdev = 0;
	for (int i = 0; i < img.rows; i++) {
		for (int j = 0; j < img.cols; j++) {
			stdev += (img(i, j) - mean) * (img(i, j) - mean);
		}
	}

	stdev = stdev / M;
	stdev = sqrt(stdev);
	return stdev;
}

float get_cumulative(Mat_<uchar> img, int min_gray) {
	vector<int> hist = get_histogram(img);

	float C = 0;
	for (int i = 0; i < min_gray; i++) {
		C += hist[i];
	}

	return C;
}

Mat_<uchar> binarize(Mat_<uchar> img) {
	Mat_<uchar> img2 = img.clone();
	vector<int> hist = get_histogram(img);

	int Imin = 999; int Imax = 0;
	for (int i = 0; i < hist.size(); i++) {
		if (hist[i] > Imax) Imax = i;
		if (hist[i] < Imin) Imin = i;
	}

	float T1 = (Imin + Imax) / 2;
	float T2 = 0;
	while(1){
		float sum = 0; float N1 = 0;
		for (int g = Imin; g <= T1; g++) {
			sum += g * hist[g];
			N1 += hist[g];
		}
		float mean1 = sum / N1;

		sum = 0; float N2 = 0;
		for (int g = T1 + 1; g <= Imax; g++) {
			sum += g * hist[g];
			N2 += hist[g];
		}
		float mean2 = sum / N2;

		T2 = (mean1 + mean2) / 2;

		if (abs(T1 - T2) < 0.1) break;
		T1 = T2;
	}

	for (int i = 0; i < img.rows; i++) {
		for (int j = 0; j < img.cols; j++) {
			if (img(i, j) <= T1) 
				img2(i, j) = 0;
			else 
				img2(i, j) = 255;
		}
	}

	return img2;
}

Mat_<uchar> negative(Mat_<uchar> img) {
	Mat_<uchar> img2 = img.clone();

	for (int i = 0; i < img.rows; i++) {
		for (int j = 0; j < img.cols; j++) {
			img2(i, j) = 255 - img(i, j);
		}
	}

	return img2;
}

Mat_<uchar> brightness(Mat_<uchar> img, int offset) {
	Mat_<uchar> img2 = img.clone();

	for (int i = 0; i < img.rows; i++) {
		for (int j = 0; j < img.cols; j++) {
			int new_val = img(i, j) + offset;

			if (new_val > 255) new_val = 255;
			if (new_val < 0) new_val = 0;

			img2(i, j) = new_val;
		}
	}

	return img2;
}

Mat_<uchar> contrast(Mat_<uchar> img) {
	Mat_<uchar> img2 = img.clone();
	vector<int> hist = get_histogram(img);
	int Gmax = 150, Gmin = 50;

	int Imin = 999; int Imax = 0;
	for (int i = 0; i < hist.size(); i++) {
		if (hist[i] > Imax) Imax = i;
		if (hist[i] < Imin) Imin = i;
	}

	for (int i = 0; i < img.rows; i++) {
		for (int j = 0; j < img.cols; j++) {
			int Gout = Gmin + (img(i, j) - Imin) * (Gmax - Gmin) / (Imax - Imin);
			img2(i, j) = Gout;
		}
	}

	return img2;
}

Mat_<uchar> gamma(Mat_<uchar> img, float gamma) {
	Mat_<uchar> img2 = img.clone();

	for (int i = 0; i < img.rows; i++) {
		for (int j = 0; j < img.cols; j++) {
			float gin = (float)img(i, j);
			int new_val = 255 * pow(gin / 255, gamma);

			if (new_val > 255) new_val = 255;
			if (new_val < 0) new_val = 0;

			img2(i, j) = new_val;
		}
	}

	return img2;
}

Mat_<uchar> equalize_hist(Mat_<uchar> img) {
	Mat_<uchar> img2 = img.clone();
	vector<int> hist = get_histogram(img);
	vector<float> pc(256);

	for (int k = 0; k < 256; k++) {
		int sum = 0;
		for (int g = 0; g <= k; g++) {
			sum += hist[g];
		}
		pc[k] = (float)sum / (img.rows * img.cols);
	}

	for (int i = 0; i < img.rows; i++) {
		for (int j = 0; j < img.cols; j++) {
			int gin = img(i, j);
			int gout = 255 * pc[gin];
			img2(i, j) = gout;
		}
	}

	return img2;
}


int main()
{
	Mat_<uchar> img = imread("Images/balloons.bmp", 0);
	Mat_<uchar> img2 = imread("Images/Hawkes_Bay_NZ.bmp", 0);


	imshow("Balloons", img);
	display_histogram(img);
	cout << "Mean: " << get_mean(img) << endl;
	cout << "Standard deviation: " << get_stdev(img) << endl;

	int min_gray = 128;
	cout << "Cumulative histogram for g = " << min_gray << ": " << get_cumulative(img, min_gray) << endl;

	imshow("Binarization", binarize(img));
	imshow("Negative", negative(img));
	imshow("Brightness", brightness(img, -50));
	imshow("Wheel", img2);
	imshow("Contrast", contrast(img2));
	imshow("Gamma", gamma(img, 0.1));
	imshow("Equalize Histogram", equalize_hist(img2));

	waitKey();
	return 0;
}