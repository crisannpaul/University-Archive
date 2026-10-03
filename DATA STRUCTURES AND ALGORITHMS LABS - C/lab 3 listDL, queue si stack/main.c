#include <stdio.h>
#include "util.h"

void printInt(void *x) {
    printf("%d ", *(int *) x);
}

unsigned compareInt(void *a, void *b) {
    return *(int *) a == *(int *) b;
}

void helper_listSL_insert(void(*insert_function)(ListSL *, void *)) {
    int values[] = {0, 1, 2, 3};
    int size = sizeof(values) / sizeof(int);
    ListSL *list = listSL_new();
    for (int i = 0; i < size; i++) {
        printf("Inserting %d: ", values[i]);
        insert_function(list, &values[i]);
        listSL_iterate(list, printInt);
        printf("\n");
    }
    listSL_free(list);
}

void check_listSL_insert_first() {
    printf("check_listSL_insert_first:\n");
    helper_listSL_insert(listSL_insert_first);
    printf("\n");
}

void check_listSL_insert_last() {
    printf("check_listSL_insert_last:\n");
    helper_listSL_insert(listSL_insert_last);
    printf("\n");
}

void check_listSL_insert_after() {
    printf("check_listSL_insert_after:\n");
    int insertedValues[] = {0, 1, 2, 3, 4, 5};
    int insertedAfters[] = {0, 0, 1, 2, 1, 6};
    ListSL *list = listSL_new();

    printf("Initial list: ");
    listSL_iterate(list, printInt);
    printf("\n");

    for (int i = 0; i < sizeof(insertedValues) / sizeof(int); i++) {
        printf("Inserting %d after %d: ", insertedValues[i], insertedAfters[i]);
        listSL_insert_after(list, &insertedAfters[i], &insertedValues[i], compareInt);
        listSL_iterate(list, printInt);
        printf("\n");
    }
    listSL_free(list);
    printf("\n");
}

void helper_listSL_remove(void(*remove_function)(ListSL *)) {
    int values[] = {0, 1, 2, 3};
    int size = sizeof(values) / sizeof(int);
    ListSL *list = listSL_new();
    printf("Initial list: ");
    for (int i = 0; i < size; i++) {
        listSL_insert_last(list, &values[i]);
    }
    listSL_iterate(list, printInt);
    printf("\n");

    for (int i = 0; i < size; i++) {
        printf("Remove : ");
        remove_function(list);
        listSL_iterate(list, printInt);
        printf("\n");
    }
    printf("Inserting 1 : ");
    listSL_insert_last(list, &values[1]);
    listSL_iterate(list, printInt);
    printf("\n");

    listSL_free(list);
}

void check_listSL_remove_first() {
    printf("check_listSL_remove_first:\n");
    helper_listSL_remove(listSL_remove_first);
    printf("\n");
}

void check_listSL_remove_last() {
    printf("check_listSL_remove_last:\n");
    helper_listSL_remove(listSL_remove_last);
    printf("\n");
}

void helper_listSL_remove_elem(int *values, int size, int *deleteValues, int size2,
                               void (*remove_function)(ListSL *, void *, unsigned (*)(void *, void *))) {
    ListSL *list = listSL_new();
    printf("Initial list: ");
    for (int i = 0; i < size; i++) {
        listSL_insert_last(list, &values[i]);
    }
    listSL_iterate(list, printInt);
    printf("\n");

    for (int i = 0; i < size2; i++) {
        printf("Remove %d: ", deleteValues[i]);
        remove_function(list, &deleteValues[i], compareInt);
        listSL_iterate(list, printInt);
        printf("\n");
    }
    printf("Inserting 1 : ");
    listSL_insert_first(list, &values[1]);
    listSL_iterate(list, printInt);
    printf("\n");

    listSL_free(list);

}

void check_listSL_remove_elem() {
    printf("check_listSL_remove_elem:\n");
    int arr[] = {0, 1, 2, 3, 3, 2, 1, 0};
    int deleted[] = {0, 0, 1, 1, 2, 2, 4, 3, 3};
    helper_listSL_remove_elem(arr, sizeof(arr) / sizeof(int), deleted, sizeof(deleted) / sizeof(int),
                              listSL_remove_elem);
    printf("\n");
}

void check_listSL_remove_all_elem() {
    printf("check_listSL_remove_all_elem:\n");
    int arr[] = {0, 1, 2, 3, 3, 2, 1, 0};
    int deleted[] = {0, 1, 2, 4, 3};
    helper_listSL_remove_elem(arr, sizeof(arr) / sizeof(int), deleted, sizeof(deleted) / sizeof(int),
                              listSL_remove_all_elem);
    printf("\n");
}

void check_listSL_remove_all() {
    printf("check_listSL_remove_all:\n");
    int arr[] = {0, 1, 2, 3, 3, 2, 1, 0};
    ListSL *list = listSL_new();
    printf("Initial list: ");
    for (int i = 0; i < sizeof(arr) / sizeof(int); i++) {
        listSL_insert_first(list, &arr[i]);
    }
    listSL_iterate(list, printInt);
    printf("\n");

    printf("Remove all: ");
    listSL_remove_all(list);
    listSL_iterate(list, printInt);
    printf("\n");

    printf("Inserting 1 : ");
    listSL_insert_first(list, &arr[1]);
    listSL_iterate(list, printInt);
    printf("\n");

    listSL_free(list);
    printf("\n");
}

