"""性能监控服务适配器

这个模块提供了性能监控服务的适配器实现，将现有的性能监控系统包装为符合IPerformanceMonitor接口的服务。
使用适配器模式来保持向后兼容性，同时支持新的依赖注入架构。
"""

from typing import Dict, Any, Optional, List, Callable
import time
import threading
import psutil
import json
from datetime import datetime, timedelta
from collections import defaultdict, deque

from ...core.interfaces.services import (
    IPerformanceMonitor, ILoggerService, IConfigService, IErrorHandler
)


class PerformanceMonitorServiceAdapter(IPerformanceMonitor):
    """性能监控服务适配器
    
    将现有的性能监控系统适配为IPerformanceMonitor接口。
    提供系统性能监控、指标收集和分析功能。
    """
    
    def __init__(self, logger_service: Optional[ILoggerService] = None,
                 config_service: Optional[IConfigService] = None,
                 error_handler: Optional[IErrorHandler] = None):
        self._logger_service = logger_service
        self._config_service = config_service
        self._error_handler = error_handler
        self._performance_monitor_instance = None
        self._is_initialized = False
        
        # 监控状态
        self._is_monitoring = False
        self._monitor_thread = None
        self._monitor_lock = threading.Lock()
        
        # 性能指标存储
        self._metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self._current_metrics: Dict[str, Any] = {}
        self._metric_callbacks: Dict[str, List[Callable]] = defaultdict(list)
        self._alert_thresholds: Dict[str, Dict[str, float]] = {}
        self._alert_callbacks: List[Callable] = []
        
        # 配置
        self._monitor_interval = 1.0  # 秒
        self._history_size = 1000
        self._auto_save_enabled = True
        self._save_file_path = None
        self._enable_system_metrics = True
        self._enable_process_metrics = True
        self._enable_custom_metrics = True
        
        # 统计
        self._monitoring_start_time = None
        self._total_samples = 0
        self._alert_count = 0
        self._last_alert_time = None
        
        # 系统信息
        self._process = psutil.Process()
        self._system_info = self._get_system_info()
    
    def _ensure_performance_monitor_loaded(self) -> None:
        """确保性能监控器已加载"""
        if not self._is_initialized:
            try:
                # 尝试导入现有的性能监控系统
                from ...common.performance_monitor import performance_monitor
                self._performance_monitor_instance = performance_monitor
                self._is_initialized = True
                self._log_info("性能监控器已加载")
                
                # 同步现有监控器状态
                self._sync_with_existing_monitor()
                
            except ImportError as e:
                self._log_error(f"无法导入现有性能监控系统: {e}")
                # 使用内置实现
                self._performance_monitor_instance = self
                self._is_initialized = True
                self._log_info("使用内置性能监控器")
            
            # 加载配置
            self._load_configuration()
            
            # 设置默认阈值
            self._setup_default_thresholds()
    
    def _sync_with_existing_monitor(self) -> None:
        """与现有性能监控器同步"""
        try:
            if hasattr(self._performance_monitor_instance, 'is_monitoring'):
                self._is_monitoring = self._performance_monitor_instance.is_monitoring()
            
            if hasattr(self._performance_monitor_instance, 'get_current_metrics'):
                metrics = self._performance_monitor_instance.get_current_metrics()
                if metrics:
                    self._current_metrics.update(metrics)
            
            self._log_debug(f"已同步现有性能监控器: 监控状态 {self._is_monitoring}")
        
        except Exception as e:
            self._handle_error(e, {'operation': '_sync_with_existing_monitor'})
    
    def _load_configuration(self) -> None:
        """加载配置"""
        if self._config_service:
            self._monitor_interval = self._config_service.get('performance_monitor.interval', 1.0)
            self._history_size = self._config_service.get('performance_monitor.history_size', 1000)
            self._auto_save_enabled = self._config_service.get('performance_monitor.auto_save_enabled', True)
            self._save_file_path = self._config_service.get('performance_monitor.save_file_path', 'performance_metrics.json')
            self._enable_system_metrics = self._config_service.get('performance_monitor.enable_system_metrics', True)
            self._enable_process_metrics = self._config_service.get('performance_monitor.enable_process_metrics', True)
            self._enable_custom_metrics = self._config_service.get('performance_monitor.enable_custom_metrics', True)
            
            # 更新历史大小
            for metric_name in self._metrics_history:
                self._metrics_history[metric_name] = deque(self._metrics_history[metric_name], maxlen=self._history_size)
    
    def _setup_default_thresholds(self) -> None:
        """设置默认阈值"""
        default_thresholds = {
            'cpu_percent': {'warning': 80.0, 'critical': 95.0},
            'memory_percent': {'warning': 80.0, 'critical': 95.0},
            'disk_usage_percent': {'warning': 85.0, 'critical': 95.0},
            'process_memory_mb': {'warning': 1000.0, 'critical': 2000.0},
            'process_cpu_percent': {'warning': 50.0, 'critical': 80.0}
        }
        
        for metric, thresholds in default_thresholds.items():
            if metric not in self._alert_thresholds:
                self._alert_thresholds[metric] = thresholds
    
    def _get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        try:
            return {
                'platform': psutil.WINDOWS if hasattr(psutil, 'WINDOWS') else 'unknown',
                'cpu_count': psutil.cpu_count(),
                'cpu_count_logical': psutil.cpu_count(logical=True),
                'memory_total': psutil.virtual_memory().total,
                'boot_time': psutil.boot_time(),
                'python_pid': self._process.pid
            }
        except Exception as e:
            self._handle_error(e, {'operation': '_get_system_info'})
            return {}
    
    def _collect_system_metrics(self) -> Dict[str, Any]:
        """收集系统指标"""
        metrics = {}
        
        try:
            if self._enable_system_metrics:
                # CPU 使用率
                metrics['cpu_percent'] = psutil.cpu_percent(interval=None)
                metrics['cpu_count'] = psutil.cpu_count()
                
                # 内存使用情况
                memory = psutil.virtual_memory()
                metrics['memory_total'] = memory.total
                metrics['memory_available'] = memory.available
                metrics['memory_used'] = memory.used
                metrics['memory_percent'] = memory.percent
                
                # 磁盘使用情况
                disk = psutil.disk_usage('/')
                metrics['disk_total'] = disk.total
                metrics['disk_used'] = disk.used
                metrics['disk_free'] = disk.free
                metrics['disk_usage_percent'] = (disk.used / disk.total) * 100
                
                # 网络统计
                net_io = psutil.net_io_counters()
                metrics['network_bytes_sent'] = net_io.bytes_sent
                metrics['network_bytes_recv'] = net_io.bytes_recv
                metrics['network_packets_sent'] = net_io.packets_sent
                metrics['network_packets_recv'] = net_io.packets_recv
        
        except Exception as e:
            self._handle_error(e, {'operation': '_collect_system_metrics'})
        
        return metrics
    
    def _collect_process_metrics(self) -> Dict[str, Any]:
        """收集进程指标"""
        metrics = {}
        
        try:
            if self._enable_process_metrics:
                # 进程 CPU 使用率
                metrics['process_cpu_percent'] = self._process.cpu_percent()
                
                # 进程内存使用情况
                memory_info = self._process.memory_info()
                metrics['process_memory_rss'] = memory_info.rss
                metrics['process_memory_vms'] = memory_info.vms
                metrics['process_memory_mb'] = memory_info.rss / (1024 * 1024)
                
                # 进程线程数
                metrics['process_num_threads'] = self._process.num_threads()
                
                # 进程文件描述符数（Windows 上可能不可用）
                try:
                    metrics['process_num_fds'] = self._process.num_fds()
                except (AttributeError, psutil.AccessDenied):
                    pass
                
                # 进程运行时间
                create_time = self._process.create_time()
                metrics['process_uptime'] = time.time() - create_time
        
        except Exception as e:
            self._handle_error(e, {'operation': '_collect_process_metrics'})
        
        return metrics
    
    def _check_alerts(self, metrics: Dict[str, Any]) -> None:
        """检查告警"""
        try:
            current_time = time.time()
            
            for metric_name, value in metrics.items():
                if metric_name in self._alert_thresholds:
                    thresholds = self._alert_thresholds[metric_name]
                    
                    alert_level = None
                    if 'critical' in thresholds and value >= thresholds['critical']:
                        alert_level = 'critical'
                    elif 'warning' in thresholds and value >= thresholds['warning']:
                        alert_level = 'warning'
                    
                    if alert_level:
                        alert_data = {
                            'metric': metric_name,
                            'value': value,
                            'threshold': thresholds[alert_level],
                            'level': alert_level,
                            'timestamp': current_time
                        }
                        
                        self._trigger_alert(alert_data)
        
        except Exception as e:
            self._handle_error(e, {'operation': '_check_alerts'})
    
    def _trigger_alert(self, alert_data: Dict[str, Any]) -> None:
        """触发告警"""
        try:
            self._alert_count += 1
            self._last_alert_time = alert_data['timestamp']
            
            # 记录告警
            self._log_warning(f"性能告警: {alert_data['metric']} = {alert_data['value']:.2f} (阈值: {alert_data['threshold']:.2f})")
            
            # 通知告警回调
            for callback in self._alert_callbacks:
                try:
                    callback(alert_data)
                except Exception as e:
                    self._handle_error(e, {'operation': 'alert_callback', 'alert_data': alert_data})
        
        except Exception as e:
            self._handle_error(e, {'operation': '_trigger_alert', 'alert_data': alert_data})
    
    def _monitor_loop(self) -> None:
        """监控循环"""
        self._log_info("性能监控循环已启动")
        
        while self._is_monitoring:
            try:
                start_time = time.time()
                
                # 收集指标
                metrics = {}
                metrics.update(self._collect_system_metrics())
                metrics.update(self._collect_process_metrics())
                
                # 添加时间戳
                metrics['timestamp'] = start_time
                
                # 更新当前指标
                self._current_metrics = metrics
                
                # 存储历史数据
                for metric_name, value in metrics.items():
                    if isinstance(value, (int, float)):
                        self._metrics_history[metric_name].append({
                            'value': value,
                            'timestamp': start_time
                        })
                
                # 检查告警
                self._check_alerts(metrics)
                
                # 通知指标回调
                for metric_name, callbacks in self._metric_callbacks.items():
                    if metric_name in metrics:
                        for callback in callbacks:
                            try:
                                callback(metric_name, metrics[metric_name], start_time)
                            except Exception as e:
                                self._handle_error(e, {'operation': 'metric_callback', 'metric': metric_name})
                
                self._total_samples += 1
                
                # 计算睡眠时间
                elapsed = time.time() - start_time
                sleep_time = max(0, self._monitor_interval - elapsed)
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
            
            except Exception as e:
                self._handle_error(e, {'operation': '_monitor_loop'})
                time.sleep(self._monitor_interval)
        
        self._log_info("性能监控循环已停止")
    
    def _log_info(self, message: str, **kwargs) -> None:
        """记录信息日志"""
        if self._logger_service:
            self._logger_service.info(message, **kwargs)
    
    def _log_error(self, message: str, **kwargs) -> None:
        """记录错误日志"""
        if self._logger_service:
            self._logger_service.error(message, **kwargs)
    
    def _log_warning(self, message: str, **kwargs) -> None:
        """记录警告日志"""
        if self._logger_service:
            self._logger_service.warning(message, **kwargs)
    
    def _log_debug(self, message: str, **kwargs) -> None:
        """记录调试日志"""
        if self._logger_service:
            self._logger_service.debug(message, **kwargs)
    
    def _handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
        """处理错误"""
        if self._error_handler:
            self._error_handler.handle_error(error, context)
        else:
            self._log_error(f"性能监控错误: {error}")
    
    def start_monitoring(self) -> bool:
        """开始监控"""
        self._ensure_performance_monitor_loaded()
        
        with self._monitor_lock:
            if self._is_monitoring:
                self._log_warning("性能监控已在运行")
                return False
            
            try:
                # 如果有现有的方法，使用它
                if (hasattr(self._performance_monitor_instance, 'start_monitoring') and 
                    self._performance_monitor_instance != self):
                    success = self._performance_monitor_instance.start_monitoring()
                    if not success:
                        return False
                
                self._is_monitoring = True
                self._monitoring_start_time = time.time()
                self._total_samples = 0
                
                # 启动监控线程
                self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
                self._monitor_thread.start()
                
                self._log_info("性能监控已启动")
                return True
            
            except Exception as e:
                self._handle_error(e, {'operation': 'start_monitoring'})
                self._is_monitoring = False
                return False
    
    def stop_monitoring(self) -> bool:
        """停止监控"""
        self._ensure_performance_monitor_loaded()
        
        with self._monitor_lock:
            if not self._is_monitoring:
                self._log_warning("性能监控未在运行")
                return False
            
            try:
                # 如果有现有的方法，使用它
                if (hasattr(self._performance_monitor_instance, 'stop_monitoring') and 
                    self._performance_monitor_instance != self):
                    success = self._performance_monitor_instance.stop_monitoring()
                    if not success:
                        return False
                
                self._is_monitoring = False
                
                # 等待监控线程结束
                if self._monitor_thread and self._monitor_thread.is_alive():
                    self._monitor_thread.join(timeout=5.0)
                
                # 保存数据
                if self._auto_save_enabled:
                    self._save_metrics_data()
                
                self._log_info("性能监控已停止")
                return True
            
            except Exception as e:
                self._handle_error(e, {'operation': 'stop_monitoring'})
                return False
    
    def is_monitoring(self) -> bool:
        """检查是否正在监控"""
        self._ensure_performance_monitor_loaded()
        return self._is_monitoring
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """获取当前指标"""
        self._ensure_performance_monitor_loaded()
        
        try:
            # 如果有现有的方法，使用它
            if (hasattr(self._performance_monitor_instance, 'get_current_metrics') and 
                self._performance_monitor_instance != self):
                metrics = self._performance_monitor_instance.get_current_metrics()
                if metrics:
                    return metrics
            
            # 如果没有在监控，收集一次性指标
            if not self._is_monitoring:
                metrics = {}
                metrics.update(self._collect_system_metrics())
                metrics.update(self._collect_process_metrics())
                metrics['timestamp'] = time.time()
                return metrics
            
            return self._current_metrics.copy()
        
        except Exception as e:
            self._handle_error(e, {'operation': 'get_current_metrics'})
            return {}
    
    def get_metric_history(self, metric_name: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取指标历史"""
        self._ensure_performance_monitor_loaded()
        
        try:
            if metric_name not in self._metrics_history:
                return []
            
            history = list(self._metrics_history[metric_name])
            
            if limit is not None:
                history = history[-limit:]
            
            return history
        
        except Exception as e:
            self._handle_error(e, {'operation': 'get_metric_history', 'metric_name': metric_name})
            return []
    
    def get_all_metrics_history(self, limit: Optional[int] = None) -> Dict[str, List[Dict[str, Any]]]:
        """获取所有指标历史"""
        self._ensure_performance_monitor_loaded()
        
        try:
            result = {}
            
            for metric_name in self._metrics_history:
                result[metric_name] = self.get_metric_history(metric_name, limit)
            
            return result
        
        except Exception as e:
            self._handle_error(e, {'operation': 'get_all_metrics_history'})
            return {}
    
    def add_metric_callback(self, metric_name: str, callback: Callable) -> bool:
        """添加指标回调"""
        self._ensure_performance_monitor_loaded()
        
        try:
            if callback not in self._metric_callbacks[metric_name]:
                self._metric_callbacks[metric_name].append(callback)
                self._log_debug(f"已添加指标回调: {metric_name}")
                return True
            
            return False
        
        except Exception as e:
            self._handle_error(e, {'operation': 'add_metric_callback', 'metric_name': metric_name})
            return False
    
    def remove_metric_callback(self, metric_name: str, callback: Callable) -> bool:
        """移除指标回调"""
        self._ensure_performance_monitor_loaded()
        
        try:
            if callback in self._metric_callbacks[metric_name]:
                self._metric_callbacks[metric_name].remove(callback)
                self._log_debug(f"已移除指标回调: {metric_name}")
                return True
            
            return False
        
        except Exception as e:
            self._handle_error(e, {'operation': 'remove_metric_callback', 'metric_name': metric_name})
            return False
    
    def set_alert_threshold(self, metric_name: str, warning_threshold: Optional[float] = None, 
                          critical_threshold: Optional[float] = None) -> bool:
        """设置告警阈值"""
        self._ensure_performance_monitor_loaded()
        
        try:
            if metric_name not in self._alert_thresholds:
                self._alert_thresholds[metric_name] = {}
            
            if warning_threshold is not None:
                self._alert_thresholds[metric_name]['warning'] = warning_threshold
            
            if critical_threshold is not None:
                self._alert_thresholds[metric_name]['critical'] = critical_threshold
            
            self._log_debug(f"已设置告警阈值: {metric_name} = {self._alert_thresholds[metric_name]}")
            return True
        
        except Exception as e:
            self._handle_error(e, {'operation': 'set_alert_threshold', 'metric_name': metric_name})
            return False
    
    def add_alert_callback(self, callback: Callable) -> bool:
        """添加告警回调"""
        self._ensure_performance_monitor_loaded()
        
        try:
            if callback not in self._alert_callbacks:
                self._alert_callbacks.append(callback)
                self._log_debug("已添加告警回调")
                return True
            
            return False
        
        except Exception as e:
            self._handle_error(e, {'operation': 'add_alert_callback'})
            return False
    
    def remove_alert_callback(self, callback: Callable) -> bool:
        """移除告警回调"""
        self._ensure_performance_monitor_loaded()
        
        try:
            if callback in self._alert_callbacks:
                self._alert_callbacks.remove(callback)
                self._log_debug("已移除告警回调")
                return True
            
            return False
        
        except Exception as e:
            self._handle_error(e, {'operation': 'remove_alert_callback'})
            return False
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        self._ensure_performance_monitor_loaded()
        
        try:
            current_metrics = self.get_current_metrics()
            
            # 计算平均值
            averages = {}
            for metric_name, history in self._metrics_history.items():
                if history:
                    values = [item['value'] for item in history if isinstance(item['value'], (int, float))]
                    if values:
                        averages[f"{metric_name}_avg"] = sum(values) / len(values)
                        averages[f"{metric_name}_min"] = min(values)
                        averages[f"{metric_name}_max"] = max(values)
            
            # 监控统计
            monitoring_duration = 0
            if self._monitoring_start_time:
                monitoring_duration = time.time() - self._monitoring_start_time
            
            return {
                'current_metrics': current_metrics,
                'averages': averages,
                'system_info': self._system_info,
                'monitoring_status': {
                    'is_monitoring': self._is_monitoring,
                    'monitoring_duration': monitoring_duration,
                    'total_samples': self._total_samples,
                    'sample_rate': self._total_samples / monitoring_duration if monitoring_duration > 0 else 0,
                    'alert_count': self._alert_count,
                    'last_alert_time': self._last_alert_time
                },
                'configuration': {
                    'monitor_interval': self._monitor_interval,
                    'history_size': self._history_size,
                    'auto_save_enabled': self._auto_save_enabled,
                    'enable_system_metrics': self._enable_system_metrics,
                    'enable_process_metrics': self._enable_process_metrics,
                    'enable_custom_metrics': self._enable_custom_metrics
                },
                'alert_thresholds': self._alert_thresholds
            }
        
        except Exception as e:
            self._handle_error(e, {'operation': 'get_performance_summary'})
            return {}
    
    def clear_metrics_history(self) -> bool:
        """清除指标历史"""
        self._ensure_performance_monitor_loaded()
        
        try:
            self._metrics_history.clear()
            self._total_samples = 0
            self._alert_count = 0
            self._last_alert_time = None
            
            self._log_info("指标历史已清除")
            return True
        
        except Exception as e:
            self._handle_error(e, {'operation': 'clear_metrics_history'})
            return False
    
    def _save_metrics_data(self) -> bool:
        """保存指标数据"""
        if not self._auto_save_enabled or not self._save_file_path:
            return False
        
        try:
            # 准备保存数据
            save_data = {
                'system_info': self._system_info,
                'current_metrics': self._current_metrics,
                'alert_thresholds': self._alert_thresholds,
                'monitoring_stats': {
                    'total_samples': self._total_samples,
                    'alert_count': self._alert_count,
                    'last_alert_time': self._last_alert_time,
                    'monitoring_start_time': self._monitoring_start_time
                },
                'configuration': {
                    'monitor_interval': self._monitor_interval,
                    'history_size': self._history_size,
                    'enable_system_metrics': self._enable_system_metrics,
                    'enable_process_metrics': self._enable_process_metrics,
                    'enable_custom_metrics': self._enable_custom_metrics
                },
                'metrics_history': {name: list(history)[-100:] for name, history in self._metrics_history.items()},  # 只保存最近100条
                'saved_at': time.time(),
                'version': '1.0'
            }
            
            with open(self._save_file_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            self._log_debug(f"性能监控数据已保存: {self._save_file_path}")
            return True
        
        except Exception as e:
            self._handle_error(e, {'operation': '_save_metrics_data', 'file_path': self._save_file_path})
            return False
    
    def export_metrics(self, file_path: str, start_time: Optional[float] = None, 
                      end_time: Optional[float] = None) -> bool:
        """导出指标数据"""
        self._ensure_performance_monitor_loaded()
        
        try:
            # 过滤时间范围
            filtered_history = {}
            
            for metric_name, history in self._metrics_history.items():
                filtered_data = []
                
                for item in history:
                    timestamp = item.get('timestamp', 0)
                    
                    if start_time is not None and timestamp < start_time:
                        continue
                    
                    if end_time is not None and timestamp > end_time:
                        continue
                    
                    filtered_data.append(item)
                
                if filtered_data:
                    filtered_history[metric_name] = filtered_data
            
            # 准备导出数据
            export_data = {
                'export_info': {
                    'start_time': start_time,
                    'end_time': end_time,
                    'exported_at': time.time(),
                    'total_metrics': len(filtered_history),
                    'total_samples': sum(len(history) for history in filtered_history.values())
                },
                'system_info': self._system_info,
                'metrics_history': filtered_history,
                'alert_thresholds': self._alert_thresholds,
                'performance_summary': self.get_performance_summary(),
                'version': '1.0'
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            self._log_info(f"性能指标已导出到文件: {file_path}")
            return True
        
        except Exception as e:
            self._handle_error(e, {'operation': 'export_metrics', 'file_path': file_path})
            return False