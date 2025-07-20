"""
简化的系统初始化器
提供快速、简单的系统初始化功能
"""
from typing import Optional, Dict, Any
from src.common.containers import EnhancedContainer
from src.common.singleton import Singleton
import time

class SimpleInitializer(Singleton):
    """简化的系统初始化器"""
    
    def __init__(self):
        """初始化"""
        # 避免重复初始化（单例模式）
        if hasattr(self, '_initialized'):
            return
            
        self.container: Optional[EnhancedContainer] = None
        self.is_initialized = False
        self.startup_time: float = 0.0
        self.performance_metrics: Dict[str, float] = {}
        self._initialized = True
        
    def quick_init(self) -> bool:
        """快速初始化系统
        
        Returns:
            bool: 是否成功初始化
        """
        if self.is_initialized:
            print("✅ 系统已初始化（单例模式）")
            return True
            
        start_time = time.perf_counter()
        
        try:
            # 创建并初始化容器
            container_start = time.perf_counter()
            self.container = EnhancedContainer()
            container_time = time.perf_counter() - container_start
            self.performance_metrics['container_creation'] = container_time
            
            # 初始化容器
            init_start = time.perf_counter()
            if self.container.initialize():
                init_time = time.perf_counter() - init_start
                self.performance_metrics['container_initialization'] = init_time
                
                self.startup_time = time.perf_counter() - start_time
                self.is_initialized = True
                
                # 性能报告
                if self.startup_time > 2.0:
                    print(f"⚠️ 启动时间较长: {self.startup_time:.2f}s (目标: <2.0s)")
                else:
                    print(f"✅ 系统快速初始化成功 ({self.startup_time:.2f}s)")
                    
                # 详细性能指标
                print(f"   - 容器创建: {container_time:.3f}s")
                print(f"   - 容器初始化: {init_time:.3f}s")
                
                return True
            else:
                print("❌ 系统快速初始化失败")
                return False
                
        except Exception as e:
            self.startup_time = time.perf_counter() - start_time
            print(f"❌ 系统快速初始化异常: {str(e)} (耗时: {self.startup_time:.2f}s)")
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
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """获取性能指标
        
        Returns:
            Dict[str, float]: 性能指标
        """
        metrics = {
            'startup_time': self.startup_time,
            **self.performance_metrics
        }
        
        # 计算额外指标
        if 'container_creation' in self.performance_metrics and 'container_initialization' in self.performance_metrics:
            metrics['overhead_ratio'] = (
                self.performance_metrics['container_creation'] / 
                self.performance_metrics['container_initialization']
            ) if self.performance_metrics['container_initialization'] > 0 else 0
            
        return metrics
    
    def is_performance_acceptable(self) -> bool:
        """检查性能是否达标
        
        Returns:
            bool: 是否达到性能目标
        """
        return self.startup_time > 0 and self.startup_time <= 2.0
        
    def cleanup(self):
        """清理资源"""
        self.is_initialized = False
        self.container = None
        self.startup_time = 0.0
        self.performance_metrics.clear()
        print("🧹 系统资源已清理")


def get_global_initializer() -> SimpleInitializer:
    """获取全局初始化器实例（使用单例模式）
    
    Returns:
        SimpleInitializer: 初始化器实例
    """
    # 由于使用了单例模式，直接创建即可
    return SimpleInitializer()

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
    initializer = get_global_initializer()
    initializer.cleanup()
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

def get_system_performance() -> Dict[str, float]:
    """获取系统性能指标（全局函数）
    
    Returns:
        Dict[str, float]: 性能指标
    """
    initializer = get_global_initializer()
    return initializer.get_performance_metrics()

def is_system_performance_ok() -> bool:
    """检查系统性能是否达标（全局函数）
    
    Returns:
        bool: 是否达到性能目标
    """
    initializer = get_global_initializer()
    return initializer.is_performance_acceptable()

__all__ = [
    'SimpleInitializer',
    'get_global_initializer',
    'init_system', 
    'get_system_service',
    'get_system_container',
    'cleanup_system',
    'one_line_init',
    'get_system_performance',
    'is_system_performance_ok'
] 