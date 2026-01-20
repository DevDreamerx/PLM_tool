# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGroupBox, QListWidget, QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
import platform
from ui.theme import THEME

# 解决中文乱码问题
def setup_matplotlib_fonts():
    # 针对不同系统提供备选字体列表
    if platform.system() == "Windows":
        fonts = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
    elif platform.system() == "Darwin": # macOS
        fonts = ['Arial Unicode MS', 'PingFang HK', 'Heiti TC', 'sans-serif']
    else: # Linux/Other
        fonts = ['DejaVu Sans', 'Bitstream Vera Sans', 'sans-serif']
    
    matplotlib.rcParams['font.sans-serif'] = fonts
    matplotlib.rcParams['axes.unicode_minus'] = False # 解决负号显示问题

setup_matplotlib_fonts()
matplotlib.use('Qt5Agg')

from db.database import DatabaseManager
from utils.excel_exporter import ExcelExporter

class ReportWidget(QWidget):
    """数据报表界面"""
    
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # 1. 统计卡片区
        stats_layout = QHBoxLayout()
        
        self.total_card = self.create_stat_card("总记录数", "0", THEME["accent"])
        self.active_card = self.create_stat_card("正式记录", "0", THEME["success"])
        self.draft_card = self.create_stat_card("草稿数", "0", THEME["warning"])
        
        stats_layout.addWidget(self.total_card)
        stats_layout.addWidget(self.active_card)
        stats_layout.addWidget(self.draft_card)
        
        main_layout.addLayout(stats_layout)
        
        # 2. 图表区
        chart_group = QGroupBox("产品型号分布")
        chart_layout = QVBoxLayout()
        
        self.figure = Figure(figsize=(8, 4))
        self.figure.set_facecolor("#fffdf9")
        self.canvas = FigureCanvas(self.figure)
        chart_layout.addWidget(self.canvas)
        
        chart_group.setLayout(chart_layout)
        main_layout.addWidget(chart_group)
        
        # 3. 最近变更列表
        changes_group = QGroupBox("最近变更记录")
        changes_layout = QVBoxLayout()
        
        self.changes_list = QListWidget()
        self.changes_list.setMaximumHeight(200)
        changes_layout.addWidget(self.changes_list)
        
        changes_group.setLayout(changes_layout)
        main_layout.addWidget(changes_group)
        
        # 4. 导出按钮
        btn_layout = QHBoxLayout()
        self.btn_export = QPushButton("导出全部数据")
        self.btn_export.setFixedSize(150, 40)
        self.btn_export.setObjectName("SuccessButton")
        self.btn_export.clicked.connect(self.export_all_data)
        
        self.btn_refresh = QPushButton("刷新")
        self.btn_refresh.setFixedSize(100, 40)
        self.btn_refresh.setObjectName("GhostButton")
        self.btn_refresh.clicked.connect(self.refresh_data)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addWidget(self.btn_export)
        
        main_layout.addLayout(btn_layout)
        
        self.setLayout(main_layout)
        
        # 初始加载数据
        self.refresh_data()

    def create_stat_card(self, title, value, color):
        """创建统计卡片"""
        card = QGroupBox()
        card.setStyleSheet(f"""
            QGroupBox {{
                background-color: #fffdf9;
                border: 1px solid {color};
                border-radius: 12px;
                padding: 14px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-size: 14px; color: {THEME['text_muted']};")
        title_label.setAlignment(Qt.AlignCenter)
        
        value_label = QLabel(value)
        value_label.setObjectName("value")
        value_label.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {color};")
        value_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        card.setLayout(layout)
        return card

    def refresh_data(self):
        """刷新数据"""
        # 1. 更新统计卡片
        stats = self.db.get_statistics()
        self.total_card.findChild(QLabel, "value").setText(str(stats['total_count']))
        self.active_card.findChild(QLabel, "value").setText(str(stats['active_count']))
        self.draft_card.findChild(QLabel, "value").setText(str(stats['draft_count']))
        
        # 2. 更新图表
        self.update_chart()
        
        # 3. 更新最近变更（暂时显示提示）
        self.changes_list.clear()
        self.changes_list.addItem("变更记录功能开发中...")

    def update_chart(self):
        """更新图表"""
        distribution = self.db.get_model_distribution()
        
        if not distribution:
            return
        
        models = [item[0] for item in distribution]
        counts = [item[1] for item in distribution]
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        bars = ax.bar(models, counts, color=THEME["accent"], alpha=0.85)
        ax.set_xlabel('产品型号', fontsize=12)
        ax.set_ylabel('数量', fontsize=12)
        ax.set_title('产品型号分布', fontsize=14, fontweight='bold')
        
        # 在柱子上显示数值
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontsize=10)
        
        self.figure.tight_layout()
        self.canvas.draw()

    def export_all_data(self):
        """导出全部数据"""
        try:
            # 获取所有数据
            data = self.db.get_products_with_tech_status()
            
            if not data:
                QMessageBox.warning(self, "提示", "没有可导出的数据")
                return
            
            # 选择保存位置
            file_path, _ = QFileDialog.getSaveFileName(
                self, "保存Excel文件", "", "Excel Files (*.xlsx)"
            )
            
            if file_path:
                if not file_path.endswith('.xlsx'):
                    file_path += '.xlsx'
                
                # 导出
                import os
                output_dir = os.path.dirname(file_path)
                filename = os.path.basename(file_path)
                
                # 临时修改导出器以使用指定文件名
                from openpyxl import Workbook
                from openpyxl.styles import Font, Alignment, PatternFill
                
                wb = Workbook()
                ws = wb.active
                ws.title = "技术状态数据"
                
                headers = [
                    "ID", "产品代号", "产品名称", "批次编号", "所属型号",
                    "图号", "图纸版本", "软件版本", "固件版本", "硬件配置",
                    "需求基线", "接口基线", "BOM版本", "PCB版本", "硬件序列号",
                    "生产批次", "测试状态", "合格状态",
                    "更改单号", "更改内容", "生效日期", "状态", "创建时间"
                ]
                
                for col_num, header in enumerate(headers, 1):
                    cell = ws.cell(row=1, column=col_num, value=header)
                    cell.font = Font(bold=True, color="FFFFFF")
                    cell.fill = PatternFill(start_color="E07A5F", end_color="E07A5F", fill_type="solid")
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                
                for row_num, item in enumerate(data, 2):
                    ws.cell(row=row_num, column=1, value=item.get('id', ''))
                    ws.cell(row=row_num, column=2, value=item.get('product_code', ''))
                    ws.cell(row=row_num, column=3, value=item.get('product_name', ''))
                    ws.cell(row=row_num, column=4, value=item.get('batch_number', ''))
                    ws.cell(row=row_num, column=5, value=item.get('model', ''))
                    ws.cell(row=row_num, column=6, value=item.get('drawing_number', ''))
                    ws.cell(row=row_num, column=7, value=item.get('drawing_version', ''))
                    ws.cell(row=row_num, column=8, value=item.get('software_version', ''))
                    ws.cell(row=row_num, column=9, value=item.get('firmware_version', ''))
                    ws.cell(row=row_num, column=10, value=item.get('hardware_config', ''))
                    ws.cell(row=row_num, column=11, value=item.get('req_baseline', ''))
                    ws.cell(row=row_num, column=12, value=item.get('icd_version', ''))
                    ws.cell(row=row_num, column=13, value=item.get('bom_version', ''))
                    ws.cell(row=row_num, column=14, value=item.get('pcb_version', ''))
                    ws.cell(row=row_num, column=15, value=item.get('hw_serial', ''))
                    ws.cell(row=row_num, column=16, value=item.get('production_batch', ''))
                    ws.cell(row=row_num, column=17, value=item.get('test_status', ''))
                    ws.cell(row=row_num, column=18, value=item.get('qual_status', ''))
                    ws.cell(row=row_num, column=19, value=item.get('change_order', ''))
                    ws.cell(row=row_num, column=20, value=item.get('change_description', ''))
                    ws.cell(row=row_num, column=21, value=item.get('effective_date', ''))
                    status_text = "草稿" if item.get('status') == 'draft' else "正式"
                    ws.cell(row=row_num, column=22, value=status_text)
                    ws.cell(row=row_num, column=23, value=item.get('created_at', ''))
                
                for column in ws.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    ws.column_dimensions[column_letter].width = adjusted_width
                
                wb.save(file_path)
                
                QMessageBox.information(self, "成功", f"数据已导出到:\n{file_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"导出过程中发生错误:\n{str(e)}")
