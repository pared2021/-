"""
自定义异常类
提供业务异常和错误码管理
"""

from datetime import datetime
from typing import Any, Dict, Optional


class GameAutomationException(Exception):
    """游戏自动化基础异常"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "UNKNOWN_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        self.timestamp = datetime.utcnow()
        super().__init__(self.message)


class ConfigurationError(GameAutomationException):
    """配置错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            status_code=500,
            details=details
        )


class ServiceUnavailableError(GameAutomationException):
    """服务不可用错误"""
    
    def __init__(self, service_name: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"服务 {service_name} 不可用",
            error_code="SERVICE_UNAVAILABLE",
            status_code=503,
            details=details
        )


class AuthenticationError(GameAutomationException):
    """认证错误"""
    
    def __init__(self, message: str = "认证失败", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=401,
            details=details
        )


class AuthorizationError(GameAutomationException):
    """授权错误"""
    
    def __init__(self, message: str = "权限不足", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR", 
            status_code=403,
            details=details
        )


class ValidationError(GameAutomationException):
    """验证错误"""
    
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        error_details = details or {}
        if field:
            error_details["field"] = field
        
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=422,
            details=error_details
        )


class NotFoundError(GameAutomationException):
    """资源未找到错误"""
    
    def __init__(self, resource: str, resource_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        message = f"{resource} 未找到"
        if resource_id:
            message += f" (ID: {resource_id})"
        
        error_details = details or {}
        error_details.update({"resource": resource})
        if resource_id:
            error_details["resource_id"] = resource_id
        
        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            status_code=404,
            details=error_details
        )


class GameNotFoundError(NotFoundError):
    """游戏未找到错误"""
    
    def __init__(self, game_name: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            resource="游戏",
            resource_id=game_name,
            details=details
        )


class GameNotRunningError(GameAutomationException):
    """游戏未运行错误"""
    
    def __init__(self, game_name: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"游戏 {game_name} 未运行",
            error_code="GAME_NOT_RUNNING",
            status_code=409,
            details=details
        )


class VisionError(GameAutomationException):
    """视觉处理错误"""
    
    def __init__(self, message: str, operation: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        error_details = details or {}
        if operation:
            error_details["operation"] = operation
        
        super().__init__(
            message=message,
            error_code="VISION_ERROR",
            status_code=422,
            details=error_details
        )


class TemplateMatchError(VisionError):
    """模板匹配错误"""
    
    def __init__(self, template_name: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"模板匹配失败: {template_name}",
            operation="template_match",
            details=details
        )


class OCRError(VisionError):
    """OCR识别错误"""
    
    def __init__(self, message: str = "OCR识别失败", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            operation="ocr",
            details=details
        )


class AutomationError(GameAutomationException):
    """自动化执行错误"""
    
    def __init__(self, message: str, task_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        error_details = details or {}
        if task_id:
            error_details["task_id"] = task_id
        
        super().__init__(
            message=message,
            error_code="AUTOMATION_ERROR",
            status_code=422,
            details=error_details
        )


class TaskNotFoundError(NotFoundError):
    """任务未找到错误"""
    
    def __init__(self, task_id: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            resource="自动化任务",
            resource_id=task_id,
            details=details
        )


class TaskExecutionError(AutomationError):
    """任务执行错误"""
    
    def __init__(self, task_id: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"任务执行失败: {message}",
            task_id=task_id,
            details=details
        )


class RateLimitError(GameAutomationException):
    """限流错误"""
    
    def __init__(self, message: str = "请求频率过高", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT",
            status_code=429,
            details=details
        )


__all__ = [
    "GameAutomationException",
    "ConfigurationError",
    "ServiceUnavailableError",
    "AuthenticationError",
    "AuthorizationError",
    "ValidationError",
    "NotFoundError",
    "GameNotFoundError",
    "GameNotRunningError",
    "VisionError",
    "TemplateMatchError",
    "OCRError",
    "AutomationError",
    "TaskNotFoundError",
    "TaskExecutionError",
    "RateLimitError"
] 