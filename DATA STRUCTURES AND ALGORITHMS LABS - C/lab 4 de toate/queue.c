#include "queue.h"
#include <stdlib.h>

//creates a queue
Queue *queue_new() {
    Queue *queue = (Queue*)malloc(sizeof(Queue));
    if (queue == NULL) {
        return NULL;    //cannot alloc memory
    }
    queue->list = listSL_new();
    if (queue->list == NULL) {
        return NULL;    //cannot initialize list
    }
    return queue;
}

//deletes a queue
void queue_free(Queue *queue) {
    if (queue == NULL) {    //check for NULL parameter
        return;
    }
    listSL_free(queue->list);
    free(queue);
}

//searches for elem and returns 1 if it's found or 0 otherwise
int queue_search(Queue *queue, void *elem, unsigned (*compareFunction)(void *, void *)) {
    if (queue == NULL) {    //check for NULL parameter
        return 0;
    }
    return listSL_search(queue->list, elem, compareFunction);
}

//enqueue element
void queue_enqueue(Queue *queue, void *elem) {
    if (queue == NULL) {    //check for NULL parameter
        return;
    }
    listSL_insert_last(queue->list, elem);
}

//dequeue element
void *queue_dequeue(Queue *queue) {
    if (queue == NULL) {    //check for NULL parameter
        return NULL;
    }
    return listSL_remove_first(queue->list);
}

//get first element
void *queue_peek(Queue *queue) {
    if (queue == NULL) {    //check for NULL parameter
        return NULL;
    }
    return queue->list->first;
}

//removes all elements
void queue_remove_all(Queue *queue) {
    if (queue == NULL) {    //check for NULL parameter
        return;
    }
    listSL_remove_all(queue->list);
}

//apply applyFunction on each element
void queue_iterate(Queue *queue, void (*applyFunction)(void *)) {
    if (queue == NULL) {    //check for NULL parameter
        return;
    }
    listSL_iterate(queue->list, applyFunction);
}