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
    from .exceptions import GameAutomationError, WindowNotFoundError
    __all__.extend(['GameAutomationError', 'WindowNotFoundError'])
except ImportError:
    GameAutomationError = None
    WindowNotFoundError = None

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
    from .game_state import GameState
    __all__.append('GameState')
except ImportError:
    GameState = None

try:
    from .auto_operator import AutoOperator
    __all__.append('AutoOperator')
except ImportError:
    AutoOperator = None

try:
    from .config_manager import ConfigManager
    __all__.append('ConfigManager')
except ImportError:
    ConfigManager = None 