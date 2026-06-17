"""
主窗口：排盘直接调用（缓存节气，速度快），支持 AI 分析
修改：异步排盘，避免UI卡死；修复布局清理时的死循环
"""
from PySide6.QtWidgets import (QMainWindow, QLabel, QMenuBar, QStatusBar,
                               QVBoxLayout, QWidget, QPushButton, QApplication)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QThread, Signal
from datetime import datetime

from core.qimen.paipan import pai_pan
from .input_dialog import InputDialog
from .qimen_view import QimenView
from .api_settings_dialog import ApiSettingsDialog
from .analysis_dialog import AnalysisDialog
from core.llm.analyzer import analyze_qimen, load_config


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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("玄学工具箱")
        self.resize(900, 700)

        self.current_result = None
        self.current_matter = ""
        self.current_location = ""

        menubar = self.menuBar()
        qimen_menu = menubar.addMenu("奇门遁甲")
        self.qimen_action = QAction("开始排盘...", self)
        qimen_menu.addAction(self.qimen_action)
        self.qimen_action.triggered.connect(self.on_qimen_start)

        settings_menu = menubar.addMenu("设置")
        self.llm_settings_action = QAction("LLM API 设置...", self)
        settings_menu.addAction(self.llm_settings_action)
        self.llm_settings_action.triggered.connect(self.open_llm_settings)

        self.status_bar = self.statusBar()
        self.status_bar.showMessage("就绪")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.placeholder_label = QLabel("请从菜单选择术数开始", self)
        self.placeholder_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.placeholder_label)

        self.analyze_button = QPushButton("🧠 智能分析")
        self.analyze_button.setVisible(False)
        self.analyze_button.clicked.connect(self.on_analyze)
        self.main_layout.addWidget(self.analyze_button)

        self.worker = None

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
        view = QimenView(result, self)
        self._clear_central_layout()          # 清空除分析按钮外的所有控件
        self.main_layout.addWidget(view)
        self.analyze_button.setVisible(True)  # 显示分析按钮

    def on_pan_error(self, error_msg):
        self.worker = None
        self.qimen_action.setEnabled(True)
        self.status_bar.showMessage(f"排盘失败: {error_msg}")

    def on_analyze(self):
        if self.current_result is None:
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
        self.status_bar.showMessage("正在请求 AI 分析...")
        QApplication.processEvents()
        try:
            analysis_text = analyze_qimen(
                result=self.current_result,
                matter=self.current_matter,
                location=self.current_location,
                api_key=config.get("api_key"),
                base_url=config.get("base_url"),
                model=config.get("model")
            )
        except Exception as e:
            analysis_text = f"分析失败：{str(e)}"
        self.status_bar.showMessage("分析完成")
        dlg = AnalysisDialog(analysis_text, self)
        dlg.exec()

    def open_llm_settings(self):
        dlg = ApiSettingsDialog(self)
        dlg.exec()

    def _clear_central_layout(self):
        """清空布局，但保留分析按钮（以便后续重新显示）"""
        keep_widgets = []
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            widget = item.widget()
            if widget is self.analyze_button:
                keep_widgets.append(widget)
            elif widget:
                widget.deleteLater()
        # 将保留的按钮重新添加
        for w in keep_widgets:
            self.main_layout.addWidget(w)