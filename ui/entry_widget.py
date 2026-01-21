# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QTextEdit,
    QComboBox,
    QDateEdit,
    QPushButton,
    QGridLayout,
    QHBoxLayout,
    QMessageBox,
    QGroupBox,
    QVBoxLayout,
    QScrollArea,
    QSizePolicy,
)
from PyQt5.QtCore import QDate
from db.database import DatabaseManager

class EntryWidget(QWidget):
    """状态录入界面"""
    
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题
        title = QLabel("技术状态录入")
        title.setObjectName("PageTitle")
        main_layout.addWidget(title)

        # 录入模式
        mode_group = QGroupBox("录入模式")
        mode_layout = QHBoxLayout()

        self.mode_switch = QComboBox()
        self.mode_switch.addItems(["新建产品", "变更录入"])
        self.mode_switch.currentIndexChanged.connect(self.on_mode_changed)

        self.product_selector = QComboBox()
        self.product_selector.setEnabled(False)
        self.product_selector.currentIndexChanged.connect(self.on_product_selected)

        mode_layout.addWidget(QLabel("模式:"))
        mode_layout.addWidget(self.mode_switch)
        mode_layout.addSpacing(12)
        mode_layout.addWidget(QLabel("已有产品:"))
        mode_layout.addWidget(self.product_selector)
        mode_layout.addStretch()
        mode_group.setLayout(mode_layout)
        main_layout.addWidget(mode_group)
        
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
        self.software_version.setPlaceholderText("选填，可含构建号")
        
        self.firmware_version = QLineEdit()
        self.firmware_version.setPlaceholderText("选填，可含构建号")
        
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

        # 3. 配置与合格信息组
        config_group = QGroupBox("配置与合格信息")
        config_layout = QGridLayout()

        self.req_baseline = QLineEdit()
        self.req_baseline.setPlaceholderText("需求/功能基线版本")

        self.icd_version = QLineEdit()
        self.icd_version.setPlaceholderText("接口基线版本")

        self.bom_version = QLineEdit()
        self.bom_version.setPlaceholderText("BOM版本")

        self.pcb_version = QLineEdit()
        self.pcb_version.setPlaceholderText("PCB版本")

        self.hw_serial = QLineEdit()
        self.hw_serial.setPlaceholderText("硬件序列号")

        self.production_batch = QLineEdit()
        self.production_batch.setPlaceholderText("生产批次")


        self.test_status = QComboBox()
        self.test_status.addItems(["未测试", "单元测试", "集成测试", "系统测试", "环境试验"])

        self.qual_status = QComboBox()
        self.qual_status.addItems(["未评审", "评审中", "合格", "限制放行"])

        config_layout.addWidget(QLabel("需求基线:"), 0, 0)
        config_layout.addWidget(self.req_baseline, 0, 1)
        config_layout.addWidget(QLabel("接口基线:"), 0, 2)
        config_layout.addWidget(self.icd_version, 0, 3)

        config_layout.addWidget(QLabel("BOM版本:"), 1, 0)
        config_layout.addWidget(self.bom_version, 1, 1)
        config_layout.addWidget(QLabel("PCB版本:"), 1, 2)
        config_layout.addWidget(self.pcb_version, 1, 3)

        config_layout.addWidget(QLabel("硬件序列号:"), 2, 0)
        config_layout.addWidget(self.hw_serial, 2, 1)
        config_layout.addWidget(QLabel("生产批次:"), 2, 2)
        config_layout.addWidget(self.production_batch, 2, 3)

        config_layout.addWidget(QLabel("测试状态:"), 3, 0)
        config_layout.addWidget(self.test_status, 3, 1)
        config_layout.addWidget(QLabel("合格状态:"), 3, 2)
        config_layout.addWidget(self.qual_status, 3, 3)

        config_group.setLayout(config_layout)
        main_layout.addWidget(config_group)
        
        # 4. 变更信息组
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
        
        # 5. 按钮组
        btn_layout = QHBoxLayout()
        
        self.btn_draft = QPushButton("暂存草稿")
        self.btn_draft.setFixedSize(120, 40)
        self.btn_draft.setObjectName("WarningButton")
        self.btn_draft.clicked.connect(self.save_draft)
        
        self.btn_submit = QPushButton("正式提交")
        self.btn_submit.setFixedSize(120, 40)
        self.btn_submit.clicked.connect(self.submit_form)
        
        self.btn_clear = QPushButton("清空")
        self.btn_clear.setFixedSize(80, 40)
        self.btn_clear.setObjectName("GhostButton")
        self.btn_clear.clicked.connect(self.clear_form)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_clear)
        btn_layout.addWidget(self.btn_draft)
        btn_layout.addWidget(self.btn_submit)
        
        main_layout.addLayout(btn_layout)
        main_layout.addStretch()

        container = QWidget()
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        container.setLayout(main_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        scroll_area.setWidget(container)

        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll_area)

        self.setLayout(outer_layout)
        self.refresh_product_list()

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
            "req_baseline": self.req_baseline.text().strip(),
            "icd_version": self.icd_version.text().strip(),
            "bom_version": self.bom_version.text().strip(),
            "pcb_version": self.pcb_version.text().strip(),
            "hw_serial": self.hw_serial.text().strip(),
            "production_batch": self.production_batch.text().strip(),
            "test_status": self.test_status.currentText(),
            "qual_status": self.qual_status.currentText(),
            "change_order": self.change_order.text().strip(),
            "change_description": self.change_description.toPlainText().strip(),
            "effective_date": self.effective_date.date().toString("yyyy-MM-dd")
        }
        
        # 3. 校验必填项
        if not tech_data["drawing_number"] or not tech_data["drawing_version"]:
            QMessageBox.warning(self, "校验失败", "请填写图号与图纸版本")
            return

        if self.is_change_mode():
            product_id = self.current_product_id()
            if not product_id:
                QMessageBox.warning(self, "校验失败", "请选择已有产品")
                return
        else:
            if status == 'active':
                if not all([product_data["product_code"], product_data["product_name"],
                           product_data["batch_number"]]):
                    QMessageBox.warning(self, "校验失败", "请填写所有必填字段（带 * 号）")
                    return
            else:
                if not product_data["product_code"]:
                    QMessageBox.warning(self, "校验失败", "产品代号为必填项")
                    return

        # 4. 保存到数据库
        try:
            if self.is_change_mode():
                tech_status_id = self.db.insert_tech_status(product_id, tech_data)
                log_content = f"更新技术状态 {product_data['product_code']}"
                self.db.insert_change_log(tech_status_id, "update", log_content)
                QMessageBox.information(self, "成功", "技术状态变更已记录！")
                self.clear_form(keep_product=True)
            else:
                product_data['status'] = status
                product_id = self.db.insert_product(product_data)
                tech_status_id = self.db.insert_tech_status(product_id, tech_data)
                log_content = f"创建产品 {product_data['product_code']}"
                self.db.insert_change_log(tech_status_id, "create", log_content)
                if status == 'draft':
                    QMessageBox.information(self, "成功", "草稿已保存！")
                else:
                    QMessageBox.information(self, "成功", "产品状态录入成功！")
                self.clear_form()
                self.refresh_product_list()
            
        except ValueError as e:
            QMessageBox.warning(self, "录入失败", str(e))
        except Exception as e:
            QMessageBox.critical(self, "系统错误", f"发生未知错误: {str(e)}")

    def clear_form(self, keep_product=False):
        """清空表单"""
        if not keep_product:
            self.product_code.clear()
            self.product_name.clear()
            self.batch_number.clear()
            self.model.setCurrentIndex(0)
        self.drawing_number.clear()
        self.drawing_version.clear()
        self.software_version.clear()
        self.firmware_version.clear()
        self.hardware_config.clear()
        self.req_baseline.clear()
        self.icd_version.clear()
        self.bom_version.clear()
        self.pcb_version.clear()
        self.hw_serial.clear()
        self.production_batch.clear()
        self.test_status.setCurrentIndex(0)
        self.qual_status.setCurrentIndex(0)
        self.change_order.clear()
        self.change_description.clear()
        self.effective_date.setDate(QDate.currentDate())

    def refresh_product_list(self):
        self.product_selector.blockSignals(True)
        self.product_selector.clear()
        self.product_selector.addItem("请选择产品...", None)
        products = self.db.search_products("")
        for product in products:
            label = f"{product['product_code']} - {product['product_name']}"
            self.product_selector.addItem(label, product["id"])
        self.product_selector.blockSignals(False)

    def on_mode_changed(self, index):
        change_mode = index == 1
        self.product_selector.setEnabled(change_mode)
        self.btn_draft.setEnabled(not change_mode)
        for field in [self.product_code, self.product_name, self.batch_number, self.model]:
            field.setEnabled(not change_mode)
        if change_mode:
            self.on_product_selected(self.product_selector.currentIndex())
        else:
            self.clear_form()

    def on_product_selected(self, index):
        if not self.is_change_mode():
            return
        product_id = self.product_selector.itemData(index)
        if not product_id:
            self.product_code.clear()
            self.product_name.clear()
            self.batch_number.clear()
            self.model.setCurrentIndex(0)
            return
        data = self.db.get_product(product_id)
        if not data:
            return
        self.product_code.setText(data.get("product_code", ""))
        self.product_name.setText(data.get("product_name", ""))
        self.batch_number.setText(data.get("batch_number", ""))
        model_index = self.model.findText(data.get("model", ""))
        self.model.setCurrentIndex(model_index if model_index >= 0 else 0)

    def is_change_mode(self):
        return self.mode_switch.currentIndex() == 1

    def current_product_id(self):
        return self.product_selector.currentData()
