insert_ord(X, [H|T], [H|R]):-X>H, !, insert_ord(X, T, R).
insert_ord(X, T, [X|T]).

one_pass([H1,H2|T], [H2|R], F):- H1>H2, !, F=1, one_pass([H1|T],R,F).
one_pass([H1|T], [H1|R], F):- one_pass(T, R, F).
one_pass([], [] ,_).

min_char([H], H).
min_char([H|T], M):-min_char(T, M), char_code(H,CH), char_code(M, CM), CH>=CM.
min_char([H|T], H):-min_char(T, M), char_code(H,CH), char_code(M, CM), CH<CM.

min_len([H], H).
min_len([H|T], M):-min_len(T, M), length(H,CH), length(M, CM), CH>=CM.
min_len([H|T], H):-min_len(T, M), length(H,CH), length(M, CM), CH<CM.

% ex1
sel_sort(L, [M|R]):- max_list(L, M), delete(L, M, L1), sel_sort(L1, R).
sel_sort([], []).

% ex2
ins_sort([], Acc, Acc).
ins_sort([H|T], Acc, R) :- insert_ord(H, Acc, Acc1), ins_sort(T, Acc1, R).

% ex3
bubble_sort(L,R):- one_pass(L,R1,F), nonvar(F), !, bubble_sort(R1,R).
bubble_sort(L,L).

% ex4
char_sort(L, [M|R]):- min_char(L, M), delete(L, M, L1), char_sort(L1, R).
char_sort([], []).

% ex5 
len_sort(L, [M|R]):- min_len(L, M), delete(L, M, L1), len_sort(L1, R).
len_sort([], []).





