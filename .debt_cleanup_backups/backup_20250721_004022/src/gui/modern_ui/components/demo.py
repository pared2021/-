#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
现代化UI组件演示系统
展示所有组件的功能和样式
"""

import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QScrollArea, QTabWidget, QLabel, QFrame, QGridLayout, QSpacerItem,
    QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from src.gui.modern_ui.components.design_tokens import DesignTokens, ComponentSize, ComponentVariant
from src.gui.modern_ui.components.style_generator import StyleGenerator
from src.gui.modern_ui.components.button import Button, IconButton, TextButton, LinkButton
from src.gui.modern_ui.components.card import Card, ImageCard, StatCard
from src.gui.modern_ui.components.input import Input, NumberInput, SearchInput, PasswordInput
from src.gui.modern_ui.components.progress import ProgressBar, CircularProgress, StepProgress
from src.gui.modern_ui.components.layout import VBox, HBox, Grid, ScrollArea
from src.gui.modern_ui.components.typography import Typography, Heading, Body, Caption, Link
from src.gui.modern_ui.components.icon import Icon, MaterialIcon, LoadingIcon


class ComponentShowcase(QWidget):
    """组件展示页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.design_tokens = DesignTokens()
        self.style_generator = StyleGenerator()
        self.setup_ui()
        self.setup_demo_data()
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(self.style_generator.generate_global_style())
        
        # 添加各个组件演示页面
        self.add_button_demo()
        self.add_card_demo()
        self.add_input_demo()
        self.add_progress_demo()
        self.add_typography_demo()
        self.add_layout_demo()
        
        layout.addWidget(self.tab_widget)
    
    def add_button_demo(self):
        """添加按钮演示"""
        page = QWidget()
        scroll = QScrollArea()
        scroll.setWidget(page)
        scroll.setWidgetResizable(True)
        
        layout = QVBoxLayout(page)
        layout.setSpacing(30)
        
        # 标题
        title = Heading("按钮组件演示", level=1)
        layout.addWidget(title)
        
        # 基础按钮
        section = self.create_section("基础按钮")
        button_layout = QHBoxLayout()
        
        # 不同变体的按钮
        primary_btn = Button("主要按钮", variant=ComponentVariant.PRIMARY)
        secondary_btn = Button("次要按钮", variant=ComponentVariant.SECONDARY)
        success_btn = Button("成功按钮", variant=ComponentVariant.SUCCESS)
        warning_btn = Button("警告按钮", variant=ComponentVariant.WARNING)
        danger_btn = Button("危险按钮", variant=ComponentVariant.DANGER)
        
        for btn in [primary_btn, secondary_btn, success_btn, warning_btn, danger_btn]:
            button_layout.addWidget(btn)
        
        button_layout.addStretch()
        section.layout().addLayout(button_layout)
        layout.addWidget(section)
        
        # 不同尺寸的按钮
        size_section = self.create_section("按钮尺寸")
        size_layout = QHBoxLayout()
        
        small_btn = Button("小按钮", size=ComponentSize.SMALL)
        medium_btn = Button("中按钮", size=ComponentSize.MEDIUM)
        large_btn = Button("大按钮", size=ComponentSize.LARGE)
        
        for btn in [small_btn, medium_btn, large_btn]:
            size_layout.addWidget(btn)
        
        size_layout.addStretch()
        size_section.layout().addLayout(size_layout)
        layout.addWidget(size_section)
        
        # 图标按钮
        icon_section = self.create_section("图标按钮")
        icon_layout = QHBoxLayout()
        
        # 创建一个简单的图标按钮（暂时不使用图标）
        icon_btn = IconButton(QIcon())
        text_btn = TextButton("文本按钮")
        link_btn = LinkButton("链接按钮")
        
        for btn in [icon_btn, text_btn, link_btn]:
            icon_layout.addWidget(btn)
        
        icon_layout.addStretch()
        icon_section.layout().addLayout(icon_layout)
        layout.addWidget(icon_section)
        
        layout.addStretch()
        self.tab_widget.addTab(scroll, "按钮")
    
    def add_card_demo(self):
        """添加卡片演示"""
        page = QWidget()
        scroll = QScrollArea()
        scroll.setWidget(page)
        scroll.setWidgetResizable(True)
        
        layout = QVBoxLayout(page)
        layout.setSpacing(30)
        
        # 标题
        title = Heading("卡片组件演示", level=1)
        layout.addWidget(title)
        
        # 基础卡片
        section = self.create_section("基础卡片")
        card_layout = QHBoxLayout()
        
        # 创建不同类型的卡片
        basic_card = Card("基础卡片", "这是一个基础卡片的内容示例")
        
        # 图片卡片（暂时不使用图片）
        image_card = ImageCard(
            image=None,  # 暂时不使用图片
            title="图片卡片",
            subtitle="这是一个带图片的卡片"
        )
        
        # 统计卡片
        stat_card = StatCard("用户数量", "1,234", "↗️ +12%")
        
        for card in [basic_card, image_card, stat_card]:
            card.setFixedWidth(300)
            card_layout.addWidget(card)
        
        card_layout.addStretch()
        section.layout().addLayout(card_layout)
        layout.addWidget(section)
        
        layout.addStretch()
        self.tab_widget.addTab(scroll, "卡片")
    
    def add_input_demo(self):
        """添加输入组件演示"""
        page = QWidget()
        scroll = QScrollArea()
        scroll.setWidget(page)
        scroll.setWidgetResizable(True)
        
        layout = QVBoxLayout(page)
        layout.setSpacing(30)
        
        # 标题
        title = Heading("输入组件演示", level=1)
        layout.addWidget(title)
        
        # 输入框
        section = self.create_section("输入框")
        input_layout = QVBoxLayout()
        
        # 基础输入框
        basic_input = Input("请输入文本")
        input_layout.addWidget(QLabel("基础输入框:"))
        input_layout.addWidget(basic_input)
        
        # 数字输入框
        number_input = NumberInput(0, 100, 50)
        input_layout.addWidget(QLabel("数字输入框:"))
        input_layout.addWidget(number_input)
        
        # 搜索输入框
        search_input = SearchInput("搜索...")
        input_layout.addWidget(QLabel("搜索输入框:"))
        input_layout.addWidget(search_input)
        
        # 密码输入框
        password_input = PasswordInput("请输入密码")
        input_layout.addWidget(QLabel("密码输入框:"))
        input_layout.addWidget(password_input)
        
        section.layout().addLayout(input_layout)
        layout.addWidget(section)
        
        layout.addStretch()
        self.tab_widget.addTab(scroll, "输入")
    
    def add_progress_demo(self):
        """添加进度组件演示"""
        page = QWidget()
        scroll = QScrollArea()
        scroll.setWidget(page)
        scroll.setWidgetResizable(True)
        
        layout = QVBoxLayout(page)
        layout.setSpacing(30)
        
        # 标题
        title = Heading("进度组件演示", level=1)
        layout.addWidget(title)
        
        # 进度条
        section = self.create_section("进度条")
        progress_layout = QVBoxLayout()
        
        # 线性进度条
        progress_bar = ProgressBar()
        progress_bar.set_value(65)
        progress_layout.addWidget(QLabel("线性进度条 (65%):"))
        progress_layout.addWidget(progress_bar)
        
        # 圆形进度条
        circular_progress = CircularProgress()
        circular_progress.set_value(80)
        progress_layout.addWidget(QLabel("圆形进度条 (80%):"))
        progress_layout.addWidget(circular_progress)
        
        # 步骤进度条
        step_progress = StepProgress(["步骤1", "步骤2", "步骤3", "步骤4"])
        step_progress.set_current_step(2)
        progress_layout.addWidget(QLabel("步骤进度条:"))
        progress_layout.addWidget(step_progress)
        
        section.layout().addLayout(progress_layout)
        layout.addWidget(section)
        
        # 添加动画效果
        self.setup_progress_animation(progress_bar, circular_progress)
        
        layout.addStretch()
        self.tab_widget.addTab(scroll, "进度")
    
    def add_typography_demo(self):
        """添加排版演示"""
        page = QWidget()
        scroll = QScrollArea()
        scroll.setWidget(page)
        scroll.setWidgetResizable(True)
        
        layout = QVBoxLayout(page)
        layout.setSpacing(30)
        
        # 标题
        title = Heading("排版组件演示", level=1)
        layout.addWidget(title)
        
        # 标题层次
        section = self.create_section("标题层次")
        typography_layout = QVBoxLayout()
        
        for level in range(1, 7):
            heading = Heading(f"标题 H{level}", level=level)
            typography_layout.addWidget(heading)
        
        section.layout().addLayout(typography_layout)
        layout.addWidget(section)
        
        # 正文和说明文字
        text_section = self.create_section("正文和说明")
        text_layout = QVBoxLayout()
        
        body = Body("这是正文内容，用于显示主要的文本信息。正文应该具有良好的可读性和适当的行高。")
        caption = Caption("这是说明文字，通常用于提供额外的信息或注释。")
        link = Link("这是一个链接", "https://example.com")
        
        text_layout.addWidget(body)
        text_layout.addWidget(caption)
        text_layout.addWidget(link)
        
        text_section.layout().addLayout(text_layout)
        layout.addWidget(text_section)
        
        layout.addStretch()
        self.tab_widget.addTab(scroll, "排版")
    
    def add_layout_demo(self):
        """添加布局演示"""
        page = QWidget()
        scroll = QScrollArea()
        scroll.setWidget(page)
        scroll.setWidgetResizable(True)
        
        layout = QVBoxLayout(page)
        layout.setSpacing(30)
        
        # 标题
        title = Heading("布局组件演示", level=1)
        layout.addWidget(title)
        
        # 水平布局
        h_section = self.create_section("水平布局")
        h_box = HBox(spacing=10)
        for i in range(3):
            btn = Button(f"按钮 {i+1}")
            h_box.add_widget(btn)
        h_section.layout().addWidget(h_box)
        layout.addWidget(h_section)
        
        # 垂直布局
        v_section = self.create_section("垂直布局")
        v_box = VBox(spacing=10)
        for i in range(3):
            btn = Button(f"按钮 {i+1}")
            v_box.add_widget(btn)
        v_section.layout().addWidget(v_box)
        layout.addWidget(v_section)
        
        # 网格布局
        grid_section = self.create_section("网格布局")
        grid = Grid(spacing=5)
        for i in range(2):
            for j in range(3):
                btn = Button(f"({i},{j})")
                grid.add_widget(btn, i, j)
        grid_section.layout().addWidget(grid)
        layout.addWidget(grid_section)
        
        layout.addStretch()
        self.tab_widget.addTab(scroll, "布局")
    
    def create_section(self, title):
        """创建演示区域"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.Box)
        frame.setStyleSheet("""
            QFrame {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 16px;
                background-color: #fafafa;
            }
        """)
        
        layout = QVBoxLayout(frame)
        
        # 区域标题
        section_title = QLabel(title)
        section_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        section_title.setStyleSheet("color: #333; margin-bottom: 10px;")
        layout.addWidget(section_title)
        
        return frame
    
    def setup_demo_data(self):
        """设置演示数据"""
        pass
    
    def setup_progress_animation(self, progress_bar, circular_progress):
        """设置进度条动画"""
        self.progress_timer = QTimer()
        self.progress_direction = 1
        
        def update_progress():
            current = progress_bar.value
            new_value = current + self.progress_direction * 2
            
            if new_value >= 100:
                new_value = 100
                self.progress_direction = -1
            elif new_value <= 0:
                new_value = 0
                self.progress_direction = 1
            
            progress_bar.set_value(new_value)
            circular_progress.set_value(new_value)
        
        self.progress_timer.timeout.connect(update_progress)
        self.progress_timer.start(100)


class DemoMainWindow(QMainWindow):
    """演示主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("现代化UI组件演示系统")
        self.setGeometry(100, 100, 1200, 800)
        
        # 设置中央组件
        self.showcase = ComponentShowcase()
        self.setCentralWidget(self.showcase)
        
        # 应用全局样式
        self.apply_global_style()
    
    def apply_global_style(self):
        """应用全局样式"""
        style_generator = StyleGenerator()
        self.setStyleSheet(style_generator.generate_global_style())


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序属性
    app.setApplicationName("现代化UI组件演示")
    app.setApplicationVersion("1.0.0")
    
    # 创建主窗口
    window = DemoMainWindow()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec())


if __name__ == "__main__":
    main()