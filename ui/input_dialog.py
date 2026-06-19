"""
ui/input_dialog.py - 通用输入对话框，支持根据选择动态显示/隐藏字段
"""
from PySide6.QtWidgets import (QDialog, QLineEdit,
                               QComboBox, QDateTimeEdit, QDialogButtonBox,
                               QVBoxLayout, QHBoxLayout, QLabel, QWidget)
from PySide6.QtCore import QDateTime
from typing import Dict, Any, List

class InputDialog(QDialog):
    def __init__(self, title: str, fields: List[Dict[str, Any]], parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(450, 300)
        self.fields = fields
        self.inputs = {}
        self.rows = {}  # name -> (label_widget, input_widget, container_widget)
        self.conditional_fields = []  # 存储条件字段信息

        layout = QVBoxLayout(self)
        self.main_layout = QVBoxLayout()
        layout.addLayout(self.main_layout)

        # 构建动态行
        for field in fields:
            name = field.get('name')
            label = field.get('label', name)
            ftype = field.get('type', 'text')
            default = field.get('default', '')
            options = field.get('options', None)
            visible_if = field.get('visible_if', None)

            # 行容器
            row_container = QWidget()
            row_layout = QHBoxLayout(row_container)
            row_layout.setContentsMargins(0, 0, 0, 0)

            # 标签
            label_widget = QLabel(label)
            label_widget.setFixedWidth(120)
            row_layout.addWidget(label_widget)

            # 输入控件
            if ftype == 'select' and options:
                widget = QComboBox()
                widget.addItems(options)
                if default in options:
                    widget.setCurrentText(default)
                else:
                    widget.setCurrentIndex(0)
                if name == 'method':  # 约定条件字段为 'method'
                    widget.currentTextChanged.connect(self.on_condition_changed)
            elif ftype == 'datetime':
                widget = QDateTimeEdit()
                widget.setCalendarPopup(True)
                widget.setDateTime(QDateTime.currentDateTime())
            else:
                widget = QLineEdit()
                widget.setText(str(default))
                widget.setPlaceholderText(label)

            row_layout.addWidget(widget)
            self.inputs[name] = widget
            self.rows[name] = (label_widget, widget, row_container)

            # 记录条件信息
            if visible_if:
                self.conditional_fields.append((name, visible_if))

            self.main_layout.addWidget(row_container)

        # 按钮
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.button(QDialogButtonBox.Ok).setText("确定")
        self.button_box.button(QDialogButtonBox.Cancel).setText("取消")
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.main_layout.addWidget(self.button_box)

        # 初始化可见性
        self.update_visibility()

    def on_condition_changed(self, value):
        self.update_visibility()

    def update_visibility(self):
        # 获取条件字段的值
        method_widget = self.inputs.get('method')
        if not method_widget:
            return
        current_method = method_widget.currentText()

        # 遍历条件字段
        for name, visible_if in self.conditional_fields:
            if visible_if.get('field') == 'method':
                should_show = (visible_if.get('value') == current_method)
                if name in self.rows:
                    _, _, container = self.rows[name]
                    container.setVisible(should_show)

    def get_values(self) -> Dict[str, Any]:
        values = {}
        for name, widget in self.inputs.items():
            if isinstance(widget, QLineEdit):
                values[name] = widget.text()
            elif isinstance(widget, QComboBox):
                values[name] = widget.currentText()
            elif isinstance(widget, QDateTimeEdit):
                values[name] = widget.dateTime().toPython()
        return values