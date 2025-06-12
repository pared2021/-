import cv2
import numpy as np
import os
import time
import hashlib
from typing import Dict, List, Tuple, Optional
from ultralytics import YOLO
from .config import Config
from .logger import GameLogger
from .window_manager import GameWindowManager

class TemplateCollector:
    """模板收集器，负责收集和分析游戏元素模板"""
    
    def __init__(self, logger: GameLogger, window_manager: GameWindowManager, config: Config, output_dir: str = None):
        """
        初始化模板收集器
        
        Args:
            logger: 日志对象
            window_manager: 窗口管理器
            config: 配置对象
            output_dir: 模板输出目录
        """
        self.logger = logger
        self.window_manager = window_manager
        self.config = config
        self.output_dir = output_dir or config.template.output_dir
        self.templates = {}  # 存储已收集的模板
        self.template_hashes = set()  # 存储模板哈希值
        self.is_collecting = False
        self.model = None
        self.class_names = {}  # 存储类别名称映射
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 加载已有模板
        self.logger.info(f"开始加载模板: {self.output_dir}")
        self._load_existing_templates()
        self.logger.info(f"模板加载完成，共{len(self.templates)}个")
        
        # 初始化YOLOv5模型
        try:
            self.logger.info(f"初始化YOLOv5模型: {config.yolo.model_path}")
            self.model = YOLO(config.yolo.model_path)
            # 获取类别名称
            self.class_names = self.model.names
            self.logger.info(f"模型类别: {self.class_names}")
        except Exception as e:
            self.logger.error(f"加载YOLOv5模型失败: {e}")
            self.logger.warning("将以基本模式运行，不使用YOLOv5功能")
    
    def _load_existing_templates(self):
        """加载已有的模板文件"""
        for filename in os.listdir(self.output_dir):
            if filename.endswith(('.png', '.jpg', '.jpeg')):
                path = os.path.join(self.output_dir, filename)
                template = cv2.imread(path)
                if template is not None:
                    # 从文件名中提取类别名称
                    class_name = filename.split('_')[0]
                    # 计算模板哈希值
                    template_hash = self._calculate_image_hash(template)
                    # 存储模板
                    self.templates[filename] = {
                        'image': template,
                        'class': class_name,
                        'hash': template_hash
                    }
                    self.template_hashes.add(template_hash)
                    self.logger.debug(f"已加载模板: {filename}")
                else:
                    self.logger.warning(f"无法加载模板: {filename}")
    
    def collect_templates(self, duration: int = None, interval: float = None):
        """
        收集游戏元素模板
        
        Args:
            duration: 收集持续时间（秒）
            interval: 收集间隔（秒）
        """
        duration = duration or self.config.template.collect_duration
        interval = interval or self.config.template.collect_interval
        
        self.logger.info(f"开始收集模板，持续时间: {duration}秒，间隔: {interval}秒")
        
        start_time = time.time()
        while time.time() - start_time < duration:
            # 确保窗口激活
            if not self.window_manager.is_window_active():
                self.logger.warning("游戏窗口未激活，跳过当前帧")
                time.sleep(interval)
                continue
            
            # 获取游戏画面
            screenshot = self.window_manager.capture_window()
            if screenshot is None:
                self.logger.error("无法获取游戏画面")
                time.sleep(interval)
                continue
            
            # 分析画面中的元素
            self._analyze_frame(screenshot)
            
            # 等待下一次收集
            time.sleep(interval)
        
        self.logger.info("模板收集完成")
    
    def _analyze_frame(self, frame: np.ndarray):
        """
        分析画面中的元素
        
        Args:
            frame: 游戏画面
        """
        # 使用YOLOv5检测元素
        results = self.model(frame, conf=self.config.yolo.confidence_threshold)
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # 获取边界框坐标
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                # 获取类别
                cls = int(box.cls[0])
                class_name = self.class_names[cls]
                
                # 提取元素图像
                element = frame[y1:y2, x1:x2]
                
                # 计算图像哈希
                element_hash = self._calculate_image_hash(element)
                
                # 检查是否为新元素
                if element_hash not in self.template_hashes:
                    # 保存新模板
                    template_path = os.path.join(
                        self.output_dir, 
                        f"{class_name}_{len(self.template_hashes)}.png"
                    )
                    cv2.imwrite(template_path, element)
                    self.template_hashes.add(element_hash)
                    
                    self.logger.info(f"发现新模板: {template_path}")
    
    def _calculate_image_hash(self, image: np.ndarray) -> str:
        """
        计算图像哈希值
        
        Args:
            image: 输入图像
            
        Returns:
            str: 图像哈希值
        """
        # 调整图像大小
        resized = cv2.resize(image, (8, 8))
        
        # 转换为灰度图
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        
        # 计算平均值
        avg = gray.mean()
        
        # 生成哈希值
        hash_str = ''.join(['1' if pixel > avg else '0' for pixel in gray.flatten()])
        return hash_str
    
    def analyze_existing_templates(self):
        """分析已收集的模板"""
        self.logger.info("开始分析现有模板")
        
        template_stats = {}
        for filename in os.listdir(self.output_dir):
            if filename.endswith(('.png', '.jpg', '.jpeg')):
                path = os.path.join(self.output_dir, filename)
                template = cv2.imread(path)
                if template is not None:
                    # 获取模板信息
                    height, width = template.shape[:2]
                    class_name = filename.split('_')[0]
                    
                    # 更新统计信息
                    if class_name not in template_stats:
                        template_stats[class_name] = {
                            'count': 0,
                            'sizes': []
                        }
                    
                    template_stats[class_name]['count'] += 1
                    template_stats[class_name]['sizes'].append((width, height))
        
        # 输出分析结果
        for class_name, stats in template_stats.items():
            sizes = stats['sizes']
            avg_width = sum(w for w, _ in sizes) / len(sizes)
            avg_height = sum(h for _, h in sizes) / len(sizes)
            
            self.logger.info(
                f"类别: {class_name}, "
                f"数量: {stats['count']}, "
                f"平均尺寸: {avg_width:.1f}x{avg_height:.1f}"
            )
        
        self.logger.info("模板分析完成")
    
    def train_custom_model(self, data_yaml: str, epochs: int = None):
        """
        训练自定义YOLOv5模型
        
        Args:
            data_yaml: 数据集配置文件路径
            epochs: 训练轮数
        """
        epochs = epochs or self.config.yolo.train_epochs
        
        self.logger.info(f"开始训练自定义模型，配置文件: {data_yaml}, 轮数: {epochs}")
        
        try:
            # 训练模型
            self.model.train(
                data=data_yaml,
                epochs=epochs,
                imgsz=self.config.yolo.train_image_size,
                batch=self.config.yolo.train_batch_size,
                device=self.config.yolo.train_device
            )
            
            self.logger.info("模型训练完成")
        except Exception as e:
            self.logger.error(f"模型训练失败: {str(e)}")
            raise 