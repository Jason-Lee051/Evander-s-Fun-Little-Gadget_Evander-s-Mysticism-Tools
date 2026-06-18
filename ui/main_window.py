"""
主窗口：支持奇门遁甲和梅花易数，流式AI分析，并排显示
"""
import sys
from PySide6.QtWidgets import (QMainWindow, QLabel, QMenuBar, QStatusBar,
                               QVBoxLayout, QHBoxLayout, QWidget, QPushButton,
                               QApplication, QSplitter, QTextEdit, QMessageBox)
from PySide6.QtGui import QAction, QTextCursor
from PySide6.QtCore import Qt, QThread, Signal
from datetime import datetime

# 奇门遁甲
from core.qimen.paipan import pai_pan
from .qimen_view import QimenView

# 梅花易数
from core.meihua.qigua import qigua_by_number, qigua_by_time, qigua_by_characters
from core.meihua.paipan import build_full_gua
from .meihua_view import MeihuaView

# LLM
from core.llm.analyzer import (
    analyze_qimen_stream, analyze_meihua_stream,
    load_config
)

from .input_dialog import InputDialog
from .api_settings_dialog import ApiSettingsDialog


# ---------- 工作线程 ----------
class QimenWorker(QThread):
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
    text_chunk = Signal(str)
    finished = Signal()
    error = Signal(str)
    def __init__(self, method, data, matter, location, api_key, base_url, model):
        super().__init__()
        self.method = method          # 'qimen' or 'meihua'
        self.data = data
        self.matter = matter
        self.location = location
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
    def run(self):
        try:
            if self.method == 'qimen':
                generator = analyze_qimen_stream(
                    self.data, self.matter, self.location,
                    self.api_key, self.base_url, self.model
                )
            else:  # meihua
                generator = analyze_meihua_stream(
                    self.data, self.matter, self.location,
                    self.api_key, self.base_url, self.model
                )
            for chunk in generator:
                self.text_chunk.emit(chunk)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("玄学工具箱")
        self.resize(1100, 750)

        self.current_method = None          # 'qimen' or 'meihua'
        self.current_result = None
        self.current_matter = ""
        self.current_location = ""

        # 菜单
        menubar = self.menuBar()
        # 奇门遁甲
        qimen_menu = menubar.addMenu("奇门遁甲")
        self.qimen_action = QAction("开始排盘...", self)
        qimen_menu.addAction(self.qimen_action)
        self.qimen_action.triggered.connect(self.on_qimen_start)

        # 梅花易数
        meihua_menu = menubar.addMenu("梅花易数")
        self.meihua_action = QAction("开始起卦...", self)
        meihua_menu.addAction(self.meihua_action)
        self.meihua_action.triggered.connect(self.on_meihua_start)

        settings_menu = menubar.addMenu("设置")
        self.llm_settings_action = QAction("LLM API 设置...", self)
        settings_menu.addAction(self.llm_settings_action)
        self.llm_settings_action.triggered.connect(self.open_llm_settings)

        # 状态栏
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("就绪")

        # 中央部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(5, 5, 5, 5)

        # 占位标签
        self.placeholder_label = QLabel("请从菜单选择术数开始", self)
        self.placeholder_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.placeholder_label)

        # 分析按钮
        self.analyze_button = QPushButton("🧠 智能分析")
        self.analyze_button.setVisible(False)
        self.analyze_button.clicked.connect(self.on_analyze)
        self.main_layout.addWidget(self.analyze_button)

        # 工作线程引用
        self.worker = None
        self.analysis_worker = None
        self.splitter = None
        self.result_view = None
        self.analysis_text_edit = None

    # ---------- 奇门遁甲 ----------
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
        self.current_method = 'qimen'

        self.qimen_action.setEnabled(False)
        self.meihua_action.setEnabled(False)
        self.status_bar.showMessage("正在计算排盘，请稍候...")

        self.worker = QimenWorker(datetime.now(), self.current_matter, self.current_location)
        self.worker.finished.connect(self.on_pan_finished)
        self.worker.error.connect(self.on_pan_error)
        self.worker.start()

    # ---------- 梅花易数 ----------
    def on_meihua_start(self):
        # 选择起卦方式
        fields = [
            {'name': 'method', 'label': '起卦方式', 'type': 'select', 'default': '数字起卦', 'options': ['数字起卦', '时间起卦', '汉字起卦']},
        ]
        # 根据起卦方式动态显示输入字段（在输入对话框中通过后续逻辑处理）
        # 我们使用通用对话框，但需根据选择显示不同字段，这里简化处理：显示所有可能字段
        fields += [
            {'name': 'num1', 'label': '第一个数字', 'type': 'text', 'default': ''},
            {'name': 'num2', 'label': '第二个数字', 'type': 'text', 'default': ''},
            {'name': 'num3', 'label': '第三个数字', 'type': 'text', 'default': ''},
            {'name': 'question', 'label': '所问事项', 'type': 'text', 'default': ''},
            {'name': 'background', 'label': '背景信息（可选）', 'type': 'text', 'default': ''},
        ]
        dialog = InputDialog("梅花易数起卦", fields, self)
        if dialog.exec() != InputDialog.DialogCode.Accepted:
            return
        values = dialog.get_values()
        method = values.get('method', '数字起卦')
        question = values.get('question', '')
        background = values.get('background', '')
        self.current_matter = question
        self.current_location = background
        self.current_method = 'meihua'

        # 执行起卦
        try:
            if method == '数字起卦':
                num1 = int(values.get('num1', 0) or 0)
                num2 = int(values.get('num2', 0) or 0)
                num3 = int(values.get('num3', 0) or 0)
                if num1 == 0 and num2 == 0 and num3 == 0:
                    QMessageBox.warning(self, "提示", "请至少输入一个非零数字")
                    return
                upper, lower, moving = qigua_by_number(num1, num2, num3)
            elif method == '时间起卦':
                # 使用当前时间
                dt = datetime.now()
                upper, lower, moving = qigua_by_time(dt)
            else:  # 汉字起卦
                text = values.get('num1', '')  # 使用第一个字段输入汉字
                if not text:
                    QMessageBox.warning(self, "提示", "请输入汉字")
                    return
                upper, lower, moving = qigua_by_characters(text, mode="word")
        except Exception as e:
            QMessageBox.critical(self, "起卦错误", str(e))
            return

        # 构建卦盘
        self.current_result = build_full_gua(upper, lower, moving)
        # 保存额外信息
        self.current_result['question'] = question
        self.current_result['background'] = background

        self.qimen_action.setEnabled(False)
        self.meihua_action.setEnabled(False)
        self.status_bar.showMessage("起卦完成，显示卦象...")

        # 直接显示卦象（无需异步）
        self.on_pan_finished(self.current_result)

    # ---------- 显示结果 ----------
    def on_pan_finished(self, result):
        self.worker = None
        self.qimen_action.setEnabled(True)
        self.meihua_action.setEnabled(True)
        self.current_result = result
        self.status_bar.showMessage("排盘/起卦完成")

        self._clear_central_layout()

        # 创建分割器
        self.splitter = QSplitter(Qt.Horizontal)

        # 左侧视图（根据术数类型）
        if self.current_method == 'qimen':
            self.result_view = QimenView(result, self)
        else:
            self.result_view = MeihuaView(result, self)
        self.splitter.addWidget(self.result_view)

        # 右侧文本框
        self.analysis_text_edit = QTextEdit()
        self.analysis_text_edit.setReadOnly(True)
        self.analysis_text_edit.setPlaceholderText("点击「智能分析」按钮，AI 解读将实时显示于此...")
        self.analysis_text_edit.setFontPointSize(11)
        self.splitter.addWidget(self.analysis_text_edit)

        self.splitter.setSizes([550, 450])
        self.main_layout.addWidget(self.splitter)

        self.analyze_button.setVisible(True)

    def on_pan_error(self, error_msg):
        self.worker = None
        self.qimen_action.setEnabled(True)
        self.meihua_action.setEnabled(True)
        self.status_bar.showMessage(f"排盘失败: {error_msg}")

    # ---------- AI 分析 ----------
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

        self.analysis_text_edit.clear()
        self.analysis_text_edit.setPlaceholderText("")
        self.status_bar.showMessage("正在请求 AI 分析（流式输出）...")
        self.analyze_button.setEnabled(False)

        # 根据方法选择分析函数
        method = self.current_method
        data = self.current_result
        matter = self.current_matter
        location = self.current_location

        self.analysis_worker = AnalysisWorker(
            method, data, matter, location,
            config.get("api_key"),
            config.get("base_url"),
            config.get("model")
        )
        self.analysis_worker.text_chunk.connect(self.append_analysis_text)
        self.analysis_worker.finished.connect(self.on_analysis_finished)
        self.analysis_worker.error.connect(self.on_analysis_error)
        self.analysis_worker.start()

    def append_analysis_text(self, text):
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

    # ---------- 辅助 ----------
    def open_llm_settings(self):
        dlg = ApiSettingsDialog(self)
        dlg.exec()

    def _clear_central_layout(self):
        for i in reversed(range(self.main_layout.count())):
            item = self.main_layout.itemAt(i)
            widget = item.widget()
            if widget and widget is not self.analyze_button:
                widget.deleteLater()
        self.splitter = None
        self.result_view = None
        self.analysis_text_edit = None