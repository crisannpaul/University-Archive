#include <stdio.h>
#include <stdlib.h>
int BinarySearch(int *v, int low,int high,int elem)
{
    if(high < low)
    {
        printf("Nu exista dar trebuie inserat pe pozitia: ");
        return high+1;
    }
    int mid = (high + low)/2;
    if(elem == v[mid])
        return mid;
    if( elem < v[mid])
        return BinarySearch(v,low,mid-1,elem);
    else
        return BinarySearch(v,mid+1,high,elem);
}
void merge(int *v,int middle, int left, int right)
{
    int n1 = middle - left + 1;
    int n2 = right - middle ;
    int *v1 = malloc(n1 * sizeof (int));
    int *v2 = malloc(n2 * sizeof (int));

    for(int i = 0; i < n1; i++)
        v1[i] = v[left+i];
    for(int i =0; i< n2; i++)
        v2[i] = v[middle+1+i];
    int i = 0, j = 0, k = left;
 while(i < n1 && j < n2)
 {
     if(v1[i]<v2[j])
     {
         v[k] = v1[i];
         i++;
     }
   else
     {
         v[k] = v2[j];
         j++;
     }
   k++;
 }
 while(i<  n1){
     v[k] = v1[i];
     i++;
     k++;
 }
 while( j< n2)
 {
     v[k] = v2[j];
     j++;
     k++;
 }

}
void mergeSort(int *v, int low,int high)
{
    if(low < high)
{
        int mid = (high + low)/2;
        mergeSort(v,low,mid);
        mergeSort(v,mid+1,high);
        merge(v,mid,low,high);
}
}
int main() {
    int v[]={6,2,7,4,1,3,20,18,17,16,15};
    mergeSort(v,0,10);
    for(int i = 0; i < 11; i++)
    {
        printf("%d ",v[i]);
    }
    return 0;
}
