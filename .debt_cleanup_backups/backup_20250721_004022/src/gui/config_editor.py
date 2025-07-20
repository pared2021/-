"""
配置编辑器界面
提供可视化的配置编辑功能
"""
from typing import Dict, Any, Optional
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QTreeWidget,
    QTreeWidgetItem,
    QLineEdit,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QCheckBox,
    QMessageBox,
)
from PyQt6.QtCore import Qt, pyqtSignal


class ConfigEditor(QWidget):
    """配置编辑器"""

    # 配置改变信号
    config_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_config: Dict[str, Any] = {}
        self._create_ui()

    def _create_ui(self):
        """创建UI界面"""
        layout = QHBoxLayout(self)

        # 左侧配置树
        self.config_tree = QTreeWidget()
        self.config_tree.setHeaderLabels(["配置项", "值"])
        self.config_tree.itemChanged.connect(self._on_item_changed)
        layout.addWidget(self.config_tree)

        # 右侧编辑面板
        edit_panel = self._create_edit_panel()
        layout.addWidget(edit_panel)

    def _create_edit_panel(self) -> QWidget:
        """创建编辑面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # 添加配置项
        add_group = QWidget()
        add_layout = QHBoxLayout(add_group)

        self.key_edit = QLineEdit()
        self.key_edit.setPlaceholderText("配置项名称")
        add_layout.addWidget(self.key_edit)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["字符串", "数字", "布尔值", "列表", "字典"])
        add_layout.addWidget(self.type_combo)

        add_button = QPushButton("添加")
        add_button.clicked.connect(self._on_add_config)
        add_layout.addWidget(add_button)

        layout.addWidget(add_group)

        # 编辑区域
        self.edit_stack = QWidget()
        self.edit_layout = QVBoxLayout(self.edit_stack)
        layout.addWidget(self.edit_stack)

        return panel

    def load_config(self, config: Dict[str, Any]):
        """加载配置"""
        self.current_config = config.copy()
        self._update_tree()

    def get_config(self) -> Dict[str, Any]:
        """获取配置"""
        return self.current_config.copy()

    def _update_tree(self):
        """更新配置树"""
        self.config_tree.clear()

        def add_items(parent: Optional[QTreeWidgetItem], data: Dict[str, Any]):
            for key, value in data.items():
                if isinstance(value, dict):
                    item = QTreeWidgetItem(parent, [key, ""])
                    add_items(item, value)
                else:
                    item = QTreeWidgetItem(parent, [key, str(value)])
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)

        add_items(self.config_tree.invisibleRootItem(), self.current_config)
        self.config_tree.expandAll()

    def _on_item_changed(self, item: QTreeWidgetItem, column: int):
        """配置项改变"""
        if column != 1:  # 只处理值列
            return

        try:
            key = item.text(0)
            value = item.text(1)

            # 尝试转换值类型
            if value.lower() in ("true", "false"):
                value = value.lower() == "true"
            else:
                try:
                    value = int(value)
                except ValueError:
                    try:
                        value = float(value)
                    except ValueError:
                        pass

            # 更新配置
            self._update_config_value(key, value)

        except Exception as e:
            QMessageBox.warning(self, "警告", f"更新配置失败: {str(e)}")
            self._update_tree()  # 恢复显示

    def _update_config_value(self, key: str, value: Any):
        """更新配置值"""

        def update_dict(d: Dict[str, Any], key_path: str, value: Any):
            parts = key_path.split(".")
            for part in parts[:-1]:
                d = d.setdefault(part, {})
            d[parts[-1]] = value

        update_dict(self.current_config, key, value)
        self.config_changed.emit(self.current_config)

    def _on_add_config(self):
        """添加配置项"""
        key = self.key_edit.text().strip()
        if not key:
            QMessageBox.warning(self, "警告", "请输入配置项名称")
            return

        # 创建默认值
        type_text = self.type_combo.currentText()
        if type_text == "字符串":
            value = ""
        elif type_text == "数字":
            value = 0
        elif type_text == "布尔值":
            value = False
        elif type_text == "列表":
            value = []
        else:  # 字典
            value = {}

        # 更新配置
        self._update_config_value(key, value)
        self._update_tree()

        # 清空输入
        self.key_edit.clear()

    def _create_value_editor(self, value: Any) -> QWidget:
        """创建值编辑器"""
        if isinstance(value, bool):
            editor = QCheckBox()
            editor.setChecked(value)
            return editor
        elif isinstance(value, int):
            editor = QSpinBox()
            editor.setValue(value)
            return editor
        elif isinstance(value, float):
            editor = QDoubleSpinBox()
            editor.setValue(value)
            return editor
        elif isinstance(value, list):
            editor = ListEditor(value)
            return editor
        elif isinstance(value, dict):
            editor = DictEditor(value)
            return editor
        else:
            editor = QLineEdit()
            editor.setText(str(value))
            return editor


class ListEditor(QWidget):
    """列表编辑器"""

    def __init__(self, values: list, parent=None):
        super().__init__(parent)
        self.values = values.copy()
        self._create_ui()

    def _create_ui(self):
        layout = QVBoxLayout(self)

        # 列表显示
        self.list_widget = QTreeWidget()
        self.list_widget.setHeaderLabels(["索引", "值"])
        self._update_list()
        layout.addWidget(self.list_widget)

        # 控制按钮
        button_group = QWidget()
        button_layout = QHBoxLayout(button_group)

        add_button = QPushButton("添加")
        add_button.clicked.connect(self._on_add_item)
        button_layout.addWidget(add_button)

        remove_button = QPushButton("删除")
        remove_button.clicked.connect(self._on_remove_item)
        button_layout.addWidget(remove_button)

        layout.addWidget(button_group)

    def _update_list(self):
        """更新列表显示"""
        self.list_widget.clear()
        for i, value in enumerate(self.values):
            item = QTreeWidgetItem([str(i), str(value)])
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
            self.list_widget.addTopLevelItem(item)

    def _on_add_item(self):
        """添加项目"""
        self.values.append("")
        self._update_list()

    def _on_remove_item(self):
        """删除项目"""
        item = self.list_widget.currentItem()
        if item:
            index = int(item.text(0))
            del self.values[index]
            self._update_list()


class DictEditor(QWidget):
    """字典编辑器"""

    def __init__(self, values: dict, parent=None):
        super().__init__(parent)
        self.values = values.copy()
        self._create_ui()

    def _create_ui(self):
        layout = QVBoxLayout(self)

        # 字典显示
        self.dict_widget = QTreeWidget()
        self.dict_widget.setHeaderLabels(["键", "值"])
        self._update_dict()
        layout.addWidget(self.dict_widget)

        # 控制按钮
        button_group = QWidget()
        button_layout = QHBoxLayout(button_group)

        add_button = QPushButton("添加")
        add_button.clicked.connect(self._on_add_item)
        button_layout.addWidget(add_button)

        remove_button = QPushButton("删除")
        remove_button.clicked.connect(self._on_remove_item)
        button_layout.addWidget(remove_button)

        layout.addWidget(button_group)

    def _update_dict(self):
        """更新字典显示"""
        self.dict_widget.clear()
        for key, value in self.values.items():
            item = QTreeWidgetItem([str(key), str(value)])
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
            self.dict_widget.addTopLevelItem(item)

    def _on_add_item(self):
        """添加项目"""
        self.values["new_key"] = ""
        self._update_dict()

    def _on_remove_item(self):
        """删除项目"""
        item = self.dict_widget.currentItem()
        if item:
            key = item.text(0)
            del self.values[key]
            self._update_dict()
