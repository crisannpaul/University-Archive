from dataclasses import asdict

import mysql.connector
from Model.connection_factory import Connection
from Model.player import Player, PlayerDAO
from Model.statistics import Statistics


class Model(object):
    def __init__(self):
        self.session = {}
        self.status = (None, None)

    def display_statistics(self):
        games = self.find_all('games')
        Statistics.plot_score_distribution_by_player(games)

    def authenticate_user(self, username, password):
        self.status = ("Login successful", 0)
        connection = None
        try:
            connection = Connection()
            cursor = connection.get_cursor()

            sql = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"

            cursor.execute(sql)
            query_result = cursor.fetchall()

            if query_result:
                print(query_result)
                current_user = query_result[0]
                self.session = {'id': current_user[0], 'username': current_user[1], 'email': current_user[2],
                                'password': current_user[3], 'total_score': current_user[4], 'role': current_user[5]}
                print(self.session)
            else:
                self.status = ("Incorrect Username or Password", -1)
        except mysql.connector.Error as err:
            print(format(err))
        finally:
            connection.close()

    def save_user(self, username, email, password):
        self.status = ("Register successful", 0)

        connection = None
        try:
            connection = Connection()
            cursor = connection.get_cursor()

            users = self.find_all('users')
            for user in users:
                if email == user[2]:
                    self.status = ("Email already exists", -1)
                if username == user[1]:
                    self.status = ("Username already exists", -1)

            player = Player(username, email, password)
            player_dao = PlayerDAO(player)
            player_dao.id = len(users)
            player_dao = asdict(player_dao)

            sql = """INSERT INTO users (id, username, email, password, total_score, role) 
                        VALUES 
                    (%(id)s, %(username)s, %(email)s, %(password)s, %(total_score)s, %(role)s)"""

            cursor.execute(sql, player_dao)
            connection.commit()
        except mysql.connector.Error as err:
            print(format(err))
        finally:
            connection.close()

    @staticmethod
    def find_all(table_name):
        connection = None
        query_result = []
        try:
            connection = Connection()
            cursor = connection.get_cursor()

            sql = f"SELECT * FROM {table_name}"

            cursor.execute(sql)
            query_result = cursor.fetchall()
        except mysql.connector.Error as err:
            print(format(err))
        finally:
            connection.close()
            return query_result

    def execute_statement(self, sql):
        self.status = ("Statement executed successfully", 0)
        connection = None
        try:
            connection = Connection()
            cursor = connection.get_cursor()

            cursor.execute(sql)
            _ = cursor.fetchall()
            connection.commit()
        except mysql.connector.Error as err:
            self.status = (f"{format(err)}", -1)
            print(format(err))
        finally:
            connection.close()

    @staticmethod
    def create_db():
        connection = None
        try:
            connection = Connection()
            cursor = connection.get_cursor()

            # === DROP EXISTING TABLES ===
            cursor.execute("DROP TABLE IF EXISTS games")
            cursor.execute("DROP TABLE IF EXISTS users")

            # === CREATE USERS TABLE ===
            cursor.execute("""CREATE TABLE users (
                    id VARCHAR(255) PRIMARY KEY, 
                    username VARCHAR(255) NOT NULL UNIQUE, 
                    email VARCHAR(255) NOT NULL UNIQUE, 
                    password VARCHAR(255) NOT NULL, 
                    total_score INT NOT NULL, 
                    role VARCHAR(255) NOT NULL)""")

            # === CREATE GAMES TABLE ===
            cursor.execute("""CREATE TABLE games (
                   id VARCHAR(255) PRIMARY KEY,
                   player_id VARCHAR(255) NOT NULL ,
                   level INT NOT NULL,
                   score INT NOT NULL)""")

            # === ADD ADMIN ===
            cursor.execute("""INSERT INTO users (id, username, email, password, total_score, role) 
                                VALUES 
                            (0, 'admin','-', 'admin', 0, 'ADMIN')""")

            # === ADD PLAYER ID FOREIGN KEY ===
            cursor.execute("""ALTER TABLE games ADD FOREIGN KEY
                   (player_id) REFERENCES users(id);""")

            connection.commit()
        except mysql.connector.Error as err:
            print(f"Error {format(err)}")
        finally:
            connection.close()
