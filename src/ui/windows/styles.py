"""应用样式表"""

APP_STYLE = """
/* 全局样式 */
QMainWindow, QWidget {
    background-color: #1a1a1a;
    color: #e0e0e0;
}

/* 顶部控制栏 */
#topBar {
    background-color: #2d2d2d;
    border-radius: 8px;
    padding: 5px;
    margin: 5px;
}

/* 下拉框样式 */
QComboBox {
    background-color: #3d3d3d;
    border: 1px solid #0088ff;
    border-radius: 4px;
    padding: 5px;
    color: #ffffff;
    min-width: 150px;
}

QComboBox:hover {
    border: 1px solid #00aaff;
    background-color: #454545;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox::down-arrow {
    border: none;
    background: #0088ff;
    width: 8px;
    height: 8px;
    border-radius: 4px;
}

/* 按钮样式 */
QPushButton {
    background-color: #2d5a88;
    color: #ffffff;
    border: none;
    border-radius: 4px;
    padding: 8px 15px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #3d6a98;
    border: 1px solid #00aaff;
}

QPushButton:pressed {
    background-color: #1d4a78;
}

QPushButton:disabled {
    background-color: #404040;
    color: #808080;
}

/* 开始按钮特殊样式 */
#startButton {
    background-color: #2d884d;
}

#startButton:hover {
    background-color: #3d985d;
    border: 1px solid #40ff80;
}

#startButton:pressed {
    background-color: #1d783d;
}

/* 停止按钮特殊样式 */
#stopButton {
    background-color: #883d3d;
}

#stopButton:hover {
    background-color: #984d4d;
    border: 1px solid #ff4040;
}

#stopButton:pressed {
    background-color: #782d2d;
}

/* 暂停按钮特殊样式 */
#pauseButton {
    background-color: #886d2d;
}

#pauseButton:hover {
    background-color: #987d3d;
    border: 1px solid #ffaa40;
}

#pauseButton:pressed {
    background-color: #785d1d;
}

/* 右侧面板样式 */
#rightPanel {
    background-color: #2d2d2d;
    border-radius: 8px;
    padding: 10px;
    margin: 5px;
}

/* 分组框样式 */
QGroupBox {
    border: 2px solid #3d3d3d;
    border-radius: 8px;
    margin-top: 1em;
    padding-top: 10px;
    color: #00aaff;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 5px;
    background-color: #2d2d2d;
}

/* 表格样式 */
QTableWidget {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    gridline-color: #3d3d3d;
}

QTableWidget::item {
    padding: 5px;
    border-bottom: 1px solid #3d3d3d;
}

QTableWidget::item:selected {
    background-color: #2d5a88;
}

QHeaderView::section {
    background-color: #3d3d3d;
    color: #00aaff;
    padding: 5px;
    border: none;
    font-weight: bold;
}

/* 滚动条样式 */
QScrollBar:vertical {
    border: none;
    background-color: #2d2d2d;
    width: 10px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #4d4d4d;
    border-radius: 5px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #5d5d5d;
}

/* 状态栏样式 */
QStatusBar {
    background-color: #2d2d2d;
    color: #00aaff;
    border-top: 1px solid #3d3d3d;
}

QStatusBar::item {
    border: none;
}

/* 标签页样式 */
QTabWidget::pane {
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    background-color: #2d2d2d;
}

QTabBar::tab {
    background-color: #3d3d3d;
    color: #e0e0e0;
    padding: 8px 15px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #2d5a88;
    color: #ffffff;
}

QTabBar::tab:hover:!selected {
    background-color: #454545;
}

/* 复选框样式 */
QCheckBox {
    color: #e0e0e0;
    spacing: 5px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 3px;
    border: 2px solid #3d3d3d;
}

QCheckBox::indicator:unchecked {
    background-color: #2d2d2d;
}

QCheckBox::indicator:checked {
    background-color: #2d5a88;
}

QCheckBox::indicator:checked::after {
    content: "";
    position: absolute;
    width: 10px;
    height: 10px;
    background-color: #00aaff;
    border-radius: 2px;
    margin: 4px;
}

/* 数值调节框样式 */
QSpinBox, QDoubleSpinBox {
    background-color: #3d3d3d;
    border: 1px solid #0088ff;
    border-radius: 4px;
    padding: 5px;
    color: #ffffff;
}

QSpinBox:hover, QDoubleSpinBox:hover {
    border: 1px solid #00aaff;
    background-color: #454545;
}

/* 标签样式 */
QLabel {
    color: #e0e0e0;
}

QLabel#windowLabel, QLabel#statusLabel {
    color: #00aaff;
    font-weight: bold;
    background-color: transparent;
    padding: 5px;
    border-radius: 4px;
}

/* 游戏视图样式 */
#gameView {
    background-color: #1a1a1a;
    border: 2px solid #3d3d3d;
    border-radius: 8px;
}

/* 图表样式 */
#historyChart {
    background-color: #2d2d2d;
    border-radius: 8px;
    border: 1px solid #3d3d3d;
}

/* 日期时间编辑器样式 */
QDateTimeEdit {
    background-color: #3d3d3d;
    border: 1px solid #0088ff;
    border-radius: 4px;
    padding: 5px;
    color: #ffffff;
}

QDateTimeEdit:hover {
    border: 1px solid #00aaff;
    background-color: #454545;
}

QDateTimeEdit::drop-down {
    border: none;
    width: 20px;
}

QDateTimeEdit::down-arrow {
    border: none;
    background: #0088ff;
    width: 8px;
    height: 8px;
    border-radius: 4px;
}

/* 工具提示样式 */
QToolTip {
    background-color: #2d2d2d;
    color: #00aaff;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    padding: 5px;
}
"""

