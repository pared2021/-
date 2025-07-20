"""现代化UI样式表 - 基于游戏界面设计"""

# 布局常量
LAYOUT_CONSTANTS = {
    'card_spacing': 4,           # 卡片间距
    'card_margin': (4, 4, 4, 4), # 卡片边距
    'content_margin': (6, 6, 6, 6), # 内容边距
    'panel_spacing': 6,          # 面板间距
    'shadow_blur': 8,            # 阴影模糊半径
    'shadow_offset': (0, 2),     # 阴影偏移
    'border_radius': 12          # 圆角半径
}

# 现代化深色主题样式
MODERN_DARK_THEME = """
/* 主窗口样式 */
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #1a1a2e, stop:0.5 #16213e, stop:1 #0f3460);
    color: #ffffff;
}

/* 框架和容器样式 */
QFrame {
    background: rgba(26, 26, 46, 0.8);
    border: 1px solid rgba(74, 144, 226, 0.3);
    border-radius: 12px;
    padding: 15px;
}

QFrame:hover {
    background: rgba(26, 26, 46, 0.9);
    border: 1px solid rgba(74, 144, 226, 0.5);
}

/* 分组框样式 */
QGroupBox {
    background: rgba(26, 26, 46, 0.8);
    border: 2px solid rgba(74, 144, 226, 0.3);
    border-radius: 15px;
    padding: 20px;
    margin-top: 15px;
    font-weight: bold;
    font-size: 14px;
    color: #ffffff;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 5px 15px;
    background: rgba(74, 144, 226, 0.8);
    border-radius: 8px;
    color: #ffffff;
    font-weight: bold;
}

/* 现代化按钮样式 */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #4a90e2, stop:1 #357abd);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    font-weight: bold;
    font-size: 13px;
    min-height: 20px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #5ba0f2, stop:1 #4080cd);
}

QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #357abd, stop:1 #2d6da3);
}

QPushButton:disabled {
    background: rgba(128, 128, 128, 1.0);
    color: rgba(255, 255, 255, 1.0);
}

/* 特殊按钮样式 */
QPushButton#primaryButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ff6b6b, stop:1 #ee5a52);
}

QPushButton#primaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ff7b7b, stop:1 #fe6a62);
}

QPushButton#successButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #51cf66, stop:1 #40c057);
}

QPushButton#warningButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffd43b, stop:1 #fab005);
    color: #333;
}

/* 标签样式 */
QLabel {
    color: #ffffff;
    font-size: 13px;
    background: transparent;
}

QLabel[state="error"] {
    color: #ff6b6b;
    font-weight: bold;
}

QLabel[state="success"] {
    color: #51cf66;
    font-weight: bold;
}

QLabel[state="warning"] {
    color: #ffd43b;
    font-weight: bold;
}

QLabel[state="info"] {
    color: #74c0fc;
    font-weight: bold;
}

/* 下拉框样式 */
QComboBox {
    background: rgba(26, 26, 46, 0.8);
    border: 2px solid rgba(74, 144, 226, 0.3);
    border-radius: 8px;
    padding: 8px 12px;
    color: #ffffff;
    min-width: 200px;
    font-size: 13px;
}

QComboBox:hover {
    border-color: #4a90e2;
    background: rgba(26, 26, 46, 0.9);
}

QComboBox:focus {
    border-color: #74c0fc;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOCIgdmlld0JveD0iMCAwIDEyIDgiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDFMNiA2TDExIDEiIHN0cm9rZT0iI2ZmZmZmZiIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+);
    width: 12px;
    height: 8px;
}

QComboBox QAbstractItemView {
    background: rgba(26, 26, 46, 0.9);
    border: 2px solid rgba(74, 144, 226, 0.3);
    border-radius: 8px;
    color: #ffffff;
    selection-background-color: rgba(74, 144, 226, 0.8);
    padding: 5px;
}

/* 进度条样式 */
QProgressBar {
    background: rgba(26, 26, 46, 0.8);
    border: 2px solid rgba(74, 144, 226, 0.3);
    border-radius: 10px;
    text-align: center;
    color: #ffffff;
    font-weight: bold;
    height: 20px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #4a90e2, stop:0.5 #74c0fc, stop:1 #4a90e2);
    border-radius: 8px;
    margin: 2px;
}

/* 游戏视图样式 */
QLabel#gameView {
    background: rgba(0, 0, 0, 1.0);
    border: 2px solid rgba(74, 144, 226, 0.3);
    border-radius: 15px;
    padding: 10px;
}

/* 状态面板样式 */
QFrame#statusPanel {
    background: rgba(26, 26, 46, 0.8);
    border: 1px solid rgba(74, 144, 226, 0.3);
    border-radius: 12px;
    padding: 15px;
}

/* 控制面板样式 */
QFrame#controlPanel {
    background: rgba(26, 26, 46, 0.8);
    border: 1px solid rgba(74, 144, 226, 0.3);
    border-radius: 15px;
    padding: 20px;
}

/* 工具栏样式 */
QToolBar {
    background: rgba(26, 26, 46, 0.8);
    border: none;
    border-radius: 8px;
    padding: 5px;
    spacing: 5px;
}

QToolBar QToolButton {
    background: rgba(26, 26, 46, 0.6);
    border: 1px solid rgba(74, 144, 226, 0.3);
    border-radius: 6px;
    padding: 8px;
    color: #ffffff;
    font-weight: bold;
}

QToolBar QToolButton:hover {
    background: rgba(26, 26, 46, 0.8);
    border-color: #4a90e2;
}

QToolBar QToolButton:pressed {
    background: rgba(74, 144, 226, 0.8);
}

/* 状态栏样式 */
QStatusBar {
    background: rgba(26, 26, 46, 0.8);
    border-top: 1px solid rgba(74, 144, 226, 0.3);
    color: #ffffff;
    padding: 5px;
}

QStatusBar QLabel {
    background: rgba(26, 26, 46, 0.6);
    border: 1px solid rgba(74, 144, 226, 0.3);
    border-radius: 4px;
    padding: 3px 8px;
    margin: 2px;
}

/* 分割器样式 */
QSplitter::handle {
    background: rgba(74, 144, 226, 0.4);
    border-radius: 2px;
}

QSplitter::handle:horizontal {
    width: 3px;
    margin: 2px 0;
}

QSplitter::handle:vertical {
    height: 3px;
    margin: 0 2px;
}

QSplitter::handle:hover {
    background: #4a90e2;
}

/* 停靠窗口样式 */
QDockWidget {
    background: rgba(26, 26, 46, 0.8);
    border: 1px solid rgba(74, 144, 226, 0.3);
    border-radius: 8px;
    color: #ffffff;
}

QDockWidget::title {
    background: rgba(74, 144, 226, 0.8);
    border-radius: 6px;
    padding: 8px;
    text-align: center;
    font-weight: bold;
}

/* 滚动条样式 */
QScrollBar:vertical {
    background: rgba(26, 26, 46, 0.6);
    width: 12px;
    border-radius: 6px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: rgba(74, 144, 226, 0.8);
    border-radius: 6px;
    min-height: 20px;
    margin: 2px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(74, 144, 226, 1.0);
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background: rgba(26, 26, 46, 0.6);
    height: 12px;
    border-radius: 6px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background: rgba(74, 144, 226, 0.8);
    border-radius: 6px;
    min-width: 20px;
    margin: 2px;
}

QScrollBar::handle:horizontal:hover {
    background: rgba(74, 144, 226, 1.0);
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0;
}

/* 表格样式 */
QTableWidget {
    background: rgba(26, 26, 46, 0.8);
    border: 1px solid rgba(74, 144, 226, 0.3);
    border-radius: 8px;
    gridline-color: rgba(74, 144, 226, 0.3);
    color: #ffffff;
}

QTableWidget::item {
    padding: 8px;
    border-bottom: 1px solid rgba(74, 144, 226, 0.3);
}

QTableWidget::item:selected {
    background: rgba(74, 144, 226, 0.8);
    color: #ffffff;
}

QTableWidget::item:hover {
    background: rgba(26, 26, 46, 0.9);
}

QHeaderView::section {
    background: rgba(74, 144, 226, 0.8);
    padding: 10px;
    border: none;
    border-right: 1px solid rgba(74, 144, 226, 0.3);
    font-weight: bold;
    color: #ffffff;
}

QHeaderView::section:hover {
    background: rgba(74, 144, 226, 1.0);
}

/* 输入框样式 */
QLineEdit {
    background: rgba(26, 26, 46, 0.8);
    border: 2px solid rgba(74, 144, 226, 0.3);
    border-radius: 8px;
    padding: 8px 12px;
    color: #ffffff;
    font-size: 13px;
}

QLineEdit:focus {
    border-color: #74c0fc;
    background: rgba(26, 26, 46, 0.9);
}

QLineEdit:hover {
    border-color: #4a90e2;
}

/* 文本编辑器样式 */
QTextEdit {
    background: rgba(26, 26, 46, 0.8);
    border: 2px solid rgba(74, 144, 226, 0.3);
    border-radius: 8px;
    padding: 10px;
    color: #ffffff;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 12px;
}

QTextEdit:focus {
    border-color: #74c0fc;
    background: rgba(26, 26, 46, 0.9);
}

/* 选项卡样式 */
QTabWidget::pane {
    background: rgba(26, 26, 46, 0.8);
    border: 1px solid rgba(74, 144, 226, 0.3);
    border-radius: 8px;
    padding: 10px;
}

QTabWidget::tab-bar {
    alignment: center;
}

QTabBar::tab {
    background: rgba(26, 26, 46, 0.6);
    border: 1px solid rgba(74, 144, 226, 0.3);
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 10px 20px;
    margin-right: 2px;
    color: #ffffff;
    font-weight: bold;
}

QTabBar::tab:selected {
    background: rgba(74, 144, 226, 0.8);
    border-color: #4a90e2;
}

QTabBar::tab:hover {
    background: rgba(26, 26, 46, 0.8);
}

/* 菜单样式 */
QMenuBar {
    background: rgba(26, 26, 46, 0.8);
    border: none;
    color: #ffffff;
    padding: 5px;
}

QMenuBar::item {
    background: transparent;
    padding: 8px 12px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background: rgba(74, 144, 226, 0.8);
}

QMenu {
    background: rgba(26, 26, 46, 0.9);
    border: 2px solid rgba(74, 144, 226, 0.3);
    border-radius: 8px;
    color: #ffffff;
    padding: 5px;
}

QMenu::item {
    padding: 8px 20px;
    border-radius: 4px;
}

QMenu::item:selected {
    background: rgba(74, 144, 226, 0.8);
}

QMenu::separator {
    height: 1px;
    background: rgba(74, 144, 226, 0.3);
    margin: 5px 10px;
}
"""

