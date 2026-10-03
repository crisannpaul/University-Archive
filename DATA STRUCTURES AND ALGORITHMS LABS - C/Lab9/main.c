#include <stdio.h>
#include "stack.h"
#include "array.h"
#include "queue.h"
#include <stdlib.h>
#include "listSL.h"
#include <math.h>
typedef  struct Nod{
    int val;
    struct Nod *next;
}Nod;
typedef struct nodSursaa{
    int nod;
    int timpDescoperit;
    int timpProcesat;
}nodSursaa;
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
    List *list = malloc(sizeof(List));
    if (list == NULL) {
        return NULL;
    }
    list->first = NULL;
    list->last = NULL;
    return list;
}
void list_insert_first(List *list, int elem) {
    if (list == NULL) {
        return;
    }
    Nod *newNode = malloc(sizeof(Nod));
    newNode->next = NULL;
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
void  dfs_list_recur_time(ListAdiac *list,nodSursaa nodS,int *viz,int nrNod,int *timp)
{
    (*timp)++;
    nodS.timpDescoperit = *timp;

    for(int j = nrNod - 1; j >= 0; j--) // in functie de cum alegem sa parcurgem lista asa se v-a parcurge recursiv toate nodurile
    {
        if(( list_search(list->nodes[nodS.nod],j,CompInt) == 1) && (viz[j] == 0))
        {
            viz[j] = 1;
            nodSursaa vecin;
            vecin.nod = j;
            dfs_list_recur_time(list,vecin,viz,nrNod, timp);
            (*timp)++;
        }
    }
        nodS.timpProcesat = *timp+1;

    printf("\n %d cu timpulDescoperit = %d si TimpulProcesat = %d",nodS.nod,nodS.timpDescoperit,nodS.timpProcesat);

}


void  dfs_list_recur(ListAdiac *list, int nodSursa,int *viz,int nrNod)
{
    printf("%d ",nodSursa);
    for(int j = 0 ; j < nrNod; j++)
    {
        if((list_search(list->nodes[nodSursa],j,CompInt) == 1) && (viz[j] == 0))
        {
            viz[j] = 1;
            dfs_list_recur(list,j,viz,nrNod);

        }
    }

}

void dfs_list(ListAdiac *list,int nodSursa)
{
    int nrNod = list->nrNoduri;
    int *viz  = calloc(nrNod,sizeof (int));
    int *noduri  = malloc(nrNod * sizeof (int));
    for(int i = 0; i < nrNod; i++)
        noduri[i]=i;
    for(int i = 0; i < nrNod; i++)
        viz[i] = 0;
    Stack *stiva = stack_new();

    stack_push(stiva,&noduri[nodSursa]);

    viz[nodSursa] = 1;
    while(stiva->array->size != 0)
    {
        int nod = *(int*) stack_pop(stiva);

        printf("%d ",nod);
        for(int j = 0 ; j < nrNod; j++)
        {
            if(( list_search(list->nodes[nod],j,CompInt) == 1) && (viz[j] == 0))
            {
                stack_push(stiva,&noduri[j]);
                viz[j] = 1;
            }
        }
    }
    stack_free(stiva);
    free(noduri);
    free(viz);

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

void dfs_mat(int **mat, int nrNod,int nodSursa)
{
    int *viz  = calloc(nrNod,sizeof (int));
    int *noduri  = malloc(nrNod * sizeof (int));
    for(int i = 0; i < nrNod; i++)
        noduri[i] = i;


    Stack *stiva = stack_new();
    stack_push(stiva,&noduri[nodSursa]);
    viz[nodSursa] = 1;

    while(stiva->array->size != 0)
    {
        int nod = *(int*)stack_pop(stiva);

        printf("%d ",nod);
        for(int j = 0 ; j < nrNod; j++)
        {
            if((mat[nod][j] == 1) && (viz[j] == 0))
            {
                stack_push(stiva,&noduri[j]);
                viz[j] = 1;
            }
        }
    }
    stack_free(stiva);
    free(noduri);
    free(viz);
}

int main() {
    int nrNod;
    int Start;
    int **mat = citire_mat(&nrNod,"graf.in");
    printf("Introduceti nod start : ");
    scanf("%d",&Start);
    printf("\nNoduri cu matrice de adiacenta:\n");
    dfs_mat(mat,nrNod,Start);
    printf("\nNoduri cautate in lista de adiacenta\n");
    ListAdiac *lista = Citire_listAdiac("graf.in");
    dfs_list(lista, Start);
    printf("\nNoduri cautate in lista de adiacenta recurent\n");
    int *viz = calloc(nrNod, sizeof (int));
    dfs_list_recur(lista, Start, viz, nrNod);
    printf("\nNoduri cautate in lista de adiacenta recurent cu timp\n");
    nodSursaa start;
    start.nod = Start;
    int time = 0;
    for(int i = 0; i < nrNod; i++)
        viz[i] = 0;
    dfs_list_recur_time(lista, start, viz, nrNod, &time);

    return 0;
}
