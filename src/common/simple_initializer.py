"""
简化的系统初始化器
提供快速、简单的系统初始化功能
"""
from typing import Optional, Dict, Any
from src.common.containers import EnhancedContainer

class SimpleInitializer:
    """简化的系统初始化器"""
    
    def __init__(self):
        """初始化"""
        self.container: Optional[EnhancedContainer] = None
        self.is_initialized = False
        
    def quick_init(self) -> bool:
        """快速初始化系统
        
        Returns:
            bool: 是否成功初始化
        """
        try:
            # 创建并初始化容器
            self.container = EnhancedContainer()
            
            if self.container.initialize():
                self.is_initialized = True
                print("✅ 系统快速初始化成功")
                return True
            else:
                print("❌ 系统快速初始化失败")
                return False
                
        except Exception as e:
            print(f"❌ 系统快速初始化异常: {str(e)}")
            return False
    
    def get_container(self) -> Optional[EnhancedContainer]:
        """获取容器实例
        
        Returns:
            Optional[EnhancedContainer]: 容器实例
        """
        return self.container
    
    def get_service(self, service_name: str):
        """获取服务实例
        
        Args:
            service_name: 服务名称
            
        Returns:
            服务实例或None
        """
        if not self.is_initialized or not self.container:
            print(f"⚠️ 系统未初始化，无法获取服务: {service_name}")
            return None
            
        return self.container.get_service(service_name)
    
    def get_all_services(self) -> Dict[str, Any]:
        """获取所有服务实例
        
        Returns:
            Dict[str, Any]: 服务名称到实例的映射
        """
        if not self.is_initialized or not self.container:
            print("⚠️ 系统未初始化，无法获取服务")
            return {}
            
        services = {}
        service_names = [
            'config', 'logger', 'error_handler', 'window_manager', 
            'image_processor', 'action_simulator', 'game_analyzer', 
            'game_state', 'auto_operator', 'config_manager'
        ]
        
        for name in service_names:
            try:
                service = self.container.get_service(name)
                if service:
                    services[name] = service
            except Exception as e:
                print(f"⚠️ 获取服务 {name} 失败: {str(e)}")
                
        return services
    
    def check_health(self) -> Dict[str, Any]:
        """检查系统健康状态
        
        Returns:
            Dict[str, Any]: 健康状态信息
        """
        if not self.container:
            return {
                'is_healthy': False,
                'error': '容器未初始化'
            }
            
        return self.container.get_initialization_status()
    
    def cleanup(self):
        """清理资源"""
        self.is_initialized = False
        self.container = None
        print("🧹 系统资源已清理")


# 全局单例实例
_global_initializer: Optional[SimpleInitializer] = None

def get_global_initializer() -> SimpleInitializer:
    """获取全局初始化器实例
    
    Returns:
        SimpleInitializer: 初始化器实例
    """
    global _global_initializer
    if _global_initializer is None:
        _global_initializer = SimpleInitializer()
    return _global_initializer

def init_system() -> bool:
    """初始化系统（全局函数）
    
    Returns:
        bool: 是否成功初始化
    """
    initializer = get_global_initializer()
    return initializer.quick_init()

def get_system_service(service_name: str):
    """获取系统服务（全局函数）
    
    Args:
        service_name: 服务名称
        
    Returns:
        服务实例或None
    """
    initializer = get_global_initializer()
    return initializer.get_service(service_name)

def get_system_container() -> Optional[EnhancedContainer]:
    """获取系统容器（全局函数）
    
    Returns:
        Optional[EnhancedContainer]: 容器实例
    """
    initializer = get_global_initializer()
    return initializer.get_container()

def cleanup_system():
    """清理系统（全局函数）"""
    global _global_initializer
    if _global_initializer:
        _global_initializer.cleanup()
        _global_initializer = None
    print("🧹 全局系统已清理")

# 便捷初始化函数
def one_line_init() -> Optional[EnhancedContainer]:
    """一行代码初始化系统
    
    Returns:
        Optional[EnhancedContainer]: 初始化成功的容器实例
    """
    if init_system():
        return get_system_container()
    return None

__all__ = [
    'SimpleInitializer',
    'get_global_initializer',
    'init_system', 
    'get_system_service',
    'get_system_container',
    'cleanup_system',
    'one_line_init'
] 