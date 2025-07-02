"""
自动化管理对话框
"""
from typing import Optional, List, Dict
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                           QPushButton, QListWidget, QListWidgetItem, QSpinBox,
                           QLineEdit, QGroupBox, QMessageBox, QComboBox, QWidget)
from PyQt6.QtCore import Qt, pyqtSignal

from services.automation.auto_controller import AutoController, Action
from services.vision.state_recognizer import StateRecognizer
from src.services.error_handler import ErrorHandler
from src.common.error_types import ErrorCode, ErrorContext

class AutomationManagerDialog(QDialog):
    """自动化管理对话框"""
    
    def __init__(self, auto_controller: AutoController,
                 state_recognizer: StateRecognizer,
                 error_handler: ErrorHandler, parent=None):
        """初始化
        
        Args:
            auto_controller: 自动化控制器
            state_recognizer: 状态识别器
            error_handler: 错误处理器
            parent: 父窗口
        """
        super().__init__(parent)
        
        self.auto_controller = auto_controller
        self.state_recognizer = state_recognizer
        self.error_handler = error_handler
        
        self._init_ui()
        self._load_actions()
        
    def _init_ui(self):
        """初始化UI"""
        # 设置窗口属性
        self.setWindowTitle("自动化管理")
        self.setMinimumSize(800, 600)
        
        # 创建主布局
        layout = QVBoxLayout(self)
        
        # 创建动作列表
        action_group = QGroupBox("动作列表")
        action_layout = QVBoxLayout(action_group)
        
        self.action_list = QListWidget()
        self.action_list.itemClicked.connect(self._on_action_selected)
        action_layout.addWidget(self.action_list)
        
        # 创建动作操作按钮
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("添加")
        self.add_button.clicked.connect(self._on_add_action)
        button_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("编辑")
        self.edit_button.clicked.connect(self._on_edit_action)
        button_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("删除")
        self.delete_button.clicked.connect(self._on_delete_action)
        button_layout.addWidget(self.delete_button)
        
        action_layout.addLayout(button_layout)
        layout.addWidget(action_group)
        
        # 创建动作编辑
        edit_group = QGroupBox("动作编辑")
        edit_layout = QVBoxLayout(edit_group)
        
        # 动作名称
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("动作名称:"))
        self.name_edit = QLineEdit()
        name_layout.addWidget(self.name_edit)
        edit_layout.addLayout(name_layout)
        
        # 动作类型
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("动作类型:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["click", "key", "wait", "condition"])
        self.type_combo.currentTextChanged.connect(self._on_type_changed)
        type_layout.addWidget(self.type_combo)
        edit_layout.addLayout(type_layout)
        
        # 动作参数
        param_group = QGroupBox("动作参数")
        self.param_layout = QVBoxLayout(param_group)
        
        # 点击参数
        self.click_params = QWidget()
        click_layout = QVBoxLayout(self.click_params)
        
        x_layout = QHBoxLayout()
        x_layout.addWidget(QLabel("X坐标:"))
        self.x_spin = QSpinBox()
        self.x_spin.setRange(0, 9999)
        x_layout.addWidget(self.x_spin)
        click_layout.addLayout(x_layout)
        
        y_layout = QHBoxLayout()
        y_layout.addWidget(QLabel("Y坐标:"))
        self.y_spin = QSpinBox()
        self.y_spin.setRange(0, 9999)
        y_layout.addWidget(self.y_spin)
        click_layout.addLayout(y_layout)
        
        # 按键参数
        self.key_params = QWidget()
        key_layout = QVBoxLayout(self.key_params)
        
        key_layout.addWidget(QLabel("按键:"))
        self.key_edit = QLineEdit()
        key_layout.addWidget(self.key_edit)
        
        # 等待参数
        self.wait_params = QWidget()
        wait_layout = QVBoxLayout(self.wait_params)
        
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("等待时间(秒):"))
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(0, 9999)
        duration_layout.addWidget(self.duration_spin)
        wait_layout.addLayout(duration_layout)
        
        # 条件参数
        self.condition_params = QWidget()
        condition_layout = QVBoxLayout(self.condition_params)
        
        state_layout = QHBoxLayout()
        state_layout.addWidget(QLabel("状态名称:"))
        self.state_combo = QComboBox()
        state_layout.addWidget(self.state_combo)
        condition_layout.addLayout(state_layout)
        
        # 添加参数组
        self.param_layout.addWidget(self.click_params)
        self.param_layout.addWidget(self.key_params)
        self.param_layout.addWidget(self.wait_params)
        self.param_layout.addWidget(self.condition_params)
        
        edit_layout.addWidget(param_group)
        
        # 动作属性
        attr_group = QGroupBox("动作属性")
        attr_layout = QVBoxLayout(attr_group)
        
        # 超时时间
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("超时时间(秒):"))
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(0, 9999)
        self.timeout_spin.setValue(5)
        timeout_layout.addWidget(self.timeout_spin)
        attr_layout.addLayout(timeout_layout)
        
        # 重试次数
        retry_layout = QHBoxLayout()
        retry_layout.addWidget(QLabel("重试次数:"))
        self.retry_spin = QSpinBox()
        self.retry_spin.setRange(0, 9999)
        self.retry_spin.setValue(3)
        retry_layout.addWidget(self.retry_spin)
        attr_layout.addLayout(retry_layout)
        
        edit_layout.addWidget(attr_group)
        layout.addWidget(edit_group)
        
        # 创建对话框按钮
        dialog_button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self._on_save_action)
        dialog_button_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        dialog_button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(dialog_button_layout)
        
        # 初始化参数显示
        self._update_param_display()
        
    def _load_actions(self):
        """加载动作列表"""
        try:
            # 清空列表
            self.action_list.clear()
            
            # 获取所有动作
            for action in self.auto_controller.actions:
                item = QListWidgetItem(action.name)
                self.action_list.addItem(item)
                
            # 更新状态列表
            self.state_combo.clear()
            for state_name in self.state_recognizer.states:
                self.state_combo.addItem(state_name)
                
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.UI_ERROR,
                "加载动作列表失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="AutomationManagerDialog._load_actions"
                )
            )
            
    def _on_action_selected(self, item: QListWidgetItem):
        """动作选择处理
        
        Args:
            item: 选中的列表项
        """
        try:
            # 获取动作信息
            action_name = item.text()
            action = next((a for a in self.auto_controller.actions 
                         if a.name == action_name), None)
            
            if action:
                # 更新信息
                self.name_edit.setText(action.name)
                self.type_combo.setCurrentText(action.type)
                self.timeout_spin.setValue(int(action.timeout))
                self.retry_spin.setValue(action.retry_count)
                
                # 更新参数
                if action.type == "click":
                    self.x_spin.setValue(action.params.get("x", 0))
                    self.y_spin.setValue(action.params.get("y", 0))
                elif action.type == "key":
                    self.key_edit.setText(action.params.get("key", ""))
                elif action.type == "wait":
                    self.duration_spin.setValue(action.params.get("duration", 1))
                elif action.type == "condition":
                    state_name = action.params.get("state", "")
                    index = self.state_combo.findText(state_name)
                    if index >= 0:
                        self.state_combo.setCurrentIndex(index)
                        
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.UI_ERROR,
                "选择动作失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="AutomationManagerDialog._on_action_selected"
                )
            )
            
    def _on_type_changed(self, action_type: str):
        """动作类型改变处理
        
        Args:
            action_type: 动作类型
        """
        self._update_param_display()
        
    def _update_param_display(self):
        """更新参数显示"""
        # 隐藏所有参数组
        self.click_params.hide()
        self.key_params.hide()
        self.wait_params.hide()
        self.condition_params.hide()
        
        # 显示当前类型的参数组
        action_type = self.type_combo.currentText()
        if action_type == "click":
            self.click_params.show()
        elif action_type == "key":
            self.key_params.show()
        elif action_type == "wait":
            self.wait_params.show()
        elif action_type == "condition":
            self.condition_params.show()
            
    def _on_add_action(self):
        """添加动作处理"""
        try:
            # 获取动作信息
            action_name = self.name_edit.text()
            if not action_name:
                QMessageBox.warning(self, "警告", "请输入动作名称")
                return
                
            action_type = self.type_combo.currentText()
            params = {}
            
            # 获取参数
            if action_type == "click":
                params["x"] = self.x_spin.value()
                params["y"] = self.y_spin.value()
            elif action_type == "key":
                params["key"] = self.key_edit.text()
            elif action_type == "wait":
                params["duration"] = self.duration_spin.value()
            elif action_type == "condition":
                params["state"] = self.state_combo.currentText()
                
            # 创建动作
            action = Action(
                name=action_name,
                type=action_type,
                params=params,
                timeout=self.timeout_spin.value(),
                retry_count=self.retry_spin.value()
            )
            
            # 添加动作
            self.auto_controller.add_action(action)
            
            # 更新列表
            self._load_actions()
            
            # 选择新添加的动作
            items = self.action_list.findItems(action_name, Qt.MatchFlag.MatchExactly)
            if items:
                self.action_list.setCurrentItem(items[0])
                
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.UI_ERROR,
                "添加动作失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="AutomationManagerDialog._on_add_action"
                )
            )
            
    def _on_edit_action(self):
        """编辑动作处理"""
        try:
            # 获取选中的动作
            item = self.action_list.currentItem()
            if not item:
                QMessageBox.warning(self, "警告", "请选择要编辑的动作")
                return
                
            # 获取动作信息
            action_name = item.text()
            action = next((a for a in self.auto_controller.actions 
                         if a.name == action_name), None)
            
            if action:
                # 更新动作
                action.name = self.name_edit.text()
                action.type = self.type_combo.currentText()
                action.timeout = self.timeout_spin.value()
                action.retry_count = self.retry_spin.value()
                
                # 更新参数
                if action.type == "click":
                    action.params["x"] = self.x_spin.value()
                    action.params["y"] = self.y_spin.value()
                elif action.type == "key":
                    action.params["key"] = self.key_edit.text()
                elif action.type == "wait":
                    action.params["duration"] = self.duration_spin.value()
                elif action.type == "condition":
                    action.params["state"] = self.state_combo.currentText()
                    
                # 更新列表
                self._load_actions()
                
                # 选择编辑后的动作
                items = self.action_list.findItems(action.name, Qt.MatchFlag.MatchExactly)
                if items:
                    self.action_list.setCurrentItem(items[0])
                    
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.UI_ERROR,
                "编辑动作失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="AutomationManagerDialog._on_edit_action"
                )
            )
            
    def _on_delete_action(self):
        """删除动作处理"""
        try:
            # 获取选中的动作
            item = self.action_list.currentItem()
            if not item:
                QMessageBox.warning(self, "警告", "请选择要删除的动作")
                return
                
            # 确认删除
            reply = QMessageBox.question(
                self,
                "确认删除",
                f"确定要删除动作 {item.text()} 吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # 删除动作
                action_name = item.text()
                self.auto_controller.actions = [
                    a for a in self.auto_controller.actions
                    if a.name != action_name
                ]
                
                # 更新列表
                self._load_actions()
                
                # 清空编辑
                self.name_edit.clear()
                self.type_combo.setCurrentIndex(0)
                self.timeout_spin.setValue(5)
                self.retry_spin.setValue(3)
                self.x_spin.setValue(0)
                self.y_spin.setValue(0)
                self.key_edit.clear()
                self.duration_spin.setValue(1)
                self.state_combo.setCurrentIndex(0)
                
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.UI_ERROR,
                "删除动作失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="AutomationManagerDialog._on_delete_action"
                )
            )
            
    def _on_save_action(self):
        """保存动作处理"""
        try:
            # 获取选中的动作
            item = self.action_list.currentItem()
            if not item:
                QMessageBox.warning(self, "警告", "请选择要保存的动作")
                return
                
            # 更新动作
            self._on_edit_action()
            
            # 关闭对话框
            self.accept()
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.UI_ERROR,
                "保存动作失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="AutomationManagerDialog._on_save_action"
                )
            ) 