#include <stdio.h>
#include <stdlib.h>
typedef struct {
    int size;
    int *data;
}Array;
static int counter = 0;
int fibo(int n){

    if(n == 1 || n==2)
        return 1;
    counter++;
    return fibo(n-1)+fibo(n-2);
}
int fibo2(int n)
{
    int *data = calloc(n, sizeof(int));
    data[0] = 1;
    data[1] = 1;
    for(int i = 2; i < n; i++){
        data[i] = data[i -1] + data[i-2];
    }
    int result = data[n-1];
    return result;
}
void suma(Array *monede, int suma)
{   Array comb;
    comb.data = calloc(suma+1,sizeof(int));
    comb.data[0] = 1;
    for(int i = 0; i< monede->size; i++)
    {
        for(int j = 1;j <= suma; j++)
        {
            if(j >= monede->data[i])
                comb.data[j] += comb.data[j - monede->data[i]];

        }
    }
    printf("%d",comb.data[suma]);
}

void sumaMin(Array *monede, int suma)
{   Array Min;
    Min.data = calloc(suma+1,sizeof(int));
    for(int i = 1; i <= suma; i++)
        Min.data[i] = 0x7FFFFFFF;
    for(int i = 0; i< suma+1; i++)
    {
        for(int j = 0; j < monede->size; j++)
        {
            if(monede->data[j] <= i && (Min.data[i - monede->data[j]]+1) < Min.data[i])
                Min.data[i] = Min.data[i - monede->data[j]]+1;

        }
    }
    printf("%d",Min.data[suma]);
}

int main() {
    int n = 9,m = 3;
    int monede2[]={1,3,5};
    Array monede;
    monede.data = monede2;
    monede.size = 3;
    sumaMin(&monede, n);
    return 0;
}
