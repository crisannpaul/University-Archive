#include <stdio.h>
#include <iostream>
#include <fstream>	
#include "Profiler.h"

using namespace std;


typedef struct elem {
	int key;
	boolean free;
} Elem;

void printTable(Elem* table, int size)
{ 
	for (int i = 0; i < size; i++)
	{
		if (table[i].free == false) printf("[%d] ", table[i].key);
		else printf("[-] ");
	}
	printf("\n");
}

int hKey(int key, int size) {
	int hKey = key % size;
	if (hKey < 0) hKey += size;
	return hKey;
}

int hFunc(int key, int size, int i)
{
	return (hKey(key, size) + 3 * i + i * i) % size;
}

void insertKey(int key, Elem* table, int size)
{
	for (int i = 0; i < size; i++)
	{
		int index = hFunc(key, size, i);
		if (table[index].free == true)
		{
			table[index].key = key;
			table[index].free = false;
			break;
		}
	}
}

int searchKey(int key, Elem* table, int size, int* op)
{
	for (int i = 0; i < size; i++)
	{
		(*op)++;
		int index = hFunc(key, size, i);
		if (table[index].key == key) return index;
		else if (table[index].free == true) return -1;
	}
	return -1;
}

void clearTable(Elem* table, int size)
{
	for (int i = 0; i < size; i++) table[i].free = true;
}

void perf()
{
	int N = 9973;
	float a[] = { 0.8, 0.85, 0.9, 0.95, 0.99 };

	float found_avg[5] = { 0 }, nfound_avg[5] = { 0 }, found_max[5] = { 0 }, nfound_max[5] = { 0 };

	//time_t t;
	//srand((unsigned)time(&t));

	for (int tests = 0; tests < 5; tests++)
	{
		int arr[9973];
		int load = 0;
		int i = 0;

		Elem* table = (Elem*)malloc(N * sizeof(Elem));
		clearTable(table, N);

		FillRandomArray(arr, N, 0, 50000, true);

		for (int k = 0; k < 5; k++)
		{
			int n = a[k] * N;

			while (load < n)
			{
				insertKey(arr[i], table, N);
				load++;
				i++;
			}
			for (int m = 0; m < 3000; m++)
			{
				int op = 0;

				if (m % 2 == 0)
				{
					searchKey(arr[rand() % load], table, N, &op);
					found_avg[k] += op;
					if (op > found_max[k]) found_max[k] = op;
				}
				else
				{
					searchKey(arr[rand() % load + 50000], table, N, &op);
					nfound_avg[k] += op;
					if (op > nfound_max[k]) nfound_max[k] = op;
				}
			}
		}
	}

	for (int k = 0; k < 5; k++)
	{
		found_avg[k] /= (1500 * 5);
		nfound_avg[k] /= (1500 * 5);
	}

	printf("A     --     Avg Found -- Max Found -- Avg Not Found -- Max Not Found\n");

	for (int k = 0; k < 5; k++)
	{
		printf("%.2f  --       %.2f    --   %.2f   --    %.2f    --     %.2f\n", a[k], found_avg[k], found_max[k], nfound_avg[k], nfound_max[k]);
	}
}

void demo()
{

	int size = 50;
	int arr[50];
	float factor = 0.95;
	int load = (int)(factor * size);
	int dummy = 0;

	Elem* table = (Elem*)malloc(size * sizeof(Elem));
	clearTable(table, size);
	printTable(table, size);

	FillRandomArray(arr, size, 1, 500, true);


	for (int i = 0; i < load; i++) insertKey(arr[i], table, size);
	printTable(table, size);

	printf("%d\n", searchKey(arr[3], table, size, &dummy));
	printf("%d", searchKey(arr[3] + 500, table, size, &dummy));

}
int main()
{
	//demo();
	perf();
}