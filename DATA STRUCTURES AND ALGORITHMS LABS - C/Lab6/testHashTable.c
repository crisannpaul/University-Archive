#include "testHashTable.h"
#include "hashTable.h"
#include <stdlib.h>
#include <stdio.h>
static unsigned hashInt(void *key) {
    int *p = (int *)key;
    return *p;
}
static unsigned compareUnsigned(void *a, void *b) {
    return *(unsigned *)a == *(unsigned *)b;
}
void test_hashTable() {
    HashTable *hashTable = hashTable_new(30);
    unsigned keys[] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 50, 32};
    unsigned keysCount = sizeof (keys) / sizeof (*keys);
    char **values = malloc(keysCount * sizeof (*values));
    for (int i = 0; i < keysCount; i++) {
        values[i] = malloc(50 * sizeof(*values[i]));
        sprintf(values[i], "Number_%d", keys[i]);
    }
    for(int i = 0; i < keysCount; i++) {
        hashTable_put(hashTable, &keys[i], values[i], hashInt, compareUnsigned);
    }
    unsigned searchedKeys[] = {32,1, 2, 3, 32, 50, 45};
    unsigned searchedKeysCount = sizeof (searchedKeys) / sizeof (*searchedKeys);
    for(int i = 0; i < searchedKeysCount; i++) {

        printf("Finding %d: ", searchedKeys[i]);
        void *value = hashTable_get(hashTable, &keys[i], hashInt, compareUnsigned);
        if (value) {
            printf("%s\n", (char*)value);
        } else {
            printf("Not Found\n");
        }
        printf("Removing %d: \n", searchedKeys[i]);
        hashTable_remove(hashTable,&keys[i],hashInt,compareUnsigned);


    }

    hashTable_free(hashTable);
    for (int i = 0; i < keysCount; i++) {
        free(values[i]);
    }
    free(values);
}
