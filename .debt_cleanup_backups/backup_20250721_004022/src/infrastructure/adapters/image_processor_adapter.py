"""图像处理服务适配器

这个模块提供了图像处理服务的适配器实现，将现有的图像处理系统包装为符合IImageProcessorService接口的服务。
使用适配器模式来保持向后兼容性，同时支持新的依赖注入架构。
"""

from typing import List, Optional, Tuple, Dict, Any, Union
import numpy as np
from pathlib import Path

from ...core.interfaces.services import (
    IImageProcessorService, ILoggerService, IConfigService, IErrorHandler,
    Point, Rectangle, TemplateMatchResult
)


class ImageProcessorServiceAdapter(IImageProcessorService):
    """图像处理服务适配器
    
    将现有的图像处理系统适配为IImageProcessorService接口。
    提供图像加载、处理、模板匹配等功能。
    """
    
    def __init__(self, logger_service: Optional[ILoggerService] = None,
                 config_service: Optional[IConfigService] = None,
                 error_handler: Optional[IErrorHandler] = None):
        self._logger_service = logger_service
        self._config_service = config_service
        self._error_handler = error_handler
        self._image_processor_instance = None
        self._is_initialized = False
        self._template_cache: Dict[str, np.ndarray] = {}
        self._default_threshold = 0.8
    
    def _ensure_image_processor_loaded(self) -> None:
        """确保图像处理器已加载"""
        if not self._is_initialized:
            try:
                # 尝试导入现有的图像处理系统
                from ...common.image_processor import image_processor
                self._image_processor_instance = image_processor
                self._is_initialized = True
                self._log_info("图像处理器已加载")
            except ImportError as e:
                self._log_error(f"无法导入现有图像处理系统: {e}")
                # 创建一个基本的图像处理器实现
                self._create_fallback_image_processor()
                self._is_initialized = True
    
    def _create_fallback_image_processor(self) -> None:
        """创建备用图像处理器"""
        try:
            import cv2
            self._cv2 = cv2
            self._image_processor_instance = self
            self._log_info("使用备用图像处理器")
        except ImportError:
            self._log_error("无法导入OpenCV，图像处理功能将受限")
            self._image_processor_instance = None
    
    def _log_info(self, message: str, **kwargs) -> None:
        """记录信息日志"""
        if self._logger_service:
            self._logger_service.info(message, **kwargs)
    
    def _log_error(self, message: str, **kwargs) -> None:
        """记录错误日志"""
        if self._logger_service:
            self._logger_service.error(message, **kwargs)
    
    def _log_warning(self, message: str, **kwargs) -> None:
        """记录警告日志"""
        if self._logger_service:
            self._logger_service.warning(message, **kwargs)
    
    def _handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
        """处理错误"""
        if self._error_handler:
            self._error_handler.handle_error(error, context)
        else:
            self._log_error(f"图像处理错误: {error}")
    
    def _get_threshold(self) -> float:
        """获取匹配阈值"""
        if self._config_service:
            return self._config_service.get('image_processing.threshold', self._default_threshold)
        return self._default_threshold
    
    def load_image(self, path: Union[str, Path]) -> Optional[np.ndarray]:
        """加载图像"""
        self._ensure_image_processor_loaded()
        
        if not self._image_processor_instance:
            return None
        
        try:
            # 如果有现有的方法，使用它
            if (hasattr(self._image_processor_instance, 'load_image') and 
                self._image_processor_instance != self):
                return self._image_processor_instance.load_image(path)
            
            # 使用备用实现
            return self._load_image_fallback(path)
        
        except Exception as e:
            self._handle_error(e, {'operation': 'load_image', 'path': str(path)})
            return None
    
    def _load_image_fallback(self, path: Union[str, Path]) -> Optional[np.ndarray]:
        """备用图像加载实现"""
        if not hasattr(self, '_cv2'):
            return None
        
        try:
            image_path = str(path)
            image = self._cv2.imread(image_path)
            if image is not None:
                self._log_info(f"图像已加载: {image_path}")
                return image
            else:
                self._log_error(f"无法加载图像: {image_path}")
                return None
        
        except Exception as e:
            self._handle_error(e, {'operation': '_load_image_fallback', 'path': str(path)})
            return None
    
    def save_image(self, image: np.ndarray, path: Union[str, Path]) -> bool:
        """保存图像"""
        self._ensure_image_processor_loaded()
        
        if not self._image_processor_instance:
            return False
        
        try:
            # 如果有现有的方法，使用它
            if (hasattr(self._image_processor_instance, 'save_image') and 
                self._image_processor_instance != self):
                return self._image_processor_instance.save_image(image, path)
            
            # 使用备用实现
            return self._save_image_fallback(image, path)
        
        except Exception as e:
            self._handle_error(e, {'operation': 'save_image', 'path': str(path)})
            return False
    
    def _save_image_fallback(self, image: np.ndarray, path: Union[str, Path]) -> bool:
        """备用图像保存实现"""
        if not hasattr(self, '_cv2'):
            return False
        
        try:
            image_path = str(path)
            result = self._cv2.imwrite(image_path, image)
            if result:
                self._log_info(f"图像已保存: {image_path}")
                return True
            else:
                self._log_error(f"无法保存图像: {image_path}")
                return False
        
        except Exception as e:
            self._handle_error(e, {'operation': '_save_image_fallback', 'path': str(path)})
            return False
    
    def resize_image(self, image: np.ndarray, width: int, height: int) -> Optional[np.ndarray]:
        """调整图像大小"""
        self._ensure_image_processor_loaded()
        
        if not self._image_processor_instance:
            return None
        
        try:
            # 如果有现有的方法，使用它
            if (hasattr(self._image_processor_instance, 'resize_image') and 
                self._image_processor_instance != self):
                return self._image_processor_instance.resize_image(image, width, height)
            
            # 使用备用实现
            return self._resize_image_fallback(image, width, height)
        
        except Exception as e:
            self._handle_error(e, {'operation': 'resize_image', 'size': f'{width}x{height}'})
            return None
    
    def _resize_image_fallback(self, image: np.ndarray, width: int, height: int) -> Optional[np.ndarray]:
        """备用图像调整大小实现"""
        if not hasattr(self, '_cv2'):
            return None
        
        try:
            resized = self._cv2.resize(image, (width, height))
            self._log_info(f"图像大小已调整: {width}x{height}")
            return resized
        
        except Exception as e:
            self._handle_error(e, {'operation': '_resize_image_fallback'})
            return None
    
    def crop_image(self, image: np.ndarray, region: Rectangle) -> Optional[np.ndarray]:
        """裁剪图像"""
        self._ensure_image_processor_loaded()
        
        if not self._image_processor_instance:
            return None
        
        try:
            # 如果有现有的方法，使用它
            if (hasattr(self._image_processor_instance, 'crop_image') and 
                self._image_processor_instance != self):
                return self._image_processor_instance.crop_image(image, region)
            
            # 使用备用实现
            return self._crop_image_fallback(image, region)
        
        except Exception as e:
            self._handle_error(e, {'operation': 'crop_image', 'region': str(region)})
            return None
    
    def _crop_image_fallback(self, image: np.ndarray, region: Rectangle) -> Optional[np.ndarray]:
        """备用图像裁剪实现"""
        try:
            y1 = max(0, region.y)
            y2 = min(image.shape[0], region.y + region.height)
            x1 = max(0, region.x)
            x2 = min(image.shape[1], region.x + region.width)
            
            if y2 > y1 and x2 > x1:
                cropped = image[y1:y2, x1:x2]
                self._log_info(f"图像已裁剪: {region}")
                return cropped
            else:
                self._log_error(f"无效的裁剪区域: {region}")
                return None
        
        except Exception as e:
            self._handle_error(e, {'operation': '_crop_image_fallback'})
            return None
    
    def find_template(self, image: np.ndarray, template: np.ndarray, 
                     threshold: Optional[float] = None) -> List[TemplateMatchResult]:
        """模板匹配"""
        self._ensure_image_processor_loaded()
        
        if not self._image_processor_instance:
            return []
        
        try:
            # 如果有现有的方法，使用它
            if (hasattr(self._image_processor_instance, 'find_template') and 
                self._image_processor_instance != self):
                results = self._image_processor_instance.find_template(image, template, threshold)
                # 转换为TemplateMatchResult格式
                return self._convert_to_template_results(results)
            
            # 使用备用实现
            return self._find_template_fallback(image, template, threshold)
        
        except Exception as e:
            self._handle_error(e, {'operation': 'find_template'})
            return []
    
    def _find_template_fallback(self, image: np.ndarray, template: np.ndarray, 
                               threshold: Optional[float] = None) -> List[TemplateMatchResult]:
        """备用模板匹配实现"""
        if not hasattr(self, '_cv2'):
            return []
        
        try:
            if threshold is None:
                threshold = self._get_threshold()
            
            # 执行模板匹配
            result = self._cv2.matchTemplate(image, template, self._cv2.TM_CCOEFF_NORMED)
            
            # 查找所有匹配位置
            locations = np.where(result >= threshold)
            matches = []
            
            template_height, template_width = template.shape[:2]
            
            for y, x in zip(locations[0], locations[1]):
                confidence = result[y, x]
                center_x = x + template_width // 2
                center_y = y + template_height // 2
                
                match_result = TemplateMatchResult(
                    center=Point(center_x, center_y),
                    confidence=float(confidence),
                    bounds=Rectangle(x, y, template_width, template_height)
                )
                matches.append(match_result)
            
            # 按置信度排序
            matches.sort(key=lambda m: m.confidence, reverse=True)
            
            self._log_info(f"模板匹配完成，找到 {len(matches)} 个匹配")
            return matches
        
        except Exception as e:
            self._handle_error(e, {'operation': '_find_template_fallback'})
            return []
    
    def _convert_to_template_results(self, results: Any) -> List[TemplateMatchResult]:
        """转换模板匹配结果格式"""
        if not results:
            return []
        
        converted_results = []
        
        for result in results:
            if hasattr(result, 'center') and hasattr(result, 'confidence'):
                # 已经是正确格式
                converted_results.append(result)
            elif isinstance(result, dict):
                # 字典格式
                center = result.get('center', Point(0, 0))
                confidence = result.get('confidence', 0.0)
                bounds = result.get('bounds', Rectangle(0, 0, 0, 0))
                
                match_result = TemplateMatchResult(
                    center=center,
                    confidence=confidence,
                    bounds=bounds
                )
                converted_results.append(match_result)
        
        return converted_results
    
    def find_template_from_file(self, image: np.ndarray, template_path: Union[str, Path], 
                               threshold: Optional[float] = None) -> List[TemplateMatchResult]:
        """从文件加载模板并匹配"""
        template_key = str(template_path)
        
        # 检查缓存
        if template_key in self._template_cache:
            template = self._template_cache[template_key]
        else:
            # 加载模板
            template = self.load_image(template_path)
            if template is None:
                self._log_error(f"无法加载模板文件: {template_path}")
                return []
            
            # 缓存模板
            self._template_cache[template_key] = template
        
        return self.find_template(image, template, threshold)
    
    def convert_to_grayscale(self, image: np.ndarray) -> Optional[np.ndarray]:
        """转换为灰度图像"""
        self._ensure_image_processor_loaded()
        
        if not self._image_processor_instance:
            return None
        
        try:
            # 如果有现有的方法，使用它
            if (hasattr(self._image_processor_instance, 'convert_to_grayscale') and 
                self._image_processor_instance != self):
                return self._image_processor_instance.convert_to_grayscale(image)
            
            # 使用备用实现
            return self._convert_to_grayscale_fallback(image)
        
        except Exception as e:
            self._handle_error(e, {'operation': 'convert_to_grayscale'})
            return None
    
    def _convert_to_grayscale_fallback(self, image: np.ndarray) -> Optional[np.ndarray]:
        """备用灰度转换实现"""
        if not hasattr(self, '_cv2'):
            return None
        
        try:
            if len(image.shape) == 3:
                gray = self._cv2.cvtColor(image, self._cv2.COLOR_BGR2GRAY)
                self._log_info("图像已转换为灰度")
                return gray
            else:
                # 已经是灰度图像
                return image
        
        except Exception as e:
            self._handle_error(e, {'operation': '_convert_to_grayscale_fallback'})
            return None
    
    def get_image_info(self, image: np.ndarray) -> Dict[str, Any]:
        """获取图像信息"""
        try:
            height, width = image.shape[:2]
            channels = image.shape[2] if len(image.shape) == 3 else 1
            
            return {
                'width': width,
                'height': height,
                'channels': channels,
                'dtype': str(image.dtype),
                'size': image.size,
                'shape': image.shape
            }
        
        except Exception as e:
            self._handle_error(e, {'operation': 'get_image_info'})
            return {}
    
    def apply_threshold(self, image: np.ndarray, threshold_value: int, 
                      max_value: int = 255) -> Optional[np.ndarray]:
        """应用阈值处理"""
        self._ensure_image_processor_loaded()
        
        if not hasattr(self, '_cv2'):
            return None
        
        try:
            # 确保是灰度图像
            if len(image.shape) == 3:
                gray = self._cv2.cvtColor(image, self._cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            _, thresh = self._cv2.threshold(gray, threshold_value, max_value, self._cv2.THRESH_BINARY)
            self._log_info(f"阈值处理完成: {threshold_value}")
            return thresh
        
        except Exception as e:
            self._handle_error(e, {'operation': 'apply_threshold'})
            return None
    
    def find_contours(self, image: np.ndarray) -> List[np.ndarray]:
        """查找轮廓"""
        self._ensure_image_processor_loaded()
        
        if not hasattr(self, '_cv2'):
            return []
        
        try:
            # 确保是二值图像
            if len(image.shape) == 3:
                gray = self._cv2.cvtColor(image, self._cv2.COLOR_BGR2GRAY)
                _, binary = self._cv2.threshold(gray, 127, 255, self._cv2.THRESH_BINARY)
            else:
                binary = image
            
            contours, _ = self._cv2.findContours(binary, self._cv2.RETR_EXTERNAL, self._cv2.CHAIN_APPROX_SIMPLE)
            self._log_info(f"找到 {len(contours)} 个轮廓")
            return list(contours)
        
        except Exception as e:
            self._handle_error(e, {'operation': 'find_contours'})
            return []
    
    def clear_template_cache(self) -> None:
        """清除模板缓存"""
        self._template_cache.clear()
        self._log_info("模板缓存已清除")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """获取缓存信息"""
        return {
            'cached_templates': len(self._template_cache),
            'template_paths': list(self._template_cache.keys())
        }
    
    def set_default_threshold(self, threshold: float) -> None:
        """设置默认匹配阈值"""
        self._default_threshold = threshold
        self._log_info(f"默认阈值已设置为: {threshold}")
    
    def get_default_threshold(self) -> float:
        """获取默认匹配阈值"""
        return self._default_threshold