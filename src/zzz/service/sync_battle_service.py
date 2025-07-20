"""
多实例同步战斗服务
"""
import os
import time
import json
import threading
from typing import Dict, List, Optional
from ..battle import AutoBattleSystem
from ...services.config import Config as ConfigManager
from ...services.window_manager import GameWindowManager as WindowManager


class SyncBattleService:
    def __init__(self):
        self.config = ConfigManager()
        self.window_manager = WindowManager()
        self.battle_instances: Dict[str, AutoBattleSystem] = {}
        self.sync_lock = threading.Lock()
        self.running = False

    def create_battle_instance(self, window_title: str, character_name: str) -> bool:
        """
        创建新的战斗实例

        Args:
            window_title: 游戏窗口标题
            character_name: 角色名称

        Returns:
            bool: 是否创建成功
        """
        # 检查窗口是否存在
        if not self.window_manager.find_window(window_title):
            return False

        # 检查是否已存在该实例
        if window_title in self.battle_instances:
            return False

        # 创建新的战斗实例
        try:
            battle_system = AutoBattleSystem(
                character_name, os.path.join("config", "auto_battle")
            )
            self.battle_instances[window_title] = battle_system
            return True
        except Exception as e:
            print(f"创建战斗实例失败: {e}")
            return False

    def remove_battle_instance(self, window_title: str):
        """
        移除战斗实例

        Args:
            window_title: 游戏窗口标题
        """
        if window_title in self.battle_instances:
            del self.battle_instances[window_title]

    def sync_all_instances(self):
        """同步所有实例的状态"""
        with self.sync_lock:
            # 获取所有窗口的状态
            window_states = {}
            for title in self.battle_instances.keys():
                if hwnd := self.window_manager.find_window(title):
                    window_states[title] = self.window_manager.get_window_state(hwnd)

            # 更新所有实例的状态
            for title, battle_system in self.battle_instances.items():
                if title in window_states:
                    battle_system.update_state(window_states[title])

    def start_sync_service(self):
        """启动同步服务"""
        self.running = True
        threading.Thread(target=self._sync_loop, daemon=True).start()

    def stop_sync_service(self):
        """停止同步服务"""
        self.running = False

    def _sync_loop(self):
        """同步循环"""
        while self.running:
            try:
                self.sync_all_instances()

                # 执行每个实例的下一个动作
                for title, battle_system in self.battle_instances.items():
                    if action := battle_system.get_next_action():
                        # 切换到对应窗口
                        if hwnd := self.window_manager.find_window(title):
                            self.window_manager.activate_window(hwnd)
                            time.sleep(0.1)  # 等待窗口激活

                            # 执行动作
                            self._execute_action(battle_system, action)

            except Exception as e:
                print(f"同步循环出错: {e}")

            time.sleep(0.1)  # 控制同步频率

    def _execute_action(self, battle_system: AutoBattleSystem, action: "BattleAction"):
        """
        执行战斗动作

        Args:
            battle_system: 战斗系统实例
            action: 要执行的动作
        """
        try:
            # 记录动作
            battle_system.record_action(action)

            # TODO: 实现具体的动作执行逻辑
            # 这里需要根据action.action_type来执行不同类型的操作

            # 等待指定延迟
            if action.delay > 0:
                time.sleep(action.delay)

        except Exception as e:
            print(f"执行动作失败: {e}")
            # 如果有后备动作，尝试执行
            if action.fallback:
                for fallback_action in battle_system.actions:
                    if fallback_action.action_type == action.fallback:
                        self._execute_action(battle_system, fallback_action)
                        break
