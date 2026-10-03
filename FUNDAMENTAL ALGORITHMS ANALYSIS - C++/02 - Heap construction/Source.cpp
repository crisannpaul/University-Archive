/*
* Crisan Paul Teodor || Grupa 9
* Observam faptul ca in cazul mediu TD face tot mai multe operatii pe masura ce lungimea sirului creste => BU este superior
*/

#include <stdio.h>
#include "Profiler.h"

Profiler p("sortingAlgs");

#define maxSize 10000
#define stepSize 250
#define nrTests 5

void swap(int* a, int* b)
{
	int temp = *a;
	*a = *b;
	*b = temp;
}

void printHeap(int arr[], int size)
{
	for (int i = 0; i < size; i++)
	{
		printf("%d ", arr[i]);
	}
	printf("\n");
}

void heapify(int arr[], int size, int i)
{
	Operation op = p.createOperation("Bottom Up", size);

	int largest = i;
	int left = 2 * i + 1;
	int right = 2 * i + 2;
	op.count(1);
	if (left < size && arr[left] > arr[largest])
		largest = left;
	op.count(1);
	if (right < size && arr[right] > arr[largest])
		largest = right;
	if (largest != i)
	{
		op.count(3);
		swap(&arr[i], &arr[largest]);
		heapify(arr, size, largest);
	}
}

void increaseKey(int arr[], int i, int key, int size)
{

	Operation op = p.createOperation("Top Down", size);

	op.count(1);
	if (key < arr[i])
		exit(42);

	op.count(1);
	arr[i] = key;
	op.count(1);
	while (i > 0 && arr[i / 2] < arr[i])
	{
		op.count(3);
		swap(&arr[i], &arr[i / 2]);
		i = i / 2;
	}
}

void heapInsert(int arr[], int *currSize, int key, int size)
{
	arr[*currSize] = INT_MIN;
	increaseKey(arr, *currSize, key, size);
	*currSize = *currSize + 1;
}

void buildTopDown(int arr[], int size)
{
	int currSize = 0;
	for (int i = 0; i < size; i++)
		heapInsert(arr, &currSize, arr[i], size);
}

void buildBottomUp(int arr[], int size)
{
	for (int i = (size / 2) - 1; i >= 0; i--)
		heapify(arr, size, i);
}

void heapSort(int arr[], int size)
{
	Operation op = p.createOperation("Heap Sort", size);

	for (int i = size / 2 - 1; i >= 0; i--)
		heapify(arr, size, i);
	for (int i = size - 1; i > 0; i--)
	{
		swap(&arr[0], &arr[i]);
		heapify(arr, i, 0);
	}
}

void demo()
{
	int arr[] = { 5, 4, 3, 8, 7, 9, 15, 0, 6 };
	int arr2[] = { 7, 15, 6, 8, 5, 9, 4, 0, 3 };
	int arr3[] = { 6, 8, 3, 9, 1, 4, 11, 15, 5 };
	int n = sizeof(arr) / sizeof(arr[0]);

	buildBottomUp(arr, n);
	printHeap(arr, n);
	buildTopDown(arr2, n);
	printHeap(arr2, n);
	heapSort(arr3, n);
	printHeap(arr3, n);

}

void perf(int order)
{
	int a[maxSize], b[maxSize];
	int n;
	for (n = stepSize; n <= maxSize; n += stepSize)
	{
		for (int test = 0; test < nrTests; test++)
		{
			FillRandomArray(a, n, 10, 50000, false, order); //e ok daca folosesc doua siruri aleatorii?
			buildTopDown(a, n);
			FillRandomArray(b, n, 10, 50000, false, order);
			buildBottomUp(b, n);
		}
	}
	p.divideValues("Top Down", nrTests);
	p.divideValues("Bottom Up", nrTests);
	p.createGroup("TD vs. BU", "Top Down", "Bottom Up");
	p.showReport();
}

int main()
{
	demo();
	//perf(3);
}