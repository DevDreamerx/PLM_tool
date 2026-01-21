from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel,
                             QScrollArea, QFrame, QApplication, QPushButton,
                             QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, QMimeData
from PyQt5.QtGui import QDrag, QPixmap
from db.database import DatabaseManager
from ui.theme import THEME
from utils.excel_importer import ExcelImporter

class KanbanCard(QFrame):
    """看板卡片 - 高仿 Teambition 风格"""
    
    clicked = pyqtSignal(int)
    
    def __init__(self, data, state_color="#e07a5f"):
        super().__init__()
        self.data = data
        self.state_color = state_color
        self._drag_start_pos = None
        
        # 基础样式
        self.setFixedWidth(260) # 固定宽度以保持列整齐
        self.setStyleSheet(f"""
            KanbanCard {{
                background-color: #fffdf9;
                border: 1px solid {THEME['border']};
                border-radius: 8px;
                border-top: 4px solid {self.state_color};
            }}
            KanbanCard:hover {{
                border-color: {THEME['accent']};
            }}
            QLabel {{ border: none; background: transparent; color: {THEME['text']}; }}
        """)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(8)
        
        # 1. 标题区
        title_lbl = QLabel(f"{self.data.get('product_code', '')}")
        title_lbl.setStyleSheet(f"color: {THEME['text_muted']}; font-size: 11px; font-weight: 600;")
        layout.addWidget(title_lbl)
        
        content_lbl = QLabel(self.data.get('product_name', '无名称'))
        content_lbl.setWordWrap(True)
        content_lbl.setStyleSheet("color: #1f2430; font-size: 13px; font-weight: 600; line-height: 1.4;")
        layout.addWidget(content_lbl)
        
        # 2. 标签区
        tags_layout = QHBoxLayout()
        tags_layout.setSpacing(6)
        
        # 状态标签
        state_name = "进行中"
        state_icon = "🕒"
        state_bg = "#f6ece3"
        state_text = "#7a6d5a"
        
        lf_state = str(self.data.get('lifecycle_state', 'draft'))
        if 'draft' in lf_state:
            state_name = "待办"
            state_icon = "📝"
            state_bg = "#eee6db"
            state_text = "#7a6d5a"
        elif 'review' in lf_state:
            state_name = "审核"
            state_icon = "👀"
            state_bg = "#fbe8d5"
            state_text = "#b46b2a"
        elif 'released' in lf_state:
            state_name = "发布"
            state_icon = "✅"
            state_bg = "#e6f2e9"
            state_text = "#2f6f4b"
        elif 'obsolete' in lf_state:
            state_name = "废弃"
            state_icon = "⛔"
            state_bg = "#f3e3e6"
            state_text = "#a24755"
        
        tag = QLabel(f"{state_icon} {state_name}")
        tag.setStyleSheet(f"""
            background-color: {state_bg}; color: {state_text}; 
            padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;
        """)
        tags_layout.addWidget(tag)
        tags_layout.addStretch()
        
        # 模拟头像
        avatar = QLabel("👤")
        avatar.setStyleSheet(f"font-size: 14px; color: {THEME['text_muted']};")
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
        
        l1 = QLabel(f"📅 {created_at}")
        l1.setStyleSheet(f"color: {THEME['text_muted']}; font-size: 11px;")
        l2 = QLabel(f"v{ver}")
        l2.setStyleSheet(f"color: {THEME['accent']}; font-size: 11px; font-weight: 600;")
        
        footer.addWidget(l1)
        footer.addStretch()
        footer.addWidget(l2)
        layout.addLayout(footer)

        # 5. 缺失提示
        missing = self.data.get("missing_fields", [])
        if missing:
            missing_label = QLabel("缺失: " + " / ".join(missing))
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
            f"background-color: #f0ede6; border: 1px dashed {THEME['border']}; "
            f"border-top: 4px solid {self.state_color};"
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
    
    # 信号: 卡片被放置 (card_id, new_state)
    card_dropped = pyqtSignal(int, str)
    card_clicked = pyqtSignal(int)
    
    def __init__(self, title, state_key, color="#e07a5f"):
        super().__init__()
        # ... (rest of init)
        self.title = title
        self.state_key = state_key
        self.color = color
        self.setAcceptDrops(True)
        self.init_ui()
        
    def init_ui(self):
        # ... (same as before)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 列头
        header = QWidget()
        header.setStyleSheet(
            f"background-color: {self.color}; border-top-left-radius: 6px; border-top-right-radius: 6px;"
        )
        header.setFixedHeight(3)
        layout.addWidget(header)
        
        title_box = QWidget()
        title_box.setStyleSheet(f"background-color: #fbf8f2; border-bottom: 1px solid {THEME['border']};")
        tb_layout = QHBoxLayout(title_box)
        tb_layout.setContentsMargins(15, 12, 15, 12)
        
        lbl_title = QLabel(self.title)
        lbl_title.setStyleSheet("font-weight: 600; font-size: 14px; color: #1f2430;")
        self.lbl_count = QLabel("0")
        self.lbl_count.setStyleSheet("""
            background: #ebe5dd;
            border-radius: 10px;
            padding: 2px 8px;
            font-size: 11px;
            color: #6b6f7a;
            font-weight: 600;
        """)
        
        tb_layout.addWidget(lbl_title)
        tb_layout.addWidget(self.lbl_count)
        tb_layout.addStretch()
        layout.addWidget(title_box)
        
        # 卡片区域
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("QScrollArea { border: none; background-color: #fbf8f2; }")
        
        self.card_container = QWidget()
        self.card_container.setStyleSheet(
            f"background-color: #fbf8f2; border-right: 1px solid {THEME['border']};"
        )
        self.card_layout = QVBoxLayout(self.card_container)
        self.card_layout.setContentsMargins(10, 10, 10, 10)
        self.card_layout.setSpacing(10)
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
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        card_id = int(event.mimeData().text())
        self.card_dropped.emit(card_id, self.state_key)
        event.accept()

