"""
适配器接口定义

遵循Clean Architecture原则的外部系统接口
业务逻辑层不直接依赖于外部系统实现
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple, Union
import numpy as np
from dataclasses import dataclass


@dataclass
class WindowInfo:
    """窗口信息数据类"""
    title: str
    handle: int
    pid: int
    rect: Tuple[int, int, int, int]  # (x, y, width, height)
    is_visible: bool
    is_active: bool


@dataclass
class InputAction:
    """输入操作数据类"""
    action_type: str  # 'click', 'key', 'scroll', 'drag'
    x: Optional[int] = None
    y: Optional[int] = None
    key: Optional[str] = None
    button: Optional[str] = None  # 'left', 'right', 'middle'
    duration: Optional[float] = None
    delay: Optional[float] = None


class IWindowAdapter(ABC):
    """窗口适配器接口"""
    
    @abstractmethod
    def find_window(self, title: str, class_name: Optional[str] = None) -> Optional[WindowInfo]:
        """查找窗口"""
        pass
    
    @abstractmethod
    def get_window_list(self) -> List[WindowInfo]:
        """获取窗口列表"""
        pass
    
    @abstractmethod
    def capture_window(self, window_info: WindowInfo) -> Optional[np.ndarray]:
        """捕获窗口截图"""
        pass
    
    @abstractmethod
    def activate_window(self, window_info: WindowInfo) -> bool:
        """激活窗口"""
        pass
    
    @abstractmethod
    def resize_window(self, window_info: WindowInfo, width: int, height: int) -> bool:
        """调整窗口大小"""
        pass
    
    @abstractmethod
    def move_window(self, window_info: WindowInfo, x: int, y: int) -> bool:
        """移动窗口"""
        pass
    
    @abstractmethod
    def close_window(self, window_info: WindowInfo) -> bool:
        """关闭窗口"""
        pass
    
    @abstractmethod
    def get_window_rect(self, window_info: WindowInfo) -> Tuple[int, int, int, int]:
        """获取窗口位置和大小"""
        pass
    
    @abstractmethod
    def is_window_visible(self, window_info: WindowInfo) -> bool:
        """检查窗口是否可见"""
        pass


class IInputAdapter(ABC):
    """输入适配器接口"""
    
    @abstractmethod
    def click(self, x: int, y: int, button: str = 'left', duration: float = 0.1) -> bool:
        """点击操作"""
        pass
    
    @abstractmethod
    def double_click(self, x: int, y: int, button: str = 'left') -> bool:
        """双击操作"""
        pass
    
    @abstractmethod
    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 1.0) -> bool:
        """拖拽操作"""
        pass
    
    @abstractmethod
    def scroll(self, x: int, y: int, direction: str, amount: int = 1) -> bool:
        """滚动操作"""
        pass
    
    @abstractmethod
    def press_key(self, key: str, duration: float = 0.1) -> bool:
        """按键操作"""
        pass
    
    @abstractmethod
    def press_key_combination(self, keys: List[str]) -> bool:
        """组合键操作"""
        pass
    
    @abstractmethod
    def type_text(self, text: str, delay: float = 0.05) -> bool:
        """输入文本"""
        pass
    
    @abstractmethod
    def execute_action(self, action: InputAction) -> bool:
        """执行输入操作"""
        pass
    
    @abstractmethod
    def get_mouse_position(self) -> Tuple[int, int]:
        """获取鼠标位置"""
        pass
    
    @abstractmethod
    def set_mouse_position(self, x: int, y: int) -> bool:
        """设置鼠标位置"""
        pass


class IImageAdapter(ABC):
    """图像适配器接口"""
    
    @abstractmethod
    def load_image(self, path: str) -> Optional[np.ndarray]:
        """加载图像"""
        pass
    
    @abstractmethod
    def save_image(self, image: np.ndarray, path: str) -> bool:
        """保存图像"""
        pass
    
    @abstractmethod
    def resize_image(self, image: np.ndarray, width: int, height: int) -> np.ndarray:
        """调整图像大小"""
        pass
    
    @abstractmethod
    def crop_image(self, image: np.ndarray, x: int, y: int, width: int, height: int) -> np.ndarray:
        """裁剪图像"""
        pass
    
    @abstractmethod
    def convert_color_space(self, image: np.ndarray, from_space: str, to_space: str) -> np.ndarray:
        """转换颜色空间"""
        pass
    
    @abstractmethod
    def apply_filter(self, image: np.ndarray, filter_type: str, **kwargs) -> np.ndarray:
        """应用滤镜"""
        pass
    
    @abstractmethod
    def template_match(self, image: np.ndarray, template: np.ndarray, threshold: float = 0.8) -> List[Tuple[int, int, float]]:
        """模板匹配"""
        pass
    
    @abstractmethod
    def find_contours(self, image: np.ndarray) -> List[np.ndarray]:
        """查找轮廓"""
        pass
    
    @abstractmethod
    def extract_text(self, image: np.ndarray) -> str:
        """提取文本（OCR）"""
        pass


class IFileSystemAdapter(ABC):
    """文件系统适配器接口"""
    
    @abstractmethod
    def read_file(self, path: str) -> Optional[str]:
        """读取文件"""
        pass
    
    @abstractmethod
    def write_file(self, path: str, content: str) -> bool:
        """写入文件"""
        pass
    
    @abstractmethod
    def read_binary_file(self, path: str) -> Optional[bytes]:
        """读取二进制文件"""
        pass
    
    @abstractmethod
    def write_binary_file(self, path: str, content: bytes) -> bool:
        """写入二进制文件"""
        pass
    
    @abstractmethod
    def file_exists(self, path: str) -> bool:
        """检查文件是否存在"""
        pass
    
    @abstractmethod
    def create_directory(self, path: str) -> bool:
        """创建目录"""
        pass
    
    @abstractmethod
    def delete_file(self, path: str) -> bool:
        """删除文件"""
        pass
    
    @abstractmethod
    def delete_directory(self, path: str) -> bool:
        """删除目录"""
        pass
    
    @abstractmethod
    def list_files(self, path: str, pattern: Optional[str] = None) -> List[str]:
        """列出文件"""
        pass
    
    @abstractmethod
    def get_file_info(self, path: str) -> Optional[Dict[str, Any]]:
        """获取文件信息"""
        pass


class INetworkAdapter(ABC):
    """网络适配器接口"""
    
    @abstractmethod
    def http_get(self, url: str, headers: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        """HTTP GET请求"""
        pass
    
    @abstractmethod
    def http_post(self, url: str, data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        """HTTP POST请求"""
        pass
    
    @abstractmethod
    def download_file(self, url: str, save_path: str) -> bool:
        """下载文件"""
        pass
    
    @abstractmethod
    def upload_file(self, url: str, file_path: str) -> bool:
        """上传文件"""
        pass
    
    @abstractmethod
    def check_connectivity(self, host: str = "8.8.8.8", port: int = 53, timeout: float = 3.0) -> bool:
        """检查网络连接"""
        pass 