#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏分析器适配器
这个文件现在作为统一GameAnalyzer的适配器，保持向后兼容性
"""

import warnings
from typing import Optional, Dict, List, Any, Tuple
import numpy as np

from .logger import GameLogger
from .image_processor import ImageProcessor
from .config import Config

# 导入统一的GameAnalyzer
try:
    from ..core.unified_game_analyzer import UnifiedGameAnalyzer
except ImportError:
    # 如果导入失败，尝试其他路径
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src.core.unified_game_analyzer import UnifiedGameAnalyzer


class GameAnalyzer:
    """
    游戏分析器适配器
    
    这个类现在是UnifiedGameAnalyzer的适配器，保持旧API的兼容性
    同时提供新的统一功能
    """
    
    def __init__(self, logger: GameLogger, image_processor: ImageProcessor, config: Config):
        """
        初始化游戏分析器适配器
        
        Args:
            logger: 日志服务
            image_processor: 图像处理服务
            config: 配置服务
        """
        self.logger = logger
        self.image_processor = image_processor
        self.config = config
        
        # 创建统一的GameAnalyzer实例
        self._unified_analyzer = UnifiedGameAnalyzer(
            logger=logger,
            image_processor=image_processor,
            config=config,
            game_name=config.get_game_name()
        )
        
        # 发出弃用警告
        warnings.warn(
            "直接使用services.game_analyzer已弃用，建议使用core.unified_game_analyzer.UnifiedGameAnalyzer",
            DeprecationWarning,
            stacklevel=2
        )
        
        self.logger.info("GameAnalyzer适配器初始化完成，使用统一分析器")
    
    def analyze_frame(self, frame: Optional[np.ndarray]) -> Dict[str, Any]:
        """
        分析游戏画面帧 - 兼容方法
        
        Args:
            frame: 游戏画面帧数据
            
        Returns:
            Dict[str, Any]: 游戏状态分析结果
        """
        return self._unified_analyzer.analyze_frame(frame)
    
    def extract_features(self, frame: np.ndarray) -> np.ndarray:
        """
        提取图像特征 - 兼容方法
        
        Args:
            frame: 输入图像
            
        Returns:
            np.ndarray: 特征向量
        """
        return self._unified_analyzer.extract_features(frame)
    
    def analyze_screenshot(self, screenshot: np.ndarray) -> Dict:
        """
        分析游戏截图 - 兼容方法
        
        Args:
            screenshot: 游戏截图
            
        Returns:
            Dict: 分析结果
        """
        return self._unified_analyzer.analyze_screenshot(screenshot)
    
    # ============= 直接委托方法 =============
    
    def collect_ui_samples(self, screenshot: np.ndarray, roi: Tuple[int, int, int, int], 
                          name: str, num_samples: int = 10) -> None:
        """收集UI元素样本"""
        return self._unified_analyzer.collect_ui_samples(screenshot, roi, name, num_samples)
    
    def learn_ui_element(self, name: str, threshold: float = 0.8):
        """学习UI元素特征"""
        return self._unified_analyzer.learn_ui_element(name, threshold)
    
    def save_data(self) -> None:
        """保存分析数据"""
        return self._unified_analyzer.save_data()
    
    def load_custom_classifier(self, model_path: str, class_names: List[str]) -> bool:
        """
        加载自定义分类器 - 兼容方法
        
        Args:
            model_path: 模型文件路径
            class_names: 类别名称列表
            
        Returns:
            bool: 是否加载成功
        """
        # 这个方法在统一分析器中暂未实现，返回False
        self.logger.warning("load_custom_classifier方法在统一分析器中暂未实现")
        return False
    
    # ============= 兼容性属性 =============
    
    @property
    def model(self):
        """获取深度学习模型 - 兼容属性"""
        return getattr(self._unified_analyzer, 'model', None)
    
    @property
    def transform(self):
        """获取图像预处理变换 - 兼容属性"""
        return getattr(self._unified_analyzer, 'transform', None)
    
    @property
    def ui_elements(self):
        """获取UI元素字典 - 兼容属性"""
        return getattr(self._unified_analyzer, 'ui_elements', {})
    
    @property
    def scenes(self):
        """获取场景字典 - 兼容属性"""
        return getattr(self._unified_analyzer, 'scenes', {})
    
    # ============= 新功能访问方法 =============
    
    def get_unified_analyzer(self) -> UnifiedGameAnalyzer:
        """
        获取底层的统一分析器实例
        
        Returns:
            UnifiedGameAnalyzer: 统一分析器实例
        """
        return self._unified_analyzer
    
    def detect_objects(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        检测对象 - 新功能
        
        Args:
            frame: 游戏画面
            
        Returns:
            List[Dict[str, Any]]: 检测到的对象列表
        """
        # 这个方法调用统一分析器的综合检测功能
        result = self._unified_analyzer.analyze_frame(frame)
        objects = []
        
        # 合并所有检测到的对象
        objects.extend(result.get('buttons', []))
        objects.extend(result.get('enemies', []))
        objects.extend(result.get('items', []))
        
        return objects
    
    def analyze_game_state(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        分析游戏状态 - 新功能
        
        Args:
            frame: 游戏画面
            
        Returns:
            Dict[str, Any]: 游戏状态信息
        """
        return self._unified_analyzer.analyze_frame(frame)


# 保持向后兼容的别名
OriginalGameAnalyzer = GameAnalyzer 