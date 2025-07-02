"""
API路由模块
包含所有的API路由定义
"""

from .auth import router as auth_router
from .games import router as games_router  
from .vision import router as vision_router
from .automation import router as automation_router
from .health import router as health_router
from .websocket import router as websocket_router

__all__ = [
    "auth_router",
    "games_router", 
    "vision_router",
    "automation_router",
    "health_router",
    "websocket_router"
] 