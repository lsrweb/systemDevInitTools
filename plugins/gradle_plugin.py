import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
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

def download_gradle(version, target_path, plugin_api):
    """下载指定版本的 Gradle."""
    # 验证并确保目标路径存在
    if not plugin_api.validate_path(target_path):
        raise ValueError(f"无效的目标路径: {target_path}")
        
    if not plugin_api.ensure_dir_exists(target_path):
        raise ValueError(f"无法创建目标目录: {target_path}")
    
    download_url = f"https://services.gradle.org/distributions/gradle-{version}-bin.zip"
    response = requests.get(download_url, stream=True)
    zip_path = os.path.join(target_path, f"gradle-{version}.zip")
    
    # 获取文件总大小
    total_size = int(response.headers.get('content-length', 0))
    block_size = 8192
    downloaded = 0
    
    try:
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=block_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    # 计算下载进度百分比
                    if total_size:
                        progress = int((downloaded / total_size) * 100)
                        plugin_api.set_taskbar_progress(progress, "normal")
        
        plugin_api.set_taskbar_progress(100, "normal")
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(target_path)
        
        os.remove(zip_path)
        plugin_api.set_taskbar_progress(0, "none")  # 隐藏进度条
        return os.path.join(target_path, f"gradle-{version}")
        
    except Exception as e:
        plugin_api.set_taskbar_progress(100, "error")  # 显示错误状态
        raise e

def get_remote_versions():
    """获取远程可用的 Gradle 版本."""
    try:
        response = requests.get(GRADLE_VERSIONS_URL)
        versions = response.json()
        return [v['version'] for v in versions if not v.get('snapshot')]
    except Exception as e:
        print(f"获取远程版本失败: {e}")
        return []



def remove_gradle_version(version_path, api):
    """删除指定的Gradle版本"""
    try:
        # 如果是当前激活的版本，先清除环境变量
        current_gradle_home = api.get_env_var("GRADLE_HOME")
        if (current_gradle_home == version_path):
            api.set_env_var("GRADLE_HOME", "")
            api.remove_from_path(f"%GRADLE_HOME%\\bin")
            
        # 删除文件夹
        if os.path.exists(version_path):
            import shutil
            shutil.rmtree(version_path)
        return True
    except Exception as e:
        print(f"删除版本失败: {str(e)}")
        return False

def get_local_versions(config):
    """获取本地安装的版本列表."""
    return config.get(LOCAL_VERSIONS_KEY, [])

def set_active_version(version_path, api):
    """设置活动版本到系统环境变量."""
    try:
        # 设置 GRADLE_HOME 环境变量
        if not api.set_env_var("GRADLE_HOME", version_path):
            return False
            
        # 将bin目录添加到PATH，使用GRADLE_HOME作为父变量
        if not api.append_to_path(version_path, parent_var="GRADLE_HOME"):
            return False
            
        return True
    except Exception as e:
        print(f"设置环境变量失败: {str(e)}")
        return False

def register(api):
    """注册插件."""
    config = api.get_config()
    if LOCAL_VERSIONS_KEY not in config:
        config[LOCAL_VERSIONS_KEY] = []
    if "gradle_home" not in config:
        config["gradle_home"] = DEFAULT_GRADLE_HOME

def verify_gradle_version():
    """验证当前系统的 Gradle 版本."""
    try:
        # 使用 plugin_api 获取 GRADLE_HOME
        gradle_home = plugin_api.get_env_var("GRADLE_HOME")
        if not gradle_home:
            return "未找到GRADLE_HOME环境变量"
            
        gradle_exec = os.path.join(gradle_home, "bin", "gradle.bat" if os.name == 'nt' else "gradle")
        if not os.path.exists(gradle_exec):
            return f"Gradle可执行文件不存在: {gradle_exec}"
            
        env = os.environ.copy()  # 创建环境变量副本
        result = subprocess.run([gradle_exec, '--version'], 
                            capture_output=True,
                            text=True,
                            env=env)
        if result.returncode != 0:
            return f"验证失败: {result.stderr}"
        return result.stdout
    except Exception as e:
        return f"验证失败: {str(e)}\n请确保已正确设置Gradle环境变量"

