"""现代化UI组件系统演示

展示新组件系统的功能和设计
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QScrollArea
from PyQt6.QtCore import Qt, QTimer

from components import (
    VBox, HBox, Grid, Card, Button, IconButton, TextButton, LinkButton,
    Typography, Heading, Body, Caption, Overline, Link,
    Icon, MaterialIcon, FontAwesomeIcon, LoadingIcon,
    ProgressBar, CircularProgress, StepProgress,
    Input, NumberInput, SearchInput, PasswordInput
)
from design_tokens import ComponentSize, ComponentVariant
from style_generator import StyleGenerator


class ComponentShowcase(QWidget):
    """组件展示"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_demo_interactions()
    
    def setup_ui(self):
        """设置UI"""
        # 主滚动区域
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # 内容容器
        content = QWidget()
        scroll.setWidget(content)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)
        
        # 内容布局
        layout = VBox(parent=content)
        layout.set_spacing(32)
        layout.set_margins(24, 24, 24, 24)
        
        # 页面标题
        layout.add_widget(Heading("现代化UI组件系统演示", level=1))
        layout.add_widget(Body("展示基于设计Token的统一组件库", color="text.secondary"))
        
        # 排版组件展示
        self.add_typography_section(layout)
        
        # 按钮组件展示
        self.add_button_section(layout)
        
        # 图标组件展示
        self.add_icon_section(layout)
        
        # 输入组件展示
        self.add_input_section(layout)
        
        # 进度组件展示
        self.add_progress_section(layout)
        
        # 卡片组件展示
        self.add_card_section(layout)
        
        # 布局组件展示
        self.add_layout_section(layout)
    
    def add_typography_section(self, layout: VBox):
        """添加排版组件展示"""
        section = Card(title="排版组件", variant="elevated", size=ComponentSize.LARGE)
        section_layout = VBox(parent=section)
        section_layout.set_spacing(16)
        
        # 标题层级
        headings_card = Card(title="标题层级", variant="outlined")
        headings_layout = VBox(parent=headings_card)
        
        for i in range(1, 7):
            headings_layout.add_widget(Heading(f"标题 H{i}", level=i))
        
        section_layout.add_widget(headings_card)
        
        # 文本样式
        text_card = Card(title="文本样式", variant="outlined")
        text_layout = VBox(parent=text_card)
        
        text_layout.add_widget(Body("正文 - 大号", size="large"))
        text_layout.add_widget(Body("正文 - 中号", size="medium"))
        text_layout.add_widget(Body("正文 - 小号", size="small"))
        text_layout.add_widget(Caption("说明文字"))
        text_layout.add_widget(Overline("上标文字"))
        text_layout.add_widget(Link("链接文字", url="https://example.com"))
        
        section_layout.add_widget(text_card)
        
        layout.add_widget(section)
    
    def add_button_section(self, layout: VBox):
        """添加按钮组件展示"""
        section = Card(title="按钮组件", variant="elevated", size=ComponentSize.LARGE)
        section_layout = VBox(parent=section)
        section_layout.set_spacing(16)
        
        # 按钮变体
        variants_card = Card(title="按钮变体", variant="outlined")
        variants_layout = HBox(parent=variants_card)
        variants_layout.set_spacing(12)
        
        variants_layout.add_widget(Button("主要按钮", variant="primary"))
        variants_layout.add_widget(Button("次要按钮", variant="secondary"))
        variants_layout.add_widget(Button("轮廓按钮", variant="outline"))
        variants_layout.add_widget(Button("幽灵按钮", variant="ghost"))
        variants_layout.add_widget(Button("危险按钮", variant="danger"))
        variants_layout.add_stretch()
        
        section_layout.add_widget(variants_card)
        
        # 按钮尺寸
        sizes_card = Card(title="按钮尺寸", variant="outlined")
        sizes_layout = HBox(parent=sizes_card)
        sizes_layout.set_spacing(12)
        
        sizes_layout.add_widget(Button("小号", size=ComponentSize.SMALL))
        sizes_layout.add_widget(Button("中号", size=ComponentSize.MEDIUM))
        sizes_layout.add_widget(Button("大号", size=ComponentSize.LARGE))
        sizes_layout.add_stretch()
        
        section_layout.add_widget(sizes_card)
        
        # 特殊按钮
        special_card = Card(title="特殊按钮", variant="outlined")
        special_layout = HBox(parent=special_card)
        special_layout.set_spacing(12)
        
        loading_btn = Button("加载中", variant="primary")
        loading_btn.loading = True
        
        disabled_btn = Button("禁用按钮", variant="secondary")
        disabled_btn.disabled = True
        
        full_width_btn = Button("全宽按钮", variant="outline", full_width=True)
        
        special_layout.add_widget(loading_btn)
        special_layout.add_widget(disabled_btn)
        special_layout.add_stretch()
        
        section_layout.add_widget(special_card)
        section_layout.add_widget(full_width_btn)
        
        layout.add_widget(section)
    
    def add_icon_section(self, layout: VBox):
        """添加图标组件展示"""
        section = Card(title="图标组件", variant="elevated", size=ComponentSize.LARGE)
        section_layout = VBox(parent=section)
        section_layout.set_spacing(16)
        
        # Material图标
        material_card = Card(title="Material Icons", variant="outlined")
        material_layout = HBox(parent=material_card)
        material_layout.set_spacing(16)
        
        material_icons = ["home", "search", "settings", "favorite", "star", "person", "notifications", "menu"]
        for icon_name in material_icons:
            icon_container = VBox()
            icon_container.add_widget(MaterialIcon(icon_name, icon_size=32))
            icon_container.add_widget(Caption(icon_name, alignment=Qt.AlignmentFlag.AlignCenter))
            material_layout.add_widget(icon_container)
        
        material_layout.add_stretch()
        section_layout.add_widget(material_card)
        
        # 图标尺寸
        sizes_card = Card(title="图标尺寸", variant="outlined")
        sizes_layout = HBox(parent=sizes_card)
        sizes_layout.set_spacing(16)
        
        sizes = [16, 24, 32, 48, 64]
        for size in sizes:
            icon_container = VBox()
            icon_container.add_widget(MaterialIcon("star", icon_size=size, color="semantic.warning"))
            icon_container.add_widget(Caption(f"{size}px", alignment=Qt.AlignmentFlag.AlignCenter))
            sizes_layout.add_widget(icon_container)
        
        sizes_layout.add_stretch()
        section_layout.add_widget(sizes_card)
        
        # 特殊图标
        special_card = Card(title="特殊图标", variant="outlined")
        special_layout = HBox(parent=special_card)
        special_layout.set_spacing(16)
        
        # 加载图标
        loading_icon = LoadingIcon(icon_size=32, color="semantic.info")
        loading_icon.start_loading()
        
        # 可点击图标
        clickable_icon = MaterialIcon("favorite", icon_size=32, color="semantic.error", clickable=True)
        
        special_layout.add_widget(loading_icon)
        special_layout.add_widget(clickable_icon)
        special_layout.add_stretch()
        
        section_layout.add_widget(special_card)
        
        layout.add_widget(section)
    
    def add_input_section(self, layout: VBox):
        """添加输入组件展示"""
        section = Card(title="输入组件", variant="elevated", size=ComponentSize.LARGE)
        section_layout = VBox(parent=section)
        section_layout.set_spacing(16)
        
        # 基础输入
        basic_card = Card(title="基础输入", variant="outlined")
        basic_layout = Grid(columns=2, spacing=16, parent=basic_card)
        
        basic_layout.add_widget(Input(placeholder="普通输入框"), 0, 0)
        basic_layout.add_widget(Input(placeholder="必填输入框", required=True), 0, 1)
        basic_layout.add_widget(SearchInput(placeholder="搜索..."), 1, 0)
        basic_layout.add_widget(NumberInput(value=0, min_value=0, max_value=100), 1, 1)
        
        section_layout.add_widget(basic_card)
        
        # 特殊输入
        special_card = Card(title="特殊输入", variant="outlined")
        special_layout = VBox(parent=special_card)
        special_layout.set_spacing(12)
        
        password_input = PasswordInput(placeholder="密码输入")
        multiline_input = Input(placeholder="多行文本输入", multiline=True)
        multiline_input.setFixedHeight(100)
        
        special_layout.add_widget(password_input)
        special_layout.add_widget(multiline_input)
        
        section_layout.add_widget(special_card)
        
        layout.add_widget(section)
    
    def add_progress_section(self, layout: VBox):
        """添加进度组件展示"""
        section = Card(title="进度组件", variant="elevated", size=ComponentSize.LARGE)
        section_layout = VBox(parent=section)
        section_layout.set_spacing(16)
        
        # 线性进度条
        linear_card = Card(title="线性进度条", variant="outlined")
        linear_layout = VBox(parent=linear_card)
        linear_layout.set_spacing(12)
        
        # 不同样式的进度条
        progress_bars = [
            ("默认进度条", ComponentVariant.PRIMARY, 60),
            ("成功进度条", ComponentVariant.SUCCESS, 80),
            ("警告进度条", ComponentVariant.WARNING, 45),
            ("错误进度条", ComponentVariant.DANGER, 30),
        ]
        
        for label, variant, value in progress_bars:
            linear_layout.add_widget(Caption(label))
            progress = ProgressBar(value=value, variant=variant)
            linear_layout.add_widget(progress)
        
        section_layout.add_widget(linear_card)
        
        # 圆形进度条
        circular_card = Card(title="圆形进度条", variant="outlined")
        circular_layout = HBox(parent=circular_card)
        circular_layout.set_spacing(24)
        
        circular_values = [25, 50, 75, 100]
        for value in circular_values:
            circular_container = VBox()
            circular_progress = CircularProgress(value=value, size=80)
            circular_container.add_widget(circular_progress)
            circular_container.add_widget(Caption(f"{value}%", alignment=Qt.AlignmentFlag.AlignCenter))
            circular_layout.add_widget(circular_container)
        
        circular_layout.add_stretch()
        section_layout.add_widget(circular_card)
        
        # 步骤进度条
        step_card = Card(title="步骤进度条", variant="outlined")
        step_layout = VBox(parent=step_card)
        
        steps = ["开始", "处理中", "验证", "完成"]
        step_progress = StepProgress(steps=steps, current_step=2)
        step_layout.add_widget(step_progress)
        
        section_layout.add_widget(step_card)
        
        layout.add_widget(section)
    
    def add_card_section(self, layout: VBox):
        """添加卡片组件展示"""
        section = Card(title="卡片组件", variant="elevated", size=ComponentSize.LARGE)
        section_layout = VBox(parent=section)
        section_layout.set_spacing(16)
        
        # 卡片变体
        variants_grid = Grid(columns=3, parent=section)
        variants_grid.set_spacing(16)
        
        # 基础卡片
        basic_card = Card(title="基础卡片", subtitle="这是一个基础卡片", variant="default")
        basic_card.add_content(Body("卡片内容区域，可以放置任何组件。"))
        
        # 轮廓卡片
        outlined_card = Card(title="轮廓卡片", subtitle="带有边框的卡片", variant="outlined")
        outlined_card.add_content(Body("轮廓样式提供清晰的边界。"))
        
        # 阴影卡片
        elevated_card = Card(title="阴影卡片", subtitle="带有阴影效果", variant="elevated")
        elevated_card.add_content(Body("阴影效果增加层次感。"))
        
        variants_grid.add_widget(basic_card, 0, 0)
        variants_grid.add_widget(outlined_card, 0, 1)
        variants_grid.add_widget(elevated_card, 0, 2)
        
        section_layout.add_widget(variants_grid)
        
        # 交互式卡片
        interactive_card = Card(
            title="交互式卡片",
            subtitle="可以点击和悬浮",
            variant="elevated",
            interactive=True,
            hoverable=True
        )
        interactive_card.add_content(Body("这个卡片支持鼠标交互效果。"))
        interactive_card.add_action_button(Button("操作", variant="primary", size=ComponentSize.SMALL))
        interactive_card.add_action_button(Button("取消", variant="ghost", size=ComponentSize.SMALL))
        
        section_layout.add_widget(interactive_card)
        
        layout.add_widget(section)
    
    def add_layout_section(self, layout: VBox):
        """添加布局组件展示"""
        section = Card(title="布局组件", variant="elevated", size=ComponentSize.LARGE)
        section_layout = VBox(parent=section)
        section_layout.set_spacing(16)
        
        # 网格布局示例
        grid_card = Card(title="网格布局", variant="outlined")
        grid_layout = Grid(columns=4, parent=grid_card)
        grid_layout.set_spacing(8)
        
        for i in range(8):
            item = Card(variant="default", size=ComponentSize.SMALL)
            item.add_content(Body(f"项目 {i+1}", alignment=Qt.AlignmentFlag.AlignCenter))
            item.setFixedHeight(60)
            grid_layout.add_widget(item, i // 4, i % 4)
        
        section_layout.add_widget(grid_card)
        
        # 水平布局示例
        hbox_card = Card(title="水平布局", variant="outlined")
        hbox_layout = HBox(parent=hbox_card)
        hbox_layout.set_spacing(12)
        
        for i in range(4):
            item = Button(f"按钮 {i+1}", variant="outline")
            hbox_layout.add_widget(item)
        
        hbox_layout.add_stretch()
        section_layout.add_widget(hbox_card)
        
        layout.add_widget(section)
    
    def setup_demo_interactions(self):
        """设置演示交互"""
        # 定时器用于更新进度条
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress_demo)
        self.timer.start(100)  # 每100ms更新一次
        
        self.progress_value = 0
        self.progress_direction = 1
    
    def update_progress_demo(self):
        """更新进度条演示"""
        # 这里可以添加动态更新进度条的逻辑
        pass


class DemoMainWindow(QMainWindow):
    """演示主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.apply_theme()
    
    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("现代化UI组件系统演示")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        # 设置中央组件
        self.showcase = ComponentShowcase()
        self.setCentralWidget(self.showcase)
    
    def apply_theme(self):
        """应用主题"""
        style_generator = StyleGenerator()
        global_style = style_generator.generate_global_style()
        self.setStyleSheet(global_style)


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序属性
    app.setApplicationName("UI组件演示")
    app.setApplicationVersion("1.0.0")
    
    # 创建演示窗口
    window = DemoMainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()