from Server.server import GameServer
from Model.model import Model

HOST = "127.0.0.1"
PORT = 12345

model = Model()
model.create_db()
server = GameServer(HOST, PORT, model)
server.start_server()
