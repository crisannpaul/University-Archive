#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "Profiler.h"

Profiler p("Dynamic Order Statistics");

typedef struct node
{
	int key;
	int size;
	struct node* left;
	struct node* right;
}Node;

void printTree(Node* node, int h)
{
	if (node != NULL)
	{
		for (int i = 0; i < h; i++) printf("   ");
		printf("[%d] - %d\n", node->key, node->size);
		printTree(node->left, h + 1);
		printTree(node->right, h + 1);
	}
}

Node* minNode(Node* node)
{
	Node* minNode = node;
	while (minNode != NULL && minNode->left != NULL)
	{
		minNode = minNode->left;
	}
	return minNode;
}

Node* buildPBT(int arr[], int left, int right)
{
	if (left <= right)
	{
		Node* node = (Node*)malloc(sizeof(Node));
		int middle = (left + right) / 2;
		node->key = arr[middle];
		node->size = right - left + 1;
		node->left = buildPBT(arr, left, middle - 1);
		node->right = buildPBT(arr, middle + 1, right);
		return node;
	}
	else return NULL;
}

int osSelect(Node* node, int i, Operation* op)
{
	int rank;

	(*op).count(1);
	if (node->left != NULL) rank = node->left->size + 1;
	else rank = 1;

	(*op).count(2);
	if (i == rank) return node->key;
	else if (i < rank) return osSelect(node->left, i, op);
	else if (i > rank) return osSelect(node->right, i - rank, op);
}

void deleteNode(Node* node, int key, Operation* op)
{
	(*op).count(3);
	if (node->key == key)
	{
		node->size--;
		(*op).count(3);
		if (node->left == NULL && node->right == NULL)
		{
			(*op).count();
			node = NULL;
		}
		else if (node->left == NULL)
		{
			(*op).count();
			node->key = node->right->key;
			node->right = NULL;
		}
		else if (node->right == NULL)
		{
			(*op).count();
			node->key = node->left->key;
			node->left = NULL;
		}
		else
		{
			(*op).count();
			Node* min = minNode(node->right);
			node->key = min->key;
			deleteNode(node->right, min->key, op);
		}
	}
	else if (node->key < key)
	{
		node->size--;
		deleteNode(node->right, key, op);
	}
	else if (node->key > key)
	{
		node->size--;
		deleteNode(node->left, key, op);
	}
	else if (node == NULL)
	{
		printf("Node not found");
	}
}
void perf()
{
	int arr[10001];
	srand(time(NULL));

	for (int n = 100; n <= 10000; n = n + 100)
	{
		for (int k = 0; k < 5; k++)
		{
			FillRandomArray(arr, n, 1, n, false, ASCENDING);

			Node* root = buildPBT(arr, 1, n);

			Operation op = p.createOperation("Management Operations", n);

			for (int i = 0; i < n; i++)
			{
				int x = rand() % n;
				osSelect(root, x, &op);
				if (arr[x - 1] != -1)
				{
					deleteNode(root, x, &op);
					arr[x - 1] = -1;
				}
			}
		}
	}
	p.divideValues("Management Operations", 5);
	p.showReport();
}

void demo()
{
	int size = 11;
	int arr[12];

	Operation op = p.createOperation("Dummy", size);

	for (int i = 1; i <= size; i++) arr[i] = i;

	printf("Pretty print:\n");
	Node* root = buildPBT(arr, 1, size);
	printTree(root, 0);

	srand(time(NULL));

	printf("\n\nOS-Select:\n");
	for (int i = 0; i < 3; i++)
	{
		int x = (rand() % root->size) + 1;
		printf("For: %d  =>  %d\n", x, osSelect(root, x, &op));
	}

	printf("\n\nDeleted nodes: ");
	for (int i = 0; i < 3; i++)
	{
		int x = (rand() % root->size) + 1;
		printf("%d ", x);
		deleteNode(root, x, &op);
	}
	printf("\n\nTree after deleting the nodes: \n");
	printTree(root, 0);


}

int main()
{
	demo();
	//perf();
}