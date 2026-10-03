from Model.game.game import Game, GameDAO
from Model.connection_factory import Connection
from dataclasses import asdict
import mysql.connector


class Model(object):
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if Model._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Model._instance = self

        self.session = {}
        self.game = None
        self.status = (None, None)
        self.level = 0

    def play_guest(self):
        self.game = Game(level=0)
        self.game.run()

    def play(self):
        self.game = Game(level=self.level, session=self.session)
        self.game.run()
        self.save_game()

        new_score = self.game.score
        self.session['total_score'] += new_score
        self.update_user_score(self.session['username'], self.session['total_score'])

        path, best_path = self.game.path, self.game.best_path
        if len(path) > len(best_path):
            self.game = Game(level=self.level, session=self.session)
            self.game.run_ai()

        self.level = (self.level + 1) % 3

    @staticmethod
    def update_user_score(user, new_score):
        connection = None
        try:
            connection = Connection()
            cursor = connection.get_cursor()

            sql = f"UPDATE users SET total_score = {new_score} WHERE username = '{user}'"

            cursor.execute(sql)
            connection.commit()
        except mysql.connector.Error as err:
            print(format(err))
        finally:
            connection.close()

    def save_game(self):
        connection = None
        try:
            connection = Connection()
            cursor = connection.get_cursor()

            all_games = self.find_all('games')
            game_dao = GameDAO(self.game)
            game_dao.id = len(all_games)
            game_dao = asdict(game_dao)

            sql = """INSERT INTO games (id, player_id, level, score) 
                        VALUES 
                     (%(id)s, %(player_id)s, %(level)s, %(score)s)"""

            cursor.execute(sql, game_dao)
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

