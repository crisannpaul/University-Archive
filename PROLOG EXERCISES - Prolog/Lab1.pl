% Predicatul woman/1
woman(ana).
woman(sara).
woman(ema).
woman(maria).
woman(dorina).
woman(irina).
woman(carmen).

% Predicatul man/1
man(andrei).
man(george).
man(alex).
man(marius).
man(mihai).
man(iisus).

% Predicatul parent/2
parent(maria, ana). % maria este părintele anei
parent(george, ana). % george este părintele anei
parent(maria, andrei).
parent(george, andrei). % …
parent(marius, maria).
parent(dorina, maria).
parent(maria, andrei).
parent(mihai, george).
parent(irina, george).
parent(irina, carmen).
parent(carmen, sara).
parent(alex, sara).
parent(alex, ema).
parent(iisus, mihai).

sibling(X,Y) :- parent(Z,X), parent(Z,Y), X\=Y.
brother(X,Y) :- sibling(X,Y), man(X).
sister(X,Y) :- sibling(X,Y), woman(X).

uncle(X,Y) :- brother(X,Z), parent(Z,Y).
aunt(X,Y) :- sister(X,Z), parent(Z,Y).

grandparent(X,Y) :- parent(X,Z), parent(Z, Y), X\=Y.
grandfather(X,Y) :- grandparent(X,Y), man(X).
grandmother(X,Y) :- grandparent(X,Y), woman(X).

ancestor(X, Y) :- parent(X,Z), ancestor(Z,Y).
ancestor(X, Y) :- parent(X,Y).