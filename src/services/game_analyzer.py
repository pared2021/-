import cv2
import numpy as np
import torch
from torchvision import models, transforms
from PIL import Image
import os
from typing import Optional, Dict, List, Any, Tuple
from .logger import GameLogger
from .image_processor import ImageProcessor
from .config import Config

class GameAnalyzer:
    """游戏分析器，使用深度学习模型识别游戏元素"""
    
    def __init__(self, logger: GameLogger, image_processor: ImageProcessor, config: Config):
        """
        初始化游戏分析器
        
        Args:
            logger: 日志服务
            image_processor: 图像处理服务
            config: 配置
        """
        self.logger = logger
        self.image_processor = image_processor
        self.config = config
        
        # 加载预训练的ResNet模型
        self.logger.info("加载预训练的ResNet模型")
        self.model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
        self.model.eval()
        
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
        
    def analyze_frame(self, frame: Optional[np.ndarray]) -> Dict[str, Any]:
        """
        分析游戏画面帧
        
        Args:
            frame (Optional[np.ndarray]): 游戏画面帧数据
            
        Returns:
            Dict[str, Any]: 游戏状态字典
        """
        try:
            # 创建基本的默认状态字典
            default_state = {
                "timestamp": self.image_processor.get_current_timestamp(),
                "buttons": [],
                "enemies": [],
                "items": [],
                "dialog_open": False,
                "health": 100,  # 默认满血
                "mana": 100,    # 默认满蓝
                "position": (0, 0),  # 默认位置
                "screen_size": (0, 0)  # 默认屏幕大小
            }
            
            # 检查帧数据是否为None
            if frame is None:
                self.logger.warning("无法分析游戏画面：帧数据为空")
                return default_state
            
            # 处理布尔型帧(可能是capture_window的错误返回)
            if isinstance(frame, bool):
                self.logger.warning(f"无法分析游戏画面：帧数据类型错误 ({type(frame)})")
                return default_state
            
            # 检查是否是numpy数组
            if not isinstance(frame, np.ndarray):
                self.logger.warning(f"无法分析游戏画面：帧数据不是numpy数组 ({type(frame)})")
                try:
                    frame = np.array(frame)
                    self.logger.debug("成功将帧数据转换为numpy数组")
                except Exception as e:
                    self.logger.error(f"转换帧数据为numpy数组失败: {e}")
                    return default_state
                
            # 尝试将非numpy数组转换为numpy数组
            if not isinstance(frame, np.ndarray):
                try:
                    self.logger.warning(f"尝试将 {type(frame)} 转换为numpy数组")
                    frame = np.array(frame)
                except Exception as e:
                    self.logger.warning(f"无法分析游戏画面：帧数据类型转换失败 ({e})")
                    return default_state
                
            if frame.size == 0:
                self.logger.warning("无法分析游戏画面：帧数据为空数组")
                return default_state
                
            if len(frame.shape) != 3:
                self.logger.warning(f"无法分析游戏画面：帧数据维度错误 ({frame.shape})")
                return default_state
                
            # 检查并修复通道数
            if frame.shape[2] != 3:
                self.logger.warning(f"帧数据通道数错误 ({frame.shape[2]})，尝试转换")
                try:
                    if frame.shape[2] == 4:  # RGBA/BGRA
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                        self.logger.debug("成功将BGRA转换为BGR")
                    elif frame.shape[2] == 1:  # 灰度图
                        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
                        self.logger.debug("成功将灰度图转换为BGR")
                    else:
                        self.logger.warning(f"无法处理的通道数: {frame.shape[2]}")
                        return default_state
                except Exception as e:
                    self.logger.warning(f"通道转换失败: {e}")
                    return default_state
                
            # 检查图像是否全黑或全白
            if np.all(frame == 0):
                self.logger.warning("无法分析游戏画面：帧数据全黑")
                return default_state
                
            if np.all(frame == 255):
                self.logger.warning("无法分析游戏画面：帧数据全白")
                return default_state
            
            # 更新状态字典，使用默认状态作为基础
            state = default_state.copy()
            state["screen_size"] = frame.shape[:2][::-1]  # 宽高
            self.logger.debug(f"画面大小: {state['screen_size']}")
            
            # 检测按钮
            buttons = self._detect_buttons(frame)
            if buttons:
                state["buttons"] = buttons
                
            # 检测敌人
            enemies = self._detect_enemies(frame)
            if enemies:
                state["enemies"] = enemies
                
            # 检测物品
            items = self._detect_items(frame)
            if items:
                state["items"] = items
                
            # 检测对话框
            dialog_info = self._detect_dialog(frame)
            if dialog_info:
                state["dialog_open"] = True
                state["dialog"] = dialog_info
                
            # 检测生命值和法力值
            health, mana = self._detect_health_mana(frame)
            if health is not None:
                state["health"] = health
            if mana is not None:
                state["mana"] = mana
                
            # 检测玩家位置
            position = self._detect_player_position(frame)
            if position:
                state["position"] = position
                
            # 分析完成
            self.logger.debug("成功分析游戏画面")
            return state
            
        except Exception as e:
            self.logger.error(f"分析游戏画面时出错: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return default_state
    
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