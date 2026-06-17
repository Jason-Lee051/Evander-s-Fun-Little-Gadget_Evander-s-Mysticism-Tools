"""
ui/analysis_dialog.py - 显示 AI 分析结果
"""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt

class AnalysisDialog(QDialog):
    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("智能分析结果")
        self.resize(700, 600)

        layout = QVBoxLayout(self)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setText(text)
        layout.addWidget(self.text_edit)

        button_layout = QHBoxLayout()
        self.copy_btn = QPushButton("复制全文")
        self.copy_btn.clicked.connect(self.copy_text)
        button_layout.addWidget(self.copy_btn)

        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.close_btn)

        layout.addLayout(button_layout)

    def copy_text(self):
        self.text_edit.selectAll()
        self.text_edit.copy()
        # 简单提示
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(self.text_edit.toPlainText())