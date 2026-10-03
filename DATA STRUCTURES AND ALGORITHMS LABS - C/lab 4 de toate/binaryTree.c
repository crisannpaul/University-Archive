#include "binaryTree.h"
#include <stdlib.h>
#include <stdio.h>

//creates a new Binary tree
BinaryTree *binaryTree_new() {
    BinaryTree *tree = (BinaryTree*)malloc(sizeof (BinaryTree));
    tree->root = NULL;
    return tree;
}

//deletes a binary tree
void binaryTree_free(BinaryTree *tree) {

}
static NodeBT* createBinTree(NodeBT *parent, void **elements, unsigned elementsCount, unsigned *consumed){
    if(elementsCount<=0) {
        *consumed = 0;
        return NULL;

    }
    void *element = elements[0];
    if(element == 0 ) {
        *consumed = 1;
        return NULL;
    }
    NodeBT *newNode = (NodeBT*)malloc(sizeof(NodeBT));

    newNode-> parent = parent;
    unsigned consumedLeft, consumedRight;
    newNode->left = createBinTree(newNode, elements + 1,elementsCount -1, &consumedLeft);
    newNode->right = createBinTree(newNode, elements + 1 + consumedLeft,elementsCount - 1 - consumedLeft, &consumedRight);
    *consumed = 1 + consumedRight + consumedLeft;



}
static NodeBT* createBinTree2(NodeBT *parent, void **elements, unsigned elementsCount, unsigned *position){
    if(elementsCount - *position == 0 )
        return NULL;
    void *element = elements[*position];
    (*position)++;
    if(element == 0 ) {
        return NULL;
    }
    NodeBT *newNode = (NodeBT*)malloc(sizeof(NodeBT));
    newNode->data = element;
    newNode-> parent = parent;
    newNode->left = createBinTree2(newNode, elements , elementsCount, position);
    newNode->right = createBinTree2(newNode, elements, elementsCount, position);

}
//populates the tree with elements from vector. NULL element means empty branch in tree. The elements already in tree will be erased.
void binaryTree_from_elements(BinaryTree *tree, void **elements, unsigned elementsCount) {
    unsigned position = 0;
tree->root = createBinTree2(NULL,elements,elementsCount,&position);

}

//populates the tree with elements from vector. The result tree will be balanced. The elements already in tree will be erased.
void binaryTree_balanced_from_elements(BinaryTree *tree, void **elements, unsigned elementsCount) {

}

//insert an element in tree. The result tree will be balanced
void binaryTree_insert_balanced(BinaryTree *tree, void *element) {

}

void binaryTree_preOrder(BinaryTree *tree, void (*applyFunction)(void *)) {

}
static void inOrder(NodeBT *node,void (*applyFunction)(void *)){
    if(node == NULL)
        return;
    inOrder(node->left,applyFunction);
    applyFunction(node->data);
    inOrder(node->right,applyFunction);
}
void binaryTree_inOrder(BinaryTree *tree, void (*applyFunction)(void *)) {
  inOrder(tree->root,applyFunction);
}

void binaryTree_postOrder(BinaryTree *tree, void (*applyFunction)(void *)) {

}

//counts and returns the number of leaf nodes. applyFunction can be NULL
unsigned binaryTree_leafNodes(BinaryTree *tree, void (*applyFunction)(void *)) {
    return 0;
}

//counts and returns the number of intern nodes. applyFunction can be NULL
unsigned binaryTree_internNodes(BinaryTree *tree, void (*applyFunction)(void *)) {
    return 0;
}

//searches for elem and returns 1 if it is found, 0 otherwise
//compare function compares two elements and returns 1 if they are equal, 0 otherwise
unsigned binaryTree_search(BinaryTree *tree, void *elem, unsigned (*compareFunction)(void *, void *)) {
    return 0;
}

//returns the height
unsigned binaryTree_height(BinaryTree *tree) {
    return 0;
}