def gui(master, context):
    """插件 GUI 界面."""
    # 从 context 中获取所需对象
    app = context['app']
    plugin_api = context['plugin_api']
    
    notebook = ttk.Notebook(master)
    notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # 创建标签页框架
    local_frame = ttk.Frame(notebook)
    remote_frame = ttk.Frame(notebook)
    verify_frame = ttk.Frame(notebook)
    
    notebook.add(local_frame, text="本地版本")
    notebook.add(remote_frame, text="远程版本")
    notebook.add(verify_frame, text="版本验证")

    # === 本地版本管理 ===
    local_versions = get_local_versions(plugin_api.get_config())
    
    version_list = tk.Listbox(local_frame, height=6)
    version_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    for version in local_versions:
        version_list.insert(tk.END, version)

    def set_active():
        selection = version_list.curselection()
        if selection:
            version_path = local_versions[selection[0]]
            if set_active_version(version_path, plugin_api):
                # 静默更新配置
                plugin_api.set_config("gradle_active_version", version_path, silent=True)
                messagebox.showinfo("成功", "Gradle 环境变量已设置")
            else:
                messagebox.showerror("错误", "设置环境变量失败")

    def delete_version():
        selection = version_list.curselection()
        if selection:
            version_path = local_versions[selection[0]]
            if messagebox.askyesno("确认", f"确定要删除此版本吗?\n{version_path}"):
                if remove_gradle_version(version_path, plugin_api):
                    # 从配置中移除
                    local_versions.remove(version_path)
                    plugin_api.set_config(LOCAL_VERSIONS_KEY, local_versions, silent=True)
                    # 更新列表显示
                    version_list.delete(selection)
                    messagebox.showinfo("成功", "版本已删除")
                else:
                    messagebox.showerror("错误", "删除版本失败")

    # 修改本地版本管理部分的按钮布局
    button_frame = ttk.Frame(local_frame)
    button_frame.pack(pady=5)
    
    ttk.Button(button_frame, text="设为活动版本", 
               command=set_active).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="删除版本", 
               command=delete_version).pack(side=tk.LEFT, padx=5)

    # === 远程版本管理 ===
    # 添加安装位置选择框架
    location_frame = ttk.LabelFrame(remote_frame, text="安装位置")
    location_frame.pack(fill=tk.X, padx=5, pady=5)

    # Gradle 安装路径选择
    gradle_path_var = tk.StringVar(value=plugin_api.get_config("gradle_home"))
    path_entry = ttk.Entry(location_frame, textvariable=gradle_path_var, width=40)
    path_entry.pack(side=tk.LEFT, padx=5, pady=5)

    def browse_gradle_home():
        path = filedialog.askdirectory(
            title="选择 Gradle 安装目录",
            initialdir=gradle_path_var.get() or os.path.expanduser("~")
        )
        if path:
            gradle_path_var.set(path)
            plugin_api.set_config("gradle_home", path, silent=True)

    ttk.Button(location_frame, text="浏览", 
               command=browse_gradle_home).pack(side=tk.LEFT, padx=5, pady=5)

    # 远程版本列表框架
    version_frame = ttk.LabelFrame(remote_frame, text="可用版本")
    version_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    remote_list = tk.Listbox(version_frame, height=6)
    remote_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def refresh_remote_versions():
        """刷新远程版本列表"""
        remote_list.delete(0, tk.END)
        versions = get_remote_versions()
        for version in versions:
            remote_list.insert(tk.END, version)

    def download_selected():
        """下载选中的版本"""
        selection = remote_list.curselection()
        if selection:
            version = remote_list.get(selection)
            install_path = gradle_path_var.get()
            
            print(f"准备下载 Gradle {version} 到 {install_path}")
            
            try:
                # ...existing download code...
                gradle_path = download_gradle(version, install_path, plugin_api)
                
                print(f"Gradle {version} 下载完成，保存到: {gradle_path}")
                local_versions = get_local_versions(plugin_api.get_config())
                local_versions.append(gradle_path)
                
                plugin_api.set_config(LOCAL_VERSIONS_KEY, local_versions, silent=True)
                version_list.insert(tk.END, gradle_path)
                
                messagebox.showinfo("成功", f"Gradle {version} 已成功下载到 {gradle_path}")
                
            except Exception as e:
                error_msg = f"下载失败: {str(e)}"
                print(f"错误: {error_msg}")
                messagebox.showerror("错误", error_msg)

    # 远程版本管理按钮
    button_frame = ttk.Frame(remote_frame)
    button_frame.pack(pady=5)
    
    ttk.Button(button_frame, text="刷新版本列表", 
               command=refresh_remote_versions).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="下载选中版本", 
               command=download_selected).pack(side=tk.LEFT, padx=5)

    # === 版本验证 ===
    verify_text = tk.Text(verify_frame, height=10, width=50)
    verify_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def verify_version():
        verify_text.delete(1.0, tk.END)
        # 将 plugin_api 传递给验证函数
        result = verify_gradle_version()
        verify_text.insert(tk.END, result)
        # 如果验证失败，显示提示
        if "验证失败" in result or "不存在" in result:
            messagebox.showwarning("警告", "Gradle验证失败，请确保已正确设置环境变量并重启终端")

    ttk.Button(verify_frame, text="验证当前版本", 
               command=verify_version).pack(pady=5)

    # 初始加载远程版本
    refresh_remote_versions()
