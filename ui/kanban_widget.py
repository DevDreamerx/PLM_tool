from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
                             QScrollArea, QFrame, QSizePolicy, QApplication, QPushButton)
from PyQt5.QtCore import Qt, pyqtSignal, QMimeData, QPoint
from PyQt5.QtGui import QDrag, QPixmap, QPainter, QColor
from db.database import DatabaseManager

class KanbanCard(QFrame):
    """看板卡片 - 高仿 Teambition 风格"""
    
    clicked = pyqtSignal(int)
    
    def __init__(self, data, state_color="#1890FF"):
        super().__init__()
        self.data = data
        self.state_color = state_color
        self._drag_start_pos = None
        
        # 基础样式
        self.setFixedWidth(260) # 固定宽度以保持列整齐
        self.setStyleSheet(f"""
            KanbanCard {{
                background-color: #ffffff;
                border: 1px solid #dcdfe6;
                border-radius: 6px;
                border-top: 3px solid {self.state_color};
            }}
            KanbanCard:hover {{
                border-color: #3370ff;
            }}
            QLabel {{ border: none; background: transparent; color: #262626; }}
        """)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(8)
        
        # 1. 标题区
        title_lbl = QLabel(f"{self.data.get('product_code', '')}")
        title_lbl.setStyleSheet("color: #8c8c8c; font-size: 11px; font-weight: bold;")
        layout.addWidget(title_lbl)
        
        content_lbl = QLabel(self.data.get('product_name', '无名称'))
        content_lbl.setWordWrap(True)
        content_lbl.setStyleSheet("color: #262626; font-size: 13px; font-weight: bold; line-height: 1.4;")
        layout.addWidget(content_lbl)
        
        # 2. 标签区
        tags_layout = QHBoxLayout()
        tags_layout.setSpacing(6)
        
        # 状态标签
        state_name = "进行中"
        state_icon = "🕒"
        state_bg = "#e6f7ff"
        state_text = "#1890ff"
        
        lf_state = str(self.data.get('lifecycle_state', 'draft'))
        if 'draft' in lf_state:
            state_name = "待办"
            state_icon = "📝"
            state_bg = "#f5f5f5"
            state_text = "#8c8c8c"
        elif 'review' in lf_state:
            state_name = "审核"
            state_icon = "👀"
            state_bg = "#fff7e6"
            state_text = "#fa8c16"
        elif 'released' in lf_state:
            state_name = "发布"
            state_icon = "✅"
            state_bg = "#f6ffed"
            state_text = "#52c41a"
        
        tag = QLabel(f"{state_icon} {state_name}")
        tag.setStyleSheet(f"""
            background-color: {state_bg}; color: {state_text}; 
            padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;
        """)
        tags_layout.addWidget(tag)
        tags_layout.addStretch()
        
        # 模拟头像
        avatar = QLabel("👤")
        avatar.setStyleSheet("font-size: 14px; color: #bfbfbf;")
        tags_layout.addWidget(avatar)
        
        layout.addLayout(tags_layout)
        
        # 3. 分割线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #f0f0f0; border: none; height: 1px;")
        layout.addWidget(line)
        
        # 4. 底部信息
        footer = QHBoxLayout()
        footer.setSpacing(10)
        
        created_at = str(self.data.get('created_at', ''))[:10]
        ver = self.data.get('drawing_version', 'V1.0')
        
        l1 = QLabel(f"📅 {created_at}")
        l1.setStyleSheet("color: #bfbfbf; font-size: 11px;")
        l2 = QLabel(f"v{ver}")
        l2.setStyleSheet("color: #3370ff; font-size: 11px; font-weight: bold;")
        
        footer.addWidget(l1)
        footer.addStretch()
        footer.addWidget(l2)
        layout.addLayout(footer)

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
        self.setStyleSheet(f"background-color: #f0f0f0; border: 1px dashed #999; border-top: 3px solid {self.state_color};")
        
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
    
    def __init__(self, title, state_key, color="#1890FF"):
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
        header.setStyleSheet(f"background-color: {self.color}; border-top-left-radius: 4px; border-top-right-radius: 4px;")
        header.setFixedHeight(3)
        layout.addWidget(header)
        
        title_box = QWidget()
        title_box.setStyleSheet("background-color: #f5f7fa; border-bottom: 1px solid #dcdfe6;")
        tb_layout = QHBoxLayout(title_box)
        tb_layout.setContentsMargins(15, 12, 15, 12)
        
        lbl_title = QLabel(self.title)
        lbl_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #1a1a1a;")
        self.lbl_count = QLabel("0")
        self.lbl_count.setStyleSheet("""
            background: rgba(0,0,0,0.06); 
            border-radius: 10px; 
            padding: 2px 8px; 
            font-size: 11px; 
            color: #8c8c8c;
            font-weight: bold;
        """)
        
        tb_layout.addWidget(lbl_title)
        tb_layout.addWidget(self.lbl_count)
        tb_layout.addStretch()
        layout.addWidget(title_box)
        
        # 卡片区域
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("QScrollArea { border: none; background-color: #f5f7fa; }")
        
        self.card_container = QWidget()
        self.card_container.setStyleSheet("background-color: #f5f7fa; border-right: 1px solid #dcdfe6;")
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
        self.setStyleSheet("background-color: #ffffff;")
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 顶部工具栏
        toolbar = QWidget()
        toolbar.setFixedHeight(60)
        toolbar.setStyleSheet("background-color: #ffffff; border-bottom: 1px solid #dcdfe6;")
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(20, 0, 20, 0)
        
        title = QLabel("项目任务看板")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1a1a1a; border: none;")
        tb_layout.addWidget(title)
        tb_layout.addStretch()
        
        btn_refresh = QPushButton("刷新数据")
        btn_refresh.setFixedSize(80, 32)
        btn_refresh.setStyleSheet("""
            QPushButton { 
                background-color: #ffffff; border: 1px solid #dcdfe6; 
                border-radius: 4px; color: #606266; font-size: 12px;
            }
            QPushButton:hover { border-color: #3370ff; color: #3370ff; background-color: #f5f7fa; }
        """)
        btn_refresh.clicked.connect(self.load_data)
        tb_layout.addWidget(btn_refresh)
        main_layout.addWidget(toolbar)
        
        # 看板列布局容器
        board_container = QWidget()
        board_container.setStyleSheet("background-color: #ffffff;")
        board_layout = QHBoxLayout(board_container)
        board_layout.setContentsMargins(20, 20, 20, 20)
        board_layout.setSpacing(20)
        
        self.col_draft = KanbanColumn("待办 / 草稿", "draft", "#FAAD14")
        self.col_review = KanbanColumn("审核中", "review", "#1890FF")
        self.col_released = KanbanColumn("已发布", "released", "#52C41A")
        self.col_obsolete = KanbanColumn("已废弃", "obsolete", "#F5222D")
        
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
        
        # 获取所有数据 (使用 V2.0 兼容的查询)
        query_sql = """
            SELECT p.*, ts.drawing_version 
            FROM product p 
            LEFT JOIN tech_status ts ON p.id = ts.product_id 
            WHERE p.status != 'inactive' OR p.lifecycle_state = 'obsolete'
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(query_sql)
        products = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        for p in products:
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
