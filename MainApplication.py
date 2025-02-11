import tkinter as tk
from tkinter import ttk
import os
import shutil
import subprocess
import json
import time
from threading import Thread
import sys  # 导入 sys 模块
import importlib
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk  # 导入 PIL 库

# 导入各个模块
from setup_module import SetupSection
from env_config_module import EnvConfigSection
from env_vars_module import EnvVarsSection
from validation_module import ValidationSection
from plugin_api import PluginAPI  # 导入 PluginAPI


class EnvConfigurator:
    def __init__(self, master):
        self.master = master
        master.title("环境配置工具")

        # 配置文件路径
        self.config_dir = os.path.join(os.path.expanduser("~"), ".systools")
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.plugins_dir = os.path.join(self.config_dir, "plugins")  # 插件目录
        self.plugins_json = os.path.join(self.config_dir, "plugins.json")  # 插件列表文件

        self.default_config = {
            "node_path": "",
            "java_path": ""
        }
        self.config = self.load_config()

        # 插件列表
        self.plugins = []
        self.plugin_buttons = {}  # 添加插件按钮字典

        # 创建 PluginAPI 实例
        self.plugin_api = PluginAPI(self)

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

        # 扩展区
        self.extension_frame = ttk.LabelFrame(master, text="扩展区")
        self.extension_frame.pack(padx=10, pady=10, fill=tk.X)

        # 插件按钮容器
        self.plugin_button_frame = ttk.Frame(self.extension_frame)
        self.plugin_button_frame.pack(padx=5, pady=5, fill=tk.X)

        # 暂无插件标签
        self.no_plugins_label = ttk.Label(self.plugin_button_frame, text="暂无插件")
        self.no_plugins_label.pack(padx=5, pady=5)

        # 按钮容器
        button_frame = ttk.Frame(master)
        button_frame.pack(pady=10)

        # 刷新环境变量
        self.refresh_button = ttk.Button(button_frame, text="刷新环境变量", command=self.refresh_env)
        self.refresh_button.grid(row=0, column=0, padx=5)

        # 重启应用按钮
        self.restart_button = ttk.Button(button_frame, text="重启应用", command=self.restart_application)
        self.restart_button.grid(row=0, column=1, padx=5)

        # 退出应用按钮
        self.exit_button = ttk.Button(button_frame, text="退出", command=self.exit_application)
        self.exit_button.grid(row=0, column=2, padx=5)

        # 选择插件按钮
        self.select_plugin_button = ttk.Button(button_frame, text="选择插件", command=self.select_plugin)
        self.select_plugin_button.grid(row=0, column=3, padx=5)

        # 创建各个模块的实例
        self.setup_section = SetupSection(self.setup_frame)
        self.env_config_section = EnvConfigSection(self.env_frame, self.config, self.save_config)
        # 将 config_dir 传递给 EnvVarsSection
        self.env_vars_section = EnvVarsSection(self.env_vars_frame, self.config_dir)
        self.validation_section = ValidationSection(self.validation_frame)

        # 初始化 last_modified
        if os.path.exists(self.config_file):
            self.last_modified = os.path.getmtime(self.config_file)
        else:
            self.last_modified = 0

        # 启动配置文件监控线程
        self.config_monitor_thread = Thread(target=self.monitor_config_file, daemon=True)
        self.config_monitor_thread.start()

        # 加载插件
        self.load_plugins()

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

    def restart_application(self):
        # 重启应用
        print("重启应用...")
        try:
            # 获取当前 Python 解释器路径
            python_exe = sys.executable
            # 获取当前脚本路径
            script_path = os.path.abspath(__file__)
            # 使用 subprocess 启动一个新的进程
            subprocess.Popen([python_exe, script_path])
            # 关闭当前应用
            self.master.destroy()
        except Exception as e:
            print(f"重启应用失败: {e}")
            tk.messagebox.showerror("错误", f"重启应用失败: {e}")

    def exit_application(self):
        # 退出应用
        print("退出应用...")
        self.master.destroy()

    def select_plugin(self):
        """选择插件文件."""
        file_path = filedialog.askopenfilename(
            title="选择插件文件",
            filetypes=[("Python Files", "*.py")]
        )
        if file_path:
            self.load_plugin(file_path)

    def load_plugins(self):
        """加载插件."""
        if not os.path.exists(self.plugins_dir):
            os.makedirs(self.plugins_dir)

        try:
            with open(self.plugins_json, "r") as f:
                plugin_files = json.load(f)
        except Exception:
            plugin_files = []

        # 清空现有插件和按钮
        self.plugins = []
        self.clear_plugin_buttons()

        # 加载插件
        for filename in plugin_files:
            plugin_path = os.path.join(self.plugins_dir, filename)
            if os.path.exists(plugin_path):
                self.load_plugin(plugin_path)

        # 更新插件区域显示
        if not self.plugins:
            self.no_plugins_label = ttk.Label(self.plugin_button_frame, text="暂无插件")
            self.no_plugins_label.pack(padx=5, pady=5)

    def load_plugin(self, plugin_path):
        """加载单个插件."""
        plugin_name = os.path.basename(plugin_path)[:-3]
        try:
            # 尝试使用 importlib.util
            if hasattr(importlib, 'util'):
                spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
                plugin_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(plugin_module)
            else:
                # 如果 importlib.util 不可用，则使用 importlib.import_module 模块
                # 需要将文件所在目录添加到 sys.path
                plugin_dir = os.path.dirname(plugin_path)
                sys.path.insert(0, plugin_dir)  # 临时添加到搜索路径
                plugin_module = importlib.import_module(plugin_name)
                sys.path.pop(0)  # 移除临时添加的搜索路径

            # 注册插件
            self.register_plugin(plugin_module, plugin_path)
            print(f"插件 {plugin_name} 加载成功")
        except Exception as e:
            print(f"加载插件 {plugin_name} 失败: {e}")
            messagebox.showerror("加载插件失败", f"无法加载插件 {plugin_name}: {e}")

    def register_plugin(self, plugin, plugin_path):
        """注册插件."""
        try:
            # 插件必须有一个 name 属性
            if not hasattr(plugin, 'name'):
                raise ValueError("插件必须有一个 name 属性")

            # 获取插件名称
            plugin_name = plugin.name

            # 获取插件文件名
            plugin_filename = os.path.basename(plugin_path)

            # 检测同名插件
            existing_plugin = self.find_plugin_by_name(plugin_name)
            print(f"existing_plugin: {existing_plugin}")
            if (existing_plugin):
                print(f"发现同名插件 {plugin_name}，将替换旧插件")
                # 删除旧插件
                self.remove_plugin(existing_plugin)

            # 插件必须有一个 register 函数
            plugin.register(self.plugin_api)  # 传递 plugin_api 实例
            self.plugins.append(plugin)
            print(f"插件 {plugin_name} 注册成功")

            # 复制插件到插件目录
            dest_path = os.path.join(self.plugins_dir, plugin_filename)
            if not os.path.exists(dest_path):
                shutil.copy(plugin_path, dest_path)

            # 更新 plugins.json 文件
            self.update_plugins_json(plugin_filename)

            # 创建插件按钮
            self.create_plugin_button(plugin)

            # 移除“暂无插件”标签
            self.no_plugins_label.destroy()

        except Exception as e:
            print(f"注册插件 {plugin.__name__} 失败: {e}")
            messagebox.showerror("注册插件失败", f"无法注册插件: {e}")

    def create_plugin_button(self, plugin):
        """创建插件按钮。"""
        button_frame = ttk.Frame(self.plugin_button_frame)
        button_frame.pack(side=tk.LEFT, padx=5, pady=5)

        plugin_button = ttk.Button(
            button_frame,
            text=plugin.name,
            command=lambda: self.show_plugin_gui(plugin)
        )
        plugin_button.pack(side=tk.LEFT, padx=2)

        remove_button = ttk.Button(
            button_frame,
            text="删除",
            command=lambda: self.confirm_remove_plugin(plugin)
        )
        remove_button.pack(side=tk.LEFT, padx=2)

        # 保存按钮引用
        self.plugin_buttons[plugin.name] = button_frame

    def show_plugin_gui(self, plugin):
        """显示插件 GUI 界面。"""
        try:
            # 插件必须有一个 gui 函数
            if hasattr(plugin, 'gui'):
                plugin_window = tk.Toplevel(self.master)
                plugin.gui(plugin_window, self)  # 传递主窗口和app实例

                # 添加关闭按钮
                close_button = ttk.Button(plugin_window, text="关闭", command=plugin_window.destroy)
                close_button.pack(padx=5, pady=5)
            else:
                messagebox.showinfo("提示", "该插件没有 GUI 界面")
        except Exception as e:
            print(f"显示插件 {plugin.name} GUI 失败: {e}")
            messagebox.showerror("错误", f"无法显示插件 {plugin.name} GUI: {e}")

    def update_plugins_json(self, plugin_name):
        """更新 plugins.json 文件。"""
        if os.path.exists(self.plugins_json):
            try:
                with open(self.plugins_json, "r") as f:
                    plugin_files = json.load(f)
            except Exception as e:
                print(f"加载 plugins.json 失败: {e}")
                plugin_files = []
        else:
            plugin_files = []

        if plugin_name not in plugin_files:
            plugin_files.append(plugin_name)

        try:
            with open(self.plugins_json, "w") as f:
                json.dump(plugin_files, f, indent=4)
            print("plugins.json 更新成功")
        except Exception as e:
            print(f"更新 plugins.json 失败: {e}")

    def clear_plugin_buttons(self):
        """清空插件按钮区域。"""
        for button_frame in self.plugin_buttons.values():
            button_frame.destroy()
        self.plugin_buttons.clear()
        
        if hasattr(self, 'no_plugins_label'):
            self.no_plugins_label.destroy()

    def find_plugin_by_name(self, plugin_name):
        """根据插件名称查找插件。"""
        for plugin in self.plugins:
            if plugin.name == plugin_name:
                return plugin
        return None

    def remove_plugin(self, plugin):
        """移除插件。"""
        try:
            plugin_name = plugin.name
            plugin_filename = os.path.basename(plugin.__file__)
            plugin_path = os.path.join(self.plugins_dir, plugin_filename)

            # 从列表中移除插件
            self.plugins.remove(plugin)

            # 从文件系统中删除插件文件
            if os.path.exists(plugin_path):
                try:
                    os.remove(plugin_path)
                except PermissionError:
                    print(f"无法删除插件文件 {plugin_path}，将在应用重启后删除")

            # 更新 plugins.json
            self.remove_plugin_from_json(plugin_filename)

            # 删除插件按钮
            if plugin_name in self.plugin_buttons:
                self.plugin_buttons[plugin_name].destroy()
                del self.plugin_buttons[plugin_name]

            # 如果没有插件了，显示"暂无插件"标签
            if not self.plugins:
                self.no_plugins_label = ttk.Label(self.plugin_button_frame, text="暂无插件")
                self.no_plugins_label.pack(padx=5, pady=5)

            print(f"插件 {plugin_name} 移除成功")
            
        except Exception as e:
            print(f"移除插件 {plugin.name} 失败: {e}")
            messagebox.showerror("移除插件失败", f"无法移除插件 {plugin.name}: {e}")

    def remove_plugin_from_json(self, plugin_name):
        """从 plugins.json 文件中移除插件。"""
        try:
            # 读取 plugins.json 文件
            with open(self.plugins_json, "r") as f:
                plugin_files = json.load(f)

            # 移除插件
            plugin_files = [f for f in plugin_files if f != plugin_name]

            # 写入 plugins.json 文件
            with open(self.plugins_json, "w") as f:
                json.dump(plugin_files, f, indent=4)

            print("plugins.json 更新成功")
        except Exception as e:
            print(f"更新 plugins.json 失败: {e}")

    def confirm_remove_plugin(self, plugin):
        """确认是否移除插件。"""
        if messagebox.askokcancel("确认", f"确定要移除插件 {plugin.name} 吗？"):
            self.remove_plugin(plugin)

root = tk.Tk()
app = EnvConfigurator(root)
root.mainloop()
