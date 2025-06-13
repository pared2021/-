# 基础服务（无外部依赖）
from .config import Config, config

# 可选服务（有外部依赖）
__all__ = ['Config', 'config']

# 尝试导入其他服务，如果失败则跳过
try:
    from .logger import GameLogger
    __all__.append('GameLogger')
except ImportError:
    GameLogger = None

try:
    from .exceptions import (
        GameAutomationError, 
        WindowNotFoundError, 
        WindowAccessError,
        ImageProcessingError,
        ActionSimulationError,
        GameStateError,
        TemplateCollectionError,
        ModelTrainingError,
        ConfigurationError,
        ServiceInitializationError,
        ServiceUnavailableError
    )
    __all__.extend([
        'GameAutomationError', 'WindowNotFoundError', 'WindowAccessError',
        'ImageProcessingError', 'ActionSimulationError', 'GameStateError',
        'TemplateCollectionError', 'ModelTrainingError', 'ConfigurationError',
        'ServiceInitializationError', 'ServiceUnavailableError'
    ])
except ImportError:
    pass

# 需要外部依赖的服务
try:
    from .window_manager import GameWindowManager
    __all__.append('GameWindowManager')
except ImportError:
    GameWindowManager = None

try:
    from .image_processor import ImageProcessor
    __all__.append('ImageProcessor')
except ImportError:
    ImageProcessor = None

try:
    from .action_simulator import ActionSimulator
    __all__.append('ActionSimulator')
except ImportError:
    ActionSimulator = None

try:
    from .game_analyzer import GameAnalyzer
    __all__.append('GameAnalyzer')
except ImportError:
    GameAnalyzer = None

try:
    from .template_collector import TemplateCollector
    __all__.append('TemplateCollector')
except ImportError:
    TemplateCollector = None

# 新增的服务
try:
    from .resource_manager import ResourceManager
    __all__.append('ResourceManager')
except ImportError:
    ResourceManager = None

try:
    from .capture_engines import CaptureEngines
    __all__.append('CaptureEngines')
except ImportError:
    CaptureEngines = None 