from tkinter import *
from tkinter import messagebox
from PIL import ImageTk, Image

# from presenter import Controller

WIDTH = 700
HEIGHT = 250


class Register(object):
    def __init__(self, window, callbacks, language):
        self.window = window
        self.window.geometry(f'{WIDTH}x{HEIGHT}')
        self.window.title('Register')
        self.language = language

        # ====== Login Frame =========================
        self.reg_frame = Frame(self.window, bg="white", width=WIDTH, height=HEIGHT)
        self.reg_frame.config(bg="white")
        self.reg_frame.place(x=0, y=0)

        # ========================================================================
        # ============================background image============================
        # ========================================================================
        self.bg_frame = Image.open('View/images/register_background.jpg')
        self.bg_frame = self.bg_frame.resize((WIDTH, HEIGHT))
        photo = ImageTk.PhotoImage(self.bg_frame)
        self.bg_panel = Label(self.reg_frame, image=photo)
        self.bg_panel.image = photo
        self.bg_panel.pack(fill='both', expand='yes')

        # ========================================================================
        # ============================username====================================
        # ========================================================================
        X, Y = 40, 40
        self.username_label = Label(self.reg_frame, text="Username:", bg="white", fg="black",
                                    font=("yu gothic ui", 20, "bold"), cursor="arrow")
        self.username_label.place(x=X, y=Y)

        self.username_entry = Entry(self.reg_frame, highlightthickness=0, relief=SUNKEN, bg="white", fg="black",
                                    font=("yu gothic ui ", 20, "bold"), insertbackground='#000000', width=10)
        self.username_entry.place(x=4.5 * X, y=Y, width=270)

        # ========================================================================
        # ============================  email=====================================
        # ========================================================================
        X, Y = 40, 80
        self.email_label = Label(self.reg_frame, text="Email:", bg="white", fg="black",
                                 font=("yu gothic ui", 20, "bold"), cursor="arrow")
        self.email_label.place(x=X + 30, y=Y)

        self.email_entry = Entry(self.reg_frame, highlightthickness=0, relief=SUNKEN, bg="white", fg="black",
                                 font=("yu gothic ui ", 20, "bold"), insertbackground='#000000', width=10)
        self.email_entry.place(x=4.5 * X, y=Y, width=270)

        # ========================================================================
        # ============================password====================================
        # ========================================================================
        X, Y = 40, 120
        self.password_label = Label(self.reg_frame, text="Password:", bg="white", fg="black",
                                    font=("yu gothic ui", 20, "bold"), cursor="arrow")
        self.password_label.place(x=X + 5, y=Y)

        self.password_entry = Entry(self.reg_frame, highlightthickness=0, relief=SUNKEN, bg="white", fg="black",
                                    font=("yu gothic ui ", 20, "bold"), insertbackground='#000000', width=10)
        self.password_entry.place(x=4.5 * X, y=Y, width=270)

        # =========================================================================
        # ==========================register btn===================================
        # =========================================================================
        X, Y = 160, 170
        self.register_btn = Button(self.reg_frame, text='REGISTER', relief=RAISED,
                                   font=("yu gothic ui", 13, "bold"), width=18, bd=1,
                                   bg='#3047ff', cursor='hand2', activebackground='#3047ff', fg='white')
        self.register_btn.place(x=X, y=Y)

        # =========================================================================
        # ==============================back btn===================================
        # =========================================================================
        X, Y = 2, 5
        self.back_btn = Button(self.reg_frame, text='< Back', borderwidth=0,
                               font=("yu gothic ui", 10, "bold"), width=5,
                               bg="white", cursor='hand2', fg='#3047ff')
        self.back_btn.place(x=X, y=Y)

        self.register_btn['command'] = callbacks['register']
        self.back_btn['command'] = callbacks['back']

        self.username_label['text'] = language['USERNAME']
        self.email_label['text'] = language['EMAIL']
        self.password_label['text'] = language['PASSWORD']
        self.register_btn['text'] = language['REGISTER']
        self.back_btn['text'] = language['BACK']

    def username(self):
        return self.username_entry.get()

    def email(self):
        return self.email_entry.get()

    def password(self):
        return self.password_entry.get()

    @staticmethod
    def show_message(message):
        code, text = message
        if code == 'success':
            messagebox.showinfo("Register", text)
        else:
            messagebox.showerror("Register", text)
