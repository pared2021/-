"""
配置管理器
"""
from typing import Dict, Any, Optional
import json
import os


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
        self.config_data: Dict[str, Any] = {}

        # 创建配置目录
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

    def load_config(self, name: str) -> Optional[Dict[str, Any]]:
        """加载配置"""
        config_path = os.path.join(self.config_dir, f"{name}.json")
        if not os.path.exists(config_path):
            return None

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.config_data[name] = data
                return data
        except Exception as e:
            print(f"加载配置失败: {str(e)}")
            return None

    def save_config(self, name: str, data: Dict[str, Any]) -> bool:
        """保存配置"""
        config_path = os.path.join(self.config_dir, f"{name}.json")
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                self.config_data[name] = data
                return True
        except Exception as e:
            print(f"保存配置失败: {str(e)}")
            return False

    def get_config(self, name: str) -> Optional[Dict[str, Any]]:
        """获取配置"""
        return self.config_data.get(name)

    def update_config(self, name: str, data: Dict[str, Any]) -> bool:
        """更新配置"""
        if name not in self.config_data:
            return False

        self.config_data[name].update(data)
        return self.save_config(name, self.config_data[name])
