% Selection sort

min([H], H).
min([H|T], M):- min(T, M), H>=M, !.
min([H|_], H).

sel_sort(L, [M|R]):- min(L, M), delete(M, L, L1), sel_sort(L1, R).
sel_sort([], []).

% Calculați suma elementelor unei liste. 

sum([], 0).
sum([H|T], R) :- sum(T, Ri), R is Ri + H.

% Dublați elementele impare și ridicați la pătrat cele pare.

numbers([], []).
numbers([H|T], R) :- 0 is H mod 2, numbers(T, Ri), !, R = [H|[H|Ri]].
numbers([H|T], R) :- 1 is H mod 2, numbers(T, Ri), H2 is H * H, R = [H2|Ri].

% Extrageți numerele pare în E și numerele impare în O

separate_parity([], [], []).
separate_parity([H|T], E, O) :- 0 is H mod 2, !, separate_parity(T, Ei, O), E = [H|Ei].
separate_parity([H|T], E, O) :- 1 is H mod 2, separate_parity(T, E, Oi), O = [H|Oi].

%  Înlocuiți toate aparițiile lui X cu Y.

replace_all_ss(_, _, [], []).
replace_all_ss(X, Y, [H|T], R) :-  H = X, replace_all_ss(X, Y, T, Ri), R = [Y|Ri]
    						;   replace_all_ss(X, Y, T, Ri), R = [H|Ri].

% Înlocuiți toate aparițiile lui of X într-o listă diferență (al doilea si al treilea argument) cu
% secvența [Y,X,Y].

replace_all_s(_, _, S, E, []) :- S=E.
replace_all_s(X, Y, [H|T], E, R) :- X = H, replace_all_s(X, Y, T, E, Ri), R = [Y,X,Y|Ri]
    						   ;  replace_all_s(X, Y, T, E, Ri), R = [H|Ri].


% Sțergeți aparițiile lui X pe poziții pare (numerotatea poziției începe de la 1).

delete_pos_even(L, X, R) :- delete_pos_helper(L, 1, X, R).
delete_pos_helper([], _, _, []).
delete_pos_helper([H|T], K, X, R) :- 0 is K mod 2, X = H, delete_pos_helper(T, K+1, X, Ri), R = Ri
    								;   delete_pos_helper(T, K+1, X, Ri), R = [H|Ri].

% Inversează o listă incompletă

reverse_il1(L, _) :- var(L), !.
reverse_il1([H|T], R) :- reverse_il1(T, NewR), append(NewR, [H|_], R).

% Inversați elementele dintr-o lista după poziția K

reverse_k([], _, []).
reverse_k([H|T], K, [H|R]) :- K>0, !, NewK is K-1, reverse_k(T, NewK, R).
reverse_k([H|T], K, R) :- reverse_k(T, K, NewR), append(NewR, [H], R).

%ex18 codificare rle doua sau m multe elem consecutive 
%se inlocuiesc cu elemn, nr app, 
%daca nr app = 1, se scrie doar elem

count_elem(L, Elem, R) :- count_elem(L, Elem, 0, R).
count_elem([], _, Acc, Acc).
count_elem([H|T], Elem, Acc, R) :-
    H = Elem, !,
    Nacc is Acc + 1,
	count_elem(T, Elem, Nacc, R).
count_elem([_|T], Elem, Acc, R):-
    count_elem(T, Elem, Acc, R).


rle_encode(L, R) :- rle_encode(L, [], R).
rle_encode([], _, []).
rle_encode([H|T], Check, [(H,NrAp)|R]) :-
    not(member(H, Check)), !,
    count_elem([H|T], H, NrAp),
    rle_encode(T, [H|Check], R).
rle_encode([_|T], Check, R) :-
    rle_encode(T, Check, R).

%ex19 rle decode
create_list(_, 0, []).
create_list(X, Length, [X|R]):-
    Length > 0, !,
	Nlen is Length - 1,
    create_list(X, Nlen, R).

rle_decode([], []).
rle_decode([H|T], R) :-
    H = [El, Cnt],
    create_list(El, Cnt, NList), 
    rle_decode(T, NR),
    append(NList, NR, R).

% Delete duplicate elements that are on an odd position in a list (the position numbering starts
% at 1).

remove_dup_odd(L, R) :- remove_odd_help(L, [], 1, R).
remove_odd_help([], _, _, []).
remove_odd_help([H|T], Check, K, R) :- 
    not(member(H,Check)),
    Ki is K + 1,
    remove_odd_help(T, [H|Check], Ki, Ri), R = [H|Ri].
