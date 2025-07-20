"""
状态模板管理对话框
"""
from typing import Optional, List, Dict, Tuple
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                           QPushButton, QListWidget, QListWidgetItem, QSpinBox,
                           QLineEdit, QGroupBox, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap

from services.vision.state_recognizer import StateRecognizer, GameState
from ...services.error_handler import ErrorHandler
from ...common.error_types import ErrorCode, ErrorContext

class TemplateManagerDialog(QDialog):
    """状态模板管理对话框"""
    
    def __init__(self, state_recognizer: StateRecognizer,
                 error_handler: ErrorHandler, parent=None):
        """初始化
        
        Args:
            state_recognizer: 状态识别器
            error_handler: 错误处理器
            parent: 父窗口
        """
        super().__init__(parent)
        
        self.state_recognizer = state_recognizer
        self.error_handler = error_handler
        
        self._init_ui()
        self._load_templates()
        
    def _init_ui(self):
        """初始化UI"""
        # 设置窗口属性
        self.setWindowTitle("状态模板管理")
        self.setMinimumSize(800, 600)
        
        # 创建主布局
        layout = QVBoxLayout(self)
        
        # 创建模板列表
        template_group = QGroupBox("状态模板")
        template_layout = QVBoxLayout(template_group)
        
        self.template_list = QListWidget()
        self.template_list.itemClicked.connect(self._on_template_selected)
        template_layout.addWidget(self.template_list)
        
        # 创建模板操作按钮
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("添加")
        self.add_button.clicked.connect(self._on_add_template)
        button_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("编辑")
        self.edit_button.clicked.connect(self._on_edit_template)
        button_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("删除")
        self.delete_button.clicked.connect(self._on_delete_template)
        button_layout.addWidget(self.delete_button)
        
        template_layout.addLayout(button_layout)
        layout.addWidget(template_group)
        
        # 创建模板预览
        preview_group = QGroupBox("模板预览")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(400, 300)
        preview_layout.addWidget(self.preview_label)
        
        # 创建模板信息
        info_layout = QHBoxLayout()
        
        # 状态名称
        name_layout = QVBoxLayout()
        name_layout.addWidget(QLabel("状态名称:"))
        self.name_edit = QLineEdit()
        name_layout.addWidget(self.name_edit)
        info_layout.addLayout(name_layout)
        
        # 置信度阈值
        threshold_layout = QVBoxLayout()
        threshold_layout.addWidget(QLabel("置信度阈值:"))
        self.threshold_spin = QSpinBox()
        self.threshold_spin.setRange(0, 100)
        self.threshold_spin.setValue(80)
        threshold_layout.addWidget(self.threshold_spin)
        info_layout.addLayout(threshold_layout)
        
        preview_layout.addLayout(info_layout)
        layout.addWidget(preview_group)
        
        # 创建对话框按钮
        dialog_button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self._on_save_template)
        dialog_button_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        dialog_button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(dialog_button_layout)
        
    def _load_templates(self):
        """加载模板列表"""
        try:
            # 清空列表
            self.template_list.clear()
            
            # 获取所有状态
            for state_name in self.state_recognizer.states:
                item = QListWidgetItem(state_name)
                self.template_list.addItem(item)
                
        except Exception as e:
            from ...common.error_types import GameAutomationError
            error = GameAutomationError(
                ErrorCode.UI_ERROR,
                "加载模板列表失败",
                ErrorContext(
                    source="TemplateManagerDialog._load_templates",
                    details={"error_info": str(e)}
                )
            )
            self.error_handler.handle_error(error)
            
    def _on_template_selected(self, item: QListWidgetItem):
        """模板选择处理
        
        Args:
            item: 选中的列表项
        """
        try:
            # 获取状态信息
            state_name = item.text()
            state = self.state_recognizer.states.get(state_name)
            
            if state:
                # 更新预览
                if state.matches:
                    match = state.matches[0]
                    template = self.state_recognizer.template_matcher.templates.get(state_name)
                    if template is not None:
                        # 转换图像格式
                        height, width = template.shape
                        bytes_per_line = width
                        q_image = QImage(template.data, width, height,
                                       bytes_per_line, QImage.Format.Format_Grayscale8)
                        
                        # 缩放图像
                        pixmap = QPixmap.fromImage(q_image)
                        scaled_pixmap = pixmap.scaled(self.preview_label.size(),
                                                    Qt.AspectRatioMode.KeepAspectRatio,
                                                    Qt.TransformationMode.SmoothTransformation)
                        
                        # 显示图像
                        self.preview_label.setPixmap(scaled_pixmap)
                        
                # 更新信息
                self.name_edit.setText(state.name)
                self.threshold_spin.setValue(int(state.confidence * 100))
                
        except Exception as e:
            from ...common.error_types import GameAutomationError
            error = GameAutomationError(
                ErrorCode.UI_ERROR,
                "选择模板失败",
                ErrorContext(
                    source="TemplateManagerDialog._on_template_selected",
                    details={"error_info": str(e)}
                )
            )
            self.error_handler.handle_error(error)
            
    def _on_add_template(self):
        """添加模板处理"""
        try:
            # 选择模板图片
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "选择模板图片",
                "",
                "图片文件 (*.png *.jpg *.jpeg *.bmp)"
            )
            
            if not file_path:
                return
                
            # 加载模板
            state_name = self.name_edit.text()
            if not state_name:
                QMessageBox.warning(self, "警告", "请输入状态名称")
                return
                
            if self.state_recognizer.load_state_template(state_name, file_path):
                # 创建状态
                state = GameState(
                    name=state_name,
                    confidence=self.threshold_spin.value() / 100,
                    features={},
                    regions=[],
                    matches=[]
                )
                
                # 注册状态
                self.state_recognizer.register_state(state)
                
                # 更新列表
                self._load_templates()
                
                # 选择新添加的模板
                items = self.template_list.findItems(state_name, Qt.MatchFlag.MatchExactly)
                if items:
                    self.template_list.setCurrentItem(items[0])
                    
        except Exception as e:
            from ...common.error_types import GameAutomationError
            error = GameAutomationError(
                ErrorCode.UI_ERROR,
                "添加模板失败",
                ErrorContext(
                    source="TemplateManagerDialog._on_add_template",
                    details={"error_info": str(e)}
                )
            )
            self.error_handler.handle_error(error)
            
    def _on_edit_template(self):
        """编辑模板处理"""
        try:
            # 获取选中的模板
            item = self.template_list.currentItem()
            if not item:
                QMessageBox.warning(self, "警告", "请选择要编辑的模板")
                return
                
            # 选择新的模板图片
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "选择新的模板图片",
                "",
                "图片文件 (*.png *.jpg *.jpeg *.bmp)"
            )
            
            if not file_path:
                return
                
            # 更新模板
            state_name = item.text()
            if self.state_recognizer.load_state_template(state_name, file_path):
                # 更新状态
                state = self.state_recognizer.states.get(state_name)
                if state:
                    state.confidence = self.threshold_spin.value() / 100
                    
                # 更新预览
                self._on_template_selected(item)
                
        except Exception as e:
            from ...common.error_types import GameAutomationError
            error = GameAutomationError(
                ErrorCode.UI_ERROR,
                "编辑模板失败",
                ErrorContext(
                    source="TemplateManagerDialog._on_edit_template",
                    details={"error_info": str(e)}
                )
            )
            self.error_handler.handle_error(error)
            
    def _on_delete_template(self):
        """删除模板处理"""
        try:
            # 获取选中的模板
            item = self.template_list.currentItem()
            if not item:
                QMessageBox.warning(self, "警告", "请选择要删除的模板")
                return
                
            # 确认删除
            reply = QMessageBox.question(
                self,
                "确认删除",
                f"确定要删除模板 {item.text()} 吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # 删除模板
                state_name = item.text()
                if state_name in self.state_recognizer.states:
                    del self.state_recognizer.states[state_name]
                    
                if state_name in self.state_recognizer.template_matcher.templates:
                    del self.state_recognizer.template_matcher.templates[state_name]
                    
                # 更新列表
                self._load_templates()
                
                # 清空预览
                self.preview_label.clear()
                self.name_edit.clear()
                self.threshold_spin.setValue(80)
                
        except Exception as e:
            from ...common.error_types import GameAutomationError
            error = GameAutomationError(
                ErrorCode.UI_ERROR,
                "删除模板失败",
                ErrorContext(
                    source="TemplateManagerDialog._on_delete_template",
                    details={"error_info": str(e)}
                )
            )
            self.error_handler.handle_error(error)
            
    def _on_save_template(self):
        """保存模板处理"""
        try:
            # 获取选中的模板
            item = self.template_list.currentItem()
            if not item:
                QMessageBox.warning(self, "警告", "请选择要保存的模板")
                return
                
            # 更新状态
            state_name = item.text()
            state = self.state_recognizer.states.get(state_name)
            if state:
                state.confidence = self.threshold_spin.value() / 100
                
            # 关闭对话框
            self.accept()
            
        except Exception as e:
            from ...common.error_types import GameAutomationError
            error = GameAutomationError(
                ErrorCode.UI_ERROR,
                "保存模板失败",
                ErrorContext(
                    source="TemplateManagerDialog._on_save_template",
                    details={"error_info": str(e)}
                )
            )
            self.error_handler.handle_error(error)