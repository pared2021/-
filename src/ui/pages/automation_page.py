"""
自动化控制页面
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal
from qfluentwidgets import (
    PrimaryPushButton,
    ToggleButton,
    ComboBox,
    LineEdit,
    ScrollArea,
    FluentIcon,
    InfoBar,
    CardWidget,
)


class AutomationPage(ScrollArea):
    start_signal = Signal()
    stop_signal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.view = QWidget()
        self.vBoxLayout = QVBoxLayout(self.view)

        # 初始化UI
        self._init_ui()

        # 设置滚动区域
        self.setWidget(self.view)
        self.setWidgetResizable(True)

    def _init_ui(self):
        """初始化UI"""
        # 控制卡片
        self.control_card = CardWidget(self)
        self.control_layout = QVBoxLayout(self.control_card)

        # 添加控制按钮
        self.start_button = PrimaryPushButton("开始", self, icon=FluentIcon.PLAY)
        self.stop_button = PrimaryPushButton("停止", self, icon=FluentIcon.PAUSE)
        self.stop_button.setEnabled(False)

        # 添加设置选项
        settings_layout = QHBoxLayout()

        # 游戏选择
        game_layout = QVBoxLayout()
        game_layout.addWidget(QLabel("选择游戏:"))
        self.game_combo = ComboBox(self)
        self.game_combo.addItems(["游戏1", "游戏2", "游戏3"])
        game_layout.addWidget(self.game_combo)
        settings_layout.addLayout(game_layout)

        # 动作选择
        action_layout = QVBoxLayout()
        action_layout.addWidget(QLabel("选择动作:"))
        self.action_combo = ComboBox(self)
        self.action_combo.addItems(["动作1", "动作2", "动作3"])
        action_layout.addWidget(self.action_combo)
        settings_layout.addLayout(action_layout)

        # 添加到控制卡片
        self.control_layout.addLayout(settings_layout)
        control_buttons = QHBoxLayout()
        control_buttons.addWidget(self.start_button)
        control_buttons.addWidget(self.stop_button)
        self.control_layout.addLayout(control_buttons)

        # 状态卡片
        self.status_card = CardWidget(self)
        self.status_layout = QVBoxLayout(self.status_card)

        # 状态显示
        self.status_label = QLabel("当前状态: 未运行")
        self.status_layout.addWidget(self.status_label)

        # 添加到主布局
        self.vBoxLayout.addWidget(self.control_card)
        self.vBoxLayout.addWidget(self.status_card)
        self.vBoxLayout.addStretch()

        # 连接信号
        self.start_button.clicked.connect(self._on_start)
        self.stop_button.clicked.connect(self._on_stop)

    def _on_start(self):
        """开始按钮点击处理"""
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText("当前状态: 运行中")
        self.start_signal.emit()

    def _on_stop(self):
        """停止按钮点击处理"""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("当前状态: 已停止")
        self.stop_signal.emit()
