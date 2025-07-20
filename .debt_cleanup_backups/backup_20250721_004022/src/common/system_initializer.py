from typing import Dict, Any, List, Set, Optional
from src.common.containers import EnhancedContainer

# 服务依赖定义（向后兼容）
SERVICE_DEPENDENCIES = {
    'config': [],
    'logger': ['config'],
    'error_handler': ['config', 'logger'],
    'window_manager': ['config', 'logger'],
    'image_processor': ['config', 'logger'],
    'action_simulator': ['config', 'logger'],
    'game_analyzer': ['config', 'logger', 'image_processor'],
    'game_state': ['config', 'logger'],
    'auto_operator': ['config', 'logger', 'action_simulator', 'game_analyzer'],
    'config_manager': ['config']
}

def initialize_container() -> Optional[EnhancedContainer]:
    """
    简化的容器初始化函数
    
    Returns:
        EnhancedContainer: 初始化后的容器实例，失败时返回None
    """
    try:
        # 创建增强容器实例
        container = EnhancedContainer()
        
        # 使用分阶段初始化
        if container.initialize():
            print("容器初始化成功")
            return container
        else:
            print("容器初始化失败")
            return None
            
    except Exception as e:
        print(f"容器初始化异常: {str(e)}")
        return None

def check_container_health(container: EnhancedContainer) -> Dict[str, Any]:
    """
    简化的容器健康检查
    
    Args:
        container: 增强容器实例
        
    Returns:
        Dict[str, Any]: 包含检查结果的字典
    """
    if not container:
        return {
            'is_healthy': False,
            'errors': ['容器实例为空']
        }
        
    try:
        # 获取容器状态
        status = container.get_initialization_status()
        
        return {
            'is_healthy': status['is_ready'],
            'phase': status['phase'],
            'services_created': status['services_created'],
            'creation_order': status['creation_order'],
            'errors': [] if status['is_ready'] else ['容器未完成初始化']
        }
        
    except Exception as e:
        return {
            'is_healthy': False,
            'errors': [f"健康检查异常: {str(e)}"]
        }

def get_service_safely(container: EnhancedContainer, service_name: str):
    """
    安全地获取服务
    
    Args:
        container: 容器实例
        service_name: 服务名称
        
    Returns:
        服务实例或None
    """
    try:
        if not container.is_ready():
            print(f"容器未就绪，无法获取服务: {service_name}")
            return None
            
        return container.get_service(service_name)
        
    except Exception as e:
        print(f"获取服务 {service_name} 失败: {str(e)}")
        return None

# 向后兼容性函数（已废弃，保留用于兼容）
def check_dependencies(service_name: str, initialized_services: Set[str]) -> List[str]:
    """废弃函数 - 仅用于向后兼容"""
    print(f"Warning: check_dependencies 已废弃，请使用 EnhancedContainer 的分阶段初始化")
    return []

def get_initialization_order() -> List[str]:
    """废弃函数 - 仅用于向后兼容"""
    print(f"Warning: get_initialization_order 已废弃，请使用 EnhancedContainer 的分阶段初始化")
    return ['config', 'logger', 'error_handler', 'window_manager', 'image_processor', 
            'action_simulator', 'game_analyzer', 'game_state', 'auto_operator', 'config_manager'] 