void helper_array_insert(void(*insert_function)(Array *, void *)) {
    int values[] = {0, 1, 2, 3};
    int size = sizeof(values) / sizeof(int);
    Array *array = array_new(2);
    for (int i = 0; i < size; i++) {
        printf("Inserting %d: ", values[i]);
        insert_function(array, &values[i]);
        array_iterate(array, printInt);
        printf("\n");
    }
    array_free(array);
}

void check_array_insert_first() {
    printf("check_array_insert_first:\n");
    helper_array_insert(array_insert_first);
    printf("\n");
}

void check_array_insert_last() {
    printf("check_array_insert_last:\n");
    helper_array_insert(array_insert_last);
    printf("\n");
}

void check_array_insert_after() {
    printf("check_array_insert_after:\n");
    int insertedValues[] = {0, 1, 2, 3, 4, 5};
    int insertedAfters[] = {0, 0, 1, 2, 1, 6};
    Array *array = array_new(2);

    printf("Initial array: ");
    array_iterate(array, printInt);
    printf("\n");

    for (int i = 0; i < sizeof(insertedValues) / sizeof(int); i++) {
        printf("Inserting %d after %d: ", insertedValues[i], insertedAfters[i]);
        array_insert_after(array, &insertedAfters[i], &insertedValues[i], compareInt);
        array_iterate(array, printInt);
        printf("\n");
    }
    array_free(array);
    printf("\n");
}

void helper_array_remove(void(*remove_function)(Array *)) {
    int values[] = {0, 1, 2, 3};
    int size = sizeof(values) / sizeof(int);
    Array *array = array_new(2);
    printf("Initial array: ");
    for (int i = 0; i < size; i++) {
        array_insert_last(array, &values[i]);
    }
    array_iterate(array, printInt);
    printf("\n");

    for (int i = 0; i < size; i++) {
        printf("Remove : ");
        remove_function(array);
        array_iterate(array, printInt);
        printf("\n");
    }
    printf("Inserting 1 : ");
    array_insert_last(array, &values[1]);
    array_iterate(array, printInt);
    printf("\n");

    array_free(array);
}

void check_array_remove_first() {
    printf("check_array_remove_first:\n");
    helper_array_remove(array_remove_first);
    printf("\n");
}

void check_array_remove_last() {
    printf("check_array_remove_last:\n");
    helper_array_remove(array_remove_last);
    printf("\n");
}

void helper_array_remove_elem(int *values, int size, int *deleteValues, int size2,
                              void (*remove_function)(Array *, void *, unsigned (*)(void *, void *))) {
    Array *array = array_new(2);
    printf("Initial array: ");
    for (int i = 0; i < size; i++) {
        array_insert_last(array, &values[i]);
    }
    array_iterate(array, printInt);
    printf("\n");

    for (int i = 0; i < size2; i++) {
        printf("Remove %d: ", deleteValues[i]);
        remove_function(array, &deleteValues[i], compareInt);
        array_iterate(array, printInt);
        printf("\n");
    }
    printf("Inserting 1 : ");
    array_insert_first(array, &values[1]);
    array_iterate(array, printInt);
    printf("\n");

    array_free(array);

}

void check_array_remove_elem() {
    printf("check_array_remove_elem:\n");
    int arr[] = {0, 1, 2, 3, 3, 2, 1, 0};
    int deleted[] = {0, 0, 1, 1, 2, 2, 4, 3, 3};
    helper_array_remove_elem(arr, sizeof(arr) / sizeof(int), deleted, sizeof(deleted) / sizeof(int), array_remove_elem);
    printf("\n");
}

void check_array_remove_all_elem() {
    printf("check_array_remove_all_elem:\n");
    int arr[] = {0, 1, 2, 3, 3, 2, 1, 0};
    int deleted[] = {0, 1, 2, 4, 3};
    helper_array_remove_elem(arr, sizeof(arr) / sizeof(int), deleted, sizeof(deleted) / sizeof(int),
                             array_remove_all_elem);
    printf("\n");
}

void check_array_remove_all() {
    printf("check_array_remove_all:\n");
    int arr[] = {0, 1, 2, 3, 3, 2, 1, 0};
    Array *array = array_new(2);
    printf("Initial array: ");
    for (int i = 0; i < sizeof(arr) / sizeof(int); i++) {
        array_insert_last(array, &arr[i]);
    }
    array_iterate(array, printInt);
    printf("\n");

    printf("Remove all: ");
    array_remove_all(array);
    array_iterate(array, printInt);
    printf("\n");

    printf("Inserting 1 : ");
    array_insert_first(array, &arr[1]);
    array_iterate(array, printInt);
    printf("\n");

    array_free(array);
    printf("\n");
}

void check_listSL_functions() {
//    check_listSL_insert_first();
//    check_listSL_insert_last();
//    check_listSL_insert_after();
//    check_listSL_remove_first();
//    check_listSL_remove_last();
//    check_listSL_remove_elem();
//    check_listSL_remove_all_elem();
//    check_listSL_remove_all();
}
void check_array_functions() {
//    check_array_insert_first();
//    check_array_insert_last();
//    check_array_insert_after();
//    check_array_remove_first();
//    check_array_remove_last();
//    check_array_remove_elem();
//    check_array_remove_all_elem();
//    check_array_remove_all();
}

int main() {
    check_listSL_functions();
    check_array_functions();


    return 0;
}
