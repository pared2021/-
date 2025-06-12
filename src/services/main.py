import sys
import os
import cv2
import numpy as np
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QComboBox, 
                             QSpinBox, QDoubleSpinBox, QFileDialog)
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from .config import config
from .logger import logger
from .window_manager import GameWindowManager
from .image_processor import ImageProcessor
from .action_simulator import ActionSimulator
from .template_collector import TemplateCollector
from .dqn_agent import DQNAgent

class AutomationThread(QThread):
    """自动化线程"""
    
    frame_updated = Signal(np.ndarray)
    status_updated = Signal(str)
    
    def __init__(self, window_manager: GameWindowManager, 
                 image_processor: ImageProcessor,
                 action_simulator: ActionSimulator,
                 dqn_agent: DQNAgent):
        super().__init__()
        self.window_manager = window_manager
        self.image_processor = image_processor
        self.action_simulator = action_simulator
        self.dqn_agent = dqn_agent
        self.running = False
    
    def run(self):
        """运行自动化任务"""
        self.running = True
        logger.info("开始自动化任务")
        
        while self.running:
            try:
                # 确保窗口激活
                if not self.window_manager.is_window_active():
                    self.status_updated.emit("窗口未激活")
                    logger.warning("游戏窗口未激活")
                    continue
                
                # 获取游戏画面
                frame = self.window_manager.capture_window()
                if frame is None:
                    self.status_updated.emit("无法获取游戏画面")
                    logger.error("无法获取游戏画面")
                    continue
                
                # 更新画面
                self.frame_updated.emit(frame)
                
                # 获取游戏状态
                state = self.image_processor.get_state_vector(frame)
                
                # 选择动作
                action = self.dqn_agent.act(state)
                
                # 执行动作
                self._execute_action(action)
                
                # 获取奖励
                reward = self._get_reward(frame)
                
                # 获取下一个状态
                next_frame = self.window_manager.capture_window()
                if next_frame is not None:
                    next_state = self.image_processor.get_state_vector(next_frame)
                    
                    # 存储经验
                    self.dqn_agent.remember(state, action, reward, next_state, False)
                    
                    # 训练模型
                    self.dqn_agent.replay()
                    
                    # 更新目标网络
                    if self.dqn_agent.steps % config.dqn.target_update == 0:
                        self.dqn_agent.update_target_model()
                    
                    # 衰减探索率
                    self.dqn_agent.decay_epsilon()
                
                # 更新状态
                self.status_updated.emit(f"动作: {action}, 奖励: {reward:.2f}")
                
            except Exception as e:
                logger.error(f"自动化任务出错: {str(e)}")
                self.status_updated.emit(f"错误: {str(e)}")
    
    def stop(self):
        """停止自动化任务"""
        self.running = False
        logger.info("停止自动化任务")
    
    def _execute_action(self, action: int):
        """执行动作"""
        try:
            if action == 0:  # 左键点击
                self.action_simulator.click(100, 100)
            elif action == 1:  # 右键点击
                self.action_simulator.click(100, 100, button='right')
            elif action == 2:  # 移动
                self.action_simulator.move_to(200, 200)
            elif action == 3:  # 按键
                self.action_simulator.press_key('space')
            
            logger.debug(f"执行动作: {action}")
        except Exception as e:
            logger.error(f"执行动作失败: {str(e)}")
    
    def _get_reward(self, frame: np.ndarray) -> float:
        """获取奖励"""
        try:
            # 检测目标元素
            detections = self.image_processor.recognize(frame)
            
            # 计算奖励
            reward = 0.0
            for class_name, boxes in detections.items():
                if class_name in config.reward.target_classes:
                    reward += len(boxes) * config.reward.class_rewards[class_name]
            
            logger.debug(f"计算奖励: {reward:.2f}")
            return reward
        except Exception as e:
            logger.error(f"计算奖励失败: {str(e)}")
            return 0.0

