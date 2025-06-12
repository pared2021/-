"""
设置页面
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from qfluentwidgets import (
    SettingCardGroup,
    SwitchSettingCard,
    ComboBoxSettingCard,
    ScrollArea,
    ExpandLayout,
    FluentIcon,
    InfoBar,
)


class SettingsPage(ScrollArea):
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
        # OCR设置
        self.ocr_group = SettingCardGroup(self.tr("OCR设置"), self.view)

        # OCR模型选择
        self.model_card = ComboBoxSettingCard(
            FluentIcon.GAME,
            "OCR模型",
            "选择要使用的OCR模型",
            ["默认中文模型", "游戏优化模型"],
            self.ocr_group,
        )

        # 是否启用GPU加速
        self.gpu_card = SwitchSettingCard(
            FluentIcon.SPEED_HIGH, "GPU加速", "使用DirectML进行GPU加速", self.ocr_group
        )

        self.ocr_group.addSettingCard(self.model_card)
        self.ocr_group.addSettingCard(self.gpu_card)

        # 界面设置
        self.ui_group = SettingCardGroup(self.tr("界面设置"), self.view)

        # 主题设置
        self.theme_card = ComboBoxSettingCard(
            FluentIcon.BRUSH, "主题", "选择界面主题", ["浅色", "深色", "跟随系统"], self.ui_group
        )

        # 窗口置顶
        self.topmost_card = SwitchSettingCard(
            FluentIcon.PIN, "窗口置顶", "保持窗口始终在最前", self.ui_group
        )

        self.ui_group.addSettingCard(self.theme_card)
        self.ui_group.addSettingCard(self.topmost_card)

        # 添加到主布局
        self.vBoxLayout.addWidget(self.ocr_group)
        self.vBoxLayout.addWidget(self.ui_group)
        self.vBoxLayout.addStretch()

        # 连接信号
        self.gpu_card.switchButton.checkedChanged.connect(self._on_gpu_changed)
        self.theme_card.comboBox.currentIndexChanged.connect(self._on_theme_changed)
        self.topmost_card.switchButton.checkedChanged.connect(self._on_topmost_changed)

    def _on_gpu_changed(self, checked: bool):
        """GPU加速开关变化处理"""
        InfoBar.success(
            "设置已更新",
            "GPU加速已" + ("启用" if checked else "禁用"),
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            duration=2000,
            parent=self,
        )

    def _on_theme_changed(self, index: int):
        """主题变化处理"""
        themes = ["浅色", "深色", "跟随系统"]
        InfoBar.success(
            "设置已更新",
            f"主题已切换为: {themes[index]}",
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            duration=2000,
            parent=self,
        )

    def _on_topmost_changed(self, checked: bool):
        """窗口置顶变化处理"""
        InfoBar.success(
            "设置已更新",
            "窗口置顶已" + ("启用" if checked else "禁用"),
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            duration=2000,
            parent=self,
        )
