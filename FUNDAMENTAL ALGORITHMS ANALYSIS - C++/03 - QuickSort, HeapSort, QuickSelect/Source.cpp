/*
* - Quick Sort are complexitatea in cazul defavoravil = O(n^2), iar in cazurile mediu/defavorabil = O(nlogn)
* - Heap Sort are complexitatea O(nlogn)
* - Quick Select are complexitatea O(n^2) 
*/

#include <stdio.h>
#include "Profiler.h";

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

void printArray(int arr[], int size)
{
	for (int i = 0; i < size; i++)
	{
		printf("%d ", arr[i]);
	}
	printf("\n");
}

int partition(int arr[], int low, int high, int n)
{
	Operation op = p.createOperation("Quick Sort", n);

	op.count();
	int pivot = arr[high]; 
	int i = low - 1;

	for (int j = low; j <= high - 1; j++)
	{
		op.count();
		if (arr[j] < pivot)
		{
			i++;
			op.count(3);
			swap(&arr[i], &arr[j]);
		}
	}
	op.count(3);
	swap(&arr[i + 1], &arr[high]);
	return (i + 1);
}

void heapify(int arr[], int size, int i, Operation* op)
{
	int largest = i;
	int left = 2 * i + 1;
	int right = 2 * i + 2;

	if (left < size)
	{
		(*op).count(1);
		if (arr[left] > arr[largest])
			largest = left;
	}
	if (right < size)
	{
		(*op).count(1);
		if (arr[right] > arr[largest])
			largest = right;
	}
	if (largest != i)
	{
		(*op).count(3);
		swap(&arr[i], &arr[largest]);
		heapify(arr, size, largest, op);
	}
}

void quickSort(int arr[], int low, int high, int n)
{

	if (low < high)
	{
		int pi = partition(arr, low, high, n);
		quickSort(arr, low, pi - 1, n);
		quickSort(arr, pi + 1, high, n);
	}
}

int quickSelect(int arr[], int low, int high, int k)
{
	Operation op = p.createOperation("Quick Select", high);

	int index = partition(arr ,low, high, k);

	if (index - low == k - 1)
		return arr[index];
	else
	if (index - low > k - 1)
		return quickSelect(arr, low, index - 1, k);
	else
		return quickSelect(arr, index + 1, high, k - index);
}

void heapSort(int arr[], int n)
{
	Operation op = p.createOperation("Heap Sort", n);

	for (int i = n / 2 - 1; i >= 0; i--)
		heapify(arr, n, i, &op);

	for (int i = n - 1; i > 0; i--) {
		swap(&arr[0], &arr[i]);
		heapify(arr, i, 0, &op);
	}
}

void demo()
{
	int arr1[] = { 5, 4, 3, 8, 7, 9, 15, 0, 6 };
	int arr2[] = { 5, 4, 3, 8, 7, 9, 15, 0, 6 };
	int arr3[] = { 5, 4, 3, 8, 7, 9, 15, 0, 6 };
	int n = sizeof(arr1) / sizeof(arr1[0]);
	int k_quickSelect = 4;
	printf("Quick Select: %d\n", quickSelect(arr2, 0, n - 1, k_quickSelect));
	quickSort(arr1, 0, n-1, n);
	printArray(arr1, n);
	heapSort(arr3, n);
	printArray(arr3, n);
}

void perf_best()
{
	int a1[maxSize], a2[maxSize];
	int n;
	for (n = stepSize; n <= maxSize; n += stepSize)
	{
		for (int test = 0; test < nrTests; test++)
		{
			FillRandomArray(a1, n, 10, 50000, false, ASCENDING);
			memcpy(a2, a1, n * sizeof(a1[0]));
			quickSort(a1, 0, n - 1, n);
			heapSort(a2, n);
		}
	}
	p.divideValues("Heap Sort", nrTests);
	p.divideValues("Quick Sort", nrTests);
	p.createGroup("Heap Sort vs Quick Sort - BEST", "Heap Sort", "Quick Sort");
	p.showReport();
}

void perf_avg()
{
	int a1[maxSize], a2[maxSize];
	int n;
	for (n = stepSize; n <= maxSize; n += stepSize)
	{
		for (int test = 0; test < nrTests; test++)
		{
			FillRandomArray(a1, n, 10, 50000, false, UNSORTED);
			memcpy(a2, a1, n * sizeof(a1[0]));
			quickSort(a1, 0, n-1, n);
			heapSort(a2, n);			
		}
	}
	p.divideValues("Heap Sort", nrTests);
	p.divideValues("Quick Sort", nrTests);
	p.createGroup("Heap Sort vs Quick Sort - AVG", "Heap Sort", "Quick Sort");
	p.showReport();
}

void perf_worst()
{
	int a1[maxSize], a2[maxSize];
	int n;
	for (n = stepSize; n <= maxSize; n += stepSize)
	{
		for (int test = 0; test < nrTests; test++)
		{
			FillRandomArray(a1, n, 10, 50000, false, DESCENDING);
			memcpy(a2, a1, n * sizeof(a1[0]));
			quickSort(a1, 0, n - 1, n);
			heapSort(a2, n);
		}
	}
	p.divideValues("Heap Sort", nrTests);
	p.divideValues("Quick Sort", nrTests);
	p.createGroup("Heap Sort vs Quick Sort - WORST", "Heap Sort", "Quick Sort");
	p.showReport();
}
int main()
{
	//perf_best();
	//perf_avg();
	perf_worst();
	//demo();
}


