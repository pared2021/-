"""错误处理服务适配器

这个模块提供了错误处理服务的适配器实现，将现有的错误处理系统包装为符合IErrorHandler接口的服务。
使用适配器模式来保持向后兼容性，同时支持新的依赖注入架构。
"""

from typing import Any, Dict, Optional, Callable, Type, List
import traceback
import sys
from datetime import datetime
from functools import wraps

from ...core.interfaces.services import IErrorHandler, ILoggerService


class ErrorHandlerServiceAdapter(IErrorHandler):
    """错误处理服务适配器
    
    将现有的错误处理系统适配为IErrorHandler接口。
    提供统一的错误处理、记录和恢复机制。
    """
    
    def __init__(self, logger_service: Optional[ILoggerService] = None):
        self._logger_service = logger_service
        self._error_handler_instance = None
        self._is_initialized = False
        self._error_callbacks: Dict[Type[Exception], List[Callable]] = {}
        self._global_error_callbacks: List[Callable] = []
        self._error_count = 0
        self._last_error_time = None
    
    def _ensure_error_handler_loaded(self) -> None:
        """确保错误处理器已加载"""
        if not self._is_initialized:
            try:
                # 尝试导入现有的错误处理系统
                from ...common.error_handler import error_handler
                self._error_handler_instance = error_handler
                self._is_initialized = True
            except ImportError:
                # 如果没有现有错误处理系统，使用适配器自身
                self._error_handler_instance = self
                self._is_initialized = True
    
    def _log_error(self, message: str, **kwargs) -> None:
        """记录错误日志"""
        if self._logger_service:
            self._logger_service.error(message, **kwargs)
        else:
            print(f"ERROR: {message}", file=sys.stderr)
    
    def _log_warning(self, message: str, **kwargs) -> None:
        """记录警告日志"""
        if self._logger_service:
            self._logger_service.warning(message, **kwargs)
        else:
            print(f"WARNING: {message}", file=sys.stderr)
    
    def _log_info(self, message: str, **kwargs) -> None:
        """记录信息日志"""
        if self._logger_service:
            self._logger_service.info(message, **kwargs)
        else:
            print(f"INFO: {message}")
    
    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> bool:
        """处理错误"""
        self._ensure_error_handler_loaded()
        
        # 更新错误统计
        self._error_count += 1
        self._last_error_time = datetime.now()
        
        # 准备上下文信息
        error_context = context or {}
        error_context.update({
            'error_type': type(error).__name__,
            'error_message': str(error),
            'error_count': self._error_count,
            'timestamp': self._last_error_time.isoformat()
        })
        
        # 记录错误
        error_message = f"处理异常: {type(error).__name__}: {str(error)}"
        self._log_error(error_message, **error_context)
        
        # 记录堆栈跟踪
        if hasattr(error, '__traceback__') and error.__traceback__:
            stack_trace = ''.join(traceback.format_exception(
                type(error), error, error.__traceback__
            ))
            self._log_error(f"堆栈跟踪:\n{stack_trace}")
        
        # 如果有现有的错误处理器，使用它
        if (self._error_handler_instance and 
            self._error_handler_instance != self and
            hasattr(self._error_handler_instance, 'handle_error')):
            try:
                return self._error_handler_instance.handle_error(error, context)
            except Exception as handler_error:
                self._log_error(f"错误处理器本身出错: {handler_error}")
        
        # 执行特定类型的错误回调
        error_type = type(error)
        if error_type in self._error_callbacks:
            for callback in self._error_callbacks[error_type]:
                try:
                    callback(error, error_context)
                except Exception as callback_error:
                    self._log_error(f"错误回调执行失败: {callback_error}")
        
        # 执行全局错误回调
        for callback in self._global_error_callbacks:
            try:
                callback(error, error_context)
            except Exception as callback_error:
                self._log_error(f"全局错误回调执行失败: {callback_error}")
        
        # 返回是否成功处理
        return True
    
    def log_error(self, message: str, error: Optional[Exception] = None, 
                  context: Optional[Dict[str, Any]] = None) -> None:
        """记录错误信息"""
        error_context = context or {}
        
        if error:
            error_context.update({
                'error_type': type(error).__name__,
                'error_message': str(error)
            })
            message = f"{message}: {type(error).__name__}: {str(error)}"
        
        self._log_error(message, **error_context)
        
        # 如果有异常对象，记录堆栈跟踪
        if error and hasattr(error, '__traceback__') and error.__traceback__:
            stack_trace = ''.join(traceback.format_exception(
                type(error), error, error.__traceback__
            ))
            self._log_error(f"堆栈跟踪:\n{stack_trace}")
    
    def log_warning(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """记录警告信息"""
        warning_context = context or {}
        self._log_warning(message, **warning_context)
    
    def create_error_context(self, **kwargs) -> Dict[str, Any]:
        """创建错误上下文"""
        context = {
            'timestamp': datetime.now().isoformat(),
            'error_count': self._error_count
        }
        context.update(kwargs)
        return context
    
    def register_error_callback(self, error_type: Type[Exception], 
                               callback: Callable[[Exception, Dict[str, Any]], None]) -> None:
        """注册特定错误类型的回调"""
        if error_type not in self._error_callbacks:
            self._error_callbacks[error_type] = []
        self._error_callbacks[error_type].append(callback)
    
    def register_global_error_callback(self, callback: Callable[[Exception, Dict[str, Any]], None]) -> None:
        """注册全局错误回调"""
        self._global_error_callbacks.append(callback)
    
    def unregister_error_callback(self, error_type: Type[Exception], 
                                 callback: Callable[[Exception, Dict[str, Any]], None]) -> None:
        """取消注册错误回调"""
        if error_type in self._error_callbacks:
            try:
                self._error_callbacks[error_type].remove(callback)
                if not self._error_callbacks[error_type]:
                    del self._error_callbacks[error_type]
            except ValueError:
                pass
    
    def unregister_global_error_callback(self, callback: Callable[[Exception, Dict[str, Any]], None]) -> None:
        """取消注册全局错误回调"""
        try:
            self._global_error_callbacks.remove(callback)
        except ValueError:
            pass
    
    def clear_error_callbacks(self) -> None:
        """清除所有错误回调"""
        self._error_callbacks.clear()
        self._global_error_callbacks.clear()
    
    def get_error_stats(self) -> Dict[str, Any]:
        """获取错误统计信息"""
        return {
            'total_errors': self._error_count,
            'last_error_time': self._last_error_time.isoformat() if self._last_error_time else None,
            'registered_callbacks': len(self._error_callbacks),
            'global_callbacks': len(self._global_error_callbacks)
        }
    
    def reset_error_stats(self) -> None:
        """重置错误统计"""
        self._error_count = 0
        self._last_error_time = None
    
    def with_error_handling(self, func: Callable, 
                           context: Optional[Dict[str, Any]] = None,
                           reraise: bool = False) -> Callable:
        """装饰器：为函数添加错误处理"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_context = self.create_error_context(**(context or {}))
                error_context.update({
                    'function_name': func.__name__,
                    'args': str(args)[:200],  # 限制长度
                    'kwargs': str(kwargs)[:200]
                })
                
                self.handle_error(e, error_context)
                
                if reraise:
                    raise
                return None
        
        return wrapper
    
    def safe_execute(self, func: Callable, *args, 
                    default_return=None, context: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        """安全执行函数"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_context = self.create_error_context(**(context or {}))
            error_context.update({
                'function_name': getattr(func, '__name__', 'unknown'),
                'args': str(args)[:200],
                'kwargs': str(kwargs)[:200]
            })
            
            self.handle_error(e, error_context)
            return default_return
    
    def is_critical_error(self, error: Exception) -> bool:
        """判断是否为严重错误"""
        critical_errors = (
            SystemExit, KeyboardInterrupt, MemoryError,
            SystemError, OSError
        )
        return isinstance(error, critical_errors)
    
    def should_retry(self, error: Exception, retry_count: int = 0, max_retries: int = 3) -> bool:
        """判断是否应该重试"""
        if retry_count >= max_retries:
            return False
        
        if self.is_critical_error(error):
            return False
        
        # 对于网络相关错误，可以重试
        retryable_errors = (
            ConnectionError, TimeoutError, 
            OSError  # 包括网络相关的OSError
        )
        
        return isinstance(error, retryable_errors)
    
    def format_error_message(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> str:
        """格式化错误消息"""
        message = f"{type(error).__name__}: {str(error)}"
        
        if context:
            context_str = ', '.join([f'{k}={v}' for k, v in context.items()])
            message += f" [Context: {context_str}]"
        
        return message