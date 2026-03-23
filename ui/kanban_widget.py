from datetime import datetime

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from db.database import DatabaseManager
from ui.theme import THEME, scale_px


class TimelineCard(QFrame):
    clicked = pyqtSignal(object)

    def __init__(self, data, tone="amber"):
        super().__init__()
        self.data = data
        self.tone = tone
        self.init_ui()

    def init_ui(self):
        accent = "#b7791f" if self.tone == "amber" else "#315f8d"
        accent_soft = "#f9f2df" if self.tone == "amber" else "#edf4fa"
        accent_text = "#8a6116" if self.tone == "amber" else "#315f8d"

        self.setObjectName("TimelineCard")
        self.setStyleSheet(
            f"""
            QFrame#TimelineCard {{
                background: #ffffff;
                border: 1px solid #dbe4ee;
                border-left: 4px solid {accent};
                border-radius: 16px;
            }}
            QFrame#TimelineCard:hover {{
                border-color: {accent};
                background: #fcfdff;
            }}
            QLabel {{
                background: transparent;
                border: none;
            }}
            QLabel#DelayBadge {{
                background: {accent_soft};
                color: {accent_text};
                border-radius: 10px;
                padding: 4px 10px;
                font-weight: 700;
            }}
            QLabel#IssueBadge {{
                background: {accent_soft};
                color: {accent_text};
                border-radius: 10px;
                padding: 4px 10px;
                font-weight: 600;
            }}
            QPushButton#InlineAction {{
                min-height: 32px;
                color: {accent_text};
                border: 1px solid #c8d7e6;
                border-radius: 10px;
                background: #ffffff;
                padding: 0 12px;
                font-weight: 600;
            }}
            QPushButton#InlineAction:hover {{
                background: {accent_soft};
            }}
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        top = QHBoxLayout()
        top.setSpacing(8)

        time_label = QLabel(self.data.get("timeline_text", ""))
        time_label.setStyleSheet(
            f"color: {THEME['text_muted']}; font-size: {scale_px(11)}px; font-weight: 600;"
        )
        delay = QLabel(self.data.get("delay_text", ""))
        delay.setObjectName("DelayBadge")
        delay.setStyleSheet(
            delay.styleSheet() + f"font-size: {scale_px(11)}px;"
        )
        top.addWidget(time_label)
        top.addStretch()
        top.addWidget(delay)
        layout.addLayout(top)

        title = QLabel(f"{self.data.get('product_code', '')}  {self.data.get('product_name', '')}")
        title.setWordWrap(True)
        title.setStyleSheet(
            f"color: {THEME['text']}; font-size: {scale_px(15)}px; font-weight: 700;"
        )
        layout.addWidget(title)

        badges = QHBoxLayout()
        badges.setSpacing(8)
        for text in self.data.get("badges", []):
            badge = QLabel(text)
            badge.setObjectName("IssueBadge")
            badge.setStyleSheet(
                badge.styleSheet() + f"font-size: {scale_px(11)}px;"
            )
            badges.addWidget(badge)
        badges.addStretch()
        layout.addLayout(badges)

        summary = QLabel(self.data.get("summary", ""))
        summary.setWordWrap(True)
        summary.setStyleSheet(
            f"color: {THEME['text_muted']}; font-size: {scale_px(12)}px; line-height: 1.5;"
        )
        layout.addWidget(summary)

        footer = QHBoxLayout()
        footer.setSpacing(10)

        owner = QLabel(f"责任人：{self.data.get('owner', '未填写')}")
        owner.setStyleSheet(
            f"color: {THEME['text_muted']}; font-size: {scale_px(11)}px;"
        )
        footer.addWidget(owner)
        footer.addStretch()

        action = QPushButton(self.data.get("action_text", "去补录"))
        action.setObjectName("InlineAction")
        action.clicked.connect(lambda: self.clicked.emit(self.data))
        footer.addWidget(action)
        layout.addLayout(footer)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.data)
        super().mouseReleaseEvent(event)


class TimelineLane(QFrame):
    card_clicked = pyqtSignal(object)

    def __init__(self, title, hint, tone="amber"):
        super().__init__()
        self.title = title
        self.hint = hint
        self.tone = tone
        self.cards = []
        self.init_ui()

    def init_ui(self):
        accent = "#b7791f" if self.tone == "amber" else "#315f8d"
        soft_bg = "#fcf8ef" if self.tone == "amber" else "#f4f8fc"
        self.setObjectName("TimelineLane")
        self.setStyleSheet(
            f"""
            QFrame#TimelineLane {{
                background: #ffffff;
                border: 1px solid #dbe4ee;
                border-radius: 20px;
            }}
            QFrame#LaneHeader {{
                background: {soft_bg};
                border-bottom: 1px solid #e3ebf3;
                border-top-left-radius: 20px;
                border-top-right-radius: 20px;
            }}
            QLabel#LaneTitle {{
                color: {THEME['text']};
                font-size: {scale_px(16)}px;
                font-weight: 700;
            }}
            QLabel#LaneHint {{
                color: {THEME['text_muted']};
                font-size: {scale_px(12)}px;
            }}
            QLabel#LaneCount {{
                background: rgba(255,255,255,0.72);
                color: {accent};
                border: 1px solid #d7e2ed;
                border-radius: 11px;
                padding: 4px 10px;
                font-size: {scale_px(11)}px;
                font-weight: 700;
            }}
            QFrame#LaneEmptyState {{
                background: #f8fbfd;
                border: 1px dashed #d7e2ed;
                border-radius: 14px;
            }}
            QLabel#LaneEmptyTitle {{
                color: {THEME['text']};
                font-size: {scale_px(13)}px;
                font-weight: 700;
            }}
            QLabel#LaneEmptyHint {{
                color: {THEME['text_muted']};
                font-size: {scale_px(12)}px;
            }}
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QFrame()
        header.setObjectName("LaneHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(18, 16, 18, 16)

        text_wrap = QVBoxLayout()
        text_wrap.setSpacing(4)
        title = QLabel(self.title)
        title.setObjectName("LaneTitle")
        hint = QLabel(self.hint)
        hint.setObjectName("LaneHint")
        hint.setWordWrap(True)
        text_wrap.addWidget(title)
        text_wrap.addWidget(hint)
        header_layout.addLayout(text_wrap)
        header_layout.addStretch()

        self.count_label = QLabel("0 项")
        self.count_label.setObjectName("LaneCount")
        header_layout.addWidget(self.count_label)

        layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        self.card_layout = QVBoxLayout(container)
        self.card_layout.setContentsMargins(18, 18, 18, 18)
        self.card_layout.setSpacing(12)
        self.empty_state = QFrame()
        self.empty_state.setObjectName("LaneEmptyState")
        empty_layout = QVBoxLayout(self.empty_state)
        empty_layout.setContentsMargins(16, 18, 16, 18)
        empty_layout.setSpacing(6)
        empty_title = QLabel("当前没有待处理项")
        empty_title.setObjectName("LaneEmptyTitle")
        empty_hint = QLabel(self.hint)
        empty_hint.setObjectName("LaneEmptyHint")
        empty_hint.setWordWrap(True)
        empty_layout.addWidget(empty_title)
        empty_layout.addWidget(empty_hint)
        self.card_layout.addWidget(self.empty_state)
        self.card_layout.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)
        self.card_count = 0

    def clear_cards(self):
        for index in range(self.card_layout.count() - 2, -1, -1):
            item = self.card_layout.itemAt(index)
            widget = item.widget()
            if widget is not None and widget is not self.empty_state:
                self.card_layout.removeWidget(widget)
                widget.deleteLater()
        self.card_count = 0
        self.empty_state.show()
        self.count_label.setText("0 项")

    def add_card(self, card_data):
        card = TimelineCard(card_data, self.tone)
        card.clicked.connect(self.card_clicked.emit)
        self.empty_state.hide()
        self.card_layout.insertWidget(self.card_layout.count() - 1, card)
        self.card_count += 1
        self.count_label.setText(f"{self.card_count} 项")

    def apply_font_scale(self, scale):
        self.count_label.setStyleSheet(
            f"background: rgba(255,255,255,0.72); color: {'#b7791f' if self.tone == 'amber' else '#315f8d'};"
            f"border: 1px solid #d7e2ed; border-radius: 11px; padding: 4px 10px;"
            f"font-size: {scale_px(11, scale)}px; font-weight: 700;"
        )


