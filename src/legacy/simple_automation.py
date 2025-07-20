#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单自动化系统实现 - 原main.py的备份
这是原来根目录main.py中的简单实现，保留作为备用方案
"""

import time
import psutil
import keyboard
import logging
from ..collector.screen_collector import ScreenCollector
from ..engine.decision_engine import DecisionEngine
from ..executor.action_executor import ActionExecutor


class SimpleAutomationSystem:
    """简单的自动化系统实现"""
    
    def __init__(self):
        self.collector = ScreenCollector()
        self.engine = DecisionEngine()
        self.executor = ActionExecutor()
        self.running = False
        self.logger = logging.getLogger(__name__)

    def check_resource_usage(self) -> bool:
        """
        监控系统资源使用情况

        Returns:
            bool: 如果资源使用正常返回True，否则返回False
        """
        try:
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent

            if cpu_percent > 80:
                self.logger.warning(f"CPU使用率过高: {cpu_percent}%")
                return False
            if memory_percent > 90:
                self.logger.warning(f"内存使用率过高: {memory_percent}%")
                return False
            return True
        except Exception as e:
            self.logger.error(f"资源监控失败: {str(e)}")
            return True  # 监控失败时默认继续运行

    def check_safety_conditions(self) -> bool:
        """
        检查安全条件

        Returns:
            bool: 如果安全条件正常返回True，否则返回False
        """
        try:
            if keyboard.is_pressed("esc"):
                self.logger.info("检测到紧急停止热键")
                return False
            return True
        except Exception as e:
            self.logger.error(f"安全检查失败: {str(e)}")
            return True  # 检查失败时默认继续运行

    def start(self):
        """启动自动化系统"""
        self.running = True
        self.executor.start()

        while self.running:
            cycle_start = time.time()

            # 检查安全条件和资源使用
            if not self.check_safety_conditions() or not self.check_resource_usage():
                self.stop()
                break

            try:
                # 1. 收集信息
                current_state = self.collector.analyze_screen()

                # 2. 决策
                actions = self.engine.analyze_state(current_state)

                # 3. 执行
                for action in actions:
                    if not self.running:
                        break
                    self.executor.execute_action(action)

                # 计算并应用自适应延迟
                cycle_time = time.time() - cycle_start
                sleep_time = max(0.01, 0.1 - cycle_time)  # 确保至少有0.01秒的延迟
                time.sleep(sleep_time)

            except Exception as e:
                self.logger.error(f"自动化系统运行错误: {str(e)}")
                self.stop()
                break

    def stop(self):
        """停止自动化系统"""
        self.running = False
        self.executor.stop()
        self.logger.info("自动化系统已停止")


def create_simple_automation():
    """创建简单自动化系统实例"""
    return SimpleAutomationSystem()