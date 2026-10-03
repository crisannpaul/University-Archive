from View.admin_panel import AdminPanel
from View.login import Login
from View.register import Register
from View.main_menu import MainMenu
import json

HOST = "127.0.0.1"
PORT = 12345


class Controller(object):
    def __init__(self, model, window):
        self.view = None
        self.model = model
        self.window = window
        self.language = 'ENGLISH'
        self.client = None

        with open('languages.json', 'r') as file:
            self.languages = json.loads(file.read())

        self.login_callbacks = {'login': self.login,
                                'register': self.to_register,
                                'guest': self.play_as_guest,
                                'english': self.language_english,
                                'spanish': self.language_spanish,
                                'russian': self.language_russian}
        self.register_callbacks = {'register': self.register_user,
                                   'back': self.back_to_login}
        self.admin_callbacks = {'execute': self.execute_statement,
                                'statistics': self.game_statistics,
                                'back': self.back_to_login}
        self.menu_callbacks = {'play': self.play,
                               'back': self.back_to_login}

    def init_view(self):
        self.view = Login(self.window, self.login_callbacks, self.languages[self.language])
        self.window.mainloop()

    def assign_client(self, client):
        self.client = client

    # ========================================================================
    # ==========================LOGIN CALLBACKS===============================
    # ========================================================================
    def login(self):
        request = {
            'type': 'login',
            'data': {
                'username': self.view.username(),
                'password': self.view.password()
            }
        }

        self.client.send_request(request)
        response = self.client.get_response()

        self.view.show_message((response['status'], response['message']))
        if response['status'] == 'success':

            request = {'type': 'session'}
            self.client.send_request(request)
            response = self.client.get_response()
            self.model.session = response

            user, score, role = response['username'], response['total_score'], response['role']

            if role == 'ADMIN':
                self.view = AdminPanel(self.window, self.admin_callbacks, self.languages[self.language])
                all_users = self.model.find_all('users')
                self.view.update_list(all_users)
            else:
                self.view = MainMenu(self.window, self.menu_callbacks, self.languages[self.language])
                self.view.update_user(user)
                self.view.update_score(score)

    def to_register(self):
        self.view = Register(self.window, self.register_callbacks, self.languages[self.language])

    def play_as_guest(self):
        self.model.play_guest()
        self.view = Login(self.window, self.login_callbacks, self.languages[self.language])

    def language_english(self):
        self.language = 'ENGLISH'
        self.view.update_language(self.languages[self.language])

    def language_spanish(self):
        self.language = 'SPANISH'
        self.view.update_language(self.languages[self.language])

    def language_russian(self):
        self.language = 'RUSSIAN'
        self.view.update_language(self.languages[self.language])

    # ========================================================================
    # ========================REGISTER CALLBACKS==============================
    # ========================================================================
    def register_user(self):
        request = {
            'type': 'register',
            'data': {
                'username': self.view.username(),
                'email': self.view.email(),
                'password': self.view.password()
            }
        }

        self.client.send_request(request)
        response = self.client.get_response()
        self.view.show_message((response['status'], response['message']))

    # ========================================================================
    # ==========================ADMIN CALLBACKS===============================
    # ========================================================================
    def execute_statement(self):
        # DELETE FROM games WHERE id='1'
        request = {
            'type': 'crud_op',
            'data': {
                'sql': self.view.get_input()
            }
        }
        self.client.send_request(request)
        response = self.client.get_response()
        self.view.show_message(response)

        request = {
            'type': 'find_all',
            'data': {
                'table_name': 'users'
            }
        }
        self.client.send_request(request)
        response = self.client.get_response()
        self.view.update_list(response)

    def game_statistics(self):
        request = {
            'type': 'statistics',
        }
        self.client.send_request(request)

    # ========================================================================
    # ===========================MENU CALLBACKS===============================
    # ========================================================================
    def play(self):
        self.model.play()

        new_score = self.model.session['total_score']
        self.view.update_score(new_score)

    # ========================================================================
    # ========================UNIVERSAL CALLBACKS=============================
    # ========================================================================
    def back_to_login(self):
        self.view = Login(self.window, self.login_callbacks, self.languages[self.language])
