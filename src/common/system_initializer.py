from typing import Dict, Any, List, Set, Optional
from src.common.containers import Container

# 服务依赖关系定义
SERVICE_DEPENDENCIES = {
    'config': set(),  # 配置服务没有依赖
    'logger': {'config'},  # 日志服务依赖配置
    'window_manager': {'config', 'logger'},  # 窗口管理服务依赖配置和日志
    'image_processor': {'config', 'logger'},  # 图像处理服务依赖配置和日志
    'game_analyzer': {'logger', 'image_processor'},  # 游戏分析服务依赖日志和图像处理
    'action_simulator': {'config', 'logger', 'window_manager'},  # 动作模拟服务依赖配置、日志和窗口管理
    'game_state': {'logger', 'game_analyzer'},  # 游戏状态服务依赖日志和游戏分析
    'auto_operator': {'logger', 'game_state', 'action_simulator', 'image_processor'}  # 自动操作服务依赖日志、游戏状态、动作模拟和图像处理
}

def check_dependencies(service_name: str, initialized_services: Set[str]) -> List[str]:
    """
    检查服务的依赖是否都已初始化
    
    Args:
        service_name: 要检查的服务名称
        initialized_services: 已初始化的服务集合
        
    Returns:
        List[str]: 未满足的依赖列表
    """
    missing_deps = []
    for dep in SERVICE_DEPENDENCIES.get(service_name, set()):
        if dep not in initialized_services:
            missing_deps.append(dep)
    return missing_deps

def get_initialization_order() -> List[str]:
    """
    获取服务初始化顺序
    
    Returns:
        List[str]: 服务初始化顺序列表
    """
    # 使用拓扑排序确定初始化顺序
    order = []
    remaining = set(SERVICE_DEPENDENCIES.keys())
    initialized = set()
    
    while remaining:
        # 找到没有未初始化依赖的服务
        ready = set()
        for service in remaining:
            if not check_dependencies(service, initialized):
                ready.add(service)
        
        if not ready:
            # 存在循环依赖
            raise RuntimeError("检测到循环依赖")
            
        # 将准备好的服务添加到顺序中
        order.extend(ready)
        initialized.update(ready)
        remaining -= ready
    
    return order

def check_container_health(container: Container) -> Dict[str, Any]:
    """
    检查容器健康状态
    
    Args:
        container: 依赖注入容器实例
        
    Returns:
        Dict[str, Any]: 包含检查结果的字典
    """
    health_status = {
        'is_healthy': True,
        'services': {},
        'errors': []
    }
    
    try:
        # 获取初始化顺序
        init_order = get_initialization_order()
        initialized_services = set()
        
        for service_name in init_order:
            try:
                # 检查依赖
                missing_deps = check_dependencies(service_name, initialized_services)
                if missing_deps:
                    health_status['services'][service_name] = {
                        'status': 'error',
                        'missing_dependencies': missing_deps
                    }
                    health_status['is_healthy'] = False
                    health_status['errors'].append(
                        f"服务 {service_name} 缺少依赖: {', '.join(missing_deps)}"
                    )
                    continue
                
                # 尝试初始化服务
                service = getattr(container, service_name)
                if service is None:
                    health_status['services'][service_name] = {
                        'status': 'error',
                        'error': '服务初始化失败'
                    }
                    health_status['is_healthy'] = False
                    health_status['errors'].append(f"服务 {service_name} 初始化失败")
                else:
                    health_status['services'][service_name] = {
                        'status': 'ok'
                    }
                    initialized_services.add(service_name)
                    
            except Exception as e:
                health_status['services'][service_name] = {
                    'status': 'error',
                    'error': str(e)
                }
                health_status['is_healthy'] = False
                health_status['errors'].append(f"服务 {service_name} 初始化异常: {str(e)}")
                
    except Exception as e:
        health_status['is_healthy'] = False
        health_status['errors'].append(f"容器健康检查异常: {str(e)}")
        
    return health_status

def initialize_container() -> Optional[Container]:
    """
    初始化依赖注入容器
    
    Returns:
        Container: 初始化后的容器实例，失败时返回None
    """
    try:
        # 创建容器实例
        container = Container()
        
        # 检查容器健康状态
        health_status = check_container_health(container)
        
        if not health_status['is_healthy']:
            error_msg = "容器初始化失败:\n"
            for error in health_status['errors']:
                error_msg += f"  - {error}\n"
            print(error_msg)
            return None
            
        print("容器初始化成功")
        
        # 预初始化所有服务
        try:
            # 配置服务
            config = container.config()
            if not config:
                raise RuntimeError("配置服务初始化失败")
                
            # 日志服务
            logger = container.logger()
            if not logger:
                raise RuntimeError("日志服务初始化失败")
                
            # 窗口管理服务
            window_manager = container.window_manager()
            if not window_manager:
                raise RuntimeError("窗口管理服务初始化失败")
                
            # 图像处理服务
            image_processor = container.image_processor()
            if not image_processor:
                raise RuntimeError("图像处理服务初始化失败")
                
            # 游戏分析服务
            game_analyzer = container.game_analyzer()
            if not game_analyzer:
                raise RuntimeError("游戏分析服务初始化失败")
                
            # 动作模拟服务
            action_simulator = container.action_simulator()
            if not action_simulator:
                raise RuntimeError("动作模拟服务初始化失败")
                
            # 游戏状态服务
            game_state = container.game_state()
            if not game_state:
                raise RuntimeError("游戏状态服务初始化失败")
                
            # 自动操作服务
            auto_operator = container.auto_operator()
            if not auto_operator:
                raise RuntimeError("自动操作服务初始化失败")
                
        except Exception as e:
            print(f"服务预初始化失败: {str(e)}")
            return None
            
        return container
        
    except Exception as e:
        print(f"容器初始化异常: {str(e)}")
        return None 