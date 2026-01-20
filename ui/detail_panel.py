# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QScrollArea, QTabWidget, QFormLayout, 
                             QGroupBox, QTableWidget, QTableWidgetItem, QMessageBox,
                             QHeaderView, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from db.database import DatabaseManager

class DetailPanel(QWidget):
    """右侧详情面板 (替代原有的弹窗)"""
    
    # 信号: 请求关闭面板
    close_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.product_data = None
        self.setFixedWidth(400)
        self.setStyleSheet("""
            DetailPanel {
                background-color: #ffffff;
                border-left: 1px solid #dcdfe6;
            }
            QGroupBox {
                border: none;
                border-top: 1px solid #e4e7ed;
                margin-top: 20px;
                padding-top: 15px;
                font-weight: bold;
                color: #1a1a1a;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 0px;
                padding: 0px;
                font-size: 14px;
            }
            QLabel#ValueLabel {
                color: #262626;
                font-size: 13px;
            }
            QLabel#PropLabel {
                color: #595959;
                font-size: 13px;
            }
        """)
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 1. 顶部工具栏
        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet("border-bottom: 1px solid #dcdfe6; background-color: #ffffff;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 15, 0)
        
        self.title_label = QLabel("任务详情")
        self.title_label.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        self.title_label.setStyleSheet("border: none; color: #1a1a1a;")
        
        btn_close = QPushButton("×")
        btn_close.setFixedSize(32, 32)
        btn_close.setStyleSheet("""
            QPushButton { border: none; font-size: 24px; color: #bfbfbf; background: transparent; }
            QPushButton:hover { color: #595959; background: #f5f5f5; border-radius: 16px; }
        """)
        btn_close.clicked.connect(self.close_requested.emit)
        
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(btn_close)
        
        main_layout.addWidget(header)
        
        # 2. 内容区域 (滚动)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("background-color: #ffffff;")
        
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background-color: #ffffff;")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(25, 10, 25, 25)
        self.content_layout.setSpacing(0)
        
        # 占位符
        self.msg_placeholder = QLabel("请选择一个卡片查看详情")
        self.msg_placeholder.setAlignment(Qt.AlignCenter)
        self.msg_placeholder.setStyleSheet("color: #bfbfbf; margin-top: 80px; font-size: 14px;")
        self.content_layout.addWidget(self.msg_placeholder)
        
        # 动态内容容器
        self.dynamic_container = QWidget()
        self.dynamic_layout = QVBoxLayout(self.dynamic_container)
        self.dynamic_layout.setContentsMargins(0, 0, 0, 0)
        self.dynamic_layout.setSpacing(0)
        self.content_layout.addWidget(self.dynamic_container)
        self.dynamic_container.hide()
        
        self.scroll.setWidget(self.content_widget)
        main_layout.addWidget(self.scroll)

    def load_data(self, product_id):
        """加载数据并刷新界面"""
        self.product_data = self.db.get_product(product_id)
        if not self.product_data:
            return

        self.clear_dynamic_content()
        self.msg_placeholder.hide()
        self.dynamic_container.show()
        
        self.title_label.setText(f"{self.product_data['product_code']}")
        
        # 1. 顶部状态栏
        status_bar = QWidget()
        status_bar.setFixedHeight(50)
        status_l = QHBoxLayout(status_bar)
        status_l.setContentsMargins(0, 10, 0, 10)
        
        state = self.product_data.get('lifecycle_state', 'draft')
        state_map = {
            'draft': ('待办', '#8c8c8c', '#f5f5f5'),
            'review': ('审核', '#fa8c16', '#fff7e6'),
            'released': ('已发布', '#52c41a', '#f6ffed'),
            'obsolete': ('已废弃', '#f5222d', '#fff1f0')
        }
        text, color, bg = state_map.get(state, (state, '#3370ff', '#e8f0ff'))
        
        badge = QLabel(text)
        badge.setStyleSheet(f"""
            background-color: {bg}; color: {color}; 
            padding: 4px 12px; border-radius: 12px; font-weight: bold; font-size: 11px;
        """)
        status_l.addWidget(badge)
        status_l.addStretch()
        self.dynamic_layout.addWidget(status_bar)
        
        # 2. 基本信息
        info_group = QGroupBox("基本资料")
        info_form = QFormLayout()
        info_form.setVerticalSpacing(12)
        info_form.setLabelAlignment(Qt.AlignLeft)
        
        fields = [
            ("项目名称", self.product_data.get("product_name", "")),
            ("所属型号", self.product_data.get("model", "")),
            ("生产批次", self.product_data.get("batch_number", ""))
        ]
        for label, val in fields:
            lbl_prop = QLabel(f"{label}")
            lbl_prop.setObjectName("PropLabel")
            lbl_val = QLabel(str(val))
            lbl_val.setObjectName("ValueLabel")
            lbl_val.setWordWrap(True)
            info_form.addRow(lbl_prop, lbl_val)
        
        info_group.setLayout(info_form)
        self.dynamic_layout.addWidget(info_group)
        
        # 3. 技术参数
        tech_status = self.db.get_tech_status(product_id)
        if tech_status:
            tech_group = QGroupBox("技术参数")
            tech_form = QFormLayout()
            tech_form.setVerticalSpacing(12)
            t_fields = [
                ("图纸编号", tech_status.get("drawing_number", "")),
                ("当前版本", tech_status.get("drawing_version", "")),
                ("固件版本", tech_status.get("firmware_version", "-")),
                ("软件版本", tech_status.get("software_version", "-"))
            ]
            for label, val in t_fields:
                lbl_p = QLabel(label)
                lbl_p.setObjectName("PropLabel")
                lbl_v = QLabel(str(val))
                lbl_v.setObjectName("ValueLabel")
                tech_form.addRow(lbl_p, lbl_v)
            tech_group.setLayout(tech_form)
            self.dynamic_layout.addWidget(tech_group)
            
        # 4. 动态时光轴
        history_group = QGroupBox("最近活动")
        hist_layout = QVBoxLayout()
        hist_layout.setContentsMargins(0, 5, 0, 0)
        hist_layout.setSpacing(15)
        
        history = self.db.get_change_history(product_id)
        if history:
            for item in history[:5]:
                h_container = QWidget()
                h_l = QVBoxLayout(h_container)
                h_l.setContentsMargins(0, 0, 0, 0)
                h_l.setSpacing(4)
                
                h_time = QLabel(item['created_at'])
                h_time.setStyleSheet("color: #bfbfbf; font-size: 11px;")
                h_content = QLabel(item['change_content'])
                h_content.setWordWrap(True)
                h_content.setStyleSheet("color: #595959; font-size: 12px;")
                
                h_l.addWidget(h_time)
                h_l.addWidget(h_content)
                hist_layout.addWidget(h_container)
        else:
            hist_layout.addWidget(QLabel("暂无最近活动", styleSheet="color:#bfbfbf; font-size: 12px;"))
        
        history_group.setLayout(hist_layout)
        self.dynamic_layout.addWidget(history_group)
            
        self.dynamic_layout.addStretch()
            
        self.dynamic_layout.addStretch()

    def clear_dynamic_content(self):
        """清理动态区域"""
        while self.dynamic_layout.count():
            item = self.dynamic_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout_item(item)
                
    def clear_layout_item(self, layout_item):
        if layout_item.layout():
            while layout_item.layout().count():
                child = layout_item.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
                elif child.layout():
                    self.clear_layout_item(child)
