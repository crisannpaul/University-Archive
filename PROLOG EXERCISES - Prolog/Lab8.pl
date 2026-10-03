% Arbori:
incomplete_tree(t(7, t(5, t(3, _, _), t(6, _, _)), t(11, _, _))).
complete_tree(t(7, t(5, t(3, nil, nil), t(6, nil, nil)), t(11, nil, nil))).

% ex1
convertI2C(L,[]) :- var(L).
convertI2C([H|T],[H|Ri]) :- convertI2C(T,Ri), !.

convertC2I([],[_]).
convertC2I([H|T],[H|Ri]) :- convertC2I(T,Ri), !.

% ex2
append_i(L,L2,L2) :- var(L).
append_i([H|T],L2,[H|Ri]) :- append(T,L2,Ri), !.

% ex3 - nu mere ma bate
%reverse_i(L,L,L) :- var(L).
%reverse_i([H|T],Acc,R) :- reverse_i(T,NAcc,RT), concat(Acc,[H|_],Nacc).

% ex4 
flatten_i(L,_) :- var(L), !.
flatten_i([],[]).
flatten_i([H|T], [H|R]):- atomic(H), !, flatten_i(T,R).
flatten_i([H|T], R):- flatten_i(H,R1), flatten_i(T,R2), append(R1,R2,R).

% ex5 
convertIT2CT(T,nil) :- var(T).
convertIT2CT(t(K,L,R),t(KI,LI,RI)) :- convertIT2CT(K,KI), 
    convertIT2CT(L,LI), 
    convertIT2CT(R,RI), !.
convertIT2CT(K,K).	

convertCT2IT(T,_).
convertCT2IT(t(K,L,R),t(KI,LI,RI)) :- convertIT2CT(K,KI), 
    convertIT2CT(L,LI), 
    convertIT2CT(R,RI), !.
convertCT2IT(K,K).



