import unittest
from unittest.mock import Mock, patch
import numpy as np
import torch
from src.common.error_types import (
    ErrorCode, GameAutomationError, WindowError,
    ImageProcessingError, ActionError, StateError, ModelError,
    ErrorContext
)
from src.services.error_handler import ErrorHandler
from src.services.logger import GameLogger

class TestErrorHandler(unittest.TestCase):
    """错误处理服务测试"""
    
    def setUp(self):
        """测试前准备"""
        self.logger = Mock(spec=GameLogger)
        self.error_handler = ErrorHandler(self.logger)
        
        # 模拟服务
        self.window_manager = Mock()
        self.image_processor = Mock()
        self.action_simulator = Mock()
        self.game_state = Mock()
        self.game_analyzer = Mock()
        self.config = Mock()
        
        # 设置服务引用
        self.error_handler.set_window_manager(self.window_manager)
        self.error_handler.set_image_processor(self.image_processor)
        self.error_handler.set_action_simulator(self.action_simulator)
        self.error_handler.set_game_state(self.game_state)
        self.error_handler.set_game_analyzer(self.game_analyzer)
        self.error_handler.set_config(self.config)
        
    def test_handle_window_error(self):
        """测试窗口错误处理"""
        # 创建窗口错误
        error = WindowError(
            ErrorCode.WINDOW_NOT_FOUND,
            "窗口未找到",
            ErrorContext(
                source="test",
                details="测试窗口"
            )
        )
        
        # 模拟窗口恢复
        self.window_manager.find_window.return_value = 12345
        self.window_manager.is_window_exists.return_value = True
        self.window_manager.is_window_valid.return_value = True
        self.window_manager.is_window_visible.return_value = True
        self.window_manager.is_window_minimized.return_value = False
        self.window_manager.capture_window.return_value = np.zeros((100, 100, 3))
        
        # 处理错误
        result = self.error_handler.handle_error(error)
        
        # 验证结果
        self.assertTrue(result)
        self.window_manager.find_window.assert_called_once()
        self.window_manager.activate_window.assert_called_once()
        
    def test_handle_image_processing_error(self):
        """测试图像处理错误处理"""
        # 创建图像处理错误
        error = ImageProcessingError(
            ErrorCode.IMAGE_PROCESSING_FAILED,
            "图像处理失败",
            ErrorContext(
                source="test",
                details="测试图像"
            )
        )
        
        # 模拟图像处理器恢复
        self.image_processor.is_initialized.return_value = True
        self.image_processor.process_image.return_value = np.zeros((100, 100))
        
        # 处理错误
        result = self.error_handler.handle_error(error)
        
        # 验证结果
        self.assertTrue(result)
        self.image_processor.initialize.assert_called_once()
        self.image_processor.load_templates.assert_called_once()
        
    def test_handle_action_error(self):
        """测试动作错误处理"""
        # 创建动作错误
        error = ActionError(
            ErrorCode.ACTION_EXECUTION_FAILED,
            "动作执行失败",
            ErrorContext(
                source="test",
                details="测试动作"
            )
        )
        
        # 模拟动作模拟器恢复
        self.action_simulator.is_initialized.return_value = True
        self.action_simulator.execute_action.return_value = True
        
        # 处理错误
        result = self.error_handler.handle_error(error)
        
        # 验证结果
        self.assertTrue(result)
        self.action_simulator.initialize.assert_called_once()
        self.action_simulator.reset_mouse_position.assert_called_once()
        
    def test_handle_state_error(self):
        """测试状态错误处理"""
        # 创建状态错误
        error = StateError(
            ErrorCode.STATE_UPDATE_FAILED,
            "状态更新失败",
            ErrorContext(
                source="test",
                details="测试状态"
            )
        )
        
        # 模拟状态管理器恢复
        self.game_state.is_initialized.return_value = True
        self.game_state.get_current_state.return_value = {"test": "state"}
        
        # 处理错误
        result = self.error_handler.handle_error(error)
        
        # 验证结果
        self.assertTrue(result)
        self.game_state.initialize.assert_called_once()
        self.game_state.reset_state.assert_called_once()
        
    def test_handle_model_error(self):
        """测试模型错误处理"""
        # 创建模型错误
        error = ModelError(
            ErrorCode.MODEL_INFERENCE_FAILED,
            "模型推理失败",
            ErrorContext(
                source="test",
                details="测试模型"
            )
        )
        
        # 模拟游戏分析器恢复
        self.game_analyzer.is_initialized.return_value = True
        self.game_analyzer.is_model_loaded.return_value = True
        
        # 处理错误
        result = self.error_handler.handle_error(error)
        
        # 验证结果
        self.assertTrue(result)
        self.game_analyzer.reload_model.assert_called_once()
        
    def test_error_statistics(self):
        """测试错误统计"""
        # 创建多个错误
        errors = [
            WindowError(ErrorCode.WINDOW_NOT_FOUND, "窗口未找到", ErrorContext("test", "test")),
            ImageProcessingError(ErrorCode.IMAGE_PROCESSING_FAILED, "图像处理失败", ErrorContext("test", "test")),
            ActionError(ErrorCode.ACTION_EXECUTION_FAILED, "动作执行失败", ErrorContext("test", "test")),
            StateError(ErrorCode.STATE_UPDATE_FAILED, "状态更新失败", ErrorContext("test", "test")),
            ModelError(ErrorCode.MODEL_INFERENCE_FAILED, "模型推理失败", ErrorContext("test", "test"))
        ]
        
        # 处理错误
        for error in errors:
            self.error_handler.handle_error(error)
            
        # 获取错误统计
        stats = self.error_handler.get_error_stats()
        
        # 验证统计结果
        self.assertEqual(stats['total_errors'], 5)
        self.assertEqual(stats['error_types']['window'], 1)
        self.assertEqual(stats['error_types']['image_processing'], 1)
        self.assertEqual(stats['error_types']['action'], 1)
        self.assertEqual(stats['error_types']['state'], 1)
        self.assertEqual(stats['error_types']['model'], 1)
        
    def test_recovery_attempts(self):
        """测试恢复尝试次数限制"""
        # 创建错误
        error = WindowError(
            ErrorCode.WINDOW_NOT_FOUND,
            "窗口未找到",
            ErrorContext(
                source="test",
                details="测试窗口"
            )
        )
        
        # 模拟恢复失败
        self.window_manager.find_window.return_value = None
        
        # 多次处理错误
        for _ in range(5):
            result = self.error_handler.handle_error(error)
            
        # 验证结果
        self.assertFalse(result)
        self.assertEqual(self.window_manager.find_window.call_count, 3)  # 最大尝试次数
        
    def test_system_resource_check(self):
        """测试系统资源检查"""
        # 模拟系统资源正常
        with patch('psutil.virtual_memory') as mock_memory, \
             patch('psutil.cpu_percent') as mock_cpu, \
             patch('psutil.disk_usage') as mock_disk:
            
            mock_memory.return_value.percent = 50
            mock_cpu.return_value = 50
            mock_disk.return_value.percent = 50
            
            # 检查资源
            result = self.error_handler._check_system_resources()
            
            # 验证结果
            self.assertTrue(result)
            
        # 模拟系统资源不足
        with patch('psutil.virtual_memory') as mock_memory, \
             patch('psutil.cpu_percent') as mock_cpu, \
             patch('psutil.disk_usage') as mock_disk:
            
            mock_memory.return_value.percent = 95
            mock_cpu.return_value = 95
            mock_disk.return_value.percent = 95
            
            # 检查资源
            result = self.error_handler._check_system_resources()
            
            # 验证结果
            self.assertFalse(result)
            
if __name__ == '__main__':
    unittest.main() 