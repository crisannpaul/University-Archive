#include "testBinaryTree.h"
#include "binaryTree.h"
#include <stdio.h>
#include <stdlib.h>

static void printInt(void *x) {
    printf("%d ", *(int *) x);
}

static unsigned compareInt(void *a, void *b) {
    return *(int *) a == *(int *) b;
}

void test_binaryTree_from_elements() {
    printf("test_binaryTree_from_elements:\n");
    int elements[] = {1, 7, 2, 0, 5, 0, 0, 0, 9, 3, 0, 0, 4, 0, 6, 0, 0};
    int elementsCount = sizeof(elements) / sizeof(*elements);
    void **elementsVoid = malloc(elementsCount * sizeof(void *));
    for (int i = 0; i < elementsCount; i++) {
        elementsVoid[i] = &elements[i];
        if (elements[i] == 0) {
            elementsVoid[i] = NULL;
        }
    }
    BinaryTree *tree = binaryTree_new();
    binaryTree_from_elements(tree, elementsVoid, elementsCount);
    printf("Inorder: ");
    binaryTree_inOrder(tree, printInt);
    binaryTree_free(tree);
    printf("\n");
    free(elementsVoid);
}

void test_binaryTree_balanced_from_elements() {
    printf("test_binaryTree_balanced_from_elements:\n");
    int elements[] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15};
    int elementsCount = sizeof(elements) / sizeof(*elements);
    void **elementsVoid = malloc(elementsCount * sizeof(void *));
    for (int i = 0; i < elementsCount; i++) {
        elementsVoid[i] = &elements[i];
    }
    BinaryTree *tree = binaryTree_new();
    binaryTree_balanced_from_elements(tree, elementsVoid, elementsCount);
    printf("Inorder: ");
    binaryTree_inOrder(tree, printInt);
    binaryTree_free(tree);
    printf("\n");
    free(elementsVoid);
}

void test_binaryTree_insert_balanced() {
    printf("test_binaryTree_insert_balanced:\n");
    int elements[] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15};
    int elementsCount = sizeof(elements) / sizeof(*elements);
    BinaryTree *tree = binaryTree_new();
    for (int i = 0; i < elementsCount; i++) {
        printf("Inserting %d : Inorder: ", elements[i]);
        binaryTree_insert_balanced(tree, &elements[i]);
        binaryTree_inOrder(tree, printInt);
        printf("\n");
    }
    binaryTree_free(tree);
    printf("\n");
}

void test_binaryTree_leafNodes() {
    printf("test_binaryTree_leafNodes:\n");
    int elements[] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15};
    int elementsCount = sizeof(elements) / sizeof(*elements);
    void **elementsVoid = malloc(elementsCount * sizeof(void *));
    for (int i = 0; i < elementsCount; i++) {
        elementsVoid[i] = &elements[i];
    }
    BinaryTree *tree = binaryTree_new();
    binaryTree_balanced_from_elements(tree, elementsVoid, elementsCount);
    printf("Inorder: ");
    binaryTree_inOrder(tree, printInt);
    printf("\n");
    printf("Leafs: ");
    unsigned count = binaryTree_leafNodes(tree, printInt);
    printf("\n");
    printf("Count: %u\n", count);
    binaryTree_free(tree);
    printf("\n");
    free(elementsVoid);
}

void test_binaryTree_internNodes() {
    printf("test_binaryTree_leafNodes:\n");
    int elements[] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15};
    int elementsCount = sizeof(elements) / sizeof(*elements);
    void **elementsVoid = malloc(elementsCount * sizeof(void *));
    for (int i = 0; i < elementsCount; i++) {
        elementsVoid[i] = &elements[i];
    }
    BinaryTree *tree = binaryTree_new();
    binaryTree_balanced_from_elements(tree, elementsVoid, elementsCount);
    printf("Inorder: ");
    binaryTree_inOrder(tree, printInt);
    printf("\n");
    printf("Intern nodes: ");
    unsigned count = binaryTree_internNodes(tree, printInt);
    printf("\n");
    printf("Count: %u\n", count);
    binaryTree_free(tree);
    printf("\n");
    free(elementsVoid);
}

void test_binaryTree_search() {
    printf("test_binaryTree_leafNodes:\n");
    int elements[] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15};
    int searchedElements[] = {1, 4, 15, 0, -5};
    int elementsCount = sizeof(elements) / sizeof(*elements);
    int searchedElementsCount = sizeof(searchedElements) / sizeof(*searchedElements);
    void **elementsVoid = malloc(elementsCount * sizeof(void *));
    for (int i = 0; i < elementsCount; i++) {
        elementsVoid[i] = &elements[i];
    }
    BinaryTree *tree = binaryTree_new();
    binaryTree_balanced_from_elements(tree, elementsVoid, elementsCount);
    printf("Inorder: ");
    binaryTree_inOrder(tree, printInt);
    printf("\n");

    for (int i = 0; i < searchedElementsCount; i++) {
        printf("Searching %d: ", searchedElements[i]);
        unsigned found = binaryTree_search(tree, &searchedElements[i], compareInt);
        printf("%s\n", (found) ? "Found" : "Not found");
    }
    binaryTree_free(tree);
    free(elementsVoid);
    printf("\n");
}

void test_binaryTree_height() {
    printf("test_binaryTree_leafNodes:\n");
    int elements[] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15};
    int elementsCount = sizeof(elements) / sizeof(*elements);
    void **elementsVoid = malloc(elementsCount * sizeof(void *));
    for (int i = 0; i < elementsCount; i++) {
        elementsVoid[i] = &elements[i];
    }
    BinaryTree *tree = binaryTree_new();
    binaryTree_balanced_from_elements(tree, elementsVoid, elementsCount);
    printf("Inorder: ");
    binaryTree_inOrder(tree, printInt);
    printf("\n");
    unsigned height = binaryTree_height(tree);
    printf("Height: %d\n", height);
    binaryTree_free(tree);
    free(elementsVoid);
    printf("\n");
}

void test_binaryTree_all() {
    test_binaryTree_from_elements();
    test_binaryTree_balanced_from_elements();
    test_binaryTree_insert_balanced();
    test_binaryTree_leafNodes();
    test_binaryTree_internNodes();
    test_binaryTree_height();
    test_binaryTree_search();
}
