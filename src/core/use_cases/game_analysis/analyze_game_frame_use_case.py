"""
游戏帧分析用例

遵循Clean Architecture原则的用例实现
封装业务逻辑，不依赖于外部实现细节
"""
from typing import Dict, Any, Optional
import numpy as np
from dataclasses import dataclass
from dependency_injector.wiring import inject, Provide
from typing import TYPE_CHECKING

from ...interfaces.services import IGameAnalyzer, AnalysisResult
from ...interfaces.repositories import IConfigRepository

if TYPE_CHECKING:
    from src.application.containers.main_container import MainContainer


@dataclass
class AnalyzeGameFrameRequest:
    """游戏帧分析请求"""
    frame: np.ndarray
    game_id: str
    options: Optional[Dict[str, Any]] = None


@dataclass
class AnalyzeGameFrameResponse:
    """游戏帧分析响应"""
    success: bool
    result: Optional[AnalysisResult] = None
    error_message: Optional[str] = None


class AnalyzeGameFrameUseCase:
    """游戏帧分析用例"""
    
    @inject
    def __init__(self,
                 game_analyzer: IGameAnalyzer = Provide['game_analyzer'],
                 config_repository: IConfigRepository = Provide['config_repository']):
        self._game_analyzer = game_analyzer
        self._config_repository = config_repository
    
    def execute(self, request: AnalyzeGameFrameRequest) -> AnalyzeGameFrameResponse:
        """
        执行游戏帧分析用例
        
        Args:
            request: 分析请求
            
        Returns:
            AnalyzeGameFrameResponse: 分析结果
        """
        try:
            # 1. 验证输入
            if not self._validate_request(request):
                return AnalyzeGameFrameResponse(
                    success=False,
                    error_message="Invalid request parameters"
                )
            
            # 2. 设置游戏上下文
            if not self._game_analyzer.set_game_context(request.game_id):
                return AnalyzeGameFrameResponse(
                    success=False,
                    error_message=f"Failed to set game context for {request.game_id}"
                )
            
            # 3. 执行分析
            result = self._game_analyzer.analyze_frame(request.frame)
            
            # 4. 后处理结果
            processed_result = self._post_process_result(result, request.options)
            
            return AnalyzeGameFrameResponse(
                success=True,
                result=processed_result
            )
            
        except Exception as e:
            return AnalyzeGameFrameResponse(
                success=False,
                error_message=f"Analysis failed: {str(e)}"
            )
    
    def _validate_request(self, request: AnalyzeGameFrameRequest) -> bool:
        """验证请求参数"""
        if request.frame is None or request.frame.size == 0:
            return False
        
        if not request.game_id:
            return False
        
        # 检查游戏是否支持
        supported_games = self._game_analyzer.get_supported_games()
        if request.game_id not in supported_games:
            return False
        
        return True
    
    def _post_process_result(self, 
                           result: AnalysisResult, 
                           options: Optional[Dict[str, Any]]) -> AnalysisResult:
        """后处理分析结果"""
        if not options:
            return result
        
        # 根据配置和选项调整结果
        min_confidence = options.get('min_confidence', 0.5)
        if result.confidence < min_confidence:
            result.status = 'low_confidence'
        
        # 添加额外的元数据
        if 'add_metadata' in options:
            result.data['metadata'] = {
                'processing_options': options,
                'timestamp': result.timestamp
            }
        
        return result


# 便捷函数
def analyze_game_frame(frame: np.ndarray, 
                      game_id: str, 
                      options: Optional[Dict[str, Any]] = None) -> AnalyzeGameFrameResponse:
    """
    分析游戏帧的便捷函数
    
    Args:
        frame: 游戏帧图像
        game_id: 游戏ID
        options: 分析选项
        
    Returns:
        AnalyzeGameFrameResponse: 分析结果
    """
    use_case = AnalyzeGameFrameUseCase()
    request = AnalyzeGameFrameRequest(frame=frame, game_id=game_id, options=options)
    return use_case.execute(request)