#include <stdio.h>
#include "queue.h"
#include <stdlib.h>
#include "listSL.h"
#include <math.h>
typedef  struct Nod{
    int val;
    struct Nod *next;
}Nod;
typedef struct {
    Nod *first;
    Nod *last;
} List;
typedef struct ListAdiac
{
    int nrNoduri;
    void **nodes;

}ListAdiac;
List *list_new() {
    List *list = malloc(sizeof(List)); //allocate memory
    if (list == NULL) {
        return NULL; // cannot allocate memory
    }
    list->first = NULL; //initialize fields
    list->last = NULL;
    return list;
}
void list_insert_first(List *list, int elem) {
    if (list == NULL) {
        return; // NULL list
    }
    Nod *newNode = malloc(sizeof(Nod)); //allocate memory
    newNode->next = NULL; //initialize fields
    newNode->val = elem;

    if (list->first == NULL) { //check for empty list
        list->last = newNode; //if empty, first and last node will be this node
    }

    newNode->next = list->first; //insert newNode in list
    list->first = newNode;
    //printf("%d ",list->first->val);
}
int CompInt(int x, int y)
{
    return (x == y);
}
int list_search(List *list,int elem, int(*Compare)(int , int )){
    if (list == NULL) {
        return 0; // NULL list
    }
    Nod *p = list->first;
    while(p != NULL)
    {
        if(Compare(p->val,elem) == 1)
            return 1;
        p = p->next;
    }
    return 0;
}

void afisare (List *list)
{
    Nod *p = list->first;
    while(p!=NULL)
    {
        printf("%d ", p->val);
        p=p->next;
    }
}
ListAdiac *Citire_listAdiac(char *file)
{
    FILE *pf = fopen(file,"r");
    struct ListAdiac *list = malloc(sizeof (ListAdiac));
    fscanf(pf,"%d",&list->nrNoduri);
    list->nodes = calloc(list->nrNoduri,sizeof (void*));
    int x,y;
    while(1)
    {
        if(!feof(pf))
        {
            fscanf(pf,"%d %d",&x,&y);
            if(list->nodes[x] == NULL) {
                list->nodes[x] = list_new();

            }
            list_insert_first(list->nodes[x],y);
            //printf("%d %d = ",x,y);
            //afisare(list->nodes[x]);
           // printf("\n");
        }
        else
            break;
    }
    return list;
}


void bfs_list(ListAdiac *list,int nodSursa)
{
    int nrNod = list->nrNoduri;
    int viz[nrNod];
    int noduri[nrNod];
    for(int i = 0; i < nrNod; i++)
        noduri[i]=i;
    for(int i = 0; i < nrNod; i++)
        viz[i] = 0;
    Queue *que = queue_new();

    queue_enqueue(que,&noduri[nodSursa]);

    viz[nodSursa] = 1;
    while(que->list->first != NULL)
    {
        int nod = *(int*) queue_dequeue(que);

        printf("%d ",nod);
        for(int j = 0 ; j < nrNod; j++)
        {
            if(( list_search(list->nodes[nod],j,CompInt) == 1) && (viz[j] == 0))
            {
                queue_enqueue(que,&noduri[j]);
                viz[j] = 1;
            }
        }
    }
    queue_free(que);
    free(&noduri);
    free(&viz);

}

typedef struct ListaStatica{
    int nrNoduri;
    int *vecini;
    int *nodes;

}ListaStatica;

double CapacitateMax(int x) {
    return x*x;

}

void afisare_vecini(ListaStatica *vector,int index)
{
    int i = vector->nodes[index];
    printf("\nVecinii pentru %d sunt : ", index);
    while(vector->vecini[i]!=-1){
        printf("%d ", vector->vecini[i]);
        i++;
    }
}

