import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
import random
from collections import deque
from typing import Dict, List, Tuple, Optional
from PyQt6.QtCore import QObject, pyqtSignal
from .config import Config
from .logger import GameLogger

# 可选依赖导入
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    YOLO = None

class DQN(nn.Module):
    """深度Q网络模型"""
    
    def __init__(self, state_size: int, action_size: int, config: Config, logger: GameLogger):
        """
        初始化DQN模型
        
        Args:
            state_size: 状态空间大小
            action_size: 动作空间大小
            config: 配置对象
            logger: 日志对象
        """
        super(DQN, self).__init__()
        
        self.config = config
        self.logger = logger
        
        # 获取DQN配置
        if hasattr(config, 'get_dqn_config'):
            dqn_config = config.get_dqn_config()
            hidden_size = dqn_config.get('hidden_size', 128)
        else:
            hidden_size = 128
        
        # 定义网络层
        self.fc1 = nn.Linear(state_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, action_size)
        
        logger.info(f"初始化DQN模型，状态大小: {state_size}, 动作大小: {action_size}")
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        前向传播
        
        Args:
            x: 输入状态
            
        Returns:
            动作值
        """
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.fc3(x)

class DQNAgent(QObject):
    """DQN强化学习代理"""
    
    # 定义信号
    training_started = pyqtSignal()  # 训练开始信号
    training_finished = pyqtSignal()  # 训练完成信号
    training_progress = pyqtSignal(float)  # 训练进度信号
    model_updated = pyqtSignal(float)  # 模型更新信号
    epsilon_updated = pyqtSignal(float)  # 探索率更新信号
    
    def __init__(self, config: Config, logger: GameLogger, game_state, action_simulator):
        """
        初始化DQN代理
        
        Args:
            config: 配置对象
            logger: 日志对象
            game_state: 游戏状态对象
            action_simulator: 动作模拟器对象
        """
        super().__init__()
        self.config = config
        self.logger = logger
        self.game_state = game_state
        self.action_simulator = action_simulator
        
        # 获取DQN配置
        if hasattr(config, 'get_dqn_config'):
            dqn_config = config.get_dqn_config()
            self.state_size = dqn_config.get('state_size', 84)
            self.action_size = dqn_config.get('action_size', 4)
            memory_size = dqn_config.get('memory_size', 10000)
            device = dqn_config.get('device', 'cpu')
            learning_rate = dqn_config.get('learning_rate', 0.001)
            self.gamma = dqn_config.get('gamma', 0.99)
            self.epsilon = dqn_config.get('initial_epsilon', 1.0)
            self.epsilon_min = dqn_config.get('min_epsilon', 0.01)
            self.epsilon_decay = dqn_config.get('epsilon_decay', 0.995)
            self.batch_size = dqn_config.get('batch_size', 32)
        else:
            # 使用默认值
            self.state_size = 84
            self.action_size = 4
            memory_size = 10000
            device = 'cpu'
            learning_rate = 0.001
            self.gamma = 0.99
            self.epsilon = 1.0
            self.epsilon_min = 0.01
            self.epsilon_decay = 0.995
            self.batch_size = 32
        
        # 初始化经验回放缓冲区
        self.memory = deque(maxlen=memory_size)
        
        # 初始化Q网络和目标网络
        self.device = torch.device(device)
        self.model = DQN(self.state_size, self.action_size, config, logger).to(self.device)
        self.target_model = DQN(self.state_size, self.action_size, config, logger).to(self.device)
        self.target_model.load_state_dict(self.model.state_dict())
        
        # 初始化优化器
        self.optimizer = optim.Adam(
            self.model.parameters(), 
            lr=learning_rate
        )
        
        logger.info(f"初始化DQN代理，状态大小: {self.state_size}, 动作大小: {self.action_size}")
        
        # 初始化YOLOv5模型（如果可用）
        if YOLO_AVAILABLE:
            try:
                self.yolo_model = YOLO('yolov5n.pt')
                logger.info("YOLO模型初始化成功")
            except Exception as e:
                logger.warning(f"YOLO模型初始化失败: {e}")
                self.yolo_model = None
        else:
            logger.warning("ultralytics库不可用，DQN将不使用YOLO特征")
            self.yolo_model = None
        
        # 发送初始信号
        self.epsilon_updated.emit(self.epsilon)
    
    def remember(self, state: np.ndarray, action: int, reward: float, 
                next_state: np.ndarray, done: bool):
        """
        存储经验到回放缓冲区
        
        Args:
            state: 当前状态
            action: 执行的动作
            reward: 获得的奖励
            next_state: 下一个状态
            done: 是否结束
        """
        self.memory.append((state, action, reward, next_state, done))
    
    def act(self, state: np.ndarray) -> int:
        """
        根据当前状态选择动作
        
        Args:
            state: 当前状态
            
        Returns:
            选择的动作
        """
        if random.random() < self.epsilon:
            # 探索：随机选择动作
            action = random.randrange(self.action_size)
            self.logger.debug(f"探索: 随机选择动作 {action}")
        else:
            # 利用：选择最优动作
            state = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            with torch.no_grad():
                q_values = self.model(state)
            action = q_values.argmax().item()
            self.logger.debug(f"利用: 选择最优动作 {action}")
        
        return action
    
    def replay(self):
        """
        从经验回放缓冲区中学习
        """
        if len(self.memory) < self.batch_size:
            return
            
        self.training_started.emit()
        try:
            # 从缓冲区中随机采样
            batch = random.sample(self.memory, self.batch_size)
            states, actions, rewards, next_states, dones = zip(*batch)
            
            # 转换为张量
            states = torch.FloatTensor(states).to(self.device)
            actions = torch.LongTensor(actions).to(self.device)
            rewards = torch.FloatTensor(rewards).to(self.device)
            next_states = torch.FloatTensor(next_states).to(self.device)
            dones = torch.FloatTensor(dones).to(self.device)
            
            # 计算当前Q值
            current_q_values = self.model(states).gather(1, actions.unsqueeze(1))
            
            # 计算目标Q值
            with torch.no_grad():
                next_q_values = self.target_model(next_states).max(1)[0]
                target_q_values = rewards + (1 - dones) * self.gamma * next_q_values
            
            # 计算损失
            loss = F.mse_loss(current_q_values.squeeze(), target_q_values)
            
            # 优化模型
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
            
            # 发送训练进度信号
            self.training_progress.emit(loss.item())
            self.model_updated.emit(loss.item())
            
            self.logger.debug(f"训练损失: {loss.item():.4f}")
        finally:
            self.training_finished.emit()
    
    def update_target_model(self):
        """更新目标网络"""
        self.target_model.load_state_dict(self.model.state_dict())
        self.logger.debug("更新目标网络")
    
    def decay_epsilon(self):
        """衰减探索率"""
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
            self.epsilon_updated.emit(self.epsilon)
            self.logger.debug(f"探索率衰减至: {self.epsilon:.4f}")
    
    def save(self, path: str):
        """
        保存模型
        
        Args:
            path: 保存路径
        """
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'target_model_state_dict': self.target_model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon
        }, path)
        self.logger.info(f"保存模型到: {path}")
    
    def load(self, path: str):
        """
        加载模型
        
        Args:
            path: 加载路径
        """
        checkpoint = torch.load(path)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.target_model.load_state_dict(checkpoint['target_model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.epsilon = checkpoint['epsilon']
        self.epsilon_updated.emit(self.epsilon)
        self.logger.info(f"从 {path} 加载模型")
    
    def get_state_from_image(self, image: np.ndarray) -> np.ndarray:
        """
        从图像中提取状态向量
        
        Args:
            image: 游戏画面
            
        Returns:
            状态向量
        """
        # 检查YOLO模型是否可用
        if not self.yolo_model:
            # 如果没有YOLO模型，返回基本的图像特征
            # 例如：图像的统计特征
            gray = np.mean(image, axis=2) if len(image.shape) == 3 else image
            # 计算图像的基本统计特征
            features = [
                np.mean(gray),      # 平均亮度
                np.std(gray),       # 亮度标准差
                np.min(gray),       # 最小亮度
                np.max(gray),       # 最大亮度
            ]
            # 确保返回正确的状态大小
            while len(features) < self.state_size:
                features.append(0.0)
            return np.array(features[:self.state_size])
        
        try:
            # 使用YOLOv5检测元素
            results = self.yolo_model(image)
            
            # 提取状态特征
            state = []
            
            # 添加每个类别的元素数量
            for class_name in self.yolo_model.names.values():
                count = 0
                for result in results:
                    boxes = result.boxes
                    if boxes is None:
                        continue
                    for box in boxes:
                        cls_id = int(box.cls[0])
                        if cls_id in self.yolo_model.names and self.yolo_model.names[cls_id] == class_name:
                            count += 1
                state.append(count)
            
            # 添加元素位置信息
            for result in results:
                boxes = result.boxes
                if boxes is None:
                    continue
                for box in boxes:
                    # 获取边界框坐标
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    # 计算中心点坐标
                    center_x = (x1 + x2) / 2 / image.shape[1]  # 归一化
                    center_y = (y1 + y2) / 2 / image.shape[0]  # 归一化
                    state.extend([center_x, center_y])
            
            # 确保返回正确的状态大小
            while len(state) < self.state_size:
                state.append(0.0)
            
            return np.array(state[:self.state_size])
            
        except Exception as e:
            self.logger.error(f"YOLO状态提取失败: {e}")
            # 返回零状态
            return np.zeros(self.state_size) 