#ifndef SDA_UTIL_LISTDL_H
#define SDA_UTIL_LISTDL_H
typedef struct NodeDL {
    void *data;
    struct NodeDL *next;
    struct NodeDL *prev;
} NodeDL;

typedef struct {
    NodeDL *first;
    NodeDL *last;
} ListDL;

//ListDL functions

//creates an empty list
ListDL *listDL_new();

//deletes a list and free memory
void listDL_free(ListDL *list);

//searches for elem and returns element if it is found, NULL otherwise
void* listDL_search(ListDL *list, void *elem, unsigned (*compareFunction)(void *, void *));

//inserts elem on first position
void listDL_insert_first(ListDL *list, void *elem);

//inserts elem on last position
void listDL_insert_last(ListDL *list, void *elem);

//inserts elem after the afterElem; if not found, insert on last position
void listDL_insert_after(ListDL *list, void *afterElem, void *elem, unsigned (*compareFunction)(void *, void *));

//removes first element
void *listDL_remove_first(ListDL *list);

//removes last element
void *listDL_remove_last(ListDL *list);

//removes first occurrence of element elem
void listDL_remove_elem(ListDL *list, void *elem, unsigned (*compareFunction)(void *, void *));

//removes all occurrences of element elem
void listDL_remove_all_elem(ListDL *list, void *elem, unsigned (*compareFunction)(void *, void *));

//removes all elements
void listDL_remove_all(ListDL *list);

//apply applyFunction on each element
void listDL_iterate(ListDL *list, void (*applyFunction)(void *));

//apply applyFunction on each element
void listDL_iterate_backward(ListDL *list, void (*applyFunction)(void *));

#endif //SDA_UTIL_LISTDL_H
