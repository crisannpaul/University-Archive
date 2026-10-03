#include <stdio.h>
#include <stdlib.h>
#include "Profiler.h"


struct Set
{
	int key;
	int rank;
	Set* parent;
};

struct Edge
{
	int left;
	int right;
	int weight;
};

Set* makeSet(int key)
{
	Set* set = new Set;
	set->key = key;
	set->rank = 0;
	set->parent = set;
	return set;
}

Set* findSet(Set* set)
{
	if (set != set->parent)
	{
		set->parent = findSet(set->parent);
	}
	return set->parent;
}

void link(Set* set1, Set* set2)
{
	if (set1->rank > set2->rank)
	{
		set2->parent = set1;
	}
	else
	{
		set1->parent = set2;
		if (set1->rank == set2->rank)
		{
			set2->rank++;
		}
	}
}

void unionn(Set* set1, Set* set2)
{
	link(findSet(set1), findSet(set2));
}

void bubbleSort(Edge arr[], int size)
{
	for(int i = 0; i < size; i++)
		for(int j = 0; j < size - i - 1; j++)
			if (arr[j].weight > arr[j + 1].weight)
			{
				Edge temp = arr[j];
				arr[j] = arr[j + 1];
				arr[j + 1] = temp;
			}
}

Edge* kruskalAlg(Edge edges[], int n, int m)
{
	Set* nodes[10];
	Edge* arr = new Edge[n];

	int size = 0;

	for (int i = 1; i <= n; i++)
	{
		nodes[i] = makeSet(i);
	}

	bubbleSort(edges, n);

	int i = 0;
	while (i < m && size < n - 1)
	{
		if (findSet(nodes[edges[i].right]) != findSet(nodes[edges[i].left]))
		{
			arr[size] = edges[i];
			size++;
			unionn(nodes[edges[i].right], nodes[edges[i].left]);
		}
		i++;
	}
	return arr;
}

void demoUnion()
{
	Set* arr[10];

	for (int i = 0; i < 10; i++)
	{
		arr[i] = makeSet(i + 1); 
		printf("%d -> Set: %d\n", arr[i]->key, findSet(arr[i])->key);
	}

	unionn(arr[3], arr[5]);
	unionn(arr[2], arr[5]);
	unionn(arr[0], arr[4]);
	unionn(arr[7], arr[4]);
	printf("\n");

	for (int i = 0; i < 10; i++)
	{
		printf("%d -> Set: %d\n", arr[i]->key, findSet(arr[i])->key);
	}
}

void demoKruskal()
{
	Edge edges[10];
	Edge* tree;

	int n = 5;
	int m = 6;

	edges[0].left = 1;
	edges[0].right = 2;
	edges[0].weight = 1;

	edges[1].left = 1;
	edges[1].right = 3;
	edges[1].weight = 6;

	edges[2].left = 1;
	edges[2].right = 5;
	edges[2].weight = 7;

	edges[3].left = 2;
	edges[3].right = 5;
	edges[3].weight = 3;

	edges[4].left = 3;
	edges[4].right = 4;
	edges[4].weight = 10;

	edges[5].left = 4;
	edges[5].right = 5;
	edges[5].weight = 2;

	tree = kruskalAlg(edges, n, m);

	for (int i = 0; i < n - 1; i++)
		printf("%d -- %d | cost: %d\n", tree[i].left, tree[i].right, tree[i].weight);
}

int main()
{
	//demoUnion();
	demoKruskal();
}
