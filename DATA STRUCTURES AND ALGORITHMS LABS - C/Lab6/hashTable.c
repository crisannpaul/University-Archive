#include "hashTable.h"
#include <stdlib.h>
#include <stdio.h>
#include "listDL.h"
typedef struct {
void *key;
void *value;
} HashTablePair;

HashTable *hashTable_new(unsigned capacity) {
    HashTable *table = malloc(sizeof(HashTable));
    table->capacity = capacity;
    table->table =calloc(capacity,sizeof (void*));
    return table;
}

void hashTable_free(HashTable *hashTable) {
    for(int i = 0; i < hashTable->capacity; i++)
    {
        if(hashTable->table[i] != NULL)
            listDL_free(hashTable->table[i]);
    }
    printf("Proccess for freeing list - Done!\n");
    free(hashTable->table);
    printf("HashTable-> Table free - Done\n");
    free(hashTable);
    printf("hashtable free - Done\n");

}
unsigned (*compareKeysGlobal)(void *, void *);
static unsigned cautareElem(void *a, void *b)
{
return compareKeysGlobal(((HashTablePair*)a)->key,((HashTablePair*)b)->key);
}
static unsigned hashTable_put_list(HashTable *hashTable, void *key, void *value, unsigned(*hashFunction)(void*),
                                   unsigned (*compareKeys)(void *, void *)){
    unsigned index = hashFunction(key) % hashTable->capacity;
    if(hashTable->table[index] == NULL)
    {

        hashTable->table[index] = listDL_new();// Daca nu am gasit pozitia si nu exista o lista deja creeat inseamna ca nu avem nici un element acolo
                                               // si creeam noi o lista noua unde urmeaza sa punem elementele care colisioneaza

    }
    HashTablePair *Elem = malloc(sizeof (HashTablePair)); // e un struct care contine elemetele dintr-un hash table pentru a le putea verifica daca il in lista
                                                          // de pe o anumita pozitie sau nu;

    Elem->key = key; //creeam un element nou pe care il initializam cu key si valoarea cautata
    Elem->value = value;
    compareKeysGlobal = compareKeys;// atribuim lui compareKeysGlobal functia de comparare din antentul fct
    HashTablePair *found = ( HashTablePair*)listDL_search(hashTable->table[index],Elem,cautareElem);
    if(found){ // Daca am gasit key pentru elemetul pe care il cautam ii punem valoarea dorita;
        found->value = value;
        free(Elem);// eliberam elemetul cautat;
    }
    else// daca nu gasim elementul cu key in lista il adaugam la final (si key si valoarea)
    {
        listDL_insert_last(hashTable->table[index],Elem);
    }

    return 0;
}
//adds (key,value) into hashTable and returns 0 if success, 1 otherwise
//NULL value not allowed
//if key is already in hashTable, value is override
unsigned hashTable_put(HashTable *hashTable, void *key, void *value, unsigned(*hashFunction)(void *),
                       unsigned (*compareKeys)(void *, void *)) {

    return hashTable_put_list(hashTable,key,value,hashFunction,compareKeys);
}

static void *hashTable_get_list(HashTable *hashTable, void *key, unsigned(*hashFunction)(void*),
                                   unsigned (*compareKeys)(void *, void *)){
    unsigned index = hashFunction(key) % hashTable->capacity;
    if(hashTable->table[index] == NULL)
    {
       return NULL;
    }
    HashTablePair *elem = malloc(sizeof(HashTablePair));
    elem->key = key;
    compareKeysGlobal = compareKeys;
    HashTablePair *found = ( HashTablePair*)listDL_search(hashTable->table[index],elem,cautareElem);
    free(elem);
    if(found){
        return found->value;
    }
   return NULL;
}

//retrieves the value for the given key. If key not present, return NULL
void *hashTable_get(HashTable *hashTable, void *key, unsigned(*hashFunction)(void *),
                    unsigned (*compareKeys)(void *, void *)) {
    return hashTable_get_list(hashTable, key, hashFunction, compareKeys);
}

//removes the key(and its corresponding value) and returns the value. If element not present, it returns NULL;
void *hashTable_remove(HashTable *hashTable, void *key, unsigned(*hashFunction)(void *),
                       unsigned (*compareKeys)(void *, void *)) {
    unsigned index = hashFunction(key) % hashTable->capacity;
    if(hashTable->table[index] == NULL)
    {
        return NULL;
    }
    else
    {
        HashTablePair *elem = (HashTablePair*)malloc(sizeof (HashTablePair));
        elem->key = key;
        compareKeysGlobal = compareKeys;
        listDL_remove_elem(hashTable->table[index],elem,cautareElem);

    }

    return NULL;

}
