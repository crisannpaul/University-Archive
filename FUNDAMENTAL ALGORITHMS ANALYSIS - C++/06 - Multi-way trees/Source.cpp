#include <stdlib.h>
#include <stdio.h>

typedef struct nodeR2
{
	int key;
	int nrChildren;
	struct nodeR2* children[3];
}NodeR2;

typedef struct nodeR3
{
	int key;
	struct nodeR3* firstChild;
	struct nodeR3* rightBrother;
}NodeR3;

void prettyR1(int R1[], int size, int node, int h)
{
	for (int i = 0; i < size; i++)
	{
		if (node == R1[i])
		{
			for (int j = 0; j < h; j++) printf("   ");
			printf("%d\n", i);
			prettyR1(R1, size, i, h + 1);
		}
	}
}

NodeR2* constructT1(int R1[], int size)
{
	NodeR2* R2[10];

	int root;

	for (int i = 0; i < size; i++)
	{
		R2[i] = (NodeR2*)malloc(sizeof(nodeR2));
		R2[i]->key = i;
		R2[i]->nrChildren = 0;
	}

	for (int i = 0; i < size; i++)
		if (R1[i] != -1)
		{
			R2[R1[i]]->children[R2[R1[i]]->nrChildren] = R2[i];
			R2[R1[i]]->nrChildren++;
		}
		else root = i;

	return R2[root];
}

void prettyR2(NodeR2* node, int h)
{
	if (node != NULL)
	{
		for (int i = 0; i < h; i++) printf("   ");
		printf("%d\n", node->key);
		for (int i = 0; i < node->nrChildren; i++)
		{
			prettyR2(node->children[i], h + 1);
		}
	}
}

NodeR3* constructT2(NodeR2* node, int root)
{
	NodeR3* newNode = new NodeR3;
	newNode->key = node->key;
	newNode->firstChild = NULL;
	newNode->rightBrother = NULL;
	if (node->nrChildren > 0)
	{
		newNode->firstChild = constructT2(node->children[0], -1);
		NodeR3* lastNode = newNode->firstChild;
		for (int i = 1; i < node->nrChildren; i++)
		{
			 NodeR3* aux = constructT2(node->children[i], -1);
			lastNode->rightBrother = aux;
			lastNode = aux;
		}
	}
	if (newNode->key == root) return newNode;
}

void prettyR3(NodeR3* node, int h)
{
	if (node != NULL)
	{
		for (int i = 0; i < h; i++) printf("   ");
		printf("%d\n", node->key);
		prettyR3(node->firstChild, h + 1);
		prettyR3(node->rightBrother, h);
	}
}

void demo()
{
	int R1[] = { 9, 2, 5, 4, 5, -1, 4, 9, 9, 5};
	int size = sizeof(R1) / sizeof(R1[0]);

	printf("Pretty-print pentru R1:\n\n");
	prettyR1(R1, size, -1, 0);

	printf("\n\nPretty-print pentru R2:\n\n");
	NodeR2* R2 = (NodeR2*)malloc(sizeof(NodeR2));
	R2 = constructT1(R1, size);
	prettyR2(R2, 0);

	printf("\n\nPretty-print pentru R3:\n\n");
	NodeR3* R3 = (NodeR3*)malloc(sizeof(NodeR3));
	R3 = constructT2(R2, R2->key);
	prettyR3(R3, 0);
}

int main()
{ 
	demo();
}