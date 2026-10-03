tree1(t(6, t(4,t(2,nil,nil),t(5,nil,nil)), t(9,t(7,nil,nil),nil))).
tree2(t(8, t(5, nil, t(7, nil, nil)), t(9, t(12, nil, nil), t(11, nil, nil)))).

%inorder
inorder(t(K,L,R), List):-
inorder(L,LL),
inorder(R,LR),
append(LL, [K|LR], List).
inorder(nil, []).

%preorder
preorder(t(K,L,R), List):-
preorder(L,LL),
preorder(R, LR),
append([K|LL], LR, List).
preorder(nil, []).

%postorder
postorder(t(K,L,R), List):-
postorder(L,LL),
postorder(R, LR),
append(LL, LR,R1),
append(R1, [K], List).
postorder(nil, []).

%prettyprint
pretty_print(nil, _).
pretty_print(t(K,L,R), D):-
	D1 is D+1,
	pretty_print(L, D1),
	print_key(K, D),
	pretty_print(R, D1).

print_key(K, D):-D>0, !, D1 is D-1, tab(8), print_key(K, D1).
print_key(K, _):-write(K), nl.

%search_key
search_key(Key, t(Key, _, _)):- !.
search_key(Key, t(K, L, _)):- Key<K, !, search_key(Key, L).
search_key(Key, t(_, _, R)):- search_key(Key, R).

%insert_key
insert_key(Key, nil, t(Key, nil, nil)). % inserează cheia în arbore
insert_key(Key, t(Key, L, R), t(Key, L, R)):- !. % cheia există deja
insert_key(Key, t(K,L,R), t(K,NL,R)):- Key<K,!,insert_key(Key,L,NL).
insert_key(Key, t(K,L,R), t(K,L,NR)):- insert_key(Key, R, NR).

%delete_key
delete_key(Key, t(Key, L, nil), L):- !.
delete_key(Key, t(Key, nil, R), R):- !.
delete_key(Key, t(Key, L, R), t(Pred,NL,R)):- !, get_pred(L,Pred,NL).
delete_key(Key, t(K,L,R), t(K,NL,R)):- Key<K, !, delete_key(Key,L,NL).
delete_key(Key, t(K,L,R), t(K,L,NR)):- delete_key(Key,R,NR).

get_pred(t(Pred, L, nil), Pred, L):- !.
get_pred(t(Key, L, R), Pred, t(Key, L, NR)):- get_pred(R, Pred, NR).

%height
height(nil, 0).
height(t(_, L, R), H):-
height(L, H1),
height(R, H2),
max(H1, H2, H3),
H is H3+1.
max(A, B, A):-A>B, !.
max(_, B, B).

% Example ternary tree
ternary_tree(
    t(6,
        t(4,
            t(2, nil, nil, nil),
            nil,
            t(7, nil, nil, nil)),
        t(5, nil, nil, nil),
        t(9,
            t(3, nil, nil, nil),
            nil,
            nil)
    )
).

% ex1
%inorder traversal for a ternary tree
inorder_3(t(K, L, M, R), List) :-
    inorder_3(L, LL),
    inorder_3(M, LM),
    inorder_3(R, LR),
    append(LL, [K|LM], Tmp),
    append(Tmp, LR, List).
inorder_3(nil, []).

%preorder traversal for a ternary tree
preorder_3(t(K, L, M, R), List) :-
    preorder_3(L, LL),
    preorder_3(M, LM),
    preorder_3(R, LR),
    append([K|LL], LM, Tmp),
    append(Tmp, LR, List).
preorder_3(nil, []).

%postorder traversal for a ternary tree
postorder_3(t(K, L, M, R), List) :-
    postorder_3(L, LL),
    postorder_3(M, LM),
    postorder_3(R, LR),
    append(LL, LM, Tmp),
    append(Tmp, LR, Tmp2),
    append(Tmp2, [K], List).
postorder_3(nil, []).

% ex2
%pretty_print_3
pretty_print_3(nil, _).
pretty_print_3(t(K,L,M,R), D):-
    D1 is D+1,
	print_key(K, D),
    pretty_print_3(L, D1),
    pretty_print_3(M, D1),
    pretty_print_3(R, D1).

% ex3
%ternary_tree height
ternary_height(nil, 0).
ternary_height(t(_, L, M, R), H):-
    ternary_height(L, HL),
    ternary_height(M, HM),
    ternary_height(R, HR),
    max(HL, HM, Temp),
    max(Temp, HR, MaxHeight),
    H is MaxHeight + 1.
	
% ex5
%leaf_list
leaf_list(nil, []).
leaf_list(t(K,nil,nil), [K]):- !.
leaf_list(t(_,L,R), List):-
    leaf_list(L, LL),
    leaf_list(R, LR),
    append(LL, LR, List).

% ex6
%diam/2 
diam(nil, 0).
diam(t(_, L, R), D) :-
    diam(L, D1),
    diam(R, D2),
    height(L, H1),
    height(R, H2),
    D3 is H1 + H2 + 1,
    max_list([D1, D2, D3], D).
	
% ex7
%same_depth
same_depth(nil, _, []).
same_depth(t(K, _, _), 1, [K]).
same_depth(t(_, L, R), D, Res) :-
    D > 1,
    D1 is D - 1,
    same_depth(L, D1, R1),
    same_depth(R, D1, R2),
    append(R1, R2, Res).

% ex8
%symmetric and mirror
symmetric(nil).
symmetric(t(_, L, R)) :- mirror(L, R).

mirror(nil, nil).
mirror(t(_, L1, R1), t(_, L2, R2)) :- mirror(L1, R2), mirror(R1, L2).

