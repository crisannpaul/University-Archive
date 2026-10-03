#include "binarySearchTree.h"
#include <stdlib.h>
//creates a new Binary tree
BinarySearchTree *binarySearchTree_new(){
    BinarySearchTree *bst = (BinarySearchTree* )malloc(sizeof(*bst));
    bst->root = NULL;
    return bst;
}

//deletes a binary tree
void binarySearchTree_free(BinarySearchTree *tree){

}
static NodeBST *createNode(void *data, NodeBST *parent)
{
    NodeBST *newNode = (NodeBST*)malloc(sizeof(NodeBST));
    newNode->data = data;
    newNode->left = NULL;
    newNode->right = NULL;
    newNode->parent = parent;
    return newNode;
}

static void* insertElem1(BinarySearchTree *tree, void *element, int (*compareFunction)(void *, void *)) {
    if (tree->root == NULL) {
        tree->root = createNode(element, NULL);
        return tree->root;
    } else {
        NodeBST *current = tree->root;
        while (1) {
            if(compareFunction(element,current->data) == 0)
                return NULL;
            if (compareFunction(element, current->data) > 0) {
                if (current->right != NULL)
                    current = current->right;
                else {

                    current->right = createNode(element, current);
                    return element;
                }
            } else {
                if (current->left != NULL)
                    current = current->left;
                else {

                    current->left = createNode(element, current);
                    return element;
                }
            }
        }
    }
}


//inserts an element
void binarySearchTree_insert(BinarySearchTree *tree, void *element, int (*compareFunction)(void *, void *)){
insertElem1(tree,element,compareFunction);
}

NodeBST *predecessor(NodeBST *node){
    if(node == NULL)
        return NULL;
    if(node->left == NULL)
        return NULL;
    node = node -> left;
    while(node->right !=NULL)
    {
        node = node->right;
    }
    return node;
}
NodeBST *successor(NodeBST *node){
    if(node == NULL)
        return NULL;
    if(node->right == NULL)
        return NULL;
    node = node -> right;
    while(node->left !=NULL)
    {
        node = node->left;
    }
    return node;
}
//removes an element
NodeBST *binarySearchTree_remove(BinarySearchTree *tree, void *element, int (*compareFunction)(void *, void *)){
    if (tree->root == NULL) {
       return NULL;
    } else {
        NodeBST *current = tree->root;
        while (1) {
            if(compareFunction(element,current->data) == 0){

                    NodeBST *prev = predecessor(current);
                    if(prev == NULL)
                    {
                       if(current->right != NULL) {
                           prev = current;
                           current->data = current->right->data;
                           current->right->parent = current->parent;
                           if (current->parent != NULL){
                               current->parent->right = current->right;
                           }
                           else
                           {
                               tree->root = current->right;
                           }
                           free(prev);

                       }
                       else
                       {
                           if(current->left != NULL) {
                               prev = current;
                               current->data = current->left->data;
                               current->left->parent = current->parent;
                               if (current->parent != NULL){
                                   current->parent->left= current->left;
                               }
                               else
                               {
                                   tree->root = current->left;
                               }
                                free(prev);

                           }
                           else
                           {
                               if(current->parent == NULL)
                                   tree->root = NULL;
                               else {
                                   if(compareFunction(current->data,current->parent->data)>0)
                                   current->parent->right = NULL;
                                   else
                                       current->parent->left = NULL;
                                   free(current);
                               }
                           }
                       }
                        return tree->root;
                    }
                    else
                    {
                        if(prev->left != NULL)
                        {
                            current->data = prev->data;
                            prev->left->parent = prev->parent;
                            if(prev->parent == NULL) {
                                tree->root = prev->left;
                            }
                            else
                                prev->parent->right = prev->left;
                            free(prev);

                        }
                        else
                        {
                            current->data = prev->data;
                            if(compareFunction(prev->data,prev->parent->data)>0)
                                prev->parent->right = NULL;
                            else
                                prev->parent->left = NULL;


                            free(prev);
                        }

                        return tree->root;
                    }

                }

            if (compareFunction(element, current->data) > 0) {
                if (current->right != NULL)
                    current = current->right;
                else {
                    return NULL;
                }
            } else {
                if (current->left != NULL)
                    current = current->left;
                else {
                    return NULL;
                }
            }
        }
    }
}
static void preOrder(NodeBST *node, void (*applyFunction)(void *)){
    if(node!=NULL)
    {
        applyFunction(node->data);
        preOrder(node->left,applyFunction);
        preOrder(node->right,applyFunction);
    }
}
void binarySearchTree_preOrder(BinarySearchTree *tree, void (*applyFunction)(void *)){
preOrder(tree->root,applyFunction);
}

void binarySearchTree_inOrder(BinarySearchTree *tree, void (*applyFunction)(void *)){

}

void binarySearchTree_postOrder(BinarySearchTree *tree, void (*applyFunction)(void *)){

}

//searches for element and returns 1 if it is found, 0 otherwise
//compare function compares two elements
unsigned binarySearchTree_search(BinarySearchTree *tree, void *element, int (*compareFunction)(void *, void *)){
    return 0;
}

//returns the height
unsigned binarySearchTree_height(BinarySearchTree *tree){
    return 0;
}
