#include "stdafx.h"
#include "common.h"

using namespace std;

int di[] = { -1, -1, -1, 0, 0, 0, 1, 1, 1 };
int dj[] = { -1, 0, 1, -1, 0, 1, -1, 0, 1 };
int window_size = 9;

bool is_inside(Mat img, int i, int j) {
	int rows = img.rows; int cols = img.cols;

	if (0 <= i && i < rows && 0 <= j && j < cols) return true;
	else return false;
}

Mat_<uchar> noise_filtering(Mat_<uchar> src, string type) {
	Mat_<uchar> dst = src.clone();

	for (int i = 0; i < src.rows; i++) {
		for (int j = 0; j < src.cols; j++) {

			vector<int> pixels;
			for (int k = 0; k < window_size; k++) {
				if (is_inside(src, i + di[k], j + dj[k])) {
					pixels.push_back(src(i + di[k], j + dj[k]));
				}
			}

			sort(pixels.begin(), pixels.end());
			uchar new_val = 0;
			if (type == "min") {
				new_val = pixels.front();
			}
			if (type == "max") {
				new_val = pixels.back();
			}
			if (type == "mean") {
				new_val = pixels[pixels.size()/2];
			}
			dst(i, j) = new_val;
		}
	}

	return dst;
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

Mat_<uchar> gaussian_kernel(float w) {
	Mat_<float> H(w, w);

	for (int i = 0; i < w; i++) {
		for (int j = 0; j < w; j++) {
			int x0 = w / 2, y0 = w / 2;

			float exponent = -((pow(i - x0, 2) - pow(j - y0, 2)) / (2 * pow(w / 6.0f, 2)));
			float new_val = exp(exponent) / (2.0f * pow(PI, 2));
	
			H(i, j) = new_val;
		}
	
	}
	cout << H;
	return H;
}


int main()
{
	Mat_<uchar> img = imread("Images/portrait_Salt&Pepper1.bmp", 0);
	Mat_<uchar> img2 = imread("Images/portrait_Gauss1.bmp", 0);

	imshow("Min Filter", noise_filtering(img, "min"));
	imshow("Max Filter", noise_filtering(img, "max"));
	imshow("Mean Filter", noise_filtering(img, "mean"));

	int w = 5;
	Mat_<float> H = gaussian_kernel(w);
	imshow("Gaussian Filter", normalize(convolution(img2, H), H));

	waitKey();
	return 0;
}