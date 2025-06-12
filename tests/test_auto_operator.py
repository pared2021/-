import pytest
from unittest.mock import MagicMock, patch
from src.services.auto_operator import AutoOperator
from src.models.game_state import GameState
from src.services.action_simulator import ActionSimulator

def test_window_refresh():
    """测试窗口刷新功能"""
    # 创建模拟对象
    game_state = MagicMock(spec=GameState)
    action_simulator = MagicMock(spec=ActionSimulator)
    logger = MagicMock()
    
    # 设置游戏状态
    game_state.is_window_valid.return_value = False
    
    # 创建AutoOperator实例
    operator = AutoOperator(game_state, action_simulator, logger)
    
    # 执行自动操作
    action = operator.get_next_action()
    
    # 验证结果
    assert action is not None
    game_state.is_window_valid.assert_called_once()
    game_state.refresh_windows.assert_called_once()
    action_simulator.sleep.assert_called_once_with(1)
    logger.info.assert_called_with("正在刷新游戏窗口...")

def test_window_state_handling():
    """测试窗口状态处理"""
    # 创建模拟对象
    game_state = MagicMock(spec=GameState)
    action_simulator = MagicMock(spec=ActionSimulator)
    logger = MagicMock()
    
    # 测试无效窗口情况
    game_state.is_window_valid.return_value = False
    operator = AutoOperator(game_state, action_simulator, logger)
    action = operator.get_next_action()
    assert action is not None  # 应该返回刷新动作
    
    # 测试有效窗口情况
    game_state.is_window_valid.return_value = True
    game_state.reset_mock()
    action = operator.get_next_action()
    game_state.refresh_windows.assert_not_called()  # 不应该调用刷新 