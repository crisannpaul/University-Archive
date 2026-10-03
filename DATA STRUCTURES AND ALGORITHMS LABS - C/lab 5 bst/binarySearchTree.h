#ifndef SDA_UTIL_BINARYSEARCHTREE_H
#define SDA_UTIL_BINARYSEARCHTREE_H
typedef struct NodeBST{
void *data;
struct NodeBST *parent;
struct NodeBST *left;
struct NodeBST *right;
} NodeBST;

typedef struct {
NodeBST *root;
} BinarySearchTree;

//creates a new Binary tree
BinarySearchTree *binarySearchTree_new();

//deletes a binary tree
void binarySearchTree_free(BinarySearchTree *tree);

//inserts an element
void binarySearchTree_insert(BinarySearchTree *tree, void *element, int (*compareFunction)(void *, void *));


//removes an element
NodeBST *binarySearchTree_remove(BinarySearchTree *tree, void *element, int (*compareFunction)(void *, void *));

void binarySearchTree_preOrder(BinarySearchTree *tree, void (*applyFunction)(void *));

void binarySearchTree_inOrder(BinarySearchTree *tree, void (*applyFunction)(void *));

void binarySearchTree_postOrder(BinarySearchTree *tree, void (*applyFunction)(void *));

//searches for element and returns 1 if it is found, 0 otherwise
//compare function compares two elements
unsigned binarySearchTree_search(BinarySearchTree *tree, void *element, int (*compareFunction)(void *, void *));

//returns the height
unsigned binarySearchTree_height(BinarySearchTree *tree);

#endif //SDA_UTIL_BINARYSEARCHTREE_H
