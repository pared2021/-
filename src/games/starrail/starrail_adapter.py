"""
崩坏：星穹铁道游戏适配器
实现星穹铁道特定的操作和状态检测
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

from core.game_adapter import GameAdapter, GameWindow, GameState
from core.game_analyzer import GameAnalyzer
from src.services.error_handler import ErrorHandler
from core.task_system import Task, TaskPriority


class StarRailScene(Enum):
    """星穹铁道场景枚举"""

    UNKNOWN = auto()
    LOGIN = auto()
    MAIN_MENU = auto()
    LOADING = auto()
    WORLD = auto()
    BATTLE = auto()
    DIALOGUE = auto()
    CUTSCENE = auto()
    MAP = auto()
    INVENTORY = auto()
    GACHA = auto()
    SIMULATED_UNIVERSE = auto()
    FORGOTTEN_HALL = auto()


@dataclass
class StarRailCharacter:
    """角色信息"""

    name: str
    level: int
    hp: float
    hp_max: float
    energy: float
    energy_max: float
    skills: Dict[str, float]  # 技能名称: 冷却时间


@dataclass
class StarRailBattleInfo:
    """战斗信息"""

    in_battle: bool
    enemy_count: int
    current_character: StarRailCharacter
    team: List[StarRailCharacter]
    turn_index: int
    action_points: int


class StarRailAdapter(GameAdapter):
    """星穹铁道适配器"""

    def __init__(self, data_dir: str):
        """
        初始化星穹铁道适配器

        Args:
            data_dir: 数据目录，存放模板图片等资源
        """
        self.logger = logging.getLogger("StarRailAdapter")
        self.analyzer = GameAnalyzer("starrail", data_dir)
        self.window_title = "崩坏：星穹铁道"

        # 按键映射
        self.key_mapping = {
            "move_forward": "w",
            "move_backward": "s",
            "move_left": "a",
            "move_right": "d",
            "sprint": "shift",
            "interact": "f",
            "skill1": "1",
            "skill2": "2",
            "skill3": "3",
            "skill4": "4",
            "skill5": "5",
            "menu": "esc",
            "map": "m",
            "inventory": "b",
            "technique": "e",
        }

        # 初始化状态
        self.current_scene = StarRailScene.UNKNOWN
        self.battle_info = None
        self.last_scene_check = 0
        self.scene_check_interval = 1.0

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
        current_time = time.time()

        # 定期检查场景
        if current_time - self.last_scene_check >= self.scene_check_interval:
            screenshot = self._capture_window(window)
            self._update_scene(screenshot)
            self.last_scene_check = current_time

        # 在战斗中时更新战斗信息
        if self.current_scene == StarRailScene.BATTLE:
            self._update_battle_info(window)

        return GameState(
            scene=self.current_scene.name,
            battle_info=self.battle_info.__dict__ if self.battle_info else None,
            variables=self._collect_variables(window),
            timestamp=current_time,
        )

    def _update_scene(self, screenshot: np.ndarray):
        """更新场景状态"""
        analysis = self.analyzer.analyze_screenshot(screenshot)

        if "login_button" in analysis["ui_elements"]:
            self.current_scene = StarRailScene.LOGIN
        elif "loading_icon" in analysis["ui_elements"]:
            self.current_scene = StarRailScene.LOADING
        elif "battle_ui" in analysis["ui_elements"]:
            self.current_scene = StarRailScene.BATTLE
        elif "dialogue_box" in analysis["ui_elements"]:
            self.current_scene = StarRailScene.DIALOGUE
        elif "map_full" in analysis["ui_elements"]:
            self.current_scene = StarRailScene.MAP
        elif "inventory_title" in analysis["ui_elements"]:
            self.current_scene = StarRailScene.INVENTORY
        elif "gacha_interface" in analysis["ui_elements"]:
            self.current_scene = StarRailScene.GACHA
        elif "simulated_universe_ui" in analysis["ui_elements"]:
            self.current_scene = StarRailScene.SIMULATED_UNIVERSE
        elif "forgotten_hall_ui" in analysis["ui_elements"]:
            self.current_scene = StarRailScene.FORGOTTEN_HALL
        elif "minimap" in analysis["ui_elements"]:
            self.current_scene = StarRailScene.WORLD

    def _update_battle_info(self, window: GameWindow):
        """更新战斗信息"""
        screenshot = self._capture_window(window)
        analysis = self.analyzer.analyze_screenshot(screenshot)

        current_character = self._parse_character_info(analysis["ui_elements"])
        team = self._parse_team_info(analysis["ui_elements"])

        # 获取回合信息
        turn_index = self._get_turn_index(analysis["ui_elements"])
        action_points = self._get_action_points(analysis["ui_elements"])

        # 检测敌人数量
        enemy_count = self._count_enemies(analysis["ui_elements"])

        self.battle_info = StarRailBattleInfo(
            in_battle=True,
            enemy_count=enemy_count,
            current_character=current_character,
            team=team,
            turn_index=turn_index,
            action_points=action_points,
        )

    def _parse_character_info(self, ui_elements: Dict) -> StarRailCharacter:
        """解析角色信息"""
        try:
            char_info = ui_elements.get("character_info", {})
            return StarRailCharacter(
                name=char_info.get("name", "Unknown"),
                level=int(char_info.get("level", 1)),
                hp=float(char_info.get("hp", 0)),
                hp_max=float(char_info.get("hp_max", 1)),
                energy=float(char_info.get("energy", 0)),
                energy_max=float(char_info.get("energy_max", 100)),
                skills={
                    "basic": float(char_info.get("skill_basic_cd", 0)),
                    "skill": float(char_info.get("skill_battle_cd", 0)),
                    "ultimate": float(char_info.get("skill_ultimate_cd", 0)),
                    "technique": float(char_info.get("skill_technique_cd", 0)),
                },
            )
        except Exception as e:
            self.logger.error(f"解析角色信息失败: {e}", exc_info=True)
            return None

    def _parse_team_info(self, ui_elements: Dict) -> List[StarRailCharacter]:
        """解析队伍信息"""
        team = []
        try:
            for i in range(4):
                char_info = ui_elements.get(f"team_character_{i}", {})
                if char_info:
                    character = StarRailCharacter(
                        name=char_info.get("name", f"Character{i}"),
                        level=int(char_info.get("level", 1)),
                        hp=float(char_info.get("hp", 0)),
                        hp_max=float(char_info.get("hp_max", 1)),
                        energy=float(char_info.get("energy", 0)),
                        energy_max=float(char_info.get("energy_max", 100)),
                        skills={},
                    )
                    team.append(character)
        except Exception as e:
            self.logger.error(f"解析队伍信息失败: {e}", exc_info=True)
        return team

    def _get_turn_index(self, ui_elements: Dict) -> int:
        """获取当前回合索引"""
        try:
            return int(ui_elements.get("turn_index", 1))
        except:
            return 1

    def _get_action_points(self, ui_elements: Dict) -> int:
        """获取行动点数"""
        try:
            return int(ui_elements.get("action_points", 0))
        except:
            return 0

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

        if task_type == "daily_training":
            return self._create_daily_training_task(config)
        elif task_type == "forgotten_hall":
            return self._create_forgotten_hall_task(config)
        elif task_type == "simulated_universe":
            return self._create_simulated_universe_task(config)
        else:
            raise ValueError(f"未知的任务类型: {task_type}")

    def _create_daily_training_task(self, config: Dict) -> Task:
        """创建每日实训任务"""
        return Task(
            name="每日实训",
            priority=TaskPriority.NORMAL,
            actions=[
                lambda: self._teleport_to_training(),
                lambda: self._complete_training(),
                lambda: self._collect_rewards(),
            ],
            conditions={
                "scene": [StarRailScene.WORLD.name],
                "time": lambda: self._is_training_available(),
            },
        )

    def _create_forgotten_hall_task(self, config: Dict) -> Task:
        """创建忘却之庭任务"""
        floor = config.get("floor", 1)

        return Task(
            name=f"忘却之庭 {floor}层",
            priority=TaskPriority.HIGH,
            actions=[
                lambda: self._enter_forgotten_hall(),
                lambda: self._select_floor(floor),
                lambda: self._complete_floor(),
                lambda: self._collect_floor_rewards(),
            ],
            conditions={
                "scene": [StarRailScene.FORGOTTEN_HALL.name],
                "stamina": lambda: self._check_stamina(),
            },
        )

    def _create_simulated_universe_task(self, config: Dict) -> Task:
        """创建模拟宇宙任务"""
        world = config.get("world", 1)
        difficulty = config.get("difficulty", "normal")

        return Task(
            name=f"模拟宇宙 世界{world}",
            priority=TaskPriority.LOW,
            actions=[
                lambda: self._enter_simulated_universe(),
                lambda: self._select_world(world, difficulty),
                lambda: self._explore_universe(),
                lambda: self._collect_universe_rewards(),
            ],
            conditions={
                "scene": [StarRailScene.SIMULATED_UNIVERSE.name],
                "trailblaze_power": lambda: self._check_trailblaze_power(),
            },
        )

    def _is_training_available(self) -> bool:
        """检查实训是否可用"""
        return True  # TODO: 实现具体检查逻辑

    def _check_stamina(self) -> bool:
        """检查体力是否足够"""
        return True  # TODO: 实现具体检查逻辑

    def _check_trailblaze_power(self) -> bool:
        """检查开拓力是否足够"""
        return True  # TODO: 实现具体检查逻辑

    def save_config(self, config: Dict):
        """保存配置"""
        # TODO: 实现配置保存逻辑
        pass
