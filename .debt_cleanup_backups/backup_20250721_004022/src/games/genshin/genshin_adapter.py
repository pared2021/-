"""
原神游戏适配器
实现原神特定的操作和状态检测
"""
from typing import Dict, List, Optional, Any
import cv2
import numpy as np
import time
import logging
import win32gui
import win32con
import win32api
import win32ui
from ctypes import windll
from dataclasses import dataclass
from enum import Enum, auto

from src.core.game_adapter import GameAdapter, GameWindow, GameState
from src.core.unified_game_analyzer import UnifiedGameAnalyzer as GameAnalyzer
from src.services.error_handler import ErrorHandler
from src.core.task_system import Task, TaskPriority


class GenshinScene(Enum):
    """原神场景枚举"""

    UNKNOWN = auto()
    LOGIN = auto()
    MAIN_MENU = auto()
    LOADING = auto()
    WORLD = auto()
    DOMAIN = auto()
    BATTLE = auto()
    DIALOGUE = auto()
    CUTSCENE = auto()
    MAP = auto()
    INVENTORY = auto()
    WISH = auto()


@dataclass
class GenshinCharacter:
    """角色信息"""

    name: str
    level: int
    hp: float
    hp_max: float
    energy: float
    energy_max: float
    skills: Dict[str, float]  # 技能名称: 冷却时间


@dataclass
class GenshinBattleInfo:
    """战斗信息"""

    in_battle: bool
    enemy_count: int
    current_character: GenshinCharacter
    party: List[GenshinCharacter]


