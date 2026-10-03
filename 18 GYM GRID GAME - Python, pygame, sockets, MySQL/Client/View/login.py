from tkinter import *
from tkinter import messagebox
from PIL import ImageTk, Image

WIDTH = 700
HEIGHT = 250


class Login(object):
    def __init__(self, window, callbacks, language):
        self.window = window
        self.window.geometry(f'{WIDTH}x{HEIGHT}')
        self.window.title('Login')
        self.language = language

        # ====== Login Frame =========================
        self.lgn_frame = Frame(self.window, bg="white", width=WIDTH, height=HEIGHT)
        self.lgn_frame.config(bg="white")
        self.lgn_frame.place(x=0, y=0)

        # ========================================================================
        # ============================background image============================
        # ========================================================================
        self.bg_frame = Image.open('View/images/login_background.jpg')
        self.bg_frame = self.bg_frame.resize((WIDTH, HEIGHT))
        photo = ImageTk.PhotoImage(self.bg_frame)
        self.bg_panel = Label(self.lgn_frame, image=photo)
        self.bg_panel.image = photo
        self.bg_panel.pack(fill='both', expand='yes')

        # ========================================================================
        # ============================username====================================
        # ========================================================================
        X, Y = 40, 40
        self.username_label = Label(self.lgn_frame, text="Username:", bg="white", fg="black",
                                    font=("yu gothic ui", 20, "bold"), cursor="arrow")
        self.username_label.place(x=X, y=Y)

        self.username_entry = Entry(self.lgn_frame, highlightthickness=0, relief=SUNKEN, bg="white", fg="black",
                                    font=("yu gothic ui ", 22, "bold"), insertbackground='#000000', width=10)
        self.username_entry.place(x=4.5 * X, y=Y, width=270)

        # ========================================================================
        # ============================password====================================
        # ========================================================================
        X, Y = 40, 100
        self.password_label = Label(self.lgn_frame, text="Password:", bg="white", fg="black",
                                    font=("yu gothic ui", 20, "bold"), cursor="arrow")
        self.password_label.place(x=X + 5, y=Y)

        self.password_entry = Entry(self.lgn_frame, highlightthickness=0, relief=SUNKEN, bg="white", fg="black",
                                    font=("yu gothic ui ", 22, "bold"), insertbackground='#000000', width=10)
        self.password_entry.place(x=4.5 * X, y=Y, width=270)

        # =========================================================================
        # ============================log in btn===================================
        # =========================================================================
        X, Y = 40, 160
        self.login_btn = Button(self.lgn_frame, text='LOGIN', relief=RAISED,
                                font=("yu gothic ui", 13, "bold"), width=18, bd=1,
                                bg='#3047ff', cursor='hand2', activebackground='#3047ff', fg='white')
        self.login_btn.place(x=X, y=Y)

        # =========================================================================
        # ============================register btn=================================
        # =========================================================================
        X, Y = 263, 160
        self.register_btn = Button(self.lgn_frame, text='REGISTER', relief=RAISED,
                                   font=("yu gothic ui", 13, "bold"), width=18, bd=1,
                                   bg='#3047ff', cursor='hand2', activebackground='#3047ff', fg='white')
        self.register_btn.place(x=X, y=Y)

        # =========================================================================
        # ==========================play as guest btn==============================
        # =========================================================================
        X, Y = 145, 205
        self.play_guest_btn = Button(self.lgn_frame, text='Play as Guest', borderwidth=0,
                                     font=("yu gothic ui", 13, "bold"), width=18,
                                     bg="white", cursor='hand2', fg='#3047ff')
        self.play_guest_btn.place(x=X, y=Y)

        # =========================================================================
        # ==========================language selection=============================
        # =========================================================================
        X, Y = 5, 5
        self.english_btn = Button(self.lgn_frame, text='English', borderwidth=0,
                                  font=("yu gothic ui", 11, "bold"), width=10,
                                  bg="white", cursor='hand2', fg='#3047ff')
        self.english_btn.place(x=X, y=Y)

        X, Y = 105, 5
        self.spanish_btn = Button(self.lgn_frame, text='Spanish', borderwidth=0,
                                  font=("yu gothic ui", 11, "bold"), width=10,
                                  bg="white", cursor='hand2', fg='#3047ff')
        self.spanish_btn.place(x=X, y=Y)

        X, Y = 205, 5
        self.russian_btn = Button(self.lgn_frame, text='Russian', borderwidth=0,
                                  font=("yu gothic ui", 11, "bold"), width=10,
                                  bg="white", cursor='hand2', fg='#3047ff')
        self.russian_btn.place(x=X, y=Y)

        self.login_btn['command'] = callbacks['login']
        self.register_btn['command'] = callbacks['register']
        self.play_guest_btn['command'] = callbacks['guest']
        self.english_btn['command'] = callbacks['english']
        self.spanish_btn['command'] = callbacks['spanish']
        self.russian_btn['command'] = callbacks['russian']

        self.update_language(language)

    def username(self):
        return self.username_entry.get()

    def password(self):
        return self.password_entry.get()

    def update_language(self, language):
        self.language = language
        self.username_label['text'] = language['USERNAME']
        self.password_label['text'] = language['PASSWORD']
        self.login_btn['text'] = language['LOGIN']
        self.register_btn['text'] = language['REGISTER']
        self.play_guest_btn['text'] = language['GUEST']

    @staticmethod
    def show_message(message):
        code, text = message
        if code == 'success':
            messagebox.showinfo("Login", text)
        else:
            messagebox.showerror("Login", text)
