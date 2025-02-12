import os
import win32api
import win32con
import win32gui

class PluginAPI:
    def __init__(self, app):
        self.app = app

    def get_config(self, key=None):
        """
        获取配置信息.
        Args:
            key: 配置键名。如果提供，则返回特定配置项；否则返回整个配置字典
        """
        if key is None:
            return self.app.config
        return self.app.config.get(key)

    def set_config(self, key, value, silent=False):
        """
        设置配置信息.
        Args:
            key: 配置键名
            value: 配置值
            silent: 是否静默保存（不触发重启提示）
        """
        self.app.programmatic_change = silent
        self.app.config[key] = value
        self.app.save_config()

    def save_config(self, silent=False):
        """
        保存配置信息.
        Args:
            silent: 是否静默保存（不触发重启提示）
        """
        self.app.programmatic_change = silent
        self.app.save_config()

    def set_taskbar_progress(self, progress=0, state="normal"):
        """
        设置任务栏进度条.
        Args:
            progress: 进度值(0-100)
            state: 进度条状态("normal", "error", "none")
        """
        if not 0 <= progress <= 100:
            raise ValueError("Progress must be between 0 and 100")
            
        if state not in ["normal", "error", "none"]:
            raise ValueError("State must be one of: normal, error, none")
        
        try:
            # 尝试使用主窗口的进度条方法
            if hasattr(self.app, 'window'):
                self.app.window.setTaskbarProgress(progress, state)
            elif hasattr(self.app, 'root'):
                # 使用 Tk root 窗口作为后备方案
                if state == "none":
                    self.app.root.title(f"{self.app.title}")
                else:
                    self.app.root.title(f"{self.app.title} - {progress}%")
        except Exception as e:
            print(f"设置进度条失败: {e}")

    def _broadcast_env_update(self):
        """通知系统环境变量已更改"""
        try:
            # 发送环境变量更改通知
            win32gui.SendMessage(
                win32con.HWND_BROADCAST,
                win32con.WM_SETTINGCHANGE,
                0,
                'Environment'
            )
            # 等待消息处理完成
            win32gui.SendMessageTimeout(
                win32con.HWND_BROADCAST,
                win32con.WM_SETTINGCHANGE,
                0,
                'Environment',
                win32con.SMTO_ABORTIFHUNG,
                5000
            )
        except Exception as e:
            print(f"广播环境变量更新消息失败: {str(e)}")

    def set_env_var(self, name, value, system_wide=False):
        """设置环境变量"""
        try:
            if system_wide:
                # 系统环境变量
                key = win32api.RegOpenKey(
                    win32con.HKEY_LOCAL_MACHINE,
                    'SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment',
                    0,
                    win32con.KEY_ALL_ACCESS
                )
            else:
                # 用户环境变量
                key = win32api.RegOpenKey(
                    win32con.HKEY_CURRENT_USER,
                    'Environment',
                    0,
                    win32con.KEY_ALL_ACCESS
                )

            win32api.RegSetValueEx(key, name, 0, win32con.REG_EXPAND_SZ, value)
            win32api.RegCloseKey(key)
            
            # 立即更新当前进程的环境变量
            os.environ[name] = value
            self._broadcast_env_update()
            return True
        except Exception as e:
            print(f"设置环境变量失败: {str(e)}")
            return False

    def append_to_path(self, new_path, system_wide=False, parent_var=None):
        """追加到PATH环境变量"""
        try:
            if system_wide:
                key = win32api.RegOpenKey(
                    win32con.HKEY_LOCAL_MACHINE,
                    'SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment',
                    0,
                    win32con.KEY_ALL_ACCESS
                )
            else:
                key = win32api.RegOpenKey(
                    win32con.HKEY_CURRENT_USER,
                    'Environment',
                    0,
                    win32con.KEY_ALL_ACCESS
                )

            try:
                current_path, _ = win32api.RegQueryValueEx(key, 'PATH')
            except:
                current_path = ''

            if parent_var:
                path_to_add = f"%{parent_var}%\\bin"
            else:
                path_to_add = os.path.join(new_path, 'bin')

            paths = [p for p in current_path.split(';') if p]
            if path_to_add not in paths:
                new_path_value = ';'.join(paths + [path_to_add])
                win32api.RegSetValueEx(key, 'PATH', 0, win32con.REG_EXPAND_SZ, new_path_value)
                
                # 立即更新当前进程的环境变量
                os.environ['PATH'] = new_path_value

            win32api.RegCloseKey(key)
            self._broadcast_env_update()
            return True
        except Exception as e:
            print(f"追加PATH失败: {str(e)}")
            return False

    def get_env_var(self, name, system_wide=False):
        """获取环境变量值"""
        try:
            if system_wide:
                key = win32api.RegOpenKey(
                    win32con.HKEY_LOCAL_MACHINE,
                    'SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment',
                    0,
                    win32con.KEY_READ
                )
            else:
                key = win32api.RegOpenKey(
                    win32con.HKEY_CURRENT_USER,
                    'Environment',
                    0,
                    win32con.KEY_READ
                )
            
            value, _ = win32api.RegQueryValueEx(key, name)
            win32api.RegCloseKey(key)
            return value
        except Exception as e:
            print(f"获取环境变量失败: {str(e)}")
            return None
            
    def remove_from_path(self, path_to_remove, system_wide=False):
        """从PATH中移除指定路径"""
        try:
            if system_wide:
                key = win32api.RegOpenKey(
                    win32con.HKEY_LOCAL_MACHINE,
                    'SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment',
                    0,
                    win32con.KEY_ALL_ACCESS
                )
            else:
                key = win32api.RegOpenKey(
                    win32con.HKEY_CURRENT_USER,
                    'Environment',
                    0,
                    win32con.KEY_ALL_ACCESS
                )

            current_path, _ = win32api.RegQueryValueEx(key, 'PATH')
            paths = [p for p in current_path.split(';') if p and p != path_to_remove]
            new_path = ';'.join(paths)
            
            win32api.RegSetValueEx(key, 'PATH', 0, win32con.REG_EXPAND_SZ, new_path)
            win32api.RegCloseKey(key)
            
            os.environ['PATH'] = new_path
            self._broadcast_env_update()
            return True
        except Exception as e:
            print(f"从PATH移除失败: {str(e)}")
            return False

    def validate_path(self, path):
        """
        验证路径是否有效
        Args:
            path: 需要验证的路径
        Returns:
            bool: 路径是否有效
        """
        try:
            # 检查路径是否为空
            if not path:
                print(f"路径验证失败: 路径为空")
                return False
                
            # 规范化路径
            normalized_path = os.path.normpath(path)
            
            # 检查路径是否包含基本非法字符
            forbidden_chars = '<>"|?*'  # 移除了 : 因为Windows路径需要它
            if any(char in os.path.basename(normalized_path) for char in forbidden_chars):
                print(f"路径验证失败: 包含非法字符 {forbidden_chars}")
                return False
                
            # 尝试将路径转换为绝对路径并验证父目录是否存在或可创建
            abs_path = os.path.abspath(normalized_path)
            parent_dir = os.path.dirname(abs_path)
            
            # 如果父目录不存在，检查是否可以创建
            if not os.path.exists(parent_dir):
                parent_of_parent = os.path.dirname(parent_dir)
                if not os.path.exists(parent_of_parent):
                    print(f"路径验证失败: 父目录不存在且无法创建 {parent_dir}")
                    return False
            
            print(f"路径验证通过: {abs_path}")
            return True
            
        except Exception as e:
            print(f"路径验证出错: {str(e)}")
            return False

    def ensure_dir_exists(self, path):
        """确保目录存在，如果不存在则创建"""
        try:
            if not os.path.exists(path):
                os.makedirs(path)
            return True
        except Exception as e:
            print(f"创建目录失败: {e}")
            return False