class GenshinAdapter(GameAdapter):
    """原神适配器"""

    def __init__(self, data_dir: str):
        """
        初始化原神适配器

        Args:
            data_dir: 数据目录，存放模板图片等资源
        """
        self.logger = logging.getLogger("GenshinAdapter")
        self.analyzer = GameAnalyzer("genshin", data_dir)
        self.window_title = "原神"

        # 按键映射
        self.key_mapping = {
            "move_forward": "w",
            "move_backward": "s",
            "move_left": "a",
            "move_right": "d",
            "jump": "space",
            "sprint": "shift",
            "attack": "j",
            "skill": "e",
            "burst": "q",
            "character1": "1",
            "character2": "2",
            "character3": "3",
            "character4": "4",
            "menu": "esc",
            "map": "m",
            "inventory": "b",
        }

        # 初始化状态
        self.current_scene: GenshinScene = GenshinScene.UNKNOWN
        self.battle_info: Optional[GenshinBattleInfo] = None
        self.last_scene_check: float = 0
        self.scene_check_interval: float = 1.0  # 场景检测间隔

    def detect_game_window(self) -> List[GameWindow]:
        """检测游戏窗口"""
        windows = []

        def enum_window(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if self.window_title in title:
                    rect = win32gui.GetWindowRect(hwnd)
                    process_id = win32process.GetWindowThreadProcessId(hwnd)[1]
                    windows.append(
                        GameWindow(
                            title=title, handle=hwnd, rect=rect, process_id=process_id
                        )
                    )

        win32gui.EnumWindows(enum_window, windows)
        return windows

    def get_game_state(self, window: GameWindow) -> GameState:
        """获取游戏状态"""
        current_time: float = time.time()

        # 定期检查场景
        if current_time - self.last_scene_check >= self.scene_check_interval:
            screenshot = self._capture_window(window)
            self._update_scene(screenshot)
            self.last_scene_check = current_time

        # 在战斗中时更新战斗信息
        if self.current_scene == GenshinScene.BATTLE:
            self._update_battle_info(window)

        return GameState(
            scene=self.current_scene.name,
            battle_info=self.battle_info.__dict__ if self.battle_info else None,
            variables=self._collect_variables(window),
            timestamp=current_time,
        )

    def _update_scene(self, screenshot: np.ndarray):
        """更新场景状态"""
        # 使用模板匹配检测UI元素
        analysis = self.analyzer.analyze_screenshot(screenshot)

        # 根据UI元素判断场景
        if "login_button" in analysis["ui_elements"]:
            self.current_scene = GenshinScene.LOGIN
        elif "loading_icon" in analysis["ui_elements"]:
            self.current_scene = GenshinScene.LOADING
        elif "minimap" in analysis["ui_elements"]:
            if "enemy_hp_bar" in analysis["ui_elements"]:
                self.current_scene = GenshinScene.BATTLE
            else:
                self.current_scene = GenshinScene.WORLD
        elif "dialogue_box" in analysis["ui_elements"]:
            self.current_scene = GenshinScene.DIALOGUE
        elif "map_full" in analysis["ui_elements"]:
            self.current_scene = GenshinScene.MAP
        elif "inventory_title" in analysis["ui_elements"]:
            self.current_scene = GenshinScene.INVENTORY
        elif "wish_interface" in analysis["ui_elements"]:
            self.current_scene = GenshinScene.WISH
        elif "domain_challenge" in analysis["ui_elements"]:
            self.current_scene = GenshinScene.DOMAIN
        else:
            # 如果没有明显特征，保持当前场景
            pass

    def _update_battle_info(self, window: GameWindow):
        """更新战斗信息"""
        screenshot = self._capture_window(window)
        analysis = self.analyzer.analyze_screenshot(screenshot)

        # 解析角色信息
        current_character = self._parse_character_info(analysis["ui_elements"])
        party = self._parse_party_info(analysis["ui_elements"])

        # 检测敌人数量
        enemy_count = self._count_enemies(analysis["ui_elements"])

        self.battle_info = GenshinBattleInfo(
            in_battle=True,
            enemy_count=enemy_count,
            current_character=current_character,
            party=party,
        )

    def _parse_character_info(self, ui_elements: Dict) -> GenshinCharacter:
        """解析角色信息"""
        try:
            char_info = ui_elements.get("character_info", {})
            return GenshinCharacter(
                name=char_info.get("name", "Unknown"),
                level=int(char_info.get("level", 1)),
                hp=float(char_info.get("hp", 0)),
                hp_max=float(char_info.get("hp_max", 1)),
                energy=float(char_info.get("energy", 0)),
                energy_max=float(char_info.get("energy_max", 100)),
                skills={
                    "normal": float(char_info.get("skill_normal_cd", 0)),
                    "skill": float(char_info.get("skill_elemental_cd", 0)),
                    "burst": float(char_info.get("skill_burst_cd", 0)),
                },
            )
        except Exception as e:
            self.logger.error(f"解析角色信息失败: {e}", exc_info=True)
            return None

    def _parse_party_info(self, ui_elements: Dict) -> List[GenshinCharacter]:
        """解析队伍信息"""
        party = []
        try:
            for i in range(4):
                char_info = ui_elements.get(f"party_character_{i}", {})
                if char_info:
                    character = GenshinCharacter(
                        name=char_info.get("name", f"Character{i}"),
                        level=int(char_info.get("level", 1)),
                        hp=float(char_info.get("hp", 0)),
                        hp_max=float(char_info.get("hp_max", 1)),
                        energy=float(char_info.get("energy", 0)),
                        energy_max=float(char_info.get("energy_max", 100)),
                        skills={},  # 队伍中其他角色不需要技能CD信息
                    )
                    party.append(character)
        except Exception as e:
            self.logger.error(f"解析队伍信息失败: {e}", exc_info=True)
        return party

    def _count_enemies(self, ui_elements: Dict) -> int:
        """计算敌人数量"""
        try:
            enemy_bars = [
                k for k in ui_elements.keys() if k.startswith("enemy_hp_bar_")
            ]
            return len(enemy_bars)
        except Exception as e:
            self.logger.error(f"计算敌人数量失败: {e}", exc_info=True)
            return 0

    def create_task(self, config: Dict) -> Task:
        """创建任务"""
        task_type = config.get("type", "")

        if task_type == "daily_commission":
            return self._create_daily_commission_task(config)
        elif task_type == "domain_farming":
            return self._create_domain_farming_task(config)
        elif task_type == "exploration":
            return self._create_exploration_task(config)
        else:
            raise ValueError(f"未知的任务类型: {task_type}")

    def _create_daily_commission_task(self, config: Dict) -> Task:
        """创建每日委托任务"""
        return Task(
            name="每日委托",
            priority=TaskPriority.NORMAL,
            actions=[
                lambda: self._teleport_to_commission(),
                lambda: self._complete_commission(),
                lambda: self._collect_rewards(),
            ],
            conditions={
                "scene": [GenshinScene.WORLD.name],
                "time": lambda: self._is_commission_available(),
            },
        )

    def _create_domain_farming_task(self, config: Dict) -> Task:
        """创建副本刷取任务"""
        domain_name = config.get("domain", "")
        runs = config.get("runs", 1)

        return Task(
            name=f"刷取{domain_name}",
            priority=TaskPriority.LOW,
            actions=[
                lambda: self._teleport_to_domain(domain_name),
                lambda: self._enter_domain(),
                lambda: self._complete_domain(),
                lambda: self._collect_domain_rewards(),
            ]
            * runs,
            conditions={
                "scene": [GenshinScene.WORLD.name, GenshinScene.DOMAIN.name],
                "resin": lambda: self._check_resin(),
            },
        )

    def _create_exploration_task(self, config: Dict) -> Task:
        """创建探索任务"""
        region = config.get("region", "")
        targets = config.get("targets", [])

        return Task(
            name=f"探索{region}",
            priority=TaskPriority.LOW,
            actions=[
                lambda: self._teleport_to_region(region),
                lambda: self._explore_region(targets),
            ],
            conditions={
                "scene": [GenshinScene.WORLD.name],
                "stamina": lambda: self._check_stamina(),
            },
        )

    def _is_commission_available(self) -> bool:
        """检查委托是否可用"""
        return True  # TODO: 实现具体检查逻辑

    def _check_resin(self) -> bool:
        """检查树脂是否足够"""
        return True  # TODO: 实现具体检查逻辑

    def _check_stamina(self) -> bool:
        """检查体力是否足够"""
        return True  # TODO: 实现具体检查逻辑

    def save_config(self, config: Dict):
        """保存配置"""
        # TODO: 实现配置保存逻辑
        pass
