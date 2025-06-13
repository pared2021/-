"""
游戏状态分析服务
负责分析游戏画面并识别游戏状态
"""
from typing import Dict, List, Optional, Tuple
import cv2
import numpy as np
from dataclasses import dataclass
from core.error_handler import ErrorHandler, ErrorCode, ErrorContext

@dataclass
class GameState:
    """游戏状态"""
    name: str  # 状态名称
    confidence: float  # 置信度
    features: Dict[str, float]  # 特征值
    regions: List[Tuple[int, int, int, int]]  # 相关区域

class GameStateAnalyzer:
    """游戏状态分析器"""
    
    def __init__(self, error_handler: ErrorHandler):
        """初始化
        
        Args:
            error_handler: 错误处理器
        """
        self.error_handler = error_handler
        self.states: Dict[str, GameState] = {}
        self.templates: Dict[str, np.ndarray] = {}
        
    def load_state_template(self, state_name: str, template_path: str) -> bool:
        """加载状态模板
        
        Args:
            state_name: 状态名称
            template_path: 模板图片路径
            
        Returns:
            bool: 是否成功
        """
        try:
            template = cv2.imread(template_path)
            if template is None:
                raise ValueError(f"无法加载模板图片: {template_path}")
                
            self.templates[state_name] = template
            return True
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.STATE_ANALYSIS_ERROR,
                f"加载状态模板失败: {state_name}",
                ErrorContext(
                    error_info=str(e),
                    error_location="GameStateAnalyzer.load_state_template"
                )
            )
            return False
            
    def register_state(self, state: GameState) -> None:
        """注册游戏状态
        
        Args:
            state: 游戏状态
        """
        self.states[state.name] = state
        
    def analyze_frame(self, frame: np.ndarray) -> Optional[GameState]:
        """分析游戏画面
        
        Args:
            frame: 游戏画面
            
        Returns:
            Optional[GameState]: 识别到的游戏状态
        """
        try:
            # 预处理图像
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # 模板匹配
            best_state = None
            best_confidence = 0.0
            
            for state_name, template in self.templates.items():
                # 转换为灰度图
                template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
                
                # 模板匹配
                result = cv2.matchTemplate(blur, template_gray, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                if max_val > best_confidence:
                    best_confidence = max_val
                    best_state = self.states[state_name]
                    
            # 如果置信度足够高，返回最佳匹配状态
            if best_confidence > 0.8 and best_state:
                return best_state
                
            return None
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.STATE_ANALYSIS_ERROR,
                "分析游戏画面失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="GameStateAnalyzer.analyze_frame"
                )
            )
            return None
            
    def extract_features(self, frame: np.ndarray, region: Tuple[int, int, int, int]) -> Dict[str, float]:
        """提取区域特征
        
        Args:
            frame: 游戏画面
            region: 区域坐标 (x, y, w, h)
            
        Returns:
            Dict[str, float]: 特征值
        """
        try:
            x, y, w, h = region
            roi = frame[y:y+h, x:x+w]
            
            # 计算颜色直方图
            hist = cv2.calcHist([roi], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
            hist = cv2.normalize(hist, hist).flatten()
            
            # 计算纹理特征
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            glcm = self._calculate_glcm(gray)
            
            return {
                "color_hist": hist.tolist(),
                "texture": glcm.tolist()
            }
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.STATE_ANALYSIS_ERROR,
                "提取特征失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="GameStateAnalyzer.extract_features"
                )
            )
            return {}
            
    def _calculate_glcm(self, gray: np.ndarray) -> np.ndarray:
        """计算灰度共生矩阵
        
        Args:
            gray: 灰度图像
            
        Returns:
            np.ndarray: GLCM矩阵
        """
        # 简化版GLCM计算
        glcm = np.zeros((8, 8), dtype=np.uint8)
        h, w = gray.shape
        
        for i in range(h-1):
            for j in range(w-1):
                glcm[gray[i,j]//32, gray[i+1,j]//32] += 1
                
        return glcm 