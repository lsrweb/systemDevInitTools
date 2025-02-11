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

    def set_config(self, key, value):
        """设置配置信息."""
        self.app.config[key] = value
        self.app.save_config()

    def save_config(self):
        """保存配置信息."""
        self.app.save_config()
