#ifndef SDA_UTIL_H
#define SDA_UTIL_H
typedef struct NodeSL {
    void *data;
    struct NodeSL *next;
} NodeSL;

typedef struct {
    NodeSL *first;
    NodeSL *last;
} ListSL;

typedef struct {
    unsigned size;      //number of elements
    unsigned capacity;  //max number of elements
    void **data;       //array of pointers
} Array;

typedef struct {

} Queue;

typedef struct {
    Array *array;
    unsigned top;

} Stack;

typedef struct NodeDL {
    void *data
    struct NodeDL *next;
    struct NodeDL *prev;
} NodeDL;

typedef struct {

} ListDL;

//compareFunction is a function which returns 1 if the parameters are equal, 0 otherwise


//ListSL functions

//creates an empty list
ListSL *listSL_new();

//deletes a list and free memory
void listSL_free(ListSL *list);

//searches for elem and returns 1 if it is found, 0 otherwise
unsigned listSL_search(ListSL *list, void *elem, unsigned (*compareFunction)(void *, void *));

//inserts elem on first position
void listSL_insert_first(ListSL *list, void *elem);

//inserts elem on last position
void listSL_insert_last(ListSL *list, void *elem);

//inserts elem after the afterElem; if not found, insert on last position
void listSL_insert_after(ListSL *list, void *afterElem, void *elem, unsigned (*compareFunction)(void *, void *));

//removes first element
void listSL_remove_first(ListSL *list);

//removes last element
void listSL_remove_last(ListSL *list);

//removes first occurrence of element elem
void listSL_remove_elem(ListSL *list, void *elem, unsigned (*compareFunction)(void *, void *));

//removes all occurrences of element elem
void listSL_remove_all_elem(ListSL *list, void *elem, unsigned (*compareFunction)(void *, void *));

//removes all elements
void listSL_remove_all(ListSL *list);

//apply applyFunction on each element
void listSL_iterate(ListSL *list, void (*applyFunction)(void *));



//Array functions
//all insert functions can increase capacity, if necessary

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




// Queue functions

//creates a queue
Queue *queue_new();

//deletes a queue
void queue_free(Queue *queue);

//searches for elem and returns 1 if it's found or 0 otherwise
int queue_search(Queue *queue, void *elem, unsigned (*compareFunction)(void *, void *));

//enqueue element
void queue_enqueue(Queue *queue, void *elem);

//dequeue element
void *queue_dequeue(Queue *queue);

//removes all elements
void queue_remove_all(Queue *queue);

//apply applyFunction on each element
void queue_iterate(Queue *queue, void (*applyFunction)(void *));





// Stack functions

//creates a stack
Stack *stack_new();

//deletes a stack
void stack_free(Stack *stack);

//searches for elem and returns 1 if it's found or 0 otherwise
int stack_search(Stack *stack, void *elem, unsigned (*compareFunction)(void *, void *));

//push element
void stack_push(Stack *stack, void *elem);

//pop element
void *stack_pop(Stack *stack);

//removes all elements
void stack_remove_all(Stack *stack);

//apply applyFunction on each element
void stack_iterate(Stack *stack, void (*applyFunction)(void *));





//ListDL functions

//creates an empty list
ListDL *listDL_new();

//deletes a list and free memory
void listDL_free(ListDL *list);

//searches for elem and returns 1 if it is found, 0 otherwise
unsigned listDL_search(ListDL *list, void *elem, unsigned (*compareFunction)(void *, void *));

//inserts elem on first position
void listDL_insert_first(ListDL *list, void *elem);

//inserts elem on last position
void listDL_insert_last(ListDL *list, void *elem);

//inserts elem after the afterElem; if not found, insert on last position
void listDL_insert_after(ListDL *list, void *afterElem, void *elem, unsigned (*compareFunction)(void *, void *));

//removes first element
void listDL_remove_first(ListDL *list);

//removes last element
void listDL_remove_last(ListDL *list);

//removes first occurrence of element elem
void listDL_remove_elem(ListDL *list, void *elem, unsigned (*compareFunction)(void *, void *));

//removes all occurrences of element elem
void listDL_remove_all_elem(ListDL *list, void *elem, unsigned (*compareFunction)(void *, void *));

//removes all elements
void listDL_remove_all(ListDL *list);

//apply applyFunction on each element
void listDL_iterate(ListDL *list, void (*applyFunction)(void *));

#endif //SDA_UTIL_H
