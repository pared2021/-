"""配置管理模块"""
import json
import logging
import os


class ConfigManager:
    """配置管理器类，用于处理配置文件的加载、保存和访问"""

    def __init__(self, config_file=None):
        """初始化配置管理器

        Args:
            config_file (str, optional): 配置文件路径. Defaults to None.
        """
        self.logger = logging.getLogger("ConfigManager")
        self.config_file = config_file if config_file else "config.json"
        self.config = {}
        self.load_config()

    def load_config(self):
        """从文件加载配置

        Args:
            config_file (str): 配置文件路径
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            else:
                self.config = self._create_default_config()
                self.save_config()
        except Exception as e:
            self.logger.error("加载配置文件失败: %s", e)
            self.config = self._create_default_config()

    def save_config(self):
        """保存配置到文件

        Args:
            config_file (str): 配置文件路径
        """
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            self.logger.error("保存配置文件失败: %s", e)

    def get_config(self, key, default=None):
        """获取配置值

        Args:
            key (str): 配置键，支持点号分隔的嵌套键
            default: 默认值，当键不存在时返回

        Returns:
            配置值或默认值
        """
        return self.config.get(key, default)

    def set_config(self, key, value):
        """设置配置值

        Args:
            key (str): 配置键，支持点号分隔的嵌套键
            value: 要设置的值
        """
        self.config[key] = value
        self.save_config()

    def delete_config(self, key):
        """删除配置项

        Args:
            key (str): 配置键，支持点号分隔的嵌套键
        """
        if key in self.config:
            del self.config[key]

    def clear_config(self):
        """清空所有配置"""
        self.config.clear()

    def _create_default_config(self):
        """
        创建默认配置

        Returns:
            默认配置字典
        """
        return {
            "window_title": "游戏自动操作工具",
            "window_size": [800, 600],
            "language": "zh_CN",
            "theme": "default",
            "hotkeys": {
                "start_record": "F9",
                "stop_record": "F10",
                "start_playback": "F11",
                "stop_playback": "F12",
            },
            "playback_options": {"speed": 1.0, "loop_count": 1, "random_delay": 0.0},
        }
