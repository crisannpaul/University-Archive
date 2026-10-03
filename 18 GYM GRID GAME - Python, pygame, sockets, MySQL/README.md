# 18 Gym: grid game, client/server (Python)

Final project for the Software Design course (TUCN, year III). A pygame grid game with fog of war: the player moves towards a reward while avoiding traps and is scored against an A* optimal path (`Client/Model/game/ai_player.py`). Around the game there is login, registration, an admin CRUD panel, statistics and a multi-language UI.

This is the last stage of the project, split into a threaded TCP server exchanging JSON messages (`Server/`) and a GUI client (`Client/`). UML diagrams are in `Diagrams/`.

Not included: the game sprites and UI images (`Client/Model/game/sprites`, `Client/View/images`), so the client needs replacement assets to run. The server expects a local MySQL instance; connection settings are in `Server/Model/connection_factory.py`.
