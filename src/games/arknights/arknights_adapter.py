"""
明日方舟游戏适配器
"""
from ctypes import windll
from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List, Optional, Any

import logging
import time
import win32process

import cv2
import numpy as np
import pyautogui
import win32con
import win32gui
import win32ui

from core.game_adapter import GameAdapter, GameWindow, GameState
from core.game_analyzer import GameAnalyzer
from src.services.error_handler import ErrorHandler
from core.task_system import TaskSystem, Task, TaskPriority


class ArknightsScene(Enum):
    """明日方舟场景枚举"""

    UNKNOWN = auto()
    LOGIN = auto()
    MAIN_MENU = auto()
    LOADING = auto()
    BATTLE = auto()
    BATTLE_PREPARATION = auto()
    BATTLE_RESULT = auto()
    TERMINAL = auto()
    BASE = auto()
    SHOP = auto()
    RECRUIT = auto()
    INFRASTRUCTURE = auto()


@dataclass
class ArknightsBattleInfo:
    """战斗信息"""

    in_battle: bool
    cost: int
    max_cost: int
    life_points: int
    deployed_operators: List[str]
    available_skills: Dict[str, bool]  # 技能名称: 是否可用


@dataclass
class ArknightsBaseInfo:
    """基建信息"""

    rooms: Dict[str, Dict]  # 房间名称: 房间信息
    operators: Dict[str, Dict]  # 干员名称: 干员信息
    resources: Dict[str, float]  # 资源名称: 数量