ListaStatica *Citire_ListaStatica(char *file)
{
    FILE *pf = fopen(file,"r");
    struct ListaStatica *vector = malloc(sizeof (ListaStatica));
    fscanf(pf,"%d",&vector->nrNoduri);
    vector->nodes = calloc(vector->nrNoduri,sizeof (int));
    vector->vecini = malloc(CapacitateMax(vector->nrNoduri) * sizeof (int));
    for(int i = 0; i < CapacitateMax(vector->nrNoduri); i++)
    {
        vector->vecini[i] = -2;
    }

    int x,y;
    while(feof(pf)==0)
    {
        if(!feof(pf))
        {
            fscanf(pf,"%d %d",&x,&y);

            if(vector->nodes[x] == 0) {

                int index = x * vector->nrNoduri + 1;
                vector->nodes[x] = index;
                while(vector->vecini[index]!= -2)
                    index ++;
                vector->vecini[index] = y;
                vector->vecini[index + 1 ] = -1;

            }
            else {
                int index = vector->nodes[x];
                while (vector->vecini[index] != -1)
                    index++;
                vector->vecini[index] = y;
                vector->vecini[index + 1] = -1;

            }


        }
        else
            break;
    }

    return vector;
    }
int cautare_staticList(int *vector,int poz, int elem)
{

    int index = poz;

    while(vector[index] != -1)
    {
        if(vector[index] == elem)
            return 1;
        index++;
    }
    return 0;
}
void bfs_list_static(ListaStatica *vector,int nodSursa)
{
    int nrNod= vector->nrNoduri;
    int viz[nrNod];
    int noduri[nrNod];
    for(int i = 0; i < nrNod; i++)
        noduri[i]=i;
    for(int i = 0; i < nrNod; i++)
        viz[i] = 0;
    Queue *que = queue_new();

    queue_enqueue(que,&noduri[nodSursa]);

    viz[nodSursa] = 1;
    while(que->list->first != NULL)
    {
        int nod = *(int*) queue_dequeue(que);

        printf("%d ",nod);
        for(int j = 0 ; j < nrNod; j++)
        {
            if(( cautare_staticList(vector->vecini,nod * vector->nrNoduri + 1,j) == 1) && (viz[j] == 0))
            {
                queue_enqueue(que,&noduri[j]);
                viz[j] = 1;
            }
        }
    }
    queue_free(que);
    free(&noduri);
    free(&viz);

}





int** citire_mat(int *nrNod,char *file )
{
    FILE *pf = fopen(file,"r");
    fscanf(pf,"%d",nrNod);

    int **mat = (int**)malloc(*nrNod * sizeof (int*));
    for(int i = 0; i < *nrNod; i++)
        mat[i] = malloc(*nrNod * sizeof (int));
    int x,y;
    while(1)
    {
        if(!feof(pf))
        {
            fscanf(pf,"%d %d",&x,&y);
            mat[x][y]  = 1;
            //printf("%d %d = %d\n",x,y,mat[x][y]);
        }
        else
            break;
    }
return mat;
}

void bfs_mat(int **mat, int nrNod,int nodSursa)
{
    int viz[nrNod];
    int noduri[nrNod];
    for(int i = 0; i < nrNod; i++)
        noduri[i]=i;
    for(int i = 0; i < nrNod; i++)
        viz[i] = 0;
    Queue *que = queue_new();

    queue_enqueue(que,&noduri[nodSursa]);

    viz[nodSursa] = 1;
    while(que->list->first != NULL)
    {
        int nod = *(int*) queue_dequeue(que);

        printf("%d ",nod);
        for(int j = 0 ; j < nrNod; j++)
        {
            if((mat[nod][j] == 1) && (viz[j] == 0))
            {
                queue_enqueue(que,&noduri[j]);
                viz[j] = 1;
            }
        }
    }
    queue_free(que);
    free(&noduri);
    free(&viz);

}

int main() {
    int nrNod;
    int Start;
    int **mat = citire_mat(&nrNod,"graf.in");
    printf("Introduceti nod start : ");
    scanf("%d",&Start);
    printf("\nNoduri cu matrice de adiacenta:\n");
    bfs_mat(mat,nrNod,Start);
    printf("\nNoduri cautate in lista de adiacenta\n");
    ListAdiac *lista = Citire_listAdiac("graf.in");
    bfs_list(lista,Start);
    ListaStatica *vector = Citire_ListaStatica("graf.in");
    //for(int i = 0 ;i < vector->nrNoduri; i++)
      // afisare_vecini(vector,i);
    printf("\nNoduri cautate in lista statica\n");
    bfs_list_static(vector,Start);

    return 0;
}
