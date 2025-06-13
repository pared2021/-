from enum import Enum, auto
from typing import Dict, Any, Optional
from dataclasses import dataclass
import time

class ErrorCode(Enum):
    """错误码枚举"""
    # 系统级错误 (1000-1999)
    SYSTEM_ERROR = 1000
    CONFIG_ERROR = 1001
    RESOURCE_ERROR = 1002
    
    # 窗口相关错误 (2000-2999)
    WINDOW_ERROR = 2000
    WINDOW_NOT_FOUND = 2001
    WINDOW_CAPTURE_ERROR = 2002
    WINDOW_STATE_ERROR = 2003
    
    # 图像处理错误 (3000-3999)
    IMAGE_PROCESSING_ERROR = 3000
    IMAGE_CAPTURE_ERROR = 3001
    IMAGE_ANALYSIS_ERROR = 3002
    
    # 动作执行错误 (4000-4999)
    ACTION_ERROR = 4000
    KEYBOARD_ERROR = 4001
    MOUSE_ERROR = 4002
    
    # 游戏状态错误 (5000-5999)
    STATE_ERROR = 5000
    STATE_VALIDATION_ERROR = 5001
    STATE_TRANSITION_ERROR = 5002
    
    # 模型相关错误 (6000-6999)
    MODEL_ERROR = 6000
    MODEL_LOAD_ERROR = 6001
    MODEL_PREDICTION_ERROR = 6002

@dataclass
class ErrorContext:
    """错误上下文信息"""
    timestamp: float = time.time()
    source: str = ""
    details: Dict[str, Any] = None
    stack_trace: Optional[str] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}

class GameAutomationError(Exception):
    """游戏自动化基础错误类"""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        context: Optional[ErrorContext] = None
    ):
        self.message = message
        self.error_code = error_code
        self.context = context or ErrorContext()
        super().__init__(self.message)
    
    def __str__(self) -> str:
        return f"[{self.error_code.name}] {self.message}"

class WindowError(GameAutomationError):
    """窗口相关错误"""
    def __init__(self, message: str, error_code: ErrorCode, context: Optional[ErrorContext] = None):
        super().__init__(message, error_code, context)

class ImageProcessingError(GameAutomationError):
    """图像处理相关错误"""
    def __init__(self, message: str, error_code: ErrorCode, context: Optional[ErrorContext] = None):
        super().__init__(message, error_code, context)

class ActionError(GameAutomationError):
    """动作执行相关错误"""
    def __init__(self, message: str, error_code: ErrorCode, context: Optional[ErrorContext] = None):
        super().__init__(message, error_code, context)

class StateError(GameAutomationError):
    """状态相关错误"""
    def __init__(self, message: str, error_code: ErrorCode, context: Optional[ErrorContext] = None):
        super().__init__(message, error_code, context)

class ModelError(GameAutomationError):
    """模型相关错误"""
    def __init__(self, message: str, error_code: ErrorCode, context: Optional[ErrorContext] = None):
        super().__init__(message, error_code, context)

# 错误类型映射
ERROR_TYPE_MAP = {
    ErrorCode.WINDOW_ERROR: WindowError,
    ErrorCode.WINDOW_NOT_FOUND: WindowError,
    ErrorCode.WINDOW_CAPTURE_ERROR: WindowError,
    ErrorCode.WINDOW_STATE_ERROR: WindowError,
    ErrorCode.IMAGE_PROCESSING_ERROR: ImageProcessingError,
    ErrorCode.IMAGE_CAPTURE_ERROR: ImageProcessingError,
    ErrorCode.IMAGE_ANALYSIS_ERROR: ImageProcessingError,
    ErrorCode.ACTION_ERROR: ActionError,
    ErrorCode.KEYBOARD_ERROR: ActionError,
    ErrorCode.MOUSE_ERROR: ActionError,
    ErrorCode.STATE_ERROR: StateError,
    ErrorCode.STATE_VALIDATION_ERROR: StateError,
    ErrorCode.STATE_TRANSITION_ERROR: StateError,
    ErrorCode.MODEL_ERROR: ModelError,
    ErrorCode.MODEL_LOAD_ERROR: ModelError,
    ErrorCode.MODEL_PREDICTION_ERROR: ModelError,
} 