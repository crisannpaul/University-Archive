fact1(0,1).
fact1(N,R):-N>0, NextN is N-1, fact1(NextN,R2), R is N*R2.
    
fact2(0,R,R).
fact2(N,Aux,R):-NextN is N-1, NextAux is Aux*N, fact2(NextN, NextAux, R).

% EX1
cmmdc(X, 0, X):- !.
cmmdc(0, X, X):- !.
cmmdc(X, Y, D):- X =< Y, !, Z is Y - X, cmmdc(X, Z, D).
cmmdc(X, Y, D):- cmmdc(Y, X, D).

% EX2
pow1(_,0,1).
pow1(N,E,R):-E>0, NextE is E-1, pow1(N, NextE, R2), R is R2*N.

pow2(_,0,R,R).
pow2(N,E,Aux,R):-NextE is E-1, NextAux is Aux*N, pow2(N,NextE,NextAux,R).

% EX3
fib(0, 1) :- !.
fib(1, 1) :- !.
fib(N, R) :- N1 is N - 1, N2 is N - 2, 
    fib(N1, R1), fib(N2, R2), 
    R is R1 + R2.

% EX4

% EX5
triangle(A,B,C):-A+B>C,
    A+C>B,
    B+C>A.

% EX6 
delta(A,B,C,D):- D is B*B - 4*A*C.
solve(A,B,C,X):- delta(A,B,C,D1), D1<0, X = 0. 
solve(A,B,C,X):- delta(A,B,C,0), X is -B/2*A.
solve(A,B,C,X):- delta(A,B,C,D1), D1>0, X is ((-1*B-sqrt(D1))/2*A).
solve(A,B,C,X):- delta(A,B,C,D1), D1>0, X is ((-1*B+sqrt(D1))/2*A).
    












