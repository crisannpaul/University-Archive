#include "util.h"
#include <stdio.h>
#include <stdlib.h>

//creates an empty list
List *list_new() {
    List *list = (List *) malloc(sizeof(List));
    list->first = NULL;
    list->last = NULL;
    return list;
}

//deletes a list and free memory
void list_free(List *list) {
    list_remove_all(list);
    free(list);
}

//searches for elem and returns 1 if it is found, 0 otherwise
unsigned list_search(List *list, void *elem, unsigned (*compareFunction)(void *, void *)) {
    Node *p;
    p = list->first;
    while (p != NULL) {
       if(compareFunction(p->data,elem) == 1)
           return 1;
        p = p->next;
    }
    return 0;
}

//inserts elem on first position
void list_insert_first(List *list, void *elem) {
    Node *new_node = (Node *) malloc(sizeof(Node));
    new_node->data = elem;
    new_node->next = NULL;
    if (list->first != NULL)
        new_node->next = list->first;
    else
        list->last = new_node;
    list->first = new_node;


}

//inserts elem on last position
void list_insert_last(List *list, void *elem) {
    Node *new_node = (Node *) malloc(sizeof(Node));
    new_node->data = elem;
    new_node->next = NULL;
    if (list->first != NULL)
        list->last->next = new_node;
    else
        list->first = new_node;
    list->last = new_node;

}

//inserts elem after the afterElem
void list_insert_after(List *list, void *afterElem, void *elem, unsigned (*compareFunction)(void *, void *)) {
    Node *p = list->first;
    if(p!=NULL)
    {
        while(p->next!= NULL && compareFunction(p->data,afterElem) != 1)
            p = p->next;
        if(compareFunction(p->data,afterElem) == 1)
        {
            Node * newNode = (Node*) malloc(sizeof (Node));
            newNode->data = elem;
            if(p->next == NULL)
            {
                newNode->next = NULL;
                p->next = newNode;
                list->last = newNode;
            }
            else
            {
                newNode->next = p->next;
                p->next = newNode;
            }
        }
    }
}

//removes first element
void list_remove_first(List *list) {
   Node *p = list->first;
   if(list->first == list->last)
       free(list->first);
    if (list->first != NULL)
        list->first = list->first->next;
    free(p);

}

//removes last element
void list_remove_last(List *list) {
    Node *p = list->first;
    if(list->last == list->first)
    {
        free(list->last);
        return;
    }
    if (list->first != NULL )
    {
        while(p->next != list->last)
            p = p->next;
        p->next = NULL;
        free(list->last);
        list->last = p;
    }
}

//removes first occurrence of element elem
void list_remove_elem(List *list, void *elem, unsigned (*compareFunction)(void *, void *)) {
    Node *p = list->first;
    if(list->first == list->last && compareFunction(list->first->data,elem)==1)
    {
        free(list->last);
        return;
    }
    if(compareFunction(list->first->data,elem)==1)
    {
        Node *delete = list->first;
        list->first = list->first->next;
        free(delete);
        return;
    }
    if(p!=NULL)
    {
        while(p->next !=NULL && compareFunction(p->next->data,elem)!=1)
            p=p->next;
        if(p->next!=NULL && compareFunction(p->next->data,elem) == 1)
        {
            if(p->next->next != NULL) {
                Node *delete = p->next;
                p->next = p->next->next;
                free(delete);
            }
            else
            { //daca numarul pe care vrem sa il stergem este ultimul din lista
                free(list->last);
                list->last = p->next;
                p->next = NULL;

            }
        }


    }
}

//removes all occurrences of element elem
void list_remove_all_elem(List *list, void *elem, unsigned (*compareFunction)(void *, void *)) {
    Node *p = list->first;
    //printf("%d",list->last);
    if(list->first == list->last && (compareFunction(list->first->data,elem)==1))
    {
        free(list->last);
        return;
    }

    while(p->next!=list->last)
    {

        if(p->next !=NULL && (compareFunction(p->next->data, elem)==1))
        {
            Node *del = p->next;
            p->next = p->next->next;
            free(del);
        }
        else
            p=p->next;


    }
    if(compareFunction(list->first->data, elem)==1)
    {
        Node *delete = list->first;
        list->first = list->first->next;
        free(delete);
    }
    if(compareFunction(list->last->data, elem)==1)
    {
        Node* delete = list->last;
        p->next = NULL;
        list->last = p;
        free(delete);

    }


}

