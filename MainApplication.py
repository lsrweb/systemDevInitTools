import tkinter as tk
from tkinter import ttk
import os
import shutil
import subprocess
import json
import time
from threading import Thread

# 导入各个模块
from setup_module import SetupSection
from env_config_module import EnvConfigSection
from env_vars_module import EnvVarsSection
from validation_module import ValidationSection

class EnvConfigurator:
    def __init__(self, master):
        self.master = master
        master.title("环境配置工具")

        # 配置文件路径
        self.config_dir = os.path.join(os.path.expanduser("~"), ".systools")
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.default_config = {
            "node_path": "",
            "java_path": ""
        }
        self.config = self.load_config()

        # 软件设置
        self.setup_frame = ttk.LabelFrame(master, text="软件设置")
        self.setup_frame.pack(padx=10, pady=10, fill=tk.X)

        # 环境配置
        self.env_frame = ttk.LabelFrame(master, text="环境配置")
        self.env_frame.pack(padx=10, pady=10, fill=tk.X)

        # 系统环境变量
        self.env_vars_frame = ttk.LabelFrame(master, text="系统环境变量")
        self.env_vars_frame.pack(padx=10, pady=10, fill=tk.X)

        # 环境功能验证
        self.validation_frame = ttk.LabelFrame(master, text="环境功能验证")
        self.validation_frame.pack(padx=10, pady=10, fill=tk.X)

        # 刷新环境变量
        self.refresh_button = ttk.Button(master, text="刷新环境变量", command=self.refresh_env)
        self.refresh_button.pack(pady=10)

        # 创建各个模块的实例
        self.setup_section = SetupSection(self.setup_frame)
        self.env_config_section = EnvConfigSection(self.env_frame, self.config, self.save_config)
        self.env_vars_section = EnvVarsSection(self.env_vars_frame)
        self.validation_section = ValidationSection(self.validation_frame)

        # 初始化 last_modified
        if os.path.exists(self.config_file):
            self.last_modified = os.path.getmtime(self.config_file)
        else:
            self.last_modified = 0

        # 启动配置文件监控线程
        self.config_monitor_thread = Thread(target=self.monitor_config_file, daemon=True)
        self.config_monitor_thread.start()

    def load_config(self):
        # 加载配置文件
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        if not os.path.exists(self.config_file):
            with open(self.config_file, "w") as f:
                json.dump(self.default_config, f, indent=4)
            return self.default_config
        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置文件失败: {e}, 使用默认配置")
            return self.default_config

    def save_config(self):
        # 保存配置文件
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=4)
            print("配置文件保存成功")
        except Exception as e:
            print(f"保存配置文件失败: {e}")

    def refresh_env(self):
        if os.name == 'nt':  # Windows 系统
            subprocess.Popen("powershell.exe -command \"[Environment]::SetEnvironmentVariable('Path', [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('Path', 'User')), 'Machine'\"", creationflags=subprocess.CREATE_NO_WINDOW)
        else:  # 其他系统（如 Linux 或 macOS）
            print("请手动刷新环境变量或重启终端。")

    def monitor_config_file(self):
        # 监控配置文件修改
        while True:
            try:
                if os.path.exists(self.config_file):
                    modified_time = os.path.getmtime(self.config_file)
                    if modified_time != self.last_modified:
                        self.master.after(0, self.config_file_changed)
                        self.last_modified = modified_time
                time.sleep(1)
            except Exception as e:
                print(f"监控配置文件出错: {e}")
                time.sleep(10)

    def config_file_changed(self):
        # 配置文件发生变化时的处理
        print("配置文件已修改，请重启应用以加载新配置。")
        tk.messagebox.showinfo("提示", "配置文件已修改，请重启应用以加载新配置。")

root = tk.Tk()
app = EnvConfigurator(root)
root.mainloop()
