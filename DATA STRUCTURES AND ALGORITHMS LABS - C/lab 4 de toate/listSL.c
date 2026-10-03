#include "listSL.h"
#include <stdlib.h>

//creates an empty list
ListSL *listSL_new() {
    ListSL *list = malloc(sizeof(ListSL)); //allocate memory
    if (list == NULL) {
        return NULL; // cannot allocate memory
    }
    list->first = NULL; //initialize fields
    list->last = NULL;
    return list;
}

//deletes a list and free memory
void listSL_free(ListSL *list) {
    if (list == NULL) {
        return; // NULL list
    }
    NodeSL *it = list->first;
    while (it != NULL) {
        NodeSL *next = it->next; // remember the next element in list
        free(it); //free current node
        it = next; // go to the next element in list
    }
    free(list); //free list memory
}

//searches for elem and returns 1 if it is found, 0 otherwise
unsigned listSL_search(ListSL *list, void *elem, unsigned (*compareFunction)(void *, void *)) {
    if (list == NULL) {
        return 0; // NULL list
    }
    NodeSL *it = list->first; //start from the first node
    while (it != NULL) {
        if (compareFunction(it->data, elem) == 1) { //check if current node is the searched one
            return 1;
        }
        it = it->next; // go to the next element in list
    }
    return 0;
}

//inserts elem on first position
void listSL_insert_first(ListSL *list, void *elem) {
    if (list == NULL) {
        return; // NULL list
    }
    NodeSL *newNode = malloc(sizeof(NodeSL)); //allocate memory
    newNode->next = NULL; //initialize fields
    newNode->data = elem;

    if (list->first == NULL) { //check for empty list
        list->last = newNode; //if empty, first and last node will be this node
    }

    newNode->next = list->first; //insert newNode in list
    list->first = newNode;
}

//inserts elem on last position
void listSL_insert_last(ListSL *list, void *elem) {
    if (list == NULL) {
        return; // NULL list
    }
    NodeSL *newNode = malloc(sizeof(NodeSL)); //allocate memory
    newNode->next = NULL; //initialize fields
    newNode->data = elem;

    if (list->first == NULL) { //check for empty list
        list->first = newNode; //if empty, first and last node will be this node
    } else {
        list->last->next = newNode; //insert newNode in list
    }

    list->last = newNode;
}

//inserts elem after the afterElem; if not found, insert on last position
void listSL_insert_after(ListSL *list, void *afterElem, void *elem, unsigned (*compareFunction)(void *, void *)) {
    if (list == NULL) {
        return; // NULL list
    }
    NodeSL *newNode = malloc(sizeof(NodeSL)); //allocate memory
    newNode->next = NULL; //initialize fields
    newNode->data = elem;

    if (list->first == NULL) { //check for empty list
        listSL_insert_last(list, elem); //if empty, insert last
        return;
    }
    NodeSL *it = list->first; //start from the first node

    while (it != NULL) {
        if (compareFunction(it->data, afterElem) == 1) { //check if current node is the searched one
            //insert newNode between current node and the next one
            NodeSL *next = it->next; //remember next node
            it->next = newNode;
            newNode->next = next;
            if (next == NULL) { //check if searched element was the last one in list
                list->last = newNode; //update the last node
            }
            return;
        }
        it = it->next; // go to the next element in list
    }
    //node not found
    //insert last
    listSL_insert_last(list, elem);
}

//removes first element
void *listSL_remove_first(ListSL *list) {
    if (list == NULL) {
        return NULL; // NULL list
    }
    if (list->first == NULL) {          //check for empty list
        return NULL;
    }
    //at least one node
    NodeSL *first = list->first;          //remember first node

    //remove element from list
    if (list->first == list->last) {    // check if list has only one element
        list->first = NULL;
        list->last = NULL;
    } else {
        list->first = first->next;
    }
    void *elem = first->data;
    free(first);
    return elem;
}

//removes last element
void *listSL_remove_last(ListSL *list) {
    if (list == NULL) {
        return NULL; // NULL list
    }
    if (list->first == NULL) {          //check for empty list
        return NULL;
    }
    //at least one node
    NodeSL *last = list->last;            //remember last node

    //remove last element from list
    if (list->first == list->last) {    // check if list has only one element
        list->first = NULL;
        list->last = NULL;
    } else {
        NodeSL *it = list->first;
        //find the node before last one
        while (it->next != list->last) {
            it = it->next;
        }
        // now current node is the one before last
        // remove last node
        it->next = NULL;
        list->last = it;
    }
    void *elem = last->data;
    free(last);
    return elem;
}

//removes first occurrence of element elem
void listSL_remove_elem(ListSL *list, void *elem, unsigned (*compareFunction)(void *, void *)) {
    if (list == NULL) {
        return; // NULL list
    }
    if (list->first == NULL) {                          //check for empty list
        return;
    }
    //at least one node
    NodeSL *prev = NULL;
    NodeSL *it = list->first;
    while (it != NULL) {
        if (compareFunction(it->data, elem) == 1) {
            if (prev == NULL && it->next == NULL) {
                list->first = NULL;
                list->last = NULL;
                free(it);
            } else if (prev == NULL) {
                //current node is first node
                list->first = it->next;
                free(it);
            } else if (it->next == NULL) {
                //current node is the last node
                list->last = prev;
                list->last->next = NULL;
                free(it);
            } else {
                prev->next = it->next;
                free(it);
            }
            break;
        } else {
            prev = it;
            it = it->next;
        }
    }
}

//removes all occurrences of element elem
void listSL_remove_all_elem(ListSL *list, void *elem, unsigned (*compareFunction)(void *, void *)) {
    if (list == NULL) {
        return; // NULL list
    }
    if (list->first == NULL) {                          //check for empty list
        return;
    }
    //at least one node
    NodeSL *prev = NULL;
    NodeSL *it = list->first;
    while (it != NULL) {
        if (compareFunction(it->data, elem) == 1) {
            if (prev == NULL && it->next == NULL) {
                list->first = NULL;
                list->last = NULL;
                free(it);
                it = NULL;
            } else if (prev == NULL) {
                //current node is the first node
                list->first = it->next;
                free(it);
                it = list->first;
            } else if (it->next == NULL) {
                //current node is the last node
                list->last = prev;
                list->last->next = NULL;
                free(it);
                it = NULL;
            } else {
                prev->next = it->next;
                free(it);
                it = prev->next;
            }
        } else {
            prev = it;
            it = it->next;
        }
    }
}

//removes all elements
void listSL_remove_all(ListSL *list) {
    if (list == NULL) {
        return; // NULL list
    }
    NodeSL *it = list->first;
    while (it != NULL) {
        NodeSL *currentNode = it;  //remember current node
        it = it->next;
        free(currentNode);
    }
    list->first = NULL;
    list->last = NULL;
}

//apply applyFunction on each element
void listSL_iterate(ListSL *list, void (*applyFunction)(void *)) {
    if (list == NULL) {
        return; // NULL list
    }
    NodeSL *it = list->first;
    while (it != NULL) {
        applyFunction(it->data);
        it = it->next;
    }
}
