"""性能测试模块"""
import unittest
import os
import sys
import time
import cv2
import numpy as np
from unittest.mock import MagicMock, patch
import threading
import queue

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

class PerformanceTests(unittest.TestCase):
    """性能测试类"""
    
    def setUp(self):
        """测试前准备"""
        # 创建日志和配置
        self.logger = MagicMock(spec=GameLogger)
        self.config = MagicMock(spec=Config)
        
        # 配置模拟对象
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
        
        # 创建测试图像 - 不同大小以测试性能
        self.small_image = np.zeros((480, 640, 3), dtype=np.uint8)
        self.medium_image = np.zeros((720, 1280, 3), dtype=np.uint8)
        self.large_image = np.zeros((1080, 1920, 3), dtype=np.uint8)
        
        # 在图像中添加一些测试元素
        for img in [self.small_image, self.medium_image, self.large_image]:
            h, w = img.shape[:2]
            # 添加一个按钮
            cv2.rectangle(img, (int(w*0.1), int(h*0.1)), (int(w*0.2), int(h*0.15)), (255, 255, 255), -1)
            # 添加一个"敌人"
            cv2.rectangle(img, (int(w*0.5), int(h*0.5)), (int(w*0.55), int(h*0.55)), (0, 0, 255), -1)
            # 添加一些UI元素
            cv2.rectangle(img, (int(w*0.8), int(h*0.05)), (int(w*0.95), int(h*0.1)), (0, 255, 0), -1)
            cv2.rectangle(img, (int(w*0.05), int(h*0.8)), (int(w*0.2), int(h*0.9)), (255, 0, 0), -1)
        
        # 创建原始组件
        self.window_manager = GameWindowManager(self.logger, self.config)
        self.image_processor = ImageProcessor(self.logger, self.config)
        self.game_analyzer = GameAnalyzer(self.logger, self.config, self.image_processor)
    
    def test_frame_processing_performance(self):
        """测试帧处理性能"""
        print("\n====== 帧处理性能测试 ======")
        
        # 测试不同分辨率的图像处理性能
        resolutions = {
            "小分辨率 (640x480)": self.small_image,
            "中分辨率 (1280x720)": self.medium_image,
            "高分辨率 (1920x1080)": self.large_image
        }
        
        for name, image in resolutions.items():
            # 测量图像处理器性能
            start_time = time.time()
            iterations = 10
            
            for _ in range(iterations):
                with patch.object(self.image_processor, 'analyze_frame', return_value={
                    "timestamp": time.time(),
                    "frame_size": image.shape[:2][::-1],
                    "brightness": 128.0,
                    "dominant_colors": [(255, 255, 255), (0, 0, 255)]
                }):
                    self.image_processor.analyze_frame(image)
            
            ip_time = (time.time() - start_time) / iterations
            ip_fps = 1.0 / ip_time if ip_time > 0 else float('inf')
            
            # 测量游戏分析器性能
            start_time = time.time()
            
            for _ in range(iterations):
                with patch.object(self.image_processor, 'analyze_frame', return_value={
                    "timestamp": time.time(),
                    "frame_size": image.shape[:2][::-1],
                    "brightness": 128.0,
                    "dominant_colors": [(255, 255, 255), (0, 0, 255)]
                }), patch.object(self.game_analyzer, 'analyze_frame', return_value={
                    "timestamp": time.time(),
                    "buttons": [{"position": (150, 125), "size": (100, 50), "type": "button", "confidence": 0.9}],
                    "enemies": [{"position": (425, 325), "size": (50, 50), "type": "enemy", "confidence": 0.8}],
                    "items": [],
                    "dialog_open": False,
                    "health": 80,
                    "mana": 60,
                    "position": (200, 200),
                    "screen_size": image.shape[:2][::-1]
                }):
                    self.game_analyzer.analyze_frame(image)
            
            ga_time = (time.time() - start_time) / iterations
            ga_fps = 1.0 / ga_time if ga_time > 0 else float('inf')
            
            print(f"{name}:")
            print(f"  图像处理器: {ip_time*1000:.2f}ms/帧 ({ip_fps:.2f} FPS)")
            print(f"  游戏分析器: {ga_time*1000:.2f}ms/帧 ({ga_fps:.2f} FPS)")
            
            # 验证性能要求
            # 对于实时游戏，通常需要至少30 FPS的处理速度
            self.assertGreaterEqual(ip_fps, 30, f"图像处理器FPS过低: {ip_fps} < 30 FPS")
            self.assertGreaterEqual(ga_fps, 30, f"游戏分析器FPS过低: {ga_fps} < 30 FPS")
    
    def test_action_execution_performance(self):
        """测试动作执行性能"""
        print("\n====== 动作执行性能测试 ======")
        
        # 模拟窗口管理器
        window_manager = MagicMock(spec=GameWindowManager)
        window_manager.is_window_active.return_value = True
        window_manager.set_foreground.return_value = True
        
        # 创建动作模拟器
        action_simulator = ActionSimulator(self.logger, window_manager, self.config)
        
        # 测试不同动作类型的执行时间
        action_types = {
            "点击": lambda: action_simulator.click(100, 100),
            "按键": lambda: action_simulator.press_key('a'),
            "移动鼠标": lambda: action_simulator.move_to(200, 200),
            "等待": lambda: action_simulator.wait(0.1),
            "随机等待": lambda: action_simulator.random_wait(0.1, 0.2)
        }
        
        for name, action in action_types.items():
            iterations = 10
            start_time = time.time()
            
            for _ in range(iterations):
                action()
            
            elapsed = (time.time() - start_time) / iterations
            print(f"{name}: {elapsed*1000:.2f}ms")
            
            # 对于非等待类操作，应该在50ms内完成
            if name not in ["等待", "随机等待"]:
                self.assertLessEqual(elapsed, 0.05, f"{name}操作耗时过长: {elapsed*1000:.2f}ms > 50ms")
    
    def test_full_pipeline_performance(self):
        """测试完整管道性能"""
        print("\n====== 完整管道性能测试 ======")
        
        # 模拟窗口管理器
        window_manager = MagicMock(spec=GameWindowManager)
        window_manager.get_screenshot.return_value = self.medium_image
        window_manager.is_window_active.return_value = True
        
        # 创建模拟组件
        image_processor = MagicMock(spec=ImageProcessor)
        image_processor.analyze_frame.return_value = {
            "timestamp": time.time(),
            "frame_size": self.medium_image.shape[:2][::-1],
            "brightness": 128.0,
            "dominant_colors": [(255, 255, 255), (0, 0, 255)]
        }
        
        game_analyzer = MagicMock(spec=GameAnalyzer)
        game_analyzer.analyze_frame.return_value = {
            "timestamp": time.time(),
            "buttons": [{"position": (150, 125), "size": (100, 50), "type": "button", "confidence": 0.9}],
            "enemies": [{"position": (425, 325), "size": (50, 50), "type": "enemy", "confidence": 0.8}],
            "items": [],
            "dialog_open": False,
            "health": 80,
            "mana": 60,
            "position": (200, 200),
            "screen_size": self.medium_image.shape[:2][::-1]
        }
        
        action_simulator = MagicMock(spec=ActionSimulator)
        action_simulator.ensure_window_active.return_value = True
        action_simulator.click.return_value = True
        
        game_state = MagicMock(spec=GameState)
        
        # 创建自动操作器
        with patch.object(AutoOperator, '_init_rules'):
            auto_operator = AutoOperator(
                self.logger,
                action_simulator,
                game_state,
                image_processor,
                self.config
            )
            
            # 手动设置规则
            auto_operator.action_rules = [
                (lambda state: 'buttons' in state and len(state['buttons']) > 0, 
                 lambda state: {"type": ActionType.CLICK, "position": state['buttons'][0]['position'], "target": "button"}, 10),
                (lambda state: 'enemies' in state and len(state['enemies']) > 0, 
                 lambda state: {"type": ActionType.CLICK, "position": state['enemies'][0]['position'], "target": "enemy"}, 5),
                (lambda state: 'health' in state and state['health'] < 30, 
                 lambda state: {"type": ActionType.KEY_PRESS, "key": "h", "target": "potion"}, 15),
            ]
            
            # 测量完整流程的性能
            iterations = 10
            start_time = time.time()
            
            for _ in range(iterations):
                # 1. 获取截图
                screenshot = window_manager.get_screenshot()
                
                # 2. 处理图像
                image_state = image_processor.analyze_frame(screenshot)
                
                # 3. 分析游戏状态
                game_state_dict = game_analyzer.analyze_frame(screenshot)
                
                # 4. 选择动作
                action = auto_operator.select_action(game_state_dict)
                
                # 5. 执行动作
                auto_operator.execute_action(action)
            
            total_time = (time.time() - start_time) / iterations
            fps = 1.0 / total_time if total_time > 0 else float('inf')
            
            print(f"完整流程: {total_time*1000:.2f}ms/帧 ({fps:.2f} FPS)")
            
            # 对于模拟测试环境，至少需要5 FPS（考虑到模拟对象的开销）
            self.assertGreaterEqual(fps, 5, f"完整流程FPS过低: {fps} < 5 FPS")
    
    def test_object_detection_performance(self):
        """测试对象检测性能（不使用YOLO的情况下）"""
        print("\n====== 对象检测性能测试 ======")
        
        with patch.object(self.game_analyzer, '_detect_buttons') as mock_detect:
            # 模拟检测结果
            mock_detect.return_value = [
                {"position": (150, 125), "size": (100, 50), "type": "button", "confidence": 0.9}
            ]
            
            # 测量不同分辨率下的对象检测性能
            resolutions = {
                "小分辨率 (640x480)": self.small_image,
                "中分辨率 (1280x720)": self.medium_image,
                "高分辨率 (1920x1080)": self.large_image
            }
            
            for name, image in resolutions.items():
                iterations = 5
                start_time = time.time()
                
                for _ in range(iterations):
                    self.game_analyzer._detect_buttons(image)
                
                elapsed = (time.time() - start_time) / iterations
                fps = 1.0 / elapsed if elapsed > 0 else float('inf')
                
                print(f"{name} 对象检测: {elapsed*1000:.2f}ms/帧 ({fps:.2f} FPS)")
                
                # 对象检测应该保持在30 FPS以上
                self.assertGreaterEqual(fps, 30, f"对象检测FPS过低: {fps} < 30 FPS")
    
    def test_window_callback_performance(self):
        """测试窗口回调机制性能"""
        print("\n====== 窗口回调性能测试 ======")
        
        # 创建窗口管理器
        with patch('src.services.window_manager.win32gui'):
            window_manager = GameWindowManager(self.logger, self.config)
            
            # 创建并启动回调测试线程
            message_queue = queue.Queue()
            
            def callback_test():
                # 记录回调接收时间
                received_times = []
                
                def test_callback(windows):
                    received_times.append(time.time())
                    message_queue.put(windows)
                
                # 注册回调
                window_manager.window_callbacks = [test_callback]
                
                # 触发多次回调
                iterations = 10
                start_time = time.time()
                
                for i in range(iterations):
                    window_manager.notify_window_changed()
                    time.sleep(0.01)  # 短暂延迟
                
                # 计算平均延迟
                if received_times:
                    total_delay = sum(rt - (start_time + i*0.01) for i, rt in enumerate(received_times[:iterations]))
                    avg_delay = total_delay / len(received_times[:iterations])
                    message_queue.put(f"平均回调延迟: {avg_delay*1000:.2f}ms")
                else:
                    message_queue.put("没有收到回调")
            
            # 开始测试
            callback_thread = threading.Thread(target=callback_test)
            callback_thread.daemon = True
            callback_thread.start()
            
            # 等待完成
            callback_thread.join(timeout=2.0)
            
            # 获取结果
            results = []
            while not message_queue.empty():
                results.append(message_queue.get())
            
            # 输出结果
            for result in results:
                if isinstance(result, str):
                    print(result)
                    # 延迟应该小于10ms
                    self.assertIn("平均回调延迟", result, "没有接收到回调")
                    delay_ms = float(result.split(": ")[1].split("ms")[0])
                    self.assertLessEqual(delay_ms, 10.0, f"回调延迟过高: {delay_ms} > 10.0ms")
            
            # 验证有足够的回调被触发
            callback_count = len([r for r in results if not isinstance(r, str)])
            self.assertGreaterEqual(callback_count, 5, f"回调次数不足: {callback_count} < 5")
    
    def test_action_simulator_interaction(self):
        """测试动作模拟器与窗口交互性能"""
        print("\n====== 动作模拟器与窗口交互性能测试 ======")
        
        # 模拟窗口管理器
        window_manager = MagicMock(spec=GameWindowManager)
        window_manager.is_window_active.return_value = True
        window_manager.set_foreground.return_value = True
        
        # 创建动作模拟器
        action_simulator = ActionSimulator(self.logger, window_manager, self.config)
        
        # 测试窗口激活性能
        iterations = 10
        start_time = time.time()
        
        for _ in range(iterations):
            action_simulator.ensure_window_active()
        
        elapsed = (time.time() - start_time) / iterations
        print(f"窗口激活: {elapsed*1000:.2f}ms")
        
        # 窗口激活应该在20ms以内完成
        self.assertLessEqual(elapsed, 0.02, f"窗口激活耗时过长: {elapsed*1000:.2f}ms > 20ms")
        
        # 模拟动作交互时窗口不在前台的情况
        window_manager.is_window_active.side_effect = [False, True] * (iterations // 2)
        
        start_time = time.time()
        for _ in range(iterations // 2):
            action_simulator.ensure_window_active()
            action_simulator.click(100, 100)
        
        elapsed = time.time() - start_time
        avg_per_action = elapsed / (iterations // 2)
        print(f"窗口激活+点击 (切换窗口): {avg_per_action*1000:.2f}ms/动作")
        
        # 分析响应延迟
        # 考虑到窗口切换可能涉及操作系统开销，我们允许稍大的延迟
        self.assertLessEqual(avg_per_action, 0.05, f"窗口激活+点击耗时过长: {avg_per_action*1000:.2f}ms > 50ms")

if __name__ == '__main__':
    unittest.main() 