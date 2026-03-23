# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QFileDialog, QLabel,
                             QFrame)
from PyQt5.QtCore import Qt
from openpyxl import Workbook
from db.database import DatabaseManager
from ui.theme import THEME
from ui.detail_dialog import DetailDialog

class QueryWidget(QWidget):
    """状态查询界面"""
    
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.page_size = 50
        self.current_page = 1
        self.total_records = 0
        self.init_ui()

    def init_ui(self):
        self._apply_styles()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)
        
        search_panel = QFrame()
        search_panel.setObjectName("ToolbarPanel")
        search_layout = QHBoxLayout(search_panel)
        search_layout.setContentsMargins(18, 16, 18, 16)
        search_layout.setSpacing(12)

        tip = QLabel("默认按录入时间倒序展示，支持跨产品基础信息与最新技术状态搜索。")
        tip.setObjectName("HintText")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("支持产品信息与技术状态关键词搜索...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.returnPressed.connect(lambda: self.perform_search(reset_page=True))
        
        self.btn_search = QPushButton("搜索")
        self.btn_search.setObjectName("PrimaryButton")
        self.btn_search.setFixedWidth(100)
        self.btn_search.clicked.connect(lambda: self.perform_search(reset_page=True))

        self.btn_reset = QPushButton("清空")
        self.btn_reset.setObjectName("GhostButton")
        self.btn_reset.setFixedWidth(100)
        self.btn_reset.clicked.connect(self.reset_search)
        
        search_layout.addWidget(tip, 2)
        search_layout.addStretch()
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.btn_search)
        search_layout.addWidget(self.btn_reset)

        layout.addWidget(search_panel)

        self.result_summary = QLabel("共 0 条")
        self.result_summary.setObjectName("SummaryBanner")
        layout.addWidget(self.result_summary)
        
        # 2. 结果表格
        self.table = QTableWidget()
        self.table.setColumnCount(6) # 增加一列操作栏
        self.table.setHorizontalHeaderLabels(["ID", "产品代号", "产品名称", "批次", "录入时间", "操作"])
        
        # 表格样式调整
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents) # ID列
        header.setSectionResizeMode(5, QHeaderView.Fixed) # 操作列
        self.table.setColumnWidth(5, 248)
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(46)
        self.table.setWordWrap(False)
        
        layout.addWidget(self.table)

        self.empty_state = QFrame()
        self.empty_state.setObjectName("SectionCard")
        empty_layout = QVBoxLayout(self.empty_state)
        empty_layout.setContentsMargins(24, 26, 24, 26)
        empty_layout.setSpacing(8)
        empty_title = QLabel("当前没有匹配记录")
        empty_title.setObjectName("EmptyStateTitle")
        empty_hint = QLabel("试试换个关键词，或清空搜索后查看全部可查询记录。")
        empty_hint.setObjectName("HintText")
        empty_hint.setWordWrap(True)
        empty_layout.addWidget(empty_title)
        empty_layout.addWidget(empty_hint)
        layout.addWidget(self.empty_state)

        # 3. 分页栏
        pager_panel = QFrame()
        pager_panel.setObjectName("ToolbarPanel")
        pager_layout = QHBoxLayout(pager_panel)
        pager_layout.setContentsMargins(14, 10, 14, 10)
        self.page_info = QLabel("共 0 条")
        self.page_info.setObjectName("HintText")

        self.btn_prev = QPushButton("上一页")
        self.btn_prev.setFixedWidth(100)
        self.btn_prev.clicked.connect(self.go_prev_page)

        self.btn_next = QPushButton("下一页")
        self.btn_next.setFixedWidth(100)
        self.btn_next.clicked.connect(self.go_next_page)

        pager_layout.addWidget(self.page_info)
        pager_layout.addStretch()
        pager_layout.addWidget(self.btn_prev)
        pager_layout.addWidget(self.btn_next)
        layout.addWidget(pager_panel)
        self.pager_panel = pager_panel
        
        self.setLayout(layout)
        self.perform_search(reset_page=True)

    def _apply_styles(self):
        self.setStyleSheet(
            f"""
            QTableWidget {{
                alternate-background-color: #f8fbfd;
                selection-background-color: {THEME['accent_soft']};
                selection-color: {THEME['text']};
            }}
            QTableWidget::item {{
                padding: 4px 6px;
            }}
            QLabel#EmptyStateTitle {{
                color: {THEME['text']};
                font-size: 16px;
                font-weight: 700;
            }}
            QPushButton#RowActionButton {{
                min-height: 32px;
                padding: 0 12px;
                border-radius: 9px;
                background: #edf4fa;
                border: 1px solid #d6e2ee;
                color: {THEME['accent']};
                font-weight: 600;
            }}
            QPushButton#RowActionButton:hover {{
                background: #e2edf8;
                border-color: #c5d7e8;
            }}
            QPushButton#RowDangerAction {{
                min-height: 32px;
                padding: 0 12px;
                border-radius: 9px;
                background: #fff1f2;
                border: 1px solid #fecdd3;
                color: {THEME['danger']};
                font-weight: 600;
            }}
            QPushButton#RowDangerAction:hover {{
                background: #ffe4e6;
                border-color: #fda4af;
            }}
            """
        )

    def perform_search(self, reset_page=False):
        """执行搜索"""
        if reset_page:
            self.current_page = 1

        keyword = self.search_input.text().strip()
        try:
            result = self.db.search_products_paginated(
                keyword=keyword,
                page=self.current_page,
                page_size=self.page_size,
            )
            if not result['items'] and result['total'] > 0 and self.current_page > 1:
                self.current_page -= 1
                result = self.db.search_products_paginated(
                    keyword=keyword,
                    page=self.current_page,
                    page_size=self.page_size,
                )
            self.total_records = result['total']
            self.load_table_data(result['items'])
            self.update_pagination_state()
            self.update_result_summary(keyword)
        except Exception as e:
            QMessageBox.critical(self, "查询错误", str(e))

    def refresh_after_update(self):
        """数据更新后刷新当前列表"""
        self.perform_search(reset_page=False)

    def reset_search(self):
        self.search_input.clear()
        self.perform_search(reset_page=True)

    def load_table_data(self, data):
        """加载数据到表格"""
        self.table.setRowCount(len(data))
        self.empty_state.setVisible(len(data) == 0)
        self.table.setVisible(len(data) > 0)
        self.pager_panel.setVisible(self.total_records > 0)
        for row_idx, row_data in enumerate(data):
            self.table.setRowHeight(row_idx, 54)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(row_data['id'])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(row_data['product_code']))
            self.table.setItem(row_idx, 2, QTableWidgetItem(row_data['product_name']))
            self.table.setItem(row_idx, 3, QTableWidgetItem(row_data['batch_number']))
            self.table.setItem(row_idx, 4, QTableWidgetItem(str(row_data['created_at'])))
            
            # 添加操作按钮
            btn_widget = QWidget()
            btn_widget.setStyleSheet("background: transparent;")
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(10, 8, 10, 8)
            btn_layout.setSpacing(8)
            btn_layout.setAlignment(Qt.AlignCenter)
            
            btn_view = QPushButton("查看")
            btn_view.setObjectName("RowActionButton")
            btn_view.setMinimumWidth(64)
            btn_view.setCursor(Qt.PointingHandCursor)
            btn_view.clicked.connect(lambda checked, pid=row_data['id']: self.view_detail(pid))
            
            btn_delete = QPushButton("删除")
            btn_delete.setObjectName("RowDangerAction")
            btn_delete.setMinimumWidth(64)
            btn_delete.setCursor(Qt.PointingHandCursor)
            btn_delete.clicked.connect(lambda checked, pid=row_data['id']: self.delete_record(pid))

            btn_export = QPushButton("导出")
            btn_export.setObjectName("RowActionButton")
            btn_export.setMinimumWidth(64)
            btn_export.setCursor(Qt.PointingHandCursor)
            btn_export.clicked.connect(lambda checked, pid=row_data['id']: self.export_record(pid))
            
            btn_layout.addWidget(btn_view)
            btn_layout.addWidget(btn_delete)
            btn_layout.addWidget(btn_export)
            self.table.setCellWidget(row_idx, 5, btn_widget)

    def update_pagination_state(self):
        total_pages = max(1, (self.total_records + self.page_size - 1) // self.page_size)
        if self.current_page > total_pages:
            self.current_page = total_pages

        start_index = 0 if self.total_records == 0 else (self.current_page - 1) * self.page_size + 1
        end_index = min(self.current_page * self.page_size, self.total_records)
        self.page_info.setText(
            f"第 {self.current_page}/{total_pages} 页，显示 {start_index}-{end_index} 条，共 {self.total_records} 条"
        )
        self.btn_prev.setEnabled(self.current_page > 1)
        self.btn_next.setEnabled(self.current_page < total_pages)

    def update_result_summary(self, keyword):
        if keyword:
            if self.total_records:
                self.result_summary.setText(f"关键词“{keyword}”命中 {self.total_records} 条记录")
            else:
                self.result_summary.setText(f"关键词“{keyword}”没有命中记录")
        else:
            if self.total_records:
                self.result_summary.setText(f"当前共有 {self.total_records} 条可查询记录")
            else:
                self.result_summary.setText("当前没有可查询记录")

    def go_prev_page(self):
        if self.current_page <= 1:
            return
        self.current_page -= 1
        self.perform_search(reset_page=False)

    def go_next_page(self):
        total_pages = max(1, (self.total_records + self.page_size - 1) // self.page_size)
        if self.current_page >= total_pages:
            return
        self.current_page += 1
        self.perform_search(reset_page=False)

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
