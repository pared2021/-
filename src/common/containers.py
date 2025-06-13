from src.services.logger import GameLogger
from src.services.config import Config
from src.services.window_manager import GameWindowManager
from src.services.image_processor import ImageProcessor
from src.services.game_analyzer import GameAnalyzer
from src.services.action_simulator import ActionSimulator
from src.services.game_state import GameState
from src.services.auto_operator import AutoOperator
from src.services.config import Config as ConfigManager
from src.services.error_handler import ErrorHandler
import os

class Container:
    """依赖注入容器"""
    
    def __init__(self):
        """初始化依赖注入容器"""
        self._instances = {}
        
    def register(self, key, instance):
        """注册服务实例
        
        Args:
            key: 服务标识符
            instance: 服务实例
        """
        self._instances[key] = instance
        
    def config(self):
        """获取配置服务实例"""
        if 'config' not in self._instances:
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'settings.json')
            self._instances['config'] = Config(config_path)
        return self._instances['config']
    
    def logger(self):
        """获取日志服务实例"""
        if 'logger' not in self._instances:
            self._instances['logger'] = GameLogger()
        return self._instances['logger']
    
    def error_handler(self) -> ErrorHandler:
        """获取错误处理服务实例"""
        error_handler = ErrorHandler(self.logger())
        
        # 设置服务依赖
        error_handler.set_window_manager(self.window_manager())
        error_handler.set_image_processor(self.image_processor())
        error_handler.set_action_simulator(self.action_simulator())
        error_handler.set_game_state(self.game_state())
        error_handler.set_game_analyzer(self.game_analyzer())
        error_handler.set_config(self.config_manager())
        
        return error_handler
    
    def window_manager(self):
        """获取窗口管理服务实例"""
        if 'window_manager' not in self._instances:
            self._instances['window_manager'] = GameWindowManager(
                self.logger(),
                self.config(),
                self.error_handler()
            )
        return self._instances['window_manager']
    
    def image_processor(self):
        """获取图像处理服务实例"""
        if 'image_processor' not in self._instances:
            self._instances['image_processor'] = ImageProcessor(
                self.logger(),
                self.error_handler()
            )
        return self._instances['image_processor']
    
    def game_analyzer(self):
        """获取游戏分析服务实例"""
        if 'game_analyzer' not in self._instances:
            self._instances['game_analyzer'] = GameAnalyzer(
                self.logger(),
                self.image_processor(),
                self.config(),
                self.error_handler()
            )
        return self._instances['game_analyzer']
    
    def action_simulator(self):
        """获取动作模拟服务实例"""
        if 'action_simulator' not in self._instances:
            self._instances['action_simulator'] = ActionSimulator(
                self.logger(),
                self.window_manager(),
                self.config(),
                self.error_handler()
            )
        return self._instances['action_simulator']
    
    def game_state(self):
        """获取游戏状态服务实例"""
        if 'game_state' not in self._instances:
            self._instances['game_state'] = GameState(
                self.logger(),
                self.game_analyzer(),
                self.error_handler()
            )
        return self._instances['game_state']
    
    def auto_operator(self):
        """获取自动操作服务实例"""
        if 'auto_operator' not in self._instances:
            self._instances['auto_operator'] = AutoOperator(
                self.logger(),
                self.action_simulator(),
                self.game_state(),
                self.image_processor(),
                self.config(),
                self.error_handler()
            )
        return self._instances['auto_operator']
    
    def config_manager(self):
        """获取配置管理器实例"""
        if 'config_manager' not in self._instances:
            self._instances['config_manager'] = ConfigManager(
                self.config(),
                self.error_handler()
            )
        return self._instances['config_manager'] 