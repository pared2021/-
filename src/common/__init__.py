"""
通用基础设施模块
提供跨层次的通用基础设施组件
"""

from src.common.system_initializer import (
    check_dependencies, 
    get_initialization_order,
    check_container_health,
    initialize_container,
    SERVICE_DEPENDENCIES
)

# 依赖注入容器
try:
    from src.common.containers import DIContainer
    CONTAINER_AVAILABLE = True
except ImportError:
    CONTAINER_AVAILABLE = False
    DIContainer = None

# 错误处理器（从core迁移而来）
try:
    from src.common.error_handler import ErrorHandler
    ERROR_HANDLER_AVAILABLE = True
except ImportError:
    ERROR_HANDLER_AVAILABLE = False
    ErrorHandler = None

# 恢复管理器
try:
    from src.common.recovery import RecoveryManager
    RECOVERY_AVAILABLE = True
except ImportError:
    RECOVERY_AVAILABLE = False
    RecoveryManager = None

# 系统监控
try:
    from src.common.monitor import SystemMonitor
    MONITOR_AVAILABLE = True
except ImportError:
    MONITOR_AVAILABLE = False
    SystemMonitor = None

# PyQt6相关导入设为可选
try:
    from src.common.app_utils import (
        set_dpi_awareness,
        create_manifest_file,
        set_app_style,
        is_admin,
        run_as_admin,
        create_default_icons,
        setup_environment
    )
    APP_UTILS_AVAILABLE = True
except ImportError:
    APP_UTILS_AVAILABLE = False
    # 提供空实现
    def set_dpi_awareness(): pass
    def create_manifest_file(): pass
    def set_app_style(app): pass
    def is_admin(): return False
    def run_as_admin(): pass
    def create_default_icons(): pass
    def setup_environment(): pass

from src.common.system_cleanup import cleanup

# 异常基类（通用异常层次结构）
from src.common.exceptions import (
    GameAutomationError,
    WindowError,
    ImageProcessingError,
    ActionError,
    ModelError,
    ConfigError,
    StateError,
    RecoveryError
)

__all__ = [
    # 系统初始化
    'check_dependencies',
    'get_initialization_order',
    'check_container_health',
    'initialize_container',
    'SERVICE_DEPENDENCIES',
    
    # 依赖注入
    'DIContainer',
    'CONTAINER_AVAILABLE',
    
    # 错误处理
    'ErrorHandler',
    'ERROR_HANDLER_AVAILABLE',
    
    # 恢复管理
    'RecoveryManager',
    'RECOVERY_AVAILABLE',
    
    # 系统监控
    'SystemMonitor',
    'MONITOR_AVAILABLE',
    
    # 应用工具（可选）
    'set_dpi_awareness',
    'create_manifest_file',
    'set_app_style',
    'is_admin',
    'run_as_admin',
    'create_default_icons',
    'setup_environment',
    'APP_UTILS_AVAILABLE',
    
    # 系统清理
    'cleanup',
    
    # 异常基类
    'GameAutomationError',
    'WindowError',
    'ImageProcessingError',
    'ActionError',
    'ModelError',
    'ConfigError',
    'StateError',
    'RecoveryError'
] 