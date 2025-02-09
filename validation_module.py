import tkinter as tk
from tkinter import ttk
import subprocess
import os

class ValidationSection:
    def __init__(self, master):
        self.master = master
        # Node.js 验证
        self.node_validate_button = ttk.Button(self.master, text="验证 Node.js", command=self.validate_node)
        self.node_validate_button.grid(row=0, column=0, padx=5, pady=5)

        # Java 验证
        self.java_validate_button = ttk.Button(self.master, text="验证 Java", command=self.validate_java)
        self.java_validate_button.grid(row=1, column=0, padx=5, pady=5)

        self.java_status = tk.StringVar()
        self.java_label = ttk.Label(self.master, textvariable=self.java_status)
        self.java_label.grid(row=1, column=1, padx=5, pady=5)

        self.node_status = tk.StringVar()
        self.node_label = ttk.Label(self.master, textvariable=self.node_status)
        self.node_label.grid(row=0, column=1, padx=5, pady=5)

        self.node_log_button = ttk.Button(self.master, text="Node.js 日志", command=lambda: self.show_log(self.node_log))
        self.node_log_button.grid(row=0, column=2, padx=5, pady=5)
        self.node_log_button.grid_remove()  # Initially hide the button
        self.node_log = ""

        self.java_log_button = ttk.Button(self.master, text="Java 日志", command=lambda: self.show_log(self.java_log))
        self.java_log_button.grid(row=1, column=2, padx=5, pady=5)
        self.java_log_button.grid_remove()  # Initially hide the button
        self.java_log = ""

    def validate_node(self):
        try:
            if os.name == 'nt':  # Windows 系统
                result = subprocess.run(["node", "-v"], check=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            else:  # 其他系统
                result = subprocess.run(["node", "-v"], check=True, capture_output=True, text=True)
            self.node_status.set("Node.js 可用")
            self.node_log = result.stdout
            self.node_log_button.grid()  # Show the button after validation
        except FileNotFoundError:
            self.node_status.set("未安装Node.js")
            tk.messagebox.showerror("错误", "Node.js 未找到. 请确保已安装并配置了环境变量.")
        except subprocess.CalledProcessError as e:
            self.node_status.set("Node.js 配置错误")
            tk.messagebox.showerror("错误", f"Node.js 验证失败: {e}")

    def validate_java(self):
        try:
            if os.name == 'nt':  # Windows 系统
                result = subprocess.run(["java", "-version"], check=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            else:  # 其他系统
                result = subprocess.run(["java", "-version"], check=True, capture_output=True, text=True)
            self.java_status.set("Java可用")
            self.java_log = result.stderr
            self.java_log_button.grid()  # Show the button after validation
        except FileNotFoundError:
            self.java_status.set("未安装Java")
        except subprocess.CalledProcessError:
            self.java_status.set("Java配置错误")

    def show_log(self, log_message):
        log_window = tk.Toplevel(self.master)
        log_window.title("执行日志")
        log_text = tk.Text(log_window, height=10, width=50)
        log_text.pack(padx=10, pady=10)
        log_text.insert(tk.END, log_message)
        log_text.config(state=tk.DISABLED)

    def run_validation(self):
        script_path = self.script_path_var.get()
        if os.path.exists(script_path):
            try:
                # 添加 creationflags 参数以隐藏控制台窗口
                subprocess.run([script_path], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
                self.validation_result_label.config(text="验证成功", foreground="green")
            except subprocess.CalledProcessError as e:
                self.validation_result_label.config(text=f"验证失败: {e}", foreground="red")
            except FileNotFoundError:
                self.validation_result_label.config(text="脚本文件未找到", foreground="red")
        else:
            self.validation_result_label.config(text="脚本文件路径无效", foreground="red")
