#ifndef SDA_UTIL_ARRAY_H
#define SDA_UTIL_ARRAY_H

typedef struct {
    unsigned size;      //number of elements
    unsigned capacity;  //max number of elements
    void **data;       //array of pointers
} Array;

//all insert functions can increase capacity, if necessary
//compareFunction is a function which returns 1 if the parameters are equal, 0 otherwise

//creates an array with max capacity elements
Array *array_new(unsigned capacity);

//deletes an array
void array_free(Array *array);

//returns element at position in array
void *array_get_at(Array *array, unsigned position);

//returns the size of array
unsigned array_get_size(Array *array);

//searches for elem and returns position of elem in array or -1 if not found
int array_search(Array *array, void *elem, unsigned (*compareFunction)(void *, void *));

//inserts elem on first position
void array_insert_first(Array *array, void *elem);

//inserts elem on last position
void array_insert_last(Array *array, void *elem);

//inserts elem after the afterElem; if not found, insert on last position
void array_insert_after(Array *array, void *afterElem, void *elem, unsigned (*compareFunction)(void *, void *));

//removes first element
void* array_remove_first(Array *array);

//removes last element
void* array_remove_last(Array *array);

//removes first occurrence of element elem
void array_remove_elem(Array *array, void *elem, unsigned (*compareFunction)(void *, void *));

//removes all occurrences of element elem
void array_remove_all_elem(Array *array, void *elem, unsigned (*compareFunction)(void *, void *));

//removes all elements
void array_remove_all(Array *array);

//apply applyFunction on each element
void array_iterate(Array *array, void (*applyFunction)(void *));

#endif //SDA_UTIL_ARRAY_H
