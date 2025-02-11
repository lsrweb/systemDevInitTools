# This file has been moved and renamed to src/env_vars_section.py
import tkinter as tk
from tkinter import ttk
import os
import json
import subprocess

class EnvVarsSection:
    def __init__(self, master, config_dir):
        self.master = master
        self.config_dir = config_dir  # 保存配置文件目录
        # ... (显示、备份和恢复环境变量的GUI元素) ...
        backup_button = ttk.Button(self.master, text="备份环境变量", command=self.backup_env_vars)
        backup_button.grid(row=0, column=0, padx=5, pady=5)

    def backup_env_vars(self):
        """备份当前环境变量到JSON文件，区分用户和系统环境变量."""
        try:
            # 获取所有环境变量
            env_vars = dict(os.environ)

            # 分离用户环境变量和系统环境变量 (Windows)
            user_env_vars = {}
            system_env_vars = {}
            if os.name == 'nt':
                import winreg
                # 读取用户环境变量
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment")
                try:
                    i = 0
                    while True:
                        name, value, type = winreg.EnumValue(key, i)
                        user_env_vars[name] = value
                        i += 1
                except WindowsError:
                    pass  # 枚举完成

                # 读取系统环境变量
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"System\CurrentControlSet\Control\Session Manager\Environment")
                try:
                    i = 0
                    while True:
                        name, value, type = winreg.EnumValue(key, i)
                        system_env_vars[name] = value
                        i += 1
                except WindowsError:
                    pass  # 枚举完成
                winreg.CloseKey(key)
            else:
                # 对于非 Windows 系统，简单地将所有环境变量视为用户环境变量
                user_env_vars = env_vars

            # 使用配置文件目录作为备份文件的保存路径
            user_backup_file = os.path.join(self.config_dir, "user_env_vars_backup.json")
            system_backup_file = os.path.join(self.config_dir, "system_env_vars_backup.json")

            # 将用户环境变量写入JSON文件
            with open(user_backup_file, 'w') as f:
                json.dump(user_env_vars, f, indent=4)  # 使用indent使JSON文件更易读

            # 将系统环境变量写入JSON文件
            if os.name == 'nt':  # 仅在Windows上备份系统环境变量
                with open(system_backup_file, 'w') as f:
                    json.dump(system_env_vars, f, indent=4)  # 使用indent使JSON文件更易读
                print(f"用户环境变量已备份到 {user_backup_file}")  # 在控制台输出备份成功的消息
                print(f"系统环境变量已备份到 {system_backup_file}")  # 在控制台输出备份成功的消息
                self.show_message(f"用户环境变量已备份到 {user_backup_file}\n系统环境变量已备份到 {system_backup_file}")  # 在GUI中显示消息
            else:
                 print(f"环境变量已备份到 {user_backup_file}")  # 在控制台输出备份成功的消息
                 self.show_message(f"环境变量已备份到 {user_backup_file}")  # 在GUI中显示消息

        except Exception as e:
            print(f"备份环境变量时出错: {e}")
            self.show_message(f"备份环境变量时出错: {e}")

    def show_message(self, message):
        """在GUI中显示消息."""
        message_label = ttk.Label(self.master, text=message)
        message_label.grid(row=5, column=0, columnspan=2, padx=5, pady=5)