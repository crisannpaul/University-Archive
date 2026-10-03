#include "listDL.h"
#include <stdlib.h>

//creates an empty list
ListDL *listDL_new() {
    ListDL *list = malloc(sizeof(ListDL)); //allocate memory
    if (list == NULL) {
        return NULL; // cannot allocate memory
    }
    list->first = NULL; //initialize fields
    list->last = NULL;
    return list;
}

//deletes a list and free memory
void listDL_free(ListDL *list) {
    if (list == NULL) {
        return; // NULL list
    }
    NodeDL *it = list->first;
    while (it != NULL) {
        NodeDL *next = it->next; // remember the next element in list
        free(it); //free current node
        it = next; // go to the next element in list
    }
    free(list); //free list memory
}

//searches for elem and returns element if it is found, NULL otherwise
void* listDL_search(ListDL *list, void *elem, unsigned (*compareFunction)(void *, void *)) {
    if (list == NULL) {
        return 0; // NULL list
    }
    NodeDL *it = list->first; //start from the first node
    while (it != NULL) {
        if (compareFunction(it->data, elem) == 1) { //check if current node is the searched one
            return it->data;
        }
        it = it->next; // go to the next element in list
    }
    return NULL;
}

//inserts elem on first position
void listDL_insert_first(ListDL *list, void *elem) {
    if (list == NULL) {
        return; // NULL list
    }
    NodeDL *newNode = malloc(sizeof(NodeDL)); //allocate memory
    newNode->next = NULL; //initialize fields
    newNode->prev = NULL;
    newNode->data = elem;

    if (list->first == NULL) { //check for empty list
        list->last = newNode; //if empty, first and last node will be this node
    } else {
        list->first->prev = newNode;
    }

    newNode->next = list->first; //insert newNode in list
    list->first = newNode;
}

//inserts elem on last position
void listDL_insert_last(ListDL *list, void *elem) {
    if (list == NULL) {
        return; // NULL list
    }
    NodeDL *newNode = malloc(sizeof(NodeDL)); //allocate memory
    newNode->next = NULL; //initialize fields
    newNode->prev = NULL;
    newNode->data = elem;

    if (list->first == NULL) { //check for empty list
        list->first = newNode; //if empty, first and last node will be this node
    } else {
        list->last->next = newNode; //insert newNode in list
    }
    newNode->prev = list->last;
    list->last = newNode;
}

//inserts elem after the afterElem; if not found, insert on last position
void listDL_insert_after(ListDL *list, void *afterElem, void *elem, unsigned (*compareFunction)(void *, void *)) {
    if (list == NULL) {
        return; // NULL list
    }
    NodeDL *newNode = malloc(sizeof(NodeDL)); //allocate memory
    newNode->next = NULL; //initialize fields
    newNode->data = elem;

    if (list->first == NULL) { //check for empty list
        listDL_insert_last(list, elem); //if empty, insert last
        return;
    }
    NodeDL *it = list->first; //start from the first node

    while (it != NULL) {
        if (compareFunction(it->data, afterElem) == 1) { //check if current node is the searched one
            //insert newNode between current node and the next one
            NodeDL *next = it->next; //remember next node
            it->next = newNode;
            newNode->next = next;
            newNode->prev = it;
            if (next == NULL) { //check if searched element was the last one in list
                list->last = newNode; //update the last node
            } else {
                next->prev = newNode;
            }
            return;
        }
        it = it->next; // go to the next element in list
    }
    //node not found
    //insert last
    listDL_insert_last(list, elem);
}

//removes first element
void *listDL_remove_first(ListDL *list) {
    if (list == NULL) {
        return NULL; // NULL list
    }
    if (list->first == NULL) {          //check for empty list
        return NULL;
    }
    //at least one node
    NodeDL *first = list->first;          //remember first node

    //remove element from list
    if (list->first == list->last) {    // check if list has only one element
        list->first = NULL;
        list->last = NULL;
    } else {
        first->next->prev = NULL;       //mark prev of first as NULL
        list->first = first->next;
    }
    void *elem = first->data;
    free(first);
    return elem;
}

//removes last element
void *listDL_remove_last(ListDL *list) {
    if (list == NULL) {
        return NULL; // NULL list
    }
    if (list->first == NULL) {          //check for empty list
        return NULL;
    }
    //at least one node
    NodeDL *last = list->last;            //remember last node

    //remove last element from list
    if (list->first == list->last) {    // check if list has only one element
        list->first = NULL;
        list->last = NULL;
    } else {
        last->prev->next = NULL;
        list->last = last->prev;
    }
    void *elem = last->data;
    free(last);
    return elem;
}

//removes first occurrence of element elem
void listDL_remove_elem(ListDL *list, void *elem, unsigned (*compareFunction)(void *, void *)) {
    if (list == NULL) {
        return; // NULL list
    }
    if (list->first == NULL) {                          //check for empty list
        return;
    }
    //at one two node
    NodeDL *it = list->first;
    while (it != NULL) {
        if (compareFunction(it->data, elem) == 1) {
            if (it->prev == NULL && it->next == NULL) {
                //current node is the last one in list
                list->first = NULL;
                list->last = NULL;
                free(it);
                it = NULL;
            } else if (it->prev == NULL) {
                //current node is first node
                list->first = it->next;
                list->first->prev = NULL;
                free(it);
            } else if (it->next == NULL) {
                //current node is the last node
                list->last = it->prev;
                list->last->next = NULL;
                free(it);
            } else {
                it->prev->next = it->next;
                it->next->prev = it->prev;
                free(it);
            }
            break;
        } else {
            it = it->next;
        }
    }
}

//removes all occurrences of element elem
void listDL_remove_all_elem(ListDL *list, void *elem, unsigned (*compareFunction)(void *, void *)) {
    if (list == NULL) {
        return; // NULL list
    }
    if (list->first == NULL) {                          //check for empty list
        return;
    }
    //at least one node
    NodeDL *it = list->first;
    while (it != NULL) {
        if (compareFunction(it->data, elem) == 1) {
            if (it->prev == NULL && it->next == NULL) {
                //current node is the last one in list
                list->first = NULL;
                list->last = NULL;
                free(it);
                it = NULL;
            } else if (it->prev == NULL) {
                //current node is the first node
                list->first = it->next;
                it->next->prev = NULL;
                free(it);
                it = list->first;
            } else if (it->next == NULL) {
                //current node is the last node
                list->last = it->prev;
                list->last->next = NULL;
                free(it);
                it = NULL;
            } else {
                NodeDL *next = it->next;
                it->prev->next = it->next;
                it->next->prev = it->prev;
                free(it);
                it = next;
            }
        } else {
            it = it->next;
        }
    }
}

//removes all elements
void listDL_remove_all(ListDL *list) {
    if (list == NULL) {
        return; // NULL list
    }
    NodeDL *it = list->first;
    while (it != NULL) {
        NodeDL *currentNode = it;  //remember current node
        it = it->next;
        free(currentNode);
    }
    list->first = NULL;
    list->last = NULL;
}

//apply applyFunction on each element
void listDL_iterate(ListDL *list, void (*applyFunction)(void *)) {
    if (list == NULL) {
        return; // NULL list
    }
    NodeDL *it = list->first;
    while (it != NULL) {
        applyFunction(it->data);
        it = it->next;
    }
}

//apply applyFunction on each element
void listDL_iterate_backward(ListDL *list, void (*applyFunction)(void *)) {
    if (list == NULL) {
        return; // NULL list
    }
    NodeDL *it = list->last;
    while (it != NULL) {
        applyFunction(it->data);
        it = it->prev;
    }
}
