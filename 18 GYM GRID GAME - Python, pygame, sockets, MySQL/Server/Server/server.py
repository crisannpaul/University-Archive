import json
import socket
import threading


class GameServer:
    def __init__(self, host, port, model):
        self.host = host
        self.port = port
        self.model = model
        self.server_socket = None
        self.clients = []

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f"Server started on {self.host}:{self.port}")

        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"New connection from {client_address}")
            self.clients.append((client_socket, client_address))
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

    def handle_client(self, client_socket):
        while True:
            try:
                message = client_socket.recv(1024).decode()
                if message:
                    message_data = json.loads(message)
                    print(f"Client sent raw data:  + {message_data}")
                    request_type = message_data['type']

                    if request_type == "session":
                        response = self.model.session
                        client_socket.send(json.dumps(response).encode())

                    if request_type == "login":
                        response = self.handle_login(message_data)
                        client_socket.send(json.dumps(response).encode())

                    if request_type == "register":
                        response = self.handle_register(message_data)
                        client_socket.send(json.dumps(response).encode())

                    if request_type == "crud_op":
                        response = self.handle_crud(message_data)
                        client_socket.send(json.dumps(response).encode())

                    if request_type == "statistics":
                        self.model.display_statistics()

                    if request_type == "find_all":
                        response = self.model.find_all(message_data['data']['table_name'])
                        client_socket.send(json.dumps(response).encode())

            except Exception as e:
                print(f"Error: {e}")
                client_socket.close()
                break

    def handle_login(self, message_data):
        username = message_data["data"]["username"]
        password = message_data["data"]["password"]

        self.model.authenticate_user(username, password)
        status = self.model.status

        if status[1] == 0:
            response = {"type": "login", "status": "success", "message": status[0]}
        else:
            response = {"type": "login", "status": "failed", "message": status[0]}

        print("Server is sending:", response)
        return response

    def handle_register(self, message_data):
        username = message_data["data"]["username"]
        email = message_data["data"]["email"]
        password = message_data["data"]["password"]

        self.model.save_user(username, email, password)
        status = self.model.status

        if status[1] == 0:
            response = {"type": "register", "status": "success", "message": status[0]}
        else:
            response = {"type": "register", "status": "failed", "message": status[0]}

        print("Server is sending:", response)
        return response

    def handle_crud(self, message_data):
        sql = message_data['data']['sql']

        print("Statement" + sql)
        self.model.execute_statement(sql)
        status = self.model.status
        print("Status" + str(status))

        return status