# 卡片式组件样式
CARD_STYLE = """
/* 卡片样式 */
QFrame.card {
    background: rgba(26, 26, 46, 0.8);
    border: 1px solid rgba(74, 144, 226, 0.3);
    border-radius: 12px;
    padding: 15px;
    margin: 5px;
}

QFrame.card:hover {
    background: rgba(26, 26, 46, 0.9);
    border-color: rgba(74, 144, 226, 0.8);
    margin-top: -2px;
    margin-bottom: 2px;
}

/* 卡片标题 */
QLabel.card-title {
    font-size: 16px;
    font-weight: bold;
    color: #ffffff;
    margin-bottom: 10px;
}

/* 卡片内容 */
QLabel.card-content {
    font-size: 13px;
    color: rgba(255, 255, 255, 0.9);
    line-height: 1.4;
}

/* 卡片操作按钮 */
QPushButton.card-action {
    background: rgba(74, 144, 226, 0.8);
    border: none;
    border-radius: 6px;
    padding: 6px 12px;
    color: #ffffff;
    font-size: 12px;
    font-weight: bold;
}

QPushButton.card-action:hover {
    background: rgba(74, 144, 226, 1.0);
}
"""

# 动画效果样式
ANIMATION_STYLE = """
/* 悬浮效果 */
.hover-lift {
    transition: all 0.3s ease;
}

.hover-lift:hover {
    margin-top: -3px;
    margin-bottom: 3px;
}

/* 脉冲效果 */
.pulse {
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% {
        opacity: 1;
    }
    50% {
        opacity: 0.7;
    }
    100% {
        opacity: 1;
    }
}

/* 渐变动画 */
.gradient-animation {
    background-size: 200% 200%;
    animation: gradientShift 3s ease infinite;
}

@keyframes gradientShift {
    0% {
        background-position: 0% 50%;
    }
    50% {
        background-position: 100% 50%;
    }
    100% {
        background-position: 0% 50%;
    }
}
"""

# 组合现代化样式
MODERN_APP_STYLE = f"""
{MODERN_DARK_THEME}
{CARD_STYLE}
{ANIMATION_STYLE}
"""

# 游戏主题配色方案
GAME_THEME_COLORS = {
    'primary': '#4a90e2',
    'secondary': '#74c0fc', 
    'success': '#51cf66',
    'warning': '#ffd43b',
    'error': '#ff6b6b',
    'info': '#74c0fc',
    'background_primary': '#1a1a2e',
    'background_secondary': '#16213e',
    'background_tertiary': '#0f3460',
    'text_primary': '#ffffff',
    'text_secondary': 'rgba(255, 255, 255, 0.8)',
    'border_primary': 'rgba(74, 144, 226, 0.3)',
    'border_secondary': 'rgba(74, 144, 226, 0.5)',
    'overlay': 'rgba(26, 26, 46, 0.8)',
    'overlay_hover': 'rgba(26, 26, 46, 0.9)'
}

# 响应式设计断点
BREAKPOINTS = {
    'small': 768,
    'medium': 1024,
    'large': 1440,
    'xlarge': 1920
}