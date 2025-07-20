"""
仓储接口定义

遵循Clean Architecture原则的数据访问层接口
业务逻辑层不直接依赖于数据存储实现
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import numpy as np


class IConfigRepository(ABC):
    """配置仓储接口"""
    
    @abstractmethod
    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        pass
    
    @abstractmethod
    def set_config(self, key: str, value: Any) -> bool:
        """设置配置值"""
        pass
    
    @abstractmethod
    def get_all_configs(self) -> Dict[str, Any]:
        """获取所有配置"""
        pass
    
    @abstractmethod
    def save_configs(self) -> bool:
        """保存配置到持久化存储"""
        pass
    
    @abstractmethod
    def load_configs(self) -> bool:
        """从持久化存储加载配置"""
        pass
    
    @abstractmethod
    def reset_to_defaults(self) -> bool:
        """重置为默认配置"""
        pass
    
    @abstractmethod
    def backup_configs(self, backup_path: Union[str, Path]) -> bool:
        """备份配置"""
        pass
    
    @abstractmethod
    def restore_configs(self, backup_path: Union[str, Path]) -> bool:
        """恢复配置"""
        pass


class ITemplateRepository(ABC):
    """模板仓储接口"""
    
    @abstractmethod
    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """获取模板"""
        pass
    
    @abstractmethod
    def save_template(self, template_id: str, template_data: Dict[str, Any]) -> bool:
        """保存模板"""
        pass
    
    @abstractmethod
    def delete_template(self, template_id: str) -> bool:
        """删除模板"""
        pass
    
    @abstractmethod
    def list_templates(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出模板"""
        pass
    
    @abstractmethod
    def get_template_image(self, template_id: str) -> Optional[np.ndarray]:
        """获取模板图像"""
        pass
    
    @abstractmethod
    def save_template_image(self, template_id: str, image: np.ndarray) -> bool:
        """保存模板图像"""
        pass
    
    @abstractmethod
    def search_templates(self, query: str) -> List[Dict[str, Any]]:
        """搜索模板"""
        pass
    
    @abstractmethod
    def get_template_categories(self) -> List[str]:
        """获取模板分类"""
        pass


class IStateRepository(ABC):
    """状态仓储接口"""
    
    @abstractmethod
    def save_state(self, state_id: str, state_data: Dict[str, Any]) -> bool:
        """保存状态"""
        pass
    
    @abstractmethod
    def load_state(self, state_id: str) -> Optional[Dict[str, Any]]:
        """加载状态"""
        pass
    
    @abstractmethod
    def delete_state(self, state_id: str) -> bool:
        """删除状态"""
        pass
    
    @abstractmethod
    def list_states(self, limit: int = 100) -> List[Dict[str, Any]]:
        """列出状态"""
        pass
    
    @abstractmethod
    def get_state_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取状态历史"""
        pass
    
    @abstractmethod
    def clear_state_history(self) -> bool:
        """清空状态历史"""
        pass
    
    @abstractmethod
    def compress_old_states(self, days_old: int = 30) -> bool:
        """压缩旧状态"""
        pass


class ILogRepository(ABC):
    """日志仓储接口"""
    
    @abstractmethod
    def save_log(self, log_entry: Dict[str, Any]) -> bool:
        """保存日志条目"""
        pass
    
    @abstractmethod
    def get_logs(self, 
                 level: Optional[str] = None, 
                 limit: int = 100,
                 start_time: Optional[float] = None,
                 end_time: Optional[float] = None) -> List[Dict[str, Any]]:
        """获取日志"""
        pass
    
    @abstractmethod
    def clear_logs(self, before_time: Optional[float] = None) -> bool:
        """清空日志"""
        pass
    
    @abstractmethod
    def search_logs(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """搜索日志"""
        pass
    
    @abstractmethod
    def get_log_statistics(self) -> Dict[str, Any]:
        """获取日志统计信息"""
        pass


class IPerformanceRepository(ABC):
    """性能数据仓储接口"""
    
    @abstractmethod
    def save_performance_data(self, data: Dict[str, Any]) -> bool:
        """保存性能数据"""
        pass
    
    @abstractmethod
    def get_performance_data(self, 
                           metric_name: Optional[str] = None,
                           start_time: Optional[float] = None,
                           end_time: Optional[float] = None,
                           limit: int = 1000) -> List[Dict[str, Any]]:
        """获取性能数据"""
        pass
    
    @abstractmethod
    def get_performance_summary(self, 
                              time_range: str = "24h") -> Dict[str, Any]:
        """获取性能汇总"""
        pass
    
    @abstractmethod
    def clear_performance_data(self, before_time: Optional[float] = None) -> bool:
        """清空性能数据"""
        pass
    
    @abstractmethod
    def get_performance_alerts(self) -> List[Dict[str, Any]]:
        """获取性能告警"""
        pass 