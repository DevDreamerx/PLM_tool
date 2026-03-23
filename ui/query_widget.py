# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt
from openpyxl import Workbook
import os
from db.database import DatabaseManager
from ui.theme import THEME
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
        self.search_input.setPlaceholderText("支持产品信息与技术状态关键词搜索...")
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
            btn_widget.setStyleSheet("background: transparent;")
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(5, 2, 5, 2)
            
            btn_view = QPushButton("查看")
            btn_view.setFlat(True)
            btn_view.setStyleSheet(
                f"background: transparent; color: {THEME['accent']}; border: none; font-weight: 600;"
            )
            btn_view.setCursor(Qt.PointingHandCursor)
            btn_view.clicked.connect(lambda checked, pid=row_data['id']: self.view_detail(pid))
            
            btn_delete = QPushButton("删除")
            btn_delete.setFlat(True)
            btn_delete.setStyleSheet(
                f"background: transparent; color: {THEME['danger']}; border: none; font-weight: 600;"
            )
            btn_delete.setCursor(Qt.PointingHandCursor)
            btn_delete.clicked.connect(lambda checked, pid=row_data['id']: self.delete_record(pid))

            btn_export = QPushButton("导出")
            btn_export.setFlat(True)
            btn_export.setStyleSheet(
                f"background: transparent; color: {THEME['text']}; border: none; font-weight: 600;"
            )
            btn_export.setCursor(Qt.PointingHandCursor)
            btn_export.clicked.connect(lambda checked, pid=row_data['id']: self.export_record(pid))
            
            btn_layout.addWidget(btn_view)
            btn_layout.addWidget(btn_delete)
            btn_layout.addWidget(btn_export)
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

    def export_record(self, product_id):
        """导出单条记录为模板格式 Excel"""
        product = self.db.get_product(product_id)
        tech_status = self.db.get_tech_status(product_id)
        if not product or not tech_status:
            QMessageBox.warning(self, "导出提示", "未找到完整的产品或技术状态数据")
            return

        default_name = f"{product.get('product_code', 'export')}.xlsx"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存Excel文件", default_name, "Excel Files (*.xlsx)"
        )
        if not file_path:
            return
        if not file_path.endswith(".xlsx"):
            file_path += ".xlsx"

        try:
            wb = Workbook()
            ws = wb.active
            headers = self._export_headers()
            row_values = self._build_export_row(product, tech_status)
            ws.append(headers)
            ws.append([row_values.get(header, "") for header in headers])
            wb.save(file_path)
            QMessageBox.information(self, "导出成功", f"已导出: {file_path}")
        except Exception as exc:
            QMessageBox.critical(self, "导出失败", f"导出Excel失败:\n{exc}")

    def _export_headers(self):
        return [
            "产品型号",
            "所属机型",
            "产品名称",
            "所属阶段",
            "协调单号",
            "更改建议单号",
            "更改理由",
            "更改建议单涉及图样/文件",
            "更改单号/技术通知单号/工艺更改单号",
            "涉及更改图样",
            "更改类别",
            "更改原因",
            "更改人",
            "处理意见",
            "需落实产品编号",
            "已落实情况",
            "未落实产品编号",
            "工艺更改落实情况",
            "备注",
        ]

    def _extract_labeled_value(self, text, label):
        if not text:
            return ""
        for part in str(text).split(";"):
            part = part.strip()
            if part.startswith(f"{label}:"):
                return part[len(label) + 1:].strip()
        return ""

    def _build_export_row(self, product, tech_status):
        change_order = tech_status.get("change_order", "")
        change_desc = tech_status.get("change_description", "")
        values = {
            "产品型号": product.get("product_code", ""),
            "所属机型": product.get("model", ""),
            "产品名称": product.get("product_name", ""),
            "所属阶段": self._extract_labeled_value(change_desc, "所属阶段"),
            "协调单号": self._extract_labeled_value(change_order, "协调单号"),
            "更改建议单号": self._extract_labeled_value(change_order, "更改建议单号"),
            "更改理由": self._extract_labeled_value(change_desc, "更改理由"),
            "更改建议单涉及图样/文件": self._extract_labeled_value(change_desc, "更改建议单涉及图样/文件"),
            "更改单号/技术通知单号/工艺更改单号": self._extract_labeled_value(
                change_order, "更改单号/技术通知单号/工艺更改单号"
            ),
            "涉及更改图样": self._extract_labeled_value(change_desc, "涉及更改图样"),
            "更改类别": self._extract_labeled_value(change_desc, "更改类别"),
            "更改原因": self._extract_labeled_value(change_desc, "更改原因"),
            "更改人": self._extract_labeled_value(change_desc, "更改人"),
            "处理意见": self._extract_labeled_value(change_desc, "处理意见"),
            "需落实产品编号": self._extract_labeled_value(change_desc, "需落实产品编号"),
            "已落实情况": self._extract_labeled_value(change_desc, "已落实情况"),
            "未落实产品编号": self._extract_labeled_value(change_desc, "未落实产品编号"),
            "工艺更改落实情况": self._extract_labeled_value(change_desc, "工艺更改落实情况"),
            "备注": self._extract_labeled_value(change_desc, "备注"),
        }
        if not values["更改单号/技术通知单号/工艺更改单号"] and change_order:
            values["更改单号/技术通知单号/工艺更改单号"] = change_order
        return values
