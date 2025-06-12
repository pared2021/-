import logging
import os
import threading
import time
from datetime import datetime
from typing import Optional, Dict, Any
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from .config import Config
from .exceptions import GameAutomationError

class GameLogger:
    """游戏自动化日志类"""
    
    def __init__(self, config: Config, name: str = 'game_automation'):
        """
        初始化日志器
        
        Args:
            config: 配置对象
            name: 日志器名称
        """
        self.config = config
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, config.logging.log_level))
        
        # 创建日志目录
        log_dir = config.logging.log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # 设置日志文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'{name}_{timestamp}.log')
        
        # 创建格式化器
        formatter = logging.Formatter(
            config.logging.log_format,
            datefmt=config.logging.date_format
        )
        
        # 创建文件处理器
        if config.logging.enable_file:
            if config.logging.log_rotation == 'size':
                file_handler = RotatingFileHandler(
                    log_file,
                    maxBytes=config.logging.max_file_size,
                    backupCount=config.logging.backup_count,
                    encoding='utf-8'
                )
            else:
                when = config.logging.log_rotation
                file_handler = TimedRotatingFileHandler(
                    log_file,
                    when=when,
                    interval=1,
                    backupCount=config.logging.backup_count,
                    encoding='utf-8'
                )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        
        # 创建控制台处理器
        if config.logging.enable_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # 递归保护
        self._recursion_lock = threading.RLock()
        self._recursion_depth = 0
        self._max_recursion_depth = config.logging.max_recursion_depth
        self._recursion_messages = {}  # 消息缓存，防止重复记录
        
        # 性能统计
        self._stats = {
            'debug': 0,
            'info': 0,
            'warning': 0,
            'error': 0,
            'critical': 0
        }
        self._stats_lock = threading.Lock()
        
        self.logger.info("日志服务初始化完成")
    
    def _log_with_recursion_guard(self, level_method, message, *args, **kwargs):
        """带递归保护的日志记录"""
        # 使用锁来保护递归计数
        with self._recursion_lock:
            # 检查是否是重复消息
            message_hash = hash(f"{level_method.__name__}:{message}")
            last_time = self._recursion_messages.get(message_hash, 0)
            current_time = time.time()
            
            # 如果同一消息在短时间内重复出现，跳过
            if current_time - last_time < 0.1:  # 100毫秒内的相同消息被视为重复
                return
                
            # 更新消息最后出现时间
            self._recursion_messages[message_hash] = current_time
            
            # 检查递归深度是否超过限制
            if self._recursion_depth >= self._max_recursion_depth:
                return
                
            # 递归深度加1
            self._recursion_depth += 1
            
        try:
            # 调用原始的日志方法
            level_method(message, *args, **kwargs)
            
            # 更新统计信息
            with self._stats_lock:
                level_name = level_method.__name__.lower()
                if level_name in self._stats:
                    self._stats[level_name] += 1
        finally:
            # 递归深度减1
            with self._recursion_lock:
                self._recursion_depth -= 1
    
    def debug(self, message: str, *args, **kwargs):
        """记录调试信息"""
        self._log_with_recursion_guard(self.logger.debug, message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """记录一般信息"""
        self._log_with_recursion_guard(self.logger.info, message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """记录警告信息"""
        self._log_with_recursion_guard(self.logger.warning, message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """记录错误信息"""
        self._log_with_recursion_guard(self.logger.error, message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """记录严重错误信息"""
        self._log_with_recursion_guard(self.logger.critical, message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs):
        """记录异常信息"""
        self._log_with_recursion_guard(self.logger.exception, message, *args, **kwargs)
    
    def log_screenshot(self, image: Optional[bytes], description: str = ''):
        """
        记录截图
        
        Args:
            image: 截图数据
            description: 截图描述
        """
        if image is None:
            self.warning(f"截图失败: {description}")
            return
        
        # 创建截图目录
        screenshot_dir = os.path.join(self.config.logging.log_dir, 'screenshots')
        os.makedirs(screenshot_dir, exist_ok=True)
        
        # 保存截图
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'screenshot_{timestamp}.png'
        filepath = os.path.join(screenshot_dir, filename)
        
        try:
            with open(filepath, 'wb') as f:
                f.write(image)
            self.info(f"截图已保存: {filepath} - {description}")
        except Exception as e:
            self.error(f"保存截图失败: {e}")
    
    def get_stats(self) -> Dict[str, int]:
        """
        获取日志统计信息
        
        Returns:
            Dict[str, int]: 统计信息
        """
        with self._stats_lock:
            return self._stats.copy()
    
    def cleanup(self):
        """清理日志资源"""
        # 清理过期的日志文件
        if self.config.logging.log_retention_days > 0:
            try:
                log_dir = self.config.logging.log_dir
                current_time = time.time()
                
                for filename in os.listdir(log_dir):
                    filepath = os.path.join(log_dir, filename)
                    if os.path.isfile(filepath):
                        # 检查文件修改时间
                        file_time = os.path.getmtime(filepath)
                        if current_time - file_time > self.config.logging.log_retention_days * 86400:
                            os.remove(filepath)
                            self.info(f"删除过期日志文件: {filename}")
            except Exception as e:
                self.error(f"清理日志文件失败: {e}")
        
        # 关闭所有处理器
        for handler in self.logger.handlers:
            handler.close()
            self.logger.removeHandler(handler)
    
    def set_level(self, level):
        """设置日志级别
        
        Args:
            level: 日志级别，可以是logging模块的常量或字符串
        """
        # 如果是字符串，转换为logging模块的常量
        if isinstance(level, str):
            level = getattr(logging, level.upper())
        
        self.logger.setLevel(level)
        
        # 更新所有处理器的级别
        for handler in self.logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.setLevel(logging.DEBUG)  # 文件记录所有级别
            else:
                handler.setLevel(level)  # 控制台使用新级别
            
        self.info(f"日志级别已设置为: {logging.getLevelName(level)}") 