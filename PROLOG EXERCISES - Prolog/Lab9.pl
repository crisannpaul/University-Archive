complete_tree(t(6, t(4, t(2, nil, nil), t(5, nil, nil)), t(9, t(7, nil, nil), nil))).


% ex 1
preorder_dl(nil, L, L).
preorder_dl(t(K,L,R),LS,LE) :- preorder_dl(L, LSL, LEL),
    						preorder_dl(R, LSR, LER),
    						LS = [K|LSL], LEL = LSR, LE = LER.

postorder_dl(nil, L, L).
postorder_dl(t(K,L,R),LS,LE) :- postorder_dl(L, LSL, LEL),
    						postorder_dl(R, LSR, LER),
    						LS = LSL, LEL = LSR, LE = [K|LER].

% ex 2
convertIL2DL(IL, LS, LS) :- var(IL).
convertIL2DL([H|T], [H|LSI], LE) :- convertIL2DL(T, LSI ,LE), !.

convertDL2IL(LS, LS, _) :- var(LS).
convertDL2IL([H|T], LS, [H|Ri]) :- convertDL2IL(T, LS, Ri), !.

% ex 3
convertCL2DL([], LS, LS).
convertCL2DL([H|T],[H|LSi],LS) :- convertCL2DL(T,LSi,LS).

convertDL2CL(LS, LS, []) :- var(LS).
convertDL2CL([H|T], LS, [H|Ri]) :- convertDL2CL(T, LS, Ri), !.

% ex 5
flat_dl([], RS, RS).
flat_dl([H|T], [H|RS], RE) :- atomic(H), !, flat_dl(T, RS, RE).
flat_dl([H|T], RS, RE) :- flat_dl(H, RS1, RE1), flat_dl(T, RS2, RE2), 
    					RS = RS1, 
    					RE1 = RS2, 
    					RE = RE2.
    
% ex 6
evel_dl(nil, RS, RS).
even_dl(t(K,L,R), RS, RE) :- 0 is K mod 2, !,
    even_dl(L, RS1, RE1),
    even_dl(R, RS2, RE2),
    RS = RS1, 
    RE1 = RS2, 
    RE = RE2.
even_dl(t(K,nil,nil), [K], RE) :- 0 is K mod 2, !.
even_dl(t(_,L,R), RS, RE) :- even_dl(L, RS1, RE1), 
    even_dl(R, RS2, RE2),
    RS = RS1, 
    RE1 = RS2, 
    RE = RE2.











