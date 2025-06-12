from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any
import os
import torch

@dataclass
class WindowConfig:
    """窗口管理配置"""
    # 窗口查找参数
    window_class: str = ""  # 推荐设为目标窗口类名，如无则保持空字符串
    window_title: str = ""  # 推荐设为目标窗口标题，如无则保持空字符串
    # 截图参数
    screenshot_interval: float = 0.1  # 截图间隔（秒）
    # 窗口激活参数
    activation_delay: float = 0.5  # 激活窗口后的延迟（秒）
    # 窗口刷新参数
    refresh_interval: int = 1000  # 窗口列表刷新间隔（毫秒）
    last_selected: str = ""

@dataclass
class YOLOConfig:
    """YOLOv5配置"""
    # 模型参数
    model_path: str = 'yolov5n.pt'  # 模型路径
    confidence_threshold: float = 0.5  # 置信度阈值
    iou_threshold: float = 0.45  # IOU阈值
    # 训练参数
    train_epochs: int = 100  # 训练轮数
    train_batch_size: int = 16  # 训练批次大小
    train_img_size: int = 640  # 训练图像大小

@dataclass
class ImageProcessorConfig:
    """图像处理配置"""
    # 模板匹配参数
    template_match_threshold: float = 0.8  # 模板匹配阈值
    # 颜色检测参数
    color_detection_threshold: float = 0.7  # 颜色检测阈值
    # 状态向量参数
    max_elements_per_class: int = 10  # 每类最大元素数量

@dataclass
class ActionConfig:
    """动作模拟配置"""
    # 鼠标参数
    mouse_speed: float = 0.5  # 鼠标移动速度（0-1）
    mouse_offset: int = 5  # 鼠标随机偏移量（像素）
    click_delay: float = 0.1  # 点击延迟（秒）
    # 键盘参数
    key_press_delay: float = 0.1  # 按键延迟（秒）
    # 随机延迟参数
    min_random_delay: float = 0.1  # 最小随机延迟（秒）
    max_random_delay: float = 0.5  # 最大随机延迟（秒）

@dataclass
class DQNConfig:
    """DQN配置"""
    # 网络参数
    state_size: int = 100  # 状态空间维度
    action_size: int = 10  # 动作空间维度
    hidden_size: int = 128  # 隐藏层大小
    device: str = 'cuda' if torch.cuda.is_available() else 'cpu'  # 设备
    # 训练参数
    memory_size: int = 10000  # 经验回放缓冲区大小
    batch_size: int = 32  # 训练批次大小
    gamma: float = 0.95  # 折扣因子
    initial_epsilon: float = 1.0  # 初始探索率
    min_epsilon: float = 0.01  # 最小探索率
    epsilon_decay: float = 0.995  # 探索率衰减率
    learning_rate: float = 0.001  # 学习率
    target_update: int = 100  # 目标网络更新频率

@dataclass
class TemplateCollectorConfig:
    """模板收集配置"""
    # 收集参数
    collection_duration: int = 300  # 收集持续时间（秒）
    collection_interval: float = 0.5  # 收集间隔（秒）
    min_template_size: int = 20  # 最小模板大小（像素）
    max_template_size: int = 200  # 最大模板大小（像素）
    # 保存参数
    template_dir: str = 'templates'  # 模板保存目录
    image_similarity_threshold: float = 0.9  # 图像相似度阈值

@dataclass
class UIConfig:
    """UI配置"""
    # 窗口参数
    window_title: str = '游戏自动化工具'
    window_width: int = 1200
    window_height: int = 800
    # 显示参数
    display_fps: int = 30  # 显示帧率
    # 主题参数
    theme: str = 'light'  # 主题（light/dark）

@dataclass
class TemplateConfig:
    """模板配置"""
    # 保存参数
    output_dir: str = 'templates'  # 模板保存目录
    image_similarity_threshold: float = 0.9  # 图像相似度阈值
    # 收集参数
    duration: int = 300  # 收集持续时间（秒）
    interval: float = 0.5  # 收集间隔（秒）
    collection_interval: float = 0.5  # 收集间隔（秒）
    min_template_size: int = 20  # 最小模板大小（像素）
    max_template_size: int = 200  # 最大模板大小（像素）
    last_dir: str = "templates"

@dataclass
class LoggingConfig:
    """日志配置"""
    log_dir: str = 'logs'  # 日志目录
    log_level: str = 'INFO'  # 日志级别
    max_file_size: int = 10 * 1024 * 1024  # 最大文件大小（10MB）
    backup_count: int = 5  # 备份文件数量
    log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'  # 日志格式
    date_format: str = '%Y-%m-%d %H:%M:%S'  # 日期格式
    enable_console: bool = True  # 是否启用控制台输出
    enable_file: bool = True  # 是否启用文件输出
    max_recursion_depth: int = 10  # 最大递归深度
    log_rotation: str = 'size'  # 日志轮转方式（D: 每天, H: 每小时, M: 每分钟）
    log_retention_days: int = 30  # 日志保留天数

@dataclass
class FrameConfig:
    """画面配置"""
    # 更新参数
    update_interval: int = 33  # 画面更新间隔（毫秒）
    # 显示参数
    display_width: int = 640  # 显示宽度
    display_height: int = 480  # 显示高度
    # 缩放参数
    scale_factor: float = 1.0  # 缩放因子

@dataclass
class GameStateConfig:
    """游戏状态配置"""
    # 分析参数
    analysis_interval: int = 1000  # 状态分析间隔（毫秒）
    # 历史记录参数
    max_history_size: int = 1000  # 最大历史记录数量
    # 状态缓存参数
    cache_duration: int = 5000  # 状态缓存持续时间（毫秒）
    last_state: Dict[str, Any] = None

@dataclass
class Config:
    """总配置"""
    window: WindowConfig = field(default_factory=WindowConfig)
    yolo: YOLOConfig = field(default_factory=YOLOConfig)
    image_processor: ImageProcessorConfig = field(default_factory=ImageProcessorConfig)
    action: ActionConfig = field(default_factory=ActionConfig)
    dqn: DQNConfig = field(default_factory=DQNConfig)
    template_collector: TemplateCollectorConfig = field(default_factory=TemplateCollectorConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    template: TemplateConfig = field(default_factory=TemplateConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    frame: FrameConfig = field(default_factory=FrameConfig)
    game_state: GameStateConfig = field(default_factory=GameStateConfig)

    def __post_init__(self):
        """初始化后处理"""
        # 确保必要的目录存在
        directories = [
            self.template.output_dir,  # 模板目录
            self.logging.log_dir,      # 日志目录
            os.path.dirname(self.yolo.model_path),  # YOLO模型目录
            'models',                  # 模型保存目录
            'data',                    # 数据目录
            'screenshots'              # 截图目录
        ]
        
        for directory in directories:
            if directory:  # 确保目录路径不为空
                os.makedirs(directory, exist_ok=True)
                print(f"确保目录存在: {directory}")

# 导出Config类
__all__ = ['Config']

# 创建全局配置实例
config = Config() 