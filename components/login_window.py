import tkinter as tk
from tkinter import ttk, messagebox
from utils.logger import operation_logger, error_logger

class LoginWindow(tk.Toplevel):
    """
        Simple login window that checks credentials via DBManager.
        On success, sets self.master.current_user and closes.
    """
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager
        self.title("Login")
        self.geometry("300x180")
        self.resizable(False, False)

        ttk.Label(self, text="Username:").pack(pady=5)
        self.username_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.username_var).pack(pady=5)

        ttk.Label(self, text="Password:").pack(pady=5)
        self.password_var = tk.StringVar()
        ttk.Entry(self, show="*", textvariable=self.password_var).pack(pady=5)

        frm = ttk.Frame(self)
        frm.pack(pady=5)
        ttk.Button(frm, text="Login", command=self.on_login).pack(side=tk.LEFT, padx=5)
        ttk.Button(frm, text="Register", command=self.on_register).pack(side=tk.LEFT, padx=5)

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.grab_set()
        self.focus()
        operation_logger.info("LoginWindow opened.")

    def on_close(self):
        """ Handle the window close event by terminating the application. """
        operation_logger.info("LoginWindow closed by user.")
        self.master.destroy()

    def on_login(self):
        """ Attempt to log in the user with provided credentials. """
        user = self.username_var.get().strip()
        pwd = self.password_var.get().strip()
        if not user or not pwd:
            messagebox.showerror("Error", "Please enter both username and password.")
            error_logger.warning("Login attempt with empty username or password.")
            return
        if self.db_manager.check_user_credentials(user, pwd):
            self.master.current_user = user
            operation_logger.info(f"User logged in: {user}")
            self.destroy()
        else:
            messagebox.showerror("Error", "Invalid credentials.")
            error_logger.warning(f"Invalid login attempt for user: {user}")

    def on_register(self):
        """ Attempt to register a new user with provided credentials. """
        user = self.username_var.get().strip()
        pwd = self.password_var.get().strip()
        if not user or not pwd:
            messagebox.showerror("Error", "Please enter both username and password.")
            error_logger.warning("Registration attempt with empty username or password.")
            return
        ok, msg = self.db_manager.add_user(user, pwd)
        if not ok:
            messagebox.showerror("Error", msg)
            error_logger.error(f"Registration failed for user: {user}, Reason: {msg}")
        else:
            messagebox.showinfo("Registered", msg)
            operation_logger.info(f"User registered successfully: {user}")
