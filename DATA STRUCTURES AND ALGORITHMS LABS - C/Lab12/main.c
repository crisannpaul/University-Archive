#include <stdio.h>
#include <stdlib.h>
void problema1()
{
    int banc[]={1,5,10,50,100,200,500};
    int suma, n= 7;
    printf("suma : ");
    scanf("%d",&suma);

    int nrmin = 0;
   for(int i = n-1; i>= 0 ;i --)
   {
       if(banc[i] <= suma)
       {
           nrmin++;
           suma = suma - banc[i];
           i++;
       }

   }
    printf("\n Nr minim de bancnote: %d",nrmin);

}
typedef struct{
    int start,final;
    char denum[30];
}Activitati;
void problema2()
{
    FILE *in  = fopen("Activ.txt", "r");
    if(in  == NULL)
    {
        printf("cant open");
        return 1;
    }
    int activCount;
    fscanf(in,"%d",&activCount);
    Activitati *activ = calloc(activCount,sizeof (Activitati));
    for(int i = 0; i< activCount; i++)
    {
        fscanf(in,"%s %d %d",activ[i].denum,&activ[i].start,&activ[i].final);
    }
    int MaxActiv = 0;
    Activitati aux;
    for(int i = 0; i< activCount-1; i++)
    {
        for (int j = i+1 ; j < activCount;j++) {
            if(activ[i].final > activ[j].final)
            {
                aux = activ[i];
                activ[i] = activ[j];
                activ[j] = aux;
            }
        }
    }
    Activitati prev;
    printf("%s, %d, %d", activ[0].denum,activ[0].start,activ[0].final);
    prev = activ[0];
    for(int i = 1; i< activCount-1; i++)
    {
       if (activ[i].start >=  prev.final)
       {
           printf("\n%s, %d, %d", activ[i].denum,activ[i].start,activ[i].final);
           prev = activ[i];
       }

    }
}
void problema6()
{
    int x;
    int nrMin=0;
    scanf("%d",&x);
   while(x >0)
   {
       int n = 1;
       while(n <=x)
           n= n*2;
       n= n/2;
       printf("%d\n",n);
       x=x-n;
   }
}
int main() {
problema6();
    return 0;
}
