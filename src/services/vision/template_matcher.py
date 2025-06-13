"""
模板匹配服务
负责模板匹配和特征提取
"""
from typing import Optional, List, Dict, Tuple
import cv2
import numpy as np
from dataclasses import dataclass
from core.error_handler import ErrorHandler, ErrorCode, ErrorContext

@dataclass
class MatchResult:
    """匹配结果"""
    template_name: str  # 模板名称
    location: Tuple[int, int]  # 匹配位置 (x, y)
    confidence: float  # 置信度
    size: Tuple[int, int]  # 模板大小 (width, height)

class TemplateMatcher:
    """模板匹配器"""
    
    def __init__(self, error_handler: ErrorHandler):
        """初始化
        
        Args:
            error_handler: 错误处理器
        """
        self.error_handler = error_handler
        self.templates: Dict[str, np.ndarray] = {}
        
    def load_template(self, name: str, template: np.ndarray) -> bool:
        """加载模板
        
        Args:
            name: 模板名称
            template: 模板图像
            
        Returns:
            bool: 是否成功
        """
        try:
            # 转换为灰度图
            if len(template.shape) == 3:
                template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
                
            self.templates[name] = template
            return True
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.TEMPLATE_ERROR,
                f"加载模板失败: {name}",
                ErrorContext(
                    error_info=str(e),
                    error_location="TemplateMatcher.load_template"
                )
            )
            return False
            
    def load_template_from_file(self, name: str, filepath: str) -> bool:
        """从文件加载模板
        
        Args:
            name: 模板名称
            filepath: 文件路径
            
        Returns:
            bool: 是否成功
        """
        try:
            template = cv2.imread(filepath)
            if template is None:
                raise ValueError(f"无法加载模板图片: {filepath}")
                
            return self.load_template(name, template)
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.TEMPLATE_ERROR,
                f"从文件加载模板失败: {name}",
                ErrorContext(
                    error_info=str(e),
                    error_location="TemplateMatcher.load_template_from_file"
                )
            )
            return False
            
    def match_template(self, image: np.ndarray, template_name: str,
                      threshold: float = 0.8) -> Optional[MatchResult]:
        """匹配模板
        
        Args:
            image: 输入图像
            template_name: 模板名称
            threshold: 匹配阈值
            
        Returns:
            Optional[MatchResult]: 匹配结果
        """
        try:
            if template_name not in self.templates:
                return None
                
            template = self.templates[template_name]
            
            # 转换为灰度图
            if len(image.shape) == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                
            # 模板匹配
            result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # 检查置信度
            if max_val < threshold:
                return None
                
            # 获取模板大小
            h, w = template.shape
            
            return MatchResult(
                template_name=template_name,
                location=max_loc,
                confidence=max_val,
                size=(w, h)
            )
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.TEMPLATE_ERROR,
                f"匹配模板失败: {template_name}",
                ErrorContext(
                    error_info=str(e),
                    error_location="TemplateMatcher.match_template"
                )
            )
            return None
            
    def match_all_templates(self, image: np.ndarray,
                          threshold: float = 0.8) -> List[MatchResult]:
        """匹配所有模板
        
        Args:
            image: 输入图像
            threshold: 匹配阈值
            
        Returns:
            List[MatchResult]: 匹配结果列表
        """
        try:
            results = []
            
            for name in self.templates:
                result = self.match_template(image, name, threshold)
                if result:
                    results.append(result)
                    
            return results
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.TEMPLATE_ERROR,
                "匹配所有模板失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="TemplateMatcher.match_all_templates"
                )
            )
            return []
            
    def match_template_multi(self, image: np.ndarray, template_name: str,
                           threshold: float = 0.8) -> List[MatchResult]:
        """多位置匹配模板
        
        Args:
            image: 输入图像
            template_name: 模板名称
            threshold: 匹配阈值
            
        Returns:
            List[MatchResult]: 匹配结果列表
        """
        try:
            if template_name not in self.templates:
                return []
                
            template = self.templates[template_name]
            
            # 转换为灰度图
            if len(image.shape) == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                
            # 模板匹配
            result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
            
            # 获取模板大小
            h, w = template.shape
            
            # 查找所有匹配位置
            locations = np.where(result >= threshold)
            matches = []
            
            for pt in zip(*locations[::-1]):
                matches.append(MatchResult(
                    template_name=template_name,
                    location=pt,
                    confidence=result[pt[1], pt[0]],
                    size=(w, h)
                ))
                
            return matches
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.TEMPLATE_ERROR,
                f"多位置匹配模板失败: {template_name}",
                ErrorContext(
                    error_info=str(e),
                    error_location="TemplateMatcher.match_template_multi"
                )
            )
            return [] 