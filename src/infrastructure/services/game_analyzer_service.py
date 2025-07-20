"""
游戏分析器服务实现

基于现有UnifiedGameAnalyzer的Clean Architecture实现
整合传统计算机视觉和深度学习方法
"""
from typing import Dict, Any, Optional, List
import numpy as np
import time
from dependency_injector.wiring import inject, Provide
from typing import TYPE_CHECKING

from ...core.interfaces.services import IGameAnalyzer, AnalysisResult
from ...core.interfaces.repositories import IConfigRepository, ITemplateRepository
from ...core.interfaces.adapters import IWindowAdapter

if TYPE_CHECKING:
    from ...application.containers.main_container import MainContainer

# 导入现有的分析器实现
from ...core.unified_game_analyzer import UnifiedGameAnalyzer


class GameAnalyzerService(IGameAnalyzer):
    """
    游戏分析器服务实现
    
    封装现有的UnifiedGameAnalyzer，提供Clean Architecture接口
    """
    
    @inject
    def __init__(self,
                 config_repository: IConfigRepository = Provide['config_repository'],
                 template_repository: ITemplateRepository = Provide['template_repository'],
                 window_adapter: IWindowAdapter = Provide['window_adapter']):
        self._config_repository = config_repository
        self._template_repository = template_repository
        self._window_adapter = window_adapter
        self._analyzer = None
        self._current_game_id = None
        self._initialized = False
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化分析器"""
        try:
            # 创建UnifiedGameAnalyzer实例
            self._analyzer = UnifiedGameAnalyzer()
            
            # 从配置仓储获取配置
            analyzer_config = self._config_repository.get_config('game_analyzer', {})
            
            # 合并传入的配置
            merged_config = {**analyzer_config, **config}
            
            # 初始化底层分析器
            if hasattr(self._analyzer, 'initialize'):
                success = self._analyzer.initialize(merged_config)
            else:
                # 如果没有initialize方法，尝试直接设置配置
                success = self._setup_analyzer_config(merged_config)
            
            self._initialized = success
            return success
            
        except Exception as e:
            self._log_error(f"Failed to initialize game analyzer: {str(e)}")
            return False
    
    def analyze_frame(self, frame: np.ndarray) -> AnalysisResult:
        """分析游戏帧"""
        if not self._initialized:
            return AnalysisResult(
                status="error",
                confidence=0.0,
                data={"error": "Analyzer not initialized"},
                timestamp=time.time()
            )
        
        try:
            # 使用现有的分析器进行分析
            result = self._analyzer.analyze_frame(frame)
            
            # 转换为标准的AnalysisResult格式
            return self._convert_to_analysis_result(result)
            
        except Exception as e:
            self._log_error(f"Frame analysis failed: {str(e)}")
            return AnalysisResult(
                status="error",
                confidence=0.0,
                data={"error": str(e)},
                timestamp=time.time()
            )
    
    def detect_game_state(self, frame: np.ndarray) -> Dict[str, Any]:
        """检测游戏状态"""
        if not self._initialized:
            return {"error": "Analyzer not initialized"}
        
        try:
            if hasattr(self._analyzer, 'detect_game_state'):
                return self._analyzer.detect_game_state(frame)
            else:
                # 如果没有专门的方法，使用通用分析
                result = self.analyze_frame(frame)
                return {"state": result.status, "confidence": result.confidence}
                
        except Exception as e:
            self._log_error(f"Game state detection failed: {str(e)}")
            return {"error": str(e)}
    
    def find_elements(self, frame: np.ndarray, elements: List[str]) -> Dict[str, Any]:
        """查找界面元素"""
        if not self._initialized:
            return {"error": "Analyzer not initialized"}
        
        try:
            results = {}
            
            for element in elements:
                # 从模板仓储获取元素模板
                template = self._template_repository.get_template(element)
                if template:
                    # 使用模板匹配查找元素
                    matches = self._find_element_by_template(frame, template)
                    results[element] = matches
                else:
                    results[element] = {"error": f"Template not found for {element}"}
            
            return results
            
        except Exception as e:
            self._log_error(f"Element finding failed: {str(e)}")
            return {"error": str(e)}
    
    def get_supported_games(self) -> List[str]:
        """获取支持的游戏列表"""
        try:
            if hasattr(self._analyzer, 'get_supported_games'):
                return self._analyzer.get_supported_games()
            else:
                # 从配置中获取支持的游戏列表
                return self._config_repository.get_config('supported_games', [
                    'genshin', 'starrail', 'zzz', 'arknights'
                ])
        except Exception as e:
            self._log_error(f"Failed to get supported games: {str(e)}")
            return []
    
    def set_game_context(self, game_id: str) -> bool:
        """设置游戏上下文"""
        try:
            if hasattr(self._analyzer, 'set_game_context'):
                success = self._analyzer.set_game_context(game_id)
            else:
                # 简单的游戏上下文设置
                success = self._setup_game_context(game_id)
            
            if success:
                self._current_game_id = game_id
            
            return success
            
        except Exception as e:
            self._log_error(f"Failed to set game context: {str(e)}")
            return False
    
    def cleanup(self) -> None:
        """清理资源"""
        try:
            if self._analyzer and hasattr(self._analyzer, 'cleanup'):
                self._analyzer.cleanup()
            
            self._analyzer = None
            self._current_game_id = None
            self._initialized = False
            
        except Exception as e:
            self._log_error(f"Cleanup failed: {str(e)}")
    
    def _convert_to_analysis_result(self, result: Any) -> AnalysisResult:
        """转换分析结果为标准格式"""
        if isinstance(result, dict):
            return AnalysisResult(
                status=result.get('status', 'unknown'),
                confidence=result.get('confidence', 0.0),
                data=result.get('data', result),
                timestamp=result.get('timestamp', time.time())
            )
        else:
            # 处理其他类型的结果
            return AnalysisResult(
                status='success',
                confidence=1.0,
                data={'result': result},
                timestamp=time.time()
            )
    
    def _setup_analyzer_config(self, config: Dict[str, Any]) -> bool:
        """设置分析器配置"""
        try:
            # 设置分析器的基本配置
            for key, value in config.items():
                if hasattr(self._analyzer, key):
                    setattr(self._analyzer, key, value)
            return True
        except Exception as e:
            self._log_error(f"Config setup failed: {str(e)}")
            return False
    
    def _setup_game_context(self, game_id: str) -> bool:
        """设置游戏上下文"""
        try:
            # 从配置中获取游戏特定的设置
            game_config = self._config_repository.get_config(f'games.{game_id}', {})
            
            # 应用游戏特定的配置
            if game_config:
                return self._setup_analyzer_config(game_config)
            
            return True
            
        except Exception as e:
            self._log_error(f"Game context setup failed: {str(e)}")
            return False
    
    def _find_element_by_template(self, frame: np.ndarray, template: Dict[str, Any]) -> Dict[str, Any]:
        """通过模板查找元素"""
        try:
            # 获取模板图像
            template_image = self._template_repository.get_template_image(template.get('id', ''))
            
            if template_image is None:
                return {"error": "Template image not found"}
            
            # 使用现有的模板匹配功能
            if hasattr(self._analyzer, 'template_match'):
                matches = self._analyzer.template_match(frame, template_image)
                return {"matches": matches}
            else:
                # 简单的模板匹配实现
                return {"matches": [], "note": "Template matching not implemented"}
                
        except Exception as e:
            self._log_error(f"Template matching failed: {str(e)}")
            return {"error": str(e)}
    
    def _log_error(self, message: str) -> None:
        """记录错误日志"""
        try:
            # 这里可以使用日志服务记录错误
            print(f"[GameAnalyzerService] ERROR: {message}")
        except:
            pass  # 避免日志记录失败影响主要功能