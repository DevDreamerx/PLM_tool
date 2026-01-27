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
    QFileDialog,
)
from PyQt5.QtCore import QDate, pyqtSignal
from db.database import DatabaseManager
from ui.theme import THEME
from utils.excel_importer import ExcelImporter

class EntryWidget(QWidget):
    """状态录入界面"""

    data_updated = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.importer = ExcelImporter()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题
        title = QLabel("技术状态录入")
        title.setObjectName("PageTitle")
        main_layout.addWidget(title)

        # 数据导入
        import_group = QGroupBox("数据导入与刷新")
        import_layout = QHBoxLayout()
        import_tip = QLabel("支持批量导入 Excel 更新数据库，并同步待处理看板。")
        import_tip.setStyleSheet(f"color: {THEME['text_muted']};")

        self.btn_import = QPushButton("导入Excel")
        self.btn_import.setFixedSize(110, 36)
        self.btn_import.setObjectName("GhostButton")
        self.btn_import.clicked.connect(self.import_excel)

        self.btn_refresh = QPushButton("刷新数据")
        self.btn_refresh.setFixedSize(96, 36)
        self.btn_refresh.setObjectName("GhostButton")
        self.btn_refresh.clicked.connect(self.refresh_data)

        import_layout.addWidget(import_tip)
        import_layout.addStretch()
        import_layout.addWidget(self.btn_refresh)
        import_layout.addWidget(self.btn_import)
        import_group.setLayout(import_layout)
        main_layout.addWidget(import_group)

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
        
        # 基本信息（产品 + 模板参数）
        change_group = QGroupBox("基本信息")
        change_layout = QGridLayout()

        self.product_code = QLineEdit()
        self.product_code.setPlaceholderText("必填 *")

        self.product_name = QLineEdit()
        self.product_name.setPlaceholderText("必填 *")

        self.batch_number = QLineEdit()
        self.batch_number.setPlaceholderText("必填 *")

        self.model = QComboBox()
        self.model.addItems(["型号A", "型号B", "型号C", "其他"])

        self.stage = QLineEdit()
        self.stage.setPlaceholderText("所属阶段")

        self.coord_order = QLineEdit()
        self.coord_order.setPlaceholderText("协调单号")

        self.suggestion_order = QLineEdit()
        self.suggestion_order.setPlaceholderText("更改建议单号")

        self.main_change_order = QLineEdit()
        self.main_change_order.setPlaceholderText("更改单号/技术通知单号/工艺更改单号")

        self.change_type = QLineEdit()
        self.change_type.setPlaceholderText("更改类别")

        self.change_cause = QLineEdit()
        self.change_cause.setPlaceholderText("更改原因")

        self.change_owner = QLineEdit()
        self.change_owner.setPlaceholderText("更改人")

        self.handle_opinion = QTextEdit()
        self.handle_opinion.setPlaceholderText("处理意见")
        self.handle_opinion.setMaximumHeight(60)

        self.change_reason = QTextEdit()
        self.change_reason.setPlaceholderText("更改理由")
        self.change_reason.setMaximumHeight(60)

        self.suggestion_drawing = QLineEdit()
        self.suggestion_drawing.setPlaceholderText("更改建议单涉及图样/文件")

        self.change_drawing = QLineEdit()
        self.change_drawing.setPlaceholderText("涉及更改图样")

        self.need_impl_product = QLineEdit()
        self.need_impl_product.setPlaceholderText("需落实产品编号")

        self.impl_status = QLineEdit()
        self.impl_status.setPlaceholderText("已落实情况")

        self.not_impl_product = QLineEdit()
        self.not_impl_product.setPlaceholderText("未落实产品编号")

        self.process_impl_status = QLineEdit()
        self.process_impl_status.setPlaceholderText("工艺更改落实情况")

        self.remark = QTextEdit()
        self.remark.setPlaceholderText("备注")
        self.remark.setMaximumHeight(60)

        self.effective_date = QDateEdit()
        self.effective_date.setCalendarPopup(True)
        self.effective_date.setDate(QDate.currentDate())

        change_layout.addWidget(QLabel("产品代号:"), 0, 0)
        change_layout.addWidget(self.product_code, 0, 1)
        change_layout.addWidget(QLabel("产品名称:"), 0, 2)
        change_layout.addWidget(self.product_name, 0, 3)

        change_layout.addWidget(QLabel("批次编号:"), 1, 0)
        change_layout.addWidget(self.batch_number, 1, 1)
        change_layout.addWidget(QLabel("所属型号:"), 1, 2)
        change_layout.addWidget(self.model, 1, 3)

        change_layout.addWidget(QLabel("所属阶段:"), 2, 0)
        change_layout.addWidget(self.stage, 2, 1)
        change_layout.addWidget(QLabel("协调单号:"), 2, 2)
        change_layout.addWidget(self.coord_order, 2, 3)

        change_layout.addWidget(QLabel("更改建议单号:"), 3, 0)
        change_layout.addWidget(self.suggestion_order, 3, 1)
        change_layout.addWidget(QLabel("更改单号/技术通知单号/工艺更改单号:"), 3, 2)
        change_layout.addWidget(self.main_change_order, 3, 3)

        change_layout.addWidget(QLabel("更改类别:"), 4, 0)
        change_layout.addWidget(self.change_type, 4, 1)
        change_layout.addWidget(QLabel("更改原因:"), 4, 2)
        change_layout.addWidget(self.change_cause, 4, 3)

        change_layout.addWidget(QLabel("更改人:"), 5, 0)
        change_layout.addWidget(self.change_owner, 5, 1)
        change_layout.addWidget(QLabel("处理意见:"), 5, 2)
        change_layout.addWidget(self.handle_opinion, 5, 3)

        change_layout.addWidget(QLabel("更改理由:"), 6, 0)
        change_layout.addWidget(self.change_reason, 6, 1, 1, 3)

        change_layout.addWidget(QLabel("更改建议单涉及图样/文件:"), 7, 0)
        change_layout.addWidget(self.suggestion_drawing, 7, 1)
        change_layout.addWidget(QLabel("涉及更改图样:"), 7, 2)
        change_layout.addWidget(self.change_drawing, 7, 3)

        change_layout.addWidget(QLabel("需落实产品编号:"), 8, 0)
        change_layout.addWidget(self.need_impl_product, 8, 1)
        change_layout.addWidget(QLabel("已落实情况:"), 8, 2)
        change_layout.addWidget(self.impl_status, 8, 3)

        change_layout.addWidget(QLabel("未落实产品编号:"), 9, 0)
        change_layout.addWidget(self.not_impl_product, 9, 1)
        change_layout.addWidget(QLabel("工艺更改落实情况:"), 9, 2)
        change_layout.addWidget(self.process_impl_status, 9, 3)

        change_layout.addWidget(QLabel("备注:"), 10, 0)
        change_layout.addWidget(self.remark, 10, 1, 1, 3)
        change_layout.addWidget(QLabel("生效日期:"), 11, 0)
        change_layout.addWidget(self.effective_date, 11, 1)

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

    def refresh_data(self):
        self.refresh_product_list()
        self.data_updated.emit()

    def import_excel(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择Excel文件", "", "Excel Files (*.xlsx)"
        )
        if not file_path:
            return

        try:
            parsed = self.importer.parse(file_path)
        except Exception as exc:
            QMessageBox.critical(self, "导入失败", f"解析Excel失败:\n{exc}")
            return

        rows = parsed["rows"]
        if not rows:
            QMessageBox.information(self, "导入提示", "未识别到有效数据行")
            return

        created_products = 0
        updated_products = 0
        inserted_status = 0
        skipped_rows = 0
        errors = []

        for idx, row in enumerate(rows, 1):
            product_code = row.get("product_code")
            product_name = row.get("product_name") or product_code or "未命名"
            batch_number = row.get("batch_number") or "未填写"
            model = row.get("model") or "其他"

            if not product_code:
                skipped_rows += 1
                errors.append(f"第{idx}行缺少产品代号")
                continue

            product = self.db.get_product_by_code(product_code)
            if product:
                if any([row.get("product_name"), row.get("batch_number"), row.get("model")]):
                    self.db.update_product_basic(
                        product["id"],
                        {
                            "product_name": product_name,
                            "batch_number": batch_number,
                            "model": model,
                        },
                    )
                    updated_products += 1
                product_id = product["id"]
            else:
                try:
                    product_id = self.db.insert_product(
                        {
                            "product_code": product_code,
                            "product_name": product_name,
                            "batch_number": batch_number,
                            "model": model,
                            "status": "active",
                        }
                    )
                    created_products += 1
                except Exception as exc:
                    skipped_rows += 1
                    errors.append(f"第{idx}行产品创建失败: {exc}")
                    continue

            tech_status_id = self.db.insert_tech_status(product_id, row)
            if row.get("change_order") or row.get("change_description"):
                log_content = f"Excel导入更新 {product_code}"
                self.db.insert_change_log(tech_status_id, "update", log_content)
            inserted_status += 1

        message = (
            f"导入完成\n新增产品: {created_products}\n更新产品: {updated_products}"
            f"\n新增技术状态: {inserted_status}\n跳过行数: {skipped_rows}"
        )
        if errors:
            message += "\n\n错误示例:\n" + "\n".join(errors[:5])
        QMessageBox.information(self, "导入结果", message)
        self.refresh_product_list()
        self.data_updated.emit()

    def _save_data(self, status='active'):
        """保存数据"""
        # 1. 收集产品数据
        product_data = {
            "product_code": self.product_code.text().strip(),
            "product_name": self.product_name.text().strip(),
            "batch_number": self.batch_number.text().strip(),
            "model": self.model.currentText()
        }
        
        def _value(widget):
            if isinstance(widget, QTextEdit):
                return widget.toPlainText().strip()
            return widget.text().strip()

        change_order_fields = {
            "协调单号": _value(self.coord_order),
            "更改建议单号": _value(self.suggestion_order),
            "更改单号/技术通知单号/工艺更改单号": _value(self.main_change_order),
        }

        change_desc_fields = {
            "所属阶段": _value(self.stage),
            "更改理由": _value(self.change_reason),
            "更改建议单涉及图样/文件": _value(self.suggestion_drawing),
            "涉及更改图样": _value(self.change_drawing),
            "更改类别": _value(self.change_type),
            "更改原因": _value(self.change_cause),
            "更改人": _value(self.change_owner),
            "处理意见": _value(self.handle_opinion),
            "需落实产品编号": _value(self.need_impl_product),
            "已落实情况": _value(self.impl_status),
            "未落实产品编号": _value(self.not_impl_product),
            "工艺更改落实情况": _value(self.process_impl_status),
            "备注": _value(self.remark),
        }

        change_order = "; ".join(
            f"{label}:{value}" for label, value in change_order_fields.items() if value
        )
        change_description = "; ".join(
            f"{label}:{value}" for label, value in change_desc_fields.items() if value
        )

        # 2. 收集技术状态数据（保留模板字段）
        tech_data = {
            "drawing_number": "",
            "drawing_version": "",
            "software_version": "",
            "firmware_version": "",
            "hardware_config": "",
            "req_baseline": "",
            "icd_version": "",
            "bom_version": "",
            "pcb_version": "",
            "hw_serial": "",
            "production_batch": "",
            "test_status": "",
            "qual_status": "",
            "change_order": change_order,
            "change_description": change_description,
            "effective_date": self.effective_date.date().toString("yyyy-MM-dd")
        }
        
        # 3. 校验必填项
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
            self.data_updated.emit()
            
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
        self.stage.clear()
        self.coord_order.clear()
        self.suggestion_order.clear()
        self.main_change_order.clear()
        self.change_type.clear()
        self.change_cause.clear()
        self.change_owner.clear()
        self.handle_opinion.clear()
        self.change_reason.clear()
        self.suggestion_drawing.clear()
        self.change_drawing.clear()
        self.need_impl_product.clear()
        self.impl_status.clear()
        self.not_impl_product.clear()
        self.process_impl_status.clear()
        self.remark.clear()
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
