"""
主窗口：排盘直接调用（缓存节气，速度快），支持 AI 流式分析，并排显示
"""
import sys
from PySide6.QtWidgets import (QMainWindow, QLabel, QMenuBar, QStatusBar,
                               QVBoxLayout, QHBoxLayout, QWidget, QPushButton,
                               QApplication, QSplitter, QTextEdit)
from PySide6.QtGui import QAction, QTextCursor
from PySide6.QtCore import Qt, QThread, Signal
from datetime import datetime

from core.qimen.paipan import pai_pan
from .input_dialog import InputDialog
from .qimen_view import QimenView
from .api_settings_dialog import ApiSettingsDialog
from .analysis_dialog import AnalysisDialog  # 保留旧对话框（暂不使用）
from core.llm.analyzer import analyze_qimen_stream, load_config


class QimenWorker(QThread):
    """排盘工作线程"""
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, dt, matter, location):
        super().__init__()
        self.dt = dt
        self.matter = matter
        self.location = location

    def run(self):
        try:
            result = pai_pan(self.dt, self.matter, self.location)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class AnalysisWorker(QThread):
    """AI 分析工作线程（流式）"""
    text_chunk = Signal(str)   # 每个文本块
    finished = Signal()
    error = Signal(str)

    def __init__(self, result, matter, location, api_key, base_url, model):
        super().__init__()
        self.result = result
        self.matter = matter
        self.location = location
        self.api_key = api_key
        self.base_url = base_url
        self.model = model

    def run(self):
        try:
            # 调用生成器，逐块发射
            for chunk in analyze_qimen_stream(
                self.result, self.matter, self.location,
                self.api_key, self.base_url, self.model
            ):
                self.text_chunk.emit(chunk)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("玄学工具箱")
        self.resize(1000, 700)

        self.current_result = None
        self.current_matter = ""
        self.current_location = ""

        # --- 菜单栏 ---
        menubar = self.menuBar()
        qimen_menu = menubar.addMenu("奇门遁甲")
        self.qimen_action = QAction("开始排盘...", self)
        qimen_menu.addAction(self.qimen_action)
        self.qimen_action.triggered.connect(self.on_qimen_start)

        settings_menu = menubar.addMenu("设置")
        self.llm_settings_action = QAction("LLM API 设置...", self)
        settings_menu.addAction(self.llm_settings_action)
        self.llm_settings_action.triggered.connect(self.open_llm_settings)

        # --- 状态栏 ---
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("就绪")

        # --- 中央部件 ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(5, 5, 5, 5)

        # 占位标签（初始显示）
        self.placeholder_label = QLabel("请从菜单选择术数开始", self)
        self.placeholder_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.placeholder_label)

        # 分析按钮（初始隐藏）
        self.analyze_button = QPushButton("🧠 智能分析")
        self.analyze_button.setVisible(False)
        self.analyze_button.clicked.connect(self.on_analyze)
        self.main_layout.addWidget(self.analyze_button)

        # 排盘工作线程引用
        self.worker = None
        # 分析工作线程引用
        self.analysis_worker = None
        # 分割器和视图引用
        self.splitter = None
        self.result_view = None
        self.analysis_text_edit = None

    # --------------------------------------------
    # 排盘流程
    # --------------------------------------------
    def on_qimen_start(self):
        fields = [
            {'name': 'matter', 'label': '预测事项', 'type': 'text', 'default': ''},
            {'name': 'location', 'label': '当前位置', 'type': 'text', 'default': ''},
        ]
        dialog = InputDialog("奇门遁甲排盘", fields, self)
        if dialog.exec() != InputDialog.DialogCode.Accepted:
            return

        values = dialog.get_values()
        self.current_matter = values.get('matter', '')
        self.current_location = values.get('location', '')

        self.qimen_action.setEnabled(False)
        self.status_bar.showMessage("正在计算排盘，请稍候...")

        self.worker = QimenWorker(datetime.now(), self.current_matter, self.current_location)
        self.worker.finished.connect(self.on_pan_finished)
        self.worker.error.connect(self.on_pan_error)
        self.worker.start()

    def on_pan_finished(self, result):
        self.worker = None
        self.qimen_action.setEnabled(True)
        self.current_result = result
        self.status_bar.showMessage("排盘完成")

        # 清除中央布局（保留分析按钮）
        self._clear_central_layout()

        # 创建水平分割器
        self.splitter = QSplitter(Qt.Horizontal)

        # 左侧：九宫格视图
        self.result_view = QimenView(result, self)
        self.splitter.addWidget(self.result_view)

        # 右侧：分析结果文本框（流式显示）
        self.analysis_text_edit = QTextEdit()
        self.analysis_text_edit.setReadOnly(True)
        self.analysis_text_edit.setPlaceholderText("点击「智能分析」按钮，AI 解读将实时显示于此...")
        self.analysis_text_edit.setFontPointSize(11)
        self.splitter.addWidget(self.analysis_text_edit)

        # 设置初始比例（左55%，右45%）
        self.splitter.setSizes([550, 450])

        # 将分割器添加到主布局
        self.main_layout.addWidget(self.splitter)

        # 显示分析按钮
        self.analyze_button.setVisible(True)

    def on_pan_error(self, error_msg):
        self.worker = None
        self.qimen_action.setEnabled(True)
        self.status_bar.showMessage(f"排盘失败: {error_msg}")

    # --------------------------------------------
    # AI 分析流程（流式）
    # --------------------------------------------
    def on_analyze(self):
        if self.current_result is None or self.analysis_text_edit is None:
            return

        config = load_config()
        if not config.get("api_key"):
            self.status_bar.showMessage("请先设置 API Key")
            dlg = ApiSettingsDialog(self)
            dlg.exec()
            config = load_config()
            if not config.get("api_key"):
                self.status_bar.showMessage("未配置 API Key，分析取消")
                return

        # 清空文本框
        self.analysis_text_edit.clear()
        self.analysis_text_edit.setPlaceholderText("")
        self.status_bar.showMessage("正在请求 AI 分析（流式输出）...")
        self.analyze_button.setEnabled(False)   # 防止重复点击

        self.analysis_worker = AnalysisWorker(
            self.current_result,
            self.current_matter,
            self.current_location,
            config.get("api_key"),
            config.get("base_url"),
            config.get("model")
        )
        self.analysis_worker.text_chunk.connect(self.append_analysis_text)
        self.analysis_worker.finished.connect(self.on_analysis_finished)
        self.analysis_worker.error.connect(self.on_analysis_error)
        self.analysis_worker.start()

    def append_analysis_text(self, text):
        """将文本块追加到文本框末尾"""
        if self.analysis_text_edit:
            self.analysis_text_edit.moveCursor(QTextCursor.MoveOperation.End)
            self.analysis_text_edit.insertPlainText(text)
            self.analysis_text_edit.moveCursor(QTextCursor.MoveOperation.End)

    def on_analysis_finished(self):
        self.status_bar.showMessage("分析完成")
        self.analyze_button.setEnabled(True)
        self.analysis_worker = None

    def on_analysis_error(self, err):
        self.status_bar.showMessage(f"分析错误: {err}")
        self.analysis_text_edit.append(f"\n[错误] {err}")
        self.analyze_button.setEnabled(True)
        self.analysis_worker = None

    # --------------------------------------------
    # 辅助方法
    # --------------------------------------------
    def open_llm_settings(self):
        dlg = ApiSettingsDialog(self)
        dlg.exec()

    def _clear_central_layout(self):
        """清空主布局（保留分析按钮），重置相关变量"""
        # 移除所有子控件（保留分析按钮）
        for i in reversed(range(self.main_layout.count())):
            item = self.main_layout.itemAt(i)
            widget = item.widget()
            if widget and widget is not self.analyze_button:
                widget.deleteLater()
        # 重置引用
        self.splitter = None
        self.result_view = None
        self.analysis_text_edit = None
        # 注意：placeholder_label 在首次排盘后也会被删除，无需保留