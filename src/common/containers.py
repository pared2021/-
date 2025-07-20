from ..services.logger import GameLogger
from ..services.config import config  # 使用统一配置系统单例
from ..services.window_manager import GameWindowManager
from ..services.image_processor import ImageProcessor
from ..services.game_analyzer import GameAnalyzer
from ..services.action_simulator import ActionSimulator
from ..core.types import UnifiedGameState as GameState
from ..services.error_handler import ErrorHandler
import os

class EnhancedContainer:
    """增强的依赖注入容器 - 解决循环依赖问题"""
    
    def __init__(self):
        """初始化依赖注入容器"""
        self._instances = {}
        self._initialization_phase = "CREATING"  # CREATING, INJECTING, READY
        self._service_creation_order = []
        self._post_init_callbacks = []
        
    def initialize(self):
        """分阶段初始化容器"""
        try:
            # 阶段1: 创建核心服务（无依赖）
            self._initialization_phase = "CREATING"
            self._create_core_services()
            
            # 阶段2: 创建基础服务（依赖核心服务）
            self._create_basic_services()
            
            # 阶段3: 创建高级服务（依赖基础服务）
            self._create_advanced_services()
            
            # 阶段4: 依赖注入
            self._initialization_phase = "INJECTING"
            self._inject_dependencies()
            
            # 阶段5: 后置初始化
            self._initialization_phase = "READY"
            self._post_initialize()
            
            return True
        except Exception as e:
            print(f"容器初始化失败: {e}")
            return False
    
    def _create_core_services(self):
        """创建核心服务（无依赖）"""
        # 配置服务（使用统一配置系统单例）
        if 'config' not in self._instances:
            self._instances['config'] = config
            self._service_creation_order.append('config')
            
        # 日志服务
        if 'logger' not in self._instances:
            self._instances['logger'] = GameLogger(config, "Container")
            self._service_creation_order.append('logger')
    
    def _create_basic_services(self):
        """创建基础服务（依赖核心服务）"""
        # 错误处理服务（仅依赖logger，不立即注入其他依赖）
        if 'error_handler' not in self._instances:
            self._instances['error_handler'] = ErrorHandler(self._instances['logger'])
            self._service_creation_order.append('error_handler')
    
    def _create_advanced_services(self):
        """创建高级服务（依赖基础服务）"""
        # 窗口管理器
        if 'window_manager' not in self._instances:
            self._instances['window_manager'] = GameWindowManager(
                self._instances['logger'],
                self._instances['config'],
                self._instances['error_handler']
            )
            self._service_creation_order.append('window_manager')
        
        # 图像处理器
        if 'image_processor' not in self._instances:
            self._instances['image_processor'] = ImageProcessor(
                self._instances['logger'],
                self._instances['config'],
                self._instances['error_handler']
            )
            self._service_creation_order.append('image_processor')
        
        # 动作模拟器
        if 'action_simulator' not in self._instances:
            self._instances['action_simulator'] = ActionSimulator(
                self._instances['logger'],
                self._instances['window_manager'],
                self._instances['config'],
                self._instances['error_handler']
            )
            self._service_creation_order.append('action_simulator')
        
        # 游戏分析器
        if 'game_analyzer' not in self._instances:
            self._instances['game_analyzer'] = GameAnalyzer(
                self._instances['logger'],
                self._instances['image_processor'],
                self._instances['config'],
                self._instances['error_handler']
            )
            self._service_creation_order.append('game_analyzer')
        
        # 游戏状态
        if 'game_state' not in self._instances:
            self._instances['game_state'] = GameState(
                self._instances['logger'],
                self._instances['game_analyzer'],
                self._instances['error_handler']
            )
            self._service_creation_order.append('game_state')
        
        # 自动操作器（懒加载避免循环导入）
        if 'auto_operator' not in self._instances:
            from ..services.auto_operator import AutoOperator
            self._instances['auto_operator'] = AutoOperator(
                self._instances['error_handler'],
                self._instances['window_manager'],
                self._instances['image_processor']
            )
            self._service_creation_order.append('auto_operator')
        
        # 注意：配置管理器现在由统一配置系统提供，无需单独创建
    
    def _inject_dependencies(self):
        """注入依赖关系"""
        error_handler = self._instances.get('error_handler')
        if error_handler:
            # 安全地注入依赖，检查服务是否存在
            if 'window_manager' in self._instances:
                error_handler.set_window_manager(self._instances['window_manager'])
            if 'image_processor' in self._instances:
                error_handler.set_image_processor(self._instances['image_processor'])
            if 'action_simulator' in self._instances:
                error_handler.set_action_simulator(self._instances['action_simulator'])
            if 'game_state' in self._instances:
                error_handler.set_game_state(self._instances['game_state'])
            if 'game_analyzer' in self._instances:
                error_handler.set_game_analyzer(self._instances['game_analyzer'])
            # 配置由统一配置系统管理，无需手动设置
        
        # 为其他服务注入error_handler（如果它们支持的话）
        for service_name, service in self._instances.items():
            if service_name != 'error_handler' and hasattr(service, 'set_error_handler'):
                service.set_error_handler(error_handler)
    
    def _post_initialize(self):
        """后置初始化"""
        # 执行注册的后置初始化回调
        for callback in self._post_init_callbacks:
            try:
                callback(self)
            except Exception as e:
                print(f"后置初始化回调失败: {e}")
        
        # 添加默认错误处理函数
        error_handler = self._instances.get('error_handler')
        if error_handler and hasattr(error_handler, 'add_default_handlers'):
            error_handler.add_default_handlers()
    
    def register_post_init_callback(self, callback):
        """注册后置初始化回调"""
        self._post_init_callbacks.append(callback)
    
    def is_ready(self) -> bool:
        """检查容器是否已准备就绪"""
        return self._initialization_phase == "READY"
    
    def get_service(self, service_name: str):
        """安全地获取服务"""
        if not self.is_ready():
            raise RuntimeError(f"容器尚未初始化完成，无法获取服务: {service_name}")
        return self._instances.get(service_name)
    
    # === 向后兼容性方法 ===
    
    def register(self, key, instance):
        """注册服务实例"""
        self._instances[key] = instance
        
    def config(self):
        """获取配置服务实例"""
        if self._initialization_phase == "READY":
            return self._instances.get('config')
        elif 'config' in self._instances:
            return self._instances['config']
        else:
            # 兼容旧版本调用，使用统一配置系统单例
            self._instances['config'] = config
            return self._instances['config']
    
    def logger(self):
        """获取日志服务实例"""
        if self._initialization_phase == "READY":
            return self._instances.get('logger')
        elif 'logger' in self._instances:
            return self._instances['logger']
        else:
            # 兼容旧版本调用，使用统一配置系统
            self._instances['logger'] = GameLogger(self.config(), "Container")
            return self._instances['logger']
    
    def error_handler(self) -> ErrorHandler:
        """获取错误处理服务实例 - 解决循环依赖版本"""
        if self._initialization_phase == "READY":
            return self._instances.get('error_handler')
        elif 'error_handler' in self._instances:
            return self._instances['error_handler']
        else:
            # 兼容旧版本调用，但避免循环依赖
            if 'logger' not in self._instances:
                self._instances['logger'] = GameLogger()
            
            error_handler = ErrorHandler(self._instances['logger'])
            self._instances['error_handler'] = error_handler
            
            # 延迟设置依赖关系，避免循环调用
            self.register_post_init_callback(lambda container: self._setup_error_handler_dependencies())
            
            return error_handler
    
    def _setup_error_handler_dependencies(self):
        """设置错误处理器的依赖关系"""
        error_handler = self._instances.get('error_handler')
        if not error_handler:
            return
            
        # 只在服务存在时才设置依赖
        if 'window_manager' in self._instances:
            error_handler.set_window_manager(self._instances['window_manager'])
        if 'image_processor' in self._instances:
            error_handler.set_image_processor(self._instances['image_processor'])
        if 'action_simulator' in self._instances:
            error_handler.set_action_simulator(self._instances['action_simulator'])
        if 'game_state' in self._instances:
            error_handler.set_game_state(self._instances['game_state'])
        if 'game_analyzer' in self._instances:
            error_handler.set_game_analyzer(self._instances['game_analyzer'])
        # 配置由统一配置系统管理，无需手动设置
    
    def window_manager(self):
        """获取窗口管理服务实例"""
        if self._initialization_phase == "READY":
            return self._instances.get('window_manager')
        elif 'window_manager' in self._instances:
            return self._instances['window_manager']
        else:
            # 兼容旧版本调用
            if 'window_manager' not in self._instances:
                self._instances['window_manager'] = GameWindowManager(
                    self.logger(),
                    self.config()
                )
            return self._instances['window_manager']
    
    def image_processor(self):
        """获取图像处理服务实例"""
        if self._initialization_phase == "READY":
            return self._instances.get('image_processor')
        elif 'image_processor' in self._instances:
            return self._instances['image_processor']
        else:
            # 兼容旧版本调用
            if 'image_processor' not in self._instances:
                self._instances['image_processor'] = ImageProcessor(
                    self.logger(),
                    self.config()
                )
            return self._instances['image_processor']
    
    def game_analyzer(self):
        """获取游戏分析服务实例"""
        if self._initialization_phase == "READY":
            return self._instances.get('game_analyzer')
        elif 'game_analyzer' in self._instances:
            return self._instances['game_analyzer']
        else:
            # 兼容旧版本调用
            if 'game_analyzer' not in self._instances:
                self._instances['game_analyzer'] = GameAnalyzer(
                    self.logger(),
                    self.image_processor(),
                    self.config()
                )
            return self._instances['game_analyzer']
    
    def action_simulator(self):
        """获取动作模拟服务实例"""
        if self._initialization_phase == "READY":
            return self._instances.get('action_simulator')
        elif 'action_simulator' in self._instances:
            return self._instances['action_simulator']
        else:
            # 兼容旧版本调用
            if 'action_simulator' not in self._instances:
                self._instances['action_simulator'] = ActionSimulator(
                    self.logger(),
                    self.window_manager(),
                    self.config()
                )
            return self._instances['action_simulator']
    
    def game_state(self):
        """获取游戏状态服务实例"""
        if self._initialization_phase == "READY":
            return self._instances.get('game_state')
        elif 'game_state' in self._instances:
            return self._instances['game_state']
        else:
            # 兼容旧版本调用
            if 'game_state' not in self._instances:
                self._instances['game_state'] = GameState(
                    self.logger(),
                    self.game_analyzer()
                )
            return self._instances['game_state']
    
    def auto_operator(self):
        """获取自动操作服务实例"""
        if self._initialization_phase == "READY":
            return self._instances.get('auto_operator')
        elif 'auto_operator' in self._instances:
            return self._instances['auto_operator']
        else:
            # 兼容旧版本调用（懒加载避免循环导入）
            if 'auto_operator' not in self._instances:
                from ..services.auto_operator import AutoOperator
                self._instances['auto_operator'] = AutoOperator(
                    self.error_handler(),
                    self.window_manager(),
                    self.image_processor()
                )
            return self._instances['auto_operator']
    
    def config_manager(self):
        """获取配置管理器实例 - 现在直接返回统一配置系统"""
        # 统一配置系统替代了传统的配置管理器
        return self.config()
    
    def get_initialization_status(self):
        """获取初始化状态"""
        return {
            "phase": self._initialization_phase,
            "services_created": list(self._instances.keys()),
            "creation_order": self._service_creation_order,
            "is_ready": self.is_ready()
        }


# 向后兼容性别名
Container = EnhancedContainer