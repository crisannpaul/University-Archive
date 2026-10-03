#include <stdio.h>
#include "util.h"
#include <stdlib.h>
void afisareElem(void *elem){
    int val = *(int*)elem;
    printf("%d ",val);
}
unsigned compareInt(void *elem1, void *elem2)
{
    return *(unsigned*)(elem1) == *(unsigned *)(elem2);
}
unsigned compareFunction(void *elem1, void *elem2)
{
    if(*(int *)(elem1) == *(int *)elem2)
        return 1;
    return 0;
}
int main() {
//    List *list = list_new();
//    int a[]={1, 2, 2};
//    int n =1, m = 5,elem = 2;
//    list_insert_first(list, &a[1]);
//    list_insert_first(list, &a[2]);
//    list_insert_first(list, &a[0]);
//    // int n =4;
//    //printf("%d\n",list_search(list,&n,compareInt));
//    list_insert_after(list,&n,&m,compareFunction);
//    list_iterate(list,afisareElem);
//    //printf("\n");
//    //list_remove_elem(list,&elem,compareFunction);
//    //list_iterate(list,afisareElem);
//    printf("\n");
//    list_remove_all_elem(list,&elem,compareFunction);
//    list_iterate(list,afisareElem);

    Array *v = array_new(2);
    int a[]={1, 2, 3};
    int n =3, m = 5,elem = 1;
    array_insert_last(v, &a[1]);
    array_insert_last(v, &a[2]);
    array_insert_first(v, &a[0]);
    array_insert_last(v, &a[0]);
    array_iterate(v,afisareElem);
    array_insert_after(v,&n,&m,compareFunction);
    printf("\n");
    array_iterate(v,afisareElem);
    array_remove_all_elem(v,&elem,compareFunction);
    printf("\n");
    array_iterate(v,afisareElem);



    return 0;
}
