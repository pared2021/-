"""现代化UI模块"""

from .modern_main_window import ModernMainWindow
from .modern_widgets import (
    ModernCard,
    ModernButton,
    ModernProgressBar,
    ModernControlPanel,
    ModernGameView,
    ModernStatusPanel
)
from .modern_styles import (
    MODERN_APP_STYLE,
    MODERN_DARK_THEME,
    CARD_STYLE,
    ANIMATION_STYLE,
    GAME_THEME_COLORS,
    BREAKPOINTS
)

__all__ = [
    'ModernMainWindow',
    'ModernCard',
    'ModernButton', 
    'ModernProgressBar',
    'ModernControlPanel',
    'ModernGameView',
    'ModernStatusPanel',
    'MODERN_APP_STYLE',
    'MODERN_DARK_THEME',
    'CARD_STYLE',
    'ANIMATION_STYLE',
    'GAME_THEME_COLORS',
    'BREAKPOINTS'
]