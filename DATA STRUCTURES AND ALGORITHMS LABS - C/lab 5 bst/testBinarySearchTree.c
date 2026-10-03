#include "testBinarySearchTree.h"
#include "binarySearchTree.h"
#include <stdio.h>
static void printInt(void *x) {
    printf("%d ", *(int *) x);
}

static int compareInt(void *a, void *b) {
    return *(int *) a - *(int *) b;
}
void test_binarySearchTree_insert(){
    printf("test_binarySearchTree_insert:\n");
    int elements[] = {4, 2, 1, 3, 6, 5, 7};
    int elementsCount = sizeof(elements) / sizeof(*elements);
    BinarySearchTree *tree = binarySearchTree_new();
    for (int i = 0; i < elementsCount; i++) {
        printf("Inserting %d : Preorder: ", elements[i]);
        binarySearchTree_insert(tree, &elements[i], compareInt);
        binarySearchTree_preOrder(tree, printInt);
        printf("\n");
    }
    //tree->root = binarySearchTree_remove(tree,&elements[0],compareInt);  // am scris asta aici pentru teste, exista functie de remove mai jos
    //binarySearchTree_preOrder(tree, printInt);
    binarySearchTree_free(tree);
    printf("\n");
}

void test_binarySearchTree_search(){
    printf("test_binarySearchTree_search:\n");
    int elements[] = {4, 2, 1, 3, 6, 5, 7};
    int elementsCount = sizeof(elements) / sizeof(*elements);
    int searchedElements[] = {2, 5, 13, 15, -1};
    int searchedElementsCount = sizeof(searchedElements) / sizeof (*searchedElements);

    BinarySearchTree *tree = binarySearchTree_new();
    for (int i = 0; i < elementsCount; i++) {
        binarySearchTree_insert(tree, &elements[i], compareInt);
    }
    printf("Initial tree: Preorder: ");
    binarySearchTree_preOrder(tree, printInt);
    printf("\n");

    for (int i = 0; i < searchedElementsCount; i++) {
        printf("Searching %d: ", searchedElements[i]);
        unsigned found = binarySearchTree_search(tree, &searchedElements[i], compareInt);
        printf("%s\n", (found) ? "Found" : "Not found");
    }
    binarySearchTree_free(tree);
    printf("\n");
}

void test_binarySearchTree_remove(){
    printf("test_binarySearchTree_remove:\n");
    int elements[] = {4, 2, 1, 3, 6, 5, 7};
    int elementsCount = sizeof(elements) / sizeof(*elements);
    int removedElements[] = {1, 4, 5, 13, 15, -1};
    int removedElementsCount = sizeof(removedElements) / sizeof (*removedElements);

    BinarySearchTree *tree = binarySearchTree_new();
    for (int i = 0; i < elementsCount; i++) {
        binarySearchTree_insert(tree, &elements[i], compareInt);
    }
    printf("Initial tree: Preorder: ");
    binarySearchTree_preOrder(tree, printInt);
    printf("\n");

    for (int i = 0; i < removedElementsCount; i++) {
        printf("Removing %d: ", removedElements[i]);
        binarySearchTree_remove(tree, &removedElements[i], compareInt);
        printf("Preorder: ");
        binarySearchTree_preOrder(tree, printInt);
        printf("\n");
    }
    binarySearchTree_free(tree);
    printf("\n");
}

void test_binarySearchTree_all(){
    test_binarySearchTree_insert();
    test_binarySearchTree_search();
    test_binarySearchTree_remove();
}
