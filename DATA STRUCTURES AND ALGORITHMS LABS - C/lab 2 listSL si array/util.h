#ifndef SDA_UTIL_H
#define SDA_UTIL_H
typedef struct Node{
void *data;
struct Node *next;
} Node;

typedef struct {
struct Node *first;
struct Node *last;
} List;

typedef struct {
    void **data;
    unsigned size;
    unsigned capacity;
} Array;

//compareFunction is a function which returns 1 if the parameters are equal, 0 otherwise


//List functions

//creates an empty list
List *list_new();

//deletes a list and free memory
void list_free(List *list);

//searches for elem and returns 1 if it is found, 0 otherwise
unsigned list_search(List *list, void *elem, unsigned (*compareFunction)(void *, void *));

//inserts elem on first position
void list_insert_first(List *list, void *elem);

//inserts elem on last position
void list_insert_last(List *list, void *elem);

//inserts elem after the afterElem
void list_insert_after(List *list, void *afterElem, void *elem, unsigned (*compareFunction)(void *, void *));

//removes first element
void list_remove_first(List *list);

//removes last element
void list_remove_last(List *list);

//removes first occurrence of element elem
void list_remove_elem(List *list, void *elem, unsigned (*compareFunction)(void *, void *));

//removes all occurrences of element elem
void list_remove_all_elem(List *list, void *elem, unsigned (*compareFunction)(void *, void *));

//removes all elements
void list_remove_all(List *list);

//apply applyFunction on each element
void list_iterate(List *list, void (*applyFunction)(void *));



//Array functions
//all insert functions can increase capacity, if necessary

//creates an array with max capacity elements
Array *array_new(unsigned capacity);

//deletes an array
void array_free(Array *array);

//returns element at position in array
void *array_get_at(Array *array, unsigned position);

//searches for elem and returns position of elem in array or -1 if not found
int array_search(Array *array, void *elem, unsigned (*compareFunction)(void *, void *));

//inserts elem on first position
void array_insert_first(Array *array, void *elem);

//inserts elem on last position
void array_insert_last(Array *array, void *elem);

//inserts elem after the afterElem
void array_insert_after(Array *array, void *afterElem, void *elem, unsigned (*compareFunction)(void *, void *));

//removes first element
void array_remove_first(Array *array);

//removes last element
void array_remove_last(Array *array);

//removes first occurrence of element elem
void array_remove_elem(Array *array, void *elem, unsigned (*compareFunction)(void *, void *));

//removes all occurrences of element elem
void array_remove_all_elem(Array *array, void *elem, unsigned (*compareFunction)(void *, void *));

//removes all elements
void array_remove_all(Array *array);

//apply applyFunction on each element
void array_iterate(Array *array, void (*applyFunction)(void *));


#endif //SDA_UTIL_H
