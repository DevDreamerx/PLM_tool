# -*- coding: utf-8 -*-
from PyQt5.QtCore import QDate, QStringListModel, Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QCompleter,
    QDateEdit,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from db.database import DatabaseManager
from ui.theme import THEME
from utils.excel_importer import ExcelImporter


class EntryWidget(QWidget):
    """技术变更录入界面"""

    data_updated = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.importer = ExcelImporter()
        self.selected_product_id = None
        self.follow_up_issue_type = None
        self.product_options = {}
        self.product_label_by_id = {}
        self.init_ui()

    def init_ui(self):
        self._apply_entry_styles()

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(18)

        step_panel = QGroupBox("主流程")
        step_panel.setObjectName("StepCard")
        step_layout = QHBoxLayout()
        step_layout.setContentsMargins(22, 16, 22, 16)
        step_layout.setSpacing(10)
        for text in [
            "1. 选择产品",
            "2. 填写主信息",
            "3. 按需补充并提交",
        ]:
            label = QLabel(text)
            label.setObjectName("StepBadge")
            step_layout.addWidget(label)
        step_layout.addStretch()
        step_panel.setLayout(step_layout)
        main_layout.addWidget(step_panel)

        select_group = QGroupBox("产品定位")
        select_group.setObjectName("EntryCard")
        select_layout = QGridLayout()
        select_layout.setContentsMargins(24, 18, 24, 18)
        select_layout.setHorizontalSpacing(14)
        select_layout.setVerticalSpacing(10)

        self.product_search = QLineEdit()
        self.product_search.setPlaceholderText("输入产品代号、名称、批次或型号进行搜索")

        self.product_completer = QCompleter(self)
        self.product_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.product_completer.setFilterMode(Qt.MatchContains)
        self.product_completer.setCompletionMode(QCompleter.PopupCompletion)
        self.product_search.setCompleter(self.product_completer)
        self.product_search.editingFinished.connect(self.resolve_product_selection)
        self.product_completer.activated.connect(self.on_product_completion_selected)

        self.btn_clear_product = QPushButton("重新选择")
        self.btn_clear_product.setObjectName("GhostButton")
        self.btn_clear_product.setMinimumSize(116, 42)
        self.btn_clear_product.clicked.connect(self.clear_selected_product)

        select_hint = QLabel("自动补全格式：产品代号 | 产品名称 | 批次 | 型号")
        select_hint.setObjectName("HintText")

        select_layout.addWidget(QLabel("产品搜索:"), 0, 0)
        select_layout.addWidget(self.product_search, 0, 1, 1, 3)
        select_layout.addWidget(self.btn_clear_product, 0, 4)
        select_layout.addWidget(select_hint, 1, 1, 1, 4)
        select_layout.setColumnStretch(1, 2)
        select_layout.setColumnStretch(2, 0)
        select_layout.setColumnStretch(3, 1)
        select_group.setLayout(select_layout)
        main_layout.addWidget(select_group)

        self.product_group = QGroupBox("产品摘要")
        self.product_group.setObjectName("SummaryCard")
        product_layout = QGridLayout()
        product_layout.setContentsMargins(24, 18, 24, 18)
        product_layout.setHorizontalSpacing(14)
        product_layout.setVerticalSpacing(8)

        self.product_code = QLineEdit()
        self.product_code.setReadOnly(True)
        self.product_code.setObjectName("ReadOnlyField")
        self.product_name = QLineEdit()
        self.product_name.setReadOnly(True)
        self.product_name.setObjectName("ReadOnlyField")
        self.batch_number = QLineEdit()
        self.batch_number.setReadOnly(True)
        self.batch_number.setObjectName("ReadOnlyField")
        self.model = QLineEdit()
        self.model.setReadOnly(True)
        self.model.setObjectName("ReadOnlyField")

        product_layout.addWidget(QLabel("产品代号:"), 0, 0)
        product_layout.addWidget(self.product_code, 0, 1)
        product_layout.addWidget(QLabel("产品名称:"), 0, 2)
        product_layout.addWidget(self.product_name, 0, 3)
        product_layout.addWidget(QLabel("批次:"), 0, 4)
        product_layout.addWidget(self.batch_number, 0, 5)
        product_layout.addWidget(QLabel("型号:"), 0, 6)
        product_layout.addWidget(self.model, 0, 7)
        product_layout.setColumnStretch(1, 2)
        product_layout.setColumnStretch(3, 2)
        product_layout.setColumnStretch(5, 1)
        product_layout.setColumnStretch(7, 1)
        self.product_group.setLayout(product_layout)
        main_layout.addWidget(self.product_group)

        self.summary_banner = QLabel("请先选择一个已有产品，再开始录入本次技术变更。")
        self.summary_banner.setObjectName("SummaryBanner")
        self.summary_banner.setWordWrap(True)
        main_layout.addWidget(self.summary_banner)

        self.order_group = QGroupBox("变更主信息")
        self.order_group.setObjectName("EntryCard")
        order_layout = QGridLayout()
        order_layout.setContentsMargins(24, 18, 24, 18)
        order_layout.setHorizontalSpacing(14)
        order_layout.setVerticalSpacing(12)

        self.stage = QLineEdit()
        self.stage.setPlaceholderText("例如 C / S")
        self.coord_order = QLineEdit()
        self.coord_order.setPlaceholderText("协调单号")
        self.suggestion_order = QLineEdit()
        self.suggestion_order.setPlaceholderText("更改建议单号")
        self.main_change_order = QLineEdit()
        self.main_change_order.setPlaceholderText("更改单号/技术通知单号/工艺更改单号")

        order_layout.addWidget(QLabel("所属阶段:"), 0, 0)
        order_layout.addWidget(self.stage, 0, 1)
        order_layout.addWidget(QLabel("协调单号:"), 0, 2)
        order_layout.addWidget(self.coord_order, 0, 3)
        order_layout.addWidget(QLabel("更改建议单号:"), 1, 0)
        order_layout.addWidget(self.suggestion_order, 1, 1)
        order_layout.addWidget(QLabel("更改单号/技术通知单号/工艺更改单号:"), 1, 2)
        order_layout.addWidget(self.main_change_order, 1, 3)
        order_layout.setColumnStretch(1, 1)
        order_layout.setColumnStretch(3, 1)
        self.order_group.setLayout(order_layout)
        main_layout.addWidget(self.order_group)

        detail_wrap = QHBoxLayout()
        detail_wrap.setContentsMargins(4, 0, 4, 0)
        self.detail_tip = QLabel("更改类别、原因、处理意见等详细说明按需填写。")
        self.detail_tip.setObjectName("HintText")
        self.btn_toggle_detail = QPushButton("补充变更说明")
        self.btn_toggle_detail.setObjectName("GhostButton")
        self.btn_toggle_detail.setMinimumSize(128, 42)
        self.btn_toggle_detail.clicked.connect(self.toggle_detail_group)
        detail_wrap.addWidget(self.detail_tip)
        detail_wrap.addStretch()
        detail_wrap.addWidget(self.btn_toggle_detail)
        main_layout.addLayout(detail_wrap)

        self.change_group = QGroupBox("详细说明")
        self.change_group.setObjectName("SoftCard")
        change_layout = QGridLayout()
        change_layout.setContentsMargins(24, 18, 24, 18)
        change_layout.setHorizontalSpacing(14)
        change_layout.setVerticalSpacing(12)

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
        self.change_reason.setPlaceholderText("本次变更理由或摘要")
        self.change_reason.setMaximumHeight(80)
        self.suggestion_drawing = QLineEdit()
        self.suggestion_drawing.setPlaceholderText("更改建议单涉及图样/文件")
        self.change_drawing = QLineEdit()
        self.change_drawing.setPlaceholderText("涉及更改图样")

        change_layout.addWidget(QLabel("更改类别:"), 0, 0)
        change_layout.addWidget(self.change_type, 0, 1)
        change_layout.addWidget(QLabel("更改原因:"), 0, 2)
        change_layout.addWidget(self.change_cause, 0, 3)
        change_layout.addWidget(QLabel("更改人:"), 1, 0)
        change_layout.addWidget(self.change_owner, 1, 1)
        change_layout.addWidget(QLabel("处理意见:"), 1, 2)
        change_layout.addWidget(self.handle_opinion, 1, 3)
        change_layout.addWidget(QLabel("更改理由:"), 2, 0)
        change_layout.addWidget(self.change_reason, 2, 1, 1, 3)
        change_layout.addWidget(QLabel("更改建议单涉及图样/文件:"), 3, 0)
        change_layout.addWidget(self.suggestion_drawing, 3, 1)
        change_layout.addWidget(QLabel("涉及更改图样:"), 3, 2)
        change_layout.addWidget(self.change_drawing, 3, 3)
        change_layout.setColumnStretch(1, 1)
        change_layout.setColumnStretch(3, 1)
        self.change_group.setLayout(change_layout)
        main_layout.addWidget(self.change_group)

        optional_wrap = QHBoxLayout()
        optional_wrap.setContentsMargins(4, 0, 4, 0)
        self.optional_tip = QLabel("落实情况、备注和生效日期默认为可选补充信息。")
        self.optional_tip.setObjectName("HintText")
        self.btn_toggle_optional = QPushButton("补充落实信息")
        self.btn_toggle_optional.setObjectName("GhostButton")
        self.btn_toggle_optional.setMinimumSize(128, 42)
        self.btn_toggle_optional.clicked.connect(self.toggle_optional_group)
        optional_wrap.addWidget(self.optional_tip)
        optional_wrap.addStretch()
        optional_wrap.addWidget(self.btn_toggle_optional)
        main_layout.addLayout(optional_wrap)

        self.optional_group = QGroupBox("补充信息")
        self.optional_group.setObjectName("SoftCard")
        optional_layout = QGridLayout()
        optional_layout.setContentsMargins(24, 18, 24, 18)
        optional_layout.setHorizontalSpacing(14)
        optional_layout.setVerticalSpacing(12)

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

        optional_layout.addWidget(QLabel("需落实产品编号:"), 0, 0)
        optional_layout.addWidget(self.need_impl_product, 0, 1)
        optional_layout.addWidget(QLabel("已落实情况:"), 0, 2)
        optional_layout.addWidget(self.impl_status, 0, 3)
        optional_layout.addWidget(QLabel("未落实产品编号:"), 1, 0)
        optional_layout.addWidget(self.not_impl_product, 1, 1)
        optional_layout.addWidget(QLabel("工艺更改落实情况:"), 1, 2)
        optional_layout.addWidget(self.process_impl_status, 1, 3)
        optional_layout.addWidget(QLabel("备注:"), 2, 0)
        optional_layout.addWidget(self.remark, 2, 1, 1, 3)
        optional_layout.addWidget(QLabel("生效日期:"), 3, 0)
        optional_layout.addWidget(self.effective_date, 3, 1)
        optional_layout.setColumnStretch(1, 1)
        optional_layout.setColumnStretch(3, 1)
        self.optional_group.setLayout(optional_layout)
        main_layout.addWidget(self.optional_group)

        action_card = QGroupBox("提交操作")
        action_card.setObjectName("EntryCard")
        action_layout = QVBoxLayout()
        action_layout.setContentsMargins(24, 18, 24, 18)
        action_layout.setSpacing(12)

        self.action_hint = QLabel("主信息填写完成后即可提交；详细说明和补充信息可按需要再展开。")
        self.action_hint.setObjectName("ActionHint")
        self.action_hint.setWordWrap(True)
        action_layout.addWidget(self.action_hint)

        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 4, 0, 0)
        btn_layout.setSpacing(12)
        self.btn_clear = QPushButton("清空本次变更")
        self.btn_clear.setMinimumSize(122, 44)
        self.btn_clear.setObjectName("GhostButton")
        self.btn_clear.clicked.connect(self.clear_form)

        self.btn_submit = QPushButton("提交本次变更")
        self.btn_submit.setMinimumSize(132, 44)
        self.btn_submit.setObjectName("PrimaryButton")
        self.btn_submit.clicked.connect(self.submit_form)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_clear)
        btn_layout.addWidget(self.btn_submit)
        action_layout.addLayout(btn_layout)
        action_card.setLayout(action_layout)
        main_layout.addWidget(action_card)

        import_group = QGroupBox("辅助操作")
        import_group.setObjectName("SoftCard")
        import_layout = QHBoxLayout()
        import_layout.setContentsMargins(24, 18, 24, 18)
        import_layout.setSpacing(14)
        import_tip = QLabel("批量导入和刷新数据默认后置，避免打断当前录入主流程。")
        import_tip.setObjectName("HintText")

        self.btn_import = QPushButton("导入Excel")
        self.btn_import.setMinimumSize(116, 42)
        self.btn_import.setObjectName("GhostButton")
        self.btn_import.clicked.connect(self.import_excel)

        self.btn_refresh = QPushButton("刷新数据")
        self.btn_refresh.setMinimumSize(104, 42)
        self.btn_refresh.setObjectName("GhostButton")
        self.btn_refresh.clicked.connect(self.refresh_data)

        import_layout.addWidget(import_tip)
        import_layout.addStretch()
        import_layout.addWidget(self.btn_refresh)
        import_layout.addWidget(self.btn_import)
        import_group.setLayout(import_layout)
        main_layout.addWidget(import_group)

        main_layout.addStretch()

        container = QWidget()
        container.setObjectName("EntryContainer")
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        container.setLayout(main_layout)

        centered_container = QWidget()
        centered_layout = QHBoxLayout()
        centered_layout.setContentsMargins(18, 0, 18, 24)
        centered_layout.addStretch()
        centered_layout.addWidget(container)
        centered_layout.addStretch()
        centered_container.setLayout(centered_layout)

        container.setMaximumWidth(1240)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        scroll_area.setWidget(centered_container)

        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll_area)
        self.setLayout(outer_layout)

        self._connect_progress_signals()
        self.refresh_product_list()
        self.clear_selected_product()

    def _apply_entry_styles(self):
        self.setStyleSheet(
            f"""
            QWidget#EntryContainer {{
                background: transparent;
            }}
            QLabel#PageIntro, QLabel#EntryIntro {{
                color: {THEME['text_muted']};
                font-size: 14px;
                line-height: 1.5;
                padding: 0 4px 2px 4px;
            }}
            QLabel#HintText, QLabel#EntryHint {{
                color: {THEME['text_muted']};
                font-size: 12px;
            }}
            QLabel#SummaryBanner, QLabel#ActionHint {{
                color: {THEME['text']};
                background: #edf4fa;
                border: 1px solid #d7e3ee;
                border-radius: 14px;
                padding: 12px 16px;
                font-size: 13px;
                font-weight: 600;
            }}
            QGroupBox#EntryCard, QGroupBox#SummaryCard, QGroupBox#SoftCard, QGroupBox#StepCard {{
                border: 1px solid {THEME['border']};
                border-radius: 18px;
                margin-top: 10px;
                background: {THEME['bg_panel']};
                padding: 6px 0 0 0;
            }}
            QGroupBox#StepCard {{
                background: #f7fafc;
                border-color: #d9e3ef;
            }}
            QGroupBox#SummaryCard {{
                background: #f7fafc;
                border-color: #d9e3ef;
            }}
            QGroupBox#SoftCard {{
                background: #fbfcfe;
                border-color: #e5ebf3;
            }}
            QLabel#StepBadge {{
                color: #315f8d;
                background: #e8f1f8;
                border: 1px solid #d3e1ef;
                border-radius: 12px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: 700;
            }}
            QGroupBox#EntryCard::title, QGroupBox#SummaryCard::title, QGroupBox#SoftCard::title, QGroupBox#StepCard::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 16px;
                padding: 0 8px;
                color: {THEME['text_muted']};
                font-size: 13px;
                font-weight: 700;
                background: {THEME['bg_app']};
                border-radius: 8px;
            }}
            QLineEdit, QDateEdit {{
                min-height: 44px;
                border-radius: 12px;
                border: 1px solid #d8e2ee;
                background: #ffffff;
                padding: 0 14px;
            }}
            QLineEdit:focus, QDateEdit:focus, QTextEdit:focus {{
                border-color: #7ea6d8;
            }}
            QTextEdit {{
                border-radius: 14px;
                border: 1px solid #d8e2ee;
                background: #ffffff;
                padding: 10px 14px;
            }}
            QLineEdit#ReadOnlyField {{
                background: #eef4f8;
                color: {THEME['text']};
                border: 1px solid #d6e0ea;
                min-height: 38px;
            }}
            """
        )

    def _connect_progress_signals(self):
        for widget in [self.stage, self.coord_order, self.suggestion_order, self.main_change_order]:
            widget.textChanged.connect(self.update_progressive_state)

        for widget in [
            self.change_type,
            self.change_cause,
            self.change_owner,
            self.suggestion_drawing,
            self.change_drawing,
            self.need_impl_product,
            self.impl_status,
            self.not_impl_product,
            self.process_impl_status,
        ]:
            widget.textChanged.connect(self.update_progressive_state)

        self.change_reason.textChanged.connect(self.update_progressive_state)
        self.handle_opinion.textChanged.connect(self.update_progressive_state)
        self.remark.textChanged.connect(self.update_progressive_state)

    def refresh_data(self):
        self.refresh_product_list()
        self.data_updated.emit()

    def refresh_product_list(self):
        products = self.db.search_products("")
        self.product_options = {}
        self.product_label_by_id = {}
        labels = []

        for product in products:
            label = (
                f"{product['product_code']} | {product['product_name']} | "
                f"批次:{product['batch_number']} | 型号:{product['model']}"
            )
            self.product_options[label] = product
            self.product_label_by_id[product["id"]] = label
            labels.append(label)

        model = QStringListModel(labels, self.product_completer)
        self.product_completer.setModel(model)

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

    def on_product_completion_selected(self, text):
        product = self.product_options.get(text)
        if product:
            self.set_selected_product(product)

    def resolve_product_selection(self):
        text = self.product_search.text().strip()
        if not text:
            self.clear_selected_product()
            return

        product = self.product_options.get(text)
        if product:
            self.set_selected_product(product)
            return

        matches = self.db.search_products(text)
        if len(matches) == 1:
            self.set_selected_product(matches[0])
            return

        if self.selected_product_id in self.product_label_by_id:
            self.product_search.setText(self.product_label_by_id[self.selected_product_id])
        else:
            self.clear_selected_product()
            QMessageBox.information(self, "选择产品", "未匹配到唯一产品，请继续输入或从自动补全中选择。")

    def set_selected_product(self, product):
        self.follow_up_issue_type = None
        self.selected_product_id = product["id"]
        self.product_code.setText(product.get("product_code", ""))
        self.product_name.setText(product.get("product_name", ""))
        self.batch_number.setText(product.get("batch_number", ""))
        self.model.setText(product.get("model", ""))
        label = self.product_label_by_id.get(product["id"])
        if label:
            self.product_search.setText(label)
        self.update_progressive_state()

    def _is_prefill_value(self, value):
        if value is None:
            return False
        return str(value).strip() not in {"", "——", "--", "-", "—"}

    def _apply_follow_up_prefill(self, prefill):
        if not isinstance(prefill, dict):
            return

        line_edit_mapping = {
            "stage": self.stage,
            "coord_order": self.coord_order,
            "suggestion_order": self.suggestion_order,
            "main_change_order": self.main_change_order,
            "suggestion_drawing": self.suggestion_drawing,
            "change_drawing": self.change_drawing,
            "change_type": self.change_type,
            "change_cause": self.change_cause,
            "change_owner": self.change_owner,
            "need_impl_product": self.need_impl_product,
            "impl_status": self.impl_status,
            "not_impl_product": self.not_impl_product,
            "process_impl_status": self.process_impl_status,
        }
        text_edit_mapping = {
            "change_reason": self.change_reason,
            "handle_opinion": self.handle_opinion,
            "remark": self.remark,
        }

        for key, widget in line_edit_mapping.items():
            value = prefill.get(key)
            if self._is_prefill_value(value):
                widget.setText(str(value).strip())

        for key, widget in text_edit_mapping.items():
            value = prefill.get(key)
            if self._is_prefill_value(value):
                widget.setPlainText(str(value).strip())

        effective_date = prefill.get("effective_date")
        if self._is_prefill_value(effective_date):
            parsed_date = QDate.fromString(str(effective_date), "yyyy-MM-dd")
            if not parsed_date.isValid():
                parsed_date = QDate.fromString(str(effective_date), "yyyy-MM-dd HH:mm:ss")
            if parsed_date.isValid():
                self.effective_date.setDate(parsed_date)

    def open_follow_up_for_issue(self, product_id, issue_type=None, prefill=None):
        product = self.db.get_product(product_id)
        if not product:
            QMessageBox.warning(self, "错误", "未找到需要补录的产品")
            return False

        self.clear_form()
        self.set_selected_product(product)
        self.follow_up_issue_type = issue_type
        self._apply_follow_up_prefill(prefill)

        if issue_type == "missing_change":
            self.change_group.setVisible(True)
            self.btn_toggle_detail.setText("收起变更说明")
            self.optional_group.setVisible(False)
            self.btn_toggle_optional.setText("补充落实信息")
            self.main_change_order.setFocus()
        elif issue_type == "not_implemented":
            self.change_group.setVisible(False)
            self.btn_toggle_detail.setText("补充变更说明")
            self.optional_group.setVisible(True)
            self.btn_toggle_optional.setText("收起落实信息")
            self.impl_status.setFocus()
        else:
            self.change_group.setVisible(True)
            self.btn_toggle_detail.setText("收起变更说明")
            self.main_change_order.setFocus()

        self.update_progressive_state()
        return True

    def clear_selected_product(self):
        self.selected_product_id = None
        self.follow_up_issue_type = None
        self.product_search.clear()
        self.product_code.clear()
        self.product_name.clear()
        self.batch_number.clear()
        self.model.clear()
        self.clear_form()
        self.update_progressive_state()

    def toggle_optional_group(self):
        visible = not self.optional_group.isVisible()
        self.optional_group.setVisible(visible)
        self.btn_toggle_optional.setText("收起落实信息" if visible else "补充落实信息")

    def toggle_detail_group(self):
        visible = not self.change_group.isVisible()
        self.change_group.setVisible(visible)
        self.btn_toggle_detail.setText("收起变更说明" if visible else "补充变更说明")

    def update_progressive_state(self):
        has_product = self.selected_product_id is not None
        has_order_context = any([
            self.stage.text().strip(),
            self.coord_order.text().strip(),
            self.suggestion_order.text().strip(),
            self.main_change_order.text().strip(),
        ])
        has_core_change = any([
            self.change_type.text().strip(),
            self.change_cause.text().strip(),
            self.change_owner.text().strip(),
            self.change_reason.toPlainText().strip(),
            self.handle_opinion.toPlainText().strip(),
            self.suggestion_drawing.text().strip(),
            self.change_drawing.text().strip(),
        ])
        has_optional_change = any([
            self.need_impl_product.text().strip(),
            self.impl_status.text().strip(),
            self.not_impl_product.text().strip(),
            self.process_impl_status.text().strip(),
            self.remark.toPlainText().strip(),
        ])

        self.product_group.setEnabled(has_product)
        self.order_group.setEnabled(has_product)
        self.change_group.setEnabled(has_product)
        self.btn_toggle_detail.setEnabled(has_product)
        self.btn_toggle_optional.setEnabled(has_product and (has_order_context or has_core_change or has_optional_change))
        self.optional_tip.setEnabled(has_product)
        self.btn_submit.setEnabled(has_product)

        if has_product:
            product_code = self.product_code.text().strip() or "未选择"
            if self.follow_up_issue_type == "missing_change":
                self.summary_banner.setText(
                    f"当前产品：{product_code}｜该记录缺少更改单号或图样关联，建议优先补齐变更主信息。"
                )
                self.action_hint.setText("请补充更改单号、涉及图样或相关说明，提交后看板会自动刷新。")
            elif self.follow_up_issue_type == "not_implemented":
                self.summary_banner.setText(
                    f"当前产品：{product_code}｜该记录存在待落实项，建议优先补充落实状态与闭环结果。"
                )
                self.action_hint.setText("请补充已落实情况或工艺落实结果，提交后看板会自动刷新。")
            elif has_order_context:
                self.summary_banner.setText(
                    f"当前产品：{product_code}｜先完成主信息，需要补充说明时再展开下方详细区域。"
                )
                self.action_hint.setText("已填写部分主信息，可以直接提交，或继续补充详细说明。")
            else:
                self.summary_banner.setText(
                    f"当前产品：{product_code}｜先完成主信息，需要补充说明时再展开下方详细区域。"
                )
                self.action_hint.setText("建议先填写所属阶段、单号等主信息，再决定是否补充详细说明。")
        else:
            self.follow_up_issue_type = None
            self.summary_banner.setText("请先选择一个已有产品，再开始录入本次技术变更。")
            self.action_hint.setText("主信息填写完成后即可提交；详细说明和补充信息可按需要再展开。")

        if not has_product:
            self.change_group.setVisible(False)
            self.btn_toggle_detail.setText("补充变更说明")
            self.optional_group.setVisible(False)
            self.btn_toggle_optional.setText("补充落实信息")
        elif not self.btn_toggle_optional.isEnabled():
            self.optional_group.setVisible(False)
            self.btn_toggle_optional.setText("补充落实信息")

    def submit_form(self):
        if not self.selected_product_id:
            QMessageBox.warning(self, "校验失败", "请先选择已有产品")
            return

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

        has_substantive_change = any([
            _value(self.coord_order),
            _value(self.suggestion_order),
            _value(self.main_change_order),
            _value(self.change_reason),
            _value(self.suggestion_drawing),
            _value(self.change_drawing),
            _value(self.change_type),
            _value(self.change_cause),
            _value(self.change_owner),
            _value(self.handle_opinion),
            _value(self.need_impl_product),
            _value(self.impl_status),
            _value(self.not_impl_product),
            _value(self.process_impl_status),
            _value(self.remark),
        ])
        if not has_substantive_change:
            QMessageBox.warning(self, "校验失败", "请至少填写一项实质性变更内容")
            return

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
            "effective_date": self.effective_date.date().toString("yyyy-MM-dd"),
        }

        try:
            tech_status_id = self.db.insert_tech_status(self.selected_product_id, tech_data)
            log_content = f"更新技术状态 {self.product_code.text().strip()}"
            self.db.insert_change_log(tech_status_id, "update", log_content)
            QMessageBox.information(self, "成功", "技术状态变更已记录！")
            self.clear_form()
            self.data_updated.emit()
        except Exception as exc:
            QMessageBox.critical(self, "系统错误", f"发生未知错误: {exc}")

    def clear_form(self):
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
        self.change_group.setVisible(False)
        self.btn_toggle_detail.setText("补充变更说明")
        self.optional_group.setVisible(False)
        self.btn_toggle_optional.setText("补充落实信息")
        self.update_progressive_state()
