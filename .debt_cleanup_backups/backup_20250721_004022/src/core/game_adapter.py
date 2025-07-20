"""
游戏适配器接口
定义了游戏自动化所需的基本接口
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any
from dataclasses import dataclass
import numpy as np


@dataclass
class GameWindow:
    """游戏窗口信息"""

    title: str
    handle: int
    rect: tuple  # (x, y, width, height)
    process_id: int


@dataclass
class GameState:
    """游戏状态信息"""

    scene: str  # 当前场景
    ui_elements: Dict[str, Dict]  # UI元素位置和状态
    variables: Dict[str, Any]  # 游戏变量
    timestamp: float  # 状态时间戳


class GameAdapter(ABC):
    """游戏适配器基类"""

    @abstractmethod
    def detect_game_window(self) -> List[GameWindow]:
        """
        检测游戏窗口

        Returns:
            List[GameWindow]: 检测到的游戏窗口列表
        """

    @abstractmethod
    def get_game_state(self, window: GameWindow) -> GameState:
        """
        获取游戏状态

        Args:
            window: 游戏窗口信息

        Returns:
            GameState: 当前游戏状态
        """

    @abstractmethod
    def analyze_scene(self, screenshot: np.ndarray) -> str:
        """
        分析游戏场景

        Args:
            screenshot: 游戏截图

        Returns:
            str: 场景标识
        """

    @abstractmethod
    def collect_ui_info(self, window: GameWindow) -> Dict[str, Dict]:
        """
        收集UI信息

        Args:
            window: 游戏窗口信息

        Returns:
            Dict[str, Dict]: UI元素信息
        """

    @abstractmethod
    def get_action_template(self) -> Dict:
        """
        获取动作模板

        Returns:
            Dict: 支持的动作类型和参数
        """

    @abstractmethod
    def execute_action(self, window: GameWindow, action: str, params: Dict) -> bool:
        """
        执行动作

        Args:
            window: 游戏窗口信息
            action: 动作类型
            params: 动作参数

        Returns:
            bool: 是否执行成功
        """

    @abstractmethod
    def is_action_valid(self, state: GameState, action: str, params: Dict) -> bool:
        """
        检查动作是否有效

        Args:
            state: 当前游戏状态
            action: 动作类型
            params: 动作参数

        Returns:
            bool: 动作是否有效
        """
