"""应用程序样式表"""

# 主窗口样式
MAIN_WINDOW_STYLE = """
QMainWindow {
    background-color: #f0f0f0;
}

QFrame {
    background-color: white;
    border: 1px solid #cccccc;
    border-radius: 5px;
    padding: 10px;
}

QGroupBox {
    background-color: white;
    border: 1px solid #cccccc;
    border-radius: 5px;
    padding: 10px;
    margin-top: 10px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
}
"""

# 按钮样式
BUTTON_STYLE = """
QPushButton {
    background-color: #4a90e2;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #357abd;
}

QPushButton:pressed {
    background-color: #2d6da3;
}

QPushButton:disabled {
    background-color: #cccccc;
    color: #666666;
}
"""

# 标签样式
LABEL_STYLE = """
QLabel {
    color: #333333;
    font-size: 14px;
}

QLabel[state="error"] {
    color: #e74c3c;
}

QLabel[state="success"] {
    color: #2ecc71;
}

QLabel[state="warning"] {
    color: #f39c12;
}
"""

# 下拉框样式
COMBO_BOX_STYLE = """
QComboBox {
    border: 1px solid #cccccc;
    border-radius: 4px;
    padding: 5px;
    background-color: white;
    min-width: 200px;
}

QComboBox:hover {
    border-color: #4a90e2;
}

QComboBox:disabled {
    background-color: #f0f0f0;
    color: #666666;
}
"""

# 进度条样式
PROGRESS_BAR_STYLE = """
QProgressBar {
    border: 1px solid #cccccc;
    border-radius: 4px;
    text-align: center;
    background-color: #f0f0f0;
}

QProgressBar::chunk {
    background-color: #4a90e2;
    border-radius: 3px;
}
"""

# 状态标签样式
STATE_LABEL_STYLE = """
QLabel[state="normal"] {
    color: #333333;
}

QLabel[state="critical"] {
    color: #e74c3c;
    font-weight: bold;
}

QLabel[state="warning"] {
    color: #f39c12;
}

QLabel[state="good"] {
    color: #2ecc71;
}
"""

# 游戏状态显示样式
GAME_STATE_STYLE = """
QGroupBox#gameState {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 5px;
    padding: 15px;
}

QGroupBox#gameState QLabel {
    color: #495057;
    font-size: 13px;
}

QGroupBox#gameState QLabel[state="value"] {
    color: #212529;
    font-weight: bold;
}
"""

# 状态显示样式
STATE_STYLE = """
QGroupBox#gameState {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 15px;
    margin-top: 10px;
}

QGroupBox#gameState QLabel#stateIcon {
    font-size: 16px;
    min-width: 20px;
    text-align: center;
}

QGroupBox#gameState QLabel#stateName {
    color: #495057;
    font-size: 13px;
    min-width: 80px;
}

QGroupBox#gameState QLabel#stateValue {
    color: #212529;
    font-weight: bold;
    font-size: 13px;
    min-width: 60px;
}

QGroupBox#gameState QWidget#stateContainer[state="normal"] {
    background-color: transparent;
}

QGroupBox#gameState QWidget#stateContainer[state="warning"] {
    background-color: #fff3cd;
    border-radius: 4px;
    padding: 2px 5px;
}

QGroupBox#gameState QWidget#stateContainer[state="critical"] {
    background-color: #f8d7da;
    border-radius: 4px;
    padding: 2px 5px;
}

QGroupBox#gameState QWidget#stateContainer[state="good"] {
    background-color: #d4edda;
    border-radius: 4px;
    padding: 2px 5px;
}

QGroupBox#gameState QWidget#stateContainer:hover {
    background-color: #e9ecef;
    border-radius: 4px;
    padding: 2px 5px;
}
"""

# 状态历史记录样式
HISTORY_STYLE = """
QFrame#controlPanel {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 10px;
}

QFrame#statsPanel {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 10px;
}

QTabWidget#historyTabs {
    background-color: white;
    border: 1px solid #dee2e6;
    border-radius: 8px;
}

QTabWidget#historyTabs::pane {
    border: 1px solid #dee2e6;
    border-radius: 8px;
    background-color: white;
}

QTabWidget#historyTabs::tab-bar {
    alignment: left;
}

QTabWidget#historyTabs QTabBar::tab {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 8px 16px;
    margin-right: 2px;
}

QTabWidget#historyTabs QTabBar::tab:selected {
    background-color: white;
    border-bottom-color: white;
}

QTabWidget#historyTabs QTabBar::tab:hover {
    background-color: #e9ecef;
}

QTableWidget#historyTable {
    background-color: white;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    gridline-color: #dee2e6;
}

QTableWidget#historyTable::item {
    padding: 5px;
}

QTableWidget#historyTable::item:selected {
    background-color: #e9ecef;
    color: #212529;
}

QHeaderView::section {
    background-color: #f8f9fa;
    padding: 5px;
    border: 1px solid #dee2e6;
    font-weight: bold;
}

QDateTimeEdit {
    border: 1px solid #ced4da;
    border-radius: 4px;
    padding: 5px;
    background-color: white;
}

QDateTimeEdit:hover {
    border-color: #80bdff;
}

QDateTimeEdit:focus {
    border-color: #80bdff;
    outline: 0;
    box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

QPushButton#queryButton, QPushButton#exportButton {
    background-color: #4a90e2;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
}

QPushButton#queryButton:hover, QPushButton#exportButton:hover {
    background-color: #357abd;
}

QPushButton#queryButton:pressed, QPushButton#exportButton:pressed {
    background-color: #2d6da3;
}

QPushButton#queryButton:disabled, QPushButton#exportButton:disabled {
    background-color: #cccccc;
    color: #666666;
}

/* 图表样式 */
FigureCanvas {
    background-color: white;
    border: 1px solid #dee2e6;
    border-radius: 8px;
}
"""

# 组合所有样式
APP_STYLE = f"""
{MAIN_WINDOW_STYLE}
{BUTTON_STYLE}
{LABEL_STYLE}
{COMBO_BOX_STYLE}
{PROGRESS_BAR_STYLE}
{STATE_LABEL_STYLE}
{GAME_STATE_STYLE}
{STATE_STYLE}
{HISTORY_STYLE}
""" 