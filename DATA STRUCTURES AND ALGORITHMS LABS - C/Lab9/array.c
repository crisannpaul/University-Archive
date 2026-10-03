#include "array.h"
#include <stdlib.h>
//all insert functions can increase capacity, if necessary

//creates an array with max capacity elements
Array *array_new(unsigned capacity) {
    if (capacity <= 0) { //check for invalid capacity
        return NULL;
    }
    Array *array = malloc(sizeof(Array));
    if (array == NULL) {
        return NULL; //cannot allocate memory
    }
    array->size = 0; //initialize fields
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
    if (position < 0) {
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
    if (array == NULL) { //check for NULL array
        return NULL;
    }
    if (array->size > 0) {
        void *elem = array->data[0];
        array_delete_space(array, 0);
        return elem;
    }
    return NULL;
}

//removes last element
void* array_remove_last(Array *array) {
    if (array == NULL) { //check for NULL array
        return NULL;
    }
    if (array->size > 0) {
        void *elem = array->data[array->size - 1];
        array_delete_space(array, array->size - 1);
        return elem;
    }
    return NULL;
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
