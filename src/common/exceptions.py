class GameAutomationError(Exception):
    """游戏自动化基础异常类"""
    def __init__(self, message: str, error_code: int = 0):
        super().__init__(message)
        self.error_code = error_code
        self.message = message

class WindowError(GameAutomationError):
    """窗口操作相关异常"""
    def __init__(self, message: str, error_code: int = 1000):
        super().__init__(message, error_code)

class ImageProcessingError(GameAutomationError):
    """图像处理相关异常"""
    def __init__(self, message: str, error_code: int = 2000):
        super().__init__(message, error_code)

class ActionError(GameAutomationError):
    """动作模拟相关异常"""
    def __init__(self, message: str, error_code: int = 3000):
        super().__init__(message, error_code)

class ModelError(GameAutomationError):
    """模型相关异常"""
    def __init__(self, message: str, error_code: int = 4000):
        super().__init__(message, error_code)

class ConfigError(GameAutomationError):
    """配置相关异常"""
    def __init__(self, message: str, error_code: int = 5000):
        super().__init__(message, error_code)

class StateError(GameAutomationError):
    """状态管理相关异常"""
    def __init__(self, message: str, error_code: int = 6000):
        super().__init__(message, error_code)

class RecoveryError(GameAutomationError):
    """恢复机制相关异常"""
    def __init__(self, message: str, error_code: int = 7000):
        super().__init__(message, error_code) 