//removes all elements
void list_remove_all(List *list) {

    while(list->first != list->last)
    {
        list_remove_last(list);
    }
  free(list->first);
    list->first = NULL;
    list->last = NULL;
}

//apply applyFunction on each element
void list_iterate(List *list, void (*applyFunction)(void *)) {
    Node *p;
    p = list->first;
    while (p != NULL) {
        applyFunction(p->data);
        p = p->next;
    }
}



//Array functions
//all insert functions can increase capacity, if necessary

//creates an array with max capacity elements
Array *array_new(unsigned capacity) {
    Array *array = (Array*) malloc(sizeof(Array));
    array->size = 0;
    array->capacity = capacity;
    array->data = (void**)malloc(capacity * sizeof(void*));
    return array;
}

//deletes an array
void array_free(Array *array) {
    free(array->data);
    free(array);
}

//returns element at position in array
void *array_get_at(Array *array, unsigned position) {
    return *(int*)array->data[position];

}

//searches for elem and returns position of elem in array or -1 if not found
int array_search(Array *array, void *elem, unsigned (*compareFunction)(void *, void *)) {
     for(int i = 0 ;i < array->size; i++)
     {
         if(compareFunction(array->data[i],elem) == 1)
             return i;

     }
     return -1;
}

//inserts elem on first position
void array_insert_first(Array *array, void *elem) {
    if(array->size == array->capacity)
    {
        array->capacity*=2;
        array->data =(void**)realloc(array->data,array->capacity * sizeof (void*));

    }
    array->size++;
    for(int i = array->size ;i >0; i--)
    {
        array->data[i] = array->data[i-1];
    }
    array->data[0] = elem;
}

//inserts elem on last position
void array_insert_last(Array *array, void *elem) {
    if(array->size == array->capacity)
    {
        array->capacity *= 2;
        array->data = (void**)realloc(array->data,array->capacity * sizeof (void*));
    }

    array->data[array->size] = elem;
    array->size++;

}

//inserts elem after the afterElem
void array_insert_after(Array *array, void *afterElem, void *elem, unsigned (*compareFunction)(void *, void *)) {
    for(int i = 0; i <= array->size; i++)
    {
        if(compareFunction(array->data[i],afterElem)==1)
        {
            if(array->size == array->capacity)
            {
                array->capacity*= 2;
                array->data = (void**)realloc(array->data,array->capacity * sizeof (void*));
            }

            for(int j = array->size; j > i; j--)
            {
                array->data[j] = array->data[j-1];

            }
            array->data[i+1] = elem;
            array->size++;
            return;
        }

    }
}

//removes first element
void array_remove_first(Array *array) {
    for(int i = 0; i< array->size; i++)
    {
        array->data[i] = array->data[i+1];

    }
    array->size--;
}

//removes last element
void array_remove_last(Array *array) {
    if(array->size > 0)
        array->size--;

}

//removes first occurrence of element elem
void array_remove_elem(Array *array, void *elem, unsigned (*compareFunction)(void *, void *)) {
    for(int i = 0; i < array->size; i++)
    {
        if (compareFunction(array->data[i],elem) == 1)
        {
            for(int j = i; j < array->size ; j++)
                array->data[j] = array->data[j+1];
            array->size--;
            break;
        }
    }
}

//removes all occurrences of element elem
void array_remove_all_elem(Array *array, void *elem, unsigned (*compareFunction)(void *, void *)) {
    for(int i = 0; i < array->size; i++)
    {
        if (compareFunction(array->data[i],elem) == 1)
        {
            for(int j = i; j < array->size ; j++)
                array->data[j] = array->data[j+1];
            array->size--;
            i--;
        }
    }
}

//removes all elements
void array_remove_all(Array *array) {
    array->size = -1;
}

//apply applyFunction on each element
void array_iterate(Array *array, void (*applyFunction)(void *)) {
    for(int i = 0; i < array->size; i++)
    {
        applyFunction(array->data[i]);
    }
}