"""
状态识别服务
负责游戏状态的识别和分析
"""
from typing import Optional, List, Dict, Tuple
import cv2
import numpy as np
from dataclasses import dataclass
from src.services.error_handler import ErrorHandler
from src.common.error_types import ErrorCode, ErrorContext
from .template_matcher import TemplateMatcher, MatchResult
import os

@dataclass
class GameState:
    """游戏状态"""
    name: str  # 状态名称
    confidence: float  # 置信度
    features: Dict[str, float]  # 特征值
    regions: List[Tuple[int, int, int, int]]  # 相关区域
    matches: List[MatchResult]  # 模板匹配结果

class StateRecognizer:
    """状态识别器"""
    
    def __init__(self, error_handler: ErrorHandler):
        """初始化
        
        Args:
            error_handler: 错误处理器
        """
        self.error_handler = error_handler
        self.template_matcher = TemplateMatcher(error_handler)
        self.states: Dict[str, GameState] = {}
        
    def register_state(self, state: GameState) -> None:
        """注册游戏状态
        
        Args:
            state: 游戏状态
        """
        self.states[state.name] = state
        
    def load_state_template(self, state_name: str, template_path: str) -> bool:
        """加载状态模板
        
        Args:
            state_name: 状态名称
            template_path: 模板图片路径
            
        Returns:
            bool: 是否成功
        """
        return self.template_matcher.load_template_from_file(state_name, template_path)
        
    def analyze_frame(self, frame: np.ndarray) -> Optional[GameState]:
        """分析游戏画面
        
        Args:
            frame: 游戏画面
            
        Returns:
            Optional[GameState]: 识别到的游戏状态
        """
        try:
            # 匹配所有模板
            matches = self.template_matcher.match_all_templates(frame)
            
            if not matches:
                return None
                
            # 按置信度排序
            matches.sort(key=lambda x: x.confidence, reverse=True)
            
            # 获取最佳匹配
            best_match = matches[0]
            state_name = best_match.template_name
            
            if state_name not in self.states:
                return None
                
            # 获取状态信息
            state = self.states[state_name]
            
            # 更新状态信息
            state.confidence = best_match.confidence
            state.matches = matches
            
            # 提取特征
            state.features = self._extract_features(frame, state.regions)
            
            return state
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.STATE_ANALYSIS_ERROR,
                "分析游戏画面失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="StateRecognizer.analyze_frame"
                )
            )
            return None
            
    def _extract_features(self, frame: np.ndarray, 
                         regions: List[Tuple[int, int, int, int]]) -> Dict[str, float]:
        """提取特征
        
        Args:
            frame: 游戏画面
            regions: 区域列表
            
        Returns:
            Dict[str, float]: 特征值
        """
        try:
            features = {}
            
            for i, (x, y, w, h) in enumerate(regions):
                # 提取区域
                roi = frame[y:y+h, x:x+w]
                
                # 计算颜色直方图
                hist = cv2.calcHist([roi], [0, 1, 2], None, [8, 8, 8], 
                                  [0, 256, 0, 256, 0, 256])
                hist = cv2.normalize(hist, hist).flatten()
                
                # 计算纹理特征
                gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                glcm = self._calculate_glcm(gray)
                
                # 保存特征
                features[f"region_{i}_color"] = hist.tolist()
                features[f"region_{i}_texture"] = glcm.tolist()
                
            return features
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.STATE_ANALYSIS_ERROR,
                "提取特征失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="StateRecognizer._extract_features"
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
        
    def save_debug_image(self, frame: np.ndarray, state: GameState,
                        filename: str, debug_dir: str = "debug") -> bool:
        """保存调试图像
        
        Args:
            frame: 游戏画面
            state: 游戏状态
            filename: 文件名
            debug_dir: 调试目录
            
        Returns:
            bool: 是否成功
        """
        try:
            # 创建调试目录
            os.makedirs(debug_dir, exist_ok=True)
            
            # 创建调试图像
            debug_frame = frame.copy()
            
            # 绘制匹配区域
            for match in state.matches:
                x, y = match.location
                w, h = match.size
                cv2.rectangle(debug_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(debug_frame, f"{match.template_name}: {match.confidence:.2f}",
                          (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
            # 绘制状态区域
            for i, (x, y, w, h) in enumerate(state.regions):
                cv2.rectangle(debug_frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                cv2.putText(debug_frame, f"Region {i}",
                          (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                
            # 保存图像
            filepath = os.path.join(debug_dir, f"{filename}.png")
            cv2.imwrite(filepath, debug_frame)
            return True
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.STATE_ANALYSIS_ERROR,
                "保存调试图像失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="StateRecognizer.save_debug_image"
                )
            )
            return False 