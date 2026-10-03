#include "stack.h"
#include <stdlib.h>

//creates a stack
Stack *stack_new() {
    Stack *stack = (Stack *) malloc(sizeof(Stack));
    if (stack == NULL) {
        return NULL;    //cannot allocate memory
    }
    stack->array = array_new(2);
    if (stack->array == NULL) {
        return NULL;    //cannot allocate memory
    }
    return stack;
}

//deletes a stack
void stack_free(Stack *stack) {
    if (stack == NULL) {    //check for NULL parameter
        return;
    }
    array_free(stack->array);
    free(stack);
}

//searches for elem and returns 1 if it's found or 0 otherwise
int stack_search(Stack *stack, void *elem, unsigned (*compareFunction)(void *, void *)) {
    if (stack == NULL) {    //check for NULL parameter
        return 0;
    }
    return array_search(stack, elem, compareFunction);
}

//push element
void stack_push(Stack *stack, void *elem) {
    if (stack == NULL) {    //check for NULL parameter
        return;
    }
    array_insert_last(stack->array, elem);
}

//pop element
void *stack_pop(Stack *stack) {
    if (stack == NULL) {    //check for NULL parameter
        return NULL;
    }
    return array_remove_last(stack->array);
}

//get top element without removing it
void *stack_peek(Stack *stack) {
    if (stack == NULL) {    //check for NULL parameter
        return NULL;
    }
    int pos = array_get_size(stack->array);
    return array_get_at(stack->array, pos - 1);
}


//removes all elements
void stack_remove_all(Stack *stack) {
    if (stack == NULL) {    //check for NULL parameter
        return;
    }
    array_remove_all(stack->array);
}

//apply applyFunction on each element
void stack_iterate(Stack *stack, void (*applyFunction)(void *)) {
    if (stack == NULL) {    //check for NULL parameter
        return;
    }
    array_iterate(stack->array, applyFunction);
}
