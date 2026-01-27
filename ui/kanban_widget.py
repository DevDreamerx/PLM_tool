from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel,
                             QScrollArea, QFrame, QApplication, QPushButton,
                             QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, QMimeData
from PyQt5.QtGui import QDrag, QPixmap, QColor
from db.database import DatabaseManager
from ui.theme import THEME
from utils.excel_importer import ExcelImporter

def rgba_color(hex_color, alpha):
    color = QColor(hex_color)
    return f"rgba({color.red()}, {color.green()}, {color.blue()}, {alpha})"

def darker_color(hex_color, factor=160):
    color = QColor(hex_color)
    return color.darker(factor).name()

class KanbanCard(QFrame):
    """看板卡片 - 高仿 Teambition 风格"""
    
    clicked = pyqtSignal(int)
    
    def __init__(self, data, state_color="#e07a5f"):
        super().__init__()
        self.data = data
        self.state_color = state_color
        self._drag_start_pos = None
        
        # 基础样式
        self.setMinimumWidth(240)
        self.setStyleSheet(f"""
            KanbanCard {{
                background-color: {THEME['bg_panel']};
                border: 1px solid {THEME['border']};
                border-radius: 12px;
                border-top: 3px solid {self.state_color};
            }}
            KanbanCard:hover {{
                border-color: {self.state_color};
            }}
            QLabel {{ border: none; background: transparent; color: {THEME['text']}; }}
        """)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)
        
        # 1. 标题区
        title_lbl = QLabel(f"{self.data.get('product_code', '')}")
        title_lbl.setStyleSheet(f"color: {THEME['text_muted']}; font-size: 13px; font-weight: 700;")
        layout.addWidget(title_lbl)
        
        content_lbl = QLabel(self.data.get('product_name', '无名称'))
        content_lbl.setWordWrap(True)
        content_lbl.setStyleSheet(
            f"color: {THEME['text']}; font-size: 16px; font-weight: 700; line-height: 1.4;"
        )
        layout.addWidget(content_lbl)
        
        # 2. 标签区
        tags_layout = QHBoxLayout()
        tags_layout.setSpacing(6)
        
        # 状态标签
        state_name = self.data.get("issue_label", "缺失更改")
        state_icon = "●"
        state_bg = rgba_color(self.state_color, 0.12)
        state_text = darker_color(self.state_color)
        if self.data.get("issue_type") == "not_implemented":
            state_name = self.data.get("issue_label", "未落实")
            state_icon = "●"
            state_bg = rgba_color(self.state_color, 0.12)
            state_text = darker_color(self.state_color)
        
        tag = QLabel(f"{state_icon} {state_name}")
        tag.setStyleSheet(f"""
            background-color: {state_bg}; color: {state_text};
            padding: 3px 8px; border-radius: 6px; font-size: 11px; font-weight: 600;
        """)
        tag.setMinimumHeight(20)
        tags_layout.addWidget(tag)
        tags_layout.addStretch()
        
        # 模拟头像
        avatar = QLabel("👤")
        avatar.setStyleSheet(f"font-size: 13px; color: {THEME['text_muted']};")
        tags_layout.addWidget(avatar)
        
        layout.addLayout(tags_layout)
        
        # 3. 分割线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"background-color: {THEME['border']}; border: none; height: 1px;")
        layout.addWidget(line)
        
        # 4. 底部信息
        footer = QHBoxLayout()
        footer.setSpacing(10)
        
        created_at = str(self.data.get('created_at', ''))[:10]
        ver = self.data.get('drawing_version', 'V1.0')
        
        l1 = QLabel(f"创建: {created_at}")
        l1.setStyleSheet(f"color: {THEME['text_muted']}; font-size: 11px;")
        l2 = QLabel(f"版本 {ver}")
        l2.setStyleSheet(f"color: {THEME['accent']}; font-size: 11px; font-weight: 600;")
        
        footer.addWidget(l1)
        footer.addStretch()
        footer.addWidget(l2)
        layout.addLayout(footer)

        # 5. 缺失提示
        missing = self.data.get("missing_fields", [])
        if missing:
            prefix = self.data.get("missing_prefix", "缺失")
            missing_label = QLabel(f"{prefix}: " + " / ".join(missing))
            missing_label.setWordWrap(True)
            missing_label.setStyleSheet(
                f"color: {THEME['danger']}; font-size: 11px; font-weight: 600;"
            )
            layout.addWidget(missing_label)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_start_pos = event.pos()
            
    def mouseMoveEvent(self, event):
        if not self._drag_start_pos:
            return
            
        if (event.pos() - self._drag_start_pos).manhattanLength() < QApplication.startDragDistance():
            return
            
        drag = QDrag(self)
        mime = QMimeData()
        mime.setText(str(self.data['id']))
        drag.setMimeData(mime)
        self.setStyleSheet(
            f"background-color: {THEME['bg_panel']}; border: 1px dashed {THEME['border']}; "
            f"border-top: 3px solid {self.state_color};"
        )
        
        pixmap = QPixmap(self.size())
        self.render(pixmap)
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos())
        
        drag.exec_(Qt.MoveAction)
        self._drag_start_pos = None # Reset
        
        # 恢复样式? 需要一种机制，或者在 load_data 时重置
        
    def mouseReleaseEvent(self, event):
        if self._drag_start_pos:
            # If we released without dragging, it's a click
            self.clicked.emit(self.data['id'])
            self._drag_start_pos = None

