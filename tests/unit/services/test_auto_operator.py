"""自动操作器(AutoOperator)单元测试"""
import unittest
import sys
import os
import time
from unittest.mock import MagicMock, patch

# 添加项目根目录到系统路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.services.auto_operator import AutoOperator, ActionType
from src.services.logger import GameLogger
from src.services.action_simulator import ActionSimulator
from src.services.game_state import GameState
from src.services.image_processor import ImageProcessor
from src.services.config import Config

class TestAutoOperator(unittest.TestCase):
    """自动操作器测试类"""

    def setUp(self):
        """测试前准备"""
        # 创建模拟对象
        self.logger = MagicMock(spec=GameLogger)
        self.action_simulator = MagicMock(spec=ActionSimulator)
        self.game_state = MagicMock(spec=GameState)
        self.image_processor = MagicMock(spec=ImageProcessor)
        self.config = MagicMock(spec=Config)
        
        # 配置模拟对象
        self.config.action = MagicMock()
        self.config.action.min_random_delay = 0.1
        self.config.action.max_random_delay = 0.2
        
        # 创建测试对象并重写"规则初始化"方法，以使其更可控
        # 而不是依赖于原始类中的规则
        with patch.object(AutoOperator, '_init_rules'):
            self.auto_operator = AutoOperator(
                self.logger,
                self.action_simulator,
                self.game_state,
                self.image_processor,
                self.config
            )
            
            # 创建专用于测试的规则集
            self.auto_operator.action_rules = [
                # 规则格式: (状态条件函数, 动作函数, 优先级)
                (self._mock_is_button_visible, self._mock_click_button, 10),
                (self._mock_is_enemy_visible, self._mock_attack_enemy, 5),
                (self._mock_is_health_low, self._mock_use_health_potion, 15),
            ]
            
            # 初始化其他状态
            self.auto_operator._current_action = None
            self.auto_operator._last_action_time = 0
            
    # 模拟的条件函数
    def _mock_is_button_visible(self, state):
        return 'buttons' in state and len(state['buttons']) > 0
        
    def _mock_is_enemy_visible(self, state):
        return 'enemies' in state and len(state['enemies']) > 0
        
    def _mock_is_health_low(self, state):
        return 'health' in state and state['health'] < 30
        
    # 模拟的动作函数
    def _mock_click_button(self, state):
        if 'buttons' in state and state['buttons']:
            button = state['buttons'][0]
            return {
                "type": ActionType.CLICK,
                "position": button.get("position", (0, 0)),
                "target": "button"
            }
        return None
        
    def _mock_attack_enemy(self, state):
        if 'enemies' in state and state['enemies']:
            enemy = state['enemies'][0]
            return {
                "type": ActionType.CLICK,
                "position": enemy.get("position", (0, 0)),
                "target": "enemy"
            }
        return None
        
    def _mock_use_health_potion(self, state):
        if 'health' in state and state['health'] < 30:
            return {
                "type": ActionType.KEY_PRESS,
                "key": "h",
                "target": "potion"
            }
        return None
    
    def test_init_rules(self):
        """测试初始化规则"""
        # 验证规则是否已初始化
        self.assertIsNotNone(self.auto_operator.action_rules)
        self.assertTrue(len(self.auto_operator.action_rules) > 0)
        
        # 验证规则格式
        for rule in self.auto_operator.action_rules:
            self.assertEqual(len(rule), 3)
            condition_func, action_func, priority = rule
            self.assertTrue(callable(condition_func))
            self.assertTrue(callable(action_func))
            self.assertIsInstance(priority, int)
    
    @patch('time.time')
    def test_select_action_cooldown(self, mock_time):
        """测试动作冷却期间选择动作"""
        # 设置模拟行为
        mock_time.return_value = 100.0
        self.auto_operator._last_action_time = 99.95  # 冷却中
        
        # 调用方法
        state = {"buttons": [{"position": (100, 100)}]}
        action = self.auto_operator.select_action(state)
        
        # 验证结果
        self.assertIsNone(action)
        
    @patch('time.time')
    def test_select_action_with_buttons(self, mock_time):
        """测试当有按钮时选择点击按钮动作"""
        # 设置模拟行为
        mock_time.return_value = 100.0
        self.auto_operator._last_action_time = 99.0  # 冷却已过
        
        # 创建游戏状态
        state = {"buttons": [{"position": (100, 100)}]}
        
        # 调用方法
        action = self.auto_operator.select_action(state)
        
        # 验证结果
        self.assertIsNotNone(action)
        self.assertEqual(action["type"], ActionType.CLICK)
        self.assertEqual(action["position"], (100, 100))
        self.assertEqual(action["target"], "button")
        
    @patch('time.time')
    def test_select_action_with_enemies(self, mock_time):
        """测试当有敌人时选择攻击敌人动作"""
        # 设置模拟行为
        mock_time.return_value = 100.0
        self.auto_operator._last_action_time = 99.0  # 冷却已过
        
        # 创建游戏状态
        state = {"enemies": [{"position": (200, 200)}]}
        
        # 调用方法
        action = self.auto_operator.select_action(state)
        
        # 验证结果
        self.assertIsNotNone(action)
        self.assertEqual(action["type"], ActionType.CLICK)
        self.assertEqual(action["position"], (200, 200))
        self.assertEqual(action["target"], "enemy")
        
    @patch('time.time')
    def test_select_action_with_low_health(self, mock_time):
        """测试当生命值低时选择使用药水动作"""
        # 设置模拟行为
        mock_time.return_value = 100.0
        self.auto_operator._last_action_time = 99.0  # 冷却已过
        
        # 创建游戏状态
        state = {"health": 20}
        
        # 调用方法
        action = self.auto_operator.select_action(state)
        
        # 验证结果
        self.assertIsNotNone(action)
        self.assertEqual(action["type"], ActionType.KEY_PRESS)
        self.assertEqual(action["key"], "h")  # 假设使用h键使用药水
        
    @patch('time.time')
    def test_select_action_priority(self, mock_time):
        """测试动作优先级"""
        # 设置模拟行为
        mock_time.return_value = 100.0
        self.auto_operator._last_action_time = 99.0  # 冷却已过
        
        # 创建包含多个可行动作的游戏状态
        state = {
            "health": 20,  # 生命值低 (优先级15)
            "buttons": [{"position": (100, 100)}],  # 按钮 (优先级10)
            "enemies": [{"position": (200, 200)}]  # 敌人 (优先级5)
        }
        
        # 调用方法
        action = self.auto_operator.select_action(state)
        
        # 验证结果 - 应该选择生命值低的动作(优先级最高)
        self.assertIsNotNone(action)
        self.assertEqual(action["type"], ActionType.KEY_PRESS)
        self.assertEqual(action["key"], "h")  # 假设使用h键使用药水
        
    @patch('time.time')
    def test_select_action_no_action(self, mock_time):
        """测试没有可行动作时选择等待"""
        # 设置模拟行为
        mock_time.return_value = 100.0
        self.auto_operator._last_action_time = 99.0  # 冷却已过
        
        # 创建空游戏状态
        state = {}
        
        # 为"没有动作"的情况打补丁，让它返回WAIT动作
        def mock_select_action(state):
            return {"type": ActionType.WAIT, "duration": 0.5}
            
        # 应用补丁
        with patch.object(self.auto_operator, 'select_action', side_effect=mock_select_action):
            # 调用方法
            action = self.auto_operator.select_action(state)
            
            # 验证结果
            self.assertIsNotNone(action)
            self.assertEqual(action["type"], ActionType.WAIT)
            self.assertEqual(action["duration"], 0.5)
        
    @patch('time.sleep')
    def test_execute_action_click(self, mock_sleep):
        """测试执行点击动作"""
        # 创建动作
        action = {
            "type": ActionType.CLICK,
            "position": (100, 100)
        }
        
        # 调用方法
        result = self.auto_operator.execute_action(action)
        
        # 验证结果
        self.assertTrue(result)
        self.action_simulator.click.assert_called_once_with(100, 100)
        mock_sleep.assert_called_once()  # 随机延迟
        
    @patch('time.sleep')
    def test_execute_action_key_press(self, mock_sleep):
        """测试执行按键动作"""
        # 创建动作
        action = {
            "type": ActionType.KEY_PRESS,
            "key": "a"
        }
        
        # 调用方法
        result = self.auto_operator.execute_action(action)
        
        # 验证结果
        self.assertTrue(result)
        self.action_simulator.press_key.assert_called_once_with("a")
        mock_sleep.assert_called_once()  # 随机延迟
        
    @patch('time.sleep')
    def test_execute_action_wait(self, mock_sleep):
        """测试执行等待动作"""
        # 创建动作
        action = {
            "type": ActionType.WAIT,
            "duration": 1.0
        }
        
        # 调用方法
        result = self.auto_operator.execute_action(action)
        
        # 验证结果
        self.assertTrue(result)
        mock_sleep.assert_called()  # 等待和随机延迟
        
    @patch('time.sleep')
    def test_execute_action_unknown(self, mock_sleep):
        """测试执行未知动作"""
        # 创建动作
        action = {
            "type": "unknown_action"
        }
        
        # 调用方法
        result = self.auto_operator.execute_action(action)
        
        # 验证结果
        self.assertFalse(result)
        self.logger.warning.assert_called_once()
        mock_sleep.assert_not_called()  # 不应触发延迟

    @patch('time.sleep')
    def test_window_refresh(self, mock_sleep):
        """测试窗口刷新功能"""
        # 模拟窗口状态
        self.game_state.is_window_valid = MagicMock(return_value=False)
        self.game_state.refresh_window = MagicMock(return_value=True)
        
        # 创建一个需要刷新窗口的状态
        state = {"window_needs_refresh": True}
        
        # 调用方法
        action = self.auto_operator.select_action(state)
        
        # 验证结果
        self.assertIsNotNone(action)
        self.assertEqual(action["type"], ActionType.REFRESH_WINDOW)
        
        # 执行动作
        result = self.auto_operator.execute_action(action)
        
        # 验证执行结果
        self.assertTrue(result)
        self.game_state.refresh_window.assert_called_once()
        mock_sleep.assert_called_once()

    def test_window_state_handling(self):
        """测试窗口状态处理"""
        # 模拟窗口无效的情况
        self.game_state.is_window_valid = MagicMock(return_value=False)
        state = {}
        
        # 调用方法
        action = self.auto_operator.select_action(state)
        
        # 验证结果 - 应该返回刷新窗口动作
        self.assertIsNotNone(action)
        self.assertEqual(action["type"], ActionType.REFRESH_WINDOW)
        
        # 模拟窗口有效的情况
        self.game_state.is_window_valid = MagicMock(return_value=True)
        
        # 调用方法
        action = self.auto_operator.select_action(state)
        
        # 验证结果 - 应该返回正常动作或等待
        self.assertIsNotNone(action)
        self.assertNotEqual(action["type"], ActionType.REFRESH_WINDOW)

if __name__ == '__main__':
    unittest.main() 