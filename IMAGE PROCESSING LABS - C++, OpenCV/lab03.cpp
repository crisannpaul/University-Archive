// OpenCVApplication.cpp : Defines the entry point for the console application.
//

#include "stdafx.h"
#include "common.h"

using namespace std;

String to_string(vector<int> vec) {
	std::stringstream ss;

	for (size_t i = 0; i < vec.size(); i++) {
		if (i != 0) {
			ss << ", ";
		}
		ss << vec[i];
	}
	return ss.str();
}

String to_string(vector<float> vec) {
	std::stringstream ss;

	for (size_t i = 0; i < vec.size(); i++) {
		if (i != 0) {
			ss << ", ";
		}
		ss << vec[i];
	}
	return ss.str();
}

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

void display_histogram(vector<int> hist) {

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

Mat_<uchar> multilevel_treshold(Mat_<uchar> img) {
	vector<float> pdf = get_pdf(img);

	int WH = 5;
	int window = 2 * WH + 1;
	float TH = 0.0003;

	vector<int> local_maxima;
	local_maxima.push_back(0);
	for (int i = WH; i < 256 - WH; i++) {
		float avg = 0;
		float maxim = 0;
		for (int j = i - WH; j <= i + WH; j++) {
			maxim = max(maxim, pdf[j]);
			avg += pdf[j];
		}
		avg /= window;
		if (pdf[i] > avg + TH && pdf[i] >= maxim) {
			local_maxima.push_back(i);
		}
	}
	local_maxima.push_back(255);
	cout << to_string(local_maxima);

	for (int i = 0; i < img.rows; i++) 
		for (int j = 0; j < img.cols; j++) {
			uchar color = img(i, j);
			int min_dst = 999;
			int coresp = 0;
			for (int k = 0; k < local_maxima.size(); k++) {
				if (abs(color - local_maxima[k]) < min_dst) {
					coresp = local_maxima[k];
					min_dst = abs(color - local_maxima[k]);
				}
			}
			img(i, j) = coresp;
		}

	return img;
}

int getMaxim(uchar val, vector<int> maxime) {
	int dist = 99999;
	int res = 0;
	for (int i = 0; i < maxime.size(); i++)
	{
		if (dist > abs(val - maxime[i]))
		{
			dist = abs(val - maxime[i]);
			res = maxime[i];
		}
	}
	return res;
}

bool is_inside(Mat img, int i, int j) {
	int rows = img.rows; int cols = img.cols;

	if (0 <= i && i < rows && 0 <= j && j < cols) return true;
	else return false;
}

Mat_<uchar> Floyd_Steinberg(Mat_<uchar> img) {
	vector<float> pdf = get_pdf(img);

	int WH = 5;
	int window = 2 * WH + 1;
	float TH = 0.0003;
	vector<int> local_maxima;
	local_maxima.push_back(0);
	for (int i = WH; i < 256 - WH; i++) {
		float avg = 0;
		float maxim = 0;
		for (int j = i - WH; j <= i + WH; j++) {
			maxim = max(maxim, pdf[j]);
			avg += pdf[j];
		}
		avg /= window;
		if (pdf[i] > avg + TH && pdf[i] >= maxim) {
			local_maxima.push_back(i);
		}
	}
	local_maxima.push_back(255);

	for (int i = 0; i < img.rows; i++)
		for (int j = 0; j < img.cols; j++)
		{
			int old_pixel = img(i, j);
			int new_pixel = getMaxim(old_pixel, local_maxima);
			img(i, j) = new_pixel;
			int err = old_pixel - new_pixel;
			if (is_inside(img, i, j + 1)) {
				if (img(i, j + 1) + 7 * err / 16 > 255)
					img(i, j + 1) = 255;
				else if (img(i, j + 1) + 7 * err / 16 < 0)
					img(i, j + 1) = 0;
				else
					img(i, j + 1) += 7 * err / 16;
			}
			if (is_inside(img, i + 1, j - 1)) {
				if (img(i + 1, j - 1) + 3 * err / 16 > 255)
					img(i + 1, j - 1) = 255;
				else if (img(i, j - 1) + 3 * err / 16 < 0)
					img(i + 1, j - 1) = 0;
				else
					img(i + 1, j - 1) += 3 * err / 16;
			}
			if (is_inside(img, i + 1, j))
			{
				if (img(i + 1, j) + 5 * err / 16 > 255)
					img(i + 1, j) = 255;
				else if (img(i + 1, j) + 5 * err / 16 < 0)
					img(i + 1, j) = 0;
				else
					img(i + 1, j) += 5 * err / 16;
			}
			if (is_inside(img, i + 1, j + 1)) {
				if (img(i + 1, j + 1) + err / 16 > 255)
					img(i + 1, j + 1) = 255;
				else if (img(i + 1, j + 1) + err / 16 < 0)
					img(i + 1, j + 1) = 0;
				else
					img(i + 1, j + 1) += err / 16;
			}

		}
	return img;
}
	

int main() {
	Mat_<uchar> img = imread("Images/cameraman.bmp", 0);
	vector<int> hist = get_histogram(img);
	vector<float> pdf = get_pdf(img);

	img = imread("Images/saturn.bmp", 0);
	Mat_<uchar> img2 = multilevel_treshold(img);
	img = imread("Images/saturn.bmp", 0);
	Mat_<uchar> img3 = Floyd_Steinberg(img);

	

	//cout << to_string(hist);
	//cout << to_string(pdf);

	display_histogram(hist);
	imshow("Multilevel Treshold", img2);
	imshow("Floyd Steinberg", img3);
	waitKey();
}