class KanbanColumn(QWidget):
    """看板列"""
    
    card_clicked = pyqtSignal(int)
    
    def __init__(self, title, state_key, color="#e07a5f", allow_drop=False):
        super().__init__()
        # ... (rest of init)
        self.title = title
        self.state_key = state_key
        self.color = color
        self.col_bg = rgba_color(self.color, 0.06)
        self.col_header_bg = rgba_color(self.color, 0.12)
        self.col_badge_bg = rgba_color(self.color, 0.18)
        self.allow_drop = allow_drop
        self.setAcceptDrops(allow_drop)
        self.init_ui()
        
    def init_ui(self):
        # ... (same as before)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setStyleSheet(
            f"background-color: {self.col_bg}; border: 1px solid {THEME['border']}; border-radius: 12px;"
        )
        
        # 列头
        header = QWidget()
        header.setStyleSheet(
            f"background-color: {self.color}; border-top-left-radius: 12px; border-top-right-radius: 12px;"
        )
        header.setFixedHeight(4)
        layout.addWidget(header)
        
        title_box = QWidget()
        title_box.setStyleSheet(
            f"background-color: {self.col_header_bg}; border-bottom: 1px solid {THEME['border']};"
        )
        tb_layout = QHBoxLayout(title_box)
        tb_layout.setContentsMargins(16, 12, 16, 12)
        
        lbl_title = QLabel(self.title)
        lbl_title.setStyleSheet(f"font-weight: 600; font-size: 14px; color: {THEME['text']};")
        self.lbl_count = QLabel("0")
        self.lbl_count.setStyleSheet(
            f"""
            background: {self.col_badge_bg};
            border-radius: 10px;
            padding: 2px 8px;
            font-size: 11px;
            color: {self.color};
            font-weight: 600;
        """
        )
        
        tb_layout.addWidget(lbl_title)
        tb_layout.addWidget(self.lbl_count)
        tb_layout.addStretch()
        layout.addWidget(title_box)
        
        # 卡片区域
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.card_container = QWidget()
        self.card_container.setStyleSheet("background: transparent;")
        self.card_layout = QVBoxLayout(self.card_container)
        self.card_layout.setContentsMargins(12, 12, 12, 12)
        self.card_layout.setSpacing(12)
        self.card_layout.addStretch()
        
        self.scroll.setWidget(self.card_container)
        layout.addWidget(self.scroll)

    def add_card(self, card_data):
        card = KanbanCard(card_data, self.color)
        card.clicked.connect(self.card_clicked.emit) # Forward signal
        # 插入到 stretch 之前
        count = self.card_layout.count()
        self.card_layout.insertWidget(count - 1, card)
        self.update_count()

    def clear_cards(self):
        # 保留最后一个 stretch item
        while self.card_layout.count() > 1:
            item = self.card_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.update_count()

    def update_count(self):
        # 减去 stretch
        count = self.card_layout.count() - 1
        self.lbl_count.setText(str(count))

    def dragEnterEvent(self, event):
        if not self.allow_drop:
            event.ignore()
            return
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if not self.allow_drop:
            event.ignore()
            return
        card_id = int(event.mimeData().text())
        event.accept()

class KanbanWidget(QWidget):
    """看板主视图"""
    
    card_clicked = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.importer = ExcelImporter()
        self.setStyleSheet(f"background-color: {THEME['bg_app']};")
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(12)

        # 看板列布局容器
        board_container = QWidget()
        board_container.setStyleSheet(f"background-color: {THEME['bg_app']};")
        board_layout = QHBoxLayout(board_container)
        board_layout.setContentsMargins(16, 18, 16, 16)
        board_layout.setSpacing(16)
        
        self.col_missing_change = KanbanColumn("缺失更改", "missing_change", THEME["warning"])
        self.col_not_implemented = KanbanColumn("未落实", "not_implemented", THEME["danger"])
        
        # 连接信号
        for col in [self.col_missing_change, self.col_not_implemented]:
            col.card_clicked.connect(self.card_clicked.emit) # Forward to Widget
            board_layout.addWidget(col)
            
        main_layout.addWidget(board_container)
        
        # 加载数据
        self.load_data()

    def load_data(self):
        # 清空现有卡片
        self.col_missing_change.clear_cards()
        self.col_not_implemented.clear_cards()
        
        # 获取最新技术状态并筛选缺失项
        query_sql = """
            SELECT p.*,
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
        
        for p in products:
            issue = self._classify_issue(p)
            if not issue:
                continue
            if issue == "missing_change":
                p["issue_type"] = "missing_change"
                p["issue_label"] = "缺失更改"
                p["missing_prefix"] = "缺失"
                p["missing_fields"] = ["涉及更改图样"]
                self.col_missing_change.add_card(p)
            elif issue == "not_implemented":
                p["issue_type"] = "not_implemented"
                p["issue_label"] = "未落实"
                p["missing_prefix"] = "未落实"
                p["missing_fields"] = ["已落实情况"]
                self.col_not_implemented.add_card(p)

    def _extract_labeled_value(self, text, label):
        if not text:
            return ""
        for part in text.split(";"):
            part = part.strip()
            if not part:
                continue
            if part.startswith(f"{label}:"):
                return part[len(label) + 1:].strip()
        return ""

    def _is_effective(self, value):
        if not value:
            return False
        return value.strip() not in {"——", "--", "-", "—"}

    def _classify_issue(self, data):
        change_order = data.get("change_order", "")
        change_desc = data.get("change_description", "")
        doc_no = self._extract_labeled_value(change_order, "更改单号/技术通知单号/工艺更改单号")
        change_drawing = self._extract_labeled_value(change_desc, "涉及更改图样")
        implement_status = self._extract_labeled_value(change_desc, "已落实情况")
        if not self._is_effective(doc_no):
            return None
        if not self._is_effective(change_drawing):
            return "missing_change"
        if not self._is_effective(implement_status) or implement_status.strip() != "已落实":
            return "not_implemented"
        return None

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
        self.load_data()
