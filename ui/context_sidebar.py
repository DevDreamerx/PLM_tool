# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTreeWidget, QTreeWidgetItem, 
                             QStackedWidget, QLineEdit, QHBoxLayout, QPushButton)
from PyQt5.QtCore import Qt, pyqtSignal
from db.database import DatabaseManager

class ContextSidebar(QWidget):
    """二级导航栏 (上下文侧边栏)"""
    
    # ... (existing signals and init) ...
    item_selected = pyqtSignal(str, str) # type, id

    def __init__(self):
        super().__init__()
        self.db = DatabaseManager() # Add DB Manager
        # ... (rest of style setup)
        self.setFixedWidth(240)
        self.setObjectName("ContextSidebar")
        self.setStyleSheet("""
            #ContextSidebar { 
                background-color: #e5eaf2; 
                border-right: 1px solid #c0c8d4; 
            }
            QLabel#TitleLabel { 
                font-weight: bold; color: #1f2430; font-size: 15px; padding: 15px; 
                background-color: transparent;
            }
            QLineEdit { 
                background-color: #f8fafc; border: 1px solid #c0c8d4; 
                border-radius: 4px; padding: 6px; margin: 0 15px 15px 15px;
                color: #1f2430;
            }
            QLineEdit:focus { border-color: #3370ff; }
            
            QTreeWidget { 
                border: none; background-color: transparent; 
                outline: none; font-size: 13px;
                color: #2b2f36;
            }
            QTreeWidget::item { 
                height: 38px; padding-left: 10px; border-radius: 6px; margin: 2px 8px; 
            }
            QTreeWidget::item:hover { background-color: #d7dee9; }
            QTreeWidget::item:selected { 
                background-color: #2b6cb0; 
                color: #ffffff; 
                font-weight: bold;
            }
        """)
        self.init_ui()
        
    def init_ui(self):
        # ... (UI setup same as before until init_dummy_data)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 顶部标题栏
        self.header_area = QWidget()
        self.header_area.setFixedHeight(60)
        header_layout = QHBoxLayout(self.header_area)
        header_layout.setContentsMargins(15, 0, 15, 0)
        
        self.title_label = QLabel("全部项目")
        self.title_label.setObjectName("TitleLabel")
        self.title_label.setStyleSheet("border: none; background: transparent;")
        
        btn_add = QPushButton("+")
        btn_add.setFixedSize(24, 24)
        btn_add.setStyleSheet("""
            QPushButton { border-radius: 4px; border: 1px solid #c7ced9; background: white; color: #4b5563; }
            QPushButton:hover { border-color: #3370ff; color: #3370ff; }
        """)
        
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(btn_add)
        
        layout.addWidget(self.header_area)
        
        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索...")
        layout.addWidget(self.search_input)
        
        # 内容区域 (堆叠)
        self.stack = QStackedWidget()
        
        # 1. 项目树
        self.project_tree = QTreeWidget()
        self.project_tree.setHeaderHidden(True)
        self.stack.addWidget(self.project_tree)
        
        # 2. 报表列表
        self.report_list = QTreeWidget()
        self.report_list.setHeaderHidden(True)
        self.stack.addWidget(self.report_list)
        
        # 3. 设置列表
        self.settings_list = QTreeWidget()
        self.settings_list.setHeaderHidden(True)
        root = QTreeWidgetItem(self.settings_list)
        root.setText(0, "全局设置")
        child1 = QTreeWidgetItem(root)
        child1.setText(0, "备份管理")
        child2 = QTreeWidgetItem(root)
        child2.setText(0, "账户信息")
        self.settings_list.expandAll()
        self.settings_list.itemClicked.connect(lambda item, col: self.item_selected.emit("settings", item.text(0)))
        self.stack.addWidget(self.settings_list)

        layout.addWidget(self.stack)
        
        # 加载真实数据
        self.load_projects()
        
        # 连接事件
        self.project_tree.itemClicked.connect(self.on_project_clicked)

    def load_projects(self):
        """加载项目（型号）列表"""
        self.project_tree.clear()
        
        # 获取所有型号分布
        dist = self.db.get_model_distribution()
        
        root = QTreeWidgetItem(self.project_tree)
        root.setText(0, "📦 全部产品型号")
        root.setExpanded(True)
        
        for model, count in dist:
            item = QTreeWidgetItem(root)
            item.setText(0, f"{model} ({count})")
            item.setData(0, Qt.UserRole, model) # Store model name
    
    def on_project_clicked(self, item, column):
        proj_id = item.data(0, Qt.UserRole)
        if proj_id:
            self.item_selected.emit("project", proj_id)
        else:
            # 这是一个组
            if item.isExpanded():
                item.setExpanded(False)
            else:
                item.setExpanded(True)

    def switch_context(self, index):
        """切换上下文视图"""
        if index == 1: # 项目
            self.title_label.setText("全部项目")
            self.stack.setCurrentWidget(self.project_tree)
        elif index == 3: # 报表
            self.title_label.setText("统计报表")
            self.stack.setCurrentWidget(self.report_list)
        elif index == 4: # 设置
            self.title_label.setText("系统设置")
            self.stack.setCurrentWidget(self.settings_list)
        else:
            self.title_label.setText("工作台")
