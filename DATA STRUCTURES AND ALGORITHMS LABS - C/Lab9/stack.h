#ifndef SDA_UTIL_STACK_H
#define SDA_UTIL_STACK_H
#include "array.h"
typedef struct {
    Array *array;
} Stack;

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

//get top element without removing it
void *stack_peek(Stack *stack);

//removes all elements
void stack_remove_all(Stack *stack);

//apply applyFunction on each element
void stack_iterate(Stack *stack, void (*applyFunction)(void *));

#endif //SDA_UTIL_STACK_H
