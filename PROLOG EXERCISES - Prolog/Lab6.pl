
member1(H, [H|_]).
member1(X, [H|_]):- member1(X,H).
member1(X, [_|T]):- member1(X,T).

depth([],1).
depth([H|T],R):- atomic(H), !, depth(T,R).
depth([H|T],R):- depth(H,R1), depth(T,R2), R3 is R1+1, max(R3,R2,R).

flatten([],[]).
flatten([H|T], [H|R]):- atomic(H), !, flatten(T,R).
flatten([H|T], R):- flatten(H,R1), flatten(T,R2), append(R1,R2,R).

% ex1
count_atomic([], 0).
count_atomic([H|T],R):- atomic(H), !, count_atomic(T, R1), R is R1+1.
count_atomic([H|T],R):- count_atomic(H, R1), count_atomic(T, R2), R is R1+R2.

% ex2
sum_atomic([],0).
sum_atomic([H|T],R):- atomic(H), !, sum_atomic(T, R1), R is R1+H.
sum_atomic([H|T],R):- sum_atomic(H, R1), sum_atomic(T, R2), R is R1+R2.

% ex3
member2(H, [H|_]).
member2(X, [H|_]):- member2(X,H), !.
member2(X, [_|T]):- member2(X,T).

% ex4
replace(_, _, [], []).
replace(X, Y, [X|T], [Y|R]) :- replace(X, Y, T, R).
replace(X, Y, [H|T], [H|R]) :- atomic(H), H \= X, !, replace(X, Y, T, R).
replace(X, Y, [H|T], [HR|R]) :- replace(X, Y, H, HR), replace(X, Y, T, R).

% ex5
lasts([],[]).
lasts([H|T],R):- atomic(H), T=[], !, lasts(T,Ri), R=[H|Ri].
lasts([H|T], R):- lasts(H, R1), lasts(T, R2), append(R1, R2, R).
lasts([_|T],R):- lasts(T,R).












