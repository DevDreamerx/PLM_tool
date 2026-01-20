# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QTextEdit, 
                             QComboBox, QDateEdit, QPushButton, 
                             QGridLayout, QHBoxLayout, QMessageBox, QGroupBox, QVBoxLayout)
from PyQt5.QtCore import QDate, Qt
from db.database import DatabaseManager

class EntryWidget(QWidget):
    """状态录入界面"""
    
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # 标题
        title = QLabel("技术状态录入")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(title)
        
        # 1. 产品基本信息组
        product_group = QGroupBox("产品基本信息")
        product_layout = QGridLayout()
        
        self.product_code = QLineEdit()
        self.product_code.setPlaceholderText("必填 *")
        
        self.product_name = QLineEdit()
        self.product_name.setPlaceholderText("必填 *")
        
        self.batch_number = QLineEdit()
        self.batch_number.setPlaceholderText("必填 *")
        
        self.model = QComboBox()
        self.model.addItems(["型号A", "型号B", "型号C", "其他"])
        
        product_layout.addWidget(QLabel("产品代号:"), 0, 0)
        product_layout.addWidget(self.product_code, 0, 1)
        product_layout.addWidget(QLabel("产品名称:"), 0, 2)
        product_layout.addWidget(self.product_name, 0, 3)
        product_layout.addWidget(QLabel("批次编号:"), 1, 0)
        product_layout.addWidget(self.batch_number, 1, 1)
        product_layout.addWidget(QLabel("所属型号:"), 1, 2)
        product_layout.addWidget(self.model, 1, 3)
        
        product_group.setLayout(product_layout)
        main_layout.addWidget(product_group)
        
        # 2. 技术状态信息组
        tech_group = QGroupBox("技术状态信息")
        tech_layout = QGridLayout()
        
        self.drawing_number = QLineEdit()
        self.drawing_number.setPlaceholderText("必填 *")
        
        self.drawing_version = QLineEdit()
        self.drawing_version.setPlaceholderText("必填 *")
        
        self.software_version = QLineEdit()
        self.software_version.setPlaceholderText("选填")
        
        self.firmware_version = QLineEdit()
        self.firmware_version.setPlaceholderText("选填")
        
        self.hardware_config = QTextEdit()
        self.hardware_config.setPlaceholderText("硬件配置说明 (选填)")
        self.hardware_config.setMaximumHeight(80)
        
        tech_layout.addWidget(QLabel("图号:"), 0, 0)
        tech_layout.addWidget(self.drawing_number, 0, 1)
        tech_layout.addWidget(QLabel("图纸版本:"), 0, 2)
        tech_layout.addWidget(self.drawing_version, 0, 3)
        tech_layout.addWidget(QLabel("软件版本:"), 1, 0)
        tech_layout.addWidget(self.software_version, 1, 1)
        tech_layout.addWidget(QLabel("固件版本:"), 1, 2)
        tech_layout.addWidget(self.firmware_version, 1, 3)
        tech_layout.addWidget(QLabel("硬件配置:"), 2, 0)
        tech_layout.addWidget(self.hardware_config, 2, 1, 1, 3)
        
        tech_group.setLayout(tech_layout)
        main_layout.addWidget(tech_group)
        
        # 3. 变更信息组
        change_group = QGroupBox("变更信息")
        change_layout = QGridLayout()
        
        self.change_order = QLineEdit()
        self.change_order.setPlaceholderText("选填")
        
        self.change_description = QTextEdit()
        self.change_description.setPlaceholderText("变更内容摘要 (选填)")
        self.change_description.setMaximumHeight(60)
        
        self.effective_date = QDateEdit()
        self.effective_date.setCalendarPopup(True)
        self.effective_date.setDate(QDate.currentDate())
        
        change_layout.addWidget(QLabel("更改单号:"), 0, 0)
        change_layout.addWidget(self.change_order, 0, 1)
        change_layout.addWidget(QLabel("生效日期:"), 0, 2)
        change_layout.addWidget(self.effective_date, 0, 3)
        change_layout.addWidget(QLabel("更改内容:"), 1, 0)
        change_layout.addWidget(self.change_description, 1, 1, 1, 3)
        
        change_group.setLayout(change_layout)
        main_layout.addWidget(change_group)
        
        # 4. 按钮组
        btn_layout = QHBoxLayout()
        
        self.btn_draft = QPushButton("暂存草稿")
        self.btn_draft.setFixedSize(120, 40)
        self.btn_draft.setStyleSheet("background-color: #FAAD14; color: white; font-weight: bold; border-radius: 4px;")
        self.btn_draft.clicked.connect(self.save_draft)
        
        self.btn_submit = QPushButton("正式提交")
        self.btn_submit.setFixedSize(120, 40)
        self.btn_submit.setStyleSheet("background-color: #1890FF; color: white; font-weight: bold; border-radius: 4px;")
        self.btn_submit.clicked.connect(self.submit_form)
        
        self.btn_clear = QPushButton("清空")
        self.btn_clear.setFixedSize(80, 40)
        self.btn_clear.clicked.connect(self.clear_form)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_clear)
        btn_layout.addWidget(self.btn_draft)
        btn_layout.addWidget(self.btn_submit)
        
        main_layout.addLayout(btn_layout)
        main_layout.addStretch()
        
        self.setLayout(main_layout)

    def save_draft(self):
        """暂存草稿"""
        self._save_data(status='draft')

    def submit_form(self):
        """正式提交"""
        self._save_data(status='active')

    def _save_data(self, status='active'):
        """保存数据"""
        # 1. 收集产品数据
        product_data = {
            "product_code": self.product_code.text().strip(),
            "product_name": self.product_name.text().strip(),
            "batch_number": self.batch_number.text().strip(),
            "model": self.model.currentText()
        }
        
        # 2. 收集技术状态数据
        tech_data = {
            "drawing_number": self.drawing_number.text().strip(),
            "drawing_version": self.drawing_version.text().strip(),
            "software_version": self.software_version.text().strip(),
            "firmware_version": self.firmware_version.text().strip(),
            "hardware_config": self.hardware_config.toPlainText().strip(),
            "change_order": self.change_order.text().strip(),
            "change_description": self.change_description.toPlainText().strip(),
            "effective_date": self.effective_date.date().toString("yyyy-MM-dd")
        }
        
        # 3. 校验必填项
        if status == 'active':
            # 正式提交需要完整校验
            if not all([product_data["product_code"], product_data["product_name"], 
                       product_data["batch_number"], tech_data["drawing_number"], 
                       tech_data["drawing_version"]]):
                QMessageBox.warning(self, "校验失败", "请填写所有必填字段（带 * 号）")
                return
        else:
            # 草稿只需要产品代号
            if not product_data["product_code"]:
                QMessageBox.warning(self, "校验失败", "产品代号为必填项")
                return
        
        # 4. 保存到数据库
        try:
            # 保存产品
            product_data['status'] = status
            product_id = self.db.insert_product(product_data)
            
            # 保存技术状态
            tech_status_id = self.db.insert_tech_status(product_id, tech_data)
            
            # 记录变更日志
            log_content = f"创建产品 {product_data['product_code']}"
            self.db.insert_change_log(tech_status_id, "create", log_content)
            
            if status == 'draft':
                QMessageBox.information(self, "成功", "草稿已保存！")
            else:
                QMessageBox.information(self, "成功", "产品状态录入成功！")
            
            self.clear_form()
            
        except ValueError as e:
            QMessageBox.warning(self, "录入失败", str(e))
        except Exception as e:
            QMessageBox.critical(self, "系统错误", f"发生未知错误: {str(e)}")

    def clear_form(self):
        """清空表单"""
        self.product_code.clear()
        self.product_name.clear()
        self.batch_number.clear()
        self.model.setCurrentIndex(0)
        self.drawing_number.clear()
        self.drawing_version.clear()
        self.software_version.clear()
        self.firmware_version.clear()
        self.hardware_config.clear()
        self.change_order.clear()
        self.change_description.clear()
        self.effective_date.setDate(QDate.currentDate())
