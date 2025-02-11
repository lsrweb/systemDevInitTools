import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import importlib
import importlib.util

name = "Gradle 配置"

def is_module_installed(module_name):
    """检查模块是否已安装"""
    return importlib.util.find_spec(module_name) is not None

def install_module(module_name):
    """安装指定的模块"""
    try:
        subprocess.check_call([
            sys.executable, 
            "-m", 
            "pip", 
            "install", 
            "--disable-pip-version-check",
            module_name
        ])
        return True
    except subprocess.CalledProcessError:
        return False

# 检查并安装 requests
if not is_module_installed('requests'):
    print("Installing requests module...")
    if not install_module('requests'):
        raise ImportError("Failed to install requests module")
    # 重新加载 sys.modules 缓存
    importlib.invalidate_caches()

# 现在安全地导入 requests
import requests
import zipfile
import json

GRADLE_VERSIONS_URL = "https://services.gradle.org/versions/all"
DEFAULT_GRADLE_HOME = os.path.expanduser("~/.gradle")
GRADLE_BIN_NAME = "bin" if os.name == 'nt' else "bin/gradle"
LOCAL_VERSIONS_KEY = "gradle_installed_versions"

def download_gradle(version, target_path):
    """下载指定版本的 Gradle."""
    download_url = f"https://services.gradle.org/distributions/gradle-{version}-bin.zip"
    response = requests.get(download_url, stream=True)
    zip_path = os.path.join(target_path, f"gradle-{version}.zip")
    
    with open(zip_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(target_path)
    
    os.remove(zip_path)
    return os.path.join(target_path, f"gradle-{version}")

def get_remote_versions():
    """获取远程可用的 Gradle 版本."""
    try:
        response = requests.get(GRADLE_VERSIONS_URL)
        versions = response.json()
        return [v['version'] for v in versions if not v.get('snapshot')]
    except Exception as e:
        print(f"获取远程版本失败: {e}")
        return []

def verify_gradle_version():
    """验证当前系统的 Gradle 版本."""
    try:
        result = subprocess.run(['gradle', '--version'], 
                              capture_output=True, 
                              text=True)
        return result.stdout
    except Exception as e:
        return f"验证失败: {str(e)}"

def get_local_versions(config):
    """获取本地安装的版本列表."""
    return config.get(LOCAL_VERSIONS_KEY, [])

def set_active_version(version_path):
    """设置活动版本到系统环境变量."""
    gradle_bin = os.path.join(version_path, GRADLE_BIN_NAME)
    if os.name == 'nt':  # Windows
        subprocess.run(['setx', 'PATH', f"%PATH%;{gradle_bin}"], shell=True)
    else:  # Unix-like
        # 更新 ~/.bashrc 或 ~/.zshrc
        pass

def register(api):
    """注册插件."""
    config = api.get_config()
    if LOCAL_VERSIONS_KEY not in config:
        config[LOCAL_VERSIONS_KEY] = []
    if "gradle_home" not in config:
        config["gradle_home"] = DEFAULT_GRADLE_HOME
    # 使用静默保存避免触发重启提示
    api.save_config(silent=True)

def gui(master, app):
    """插件 GUI 界面."""
    notebook = ttk.Notebook(master)
    notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # 本地版本管理标签页
    local_frame = ttk.Frame(notebook)
    notebook.add(local_frame, text="本地版本")

    # 远程版本标签页
    remote_frame = ttk.Frame(notebook)
    notebook.add(remote_frame, text="远程版本")

    # 版本验证标签页
    verify_frame = ttk.Frame(notebook)
    notebook.add(verify_frame, text="版本验证")

    # === 本地版本管理 ===
    local_versions = get_local_versions(app.plugin_api.get_config())
    
    version_list = tk.Listbox(local_frame, height=6)
    version_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    for version in local_versions:
        version_list.insert(tk.END, version)

    def set_active():
        selection = version_list.curselection()
        if selection:
            version_path = local_versions[selection[0]]
            try:
                set_active_version(version_path)
                # 静默更新配置
                app.plugin_api.set_config("gradle_active_version", version_path, silent=True)
                messagebox.showinfo("成功", "Gradle 版本已更新，请重启终端使环境变量生效")
            except Exception as e:
                messagebox.showerror("错误", f"设置版本失败: {str(e)}")

    ttk.Button(local_frame, text="设为活动版本", 
               command=set_active).pack(pady=5)

    # === 远程版本管理 ===
    remote_list = tk.Listbox(remote_frame, height=6)
    remote_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def refresh_remote_versions():
        remote_list.delete(0, tk.END)
        versions = get_remote_versions()
        for version in versions:
            remote_list.insert(tk.END, version)

    def download_selected():
        selection = remote_list.curselection()
        if selection:
            version = remote_list.get(selection)
            install_path = app.plugin_api.get_config("gradle_home")
            try:
                gradle_path = download_gradle(version, install_path)
                local_versions = get_local_versions(app.plugin_api.get_config())
                local_versions.append(gradle_path)
                # 静默更新版本列表
                app.plugin_api.set_config(LOCAL_VERSIONS_KEY, local_versions, silent=True)
                version_list.insert(tk.END, gradle_path)
                messagebox.showinfo("成功", f"Gradle {version} 已下载")
            except Exception as e:
                messagebox.showerror("错误", f"下载失败: {str(e)}")

    ttk.Button(remote_frame, text="刷新版本列表", 
               command=refresh_remote_versions).pack(pady=5)
    ttk.Button(remote_frame, text="下载选中版本", 
               command=download_selected).pack(pady=5)

    # === 版本验证 ===
    verify_text = tk.Text(verify_frame, height=10, width=50)
    verify_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def verify_version():
        verify_text.delete(1.0, tk.END)
        result = verify_gradle_version()
        verify_text.insert(tk.END, result)

    ttk.Button(verify_frame, text="验证当前版本", 
               command=verify_version).pack(pady=5)

    # 初始加载远程版本
    refresh_remote_versions()
