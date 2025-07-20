"""日志服务适配器

这个模块提供了日志服务的适配器实现，将现有的日志系统包装为符合ILoggerService接口的服务。
使用适配器模式来保持向后兼容性，同时支持新的依赖注入架构。
"""

from typing import Any, Dict, Optional, Union
from pathlib import Path
import logging
import sys
from datetime import datetime

from ...core.interfaces.services import ILoggerService, IConfigService, LogLevel


class LoggerServiceAdapter(ILoggerService):
    """日志服务适配器
    
    将现有的日志系统适配为ILoggerService接口。
    支持多种日志级别和格式化选项。
    """
    
    def __init__(self, config_service: Optional[IConfigService] = None):
        self._config_service = config_service
        self._logger_instance = None
        self._is_initialized = False
        self._log_level_mapping = {
            LogLevel.DEBUG: logging.DEBUG,
            LogLevel.INFO: logging.INFO,
            LogLevel.WARNING: logging.WARNING,
            LogLevel.ERROR: logging.ERROR,
            LogLevel.CRITICAL: logging.CRITICAL
        }
    
    def _ensure_logger_loaded(self) -> None:
        """确保日志器已加载"""
        if not self._is_initialized:
            try:
                # 尝试导入现有的日志系统
                from ...common.logger import logger
                self._logger_instance = logger
                self._is_initialized = True
            except ImportError:
                # 如果没有现有日志系统，创建一个基本的
                self._create_default_logger()
                self._is_initialized = True
    
    def _create_default_logger(self) -> None:
        """创建默认日志器"""
        self._logger_instance = logging.getLogger('game_automation')
        
        # 设置日志级别
        log_level = logging.INFO
        if self._config_service:
            level_str = self._config_service.get('logging.level', 'INFO')
            log_level = getattr(logging, level_str.upper(), logging.INFO)
        
        self._logger_instance.setLevel(log_level)
        
        # 如果没有处理器，添加控制台处理器
        if not self._logger_instance.handlers:
            console_handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            self._logger_instance.addHandler(console_handler)
    
    def _convert_log_level(self, level: LogLevel) -> int:
        """转换日志级别"""
        return self._log_level_mapping.get(level, logging.INFO)
    
    def debug(self, message: str, **kwargs) -> None:
        """记录调试信息"""
        self._ensure_logger_loaded()
        if self._logger_instance:
            self._logger_instance.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """记录信息"""
        self._ensure_logger_loaded()
        if self._logger_instance:
            self._logger_instance.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """记录警告"""
        self._ensure_logger_loaded()
        if self._logger_instance:
            self._logger_instance.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """记录错误"""
        self._ensure_logger_loaded()
        if self._logger_instance:
            self._logger_instance.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """记录严重错误"""
        self._ensure_logger_loaded()
        if self._logger_instance:
            self._logger_instance.critical(message, **kwargs)
    
    def log(self, level: LogLevel, message: str, **kwargs) -> None:
        """记录指定级别的日志"""
        self._ensure_logger_loaded()
        if self._logger_instance:
            log_level = self._convert_log_level(level)
            self._logger_instance.log(log_level, message, **kwargs)
    
    def exception(self, message: str, **kwargs) -> None:
        """记录异常信息"""
        self._ensure_logger_loaded()
        if self._logger_instance:
            self._logger_instance.exception(message, **kwargs)
    
    def set_level(self, level: LogLevel) -> None:
        """设置日志级别"""
        self._ensure_logger_loaded()
        if self._logger_instance:
            log_level = self._convert_log_level(level)
            self._logger_instance.setLevel(log_level)
    
    def get_level(self) -> LogLevel:
        """获取当前日志级别"""
        self._ensure_logger_loaded()
        if self._logger_instance:
            current_level = self._logger_instance.getEffectiveLevel()
            # 反向映射
            for log_level, std_level in self._log_level_mapping.items():
                if std_level == current_level:
                    return log_level
        return LogLevel.INFO
    
    def add_handler(self, handler_type: str, **config) -> None:
        """添加日志处理器"""
        self._ensure_logger_loaded()
        if not self._logger_instance:
            return
        
        handler = None
        
        if handler_type.lower() == 'file':
            log_file = config.get('filename', 'game_automation.log')
            handler = logging.FileHandler(log_file, encoding='utf-8')
        elif handler_type.lower() == 'console':
            handler = logging.StreamHandler(sys.stdout)
        elif handler_type.lower() == 'rotating':
            from logging.handlers import RotatingFileHandler
            log_file = config.get('filename', 'game_automation.log')
            max_bytes = config.get('max_bytes', 10 * 1024 * 1024)  # 10MB
            backup_count = config.get('backup_count', 5)
            handler = RotatingFileHandler(log_file, maxBytes=max_bytes, 
                                        backupCount=backup_count, encoding='utf-8')
        
        if handler:
            # 设置格式
            format_str = config.get('format', 
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            formatter = logging.Formatter(format_str)
            handler.setFormatter(formatter)
            
            # 设置级别
            if 'level' in config:
                level_str = config['level'].upper()
                level = getattr(logging, level_str, logging.INFO)
                handler.setLevel(level)
            
            self._logger_instance.addHandler(handler)
    
    def remove_handlers(self) -> None:
        """移除所有处理器"""
        self._ensure_logger_loaded()
        if self._logger_instance:
            for handler in self._logger_instance.handlers[:]:
                self._logger_instance.removeHandler(handler)
    
    def get_logger_name(self) -> str:
        """获取日志器名称"""
        self._ensure_logger_loaded()
        if self._logger_instance:
            return self._logger_instance.name
        return 'unknown'
    
    def is_enabled_for(self, level: LogLevel) -> bool:
        """检查是否启用了指定级别的日志"""
        self._ensure_logger_loaded()
        if self._logger_instance:
            log_level = self._convert_log_level(level)
            return self._logger_instance.isEnabledFor(log_level)
        return False
    
    def format_message(self, message: str, **context) -> str:
        """格式化日志消息"""
        if not context:
            return message
        
        # 添加上下文信息
        context_str = ', '.join([f'{k}={v}' for k, v in context.items()])
        return f"{message} [{context_str}]"
    
    def log_performance(self, operation: str, duration: float, **context) -> None:
        """记录性能信息"""
        message = f"Performance: {operation} took {duration:.3f}s"
        self.info(self.format_message(message, **context))
    
    def log_user_action(self, action: str, **context) -> None:
        """记录用户操作"""
        message = f"User Action: {action}"
        self.info(self.format_message(message, **context))
    
    def log_system_event(self, event: str, **context) -> None:
        """记录系统事件"""
        message = f"System Event: {event}"
        self.info(self.format_message(message, **context))
    
    def log_error_with_context(self, error: Exception, context: Dict[str, Any]) -> None:
        """记录带上下文的错误"""
        error_message = f"Error: {type(error).__name__}: {str(error)}"
        formatted_message = self.format_message(error_message, **context)
        self.error(formatted_message)
        
        # 如果有异常堆栈，也记录下来
        if hasattr(error, '__traceback__') and error.__traceback__:
            self.exception("Exception details:")
    
    def create_child_logger(self, name: str) -> 'LoggerServiceAdapter':
        """创建子日志器"""
        self._ensure_logger_loaded()
        
        child_adapter = LoggerServiceAdapter(self._config_service)
        
        if self._logger_instance:
            child_logger = self._logger_instance.getChild(name)
            child_adapter._logger_instance = child_logger
            child_adapter._is_initialized = True
        
        return child_adapter
    
    def flush(self) -> None:
        """刷新所有处理器"""
        self._ensure_logger_loaded()
        if self._logger_instance:
            for handler in self._logger_instance.handlers:
                if hasattr(handler, 'flush'):
                    handler.flush()
    
    def close(self) -> None:
        """关闭所有处理器"""
        self._ensure_logger_loaded()
        if self._logger_instance:
            for handler in self._logger_instance.handlers[:]:
                if hasattr(handler, 'close'):
                    handler.close()
                self._logger_instance.removeHandler(handler)