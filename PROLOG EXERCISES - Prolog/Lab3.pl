append([], L2, L2).
append([H|T], L2, [H|CoadaR]) :- append(T, L2, CoadaR).

% ex1
append3([],[],L3,L3).
append3([H|T],L2,L3,[H|CoadaR]) :- append3(T,L2,L3,CoadaR).
append3([],[H|T],L3,[H|CoadaR]) :- append3([],T,L3,CoadaR).

% ex2
add_first(E,[],[E]).
add_first(E,L,[E|L]).

% ex3
sum([],0).
sum([H|T],R) :- sum(T,R1), R is R1 + H.

% ex4
odd(X) :- 1 is X mod 2.
even(X) :- 0 is X mod 2.
separate_parity([], [], []).
separate_parity([H|T], [H|ODD1], EVEN) :- odd(H), separate_parity(T, ODD1, EVEN1), EVEN = EVEN1.
separate_parity([H|T], ODD, [H|EVEN1]) :- even(H), separate_parity(T, ODD1, EVEN1), ODD = ODD1.

% ex5
member(X, [X|_]).
member(X, [_|T]) :- member(X, T).
remove_duplicates([],[]).
remove_duplicates([H|T],R) :- member(H,T), remove_duplicates(T,Ri), Ri = R.
remove_duplicates([H|T],R) :- not(member(H,T)), remove_duplicates(T,Ri), R = [H|Ri].

% ex6
equals(X,Y) :- X is Y.
replace(_,_,[],[]).
replace(X,Y,[H|T],R) :- not(equals(X,H)), replace(X,Y,T,Ri), R=[H|Ri].
replace(X,Y,[H|T],R) :- equals(X,H), replace(X,Y,T,Ri), R=[Y|Ri].

% ex7
drop_k([],_,[],_).
drop_k([H|T],K,R,Cnt) :- CntI is Cnt+1, not(equals(Cnt,K)), drop_k(T,K,Ri,CntI), R=[H|Ri].
drop_k([_|T],K,R,Cnt) :- equals(Cnt,K), drop_k(T,K,Ri,1), R=Ri.









