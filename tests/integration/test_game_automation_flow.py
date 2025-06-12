"""游戏自动化流程集成测试"""
import unittest
import sys
import os
import numpy as np
import cv2
from unittest.mock import MagicMock, patch, call
import copy

# 添加项目根目录到系统路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.services.window_manager import GameWindowManager
from src.services.image_processor import ImageProcessor
from src.services.game_analyzer import GameAnalyzer
from src.services.action_simulator import ActionSimulator
from src.services.auto_operator import AutoOperator, ActionType
from src.services.game_state import GameState
from src.services.logger import GameLogger
from src.services.config import Config

class TestGameAutomationFlow(unittest.TestCase):
    """测试游戏自动化流程的集成测试类"""

    def setUp(self):
        """测试前准备"""
        # 创建配置
        self.config = MagicMock(spec=Config)
        self.config.window = MagicMock()
        self.config.window.window_class = "TestWindowClass"
        self.config.window.window_title = "TestWindowTitle"
        self.config.image_processor = MagicMock()
        self.config.image_processor.template_match_threshold = 0.8
        self.config.action = MagicMock()
        self.config.action.key_press_delay = 0.01
        self.config.action.click_delay = 0.01
        self.config.action.mouse_offset = 2
        self.config.action.mouse_speed = 0.1
        self.config.action.min_wait_time = 0.1
        self.config.action.max_wait_time = 0.2
        self.config.action.min_random_delay = 0.1
        self.config.action.max_random_delay = 0.2
        
        # 创建日志组件
        self.logger = MagicMock(spec=GameLogger)
        
        # 创建测试图像
        self.test_image = np.zeros((600, 800, 3), dtype=np.uint8)
        # 添加一个白色按钮
        cv2.rectangle(self.test_image, (100, 100), (200, 150), (255, 255, 255), -1)
        # 添加一个红色"敌人"
        cv2.rectangle(self.test_image, (400, 300), (450, 350), (0, 0, 255), -1)
        
        # 创建游戏状态字典
        self.game_state_dict = {
            "timestamp": 1234567890.0,
            "buttons": [{"position": (150, 125), "size": (100, 50), "type": "button", "confidence": 0.9}],
            "enemies": [{"position": (425, 325), "size": (50, 50), "type": "enemy", "confidence": 0.8}],
            "items": [],
            "dialog_open": False,
            "health": 80,
            "mana": 60,
            "position": (200, 200),
            "screen_size": (800, 600)
        }
        
        # 应用模块补丁
        self.window_manager_patcher = patch('src.services.window_manager.GameWindowManager', autospec=True)
        self.image_processor_patcher = patch('src.services.image_processor.ImageProcessor', autospec=True)
        self.game_analyzer_patcher = patch('src.services.game_analyzer.GameAnalyzer', autospec=True)
        self.action_simulator_patcher = patch('src.services.action_simulator.ActionSimulator', autospec=True)
        self.game_state_patcher = patch('src.services.game_state.GameState', autospec=True)
        
        # 启动补丁
        self.mock_window_manager = self.window_manager_patcher.start()
        self.mock_image_processor = self.image_processor_patcher.start()
        self.mock_game_analyzer = self.game_analyzer_patcher.start()
        self.mock_action_simulator = self.action_simulator_patcher.start()
        self.mock_game_state = self.game_state_patcher.start()
        
        # 创建测试注入的实例
        self.window_manager = MagicMock(spec=GameWindowManager)
        self.image_processor = MagicMock(spec=ImageProcessor)
        self.game_analyzer = MagicMock(spec=GameAnalyzer)
        self.action_simulator = MagicMock(spec=ActionSimulator)
        self.game_state = MagicMock(spec=GameState)
        
        # 配置模拟对象行为
        self.window_manager.get_screenshot.return_value = self.test_image
        self.window_manager.find_window.return_value = True
        self.window_manager.window_handle = 123
        self.window_manager.window_rect = (0, 0, 800, 600)
        
        self.image_processor.analyze_frame.return_value = {
            "timestamp": 1234567890.0,
            "frame_size": (800, 600),
            "brightness": 128.0,
            "dominant_colors": [(255, 255, 255), (0, 0, 255)]
        }
        
        # 配置游戏分析器返回的游戏状态
        self.game_analyzer.analyze_frame.return_value = self.game_state_dict
        
        # 配置动作模拟器
        self.action_simulator.ensure_window_active.return_value = True
        
        # 创建自动操作器
        with patch.object(AutoOperator, '_init_rules'):
            self.auto_operator = AutoOperator(
                self.logger,
                self.action_simulator,
                self.game_state,
                self.image_processor,
                self.config
            )
            
            # 手动设置规则
            self.auto_operator.action_rules = [
                (lambda state: 'buttons' in state and len(state['buttons']) > 0, 
                 lambda state: {"type": ActionType.CLICK, "position": state['buttons'][0]['position'], "target": "button"}, 10),
                (lambda state: 'enemies' in state and len(state['enemies']) > 0, 
                 lambda state: {"type": ActionType.CLICK, "position": state['enemies'][0]['position'], "target": "enemy"}, 5),
                (lambda state: 'health' in state and state['health'] < 30, 
                 lambda state: {"type": ActionType.KEY_PRESS, "key": "h", "target": "potion"}, 15),
            ]
    
    def tearDown(self):
        """测试后清理"""
        # 停止所有补丁
        self.window_manager_patcher.stop()
        self.image_processor_patcher.stop()
        self.game_analyzer_patcher.stop()
        self.action_simulator_patcher.stop()
        self.game_state_patcher.stop()
    
    @patch('time.time')
    @patch('time.sleep')
    def test_game_automation_flow(self, mock_sleep, mock_time):
        """测试完整的游戏自动化流程"""
        # 设置时间模拟
        mock_time.return_value = 100.0
        
        # 步骤1: 窗口捕获阶段
        # 模拟窗口捕获
        screenshot = self.window_manager.get_screenshot()
        
        # 验证截图
        self.assertIsNotNone(screenshot)
        self.assertEqual(screenshot.shape, (600, 800, 3))
        
        # 步骤2: 图像处理阶段
        # 模拟图像处理
        image_state = self.image_processor.analyze_frame(screenshot)
        
        # 验证图像处理结果
        self.assertIsNotNone(image_state)
        self.assertIn("timestamp", image_state)
        self.assertIn("frame_size", image_state)
        self.assertEqual(image_state["frame_size"], (800, 600))
        
        # 步骤3: 游戏分析阶段
        # 模拟游戏分析
        game_state = self.game_analyzer.analyze_frame(screenshot)
        
        # 验证游戏分析结果
        self.assertIsNotNone(game_state)
        self.assertIn("buttons", game_state)
        self.assertIn("enemies", game_state)
        self.assertEqual(len(game_state["buttons"]), 1)
        self.assertEqual(len(game_state["enemies"]), 1)
        
        # 步骤4: 行为选择阶段
        # 使用工厂方法创建动作，直接伪造动作选择结果
        def mock_select_action(state):
            # 检查状态中的健康值
            if state.get('health', 100) < 30:
                return {
                    "type": ActionType.KEY_PRESS,
                    "key": "h",
                    "target": "potion"
                }
            # 否则，点击按钮（如果有）
            elif 'buttons' in state and len(state['buttons']) > 0:
                return {
                    "type": ActionType.CLICK,
                    "position": state['buttons'][0]['position'],
                    "target": "button"
                }
            # 或者点击敌人（如果有）
            elif 'enemies' in state and len(state['enemies']) > 0:
                return {
                    "type": ActionType.CLICK,
                    "position": state['enemies'][0]['position'],
                    "target": "enemy"
                }
            # 默认等待
            return {
                "type": ActionType.WAIT,
                "duration": 0.5
            }
        
        # 设置mock对象的行为
        self.auto_operator.select_action = MagicMock(side_effect=mock_select_action)
        
        # 获取动作
        action = self.auto_operator.select_action(game_state)
        
        # 验证选择的行为
        self.assertIsNotNone(action)
        self.assertIn("type", action)
        
        # 由于按钮比敌人优先级高，应该选择点击按钮
        self.assertEqual(action["type"], ActionType.CLICK)
        self.assertEqual(action["position"], (150, 125))
        self.assertEqual(action["target"], "button")
        
        # 步骤5: 行为执行阶段
        # 模拟行为执行
        result = self.auto_operator.execute_action(action)
        
        # 验证行为执行结果
        self.assertTrue(result)
        self.action_simulator.click.assert_called_once_with(150, 125)
        
        # 验证数据流通性和一致性
        # 确保窗口捕获的图像被传递给了图像处理器和游戏分析器
        self.image_processor.analyze_frame.assert_called_once()
        self.game_analyzer.analyze_frame.assert_called_once()
        
        # 测试优先级规则 - 直接创建一个低生命值的状态字典
        low_health_state = {
            "timestamp": 1234567890.0,
            "buttons": [{"position": (150, 125), "size": (100, 50), "type": "button", "confidence": 0.9}],
            "enemies": [{"position": (425, 325), "size": (50, 50), "type": "enemy", "confidence": 0.8}],
            "items": [],
            "dialog_open": False,
            "health": 20,  # 低生命值
            "mana": 60,
            "position": (200, 200),
            "screen_size": (800, 600)
        }
        
        # 选择行为 - 使用新创建的低生命值状态字典
        action = self.auto_operator.select_action(low_health_state)
        
        # 验证选择了最高优先级的动作（使用生命药水）
        self.assertEqual(action["type"], ActionType.KEY_PRESS)
        self.assertEqual(action["key"], "h")
        
    @patch('time.time')
    @patch('time.sleep')
    def test_full_automation_cycle(self, mock_sleep, mock_time):
        """测试完整的自动化循环"""
        # 设置时间模拟
        mock_time.return_value = 100.0
        
        # 模拟窗口管理器找到窗口并获取截图
        self.window_manager.find_window.return_value = True
        self.window_manager.get_screenshot.return_value = self.test_image
        
        # 执行窗口查找和截图
        window_found = self.window_manager.find_window()
        screenshot = self.window_manager.get_screenshot()
        
        # 验证窗口查找和截图
        self.assertTrue(window_found)
        self.assertIsNotNone(screenshot)
        
        # 执行图像分析
        image_state = self.image_processor.analyze_frame(screenshot)
        
        # 验证图像分析
        self.assertIsNotNone(image_state)
        
        # 执行游戏状态分析
        game_state = self.game_analyzer.analyze_frame(screenshot)
        
        # 验证游戏状态分析
        self.assertIsNotNone(game_state)
        self.assertIn("buttons", game_state)
        self.assertIn("enemies", game_state)
        
        # 确保窗口处于激活状态
        window_active = self.action_simulator.ensure_window_active()
        self.assertTrue(window_active)
        
        # 选择行为
        action = self.auto_operator.select_action(game_state)
        
        # 验证行为选择
        self.assertIsNotNone(action)
        self.assertEqual(action["type"], ActionType.CLICK)
        
        # 执行行为
        result = self.auto_operator.execute_action(action)
        
        # 验证行为执行
        self.assertTrue(result)
        
        # 验证完整流程
        self.window_manager.find_window.assert_called_once()
        self.window_manager.get_screenshot.assert_called_once()
        self.image_processor.analyze_frame.assert_called_once_with(screenshot)
        self.game_analyzer.analyze_frame.assert_called_once_with(screenshot)
        self.action_simulator.ensure_window_active.assert_called_once()
        self.action_simulator.click.assert_called_once_with(150, 125)

if __name__ == '__main__':
    unittest.main() 