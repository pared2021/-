"""动作模拟器(ActionSimulator)单元测试"""
import unittest
import sys
import os
import time
from unittest.mock import MagicMock, patch, call

# 添加项目根目录到系统路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from ....src.services.action_simulator import ActionSimulator
from ....src.services.logger import GameLogger
from ....src.services.window_manager import GameWindowManager
from ....src.services.config import Config

class TestActionSimulator(unittest.TestCase):
    """动作模拟器测试类"""

    def setUp(self):
        """测试前准备"""
        # 创建模拟对象
        self.logger = MagicMock(spec=GameLogger)
        self.window_manager = MagicMock(spec=GameWindowManager)
        self.config = MagicMock(spec=Config)
        
        # 配置模拟对象
        self.config.action = MagicMock()
        self.config.action.key_press_delay = 0.01
        self.config.action.click_delay = 0.01
        self.config.action.mouse_offset = 2
        self.config.action.mouse_speed = 0.1
        self.config.action.min_wait_time = 0.1
        self.config.action.max_wait_time = 0.2
        
        # 创建测试对象
        with patch('src.services.action_simulator.pyautogui') as self.mock_pyautogui:
            self.action_simulator = ActionSimulator(self.logger, self.window_manager, self.config)
    
    @patch('src.services.action_simulator.pyautogui')
    def test_move_to(self, mock_pyautogui):
        """测试移动鼠标"""
        # 设置信号监听
        on_started = MagicMock()
        on_finished = MagicMock()
        
        self.action_simulator.action_started.connect(on_started)
        self.action_simulator.action_finished.connect(on_finished)
        
        # 调用方法
        self.action_simulator.move_to(100, 200, 0.1)
        
        # 验证信号
        on_started.assert_called_once_with("move_to")
        on_finished.assert_called_once_with("move_to")
        
        # 验证方法调用
        mock_pyautogui.moveTo.assert_called_once()
        
        # 检查传入参数
        args, kwargs = mock_pyautogui.moveTo.call_args
        # 考虑到随机偏移，检查坐标在预期范围内
        self.assertTrue(98 <= args[0] <= 102)
        self.assertTrue(198 <= args[1] <= 202)
        self.assertEqual(kwargs['duration'], 0.1)
        
    @patch('src.services.action_simulator.pyautogui')
    def test_click(self, mock_pyautogui):
        """测试鼠标点击"""
        # 设置信号监听
        on_started = MagicMock()
        on_finished = MagicMock()
        
        self.action_simulator.action_started.connect(on_started)
        self.action_simulator.action_finished.connect(on_finished)
        
        # 模拟移动到方法
        self.action_simulator.move_to = MagicMock()
        
        # 调用方法
        self.action_simulator.click(100, 200, 'left', 2, 0.05)
        
        # 验证信号
        on_started.assert_called_once_with("click")
        on_finished.assert_called_once_with("click")
        
        # 验证方法调用
        self.action_simulator.move_to.assert_called_once_with(100, 200)
        mock_pyautogui.click.assert_called_once_with(button='left', clicks=2, interval=0.05)
        
    @patch('src.services.action_simulator.pyautogui')
    def test_press_key(self, mock_pyautogui):
        """测试按键"""
        # 设置信号监听
        on_started = MagicMock()
        on_finished = MagicMock()
        
        self.action_simulator.action_started.connect(on_started)
        self.action_simulator.action_finished.connect(on_finished)
        
        # 调用方法
        self.action_simulator.press_key('a', 3, 0.1)
        
        # 验证信号
        on_started.assert_called_once_with("press_key")
        on_finished.assert_called_once_with("press_key")
        
        # 验证方法调用
        mock_pyautogui.press.assert_called_once_with('a', presses=3, interval=0.1)
        
    @patch('src.services.action_simulator.pyautogui')
    def test_hotkey(self, mock_pyautogui):
        """测试组合键"""
        # 设置信号监听
        on_started = MagicMock()
        on_finished = MagicMock()
        
        self.action_simulator.action_started.connect(on_started)
        self.action_simulator.action_finished.connect(on_finished)
        
        # 调用方法
        self.action_simulator.hotkey('ctrl', 'a')
        
        # 验证信号
        on_started.assert_called_once_with("hotkey")
        on_finished.assert_called_once_with("hotkey")
        
        # 验证方法调用
        mock_pyautogui.hotkey.assert_called_once_with('ctrl', 'a')
        
    @patch('src.services.action_simulator.pyautogui')
    def test_typewrite(self, mock_pyautogui):
        """测试文本输入"""
        # 设置信号监听
        on_started = MagicMock()
        on_finished = MagicMock()
        
        self.action_simulator.action_started.connect(on_started)
        self.action_simulator.action_finished.connect(on_finished)
        
        # 调用方法
        self.action_simulator.typewrite("Hello, World!", 0.05)
        
        # 验证信号
        on_started.assert_called_once_with("typewrite")
        on_finished.assert_called_once_with("typewrite")
        
        # 验证方法调用
        mock_pyautogui.typewrite.assert_called_once_with("Hello, World!", interval=0.05)
        
    @patch('time.sleep')
    def test_wait(self, mock_sleep):
        """测试等待"""
        # 设置信号监听
        on_started = MagicMock()
        on_finished = MagicMock()
        
        self.action_simulator.action_started.connect(on_started)
        self.action_simulator.action_finished.connect(on_finished)
        
        # 调用方法
        self.action_simulator.wait(1.5)
        
        # 验证信号
        on_started.assert_called_once_with("wait")
        on_finished.assert_called_once_with("wait")
        
        # 验证方法调用
        mock_sleep.assert_called_once_with(1.5)
        
    @patch('random.uniform')
    @patch('time.sleep')
    def test_random_wait(self, mock_sleep, mock_uniform):
        """测试随机等待"""
        # 设置模拟行为
        mock_uniform.return_value = 0.15
        
        # 设置信号监听
        on_started = MagicMock()
        on_finished = MagicMock()
        
        self.action_simulator.action_started.connect(on_started)
        self.action_simulator.action_finished.connect(on_finished)
        
        # 调用方法
        self.action_simulator.random_wait()
        
        # 验证信号
        on_started.assert_called_once_with("random_wait")
        on_finished.assert_called_once_with("random_wait")
        
        # 验证方法调用
        mock_uniform.assert_called_once_with(0.1, 0.2)
        mock_sleep.assert_called_once_with(0.15)
        
    def test_ensure_window_active_already_active(self):
        """测试确保窗口激活(已激活)"""
        # 设置模拟行为
        self.window_manager.is_window_active.return_value = True
        
        # 设置信号监听
        on_started = MagicMock()
        on_finished = MagicMock()
        
        self.action_simulator.action_started.connect(on_started)
        self.action_simulator.action_finished.connect(on_finished)
        
        # 调用方法
        result = self.action_simulator.ensure_window_active()
        
        # 验证结果
        self.assertTrue(result)
        
        # 验证信号
        on_started.assert_called_once_with("ensure_window_active")
        on_finished.assert_called_once_with("ensure_window_active")
        
        # 验证方法调用
        self.window_manager.is_window_active.assert_called_once()
        self.window_manager.set_foreground.assert_not_called()
        
    def test_ensure_window_active_needs_activation(self):
        """测试确保窗口激活(需要激活)"""
        # 设置模拟行为
        self.window_manager.is_window_active.return_value = False
        self.window_manager.set_foreground.return_value = True
        
        # 设置信号监听
        on_started = MagicMock()
        on_finished = MagicMock()
        
        self.action_simulator.action_started.connect(on_started)
        self.action_simulator.action_finished.connect(on_finished)
        
        # 调用方法
        result = self.action_simulator.ensure_window_active()
        
        # 验证结果
        self.assertTrue(result)
        
        # 验证信号
        on_started.assert_called_once_with("ensure_window_active")
        on_finished.assert_called_once_with("ensure_window_active")
        
        # 验证方法调用
        self.window_manager.is_window_active.assert_called_once()
        self.window_manager.set_foreground.assert_called_once()

if __name__ == '__main__':
    unittest.main()