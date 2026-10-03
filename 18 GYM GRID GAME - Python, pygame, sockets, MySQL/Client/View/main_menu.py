from tkinter import *
from PIL import ImageTk, Image

WIDTH = 600
HEIGHT = 300


class MainMenu(object):
    def __init__(self, window, callbacks, language):
        self.window = window
        self.window.geometry(f'{WIDTH}x{HEIGHT}')
        self.window.title('Menu')
        self.language = language

        # ====== Login Frame =========================
        self.menu_frame = Frame(self.window, width=WIDTH, height=HEIGHT)
        self.menu_frame.config(bg="white")
        self.menu_frame.place(x=0, y=0)

        # ========================================================================
        # ============================background image============================
        # ========================================================================
        self.bg_frame = Image.open('View/images/login_background.jpg')
        self.bg_frame = self.bg_frame.resize((WIDTH, HEIGHT))
        photo = ImageTk.PhotoImage(self.bg_frame)
        self.bg_panel = Label(self.menu_frame, image=photo)
        self.bg_panel.image = photo
        self.bg_panel.pack(fill='both', expand='yes')

        # ========================================================================
        # ============================username====================================
        # ========================================================================
        X, Y = 20, 25
        self.username_label = Label(self.menu_frame, text="Username", bg="white", fg="blue",
                                    font=("yu gothic ui", 22, "bold"), cursor="arrow")
        self.username_label.place(x=X, y=Y)

        # ========================================================================
        # ============================total score=================================
        # ========================================================================
        X, Y = 20, 65
        self.score_label = Label(self.menu_frame, text="Score:", bg="white", fg="black",
                                 font=("yu gothic ui", 20, "bold"), cursor="arrow")
        self.score_label.place(x=X, y=Y)

        # =========================================================================
        # ==============================back btn==================================
        # =========================================================================
        X, Y = 2, 3
        self.back_btn = Button(self.menu_frame, text='< Back', borderwidth=0,
                           font=("yu gothic ui", 8, "bold"), width=5,
                           bg="white", cursor='hand2', fg='#3047ff')
        self.back_btn.place(x=X, y=Y)

        # =========================================================================
        # ==============================play btn===================================
        # =========================================================================
        X, Y = 40, 180
        self.play_btn = Button(self.menu_frame, text='PLAY', relief=RAISED,
                               font=("yu gothic ui", 18, "bold"), width=18, bd=4,
                               bg='#3047ff', cursor='hand2', activebackground='#3047ff', fg='white')
        self.play_btn.place(x=X, y=Y)

        self.back_btn['command'] = callbacks['back']
        self.play_btn['command'] = callbacks['play']

        self.play_btn['text'] = language['PLAY']
        self.back_btn['text'] = language['BACK']

    def update_user(self, user):
        self.username_label['text'] = user

    def update_score(self, score):
        self.score_label['text'] = f"{self.language['SCORE']}: {score}"