# 动画时长
ANIMATION_DURATION = """
    * {
        transition: all 200ms ease-in-out;
    }
"""

# 主面板样式
PANEL_STYLE = """
    QFrame {
        background-color: #2d2d2d;
        border-radius: 10px;
        border: 1px solid #3d3d3d;
    }
"""

# 导航按钮样式
NAV_BUTTON_STYLE = """
    QPushButton {
        background-color: #2d2d2d;
        border-radius: 8px;
        padding: 8px;
        margin: 4px;
        text-align: center;
        border: 1px solid transparent;
        transition: all 200ms ease-in-out;
    }
    QPushButton:hover {
        background-color: #3d3d3d;
        border: 1px solid #4d4d4d;
        transform: translateY(-2px);
    }
    QPushButton:pressed {
        background-color: #4d4d4d;
        transform: translateY(1px);
    }
    QPushButton:checked {
        background-color: #4d4d4d;
        border: 1px solid #5d5d5d;
    }
"""

# 标题栏按钮样式
TITLE_BUTTON_STYLE = """
    QPushButton {
        background-color: transparent;
        border-radius: 15px;
        font-family: 'Microsoft YaHei';
        font-size: 16px;
        color: #ffffff;
        padding: 5px;
        margin: 2px;
        transition: all 200ms ease-in-out;
    }
    QPushButton:hover {
        background-color: rgba(255, 255, 255, 0.1);
    }
    QPushButton#closeButton:hover {
        background-color: #ff4444;
    }
"""

# 标题标签样式
TITLE_LABEL_STYLE = """
    QLabel {
        color: #ffffff;
        font-size: 16px;
        font-weight: bold;
        padding: 10px 0;
    }
"""

# 普通标签样式
LABEL_STYLE = """
    QLabel {
        color: #cccccc;
        font-size: 12px;
        transition: color 200ms ease-in-out;
    }
    QLabel:hover {
        color: #ffffff;
    }
"""

