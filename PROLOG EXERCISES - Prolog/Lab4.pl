member(X, [X|_]) :- !.
member(X, [_|T]) :- member(X, T).

min([H], H).
min([H|T], M):-min(T, M), H>=M.
min([H|T], H):-min(T, M), H<M.

% ex1
intersect([],_,[]).
intersect([H|T],L2,R) :- member(H,L2), !, intersect(T,L2,Ri), R = [H|Ri].
intersect([_|T],L2,R) :- intersect(T,L2,Ri), R = Ri.

% ex2
diff([],_,[]).
diff([H|T],L2,R) :- not(member(H,L2)), !, diff(T,L2,Ri), R = [H|Ri].
diff([_|T],L2,R) :- diff(T,L2,Ri), R = Ri.

% ex3
del_min([],[],_,[]).
del_min([H|T],R,MIN,ACC) :- H<MIN, del_min(T,R,H,[H|ACC]);
    						del_min(T,R,MIN,[H|ACC]).
del_min([],R,MIN,[H|T]) :- not(H is MIN), del_min([],Ri,MIN,T), R = [H|Ri];
    						del_min([],Ri,MIN,T), R = Ri.


% ex4
help([],[]).
help([H|T],R) :- help(T,Ri), R is [H|Ri].
reverse_k(L,0,R) :- help(L, R).
reverse_k([H|T],K,R) :- Ki is K-1, reverse_k(T,Ki,Ri), R = [H|Ri].






