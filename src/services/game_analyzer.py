import cv2
import numpy as np
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import os
import json
from typing import Optional, Dict, List, Any, Tuple
from .logger import GameLogger
from .image_processor import ImageProcessor
from .config import Config
from src.common.error_types import ErrorCode, ModelError, ErrorContext

class GameAnalyzer:
    """游戏分析器，使用深度学习模型识别游戏元素"""
    
    def __init__(self, logger: GameLogger, image_processor: ImageProcessor, config: Config, error_handler):
        """
        初始化游戏分析器
        
        Args:
            logger: 日志服务
            image_processor: 图像处理服务
            config: 配置
            error_handler: 错误处理服务
        """
        self.logger = logger
        self.image_processor = image_processor
        self.config = config
        self.error_handler = error_handler
        self.model = None
        self.is_initialized = False
        self.model_path = "models/game_model.pth"
        self.model_config = "models/model_config.json"
        
        # 图像预处理
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                              std=[0.229, 0.224, 0.225])
        ])
        
        # 加载自定义分类器
        self.custom_classifier = None
        self.class_names = []
        
    def initialize(self) -> bool:
        """初始化游戏分析器"""
        try:
            # 加载模型配置
            if os.path.exists(self.model_config):
                try:
                    with open(self.model_config, 'r', encoding='utf-8') as f:
                        self.model_config = json.load(f)
                except Exception as e:
                    self.error_handler.handle_error(
                        ModelError(
                            ErrorCode.MODEL_CONFIG_LOAD_FAILED,
                            "加载模型配置失败",
                            ErrorContext(
                                source="GameAnalyzer.initialize",
                                details=str(e)
                            )
                        )
                    )
            
            self.is_initialized = True
            return True
            
        except Exception as e:
            self.error_handler.handle_error(
                ModelError(
                    ErrorCode.MODEL_INIT_FAILED,
                    "游戏分析器初始化失败",
                    ErrorContext(
                        source="GameAnalyzer.initialize",
                        details=str(e)
                    )
                )
            )
            return False
            
    def load_model(self) -> bool:
        """加载模型"""
        try:
            if not self.is_initialized:
                self.error_handler.handle_error(
                    ModelError(
                        ErrorCode.MODEL_NOT_INITIALIZED,
                        "游戏分析器未初始化",
                        ErrorContext(
                            source="GameAnalyzer.load_model",
                            details="is_initialized is False"
                        )
                    )
                )
                return False
                
            if not os.path.exists(self.model_path):
                self.error_handler.handle_error(
                    ModelError(
                        ErrorCode.MODEL_FILE_NOT_FOUND,
                        f"模型文件不存在: {self.model_path}",
                        ErrorContext(
                            source="GameAnalyzer.load_model",
                            details=f"模型路径: {self.model_path}"
                        )
                    )
                )
                return False
                
            # 创建模型
            self.model = self._create_model()
            
            # 加载模型权重
            self.model.load_state_dict(torch.load(self.model_path))
            self.model.eval()
            
            return True
            
        except Exception as e:
            self.error_handler.handle_error(
                ModelError(
                    ErrorCode.MODEL_LOAD_FAILED,
                    "模型加载失败",
                    ErrorContext(
                        source="GameAnalyzer.load_model",
                        details=str(e)
                    )
                )
            )
            return False
            
    def reload_model(self) -> bool:
        """重新加载模型"""
        try:
            self.model = None
            return self.load_model()
        except Exception as e:
            self.error_handler.handle_error(
                ModelError(
                    ErrorCode.MODEL_RELOAD_FAILED,
                    "模型重新加载失败",
                    ErrorContext(
                        source="GameAnalyzer.reload_model",
                        details=str(e)
                    )
                )
            )
            return False
            
    def analyze_frame(self, frame: np.ndarray) -> Optional[Dict[str, Any]]:
        """分析游戏画面"""
        try:
            if not self.is_initialized:
                self.error_handler.handle_error(
                    ModelError(
                        ErrorCode.MODEL_NOT_INITIALIZED,
                        "游戏分析器未初始化",
                        ErrorContext(
                            source="GameAnalyzer.analyze_frame",
                            details="is_initialized is False"
                        )
                    )
                )
                return None
                
            if self.model is None:
                self.error_handler.handle_error(
                    ModelError(
                        ErrorCode.MODEL_NOT_LOADED,
                        "模型未加载",
                        ErrorContext(
                            source="GameAnalyzer.analyze_frame",
                            details="model is None"
                        )
                    )
                )
                return None
                
            # 预处理图像
            processed_frame = self._preprocess_frame(frame)
            if processed_frame is None:
                return None
                
            # 模型推理
            with torch.no_grad():
                output = self.model(processed_frame)
                
            # 后处理结果
            result = self._postprocess_output(output)
            
            return result
            
        except Exception as e:
            self.error_handler.handle_error(
                ModelError(
                    ErrorCode.MODEL_INFERENCE_FAILED,
                    "模型推理失败",
                    ErrorContext(
                        source="GameAnalyzer.analyze_frame",
                        details=str(e)
                    )
                )
            )
            return None
            
    def is_model_loaded(self) -> bool:
        """检查模型是否已加载"""
        return self.model is not None
        
    def _create_model(self) -> nn.Module:
        """创建模型"""
        try:
            # 根据配置创建模型
            model_config = self.model_config.get('model', {})
            model_type = model_config.get('type', 'cnn')
            
            if model_type == 'cnn':
                return self._create_cnn_model(model_config)
            else:
                self.error_handler.handle_error(
                    ModelError(
                        ErrorCode.UNKNOWN_MODEL_TYPE,
                        f"未知的模型类型: {model_type}",
                        ErrorContext(
                            source="GameAnalyzer._create_model",
                            details=f"model_type: {model_type}"
                        )
                    )
                )
                return None
                
        except Exception as e:
            self.error_handler.handle_error(
                ModelError(
                    ErrorCode.MODEL_CREATION_FAILED,
                    "模型创建失败",
                    ErrorContext(
                        source="GameAnalyzer._create_model",
                        details=str(e)
                    )
                )
            )
            return None
            
    def _create_cnn_model(self, config: Dict[str, Any]) -> nn.Module:
        """创建CNN模型"""
        try:
            # 获取配置参数
            input_channels = config.get('input_channels', 3)
            num_classes = config.get('num_classes', 10)
            
            # 创建模型
            model = nn.Sequential(
                nn.Conv2d(input_channels, 32, kernel_size=3, padding=1),
                nn.ReLU(),
                nn.MaxPool2d(2),
                nn.Conv2d(32, 64, kernel_size=3, padding=1),
                nn.ReLU(),
                nn.MaxPool2d(2),
                nn.Conv2d(64, 128, kernel_size=3, padding=1),
                nn.ReLU(),
                nn.MaxPool2d(2),
                nn.Flatten(),
                nn.Linear(128 * 8 * 8, 512),
                nn.ReLU(),
                nn.Linear(512, num_classes)
            )
            
            return model
            
        except Exception as e:
            self.error_handler.handle_error(
                ModelError(
                    ErrorCode.CNN_MODEL_CREATION_FAILED,
                    "CNN模型创建失败",
                    ErrorContext(
                        source="GameAnalyzer._create_cnn_model",
                        details=str(e)
                    )
                )
            )
            return None
            
    def _preprocess_frame(self, frame: np.ndarray) -> Optional[torch.Tensor]:
        """预处理图像"""
        try:
            if frame is None or not isinstance(frame, np.ndarray):
                self.error_handler.handle_error(
                    ModelError(
                        ErrorCode.INVALID_FRAME,
                        "无效的图像数据",
                        ErrorContext(
                            source="GameAnalyzer._preprocess_frame",
                            details="frame is None or not numpy array"
                        )
                    )
                )
                return None
                
            # 调整大小
            frame = cv2.resize(frame, (64, 64))
            
            # 转换为张量
            frame = torch.from_numpy(frame).float()
            frame = frame.permute(2, 0, 1)  # HWC -> CHW
            frame = frame.unsqueeze(0)  # 添加批次维度
            
            return frame
            
        except Exception as e:
            self.error_handler.handle_error(
                ModelError(
                    ErrorCode.FRAME_PREPROCESSING_FAILED,
                    "图像预处理失败",
                    ErrorContext(
                        source="GameAnalyzer._preprocess_frame",
                        details=str(e)
                    )
                )
            )
            return None
            
    def _postprocess_output(self, output: torch.Tensor) -> Dict[str, Any]:
        """后处理模型输出"""
        try:
            # 获取预测结果
            predictions = output.softmax(dim=1)
            class_idx = predictions.argmax(dim=1).item()
            confidence = predictions[0, class_idx].item()
            
            return {
                'class': class_idx,
                'confidence': confidence,
                'predictions': predictions[0].tolist()
            }
            
        except Exception as e:
            self.error_handler.handle_error(
                ModelError(
                    ErrorCode.OUTPUT_POSTPROCESSING_FAILED,
                    "输出后处理失败",
                    ErrorContext(
                        source="GameAnalyzer._postprocess_output",
                        details=str(e)
                    )
                )
            )
            return {}
            
    def cleanup(self) -> None:
        """清理资源"""
        self.model = None
        self.is_initialized = False
        
    def load_custom_classifier(self, model_path: str, class_names: List[str]) -> bool:
        """
        加载自定义分类器
        
        Args:
            model_path: 模型文件路径
            class_names: 类别名称列表
            
        Returns:
            bool: 是否加载成功
        """
        if os.path.exists(model_path):
            try:
                self.custom_classifier = torch.load(model_path)
                self.class_names = class_names
                self.logger.info(f"成功加载自定义分类器: {model_path}")
                return True
            except Exception as e:
                self.logger.error(f"加载自定义分类器失败: {e}")
                return False
        else:
            self.logger.error(f"模型文件不存在: {model_path}")
            return False
            
    def extract_features(self, frame: np.ndarray) -> np.ndarray:
        """
        提取图像特征
        
        Args:
            frame: 输入图像
            
        Returns:
            np.ndarray: 特征向量
        """
        try:
            # 预处理图像
            img_tensor = self.transform(frame)
            img_tensor = img_tensor.unsqueeze(0)
            
            # 提取特征
            with torch.no_grad():
                features = self.model(img_tensor)
                
            return features.numpy()
        except Exception as e:
            self.logger.error(f"提取图像特征失败: {e}")
            return np.array([])
        
    def analyze_game_state(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        分析游戏状态
        
        Args:
            frame: 输入图像
            
        Returns:
            Dict[str, Any]: 游戏状态信息
        """
        try:
            # 分析画面
            analysis = self.analyze_frame(frame)
            
            # 检测物体
            objects = self.detect_objects(frame)
            
            return {
                'analysis': analysis,
                'objects': objects
            }
        except Exception as e:
            self.logger.error(f"分析游戏状态失败: {e}")
            return {
                'analysis': None,
                'objects': []
            }
    
    def _detect_buttons(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """检测按钮
        
        Args:
            frame: 游戏画面
            
        Returns:
            按钮列表，每个按钮包含位置、大小等信息
        """
        try:
            # 这里可以使用模板匹配、颜色检测等方法识别按钮
            # 示例实现，实际应用中需要根据具体游戏定制
            buttons = []
            
            # 简单示例：检测特定颜色区域作为按钮
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lower_blue = np.array([100, 50, 50])
            upper_blue = np.array([140, 255, 255])
            mask = cv2.inRange(hsv, lower_blue, upper_blue)
            
            # 查找轮廓
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                # 过滤小轮廓
                if cv2.contourArea(contour) < 500:
                    continue
                    
                # 获取轮廓的外接矩形
                x, y, w, h = cv2.boundingRect(contour)
                center_x = x + w // 2
                center_y = y + h // 2
                
                buttons.append({
                    "position": (center_x, center_y),
                    "size": (w, h),
                    "type": "button",
                    "confidence": 0.8
                })
                
            return buttons
            
        except Exception as e:
            self.logger.error(f"检测按钮失败: {str(e)}")
            return []
    
    def _detect_enemies(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """检测敌人
        
        Args:
            frame: 游戏画面
            
        Returns:
            敌人列表，每个敌人包含位置、类型等信息
        """
        try:
            # 使用图像处理服务进行目标检测
            # 这里只是示例，实际应用需要根据具体游戏定制
            enemies = []
            
            # 示例：假设敌人是红色的
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lower_red1 = np.array([0, 100, 100])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([160, 100, 100])
            upper_red2 = np.array([180, 255, 255])
            
            mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
            mask = cv2.bitwise_or(mask1, mask2)
            
            # 查找轮廓
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                # 过滤小轮廓
                if cv2.contourArea(contour) < 300:
                    continue
                    
                # 获取轮廓的外接矩形
                x, y, w, h = cv2.boundingRect(contour)
                center_x = x + w // 2
                center_y = y + h // 2
                
                enemies.append({
                    "position": (center_x, center_y),
                    "size": (w, h),
                    "type": "enemy",
                    "health": 100,  # 假设敌人满血
                    "distance": self._calculate_distance((center_x, center_y), (frame.shape[1] // 2, frame.shape[0] // 2))
                })
            
            # 按距离排序
            enemies.sort(key=lambda x: x["distance"])
            
            return enemies
            
        except Exception as e:
            self.logger.error(f"检测敌人失败: {str(e)}")
            return []
    
    def _detect_items(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """检测物品
        
        Args:
            frame: 游戏画面
            
        Returns:
            物品列表，每个物品包含位置、类型等信息
        """
        try:
            # 使用图像处理服务进行物品检测
            # 这里只是示例，实际应用需要根据具体游戏定制
            items = []
            
            # 示例：假设物品是黄色的
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lower_yellow = np.array([20, 100, 100])
            upper_yellow = np.array([30, 255, 255])
            mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
            
            # 查找轮廓
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                # 过滤小轮廓
                if cv2.contourArea(contour) < 100:
                    continue
                    
                # 获取轮廓的外接矩形
                x, y, w, h = cv2.boundingRect(contour)
                center_x = x + w // 2
                center_y = y + h // 2
                
                items.append({
                    "position": (center_x, center_y),
                    "size": (w, h),
                    "type": "item",
                    "value": "unknown",
                    "distance": self._calculate_distance((center_x, center_y), (frame.shape[1] // 2, frame.shape[0] // 2))
                })
            
            # 按距离排序
            items.sort(key=lambda x: x["distance"])
            
            return items
            
        except Exception as e:
            self.logger.error(f"检测物品失败: {str(e)}")
            return []
    
    def _detect_dialog(self, frame: np.ndarray) -> Dict[str, Any]:
        """检测对话框
        
        Args:
            frame: 游戏画面
            
        Returns:
            对话框信息，包含位置、大小、关闭按钮等
        """
        try:
            # 示例：检测灰色矩形区域作为对话框
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
            
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                # 过滤小轮廓
                if cv2.contourArea(contour) < 10000:  # 对话框通常较大
                    continue
                    
                # 获取轮廓的外接矩形
                x, y, w, h = cv2.boundingRect(contour)
                
                # 检查是否为矩形（对话框通常是矩形）
                aspect_ratio = float(w) / h
                if 1.5 < aspect_ratio < 4:  # 对话框通常是宽大于高的矩形
                    # 假设右上角是关闭按钮
                    close_button_x = x + w - 20
                    close_button_y = y + 20
                    
                    return {
                        "position": (x, y),
                        "size": (w, h),
                        "close_button": {
                            "position": (close_button_x, close_button_y),
                            "size": (20, 20)
                        }
                    }
            
            return None
            
        except Exception as e:
            self.logger.error(f"检测对话框失败: {str(e)}")
            return None
    
    def _detect_health_mana(self, frame: np.ndarray) -> Tuple[Optional[float], Optional[float]]:
        """检测生命值和法力值
        
        Args:
            frame: 游戏画面
            
        Returns:
            生命值和法力值，0-100的百分比
        """
        try:
            # 示例：假设生命条在左下角，为红色；法力条在其下方，为蓝色
            height, width = frame.shape[:2]
            
            # 假设生命条区域
            health_roi = frame[height - 50:height - 40, 10:210]
            # 假设法力条区域
            mana_roi = frame[height - 30:height - 20, 10:210]
            
            # 检测红色（生命）
            hsv_health = cv2.cvtColor(health_roi, cv2.COLOR_BGR2HSV)
            lower_red1 = np.array([0, 100, 100])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([160, 100, 100])
            upper_red2 = np.array([180, 255, 255])
            
            mask1 = cv2.inRange(hsv_health, lower_red1, upper_red1)
            mask2 = cv2.inRange(hsv_health, lower_red2, upper_red2)
            health_mask = cv2.bitwise_or(mask1, mask2)
            
            # 检测蓝色（法力）
            hsv_mana = cv2.cvtColor(mana_roi, cv2.COLOR_BGR2HSV)
            lower_blue = np.array([100, 50, 50])
            upper_blue = np.array([140, 255, 255])
            mana_mask = cv2.inRange(hsv_mana, lower_blue, upper_blue)
            
            # 计算填充比例
            health_fill = np.sum(health_mask > 0) / (health_roi.shape[0] * health_roi.shape[1])
            mana_fill = np.sum(mana_mask > 0) / (mana_roi.shape[0] * mana_roi.shape[1])
            
            # 转换为百分比
            health = min(100, max(0, health_fill * 100))
            mana = min(100, max(0, mana_fill * 100))
            
            return health, mana
            
        except Exception as e:
            self.logger.error(f"检测生命值和法力值失败: {str(e)}")
            return None, None
    
    def _detect_player_position(self, frame: np.ndarray) -> Tuple[int, int]:
        """检测玩家位置
        
        Args:
            frame: 游戏画面
            
        Returns:
            玩家位置坐标
        """
        try:
            # 示例：假设玩家总是在屏幕中心
            height, width = frame.shape[:2]
            return (width // 2, height // 2)
            
        except Exception as e:
            self.logger.error(f"检测玩家位置失败: {str(e)}")
            return (0, 0)
    
    def _calculate_distance(self, point1: Tuple[int, int], point2: Tuple[int, int]) -> float:
        """计算两点之间的距离
        
        Args:
            point1: 第一个点的坐标
            point2: 第二个点的坐标
            
        Returns:
            两点之间的欧氏距离
        """
        x1, y1 = point1
        x2, y2 = point2
        return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        
    def detect_objects(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        检测游戏中的物体
        
        Args:
            frame: 输入图像
            
        Returns:
            List[Dict[str, Any]]: 检测到的物体列表
        """
        try:
            # 使用OpenCV的物体检测
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            
            # 查找轮廓
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # 过滤轮廓
            objects = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 100:  # 过滤小区域
                    x, y, w, h = cv2.boundingRect(contour)
                    objects.append({
                        'x': x,
                        'y': y,
                        'width': w,
                        'height': h,
                        'area': area
                    })
                    
            self.logger.debug(f"检测到 {len(objects)} 个物体")
            return objects
        except Exception as e:
            self.logger.error(f"检测物体失败: {e}")
            return []
        
    def analyze_game_state(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        分析游戏状态
        
        Args:
            frame: 输入图像
            
        Returns:
            Dict[str, Any]: 游戏状态信息
        """
        try:
            # 分析画面
            analysis = self.analyze_frame(frame)
            
            # 检测物体
            objects = self.detect_objects(frame)
            
            return {
                'analysis': analysis,
                'objects': objects
            }
        except Exception as e:
            self.logger.error(f"分析游戏状态失败: {e}")
            return {
                'analysis': None,
                'objects': []
            } 