# 输入框样式
INPUT_STYLE = """
    QLineEdit, QSpinBox, QComboBox {
        background-color: #1e1e1e;
        border: 1px solid #3d3d3d;
        border-radius: 5px;
        padding: 5px 10px;
        color: #ffffff;
        font-size: 12px;
        selection-background-color: #2196F3;
        selection-color: #ffffff;
        transition: all 200ms ease-in-out;
    }
    QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
        border: 1px solid #2196F3;
        background-color: #2a2a2a;
    }
    QLineEdit:hover, QSpinBox:hover, QComboBox:hover {
        border: 1px solid #4d4d4d;
        background-color: #252525;
    }
    QComboBox::drop-down {
        border: none;
        width: 20px;
    }
    QComboBox::down-arrow {
        image: url(:/resources/down-arrow.png);
        width: 12px;
        height: 12px;
    }
    QSpinBox::up-button, QSpinBox::down-button {
        background-color: #2d2d2d;
        border: none;
        border-radius: 3px;
        margin: 1px;
    }
    QSpinBox::up-button:hover, QSpinBox::down-button:hover {
        background-color: #3d3d3d;
    }
    QSpinBox::up-button:pressed, QSpinBox::down-button:pressed {
        background-color: #4d4d4d;
    }
"""

# 列表样式
LIST_STYLE = """
    QListWidget {
        background-color: #1e1e1e;
        border: 1px solid #3d3d3d;
        border-radius: 5px;
        padding: 5px;
        color: #ffffff;
    }
    QListWidget::item {
        padding: 8px;
        border-radius: 3px;
        margin: 2px;
        transition: all 200ms ease-in-out;
    }
    QListWidget::item:hover {
        background-color: #3d3d3d;
    }
    QListWidget::item:selected {
        background-color: #2196F3;
        color: #ffffff;
    }
    QScrollBar:vertical {
        border: none;
        background-color: #2d2d2d;
        width: 8px;
        border-radius: 4px;
    }
    QScrollBar::handle:vertical {
        background-color: #4d4d4d;
        border-radius: 4px;
    }
    QScrollBar::handle:vertical:hover {
        background-color: #5d5d5d;
    }
"""

# 主要按钮样式
PRIMARY_BUTTON_STYLE = """
    QPushButton {
        background-color: #2196F3;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 8px 16px;
        font-weight: bold;
        text-align: center;
        transition: all 200ms ease-in-out;
    }
    QPushButton:hover {
        background-color: #1976D2;
        transform: translateY(-1px);
    }
    QPushButton:pressed {
        background-color: #0D47A1;
        transform: translateY(1px);
    }
    QPushButton:disabled {
        background-color: #666666;
        transform: none;
    }
"""

# 次要按钮样式
SECONDARY_BUTTON_STYLE = """
    QPushButton {
        background-color: #424242;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 8px 16px;
        text-align: center;
        transition: all 200ms ease-in-out;
    }
    QPushButton:hover {
        background-color: #4d4d4d;
        transform: translateY(-1px);
    }
    QPushButton:pressed {
        background-color: #595959;
        transform: translateY(1px);
    }
    QPushButton:disabled {
        background-color: #666666;
        transform: none;
    }
"""

# 危险按钮样式
DANGER_BUTTON_STYLE = """
    QPushButton {
        background-color: #f44336;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 8px 16px;
        font-weight: bold;
        text-align: center;
        transition: all 200ms ease-in-out;
    }
    QPushButton:hover {
        background-color: #d32f2f;
        transform: translateY(-1px);
    }
    QPushButton:pressed {
        background-color: #b71c1c;
        transform: translateY(1px);
    }
    QPushButton:disabled {
        background-color: #666666;
        transform: none;
    }
"""

# 分割线样式
SEPARATOR_STYLE = """
    QFrame[frameShape="4"] {
        color: #3d3d3d;
        margin: 5px 0;
    }
"""

# 主框架样式
MAIN_FRAME_STYLE = """
    QFrame {
        background-color: #2d2d2d;
        border-radius: 10px;
        border: 1px solid #3d3d3d;
    }
""" 