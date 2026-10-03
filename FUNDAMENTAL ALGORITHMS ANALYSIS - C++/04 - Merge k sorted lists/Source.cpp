// Crisan Paul | Grupa 9

#include <stdio.h>
#include <iostream>
#include "Profiler.h"

Profiler p("MergeLists");

typedef struct node
{
    int key;
    int index;
    struct node* next;
} Node;

void printList(Node* first)
{
	while (first != NULL)
	{
		printf(" %d,", first->key);
		first = first->next;
	}
}

void listInsert(Node** first, int key, int index)
{
	Node* node = (Node*)malloc(sizeof(Node));
	node->key = key;
	node->index = index;
	node->next = NULL;
	if (*first == NULL)
	{
		*first = node;
	}
	else
	{
		node->next = *first;
		*first = node;
	}
}

Node* listCreate(int k, int n, int index)
{
	Node* list = NULL;
	int* v = (int*)malloc((n / k) * sizeof(int));
	FillRandomArray(v, n / k, 10, 50000, false, 2);
	for (int i = 0; i < n / k; i++)
	{
		listInsert(&list, v[i], index);
	}
	return list;
}

void MinHeapify(Node** arr_min, int i, int k, Operation op)
{
	int min = i;
	int left = 2 * i + 1;
	int right = 2 * i + 2;
	op.count();
	if (arr_min[i] == NULL)
	{
		return;
	}
	if (left < k)
	{
		op.count();
		if ((arr_min[left])->key < (arr_min[i])->key)
		{
			min = left;
		}
	}
	if (right < k)
	{
		op.count();
		if ((arr_min[right])->key < (arr_min[min])->key)
		{
			min = right;
		}
	}
	if (min != i)
	{
		op.count(3);
		Node* aux = arr_min[i];
		arr_min[i] = arr_min[min];
		arr_min[min] = aux;
		MinHeapify(arr_min, min, k, op);
	}
}

void buildHeap(Node** arr_min, int k, Operation op)
{
	for (int i = k / 2 - 1; i >= 0; i--)
	{
		MinHeapify(arr_min, i, k, op);
	}
}

void mergeLists(Node** list, Node** first_rez, Node** last_rez, int k, int n, Operation op)
{
	Node** arr_min = (Node**)malloc(k * sizeof(Node*));
	for (int i = 0; i < k; i++)
	{
		op.count(3);
		arr_min[i] = list[i];
		if (list[i] != NULL)
		{
			list[i] = (list[i])->next;
		}
		arr_min[i]->next = NULL;
	}
	buildHeap(arr_min, k, op);
	while (k)
	{
		if (arr_min[0] != NULL)
		{
			op.count(2);
			Node* aux = arr_min[0];
			int index = aux->index;
			if (*first_rez == NULL)
			{
				*first_rez = *last_rez = aux;
			}
			else
			{
				(*last_rez)->next = aux;
				*last_rez = aux;
			}
			op.count();
			if (list[index] != NULL)
			{
				op.count(3);
				arr_min[0] = list[index];
				list[index] = list[index]->next;
				arr_min[0]->next = NULL;
				MinHeapify(arr_min, 0, k, op);
			}
			else
			{
				op.count();
				arr_min[0] = arr_min[k - 1];
				k--;
				MinHeapify(arr_min, 0, k, op);
			}
		}
	}
}

void demo()
{
	int k = 4;
	int n = 20;
	Node* first_rez = NULL;
	Node* last_rez = NULL;
	Node** list = (Node**)malloc(k * sizeof(Node*));
	for (int i = 0; i < k; i++)
	{
		list[i] = NULL;
	}
	for (int i = 0; i < k; i++)
	{
		list[i] = listCreate(k, n, i);
	}
	for (int i = 0; i < k; i++)
	{
		printf("List %d:", i);
		printList(list[i]);
		printf("\n");
	}
	Operation dummy = p.createOperation("Dummy", n);
	mergeLists(list, &first_rez, &last_rez, k, n, dummy);
	printf("Final list: ");
	printList(first_rez);
}

void perf_k1()
{
	for (int n = 100; n <= 10000; n += 100)
	{
		Operation op1 = p.createOperation("Merge_k1", n);
		Node* first_rez1 = NULL;
		Node* last_rez1 = NULL;
		Node** list = (Node**)malloc(5 * sizeof(Node*));
		for (int i = 0; i < 5; i++)
		{
			list[i] = NULL;
		}
		for (int i = 0; i < 5; i++)
		{
			list[i] = listCreate(5, n, i);
		}
		mergeLists(list, &first_rez1, &last_rez1, 5, n, op1);
		while (first_rez1 != NULL)
		{
			Node* aux = first_rez1;
			first_rez1 = first_rez1->next;
			free(aux);
		}
	}
}

void perf_k2()
{
	for (int n = 100; n <= 10000; n += 100)
	{
		Operation op1 = p.createOperation("Merge_k2", n);
		Node* first_rez1 = NULL;
		Node* last_rez1 = NULL;
		Node** list = (Node**)malloc(10 * sizeof(Node*));
		for (int i = 0; i < 10; i++)
		{
			list[i] = NULL;
		}
		for (int i = 0; i < 10; i++)
		{
			list[i] = listCreate(10, n, i);
		}
		mergeLists(list, &first_rez1, &last_rez1, 10, n, op1);
		while (first_rez1 != NULL)
		{
			Node* aux = first_rez1;
			first_rez1 = first_rez1->next;
			free(aux);
		}
	}
}

void perf_k3()
{
	for (int n = 100; n <= 10000; n += 100)
	{
		Operation op1 = p.createOperation("Merge_k3", n);
		Node* first_rez1 = NULL;
		Node* last_rez1 = NULL;
		Node** list = (Node**)malloc(100 * sizeof(Node*));
		for (int i = 0; i < 100; i++)
		{
			list[i] = NULL;
		}
		for (int i = 0; i < 100; i++)
		{
			list[i] = listCreate(100, n, i);
		}
		mergeLists(list, &first_rez1, &last_rez1, 100, n, op1);
		while (first_rez1 != NULL)
		{
			Node* aux = first_rez1;
			first_rez1 = first_rez1->next;
			free(aux);
		}
	}
}

void perform_avg()
{
	perf_k1();
	perf_k2();
	perf_k3();
	p.createGroup("Merge_k_lists", "Merge_k1", "Merge_k2", "Merge_k3");
	p.showReport();
}

void perf_n()
{
	int n = 10000;
	for (int k = 10; k <= 500; k += 10)
	{
		Operation op1 = p.createOperation("Merge_n", k);
		Node* first_rez1 = NULL;
		Node* last_rez1 = NULL;
		Node** list = (Node**)malloc(k * sizeof(Node*));
		for (int i = 0; i < k; i++)
		{
			list[i] = NULL;
		}
		for (int i = 0; i < k; i++)
		{
			list[i] = listCreate(k, n, i);
		}
		mergeLists(list, &first_rez1, &last_rez1, k, n, op1);
		while (first_rez1 != NULL)
		{
			Node* aux = first_rez1;
			first_rez1 = first_rez1->next;
			free(aux);
		}
		free(list);
	}
	p.showReport();
}

int main()
{
	demo();
	//perform_avg();
	//perf_n();
}