from src.services.logger import GameLogger
from src.services.config import Config

# 尝试导入可选服务
try:
    from src.services.window_manager import GameWindowManager
    WINDOW_MANAGER_AVAILABLE = True
except ImportError:
    GameWindowManager = None
    WINDOW_MANAGER_AVAILABLE = False

try:
    from src.services.image_processor import ImageProcessor
    IMAGE_PROCESSOR_AVAILABLE = True
except ImportError:
    ImageProcessor = None
    IMAGE_PROCESSOR_AVAILABLE = False

try:
    from src.services.action_simulator import ActionSimulator
    ACTION_SIMULATOR_AVAILABLE = True
except ImportError:
    ActionSimulator = None
    ACTION_SIMULATOR_AVAILABLE = False

# 使用统一的GameAnalyzer
try:
    from src.core.unified_game_analyzer import UnifiedGameAnalyzer as GameAnalyzer
    GAME_ANALYZER_AVAILABLE = True
except ImportError:
    GameAnalyzer = None
    GAME_ANALYZER_AVAILABLE = False

try:
    from src.services.game_state import GameState
    GAME_STATE_AVAILABLE = True
except ImportError:
    GameState = None
    GAME_STATE_AVAILABLE = False

try:
    from src.services.auto_operator import AutoOperator
    AUTO_OPERATOR_AVAILABLE = True
except ImportError:
    AutoOperator = None
    AUTO_OPERATOR_AVAILABLE = False

try:
    from src.services.config_manager import ConfigManager
    CONFIG_MANAGER_AVAILABLE = True
except ImportError:
    ConfigManager = None
    CONFIG_MANAGER_AVAILABLE = False

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
            self._instances['config'] = Config()
        return self._instances['config']
    
    def logger(self):
        """获取日志服务实例"""
        if 'logger' not in self._instances:
            self._instances['logger'] = GameLogger(self.config())
        return self._instances['logger']
    
    def window_manager(self):
        """获取窗口管理服务实例"""
        if not WINDOW_MANAGER_AVAILABLE:
            raise RuntimeError("WindowManager不可用：缺少win32gui依赖")
        
        if 'window_manager' not in self._instances:
            self._instances['window_manager'] = GameWindowManager(self.logger(), self.config())
        return self._instances['window_manager']
    
    def image_processor(self):
        """获取图像处理服务实例"""
        if not IMAGE_PROCESSOR_AVAILABLE:
            raise RuntimeError("ImageProcessor不可用：缺少OpenCV依赖")
        
        if 'image_processor' not in self._instances:
            self._instances['image_processor'] = ImageProcessor(self.logger(), self.config())
        return self._instances['image_processor']
    
    def game_analyzer(self):
        """获取游戏分析服务实例 - 使用统一的GameAnalyzer"""
        if not GAME_ANALYZER_AVAILABLE:
            raise RuntimeError("GameAnalyzer不可用：缺少OpenCV依赖")
        
        if 'game_analyzer' not in self._instances:
            # 使用统一的GameAnalyzer，支持传统图像处理和深度学习
            self._instances['game_analyzer'] = GameAnalyzer(
                self.logger(), 
                self.image_processor(), 
                self.config(),
                game_name="default"  # 默认游戏名，可以从配置中获取
            )
        return self._instances['game_analyzer']
    
    def action_simulator(self):
        """获取动作模拟服务实例"""
        if not ACTION_SIMULATOR_AVAILABLE:
            raise RuntimeError("ActionSimulator不可用：缺少依赖")
        
        if 'action_simulator' not in self._instances:
            self._instances['action_simulator'] = ActionSimulator(
                self.logger(),
                self.window_manager(), 
                self.config()
            )
        return self._instances['action_simulator']
    
    def game_state(self):
        """获取游戏状态服务实例"""
        if not GAME_STATE_AVAILABLE:
            raise RuntimeError("GameState不可用：缺少依赖")
        
        if 'game_state' not in self._instances:
            self._instances['game_state'] = GameState(self.logger(), self.game_analyzer())
        return self._instances['game_state']
    
    def auto_operator(self):
        """获取自动操作服务实例"""
        if not AUTO_OPERATOR_AVAILABLE:
            raise RuntimeError("AutoOperator不可用：缺少依赖")
        
        if 'auto_operator' not in self._instances:
            self._instances['auto_operator'] = AutoOperator(
                self.logger(), 
                self.action_simulator(), 
                self.game_state(), 
                self.image_processor(),
                self.config()
            )
        return self._instances['auto_operator']
    
    def config_manager(self):
        """获取配置管理器实例"""
        if not CONFIG_MANAGER_AVAILABLE:
            raise RuntimeError("ConfigManager不可用：缺少依赖")
        
        if 'config_manager' not in self._instances:
            self._instances['config_manager'] = ConfigManager(self.config())
        return self._instances['config_manager']
    
    def get_available_services(self):
        """获取可用服务列表"""
        available = ['config', 'logger']
        
        if WINDOW_MANAGER_AVAILABLE:
            available.append('window_manager')
        if IMAGE_PROCESSOR_AVAILABLE:
            available.append('image_processor')
        if GAME_ANALYZER_AVAILABLE:
            available.append('game_analyzer')
        if ACTION_SIMULATOR_AVAILABLE:
            available.append('action_simulator')
        if GAME_STATE_AVAILABLE:
            available.append('game_state')
        if AUTO_OPERATOR_AVAILABLE:
            available.append('auto_operator')
        if CONFIG_MANAGER_AVAILABLE:
            available.append('config_manager')
        
        return available
    
    def is_service_available(self, service_name: str) -> bool:
        """检查服务是否可用"""
        service_availability = {
            'config': True,
            'logger': True,
            'window_manager': WINDOW_MANAGER_AVAILABLE,
            'image_processor': IMAGE_PROCESSOR_AVAILABLE,
            'game_analyzer': GAME_ANALYZER_AVAILABLE,
            'action_simulator': ACTION_SIMULATOR_AVAILABLE,
            'game_state': GAME_STATE_AVAILABLE,
            'auto_operator': AUTO_OPERATOR_AVAILABLE,
            'config_manager': CONFIG_MANAGER_AVAILABLE,
        }
        return service_availability.get(service_name, False) 