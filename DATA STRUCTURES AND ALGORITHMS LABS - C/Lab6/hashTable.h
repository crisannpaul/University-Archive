#ifndef SDA_UTIL_HASHTABLE_H
#define SDA_UTIL_HASHTABLE_H
typedef struct {
int capacity;
void **table;
} HashTable;

//compareKeys returns 1 if the keys are equal, 0 otherwise

HashTable *hashTable_new(unsigned capacity);

void hashTable_free(HashTable *hashTable);

//adds (key,value) into hashTable and returns 0 if success, 1 otherwise
//NULL value not allowed
//if key is already in hashTable, value is override
unsigned hashTable_put(HashTable *hashTable, void *key, void *value, unsigned(*hashFunction)(void *),
                       unsigned (*compareKeys)(void *, void *));

//retrieves the value for the given key. If key not present, return NULL
void *hashTable_get(HashTable *hashTable, void *key, unsigned(*hashFunction)(void *),
                    unsigned (*compareKeys)(void *, void *));

//removes the key(and its corresponding value) and returns the value. If element not present, it returns NULL;
void *hashTable_remove(HashTable *hashTable, void *key, unsigned(*hashFunction)(void *),
                       unsigned (*compareKeys)(void *, void *));


#endif //SDA_UTIL_HASHTABLE_H
