
class PluginAPI:
    def __init__(self, app):
        self.app = app

    def get_config(self):
        """获取配置信息."""
        return self.app.config

    def set_config(self, key, value):
        """设置配置信息."""
        self.app.config[key] = value
        self.app.save_config()