class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("游戏自动化工具")
        self.setGeometry(100, 100, 1200, 800)
        
        # 初始化组件
        self.init_components()
        
        # 初始化管理器
        self.window_manager = GameWindowManager()
        self.image_processor = ImageProcessor()
        self.action_simulator = ActionSimulator(self.window_manager)
        self.template_collector = None
        self.dqn_agent = None
        
        logger.info("主窗口初始化完成")
    
    def init_components(self):
        """初始化界面组件"""
        # 创建主布局
        main_layout = QHBoxLayout()
        
        # 创建控制面板
        control_panel = QWidget()
        control_layout = QVBoxLayout()
        
        # 窗口选择
        window_layout = QHBoxLayout()
        window_layout.addWidget(QLabel("游戏窗口:"))
        self.window_combo = QComboBox()
        self.window_combo.currentIndexChanged.connect(self.on_window_selected)
        window_layout.addWidget(self.window_combo)
        self.refresh_button = QPushButton("刷新")
        self.refresh_button.clicked.connect(self.refresh_windows)
        window_layout.addWidget(self.refresh_button)
        control_layout.addLayout(window_layout)
        
        # 模板收集设置
        template_layout = QHBoxLayout()
        template_layout.addWidget(QLabel("收集时间(秒):"))
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(10, 3600)
        self.duration_spin.setValue(config.template.collect_duration)
        template_layout.addWidget(self.duration_spin)
        
        template_layout.addWidget(QLabel("间隔(秒):"))
        self.interval_spin = QDoubleSpinBox()
        self.interval_spin.setRange(0.1, 5.0)
        self.interval_spin.setValue(config.template.collect_interval)
        template_layout.addWidget(self.interval_spin)
        control_layout.addLayout(template_layout)
        
        # 模板收集按钮
        self.collect_button = QPushButton("开始收集模板")
        self.collect_button.clicked.connect(self.start_collect_templates)
        control_layout.addWidget(self.collect_button)
        
        self.analyze_button = QPushButton("分析模板")
        self.analyze_button.clicked.connect(self.analyze_templates)
        control_layout.addWidget(self.analyze_button)
        
        # YOLOv5设置
        yolo_layout = QHBoxLayout()
        yolo_layout.addWidget(QLabel("置信度阈值:"))
        self.confidence_spin = QDoubleSpinBox()
        self.confidence_spin.setRange(0.1, 1.0)
        self.confidence_spin.setValue(config.yolo.confidence_threshold)
        yolo_layout.addWidget(self.confidence_spin)
        control_layout.addLayout(yolo_layout)
        
        self.train_button = QPushButton("训练模型")
        self.train_button.clicked.connect(self.train_model)
        control_layout.addWidget(self.train_button)
        
        # 自动化控制
        self.start_button = QPushButton("开始自动化")
        self.start_button.clicked.connect(self.start_automation)
        control_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("停止自动化")
        self.stop_button.clicked.connect(self.stop_automation)
        self.stop_button.setEnabled(False)
        control_layout.addWidget(self.stop_button)
        
        # 状态显示
        self.status_label = QLabel("就绪")
        control_layout.addWidget(self.status_label)
        
        control_panel.setLayout(control_layout)
        control_panel.setFixedWidth(300)
        main_layout.addWidget(control_panel)
        
        # 创建显示面板
        display_panel = QWidget()
        display_layout = QVBoxLayout()
        
        self.frame_label = QLabel()
        self.frame_label.setAlignment(Qt.AlignCenter)
        display_layout.addWidget(self.frame_label)
        
        display_panel.setLayout(display_layout)
        main_layout.addWidget(display_panel)
        
        # 设置主窗口布局
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # 创建定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1000 // config.display.fps)
        
        logger.info("界面组件初始化完成")
    
    def refresh_windows(self):
        """刷新窗口列表"""
        try:
            self.window_combo.clear()
            windows = self.window_manager.list_windows()
            for window in windows:
                self.window_combo.addItem(window['title'], window['hwnd'])
            
            logger.info(f"刷新窗口列表，找到{len(windows)}个窗口")
        except Exception as e:
            logger.error(f"刷新窗口列表失败: {str(e)}")
    
    def on_window_selected(self, index: int):
        """窗口选择变化"""
        if index >= 0:
            hwnd = self.window_combo.currentData()
            try:
                self.window_manager.set_window(hwnd)
                self.template_collector = TemplateCollector(self.window_manager)
                
                # 初始化DQN代理
                state_size = len(self.image_processor.get_state_vector(
                    self.window_manager.capture_window()
                ))
                self.dqn_agent = DQNAgent(state_size, config.dqn.action_size)
                
                logger.info(f"选择窗口: {self.window_combo.currentText()}")
            except Exception as e:
                logger.error(f"选择窗口失败: {str(e)}")
    
    def start_collect_templates(self):
        """开始收集模板"""
        try:
            if self.template_collector is None:
                logger.error("未选择游戏窗口")
                return
            
            duration = self.duration_spin.value()
            interval = self.interval_spin.value()
            
            self.collect_button.setEnabled(False)
            self.analyze_button.setEnabled(False)
            
            # 在新线程中收集模板
            self.collect_thread = QThread()
            self.collect_thread.run = lambda: self.template_collector.collect_templates(
                duration, interval
            )
            self.collect_thread.finished.connect(
                lambda: self.collect_button.setEnabled(True)
            )
            self.collect_thread.finished.connect(
                lambda: self.analyze_button.setEnabled(True)
            )
            self.collect_thread.start()
            
            logger.info(f"开始收集模板，持续时间: {duration}秒，间隔: {interval}秒")
        except Exception as e:
            logger.error(f"开始收集模板失败: {str(e)}")
    
    def analyze_templates(self):
        """分析模板"""
        try:
            if self.template_collector is None:
                logger.error("未选择游戏窗口")
                return
            
            self.template_collector.analyze_existing_templates()
            logger.info("模板分析完成")
        except Exception as e:
            logger.error(f"分析模板失败: {str(e)}")
    
    def train_model(self):
        """训练模型"""
        try:
            data_yaml, _ = QFileDialog.getOpenFileName(
                self, "选择数据集配置文件", "", "YAML Files (*.yaml)"
            )
            if data_yaml:
                epochs = config.yolo.train_epochs
                self.template_collector.train_custom_model(data_yaml, epochs)
                logger.info(f"开始训练模型，配置文件: {data_yaml}")
        except Exception as e:
            logger.error(f"训练模型失败: {str(e)}")
    
    def start_automation(self):
        """开始自动化"""
        try:
            if self.dqn_agent is None:
                logger.error("未选择游戏窗口")
                return
            
            self.automation_thread = AutomationThread(
                self.window_manager,
                self.image_processor,
                self.action_simulator,
                self.dqn_agent
            )
            self.automation_thread.frame_updated.connect(self.update_frame)
            self.automation_thread.status_updated.connect(
                lambda status: self.status_label.setText(status)
            )
            self.automation_thread.start()
            
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            
            logger.info("开始自动化任务")
        except Exception as e:
            logger.error(f"开始自动化失败: {str(e)}")
    
    def stop_automation(self):
        """停止自动化"""
        try:
            if hasattr(self, 'automation_thread'):
                self.automation_thread.stop()
                self.automation_thread.wait()
                
                self.start_button.setEnabled(True)
                self.stop_button.setEnabled(False)
                
                logger.info("停止自动化任务")
        except Exception as e:
            logger.error(f"停止自动化失败: {str(e)}")
    
    def update_frame(self, frame: np.ndarray = None):
        """更新画面"""
        try:
            if frame is None:
                frame = self.window_manager.capture_window()
            
            if frame is not None:
                # 调整图像大小
                height, width = frame.shape[:2]
                max_size = config.display.max_size
                if width > max_size or height > max_size:
                    scale = max_size / max(width, height)
                    frame = cv2.resize(frame, None, fx=scale, fy=scale)
                
                # 转换为Qt图像
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                
                # 显示图像
                self.frame_label.setPixmap(QPixmap.fromImage(qt_image))
        except Exception as e:
            logger.error(f"更新画面失败: {str(e)}")

def main():
    """主函数"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 