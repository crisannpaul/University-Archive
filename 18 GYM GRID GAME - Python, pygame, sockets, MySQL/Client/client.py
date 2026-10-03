import json
import socket


class Client:
    def __init__(self, host, port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))

    def send_request(self, request):
        self.client.sendall(json.dumps(request).encode('utf-8'))

    def get_response(self):
        response = self.client.recv(1024)
        print(response)

        if not response:
            return None

        return json.loads(response.decode('utf-8'))

    def disconnect(self):
        self.client.close()
