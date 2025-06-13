"""
核心业务逻辑模块
包含游戏自动化的核心算法和业务逻辑
"""

# 核心分析器
try:
    from .unified_game_analyzer import UnifiedGameAnalyzer
    __all__ = ['UnifiedGameAnalyzer']
except ImportError:
    UnifiedGameAnalyzer = None
    __all__ = []

# 任务系统
try:
    from .task_system import TaskSystem
    __all__.append('TaskSystem')
except ImportError:
    TaskSystem = None

# 状态机
try:
    from .state_machine import StateMachine
    __all__.append('StateMachine')
except ImportError:
    StateMachine = None

# 游戏适配器
try:
    from .game_adapter import GameAdapter
    __all__.append('GameAdapter')
except ImportError:
    GameAdapter = None

# 子模块导入
from . import analyzers
from . import engines
from . import executors
from . import collectors
from . import models
from . import automation

# 动态导入子模块内容
try:
    # 从analyzers导入
    from .analyzers.image_recognition import ImageRecognition
    __all__.append('ImageRecognition')
except ImportError:
    pass

try:
    # 从engines导入
    from .engines.decision_engine import DecisionEngine
    __all__.append('DecisionEngine')
except ImportError:
    pass

try:
    # 从engines导入DQN代理
    from .engines.dqn_agent import DQNAgent
    __all__.append('DQNAgent')
except ImportError:
    pass

try:
    # 从executors导入
    from .executors.action_executor import ActionExecutor
    __all__.append('ActionExecutor')
except ImportError:
    pass

try:
    # 从executors导入输入控制器
    from .executors.input_controller import InputController
    __all__.append('InputController')
except ImportError:
    pass

try:
    # 从collectors导入
    from .collectors.screen_collector import ScreenCollector
    __all__.append('ScreenCollector')
except ImportError:
    pass

try:
    # 从models导入
    from .models.game_state import GameState
    __all__.append('GameState')
except ImportError:
    pass

try:
    # 从models导入状态历史
    from .models.state_history_model import StateHistoryModel
    __all__.append('StateHistoryModel')
except ImportError:
    pass

try:
    # 从automation导入自动操作器
    from .automation.auto_operator import AutoOperator
    __all__.append('AutoOperator')
except ImportError:
    pass

# 添加子模块到__all__
__all__.extend(['analyzers', 'engines', 'executors', 'collectors', 'models', 'automation'])