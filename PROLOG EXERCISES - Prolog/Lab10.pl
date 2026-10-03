% ex 1
edge_ex1(a, b).
edge_ex1(a, c).
edge_ex1(b, d).

neighbor_list(Node, Neighbors) :-
    findall(Neighbor, edge_ex1(Node, Neighbor), Neighbors).

build_neighbor_lists :-
    retractall(neighb_list(_,_)), 
    forall(edge_ex1(X,_), (
        neighbor_list(X, Neighbors),
        assertz(neighb_list(X, Neighbors))
    )).

edge_to_neighb :-
    build_neighbor_lists.

% ex 2
edge_ex2(a,b).
edge_ex2(b,c).
edge_ex2(a,c).
edge_ex2(c,d).
edge_ex2(b,d).
edge_ex2(d,e).
edge_ex2(e,a).
edge(X, Y) :- edge_ex2(X, Y); edge_ex2(Y, X).

hamilton_path(0, X, Start, Visited, Path) :-
    edge(X, Start),
    reverse([Start|Visited], Path).
hamilton_path(NN1, X, Start, Visited, Path) :-
    NN1 > 0,
    edge(X, Y),
    \+ member(Y, Visited),
    NewNN1 is NN1 - 1,
    hamilton_path(NewNN1, Y, Start, [Y|Visited], Path).

hamilton(NN, X, Path):- NN1 is NN-1, hamilton_path(NN1, X, X, [X],Path).

% ex 3
edge_ex3(a,b).
edge_ex3(b,c).
edge_ex3(a,c).
edge_ex3(c,d).
edge_ex3(b,d).
edge_ex3(d,e).
edge_ex3(e,a).









