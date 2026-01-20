# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QMessageBox)
from db.database import DatabaseManager
from ui.detail_dialog import DetailDialog

class QueryWidget(QWidget):
    """状态查询界面"""
    
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # 1. 搜索栏
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("请输入产品代号或名称...")
        self.search_input.returnPressed.connect(self.perform_search)
        
        self.btn_search = QPushButton("搜索")
        self.btn_search.setFixedWidth(100)
        self.btn_search.clicked.connect(self.perform_search)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.btn_search)
        
        layout.addLayout(search_layout)
        
        # 2. 结果表格
        self.table = QTableWidget()
        self.table.setColumnCount(6) # 增加一列操作栏
        self.table.setHorizontalHeaderLabels(["ID", "产品代号", "产品名称", "批次", "录入时间", "操作"])
        
        # 表格样式调整
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents) # ID列
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents) # 操作列
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)

    def perform_search(self):
        """执行搜索"""
        keyword = self.search_input.text().strip()
        try:
            results = self.db.search_products(keyword)
            self.load_table_data(results)
        except Exception as e:
            QMessageBox.critical(self, "查询错误", str(e))

    def load_table_data(self, data):
        """加载数据到表格"""
        self.table.setRowCount(len(data))
        for row_idx, row_data in enumerate(data):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(row_data['id'])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(row_data['product_code']))
            self.table.setItem(row_idx, 2, QTableWidgetItem(row_data['product_name']))
            self.table.setItem(row_idx, 3, QTableWidgetItem(row_data['batch_number']))
            self.table.setItem(row_idx, 4, QTableWidgetItem(str(row_data['created_at'])))
            
            # 添加操作按钮
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(5, 2, 5, 2)
            
            btn_view = QPushButton("查看")
            btn_view.setStyleSheet("color: blue; border: none;")
            btn_view.setCursor(Qt.PointingHandCursor)
            btn_view.clicked.connect(lambda checked, pid=row_data['id']: self.view_detail(pid))
            
            btn_delete = QPushButton("删除")
            btn_delete.setStyleSheet("color: red; border: none;")
            btn_delete.setCursor(Qt.PointingHandCursor)
            btn_delete.clicked.connect(lambda checked, pid=row_data['id']: self.delete_record(pid))
            
            btn_layout.addWidget(btn_view)
            btn_layout.addWidget(btn_delete)
            self.table.setCellWidget(row_idx, 5, btn_widget)

    def view_detail(self, product_id):
        """查看详情"""
        data = self.db.get_product(product_id)
        if data:
            dialog = DetailDialog(data, self)
            dialog.exec_()
        else:
            QMessageBox.warning(self, "错误", "未找到该记录")

    def delete_record(self, product_id):
        """删除记录"""
        reply = QMessageBox.question(self, '确认删除', 
                                   '确定要删除这条记录吗？\n此操作不可恢复。',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                self.db.delete_product(product_id)
                QMessageBox.information(self, "成功", "记录已删除")
                self.perform_search() # 刷新列表
            except Exception as e:
                QMessageBox.critical(self, "删除失败", str(e))

from PyQt5.QtCore import Qt
