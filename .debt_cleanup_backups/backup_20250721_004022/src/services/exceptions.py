"""
服务层异常定义
继承通用异常类并添加服务特定的异常类型
"""

from ..common.exceptions import (
    GameAutomationError,
    WindowError, 
    ImageProcessingError as BaseImageProcessingError,
    ActionError,
    ConfigError,
    StateError
)

# 服务层特定异常，继承通用异常
class WindowNotFoundError(WindowError):
    """窗口未找到异常"""
    def __init__(self, message: str = "指定窗口未找到"):
        super().__init__(message, 1001)

class WindowAccessError(WindowError):
    """窗口访问异常"""
    def __init__(self, message: str = "无法访问窗口"):
        super().__init__(message, 1002)

class ImageProcessingError(BaseImageProcessingError):
    """图像处理服务异常"""
    def __init__(self, message: str = "图像处理失败"):
        super().__init__(message, 2001)

class ActionSimulationError(ActionError):
    """动作模拟异常"""
    def __init__(self, message: str = "动作模拟失败"):
        super().__init__(message, 3001)

class GameStateError(StateError):
    """游戏状态异常"""
    def __init__(self, message: str = "游戏状态错误"):
        super().__init__(message, 6001)

class TemplateCollectionError(GameAutomationError):
    """模板收集异常"""
    def __init__(self, message: str = "模板收集失败"):
        super().__init__(message, 8001)

class ModelTrainingError(GameAutomationError):
    """模型训练异常"""
    def __init__(self, message: str = "模型训练失败"):
        super().__init__(message, 8002)

class ConfigurationError(ConfigError):
    """配置服务异常"""
    def __init__(self, message: str = "配置错误"):
        super().__init__(message, 5001)

class ServiceInitializationError(GameAutomationError):
    """服务初始化异常"""
    def __init__(self, message: str = "服务初始化失败"):
        super().__init__(message, 9001)

class ServiceUnavailableError(GameAutomationError):
    """服务不可用异常"""
    def __init__(self, message: str = "服务不可用"):
        super().__init__(message, 9002)

# 向后兼容的别名
GameAutomationError = GameAutomationError  # 重导出基础异常

__all__ = [
    'GameAutomationError',
    'WindowNotFoundError',
    'WindowAccessError', 
    'ImageProcessingError',
    'ActionSimulationError',
    'GameStateError',
    'TemplateCollectionError',
    'ModelTrainingError',
    'ConfigurationError',
    'ServiceInitializationError',
    'ServiceUnavailableError'
] 