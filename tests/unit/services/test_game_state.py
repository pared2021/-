"""GameState类单元测试"""
import unittest
import time
from unittest.mock import MagicMock
from ....src.services.game_state import GameState, StateManager
from ....src.services.logger import GameLogger
from ....src.services.game_analyzer import GameAnalyzer

class TestGameState(unittest.TestCase):
    """测试游戏状态类"""
    
    def setUp(self):
        """测试前准备"""
        # 创建模拟对象
        self.logger = MagicMock(spec=GameLogger)
        self.game_analyzer = MagicMock(spec=GameAnalyzer)
        
        # 创建游戏状态对象
        self.game_state = GameState(self.logger, self.game_analyzer)
        
    def test_update_state(self):
        """测试更新状态"""
        # 创建测试状态
        test_state = {
            "position": (100, 200),
            "health": 80,
            "enemies": [{"position": (300, 400), "type": "enemy"}]
        }
        
        # 更新状态
        self.game_state.update_state(test_state)
        
        # 验证当前状态
        current_state = self.game_state.get_current_state()
        self.assertEqual(current_state["position"], (100, 200))
        self.assertEqual(current_state["health"], 80)
        self.assertEqual(len(current_state["enemies"]), 1)
        
        # 验证状态已添加到历史
        history = self.game_state.get_state_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0], current_state)
    
    def test_update_state_with_timestamp(self):
        """测试更新带时间戳的状态"""
        # 创建带时间戳的测试状态
        timestamp = time.time()
        test_state = {
            "timestamp": timestamp,
            "position": (100, 200),
            "health": 80
        }
        
        # 更新状态
        self.game_state.update_state(test_state)
        
        # 验证时间戳
        current_state = self.game_state.get_current_state()
        self.assertEqual(current_state["timestamp"], timestamp)
    
    def test_history_limit(self):
        """测试历史记录限制"""
        # 设置小的历史记录限制
        self.game_state.max_history_size = 3
        
        # 多次更新状态
        for i in range(5):
            self.game_state.update_state({"index": i})
        
        # 验证历史记录大小
        history = self.game_state.get_state_history()
        self.assertEqual(len(history), 3)
        
        # 验证历史记录内容（应该是最后3个状态）
        self.assertEqual(history[0]["index"], 2)
        self.assertEqual(history[1]["index"], 3)
        self.assertEqual(history[2]["index"], 4)
    
    def test_clear_history(self):
        """测试清除历史记录"""
        # 更新几个状态
        for i in range(3):
            self.game_state.update_state({"index": i})
        
        # 清除历史
        self.game_state.clear_history()
        
        # 验证历史记录为空
        self.assertEqual(len(self.game_state.get_state_history()), 0)
    
    def test_find_state_in_history(self):
        """测试在历史记录中查找状态"""
        # 更新几个状态
        states = [
            {"health": 100, "position": (10, 20)},
            {"health": 80, "position": (30, 40)},
            {"health": 60, "position": (50, 60)},
            {"health": 40, "position": (70, 80)}
        ]
        
        for state in states:
            self.game_state.update_state(state)
        
        # 查找健康值低于70的状态
        found = self.game_state.find_state_in_history(lambda s: s["health"] < 70)
        self.assertIsNotNone(found)
        self.assertEqual(found["health"], 40)  # 应该找到最后一个符合条件的
        
        # 查找不存在的状态
        not_found = self.game_state.find_state_in_history(lambda s: s["health"] < 30)
        self.assertIsNone(not_found)
    
    def test_empty_state_update(self):
        """测试更新空状态"""
        # 更新空状态
        self.game_state.update_state({})
        
        # 验证当前状态仍为空
        self.assertEqual(self.game_state.get_current_state(), {})
        
        # 验证历史记录也为空
        self.assertEqual(len(self.game_state.get_state_history()), 0)
        
class TestStateManager(unittest.TestCase):
    """测试状态管理器"""
    
    def setUp(self):
        """测试前准备"""
        self.state_manager = StateManager()
        
        # 创建模拟状态
        self.mock_state1 = MagicMock()
        self.mock_state1.name = "state1"
        self.mock_state1.templates = ["template1"]
        self.mock_state1.actions = ["action1", "action2"]
        
        self.mock_state2 = MagicMock()
        self.mock_state2.name = "state2"
        self.mock_state2.templates = ["template2"]
        self.mock_state2.actions = ["action3"]
        self.mock_state2.next_states = ["state1"]
        
    def test_add_state(self):
        """测试添加状态"""
        self.state_manager.add_state(self.mock_state1)
        self.state_manager.add_state(self.mock_state2)
        
        # 验证状态已添加
        self.assertEqual(len(self.state_manager.states), 2)
        self.assertIn("state1", self.state_manager.states)
        self.assertIn("state2", self.state_manager.states)
    
    def test_recognize_state(self):
        """测试识别状态"""
        # 添加状态
        self.state_manager.add_state(self.mock_state1)
        self.state_manager.add_state(self.mock_state2)
        
        # 创建模拟帧和图像处理器
        mock_frame = MagicMock()
        mock_image_processor = MagicMock()
        
        # 设置图像处理器模拟匹配结果
        def find_template_side_effect(frame, template):
            return True if template == "template2" else False
            
        mock_image_processor.find_template.side_effect = find_template_side_effect
        
        # 识别状态
        recognized = self.state_manager.recognize_state(mock_frame, mock_image_processor)
        
        # 验证识别结果
        self.assertEqual(recognized, self.mock_state2)
        
    def test_get_possible_actions(self):
        """测试获取可能的操作"""
        # 添加状态
        self.state_manager.add_state(self.mock_state1)
        
        # 设置当前状态
        self.state_manager.current_state = self.mock_state1
        
        # 获取可能的操作
        actions = self.state_manager.get_possible_actions()
        
        # 验证操作列表
        self.assertEqual(actions, ["action1", "action2"])
        
    def test_update_state(self):
        """测试更新状态"""
        # 添加状态
        self.state_manager.add_state(self.mock_state1)
        self.state_manager.add_state(self.mock_state2)
        
        # 更新状态
        self.state_manager.update_state(self.mock_state1)
        self.state_manager.update_state(self.mock_state2)
        
        # 验证当前状态
        self.assertEqual(self.state_manager.current_state, self.mock_state2)
        
        # 验证状态历史
        self.assertEqual(len(self.state_manager.state_history), 1)
        self.assertEqual(self.state_manager.state_history[0], "state1")
        
    def test_predict_next_state(self):
        """测试预测下一个状态"""
        # 添加状态
        self.state_manager.add_state(self.mock_state1)
        self.state_manager.add_state(self.mock_state2)
        
        # 设置当前状态
        self.state_manager.current_state = self.mock_state2
        
        # 预测下一个状态
        next_state = self.state_manager.predict_next_state("action3")
        
        # 验证预测结果
        self.assertEqual(next_state, self.mock_state1)

if __name__ == '__main__':
    unittest.main()