remove_odd_help([H|T], Check, K, R) :- 
    member(H, Check),
    1 is K mod 2,
    Ki is K + 1,
    remove_odd_help(T, Check, Ki, Ri), Ri = R.
remove_odd_help([_|T], Check, K, R) :-
    Ki is K + 1,
    remove_odd_help(T, Check, Ki, R).


% Rotiți lista K poziții în dreapta. 

rotate_k(L, K, R) :- rotate_k_help(L, K, [], R).
rotate_k_help([H|T], K, Acc, R) :-
    K > 0,
    Ki = K - 1,
    rotate_k_help(T, Ki, [H|Acc], R).
rotate_k_help([_|T], K, Acc, R) :- 
    K = 0,
    rotate_k_help(T, K, Acc, R), append(T, Acc, R).


% Calculați adâncimea maximă a unei liste imbricate.

adancime(L, R) :- adancime(L, 1, R).
adancime([], Acc, Acc).
adancime([H|_], Acc, R) :-
    not(atomic(H)), !,
    NAcc is Acc + 1,
    adancime(H, NAcc, R).
adancime([_|T], Acc, R):-
    adancime(T, Acc, R).

% Aplatizați o listă imbricată cu liste complete/incomplete. 

flat([], T) :- var(T), !.
flat([H|T], [H|R]) :-
    atomic(H), !,
    flat(T, R).
flat([H|T], R) :-
    flat(H, RH), flat(T, RT), append(RH, RT, R).

% Aplatizați doar elementele de la o adâncime dată într-o listă imbricată.

flat_only(L, K, R) :- flat_only(L, K, 1, R).
flat_only([], _, _, []).
flat_only([H|T], K, Cnt, [H|R]) :- 
    atomic(H), 
    K is Cnt, !, 
    flat_only(T, K, Cnt, R).
flat_only([H|T], K, Cnt, R) :- 
    atomic(H), !,
    flat_only(T, K, Cnt, R).
flat_only([H|T], K, Cnt, R) :- 
    not(atomic(H)), 
    Cnti is Cnt + 1, !,
    flat_only(H, K, Cnti, RH), flat_only(T, K, Cnt, RT), append(RH, RT, R). 

% Calculați suma elementelor de la nivelul K intr-o lista imbricată.

sum_k(L, K, R) :- sum_k(L, K, 1, R).
sum_k(L, _, _, 0) :- var(L).
sum_k([H|T], K, Cnt, R) :- 
    atomic(H),
    K = Cnt,
    sum_k(T, K, Cnt, Ri),
    R is Ri + H.
sum_k([H|T], K, Cnt, R) :- 
    atomic(H),
    sum_k(T, K, Cnt, R).
sum_k([H|T], K, Cnt, R) :- 
    not(atomic(H)), 
    Cnti is Cnt + 1, !,
    sum_k(H, K, Cnti, RH), sum_k(T, K, Cnt, RT), R is RH + RT.

% Calculați numărul de liste într-o listă imbricată. 

count_lists([], Acc, R):-
    R is Acc+1.
count_lists([H|T], Acc, R):-
    \+ atomic(H),!,
    count_lists(H, 0, CH), 
    Nacc is Acc + CH ,
    count_lists(T, Nacc, R).
count_lists([_|T], Acc, R):-
    count_lists(T, Acc, R). 

% Înlocuiți toate aparițiile lui X cu Y în lista imbricată. 

replace_all(_, _, [], []).
replace_all(X, Y, [H|T], R) :-
    atomic(H),
    H = X,
    replace_all(X, Y, T, Ri),
    R = [Y|Ri].
replace_all(X, Y, [H|T], R) :-
    not(atomic(H)),
    replace_all(X, Y, H, RH), replace_all(X, Y, T, RT), append(RH, RT, R).
replace_all(X, Y,[_|T], R):-
    replace_all(X, Y, T, R).

% Înlocuiți fiecare secvență cu o adâncime constantă cu lungimea într-o listă adâncă.

len_con_depth(L, R) :- len_con_depth(L, 0, R).
len_con_depth([H|T], K, R) :-
    atomic(H),
    Ki is K + 1,
    len_con_depth(T, Ki, R).
len_con_depth([H|T], K, R) :-
    Ki is K + 1,
    len_con_depth(H, 0, Ri), R = [K|Ri], len_con_depth(T, Ki, RT), append(Ri, RT, R).













