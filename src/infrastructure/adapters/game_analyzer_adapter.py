"""游戏分析服务适配器

这个模块提供了游戏分析服务的适配器实现，将现有的游戏分析系统包装为符合IGameAnalyzer接口的服务。
使用适配器模式来保持向后兼容性，同时支持新的依赖注入架构。
"""

from typing import Dict, Any, Optional, List
import time
from datetime import datetime

from ...core.interfaces.services import (
    IGameAnalyzer, ILoggerService, IImageProcessorService, IConfigService, IErrorHandler,
    AnalysisResult, Point, Rectangle, GameState
)


class GameAnalyzerServiceAdapter(IGameAnalyzer):
    """游戏分析服务适配器
    
    将现有的游戏分析系统适配为IGameAnalyzer接口。
    提供游戏状态分析、元素识别等功能。
    """
    
    def __init__(self, logger_service: Optional[ILoggerService] = None,
                 image_processor: Optional[IImageProcessorService] = None,
                 config_service: Optional[IConfigService] = None,
                 error_handler: Optional[IErrorHandler] = None):
        self._logger_service = logger_service
        self._image_processor = image_processor
        self._config_service = config_service
        self._error_handler = error_handler
        self._game_analyzer_instance = None
        self._is_initialized = False
        self._analysis_cache: Dict[str, AnalysisResult] = {}
        self._cache_timeout = 2.0  # 缓存超时时间（秒）
        self._last_analysis_time = 0
        self._current_game_state = GameState.UNKNOWN
    
    def _ensure_game_analyzer_loaded(self) -> None:
        """确保游戏分析器已加载"""
        if not self._is_initialized:
            try:
                # 尝试导入现有的游戏分析系统
                from ...common.game_analyzer import game_analyzer
                self._game_analyzer_instance = game_analyzer
                self._is_initialized = True
                self._log_info("游戏分析器已加载")
            except ImportError as e:
                self._log_error(f"无法导入现有游戏分析系统: {e}")
                # 创建一个基本的游戏分析器实现
                self._create_fallback_game_analyzer()
                self._is_initialized = True
    
    def _create_fallback_game_analyzer(self) -> None:
        """创建备用游戏分析器"""
        self._game_analyzer_instance = self
        self._log_info("使用备用游戏分析器")
    
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
    
    def _log_debug(self, message: str, **kwargs) -> None:
        """记录调试日志"""
        if self._logger_service:
            self._logger_service.debug(message, **kwargs)
    
    def _handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
        """处理错误"""
        if self._error_handler:
            self._error_handler.handle_error(error, context)
        else:
            self._log_error(f"游戏分析错误: {error}")
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """检查缓存是否有效"""
        if cache_key not in self._analysis_cache:
            return False
        
        result = self._analysis_cache[cache_key]
        if hasattr(result, 'timestamp'):
            return (time.time() - result.timestamp) < self._cache_timeout
        
        return (time.time() - self._last_analysis_time) < self._cache_timeout
    
    def _create_cache_key(self, **kwargs) -> str:
        """创建缓存键"""
        key_parts = []
        for k, v in sorted(kwargs.items()):
            if v is not None:
                key_parts.append(f"{k}={v}")
        return "|".join(key_parts)
    
    def analyze_screen(self, image_data: bytes, **options) -> AnalysisResult:
        """分析屏幕图像"""
        self._ensure_game_analyzer_loaded()
        
        try:
            # 创建缓存键
            cache_key = self._create_cache_key(
                image_hash=hash(image_data) if image_data else 0,
                **options
            )
            
            # 检查缓存
            if self._is_cache_valid(cache_key):
                self._log_debug("使用缓存的分析结果")
                return self._analysis_cache[cache_key]
            
            # 如果有现有的方法，使用它
            if (hasattr(self._game_analyzer_instance, 'analyze_screen') and 
                self._game_analyzer_instance != self):
                result = self._game_analyzer_instance.analyze_screen(image_data, **options)
                # 转换为AnalysisResult格式
                analysis_result = self._convert_to_analysis_result(result)
            else:
                # 使用备用实现
                analysis_result = self._analyze_screen_fallback(image_data, **options)
            
            # 缓存结果
            self._analysis_cache[cache_key] = analysis_result
            self._last_analysis_time = time.time()
            
            return analysis_result
        
        except Exception as e:
            self._handle_error(e, {'operation': 'analyze_screen', 'options': options})
            return self._create_empty_analysis_result()
    
    def _analyze_screen_fallback(self, image_data: bytes, **options) -> AnalysisResult:
        """备用屏幕分析实现"""
        try:
            # 基本的屏幕分析逻辑
            analysis_data = {
                'timestamp': time.time(),
                'image_size': len(image_data) if image_data else 0,
                'analysis_type': 'fallback',
                'elements_found': [],
                'game_state': self._current_game_state,
                'confidence': 0.5
            }
            
            # 如果有图像处理器，尝试进行基本分析
            if self._image_processor and image_data:
                # 这里可以添加基本的图像分析逻辑
                # 例如：检测特定颜色区域、查找已知模板等
                pass
            
            self._log_info("完成备用屏幕分析")
            
            return AnalysisResult(
                success=True,
                confidence=analysis_data['confidence'],
                data=analysis_data,
                timestamp=analysis_data['timestamp'],
                error_message=None
            )
        
        except Exception as e:
            self._handle_error(e, {'operation': '_analyze_screen_fallback'})
            return self._create_empty_analysis_result()
    
    def _convert_to_analysis_result(self, result: Any) -> AnalysisResult:
        """转换分析结果格式"""
        if isinstance(result, AnalysisResult):
            return result
        
        # 如果是字典格式
        if isinstance(result, dict):
            return AnalysisResult(
                success=result.get('success', True),
                confidence=result.get('confidence', 0.0),
                data=result.get('data', {}),
                timestamp=result.get('timestamp', time.time()),
                error_message=result.get('error_message')
            )
        
        # 如果是其他格式，尝试转换
        return AnalysisResult(
            success=True,
            confidence=0.5,
            data={'raw_result': result},
            timestamp=time.time(),
            error_message=None
        )
    
    def _create_empty_analysis_result(self) -> AnalysisResult:
        """创建空的分析结果"""
        return AnalysisResult(
            success=False,
            confidence=0.0,
            data={},
            timestamp=time.time(),
            error_message="分析失败"
        )
    
    def find_elements(self, image_data: bytes, element_types: List[str], **options) -> Dict[str, List[Dict[str, Any]]]:
        """查找游戏元素"""
        self._ensure_game_analyzer_loaded()
        
        try:
            # 如果有现有的方法，使用它
            if (hasattr(self._game_analyzer_instance, 'find_elements') and 
                self._game_analyzer_instance != self):
                return self._game_analyzer_instance.find_elements(image_data, element_types, **options)
            
            # 使用备用实现
            return self._find_elements_fallback(image_data, element_types, **options)
        
        except Exception as e:
            self._handle_error(e, {'operation': 'find_elements', 'element_types': element_types})
            return {element_type: [] for element_type in element_types}
    
    def _find_elements_fallback(self, image_data: bytes, element_types: List[str], **options) -> Dict[str, List[Dict[str, Any]]]:
        """备用元素查找实现"""
        try:
            results = {}
            
            for element_type in element_types:
                elements = []
                
                # 基本的元素查找逻辑
                if element_type == 'button':
                    # 查找按钮元素
                    elements = self._find_buttons_fallback(image_data, **options)
                elif element_type == 'text':
                    # 查找文本元素
                    elements = self._find_text_fallback(image_data, **options)
                elif element_type == 'icon':
                    # 查找图标元素
                    elements = self._find_icons_fallback(image_data, **options)
                
                results[element_type] = elements
            
            self._log_info(f"元素查找完成，类型: {element_types}")
            return results
        
        except Exception as e:
            self._handle_error(e, {'operation': '_find_elements_fallback'})
            return {element_type: [] for element_type in element_types}
    
    def _find_buttons_fallback(self, image_data: bytes, **options) -> List[Dict[str, Any]]:
        """备用按钮查找实现"""
        # 这里可以实现基本的按钮识别逻辑
        # 例如：基于颜色、形状、模板匹配等
        return []
    
    def _find_text_fallback(self, image_data: bytes, **options) -> List[Dict[str, Any]]:
        """备用文本查找实现"""
        # 这里可以实现基本的文本识别逻辑
        # 例如：OCR、模板匹配等
        return []
    
    def _find_icons_fallback(self, image_data: bytes, **options) -> List[Dict[str, Any]]:
        """备用图标查找实现"""
        # 这里可以实现基本的图标识别逻辑
        # 例如：模板匹配、特征检测等
        return []
    
    def get_game_state(self, image_data: bytes, **options) -> GameState:
        """获取游戏状态"""
        self._ensure_game_analyzer_loaded()
        
        try:
            # 如果有现有的方法，使用它
            if (hasattr(self._game_analyzer_instance, 'get_game_state') and 
                self._game_analyzer_instance != self):
                state = self._game_analyzer_instance.get_game_state(image_data, **options)
                # 转换为GameState枚举
                return self._convert_to_game_state(state)
            
            # 使用备用实现
            return self._get_game_state_fallback(image_data, **options)
        
        except Exception as e:
            self._handle_error(e, {'operation': 'get_game_state'})
            return GameState.UNKNOWN
    
    def _get_game_state_fallback(self, image_data: bytes, **options) -> GameState:
        """备用游戏状态获取实现"""
        try:
            # 基本的游戏状态检测逻辑
            # 这里可以基于图像特征、模板匹配等来判断游戏状态
            
            if not image_data:
                return GameState.UNKNOWN
            
            # 简单的状态检测逻辑（示例）
            # 实际实现需要根据具体游戏来定制
            
            self._log_debug("执行备用游戏状态检测")
            
            # 默认返回运行中状态
            self._current_game_state = GameState.RUNNING
            return self._current_game_state
        
        except Exception as e:
            self._handle_error(e, {'operation': '_get_game_state_fallback'})
            return GameState.UNKNOWN
    
    def _convert_to_game_state(self, state: Any) -> GameState:
        """转换游戏状态格式"""
        if isinstance(state, GameState):
            return state
        
        if isinstance(state, str):
            state_mapping = {
                'unknown': GameState.UNKNOWN,
                'loading': GameState.LOADING,
                'menu': GameState.MENU,
                'running': GameState.RUNNING,
                'paused': GameState.PAUSED,
                'game_over': GameState.GAME_OVER,
                'error': GameState.ERROR
            }
            return state_mapping.get(state.lower(), GameState.UNKNOWN)
        
        return GameState.UNKNOWN
    
    def calculate_confidence(self, analysis_data: Dict[str, Any]) -> float:
        """计算分析置信度"""
        try:
            # 基本的置信度计算逻辑
            confidence_factors = []
            
            # 基于找到的元素数量
            elements_found = analysis_data.get('elements_found', [])
            if elements_found:
                confidence_factors.append(min(len(elements_found) * 0.2, 0.8))
            
            # 基于图像质量
            image_quality = analysis_data.get('image_quality', 0.5)
            confidence_factors.append(image_quality)
            
            # 基于匹配度
            match_score = analysis_data.get('match_score', 0.5)
            confidence_factors.append(match_score)
            
            # 计算平均置信度
            if confidence_factors:
                confidence = sum(confidence_factors) / len(confidence_factors)
            else:
                confidence = 0.5
            
            return max(0.0, min(1.0, confidence))
        
        except Exception as e:
            self._handle_error(e, {'operation': 'calculate_confidence'})
            return 0.0
    
    def validate_analysis_result(self, result: AnalysisResult) -> bool:
        """验证分析结果"""
        try:
            # 基本的结果验证
            if not isinstance(result, AnalysisResult):
                return False
            
            # 检查必要字段
            if result.confidence < 0.0 or result.confidence > 1.0:
                return False
            
            if result.timestamp <= 0:
                return False
            
            # 检查数据完整性
            if result.success and not result.data:
                self._log_warning("分析成功但数据为空")
            
            return True
        
        except Exception as e:
            self._handle_error(e, {'operation': 'validate_analysis_result'})
            return False
    
    def clear_cache(self) -> None:
        """清除分析缓存"""
        self._analysis_cache.clear()
        self._last_analysis_time = 0
        self._log_info("分析缓存已清除")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """获取缓存信息"""
        return {
            'cached_results': len(self._analysis_cache),
            'last_analysis_time': self._last_analysis_time,
            'cache_timeout': self._cache_timeout,
            'current_game_state': self._current_game_state.value if self._current_game_state else 'unknown'
        }
    
    def set_cache_timeout(self, timeout: float) -> None:
        """设置缓存超时时间"""
        self._cache_timeout = max(0.1, timeout)
        self._log_info(f"缓存超时时间已设置为: {self._cache_timeout}秒")
    
    def get_analysis_stats(self) -> Dict[str, Any]:
        """获取分析统计信息"""
        return {
            'total_analyses': len(self._analysis_cache),
            'cache_hit_rate': 0.0,  # 需要额外的统计逻辑
            'average_confidence': 0.0,  # 需要额外的统计逻辑
            'current_state': self._current_game_state.value if self._current_game_state else 'unknown',
            'last_analysis': datetime.fromtimestamp(self._last_analysis_time).isoformat() if self._last_analysis_time else None
        }
    
    def is_analysis_valid(self, result: AnalysisResult, min_confidence: float = 0.5) -> bool:
        """检查分析结果是否有效"""
        return (result.success and 
                result.confidence >= min_confidence and 
                self.validate_analysis_result(result))