class KanbanWidget(QWidget):
    card_clicked = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.init_ui()

    def init_ui(self):
        self._apply_styles()

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        content = QWidget()
        content.setObjectName("KanbanContainer")
        content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(16)
        self.main_layout = main_layout

        toolbar = QFrame()
        toolbar.setObjectName("ToolbarPanel")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(18, 16, 18, 16)
        toolbar_layout.setSpacing(14)
        self.toolbar_layout = toolbar_layout

        self.toolbar_note = QLabel("仅展示当前需要推进闭环的问题项。")
        self.toolbar_note.setObjectName("HintText")

        search_row = QHBoxLayout()
        search_row.setSpacing(12)
        self.search_row = search_row
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索产品代号、名称、批次、型号、图号")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.search_input.textChanged.connect(self.load_data)
        self.btn_refresh = QPushButton("刷新看板")
        self.btn_refresh.setObjectName("GhostButton")
        self.btn_refresh.setMinimumSize(112, 42)
        self.btn_refresh.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btn_refresh.clicked.connect(self.load_data)
        search_row.addWidget(self.search_input)
        search_row.addWidget(self.btn_refresh)
        toolbar_layout.addWidget(self.toolbar_note)
        toolbar_layout.addStretch()
        toolbar_layout.addLayout(search_row, 2)
        main_layout.addWidget(toolbar)

        stats = QHBoxLayout()
        stats.setSpacing(14)
        self.stats_layout = stats
        self.missing_stat = self._create_stat_card("缺失更改", "#b7791f")
        self.pending_stat = self._create_stat_card("待落实", "#315f8d")
        self.overdue_stat = self._create_stat_card("超 7 天未处理", "#c05621")
        stats.addWidget(self.missing_stat)
        stats.addWidget(self.pending_stat)
        stats.addWidget(self.overdue_stat)
        main_layout.addLayout(stats)

        lanes = QHBoxLayout()
        lanes.setSpacing(18)
        self.lanes_layout = lanes
        self.missing_lane = TimelineLane("缺失更改轨", "缺少核心更改单据或图样关联信息。", "amber")
        self.pending_lane = TimelineLane("待落实轨", "更改已形成，但落实闭环还未完成。", "blue")
        self.missing_lane.setMinimumWidth(380)
        self.pending_lane.setMinimumWidth(380)
        self.missing_lane.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.pending_lane.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.missing_lane.card_clicked.connect(self.card_clicked.emit)
        self.pending_lane.card_clicked.connect(self.card_clicked.emit)
        lanes.addWidget(self.missing_lane)
        lanes.addWidget(self.pending_lane)
        main_layout.addLayout(lanes)

        content.setLayout(main_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidget(content)
        root_layout.addWidget(scroll)

        self.content_widget = content
        self._responsive_mode = None
        self.load_data()
        self._update_responsive_layout()

    def _apply_styles(self):
        self.setStyleSheet(
            f"""
            QWidget#KanbanContainer {{
                background: transparent;
            }}
            QLineEdit {{
                min-height: 42px;
                border-radius: 12px;
                border: 1px solid #d8e2ee;
                background: #ffffff;
                padding: 0 14px;
            }}
            QLineEdit:focus {{
                border-color: #7ea6d8;
            }}
            QFrame#SectionCard {{
                background: #ffffff;
                border: 1px solid #dbe4ee;
                border-radius: 16px;
            }}
            QLabel#StatTitle {{
                color: {THEME['text_muted']};
                font-size: 12px;
                font-weight: 700;
            }}
            QLabel#StatValue {{
                color: {THEME['text']};
                font-size: 28px;
                font-weight: 700;
            }}
            QLabel#StatHint {{
                color: {THEME['text_muted']};
                font-size: 12px;
            }}
            """
        )

    def _create_stat_card(self, title, accent):
        card = QFrame()
        card.setObjectName("SectionCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(6)
        title_label = QLabel(title)
        title_label.setObjectName("StatTitle")
        value_label = QLabel("0")
        value_label.setObjectName("StatValue")
        value_label.setStyleSheet(
            f"color: {accent}; font-size: {scale_px(24)}px; font-weight: 700;"
        )
        hint_label = QLabel("当前异常项目")
        hint_label.setObjectName("StatHint")
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(hint_label)
        card.value_label = value_label
        card.hint_label = hint_label
        return card

    def apply_font_scale(self, scale):
        self.load_data()
        self._update_responsive_layout()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_responsive_layout()

    def load_data(self):
        self.missing_lane.clear_cards()
        self.pending_lane.clear_cards()

        query_sql = """
            SELECT p.*,
                ts.id AS tech_status_id,
                ts.created_at AS tech_status_created_at,
                ts.drawing_number, ts.drawing_version, ts.software_version, ts.firmware_version,
                ts.req_baseline, ts.icd_version, ts.bom_version, ts.pcb_version,
                ts.test_status, ts.qual_status, ts.change_order, ts.change_description
            FROM product p
            LEFT JOIN tech_status ts ON ts.id = (
                SELECT id FROM tech_status
                WHERE product_id = p.id
                ORDER BY created_at DESC
                LIMIT 1
            )
            WHERE p.status != 'inactive' OR p.lifecycle_state = 'obsolete'
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(query_sql)
        products = [dict(row) for row in cursor.fetchall()]
        conn.close()

        status_map = {}
        if products:
            product_ids = [p["id"] for p in products]
            placeholders = ",".join("?" for _ in product_ids)
            status_sql = f"""
                SELECT *
                FROM tech_status
                WHERE product_id IN ({placeholders})
                ORDER BY created_at DESC
            """
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(status_sql, product_ids)
            for row in cursor.fetchall():
                item = dict(row)
                status_map.setdefault(item["product_id"], []).append(item)
            conn.close()

        keyword = self.search_input.text().strip().lower() if hasattr(self, "search_input") else ""
        missing_cards = []
        pending_cards = []

        for product in products:
            if keyword and not self._matches_search(product, keyword):
                continue
            issue = self._build_issue(product, status_map.get(product["id"], []))
            if not issue:
                continue
            if issue["issue_type"] == "missing_change":
                missing_cards.append(issue)
            elif issue["issue_type"] == "not_implemented":
                pending_cards.append(issue)

        missing_cards.sort(key=lambda x: x["delay_days"], reverse=True)
        pending_cards.sort(key=lambda x: x["delay_days"], reverse=True)

        for item in missing_cards:
            self.missing_lane.add_card(item)
        for item in pending_cards:
            self.pending_lane.add_card(item)

        overdue_count = sum(1 for item in missing_cards + pending_cards if item["delay_days"] > 7)
        self.missing_stat.value_label.setText(str(len(missing_cards)))
        self.pending_stat.value_label.setText(str(len(pending_cards)))
        self.overdue_stat.value_label.setText(str(overdue_count))

        self.missing_stat.hint_label.setText("待补单号 / 图样关联")
        self.pending_stat.hint_label.setText("待落实 / 未闭环")
        self.overdue_stat.hint_label.setText("拖延超过 7 天")

    def _matches_search(self, data, keyword):
        fields = [
            data.get("product_code", ""),
            data.get("product_name", ""),
            data.get("batch_number", ""),
            data.get("model", ""),
            data.get("drawing_number", ""),
        ]
        blob = " ".join(str(v) for v in fields if v)
        return keyword in blob.lower()

    def _extract_labeled_value(self, text, label):
        if not text:
            return ""
        for part in str(text).split(";"):
            part = part.strip()
            if part.startswith(f"{label}:"):
                return part[len(label) + 1:].strip()
        return ""

    def _is_effective(self, value):
        if not value:
            return False
        return str(value).strip() not in {"——", "--", "-", "—"}

    def _parse_date(self, text):
        if not text:
            return None
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(str(text), fmt)
            except Exception:
                continue
        return None

    def _extract_owner(self, change_desc):
        return self._extract_labeled_value(change_desc, "更改人") or "未填写"

    def _build_prefill_payload(self, row):
        if not row:
            return {}

        change_order = row.get("change_order", "")
        change_desc = row.get("change_description", "")

        return {
            "stage": self._extract_labeled_value(change_desc, "所属阶段"),
            "coord_order": self._extract_labeled_value(change_order, "协调单号"),
            "suggestion_order": self._extract_labeled_value(change_order, "更改建议单号"),
            "main_change_order": self._extract_labeled_value(
                change_order, "更改单号/技术通知单号/工艺更改单号"
            ),
            "change_reason": self._extract_labeled_value(change_desc, "更改理由"),
            "suggestion_drawing": self._extract_labeled_value(
                change_desc, "更改建议单涉及图样/文件"
            ),
            "change_drawing": self._extract_labeled_value(change_desc, "涉及更改图样"),
            "change_type": self._extract_labeled_value(change_desc, "更改类别"),
            "change_cause": self._extract_labeled_value(change_desc, "更改原因"),
            "change_owner": self._extract_labeled_value(change_desc, "更改人"),
            "handle_opinion": self._extract_labeled_value(change_desc, "处理意见"),
            "need_impl_product": self._extract_labeled_value(change_desc, "需落实产品编号"),
            "impl_status": self._extract_labeled_value(change_desc, "已落实情况"),
            "not_impl_product": self._extract_labeled_value(change_desc, "未落实产品编号"),
            "process_impl_status": self._extract_labeled_value(
                change_desc, "工艺更改落实情况"
            ),
            "remark": self._extract_labeled_value(change_desc, "备注"),
            "effective_date": row.get("effective_date", ""),
        }

    def _build_issue(self, product, rows):
        if not rows:
            return None

        latest_row = rows[0]
        missing_fields = set()
        pending_fields = set()
        issue_type = None
        reference_row = latest_row

        for row in rows:
            change_order = row.get("change_order", "")
            change_desc = row.get("change_description", "")
            suggestion_order = self._extract_labeled_value(change_order, "更改建议单号")
            main_doc = self._extract_labeled_value(change_order, "更改单号/技术通知单号/工艺更改单号")
            suggestion_drawing = self._extract_labeled_value(change_desc, "更改建议单涉及图样/文件")
            implement_status = self._extract_labeled_value(change_desc, "已落实情况")
            need_impl = self._extract_labeled_value(change_desc, "需落实产品编号")
            process_impl = self._extract_labeled_value(change_desc, "工艺更改落实情况")

            row_missing = []
            if self._is_effective(suggestion_order):
                if not self._is_effective(main_doc):
                    row_missing.append("缺更改单号")
                if not self._is_effective(suggestion_drawing):
                    row_missing.append("缺涉及图样")

            if row_missing:
                issue_type = "missing_change"
                missing_fields.update(row_missing)
                reference_row = row
                break

            if self._is_effective(main_doc):
                if (self._is_effective(need_impl) and implement_status.strip() != "已落实") or (
                    self._is_effective(process_impl) and process_impl.strip() != "已落实"
                ):
                    issue_type = "not_implemented"
                    if self._is_effective(need_impl):
                        pending_fields.add("待落实")
                    if self._is_effective(process_impl) and process_impl.strip() != "已落实":
                        pending_fields.add("工艺未落实")
                    reference_row = row
                    break

        if not issue_type:
            return None

        ref_date = self._parse_date(reference_row.get("created_at")) or self._parse_date(product.get("created_at"))
        delay_days = max((datetime.now() - ref_date).days, 0) if ref_date else 0
        timeline_text = ref_date.strftime("%m-%d %H:%M") if ref_date else "时间未知"

        if issue_type == "missing_change":
            badges = list(missing_fields) or ["缺失更改"]
            summary = "需要补齐更改单据、阶段或图样关联信息，避免后续落实链路断开。"
            action_text = "去补录变更"
        else:
            badges = list(pending_fields) or ["待落实"]
            summary = "变更已形成，但落实状态尚未闭环，建议优先补充落实情况和闭环结果。"
            action_text = "去补录结果"

        prefill = self._build_prefill_payload(reference_row)

        return {
            "id": product["id"],
            "product_code": product.get("product_code", ""),
            "product_name": product.get("product_name", ""),
            "issue_type": issue_type,
            "badges": badges,
            "summary": summary,
            "owner": self._extract_owner(reference_row.get("change_description", "")),
            "delay_days": delay_days,
            "delay_text": f"{delay_days} 天未闭环" if delay_days > 0 else "今日新增",
            "timeline_text": f"最近异常时间 {timeline_text}",
            "action_text": action_text,
            "prefill": prefill,
        }

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

    def _update_responsive_layout(self):
        width = self.width()
        if width >= 1400:
            mode = "wide"
        elif width >= 1050:
            mode = "medium"
        else:
            mode = "compact"

        if mode == self._responsive_mode:
            return

        self._responsive_mode = mode

        self._clear_layout(self.toolbar_layout)
        self._clear_layout(self.stats_layout)
        self._clear_layout(self.lanes_layout)
        self._clear_layout(self.search_row)

        if mode == "compact":
            self.search_row.setDirection(QVBoxLayout.TopToBottom)
            self.search_row.setSpacing(10)
            self.search_row.addWidget(self.search_input)
            self.search_row.addWidget(self.btn_refresh, 0, Qt.AlignLeft)
            self.toolbar_layout.setDirection(QVBoxLayout.TopToBottom)
            self.toolbar_layout.setSpacing(10)
            self.toolbar_layout.addWidget(self.toolbar_note)
            self.toolbar_layout.addLayout(self.search_row)

            self.stats_layout.setDirection(QVBoxLayout.TopToBottom)
            self.stats_layout.setSpacing(12)
            self.stats_layout.addWidget(self.missing_stat)
            self.stats_layout.addWidget(self.pending_stat)
            self.stats_layout.addWidget(self.overdue_stat)

            self.lanes_layout.setDirection(QVBoxLayout.TopToBottom)
            self.lanes_layout.setSpacing(14)
            self.missing_lane.setMinimumWidth(0)
            self.pending_lane.setMinimumWidth(0)
            self.lanes_layout.addWidget(self.missing_lane)
            self.lanes_layout.addWidget(self.pending_lane)
        else:
            self.search_row.setDirection(QHBoxLayout.LeftToRight)
            self.search_row.setSpacing(12)
            self.search_row.addWidget(self.search_input, 1)
            self.search_row.addWidget(self.btn_refresh)
            self.toolbar_layout.setDirection(QHBoxLayout.LeftToRight)
            self.toolbar_layout.setSpacing(14)
            self.toolbar_layout.addWidget(self.toolbar_note)
            self.toolbar_layout.addStretch()
            self.toolbar_layout.addLayout(self.search_row, 2)

            self.stats_layout.setDirection(QHBoxLayout.LeftToRight)
            self.stats_layout.setSpacing(14)
            self.stats_layout.addWidget(self.missing_stat)
            self.stats_layout.addWidget(self.pending_stat)
            self.stats_layout.addWidget(self.overdue_stat)

            self.lanes_layout.setDirection(QHBoxLayout.LeftToRight)
            self.lanes_layout.setSpacing(18)
            self.missing_lane.setMinimumWidth(320 if mode == "medium" else 380)
            self.pending_lane.setMinimumWidth(320 if mode == "medium" else 380)
            self.lanes_layout.addWidget(self.missing_lane)
            self.lanes_layout.addWidget(self.pending_lane)
