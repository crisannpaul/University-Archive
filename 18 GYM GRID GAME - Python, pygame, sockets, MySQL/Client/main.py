from Controller.controller import Controller
from Model.model import Model
from client import Client
from tkinter import Tk

HOST = "127.0.0.1"
PORT = 12345
window = Tk()

model = Model()
controller = Controller(model, window)

client = Client(HOST, PORT)
controller.assign_client(client)
controller.init_view()
