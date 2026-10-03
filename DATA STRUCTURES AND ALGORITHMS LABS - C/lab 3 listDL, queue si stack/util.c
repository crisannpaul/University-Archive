#include "util.h"
#include <stdio.h>
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
void listSL_remove_first(ListSL *list) {
    if (list == NULL) {
        return; // NULL list
    }
    if (list->first == NULL) {          //check for empty list
        return;
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
    free(first);
}

//removes last element
void listSL_remove_last(ListSL *list) {
    if (list == NULL) {
        return; // NULL list
    }
    if (list->first == NULL) {          //check for empty list
        return;
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
    free(last);
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
            if (prev == NULL) {
                //current node is first node
                list->first = it->next;
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
            if (prev == NULL) {
                //current node is first node
                list->first = it->next;
                free(it);
                it = list->first;
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



//Array functions
//all insert functions can increase capacity, if necessary

//creates an array with max capacity elements
Array *array_new(unsigned capacity) {
    Array *array = malloc(sizeof(Array));
    if (array == NULL) {
        return NULL; //cannot allocate memory
    }
    array->size = 0;
    array->capacity = capacity;
    array->data = malloc(capacity * sizeof(void *));
    return array;
}

//deletes an array
void array_free(Array *array) {
    if (array == NULL) { //check for NULL array
        return;
    }
    free(array->data);
    free(array);
}

//returns element at position in array
void *array_get_at(Array *array, unsigned position) {
    if (array == NULL) { //check for NULL array
        return NULL;
    }
    if (position >= array->size) {
        return NULL;
    }
    return array->data[position];
}

//returns the size of array
unsigned array_get_size(Array *array){
    if (array == NULL) { //check for NULL array
        return 0;
    }
    return array->size;
}

//searches for elem and returns position of elem in array or -1 if not found
int array_search(Array *array, void *elem, unsigned (*compareFunction)(void *, void *)) {
    for (int i = 0; i < array->size; i++) {
        if (compareFunction(array->data[i], elem) == 1) {
            return i;
        }
    }
    return -1;
}

//helper function which makes space for an element on position "position"
static unsigned array_make_space(Array *array, int position) {
    if (array->size == array->capacity) {
        array->capacity *= 2;
        array->data = realloc(array->data, array->capacity * sizeof(void *));
        if (array->data == NULL) {
            return 1;
        }
    }
    for (int i = array->size; i > position; i--) {
        array->data[i] = array->data[i - 1];
    }
    array->size++;
    return 0;
}

static void array_delete_space(Array *array, int position) {
    for (int i = position; i < array->size - 1; i++) {
        array->data[i] = array->data[i + 1];
    }
    array->size--;
}

//inserts elem on first position
void array_insert_first(Array *array, void *elem) {
    if (array == NULL) { //check for NULL array
        return;
    }
    array_make_space(array, 0);
    array->data[0] = elem;
}

//inserts elem on last position
void array_insert_last(Array *array, void *elem) {
    if (array == NULL) { //check for NULL array
        return;
    }
    array_make_space(array, array->size);
    array->data[array->size - 1] = elem; // size already increased by array_make_space
}

//inserts elem after the afterElem; if not found, insert on last position
void array_insert_after(Array *array, void *afterElem, void *elem, unsigned (*compareFunction)(void *, void *)) {
    if (array == NULL) { //check for NULL array
        return;
    }
    int position = array_search(array, afterElem, compareFunction);
    if (position == -1) {
        position = array->size - 1;
    }
    array_make_space(array, position + 1);
    array->data[position + 1] = elem;
}

//removes first element
void* array_remove_first(Array *array) {
    void *elem;
    if (array == NULL) { //check for NULL array
        elem = NULL;
    }
    if (array->size > 0) {
        elem = array->data[0];
        array_delete_space(array, 0);
    }
    return elem;
}

//removes last element
void* array_remove_last(Array *array) {
    void *elem = NULL;
    if (array == NULL) { //check for NULL array
        elem = NULL;
    }
    if (array->size > 0) {
        void *elem = array->data[array->size - 1];
        array_delete_space(array, array->size);
    }
    return elem;
}

//removes first occurrence of element elem
void array_remove_elem(Array *array, void *elem, unsigned (*compareFunction)(void *, void *)) {
    if (array == NULL) { //check for NULL array
        return;
    }
    int position = array_search(array, elem, compareFunction);
    if (position != -1) {
        array_delete_space(array, position);
    }
}

//removes all occurrences of element elem
void array_remove_all_elem(Array *array, void *elem, unsigned (*compareFunction)(void *, void *)) {
    if (array == NULL) { //check for NULL array
        return;
    }
    int i = 0;
    while (i < array->size) {
        if (compareFunction(array->data[i], elem) == 1) {
            array_delete_space(array, i);
        } else {
            i++;
        }
    }
}

//removes all elements
void array_remove_all(Array *array) {
    if (array == NULL) { //check for NULL array
        return;
    }
    while (array->size > 0) {
        array_delete_space(array, array->size - 1);
    }
}

//apply applyFunction on each element
void array_iterate(Array *array, void (*applyFunction)(void *)) {
    if (array == NULL) { //check for NULL array
        return;
    }
    for (int i = 0; i < array->size; i++) {
        applyFunction(array->data[i]);
    }
}

//creates a queue
Queue *queue_new() {
    return NULL;
}

//deletes a queue
void queue_free(Queue *queue) {

}

//searches for elem and returns 1 if it's found or 0 otherwise
int queue_search(Queue *queue, void *elem, unsigned (*compareFunction)(void *, void *)) {
    return 0;
}

//enqueue element
void queue_enqueue(Queue *queue, void *elem) {

}

//dequeue element
void *queue_dequeue(Queue *queue) {
    return NULL;
}

//removes all elements
void queue_remove_all(Queue *queue) {

}

//apply applyFunction on each element
void queue_iterate(Queue *queue, void (*applyFunction)(void *)) {

}

//creates a stack
Stack *stack_new() {
    Stack *stack = malloc(sizeof(Stack));
    stack->array = array_new(1);
    stack->top = 0;
    return stack;

}

//deletes a stack
void stack_free(Stack *stack) {
    array_free(stack->array);
    free(stack);
}

//searches for elem and returns 1 if it's found or 0 otherwise
int stack_search(Stack *stack, void *elem, unsigned (*compareFunction)(void *, void *)) {
    return 0;
}

//push element
void stack_push(Stack *stack, void *elem) {
   array_insert_last(stack->array,elem);
   stack->top++;
}

//pop element
void *stack_pop(Stack *stack) {
    stack->top--;
    return array_remove_last(stack->array);
}

//removes all elements
void stack_remove_all(Stack *stack) {

}

//apply applyFunction on each element
void stack_iterate(Stack *stack, void (*applyFunction)(void *)) {
    array_iterate(stack->array,applyFunction);
}





//ListDL functions

//creates an empty list
ListDL *listDL_new() {
    ListDl *list = (ListDL*) malloc(sizeof(ListDL));
    list->first = NULL;
    list->last = NULL;
    return list;
}

//deletes a list and free memory
void listDL_free(ListDL *list) {
    if(list == NULL) return NULL;
    else
    {
        NodeDL *node = list->first;
        node = list->first;
        while(node != NULL)
        {
            NodeDL *nxt = node;
            free(node);
            nxt = nxt->next;
        }
    free(list);
    }
}

//searches for elem and returns 1 if it is found, 0 otherwise
unsigned listDL_search(ListDL *list, void *elem, unsigned (*compareFunction)(void *, void *)) {
    return 0;
}

//inserts elem on first position
void listDL_insert_first(ListDL *list, void *elem) {

}

//inserts elem on last position
void listDL_insert_last(ListDL *list, void *elem) {

}

//inserts elem after the afterElem; if not found, insert on last position
void listDL_insert_after(ListDL *list, void *afterElem, void *elem, unsigned (*compareFunction)(void *, void *)) {
    NodeDL *node = list->first;
    NodeDL *insert;
    insert->key = *elem;
    if(list->first = NULL) break;
    else
    {
        while (node != NULL)
        {
            if (compareFunction(node->key, *elem) == 1)
            {
                NodeDL *node2 = node->next;
                node->next = insert;
                insert->prev = node;
                insert->next = node2;
                node2->prev = insert;
            }
            node = node->next;
        }
    }
}

//removes first element
void listDL_remove_first(ListDL *list) {

}

//removes last element
void listDL_remove_last(ListDL *list) {

}

//removes first occurrence of element elem
void listDL_remove_elem(ListDL *list, void *elem, unsigned (*compareFunction)(void *, void *)) {

}

//removes all occurrences of element elem
void listDL_remove_all_elem(ListDL *list, void *elem, unsigned (*compareFunction)(void *, void *)) {

}

//removes all elements
void listDL_remove_all(ListDL *list) {

}

//apply applyFunction on each element
void listDL_iterate(ListDL *list, void (*applyFunction)(void *)) {

}
