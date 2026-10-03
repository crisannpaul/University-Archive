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

int area(Mat_<uchar> image) {
	Mat_<uchar> img = image.clone();
	
	int area = 0;
	for (int i = 0; i < img.rows; i++)
		for (int j = 0; j < img.cols; j++) {
			if (img(i, j) == 0) area++;
		}
	return area;
}

Mat_<uchar> mass_center(Mat_<uchar> image) {
	Mat_<uchar> img = image.clone();

	int r = 0; int c = 0;
	for (int i = 0; i < img.rows; i++)
		for (int j = 0; j < img.cols; j++) {
			if (img(i, j) == 0) {
				r += i;
				c += j;
			}
		}
	int A = area(img);
	
	r = r / A;
	c = c / A;

	int line_size = 8;

	Point p1(c - line_size, r), p2(c + line_size, r);
	line(img, p1, p2, 255);

	Point p3(c, r - line_size), p4(c, r + line_size);
	line(img, p3, p4, 255);

	return img;
}

Mat_<uchar> elongation_axis(Mat_<uchar> image) {
	Mat_<uchar> img = image.clone();

	int r = 0; int c = 0;
	for (int i = 0; i < img.rows; i++)
		for (int j = 0; j < img.cols; j++) {
			if (img(i, j) == 0) {
				r += i;
				c += j;
			}
		}
	int A = area(img);

	r = r / A;
	c = c / A;

	float sum1 = 0; float sum2 = 0; float sum3 = 0;
	for (int i = 0; i < img.rows; i++)
		for (int j = 0; j < img.cols; j++) {
			if (img(i, j) == 0) {
				sum1 += (i - r) * (j - c);
				sum2 += (j - c) * (j - c);
				sum3 += (i - r) * (i - r);
			}
		}
	float N = 2 * sum1;
	float n = sum2 - sum3;

	float psi = atan2(N,n) / 2;
	
	int line_size = 75;
	Point p1(c - line_size * cos(psi), r - line_size * sin(psi));
	Point p2(c + line_size * cos(psi), r + line_size * sin(psi));
	line(img, p1, p2, 255);

	return img;
}

float perimeter(Mat_<uchar> image) {
	Mat_<uchar> img = image.clone();
	float perimeter = 0;

	for (int i = 0; i < img.rows; i++)
		for (int j = 0; j < img.cols; j++) {
			if (img(i, j) == 0) {
				if (img(i + 1, j) == 255 ||
					img(i - 1, j) == 255 ||
					img(i, j + 1) == 255 ||
					img(i, j - 1) == 255) {
					perimeter++;
				}
				else {
					continue;
				}
			}
		}

	return perimeter;
}

Mat_<uchar> show_perimeter(Mat_<uchar> image) {
	Mat_<uchar> img = image.clone();

	for (int i = 0; i < img.rows; i++)
		for (int j = 0; j < img.cols; j++) {
			if (img(i, j) == 0) {
				if (img(i + 1, j) == 255 ||
					img(i - 1, j) == 255 ||
					img(i, j + 1) == 255 ||
					img(i, j - 1) == 255) {
					continue;
				}
				else {
					img(i, j) = 254;
				}
			}
		}
	
	return img;
}

float thinning_factor(Mat_<uchar> image) {
	Mat_<uchar> img = image.clone();

	float A = area(img);
	float P = perimeter(img);

	float T = 4 * PI * (A / (P * P));

	return T;
}

float aspect_ratio(Mat_<uchar> image) {
	Mat_<uchar> img = image.clone();

	int cmin = img.cols; int rmin = img.rows;
	int rmax = 0; int cmax = 0;
	for (int i = 0; i < img.rows; i++)
		for (int j = 0; j < img.cols; j++) {
			if (img(i, j) == 0) {
				cmin = min(cmin, j);
				cmax = max(cmax, j);
				rmin = min(rmin, i);
				rmax = max(rmax, i);
			}
		}
	float R = (float)(cmax - cmin + 1) / (float)(rmax - rmin + 1);

	return R;
}

Mat_<uchar> rectangle(Mat_<uchar> image) {
	Mat_<uchar> img = image.clone();

	int rmax = 0, rmin = img.rows;
	int cmax = 0, cmin = img.cols;
	for (int i = 0; i < img.rows; i++) {
		for (int j = 0; j < img.cols; j++) {
			if (img(i, j) == 0) {
				if (i < rmin) rmin = i;
				if (i > rmax) rmax = i;
				if (j < cmin) cmin = j;
				if (j > cmax) cmax = j;
			}
		}
	}

	Point p1(cmin, rmin), p2(cmin, rmax), p3(cmax, rmin), p4(cmax, rmax);

	line(img, p1, p3, 0);
	line(img, p4, p3, 0);
	line(img, p2, p4, 0);
	line(img, p2, p1, 0);

	return img;
}

Mat_<uchar> horizontal_projection(Mat_<uchar> image) {
	Mat_<uchar> img = image.clone();

	vector<int> horizontal_pixels(img.rows);
	for (int i = 0; i < img.rows; i++) {
		for (int j = 0; j < img.cols; j++) {
			if (img(i, j) == 0) horizontal_pixels[i]++;
		}
	}

	Mat_<uchar> horizontal_hist(img.rows, img.cols);
	horizontal_hist.setTo(255);
	for (int i = 0; i < img.rows; i++) {
		for (int j = 0; j < horizontal_pixels[i]; j++) {
			horizontal_hist(i, j) = 0;
		}
	}
	return horizontal_hist;
}

Mat_<uchar> vertical_projection(Mat_<uchar> image) {
	Mat_<uchar> img = image.clone();

	vector<int> vertical_pixels(img.cols);
	for (int j = 0; j < img.cols; j++) {
		for (int i = 0; i < img.rows; i++) {
			if (img(i, j) == 0) vertical_pixels[j]++;
		}
	}

	Mat_<uchar> vertical_hist(img.rows, img.cols);
	vertical_hist.setTo(255);
	for (int i = 0; i < img.rows; i++) {
		for (int j = 0; j < vertical_pixels[i]; j++) {
			vertical_hist(i, j) = 0;
		}
	}
	return vertical_hist;
}

int main() {
	Mat_<uchar> img = imread("Objects/oval_obl.bmp", 0);

	cout << "Area: " << area(img) << endl;
	cout << "Thinning factor: " << thinning_factor(img) << endl;
	cout << "Perimeter: " << perimeter(img) << endl;
	cout << "Aspect ratio: " << aspect_ratio(img) << endl;

	imshow("Mass center", mass_center(img));
	imshow("Elongation axis", elongation_axis(img));
	imshow("Perimeter", show_perimeter(img));
	imshow("Rectangle", rectangle(img));
	imshow("Horizontal histogram", horizontal_projection(img));
	imshow("Vertical histogram", vertical_projection(img));
 	
	waitKey();
	return 0;
}