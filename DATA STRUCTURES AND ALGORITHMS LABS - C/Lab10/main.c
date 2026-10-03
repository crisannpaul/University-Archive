#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void generate(char *charSet, int maxSolutionSize, char *solution, int current, unsigned (*checkPossibleSolution)(char *)) {
    int length = strlen(charSet);
    for (int i = 0; i < length;  i++){
        solution[current] = charSet[i];  //punem pe poz curenta
        if (checkPossibleSolution(solution)) {  //daca ii ok
            if (current < maxSolutionSize - 1) {  //daca mai am unde sa pun
                generate(charSet, maxSolutionSize, solution, current + 1, checkPossibleSolution);
                solution[current + 1] = '\0';  //cand ajungem la capat se sterge ultimul caracter
            }
        }
    }
}

void backtracking(char *charSet, int maxSolutionSize, unsigned (*checkPossibleSolution)(char *)) {
    char *solution = calloc(maxSolutionSize + 1, sizeof (char));
    generate(charSet, maxSolutionSize, solution, 0, checkPossibleSolution);
    free(solution);
}

unsigned check1(char *possible) {
    printf("%s\n", possible);
    int length = strlen(possible);
    if (length > 1){
        if (possible[length - 1] == possible[length - 2]) {
            return 0;
        }
    }
    if (length == 3) {
        printf("%s\n", possible);
    }
    return 1;
}

unsigned check2(char *possible) {  //toate combinatiile cu cifre distincte
    int length = strlen(possible);
    for (int i = 0; i < length - 1; i++) {
        if (possible[i] == possible[length - 1]) {
            return 0;
        }
    }
    if (length == 3) {
        printf("%s\n", possible);
    }
    return 1;
}

unsigned check3(char *possible) {  //toate combinatiile cu cifre la fel
    int length = strlen(possible);
    for (int i = 0; i < length - 1; i++) {
        if (possible[i] != possible[length - 1]) {
            return 0;
        }
    }
    if (length == 3) {
        printf("%s\n", possible);
    }
    return 1;
}

unsigned check4(char *possible) {  //toate combinatiile cu 0 in mijloc
    int length = strlen(possible);
    if (length > 1 && possible[1] != '0'){
        return 0;
    }
    if (length == 3) {
        printf("%s\n", possible);
    }
    return 1;
}
//Problema cu reginele pe tabla de sah
int counter;
int n = 4;

void printSol(char *solution) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            printf("%c ", solution[i * n + j]);
        }
        printf("\n");
    }
    printf("\n");
    printf("\n");
}


unsigned RegineSah(char *possible) {  //toate combinatiile cu 0 in mijloc
    int length = strlen(possible);
    /*counter++;
    if (counter % 1000000 == 0){
        printf("%u\n", counter);
    }
     */
    if (length % n == 0) {  //daca am terminat de generat o linie
        int queens = 0;
        int queenPos = 0; // pozitia reginei amplasata pe o linie
        for (int i = n - 1 ; i >= 0; i--) {  //parcurgem linia generata si verificam daca exista fix o regina pe acela linie
            if (possible[length - 1 - i] == 'R') {
                queens++;
                queenPos = n - i - 1;  //am memorat coloana pe care e regina
                if (queens > 1) {  //daca am mai mult de o regina pe linie
                    return 0;
                }
            }
        }
        if (queens != 1) {  //daca pe o linie sunt 0 sau mai mult de o regina returnam 0
            return 0;
        }
        int lines = length / n;
        for (int i = 0; i < lines - 1; i++) {
            if (possible[i * n + queenPos] == 'R') {  //daca am regina pe coloana nu e ok
                return 0;
            }
        }
        int diag = 0;
        for(int i = lines - 2; i >= 0; i--)
        {
            diag++;
            if((i * n + queenPos + diag) < n  && (i * n + queenPos - diag) >= 0) {
                if (possible[i * n + queenPos + diag] == 'R' ||
                    possible[i * n + queenPos - diag] == 'R') // daca exista vecina pe diagonala;
                    return 0;
            }
            else
            {
                if((i * n + queenPos + diag) < n)
                    if(possible[i * n + queenPos + diag] == 'R')
                        return 0;
                if ((i * n + queenPos - diag) >= 0)
                    if(possible[i * n + queenPos - diag] == 'R')
                        return 0;
            }
        }
    }
    if (length == n * n) {
        printSol(possible);
    }
    return 1;
}

int main() {
    //backtracking("0123456789", 3, check4);
    backtracking(".R", n * n, RegineSah);
    return 0;
}