"""
ZZZ (Zenless Zone Zero) Automation Module
"""

from .battle import battle_system
from .service import battle_service
from .scheduler.base_scheduler import BaseScheduler
from src.services.config import Config as ConfigManager

__version__ = "1.0.0"
__all__ = ["battle_system", "battle_service", "BaseScheduler", "ConfigManager"]
