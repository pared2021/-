class GameAutomationError(Exception):
    """游戏自动化基础异常类"""
    pass

class WindowNotFoundError(GameAutomationError):
    """窗口未找到异常"""
    pass

class ImageProcessingError(GameAutomationError):
    """图像处理异常"""
    pass

class ActionSimulationError(GameAutomationError):
    """动作模拟异常"""
    pass

class GameStateError(GameAutomationError):
    """游戏状态异常"""
    pass

class TemplateCollectionError(GameAutomationError):
    """模板收集异常"""
    pass

class ModelTrainingError(GameAutomationError):
    """模型训练异常"""
    pass

class ConfigurationError(GameAutomationError):
    """配置异常"""
    pass 