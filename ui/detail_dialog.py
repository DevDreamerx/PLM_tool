# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLabel, 
                             QPushButton, QHBoxLayout, QScrollArea, QWidget, 
                             QGroupBox, QTabWidget, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QFileDialog, QInputDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from db.database import DatabaseManager
import os
import json
from ui.theme import THEME

class DetailDialog(QDialog):
    """产品详情弹窗 (V2.0 - CM2增强版)"""
    
    def __init__(self, product_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"产品详情 - {product_data.get('product_code', '未知')}")
        self.resize(900, 700)
        self.product_data = product_data
        self.db = DatabaseManager()
        
        # 重新获取最新数据以确保 lifecycle_state 是最新的
        self.refresh_product_data()
        self.init_ui()

    def refresh_product_data(self):
        """刷新产品数据"""
        updated_data = self.db.get_product(self.product_data['id'])
        if updated_data:
            self.product_data = updated_data

    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # --- 顶部头部区域 ---
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        
        # 产品标识
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(16)
        
        title_label = QLabel(f"{self.product_data.get('product_code')} {self.product_data.get('product_name')}")
        title_label.setFont(title_font)
        
        # 生命周期状态徽章
        state = self.product_data.get('lifecycle_state', 'draft')
        badge_color = THEME["warning"]
        state_text = "草稿"
        
        if state == 'released':
            badge_color = THEME["success"]
            state_text = "已发布"
        elif state == 'obsolete':
            badge_color = THEME["danger"]
            state_text = "已废弃"
        elif state == 'review':
            badge_color = THEME["accent"]
            state_text = "审核中"
            
        state_badge = QLabel(state_text)
        state_badge.setStyleSheet(f"""
            QLabel {{
                background-color: {badge_color};
                color: white;
                border-radius: 4px;
                padding: 4px 12px;
                font-weight: bold;
            }}
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(state_badge)
        
        main_layout.addWidget(header_widget)
        
        # --- 中间 Tab 区域 ---
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_general_tab(), "常规信息")
        self.tabs.addTab(self.create_baselines_tab(), "基线管理")
        self.tabs.addTab(self.create_attachments_tab(), "附件文档")
        self.tabs.addTab(self.create_history_tab(), "变更历史")
        
        main_layout.addWidget(self.tabs)
        
        # --- 底部按钮区域 ---
        footer_layout = QHBoxLayout()
        
        # 生命周期操作按钮
        if state == 'draft':
            btn_submit = QPushButton("提交审核")
            btn_submit.clicked.connect(lambda: self.change_lifecycle('review'))
            footer_layout.addWidget(btn_submit)
        elif state == 'review':
            btn_approve = QPushButton("批准发布")
            btn_approve.setObjectName("SuccessButton")
            btn_approve.clicked.connect(lambda: self.change_lifecycle('released'))
            btn_reject = QPushButton("驳回")
            btn_reject.setObjectName("DangerButton")
            btn_reject.clicked.connect(lambda: self.change_lifecycle('draft'))
            footer_layout.addWidget(btn_approve)
            footer_layout.addWidget(btn_reject)
        elif state == 'released':
            btn_obsolete = QPushButton("废弃")
            btn_obsolete.clicked.connect(lambda: self.change_lifecycle('obsolete'))
            footer_layout.addWidget(btn_obsolete)
        
        footer_layout.addStretch()
        
        self.btn_close = QPushButton("关闭")
        self.btn_close.setFixedSize(100, 35)
        self.btn_close.setObjectName("GhostButton")
        self.btn_close.clicked.connect(self.accept)
        footer_layout.addWidget(self.btn_close)
        
        main_layout.addLayout(footer_layout)
        self.setLayout(main_layout)

    def create_general_tab(self):
        """创建常规信息页"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        scroll.setWidget(content_widget)
        
        layout = QVBoxLayout(content_widget)
        
        # 1. 产品基本信息
        product_group = QGroupBox("产品基本信息")
        product_form = QFormLayout()
        
        fields = [("ID", "id"), ("产品代号", "product_code"), ("产品名称", "product_name"), 
                  ("批次编号", "batch_number"), ("所属型号", "model")]
        for label, key in fields:
            product_form.addRow(f"<b>{label}:</b>", QLabel(str(self.product_data.get(key, ""))))
            
        product_group.setLayout(product_form)
        layout.addWidget(product_group)
        
        # 2. 技术状态信息
        tech_status = self.db.get_tech_status(self.product_data['id'])
        if tech_status:
            tech_group = QGroupBox("技术状态信息")
            tech_form = QFormLayout()
            tech_fields = [
                ("图号", "drawing_number"), ("图纸版本", "drawing_version"),
                ("软件版本/构建", "software_version"), ("固件版本/构建", "firmware_version"),
                ("硬件配置", "hardware_config"), ("需求基线", "req_baseline"),
                ("接口基线", "icd_version"), ("BOM版本", "bom_version"),
                ("PCB版本", "pcb_version"), ("硬件序列号", "hw_serial"),
                ("生产批次", "production_batch"), ("测试状态", "test_status"),
                ("合格状态", "qual_status"), ("生效日期", "effective_date")
            ]
            for label, key in tech_fields:
                tech_form.addRow(f"<b>{label}:</b>", QLabel(str(tech_status.get(key, "—"))))
            tech_group.setLayout(tech_form)
            layout.addWidget(tech_group)
            
        return scroll

    def create_baselines_tab(self):
        """创建基线管理页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 工具栏
        toolbar = QHBoxLayout()
        btn_create = QPushButton("创建基线快照")
        btn_create.clicked.connect(self.create_baseline)
        toolbar.addWidget(btn_create)
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # 表格
        self.baseline_table = QTableWidget()
        self.baseline_table.setColumnCount(4)
        self.baseline_table.setHorizontalHeaderLabels(["基线名称", "类型", "创建人", "创建时间"])
        self.baseline_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.baseline_table)
        
        self.load_baselines()
        
        return widget

    def create_attachments_tab(self):
        """创建附件文档页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 工具栏
        toolbar = QHBoxLayout()
        btn_add = QPushButton("添加附件")
        btn_add.clicked.connect(self.add_attachment)
        toolbar.addWidget(btn_add)
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # 表格
        self.attach_table = QTableWidget()
        self.attach_table.setColumnCount(4)
        self.attach_table.setHorizontalHeaderLabels(["文件名", "描述", "上传时间", "操作"])
        self.attach_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        layout.addWidget(self.attach_table)
        
        self.load_attachments()
        
        return widget

    def create_history_tab(self):
        """创建历史记录页"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        scroll.setWidget(content_widget)
        layout = QVBoxLayout(content_widget)
        
        change_history = self.db.get_change_history(self.product_data['id'])
        if change_history:
            for change in change_history:
                change_item = QLabel()
                type_badge = {
                    'create': (
                        f"<span style=\"background:{THEME['success']};color:white;"
                        "padding:2px 8px;border-radius:3px;\">创建</span>"
                    ),
                    'update': (
                        f"<span style=\"background:{THEME['accent']};color:white;"
                        "padding:2px 8px;border-radius:3px;\">更新</span>"
                    ),
                    'lifecycle': (
                        f"<span style=\"background:{THEME['warning']};color:#3a2c16;"
                        "padding:2px 8px;border-radius:3px;\">状态</span>"
                    ),
                }.get(change['change_type'], change['change_type'])
                
                change_item.setText(f"""
                    <div style="border-left: 3px solid {THEME['border']}; padding-left: 10px; margin-bottom: 10px;">
                        <div>{type_badge} <b>{change['created_at']}</b></div>
                        <div style="color:{THEME['text']};margin-top:5px;">{change['change_content']}</div>
                        <div style="color:{THEME['text_muted']};font-size:12px;">操作人: {change['operator']}</div>
                    </div>
                """)
                change_item.setTextFormat(Qt.RichText)
                layout.addWidget(change_item)
        
        layout.addStretch()
        return scroll

    # --- 逻辑处理 ---

    def change_lifecycle(self, new_state):
        """更改生命周期状态"""
        reply = QMessageBox.question(self, "确认操作", f"确定要将状态更改为 {new_state} 吗？")
        if reply == QMessageBox.Yes:
            self.db.update_lifecycle_state(self.product_data['id'], new_state)
            
            # 记录变更日志
            tech_status = self.db.get_tech_status(self.product_data['id'])
            if tech_status:
                self.db.insert_change_log(tech_status['id'], "lifecycle", f"状态更新为: {new_state}")
            
            QMessageBox.information(self, "成功", "状态已更新！")
            self.close() # 关闭以刷新父窗口

    def create_baseline(self):
        """创建基线"""
        name, ok = QInputDialog.getText(self, "创建基线", "请输入基线名称 (如: 功能基线 V1.0):")
        if ok and name:
            # 获取完整数据快照
            snapshot = {
                'product': self.product_data,
                'tech_status': self.db.get_tech_status(self.product_data['id'])
            }
            snapshot_json = json.dumps(snapshot, ensure_ascii=False)
            
            self.db.create_baseline(self.product_data['id'], name, "Manual", snapshot_json)
            self.load_baselines()
            QMessageBox.information(self, "成功", "基线快照已创建！")

    def load_baselines(self):
        """加载基线列表"""
        baselines = self.db.get_baselines(self.product_data['id'])
        self.baseline_table.setRowCount(len(baselines))
        for i, b in enumerate(baselines):
            self.baseline_table.setItem(i, 0, QTableWidgetItem(b['baseline_name']))
            self.baseline_table.setItem(i, 1, QTableWidgetItem(b['baseline_type']))
            self.baseline_table.setItem(i, 2, QTableWidgetItem(b['created_by']))
            self.baseline_table.setItem(i, 3, QTableWidgetItem(b['created_at']))

    def add_attachment(self):
        """添加附件"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择文件")
        if file_path:
            file_name = os.path.basename(file_path)
            # 简化操作：仅保存路径，实际项目应复制文件
            self.db.add_attachment('product', self.product_data['id'], file_name, file_path)
            self.load_attachments()

    def load_attachments(self):
        """加载附件列表"""
        attachments = self.db.get_attachments('product', self.product_data['id'])
        self.attach_table.setRowCount(len(attachments))
        for i, att in enumerate(attachments):
            self.attach_table.setItem(i, 0, QTableWidgetItem(att['file_name']))
            self.attach_table.setItem(i, 1, QTableWidgetItem(att['description']))
            self.attach_table.setItem(i, 2, QTableWidgetItem(att['uploaded_at']))
            
            btn_open = QPushButton("打开")
            btn_open.clicked.connect(lambda ch, p=att['file_path']: self.open_file(p))
            self.attach_table.setCellWidget(i, 3, btn_open)

    def open_file(self, path):
        """打开文件"""
        import subprocess, sys, platform
        if platform.system() == 'Darwin':       # macOS
            subprocess.call(('open', path))
        elif platform.system() == 'Windows':    # Windows
            os.startfile(path)
        else:                                   # linux variants
            subprocess.call(('xdg-open', path))
