"""
ui/input_dialog.py - 通用输入对话框，根据术数需要的字段动态生成表单
"""
from PySide6.QtWidgets import (QDialog, QFormLayout, QLineEdit,
                               QComboBox, QDateTimeEdit, QDialogButtonBox,
                               QVBoxLayout, QLabel)
from PySide6.QtCore import QDateTime
from typing import Dict, Any, List

class InputDialog(QDialog):
    def __init__(self, title: str, fields: List[Dict[str, Any]], parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(400, 250)
        self.fields = fields
        self.inputs = {}

        layout = QVBoxLayout(self)
        form = QFormLayout()

        for field in fields:
            name = field.get('name')
            label = field.get('label', name)
            ftype = field.get('type', 'text')
            default = field.get('default', '')
            options = field.get('options', None)

            if ftype == 'select' and options:
                widget = QComboBox()
                widget.addItems(options)
                widget.setCurrentText(default if default in options else options[0])
            elif ftype == 'datetime':
                widget = QDateTimeEdit()
                widget.setCalendarPopup(True)
                widget.setDateTime(QDateTime.currentDateTime())
            else:
                widget = QLineEdit()
                widget.setText(str(default))
                widget.setPlaceholderText(label)

            self.inputs[name] = widget
            form.addRow(label, widget)

        layout.addLayout(form)

        # 提示信息
        hint_label = QLabel("请输入信息后点击“开始排盘”")
        layout.addWidget(hint_label)

        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.button(QDialogButtonBox.Ok).setText("开始排盘")
        button_box.button(QDialogButtonBox.Cancel).setText("取消")
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_values(self) -> Dict[str, Any]:
        """返回用户输入的值字典"""
        values = {}
        for name, widget in self.inputs.items():
            if isinstance(widget, QLineEdit):
                values[name] = widget.text()
            elif isinstance(widget, QComboBox):
                values[name] = widget.currentText()
            elif isinstance(widget, QDateTimeEdit):
                values[name] = widget.dateTime().toPython()
        return values