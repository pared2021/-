"""
绝区零游戏适配器
实现游戏特定的操作和状态检测
"""
from typing import Dict, List, Optional, Any
import cv2
import numpy as np
import time
import logging
from dataclasses import dataclass
import win32gui
import win32con
import win32api
import win32process
import win32ui
from ...core.game_adapter import GameAdapter, GameWindow, GameState
from ...core.unified_game_analyzer import UnifiedGameAnalyzer as GameAnalyzer


from ...common.action_system import (
    ActionType, GameSpecificAction, ActionSequence, ActionFactory, BaseAction
)

# 向后兼容性别名
ZZZAction = GameSpecificAction


class ZZZGameAdapter(GameAdapter):
    def __init__(self, data_dir: str):
        """
        初始化绝区零适配器

        Args:
            data_dir: 数据目录
        """
        self.logger = logging.getLogger("ZZZAdapter")
        self.analyzer = GameAnalyzer("zzz", data_dir)
        self.window_title = "Zenless Zone Zero"
        self.key_mapping = {
            "attack": "j",
            "dodge": "k",
            "skill": "l",
            "switch": ["1", "2", "3"],
            "ultimate": "u",
        }

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
        # 获取窗口截图
        screenshot = self._capture_window(window)

        # 分析场景和UI
        analysis = self.analyzer.analyze_screenshot(screenshot)

        # 收集游戏变量
        variables = self._collect_variables(window)

        return GameState(
            scene=analysis["scene"],
            ui_elements=analysis["ui_elements"],
            variables=variables,
            timestamp=time.time(),
        )

    def analyze_scene(self, screenshot: np.ndarray) -> str:
        """分析游戏场景"""
        # 使用分析器识别场景
        analysis = self.analyzer.analyze_screenshot(screenshot)
        return analysis["scene"]

    def collect_ui_info(self, window: GameWindow) -> Dict[str, Dict]:
        """收集UI信息"""
        screenshot = self._capture_window(window)
        analysis = self.analyzer.analyze_screenshot(screenshot)
        return analysis["ui_elements"]

    def get_action_template(self) -> Dict:
        """获取动作模板"""
        return {
            "basic_attack": ZZZAction(
                name="basic_attack",
                type=ActionType.ZZZ_ACTION,
                game_name="zzz",
                key="attack",
                post_delay=0.1,
                params={"action_type": "key"}
            ),
            "dodge": ZZZAction(
                name="dodge",
                type=ActionType.ZZZ_ACTION,
                game_name="zzz",
                key="dodge",
                post_delay=0.2,
                params={"action_type": "key"}
            ),
            "skill": ZZZAction(
                name="skill",
                type=ActionType.ZZZ_ACTION,
                game_name="zzz",
                key="skill",
                hold_time=0.5,
                post_delay=0.3,
                params={"action_type": "key"}
            ),
            "switch_character": ZZZAction(
                name="switch_character",
                type=ActionType.ZZZ_ACTION,
                game_name="zzz",
                key="switch",
                post_delay=0.5,
                params={"action_type": "key"}
            ),
            "ultimate": ZZZAction(
                name="ultimate",
                type=ActionType.ZZZ_ACTION,
                game_name="zzz",
                key="ultimate",
                post_delay=1.0,
                params={"action_type": "key"}
            ),
        }

    def execute_action(self, window: GameWindow, action: str, params: Dict) -> bool:
        """执行动作"""
        try:
            # 获取动作模板
            template = self.get_action_template().get(action)
            if not template:
                self.logger.error(f"未知动作: {action}")
                return False

            # 更新动作参数
            action_params = {
                "key": template.key,
                "hold_time": template.hold_time,
                "post_delay": template.post_delay,
                "repeat": getattr(template, 'repeat', 1),
                "action_type": template.params.get("action_type", "key")
            }
            action_params.update(params)

            # 激活窗口
            if not self._activate_window(window):
                return False

            # 执行动作
            if action_params["action_type"] == "key":
                return self._execute_key_action(action_params)
            else:
                self.logger.error(f"不支持的动作类型: {action_params['action_type']}")
                return False

        except Exception as e:
            self.logger.error(f"执行动作失败: {e}")
            return False

    def is_action_valid(self, state: GameState, action: str, params: Dict) -> bool:
        """检查动作是否有效"""
        # 检查场景
        if state.scene not in ["battle", "exploration"]:
            return False

        # 检查技能冷却
        if action == "skill" and state.variables.get("skill_cooldown", 0) > 0:
            return False

        # 检查角色切换冷却
        if (
            action == "switch_character"
            and state.variables.get("switch_cooldown", 0) > 0
        ):
            return False

        # 检查必杀技能量
        if action == "ultimate" and state.variables.get("ultimate_energy", 0) < 100:
            return False

        return True

    def _capture_window(self, window: GameWindow) -> np.ndarray:
        """捕获窗口截图"""
        try:
            # 获取窗口DC
            hwnd = window.handle
            left, top, right, bottom = window.rect
            width = right - left
            height = bottom - top

            hwndDC = win32gui.GetWindowDC(hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()

            # 创建位图
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)

            # 复制窗口内容
            result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 0)

            # 转换为numpy数组
            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)

            image = np.frombuffer(bmpstr, dtype="uint8")
            image.shape = (height, width, 4)

            # 清理资源
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)

            # 转换为RGB
            return cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)

        except Exception as e:
            self.logger.error(f"捕获窗口截图失败: {e}")
            return np.zeros((720, 1280, 3), dtype=np.uint8)

    def _collect_variables(self, window: GameWindow) -> Dict[str, Any]:
        """收集游戏变量"""
        variables = {}

        # 获取UI元素信息
        ui_info = self.collect_ui_info(window)

        # 解析技能冷却
        if "skill_cooldown" in ui_info:
            variables["skill_cooldown"] = float(
                ui_info["skill_cooldown"].get("text", "0")
            )

        # 解析切换冷却
        if "switch_cooldown" in ui_info:
            variables["switch_cooldown"] = float(
                ui_info["switch_cooldown"].get("text", "0")
            )

        # 解析必杀技能量
        if "ultimate_energy" in ui_info:
            variables["ultimate_energy"] = float(
                ui_info["ultimate_energy"].get("text", "0")
            )

        return variables

    def _activate_window(self, window: GameWindow) -> bool:
        """激活窗口"""
        try:
            if win32gui.GetForegroundWindow() != window.handle:
                win32gui.SetForegroundWindow(window.handle)
                time.sleep(0.1)  # 等待窗口激活
            return True
        except Exception as e:
            self.logger.error(f"激活窗口失败: {e}")
            return False

    def _execute_key_action(self, params: Dict) -> bool:
        """执行按键动作"""
        try:
            key = params["key"]
            hold_time = params.get("hold_time", 0.0)
            post_delay = params.get("post_delay", 0.01)
            repeat = params.get("repeat", 1)

            # 获取虚拟键码
            if isinstance(key, list):
                # 随机选择一个按键
                import random

                key = random.choice(key)

            vk_code = ord(key.upper())

            for _ in range(repeat):
                # 按下按键
                win32api.keybd_event(vk_code, 0, 0, 0)

                if hold_time > 0:
                    time.sleep(hold_time)

                # 释放按键
                win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)

                if post_delay > 0:
                    time.sleep(post_delay)

            return True

        except Exception as e:
            self.logger.error(f"执行按键动作失败: {e}")
            return False