class ArknightsAdapter(GameAdapter):
    """明日方舟适配器"""

    def __init__(self, data_dir: str):
        """
        初始化明日方舟适配器

        Args:
            data_dir: 数据目录，存放模板图片等资源
        """
        self.logger = logging.getLogger("ArknightsAdapter")
        self.analyzer = GameAnalyzer("arknights", data_dir)
        self.window_title = "明日方舟"

        # 初始化状态
        self.current_scene = ArknightsScene.UNKNOWN
        self.battle_info = None
        self.base_info = None
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

        # 根据场景更新信息
        if self.current_scene == ArknightsScene.BATTLE:
            self._update_battle_info(window)
        elif self.current_scene == ArknightsScene.BASE:
            self._update_base_info(window)

        return GameState(
            scene=self.current_scene.name,
            battle_info=self.battle_info.__dict__ if self.battle_info else None,
            base_info=self.base_info.__dict__ if self.base_info else None,
            variables=self._collect_variables(window),
            timestamp=current_time,
        )

    def _update_scene(self, screenshot: np.ndarray):
        """更新场景状态"""
        analysis = self.analyzer.analyze_screenshot(screenshot)

        if "login_button" in analysis["ui_elements"]:
            self.current_scene = ArknightsScene.LOGIN
        elif "loading_icon" in analysis["ui_elements"]:
            self.current_scene = ArknightsScene.LOADING
        elif "battle_cost" in analysis["ui_elements"]:
            self.current_scene = ArknightsScene.BATTLE
        elif "battle_start" in analysis["ui_elements"]:
            self.current_scene = ArknightsScene.BATTLE_PREPARATION
        elif "battle_result" in analysis["ui_elements"]:
            self.current_scene = ArknightsScene.BATTLE_RESULT
        elif "terminal_title" in analysis["ui_elements"]:
            self.current_scene = ArknightsScene.TERMINAL
        elif "base_title" in analysis["ui_elements"]:
            self.current_scene = ArknightsScene.BASE
        elif "shop_title" in analysis["ui_elements"]:
            self.current_scene = ArknightsScene.SHOP
        elif "recruit_title" in analysis["ui_elements"]:
            self.current_scene = ArknightsScene.RECRUIT
        elif "infrastructure_title" in analysis["ui_elements"]:
            self.current_scene = ArknightsScene.INFRASTRUCTURE

    def _update_battle_info(self, window: GameWindow):
        """更新战斗信息"""
        screenshot = self._capture_window(window)
        analysis = self.analyzer.analyze_screenshot(screenshot)

        try:
            battle_ui = analysis["ui_elements"].get("battle_ui", {})

            # 解析战斗信息
            cost = int(battle_ui.get("cost", "0"))
            max_cost = int(battle_ui.get("max_cost", "99"))
            life_points = int(battle_ui.get("life_points", "0"))

            # 获取已部署干员
            deployed = []
            for key in battle_ui:
                if key.startswith("operator_"):
                    deployed.append(battle_ui[key].get("name", "Unknown"))

            # 检查技能可用性
            skills = {}
            for key in battle_ui:
                if key.startswith("skill_"):
                    skill_name = battle_ui[key].get("name", "Unknown")
                    skill_ready = battle_ui[key].get("ready", False)
                    skills[skill_name] = skill_ready

            self.battle_info = ArknightsBattleInfo(
                in_battle=True,
                cost=cost,
                max_cost=max_cost,
                life_points=life_points,
                deployed_operators=deployed,
                available_skills=skills,
            )

        except Exception as e:
            self.logger.error(f"更新战斗信息失败: {e}", exc_info=True)

    def _update_base_info(self, window: GameWindow):
        """更新基建信息"""
        screenshot = self._capture_window(window)
        analysis = self.analyzer.analyze_screenshot(screenshot)

        try:
            base_ui = analysis["ui_elements"].get("base_ui", {})

            # 解析房间信息
            rooms = {}
            for key in base_ui:
                if key.startswith("room_"):
                    room_info = base_ui[key]
                    rooms[room_info["name"]] = {
                        "level": room_info.get("level", 1),
                        "operators": room_info.get("operators", []),
                        "status": room_info.get("status", "normal"),
                    }

            # 解析干员信息
            operators = {}
            for key in base_ui:
                if key.startswith("operator_"):
                    op_info = base_ui[key]
                    operators[op_info["name"]] = {
                        "morale": op_info.get("morale", 24),
                        "skill": op_info.get("skill", ""),
                        "location": op_info.get("location", ""),
                    }

            # 解析资源信息
            resources = {
                "gold": float(base_ui.get("resource_gold", 0)),
                "exp": float(base_ui.get("resource_exp", 0)),
                "lmd": float(base_ui.get("resource_lmd", 0)),
                "orundum": float(base_ui.get("resource_orundum", 0)),
            }

            self.base_info = ArknightsBaseInfo(
                rooms=rooms, operators=operators, resources=resources
            )

        except Exception as e:
            self.logger.error(f"更新基建信息失败: {e}", exc_info=True)

    def create_task(self, config: Dict) -> Task:
        """创建任务"""
        task_type = config.get("type", "")

        if task_type == "auto_battle":
            return self._create_auto_battle_task(config)
        elif task_type == "base_shift":
            return self._create_base_shift_task(config)
        elif task_type == "recruitment":
            return self._create_recruitment_task(config)
        else:
            raise ValueError(f"未知的任务类型: {task_type}")

    def _create_auto_battle_task(self, config: Dict) -> Task:
        """创建自动战斗任务"""
        stage = config.get("stage", "")
        times = config.get("times", 1)

        return Task(
            name=f"自动战斗 {stage}",
            priority=TaskPriority.NORMAL,
            actions=[
                lambda: self._enter_terminal(),
                lambda: self._select_stage(stage),
                lambda: self._start_operation(),
                lambda: self._wait_battle_finish(),
                lambda: self._confirm_result(),
            ]
            * times,
            conditions={
                "scene": [ArknightsScene.TERMINAL.name, ArknightsScene.BATTLE.name],
                "sanity": lambda: self._check_sanity(),
            },
        )

    def _create_base_shift_task(self, config: Dict) -> Task:
        """创建基建换班任务"""
        return Task(
            name="基建换班",
            priority=TaskPriority.LOW,
            actions=[
                lambda: self._enter_base(),
                lambda: self._collect_resources(),
                lambda: self._check_facilities(),
                lambda: self._shift_operators(),
            ],
            conditions={
                "scene": [ArknightsScene.BASE.name],
                "time": lambda: self._is_shift_needed(),
            },
        )

    def _create_recruitment_task(self, config: Dict) -> Task:
        """创建公开招募任务"""
        return Task(
            name="公开招募",
            priority=TaskPriority.LOW,
            actions=[
                lambda: self._enter_recruit(),
                lambda: self._check_recruitment(),
                lambda: self._start_recruitment(),
            ],
            conditions={
                "scene": [ArknightsScene.RECRUIT.name],
                "permits": lambda: self._check_recruit_permits(),
            },
        )

    def _check_sanity(self) -> bool:
        """检查理智是否足够"""
        return True  # TODO: 实现具体检查逻辑

    def _is_shift_needed(self) -> bool:
        """检查是否需要换班"""
        return True  # TODO: 实现具体检查逻辑

    def _check_recruit_permits(self) -> bool:
        """检查招募许可是否足够"""
        return True  # TODO: 实现具体检查逻辑

    def save_config(self, config: Dict):
        """保存配置"""
        # TODO: 实现配置保存逻辑
        pass
