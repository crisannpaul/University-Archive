import mysql.connector

HOST = "localhost"
USERNAME = "root"
PASSWORD = "root"
DATABASE = "game"


class Connection(object):
    def __init__(self):
        self.client = mysql.connector.connect(
            host=HOST,
            user=USERNAME,
            password=PASSWORD,
            database=DATABASE)
        self.cursor = self.client.cursor()

    def get_cursor(self):
        return self.client.cursor()

    def close(self):
        self.cursor.close()
        self.client.close()

    def is_connected(self):
        return self.client.is_connected()

    def get_info(self):
        return self.client.get_server_info()

    def commit(self):
        self.client.commit()


