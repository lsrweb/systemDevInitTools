import tkinter as tk
from tkinter import ttk
import os
from tkinter import filedialog
from tkinter import messagebox

class EnvConfigSection:
    def __init__(self, master, config, save_config):
        self.master = master
        self.config = config
        self.save_config = save_config

        # Node.js 配置
        node_label = ttk.Label(self.master, text="Node.js 目录:")
        node_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.node_path = tk.StringVar(value=self.config["node_path"])
        node_entry = ttk.Entry(self.master, textvariable=self.node_path, width=40)
        node_entry.grid(row=0, column=1, padx=5, pady=5)
        node_browse_button = ttk.Button(self.master, text="浏览", command=lambda: self.browse_directory(self.node_path))
        node_browse_button.grid(row=0, column=2, padx=5, pady=5)
        node_create_button = ttk.Button(self.master, text="创建目录", command=lambda: self.create_directory(self.node_path.get()))
        node_create_button.grid(row=0, column=3, padx=5, pady=5)

        # Java 配置
        java_label = ttk.Label(self.master, text="Java 目录:")
        java_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.java_path = tk.StringVar(value=self.config["java_path"])
        java_entry = ttk.Entry(self.master, textvariable=self.java_path, width=40)
        java_entry.grid(row=1, column=1, padx=5, pady=5)
        java_browse_button = ttk.Button(self.master, text="浏览", command=lambda: self.browse_directory(self.java_path))
        java_browse_button.grid(row=1, column=2, padx=5, pady=5)
        java_create_button = ttk.Button(self.master, text="创建目录", command=lambda: self.create_directory(self.java_path.get()))
        java_create_button.grid(row=1, column=3, padx=5, pady=5)

    def browse_directory(self, variable):
        directory = filedialog.askdirectory()
        if directory:
            variable.set(directory)
            self.update_config()

    def create_directory(self, path):
        try:
            os.makedirs(path, exist_ok=True)
            messagebox.showinfo("成功", "目录创建成功!")
            self.update_config()
        except Exception as e:
            messagebox.showerror("错误", f"创建目录失败: {e}")

    def update_config(self):
        self.config["node_path"] = self.node_path.get()
        self.config["java_path"] = self.java_path.get()
        self.save_config()
