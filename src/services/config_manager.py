import json
import os
from typing import Dict, Any, Optional
from .config import Config

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config: Config):
        """
        初始化配置管理器
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.config_file = "settings.json"
        self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._update_config(data)
        except Exception as e:
            print(f"加载配置文件失败: {e}")
    
    def _save_config(self):
        """保存配置文件"""
        try:
            data = {
                'window': {
                    'last_selected': self.get_value('window.last_selected', ''),
                    'refresh_interval': self.get_value('window.refresh_interval', 1000)
                },
                'template': {
                    'duration': self.get_value('template.duration', 300),
                    'interval': self.get_value('template.interval', 1.0),
                    'last_dir': self.get_value('template.last_dir', 'templates')
                },
                'game_state': {
                    'analysis_interval': self.get_value('game_state.analysis_interval', 1000),
                    'last_state': self.get_value('game_state.last_state', {})
                }
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def _update_config(self, data: Dict[str, Any]):
        """
        更新配置
        
        Args:
            data: 配置数据
        """
        try:
            # 更新窗口配置
            if 'window' in data:
                window_config = data['window']
                self.config.window.last_selected = window_config.get('last_selected', '')
                self.config.window.refresh_interval = window_config.get('refresh_interval', 1000)
            
            # 更新模板配置
            if 'template' in data:
                template_config = data['template']
                self.config.template.duration = template_config.get('duration', 300)
                self.config.template.interval = template_config.get('interval', 1.0)
                self.config.template.last_dir = template_config.get('last_dir', 'templates')
            
            # 更新游戏状态配置
            if 'game_state' in data:
                game_state_config = data['game_state']
                self.config.game_state.analysis_interval = game_state_config.get('analysis_interval', 1000)
                self.config.game_state.last_state = game_state_config.get('last_state', {})
        except Exception as e:
            print(f"更新配置失败: {e}")
    
    def get_value(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            配置值
        """
        try:
            parts = key.split('.')
            value = self.config
            for part in parts:
                value = getattr(value, part)
            return value
        except Exception:
            return default
    
    def set_value(self, key: str, value: Any):
        """
        设置配置值
        
        Args:
            key: 配置键
            value: 配置值
        """
        try:
            parts = key.split('.')
            obj = self.config
            for part in parts[:-1]:
                obj = getattr(obj, part)
            setattr(obj, parts[-1], value)
            self._save_config()
        except Exception as e:
            print(f"设置配置值失败: {e}")
    
    def get_window_config(self) -> Optional[Dict[str, Any]]:
        """
        获取窗口配置
        
        Returns:
            窗口配置
        """
        try:
            return {
                'last_selected': self.get_value('window.last_selected', ''),
                'refresh_interval': self.get_value('window.refresh_interval', 1000)
            }
        except Exception:
            return None
    
    def get_template_config(self) -> Optional[Dict[str, Any]]:
        """
        获取模板配置
        
        Returns:
            模板配置
        """
        try:
            return {
                'duration': self.get_value('template.duration', 300),
                'interval': self.get_value('template.interval', 1.0),
                'last_dir': self.get_value('template.last_dir', 'templates')
            }
        except Exception:
            return None
    
    def get_game_state_config(self) -> Optional[Dict[str, Any]]:
        """
        获取游戏状态配置
        
        Returns:
            游戏状态配置
        """
        try:
            return {
                'analysis_interval': self.get_value('game_state.analysis_interval', 1000),
                'last_state': self.get_value('game_state.last_state', {})
            }
        except Exception:
            return None
    
    def update_last_game_state(self, state: Dict[str, Any]):
        """
        更新最后的游戏状态
        
        Args:
            state: 游戏状态
        """
        try:
            self.set_value('game_state.last_state', state)
        except Exception as e:
            print(f"更新游戏状态失败: {e}")
    
    def update_last_selected_window(self, window_title: str):
        """
        更新最后选择的窗口
        
        Args:
            window_title: 窗口标题
        """
        try:
            self.set_value('window.last_selected', window_title)
        except Exception as e:
            print(f"更新窗口选择失败: {e}")
    
    def update_last_template_dir(self, template_dir: str):
        """
        更新最后的模板目录
        
        Args:
            template_dir: 模板目录
        """
        try:
            self.set_value('template.last_dir', template_dir)
        except Exception as e:
            print(f"更新模板目录失败: {e}") 