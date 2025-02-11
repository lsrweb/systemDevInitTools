import tkinter as tk
from tkinter import ttk

# 示例插件
name = "Gradle 下载tese"  # 插件名称

def register(api):
    """注册插件."""
    # 使用主程序的 API
    config = api.get_config()

def gui(master, app):
    """插件 GUI 界面."""
    label = ttk.Label(master, text="This is the example plugin GUI.")
    label.pack(padx=10, pady=10)

    def update_node_path():
        new_path = entry.get()
        app.plugin_api.set_config("node_path", new_path)  # 使用 plugin_api
        print(f"node_path updated to: {new_path}")

    entry = ttk.Entry(master)
    entry.pack(padx=10, pady=10)

    update_button = ttk.Button(master, text="Update Node Path", command=update_node_path)
    update_button.pack(padx=10, pady=10)
