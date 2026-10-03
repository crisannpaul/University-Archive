// OpenCVApplication.cpp : Defines the entry point for the console application.
//

#include "stdafx.h"
#include "common.h"
#include <queue>
#include <random>
// default_random_engine gen;
// uniform_int_distribution<int> d(0, 255);
// uchar x = d(gen);

using namespace std;

// queue<pair<int, int>> Q;
// Q.push(pair<int, int>(i, j));
// pair<int, int> p = Q.front(); Q.pop();
// //se pot accesa coordonatele punctului p astfel
// i = p.first; j = p.second;

bool is_inside(Mat img, int i, int j) {
	int rows = img.rows; int cols = img.cols;

	if (0 <= i && i < rows && 0 <= j && j < cols) return true;
	else return false;
}

Mat_<int> label(Mat_<uchar> img) {
	int label = 0;
	Mat_<int> labels(img.rows, img.cols);
	labels.setTo(0);
	for (int i = 0; i < img.rows; i++)
		for (int j = 0; j < img.cols; j++) {
			if (img(i, j) == 0 && labels(i,j) == 0) {

				label++;
				labels(i, j) = label;

				queue<pair<int, int>> Q;
				Q.push(pair<int, int>(i, j));
				while (!Q.empty()) {
					pair<int, int> p = Q.front(); Q.pop();
					i = p.first; j = p.second;

					int di[4] = { -1,0,1,0 };
					int dj[4] = { 0,-1,0,1 };

					for (int k = 0; k < 4; k++) {
						int in = i + di[k]; int jn = j + dj[k];
						if (is_inside(img, in, jn)) {
							if (img(in, jn) == 0 && labels(in, jn) == 0) {
								labels(in, jn) = label;
								Q.push(pair<int, int>(in, jn));
							}
						}
					}
				}
			}
		}
	return labels;
}


int get_nr_labels(Mat_<int> labels) {
	//Mat_<int> labels = label2(img);
	int nr_labels = 0;

	for (int i = 0; i < labels.rows; i++)
		for (int j = 0; j < labels.cols; j++) {
			nr_labels = max(nr_labels, labels(i, j));
		}

	return nr_labels;
}

Mat_<Vec3b> img_label(Mat_<int> img) {
	int nr_labels = get_nr_labels(img);

	default_random_engine gen;
	uniform_int_distribution<int> dist(0, 255);

	vector<Vec3b> colors(nr_labels + 1);
	colors[0] = Vec3b(255, 255, 255);
	for (int i = 1; i <= nr_labels; i++) {
		uchar b = dist(gen); uchar g = dist(gen); uchar r = dist(gen);
		colors[i] = Vec3b(b, g, r);
	}

	Mat_<Vec3b> img_label(img.rows, img.cols);
	img_label.setTo(Vec3b(255, 255, 255));

	for (int i = 0; i < img.rows; i++) {
		for (int j = 0; j < img.cols; j++) {
			img_label(i, j) = colors[img(i, j)];
		}
	}

	return img_label;
}


Mat_<int> label2(Mat_<uchar> img) {
	int label = 0;
	Mat_<int> labels(img.rows, img.cols);
	labels.setTo(0);

	vector<vector<int>> edges(1000);
	for (int i = 0; i < img.rows; i++)
		for (int j = 0; j < img.cols; j++) {
			if (img(i, j) == 0 && labels(i, j) == 0) {
				vector<int> L;

				int di[4] = { -1,0,1,0 };
				int dj[4] = { 0,-1,0,1 };

				for (int k = 0; k < 4; k++) {
					int in = i + di[k]; int jn = j + dj[k];
					if (is_inside(img, in, jn)) {
						if (labels(in, jn) > 0) {
							L.push_back(labels(in, jn));
						}
					}
				}

				if (L.size() == 0) {//assign new label
					label++;
					labels(i, j) = label;
				}
				else {
					int x = *min_element(L.begin(), L.end());
					labels(i, j) = x;
					for (int k = 0; k < L.size(); k++) {
						int y = L[k];
						if (x != y) {
							edges[x].push_back(y);
							edges[y].push_back(x);
						}
					}
				}
			}
		}

	Mat_<Vec3b> labeled_img = img_label(labels);
	imshow("First iteration", labeled_img);

	int new_label = 0;
	vector<int> new_labels(label+1);
	for (int i = 1; i < label; i++) {
		if (new_labels[i] == 0) {
			new_label++;
			new_labels[i] = new_label;

			queue<int> Q;
			Q.push(i);
			while (!Q.empty()) {
				int x = Q.front(); Q.pop();

				for (int k = 0; k < edges[x].size(); k++) {
					int y = edges[x][k];
					if (new_labels[y] == 0) {
						new_labels[y] = new_label;
						Q.push(y);
					}
				}
			}
		}
	}

	for (int i = 0; i < labels.rows; i++) {
		for (int j = 0; j < labels.cols; j++) {
			labels(i, j) = new_labels[labels(i,j)];
		}
	}
	return labels;
}

String matToString(Mat_<int> mat) {
	String out = "";
	for (int i = 0; i < mat.rows; i++) {
		for (int j = 0; j < mat.cols; j++) {
			out.append(" ");
			out.append(to_string(mat(i, j)));
		}
		out.append("\n");
	}
	return out;
}

int main()
{
	Mat_<uchar> img = imread("Images/circle_square.bmp", 0);
	Mat_<uchar> img2 = imread("Images/crosses.bmp", 0);
	Mat_<uchar> img3 = imread("Images/diagonal.bmp", 0);
	Mat_<uchar> img4 = imread("Images/disks.bmp", 0);

	Mat_<int> labels1 = label2(img);
	Mat_<int> labels2 = label2(img2);
	Mat_<int> labels3 = label2(img3);
	Mat_<int> labels4 = label2(img4);

	imshow("Circle square", img_label(labels1));
	imshow("Crosses", img_label(labels2));
	imshow("Diagonal", img_label(labels3));
	imshow("Disks", img_label(labels4));

	cout << matToString(labels2);

	waitKey();
 	return 0;
}