class KanbanWidget(QWidget):
    """看板主视图"""
    
    card_clicked = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.importer = ExcelImporter()
        self.setStyleSheet("background-color: #ffffff;")
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 顶部工具栏
        toolbar = QWidget()
        toolbar.setFixedHeight(60)
        toolbar.setStyleSheet(f"background-color: #ffffff; border-bottom: 1px solid {THEME['border']};")
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(20, 0, 20, 0)
        
        title = QLabel("更改单缺失状态看板")
        title.setStyleSheet("font-size: 16px; font-weight: 600; color: #1f2430; border: none;")
        tb_layout.addWidget(title)
        tb_layout.addStretch()

        btn_import = QPushButton("导入Excel")
        btn_import.setFixedSize(96, 32)
        btn_import.setObjectName("GhostButton")
        btn_import.clicked.connect(self.import_excel)
        tb_layout.addWidget(btn_import)
        
        btn_refresh = QPushButton("刷新数据")
        btn_refresh.setFixedSize(80, 32)
        btn_refresh.setObjectName("GhostButton")
        btn_refresh.clicked.connect(self.load_data)
        tb_layout.addWidget(btn_refresh)
        main_layout.addWidget(toolbar)
        
        # 看板列布局容器
        board_container = QWidget()
        board_container.setStyleSheet("background-color: #ffffff;")
        board_layout = QHBoxLayout(board_container)
        board_layout.setContentsMargins(20, 20, 20, 20)
        board_layout.setSpacing(20)
        
        self.col_draft = KanbanColumn("待办 / 草稿", "draft", "#d1a54c")
        self.col_review = KanbanColumn("审核中", "review", "#3b6ea5")
        self.col_released = KanbanColumn("已发布", "released", THEME["success"])
        self.col_obsolete = KanbanColumn("已废弃", "obsolete", THEME["danger"])
        
        # 连接信号
        for col in [self.col_draft, self.col_review, self.col_released, self.col_obsolete]:
            col.card_dropped.connect(self.on_card_dropped)
            col.card_clicked.connect(self.card_clicked.emit) # Forward to Widget
            board_layout.addWidget(col)
            
        main_layout.addWidget(board_container)
        
        # 加载数据
        self.load_data()

    def load_data(self):
        # 清空现有卡片
        self.col_draft.clear_cards()
        self.col_review.clear_cards()
        self.col_released.clear_cards()
        self.col_obsolete.clear_cards()
        
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
            if not self._has_change_order(p):
                continue
            missing_fields = self._missing_fields(p)
            if not missing_fields:
                continue
            p["missing_fields"] = missing_fields
            state = p.get('lifecycle_state', 'draft')
            if state == 'draft':
                self.col_draft.add_card(p)
            elif state == 'review':
                self.col_review.add_card(p)
            elif state == 'released':
                self.col_released.add_card(p)
            elif state == 'obsolete':
                self.col_obsolete.add_card(p)

    def on_card_dropped(self, card_id, new_state):
        # 更新数据库状态
        self.db.update_lifecycle_state(card_id, new_state)
        # 记录变更日志
        tech_status = self.db.get_tech_status(card_id)
        if tech_status:
            self.db.insert_change_log(tech_status['id'], "lifecycle", f"看板拖拽更新状态为: {new_state}")
            
        # 重新加载
        self.load_data()

    def _has_change_order(self, data):
        return bool(data.get("change_order") or data.get("change_description"))

    def _missing_fields(self, data):
        required_fields = [
            ("drawing_number", "图号"),
            ("drawing_version", "图纸版本"),
            ("software_version", "软件版本"),
            ("firmware_version", "固件版本"),
            ("req_baseline", "需求基线"),
            ("icd_version", "接口基线"),
            ("bom_version", "BOM版本"),
            ("pcb_version", "PCB版本"),
            ("test_status", "测试状态"),
            ("qual_status", "合格状态"),
        ]
        missing = []
        for key, label in required_fields:
            value = data.get(key)
            if value is None or str(value).strip() == "":
                missing.append(label)
        return missing

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
