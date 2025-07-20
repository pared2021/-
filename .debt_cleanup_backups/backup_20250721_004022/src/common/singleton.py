from threading import Lock
from typing import Dict, Type, Any

class SingletonMeta(type):
    """
    线程安全的单例元类实现
    确保每个类只有一个实例，避免重复实例化
    """
    _instances: Dict[Type, Any] = {}
    _lock: Lock = Lock()
    
    def __call__(cls, *args, **kwargs):
        """
        控制类的实例化过程
        """
        # 双重检查锁定模式，确保线程安全
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]

class Singleton(metaclass=SingletonMeta):
    """
    单例基类，继承此类的子类将自动成为单例
    
    使用方法：
    class MyClass(Singleton):
        def __init__(self):
            self.value = "singleton instance"
    """
    
    def __init__(self):
        """
        子类可以重写此方法进行初始化
        注意：只有第一次实例化时才会调用
        """
        pass

# 单例装饰器版本，用于装饰现有类
def singleton(cls):
    """
    单例装饰器，将普通类转换为单例类
    
    用法:
    @singleton
    class MyClass:
        pass
    """
    instances = {}
    lock = Lock()
    
    def get_instance(*args, **kwargs):
        if cls not in instances:
            with lock:
                if cls not in instances:
                    instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance

__all__ = ['SingletonMeta', 'Singleton', 'singleton'] 