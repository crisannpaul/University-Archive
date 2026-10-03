#ifndef SDA_UTIL_LISTSL_H
#define SDA_UTIL_LISTSL_H

typedef struct NodeSL {
    void *data;
    struct NodeSL *next;
} NodeSL;

typedef struct {
    NodeSL *first;
    NodeSL *last;
} ListSL;

//compareFunction is a function which returns 1 if the parameters are equal, 0 otherwise

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
void* listSL_remove_first(ListSL *list);

//removes last element
void* listSL_remove_last(ListSL *list);

//removes first occurrence of element elem
void listSL_remove_elem(ListSL *list, void *elem, unsigned (*compareFunction)(void *, void *));

//removes all occurrences of element elem
void listSL_remove_all_elem(ListSL *list, void *elem, unsigned (*compareFunction)(void *, void *));

//removes all elements
void listSL_remove_all(ListSL *list);

//apply applyFunction on each element
void listSL_iterate(ListSL *list, void (*applyFunction)(void *));


#endif //SDA_UTIL_LISTSL_H
