# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QListWidget, 
                             QStackedWidget, QLabel, QVBoxLayout, QStatusBar, QMessageBox,
                             QSplitter) # Added QSplitter
from PyQt5.QtCore import Qt, QSize
from ui.entry_widget import EntryWidget
from ui.query_widget import QueryWidget
from ui.report_widget import ReportWidget
from utils.backup import BackupManager
from ui.detail_panel import DetailPanel # Added DetailPanel

class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("技术状态管理助手 - V2.5 Enterprise")
        self.resize(1300, 850) # Increased size slightly
        self.backup_manager = BackupManager()
        self.init_ui()

    def init_ui(self):
        # 1. 主容器
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # 应用全局 Enterprise 风格设计规范 (Design Tokens)
        # 1. 极简调色盘：#1e1e2d (深色轨), #f8f9fa (侧边栏), #ffffff (工作区)
        # 2. 边框规范：#e8e8e8
        # 3. 字体规范：Microsoft YaHei, 13px, #262626
        self.setStyleSheet("""
            QMainWindow { 
                background-color: #ffffff; 
            }
            QWidget {
                font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
                font-size: 13px;
                color: #262626;
                outline: none;
            }
            QStackedWidget {
                background-color: #ffffff;
            }
            
            /* 分割线整体样式 - 加深对比 */
            QSplitter::handle {
                background-color: #dcdfe6;
            }
            QSplitter::handle:horizontal {
                width: 1px;
            }
            
            /* 滚动条极简美化 */
            QScrollBar:vertical {
                border: none;
                background: #f5f7fa;
                width: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #c0c4cc;
                min-height: 20px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical:hover {
                background: #909399;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            QScrollBar:horizontal {
                border: none;
                background: #f5f7fa;
                height: 6px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: #c0c4cc;
                min-width: 20px;
                border-radius: 3px;
            }
            
            /* 移除表格/树形的基础边框 */
            QTreeWidget, QTableWidget {
                border: none;
                background-color: transparent;
            }
        """)

        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 2. 三窗格布局组件
        from ui.global_rail import GlobalRail
        from ui.context_sidebar import ContextSidebar
        from ui.kanban_widget import KanbanWidget
        
        self.global_rail = GlobalRail()
        self.context_sidebar = ContextSidebar()
        
        # 3. 核心工作区 (StackedWidget)
        self.workspace_area = QStackedWidget()
        
        # 现有页面作为"工作台"的一部分
        self.workbench_container = QWidget()
        wb_layout = QHBoxLayout(self.workbench_container)
        wb_layout.setContentsMargins(0, 0, 0, 0)
        
        # 旧的 StackedWidget 放在这里
        self.content_stack = QStackedWidget()
        
        self.entry_page = EntryWidget()
        self.query_page = QueryWidget()
        self.report_page = ReportWidget()
        
        self.kanban_page = KanbanWidget()
        
        # 延迟导入设置页
        from ui.settings_widget import SettingsWidget
        self.settings_page = SettingsWidget()
        
        self.content_stack.addWidget(self.entry_page)
        self.content_stack.addWidget(self.query_page)
        self.content_stack.addWidget(self.report_page)
        self.content_stack.addWidget(self.settings_page)
        
        wb_layout.addWidget(self.content_stack)
        
        # 添加各个主模块视图到 workspace_area
        self.workspace_area.addWidget(self.workbench_container) # Index 0: 工作台
        self.workspace_area.addWidget(self.kanban_page)       # Index 1: 项目看板
        self.workspace_area.addWidget(QLabel("甘特图视图 (开发中)")) # Index 2: 排期
        self.workspace_area.addWidget(QLabel("报表中心 (开发中)")) # Index 3: 报表
        self.workspace_area.addWidget(QLabel("全局设置 (开发中)")) # Index 4: 设置
        
        # --- 右侧详情面板区域 (Splitter) ---
        self.detail_panel = DetailPanel()
        self.detail_panel.hide() # 默认隐藏
        
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.main_splitter.addWidget(self.workspace_area)
        self.main_splitter.addWidget(self.detail_panel)
        self.main_splitter.setStretchFactor(0, 1) # 工作区占满
        self.main_splitter.setStretchFactor(1, 0) # 详情页自适应
        self.main_splitter.setHandleWidth(1)
        self.main_splitter.setStyleSheet("QSplitter::handle { background-color: #e0e0e0; }")
        
        # 4. 组装全局布局
        main_layout.addWidget(self.global_rail)
        main_layout.addWidget(self.context_sidebar)
        main_layout.addWidget(self.main_splitter) # Replace workspace_area with splitter
        
        # 5. 信号连接
        self.global_rail.module_changed.connect(self.switch_major_module)
        self.context_sidebar.item_selected.connect(self.handle_context_selection)
        
        # 看板点击 -> 打开详情
        self.kanban_page.card_clicked.connect(self.open_detail_panel)
        
        # 详情页关闭 -> 隐藏
        self.detail_panel.close_requested.connect(self.detail_panel.hide)
        
        # 6. 状态栏
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("就绪")
        
    def open_detail_panel(self, product_id):
        """打开右侧详情面板"""
        self.detail_panel.load_data(product_id)
        self.detail_panel.show()
        # 确保详情页有一定宽度
        if self.detail_panel.width() < 50:
             # 设置初始比例 (approx 70% / 30%)
             total_width = self.main_splitter.width()
             self.main_splitter.setSizes([int(total_width * 0.7), int(total_width * 0.3)])

    def switch_major_module(self, index):
        """切换一级模块 (Rail)"""
        self.context_sidebar.switch_context(index)
        self.workspace_area.setCurrentIndex(index)
        
        # 切换模块时隐藏详情页，避免混淆
        self.detail_panel.hide()
        
        modules = ["工作台", "项目", "排期", "报表", "设置"]
        self.status.showMessage(f"切换至: {modules[index]}")

    def handle_context_selection(self, context_type, context_id):
        """处理二级导航选择"""
        if context_type == "project":
            # 切换到项目视图 (目前复用查询页 for demo, or keep kanban if appropriate)
            # 根据需求，点击项目节点可能应该进看板？或者进查询列表？
            # 现改为进看板视图并作为过滤条件的演示
            self.status.showMessage(f"打开项目: {context_id}")
            self.workspace_area.setCurrentIndex(1) # 切换到看板
            # TODO: 触发看板过滤 self.kanban_page.filter_by_model(context_id)
            self.detail_panel.hide()
            
        elif context_type == "settings":
            self.workspace_area.setCurrentIndex(0)
            self.content_stack.setCurrentWidget(self.settings_page)
            self.detail_panel.hide()

    def closeEvent(self, event):
        """窗口关闭事件 - 执行自动备份"""
        # 检查是否启用自动备份
        if self.backup_manager.config.get('auto_backup', True):
            try:
                backup_path = self.backup_manager.create_backup()
                self.status.showMessage(f"数据已自动备份")
            except Exception as e:
                # 备份失败不阻止关闭
                print(f"自动备份失败: {e}")
        
        event.accept()
