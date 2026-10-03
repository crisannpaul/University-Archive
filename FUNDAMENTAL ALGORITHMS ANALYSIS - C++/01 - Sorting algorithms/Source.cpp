/*
* Crisan Paul - Teodor | Grupa 9
* Am implementat 3 algoritmi de sortare: insertionSort, bubbleSort si selectionSort
* Observam ca - in average case insertionSort e cel mai eficient, urmat de selectionSort si respectiv bubbleSort
*             - in best case insertionSort e cel mai eficient, avand graficul liniar, iar bubbleSort si selectionSort sunt relativ la egalitate
*             - in worst case insertionSort si selectionSort sunt relativ egale, fiind cele mai eficiente, urmate desigur de bubbleSort
*/
#include <stdio.h>
#include "Profiler.h"

Profiler p("sortingAlgs");

#define maxSize 10000
#define stepSize 500
#define nrTests 5

void swap(int* xp, int* yp)
{
    int temp = *xp;
    *xp = *yp;
    *yp = temp;
}

void afisare(int arr[], int size)
{
    int i;
    for (i = 0; i < size; i++)
        printf("%d, ", arr[i]);
    printf("\n");
}

void insertionSort (int arr[], int n)
{
    Operation comp = p.createOperation("ins - comp", n);
    Operation att = p.createOperation("ins - att", n);
    int i, key, j;
    for (i = 1; i < n; i++)
    {
        att.count();
        key = arr[i];
        j = i - 1;
        comp.count();
        while (j >= 0 && arr[j] > key)
        {
            att.count();
            arr[j + 1] = arr[j];
            j = j - 1;
        }
        att.count();
        arr[j + 1] = key;   
    }
}

void bubbleSort(int arr[], int n)
{
    Operation comp = p.createOperation("bubb - comp", n);
    Operation att = p.createOperation("bubb - att", n);
    int i, j;
    for (i = 0; i < n - 1; i++)
        for (j = 0; j < n - i - 1; j++)
        {
            comp.count();
            if (arr[j] > arr[j + 1])
            {
                att.count(3);
                swap(&arr[j], &arr[j + 1]);
            }
        }
}

void selectionSort(int arr[], int n)
{
    Operation comp = p.createOperation("sel - comp", n);
    Operation att = p.createOperation("sel - att", n);
    int i, j, min_idx;
    for (i = 0; i < n - 1; i++)
    {
        min_idx = i;
        for (j = i + 1; j < n; j++)
        {
            comp.count();
            if (arr[j] < arr[min_idx])
                min_idx = j;
        }
        att.count(3);
        swap(&arr[min_idx], &arr[i]);
    }
}

void perf(int order)
{
    int a[maxSize], b[maxSize], c[maxSize];
    int n;
    for (n = stepSize; n <= maxSize; n += stepSize)
    {
        for (int test = 0; test < nrTests; test++)
        {
            FillRandomArray(a, n, 10, 50000, false, order);
            insertionSort(a, n);
            FillRandomArray(b, n, 10, 50000, false, order);
            bubbleSort(b, n);
            FillRandomArray(c, n, 10, 50000, false, order);
            selectionSort(c, n);
        }
    }
    p.divideValues("ins - comp", nrTests);
    p.divideValues("ins - att", nrTests);
    p.addSeries("ins", "ins - att", "ins - comp");

    p.divideValues("bubb - comp", nrTests);
    p.divideValues("bubb - att", nrTests);
    p.addSeries("bubb", "bubb - att", "bubb - comp");

    p.divideValues("sel - comp", nrTests);
    p.divideValues("sel - att", nrTests);
    p.addSeries("sel", "sel - att", "sel - comp");

    p.createGroup("comp", "ins - comp", "bubb - comp", "sel - comp");
    p.createGroup("att", "ins - att", "bubb - att", "sel - att");
    p.createGroup("total", "ins", "bubb", "sel");
}

void perf_all()
{
    perf(UNSORTED);
    p.reset("best");
    perf(ASCENDING);
    p.reset("worst");
    perf(DESCENDING);
    p.showReport();
}

void demo()
{
    int a[] = { 1, 5, 8, 4, 10, 6, 3 };
    int b[] = { 1, 5, 8, 4, 10, 6, 3 };
    int c[] = { 1, 5, 8, 4, 10, 6, 3 };
    int n = sizeof(a) / sizeof(a[0]);
    insertionSort(a, n);
    printf("Sirul sortat cu insertionSort:\n");
    afisare(a, n);

    bubbleSort(b, n);
    printf("Sirul sortat cu bubbleSort:\n");
    afisare(b, n);

    selectionSort(c, n);
    printf("Sirul sortat cu selectionSort:\n");
    afisare(c, n);

    // sortarile functioneaza cu succes!
}

int main()
{
    perf_all();
    //demo();
    return 0;
}

