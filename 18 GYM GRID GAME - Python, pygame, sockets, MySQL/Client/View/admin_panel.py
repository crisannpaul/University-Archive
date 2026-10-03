from tkinter import *
from tkinter import messagebox
from PIL import ImageTk, Image

WIDTH = 800
HEIGHT = 400


class AdminPanel(object):
    def __init__(self, window, callbacks, language):
        self.window = window
        self.window.geometry(f'{WIDTH}x{HEIGHT}')
        self.window.title('Admin')

        # ====== Admin Panel Frame =========================
        self.admin_frame = Frame(self.window, width=WIDTH, height=HEIGHT)
        self.admin_frame.config(bg="white")
        self.admin_frame.place(x=0, y=0)

        # ========================================================================
        # ============================background image============================
        # ========================================================================
        self.bg_frame = Image.open('View/images/login_background.jpg')
        self.bg_frame = self.bg_frame.resize((WIDTH, HEIGHT))
        photo = ImageTk.PhotoImage(self.bg_frame)
        self.bg_panel = Label(self.admin_frame, image=photo)
        self.bg_panel.image = photo
        self.bg_panel.pack(fill='both', expand='yes')

        # ========================================================================
        # ===============================sql entry================================
        # ========================================================================
        X, Y = 20, 200
        self.sql_entry = Text(self.admin_frame, height=4, width=35, bg="white", fg="black",
                              font=("yu gothic ui", 15, "bold"), cursor="arrow", bd=2)
        self.sql_entry.insert(chars="*SQL goes here*", index="1.0")
        self.sql_entry.place(x=X, y=Y)

        # ========================================================================
        # =============================execute btn================================
        # ========================================================================
        X, Y = 20, 325
        self.execute_btn = Button(self.admin_frame, text='Execute', relief=RAISED,
                                  font=("yu gothic ui", 16, "bold"), width=15, bd=2,
                                  bg='#3047ff', cursor='hand2', activebackground='#3047ff', fg='white')
        self.execute_btn.place(x=X, y=Y)

        # ========================================================================
        # ===========================statistics btn===============================
        # ========================================================================
        X, Y = 220, 325
        self.statistics_btn = Button(self.admin_frame, text='Statistics', relief=RAISED,
                                  font=("yu gothic ui", 16, "bold"), width=15, bd=2,
                                  bg='#3047ff', cursor='hand2', activebackground='#3047ff', fg='white')
        self.statistics_btn.place(x=X, y=Y)

        # ========================================================================
        # ============================users label=================================
        # ========================================================================
        X, Y = 20, 20
        self.users_label = Label(self.admin_frame, text="Registered users:", bg="white", fg="black",
                                 font=("yu gothic ui", 20, "bold"), cursor="arrow")
        self.users_label.place(x=X, y=Y)

        # ========================================================================
        # ============================users list==================================
        # ========================================================================
        X, Y = 20, 60
        self.users_list = Listbox(self.admin_frame, bg="white", fg="black", height=4, width=25,
                                  font=("yu gothic ui", 16, "bold"), cursor="arrow")
        self.users_list.place(x=X, y=Y)

        # =========================================================================
        # ==============================back btn==================================
        # =========================================================================
        X, Y = 2, 3
        self.back_btn = Button(self.admin_frame, text='< Back', borderwidth=0,
                               font=("yu gothic ui", 8, "bold"), width=5,
                               bg="white", cursor='hand2', fg='#3047ff')
        self.back_btn.place(x=X, y=Y)

        self.execute_btn['command'] = callbacks['execute']
        self.statistics_btn['command'] = callbacks['statistics']
        self.back_btn['command'] = callbacks['back']

        self.execute_btn['text'] = language['EXECUTE']
        self.back_btn['text'] = language['BACK']
        self.users_label['text'] = language['REGISTERED USERS']

    def get_input(self):
        return self.sql_entry.get("1.0", 'end-1c')

    def update_list(self, users_list):
        self.users_list.delete(0, END)
        for index, user in enumerate(users_list):
            text = f"{index+1}. {user[1]} - {user[5]}"
            self.users_list.insert(index, text)

    @staticmethod
    def show_message(message):
        text, code = message
        if code == 0:
            messagebox.showinfo("SQL", text)
        else:
            messagebox.showerror("SQL", text)
