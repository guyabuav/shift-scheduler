import tkinter as tk
from models.login import LoginManager


class LoginGUI:
    def __init__(self, root, on_login_success):
        self.root = root
        self.root.title("Login")
        self.login_manager = LoginManager()
        self.on_login_success = on_login_success

        tk.Label(root, text="Username:").grid(row=0, column=0, padx=5, pady=5)
        self.username_entry = tk.Entry(root)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(root, text="Password:").grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = tk.Entry(root, show="*")  # הסיסמה תופיע מוסתרת
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        login_button = tk.Button(root, text="Login", command=self.login)
        login_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        self.message_label = tk.Label(root, text="", fg="red")
        self.message_label.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        role = self.login_manager.authenticate_user(username, password)

        if role:
            self.root.destroy()
            self.on_login_success(username, role)
        else:
            self.message_label.config(text="Invalid login, try again")