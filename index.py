import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime
import os

class LoginCadastroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Login/Cadastro")
        
        # Conectar ao banco de dados SQLite
        self.conn = sqlite3.connect("tasks.db")
        self.cursor = self.conn.cursor()
        self.create_tables()
        
        self.username_label = tk.Label(root, text="Usuário:")
        self.username_label.grid(row=0, column=0, padx=10, pady=5)
        self.username_entry = tk.Entry(root)
        self.username_entry.grid(row=0, column=1, padx=10, pady=5)
        
        self.password_label = tk.Label(root, text="Senha:")
        self.password_label.grid(row=1, column=0, padx=10, pady=5)
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=5)
        
        self.login_button = tk.Button(root, text="Login", command=self.login)
        self.login_button.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="we")
        
        self.cadastro_button = tk.Button(root, text="Cadastro", command=self.cadastro)
        self.cadastro_button.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="we")
        
    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                             username TEXT NOT NULL UNIQUE,
                             password TEXT NOT NULL)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS tasks
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                             task TEXT NOT NULL)''')
        self.conn.commit()
        
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        self.cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = self.cursor.fetchone()
        
        if user:
            messagebox.showinfo("Login", "Login bem-sucedido!")
            self.generate_log(username)
            self.open_task_manager()
        else:
            messagebox.showerror("Login", "Usuário ou senha inválidos.")
            
    def cadastro(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        try:
            self.cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            self.conn.commit()
            messagebox.showinfo("Cadastro", "Cadastro realizado com sucesso.")
            self.generate_log(username)
            self.open_task_manager()
        except sqlite3.IntegrityError:
            messagebox.showerror("Cadastro", "Usuário já existe.")
    
    def open_task_manager(self):
        self.root.destroy()
        root = tk.Tk()
        app = TaskManager(root)
        root.mainloop()
    
    def generate_log(self, username):
        log_folder = "logs"
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)
        log_file = os.path.join(log_folder, "login_log.txt")
        with open(log_file, "a") as f:
            login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"Usuário {username} fez login em {login_time}\n")

class TaskManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador de Tarefas")
        
        self.task_label = tk.Label(root, text="Tarefa:")
        self.task_label.grid(row=0, column=0, padx=10, pady=5)
        self.task_entry = tk.Entry(root)
        self.task_entry.grid(row=0, column=1, padx=10, pady=5)
        
        self.add_button = tk.Button(root, text="Adicionar", command=self.add_task)
        self.add_button.grid(row=0, column=2, padx=10, pady=5)
        
        self.task_listbox = tk.Listbox(root, width=50, height=15)
        self.task_listbox.grid(row=1, column=0, columnspan=3, padx=10, pady=5)
        
        self.view_tasks()
    
    def add_task(self):
        task = self.task_entry.get()
        if task:
            self.insert_task(task)
            self.task_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Adicionar Tarefa", "Por favor, insira uma tarefa.")
    
    def insert_task(self, task):
        conn = sqlite3.connect("tasks.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (task) VALUES (?)", (task,))
        conn.commit()
        conn.close()
        self.view_tasks()
    
    def view_tasks(self):
        self.task_listbox.delete(0, tk.END)
        conn = sqlite3.connect("tasks.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks")
        rows = cursor.fetchall()
        conn.close()
        for row in rows:
            self.task_listbox.insert(tk.END, row[1])

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginCadastroApp(root)
    root.mainloop()
