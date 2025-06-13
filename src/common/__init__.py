"""
通用工具模块包
"""

from src.common.system_initializer import (
    check_dependencies, 
    get_initialization_order,
    check_container_health,
    initialize_container,
    SERVICE_DEPENDENCIES
)

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

__all__ = [
    # 系统初始化
    'check_dependencies',
    'get_initialization_order',
    'check_container_health',
    'initialize_container',
    'SERVICE_DEPENDENCIES',
    
    # 应用工具（可选）
    'set_dpi_awareness',
    'create_manifest_file',
    'set_app_style',
    'is_admin',
    'run_as_admin',
    'create_default_icons',
    'setup_environment',
    
    # 系统清理
    'cleanup'
] 