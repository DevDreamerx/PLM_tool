# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QStackedWidget,
    QListWidget,
    QFrame,
    QStatusBar,
    QMessageBox,
)
from PyQt5.QtCore import Qt
from db.database import DatabaseManager
from ui.entry_widget import EntryWidget
from ui.query_widget import QueryWidget
from ui.kanban_widget import KanbanWidget
from ui.report_widget import ReportWidget
from ui.settings_widget import SettingsWidget
from ui.detail_dialog import DetailDialog
from utils.backup import BackupManager


class MainWindow(QMainWindow):
    """主窗口类"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("技术状态管理助手 - Demo")
        self.resize(1280, 820)
        self.backup_manager = BackupManager()
        self.db = DatabaseManager()
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        nav_frame = QFrame()
        nav_frame.setObjectName("NavFrame")
        nav_frame.setFixedWidth(220)
        nav_layout = QVBoxLayout(nav_frame)
        nav_layout.setContentsMargins(16, 18, 16, 16)
        nav_layout.setSpacing(10)

        nav_title = QLabel("技术状态管理")
        nav_title.setObjectName("NavTitle")
        nav_layout.addWidget(nav_title)

        nav_subtitle = QLabel("TSM Console")
        nav_subtitle.setObjectName("NavSubtitle")
        nav_layout.addWidget(nav_subtitle)

        nav_layout.addSpacing(10)

        self.nav_list = QListWidget()
        self.nav_list.setObjectName("NavList")
        self.nav_list.setFrameShape(QFrame.NoFrame)
        self.nav_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.nav_list.setVerticalScrollMode(QListWidget.ScrollPerPixel)

        self.page_titles = ["录入", "查询", "看板", "报表", "设置"]
        for title in self.page_titles:
            self.nav_list.addItem(title)

        self.nav_list.setCurrentRow(0)
        self.nav_list.currentRowChanged.connect(self.switch_page)

        nav_layout.addWidget(self.nav_list)
        nav_layout.addStretch()

        main_layout.addWidget(nav_frame)

        content_frame = QFrame()
        content_frame.setObjectName("ContentFrame")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(24, 16, 24, 16)
        content_layout.setSpacing(12)

        header_frame = QFrame()
        header_frame.setObjectName("HeaderFrame")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(16, 10, 16, 10)

        self.header_title = QLabel(self.page_titles[0])
        self.header_title.setObjectName("HeaderTitle")
        header_layout.addWidget(self.header_title)
        header_layout.addStretch()

        content_layout.addWidget(header_frame)

        self.workspace = QStackedWidget()
        self.workspace.setObjectName("Workspace")

        self.entry_page = EntryWidget()
        self.query_page = QueryWidget()
        self.kanban_page = KanbanWidget()
        self.report_page = ReportWidget()
        self.settings_page = SettingsWidget()

        self.workspace.addWidget(self.entry_page)
        self.workspace.addWidget(self.query_page)
        self.workspace.addWidget(self.kanban_page)
        self.workspace.addWidget(self.report_page)
        self.workspace.addWidget(self.settings_page)

        content_layout.addWidget(self.workspace)
        main_layout.addWidget(content_frame)

        self.kanban_page.card_clicked.connect(self.open_detail_dialog)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("就绪")

    def switch_page(self, index):
        if index < 0:
            return
        self.workspace.setCurrentIndex(index)
        self.header_title.setText(self.page_titles[index])
        self.status.showMessage(f"切换至: {self.page_titles[index]}")

    def open_detail_dialog(self, product_id):
        data = self.db.get_product(product_id)
        if data:
            dialog = DetailDialog(data, self)
            dialog.exec_()
        else:
            QMessageBox.warning(self, "错误", "未找到该记录")

    def closeEvent(self, event):
        """窗口关闭事件 - 执行自动备份"""
        if self.backup_manager.config.get('auto_backup', True):
            try:
                self.backup_manager.create_backup()
                self.status.showMessage("数据已自动备份")
            except Exception as exc:
                print(f"自动备份失败: {exc}")
        event.accept()
