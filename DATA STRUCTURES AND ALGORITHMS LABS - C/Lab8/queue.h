#ifndef SDA_UTIL_QUEUE_H
#define SDA_UTIL_QUEUE_H
#include "listSL.h"
typedef struct {
    ListSL *list;
} Queue;

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

//get first element without removing it
void *queue_peek(Queue *queue);

//removes all elements
void queue_remove_all(Queue *queue);

//apply applyFunction on each element
void queue_iterate(Queue *queue, void (*applyFunction)(void *));

#endif //SDA_UTIL_QUEUE_H
