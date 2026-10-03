#ifndef SDA_UTIL_BINARYTREE_H
#define SDA_UTIL_BINARYTREE_H
typedef struct NodeBT{
void *data;
struct NodeBT *left, *right, *parent;
} NodeBT;

typedef struct {
NodeBT *root;
} BinaryTree;

//creates a new Binary tree
BinaryTree *binaryTree_new();

//deletes a binary tree
void binaryTree_free(BinaryTree *tree);

//populates the tree with elements from vector. NULL element means empty branch in tree. The elements already in tree will be erased.
void binaryTree_from_elements(BinaryTree *tree, void **elements, unsigned elementsCount);

//populates the tree with elements from vector. The result tree will be balanced. The elements already in tree will be erased.
void binaryTree_balanced_from_elements(BinaryTree *tree, void **elements, unsigned elementsCount);

//insert an element in tree. The result tree will be balanced
void binaryTree_insert_balanced(BinaryTree *tree, void *element);

void binaryTree_preOrder(BinaryTree *tree, void (*applyFunction)(void *));

void binaryTree_inOrder(BinaryTree *tree, void (*applyFunction)(void *));

void binaryTree_postOrder(BinaryTree *tree, void (*applyFunction)(void *));

//counts and returns the number of leaf nodes. applyFunction can be NULL
unsigned binaryTree_leafNodes(BinaryTree *tree, void (*applyFunction)(void *));

//counts and returns the number of intern nodes. applyFunction can be NULL
unsigned binaryTree_internNodes(BinaryTree *tree, void (*applyFunction)(void *));

//searches for elem and returns 1 if it is found, 0 otherwise
//compare function compares two elements and returns 1 if they are equal, 0 otherwise
unsigned binaryTree_search(BinaryTree *tree, void *elem, unsigned (*compareFunction)(void *, void *));

//returns the height
unsigned binaryTree_height(BinaryTree *tree);


#endif //SDA_UTIL_BINARYTREE_H
