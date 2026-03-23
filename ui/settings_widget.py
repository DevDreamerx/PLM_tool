# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QGroupBox, QCheckBox, QSpinBox,
                             QLineEdit, QFileDialog, QMessageBox,
                             QListWidget, QScrollArea, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal, QSignalBlocker
from utils.backup import BackupManager
from ui.theme import THEME

class SettingsWidget(QWidget):
    font_scale_changed = pyqtSignal(float)
    """系统设置界面"""
    
    def __init__(self):
        super().__init__()
        self.backup_manager = BackupManager()
        self.init_ui()

    def init_ui(self):
        self._apply_styles()

        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        content = QWidget()
        main_layout = QVBoxLayout(content)
        main_layout.setContentsMargins(24, 0, 24, 24)
        main_layout.setSpacing(18)

        ui_group = QGroupBox("界面设置")
        ui_group.setObjectName("SectionCard")
        ui_layout = QVBoxLayout()
        ui_layout.setContentsMargins(20, 18, 20, 18)
        ui_layout.setSpacing(12)
        ui_hint = QLabel("只保留少量全局显示项，避免设置页本身变成另一套复杂界面。")
        ui_hint.setObjectName("HintText")
        ui_hint.setWordWrap(True)
        ui_layout.addWidget(ui_hint)

        self.font_scale_spin = QSpinBox()
        self.font_scale_spin.setRange(80, 150)
        self.font_scale_spin.setSingleStep(10)
        self.font_scale_spin.setSuffix("%")
        self.font_scale_spin.setValue(int(round(self.backup_manager.config.get("ui_font_scale", 1.0) * 100)))
        self.font_scale_spin.valueChanged.connect(self.on_font_scale_changed)
        self.font_scale_spin.setFixedWidth(120)

        ui_layout.addWidget(
            self._create_setting_row(
                "字体缩放",
                "调整全局字号，让录入、查询和报表页在当前显示器上都更易读。",
                self.font_scale_spin,
            )
        )
        ui_group.setLayout(ui_layout)
        main_layout.addWidget(ui_group)
        
        backup_group = QGroupBox("备份设置")
        backup_group.setObjectName("SectionCard")
        backup_layout = QVBoxLayout()
        backup_layout.setContentsMargins(20, 18, 20, 18)
        backup_layout.setSpacing(12)
        backup_hint = QLabel("自动备份、目录和保留策略集中配置，日常只需要在这里维护。")
        backup_hint.setObjectName("HintText")
        backup_hint.setWordWrap(True)
        backup_layout.addWidget(backup_hint)
        
        self.auto_backup_check = QCheckBox("启用")
        self.auto_backup_check.setChecked(self.backup_manager.config.get('auto_backup', True))
        self.auto_backup_check.stateChanged.connect(self.save_settings)
        
        backup_dir_panel = QWidget()
        backup_dir_layout = QHBoxLayout(backup_dir_panel)
        backup_dir_layout.setContentsMargins(0, 0, 0, 0)
        backup_dir_layout.setSpacing(10)
        self.backup_dir_edit = QLineEdit(self.backup_manager.config.get('backup_dir', './backups'))
        self.backup_dir_edit.setReadOnly(True)
        btn_browse = QPushButton("选择目录")
        btn_browse.setObjectName("GhostButton")
        btn_browse.setMinimumWidth(112)
        btn_browse.clicked.connect(self.select_backup_dir)
        backup_dir_layout.addWidget(self.backup_dir_edit)
        backup_dir_layout.addWidget(btn_browse)
        
        self.keep_days_spin = QSpinBox()
        self.keep_days_spin.setRange(1, 30)
        self.keep_days_spin.setValue(self.backup_manager.config.get('backup_keep_days', 7))
        self.keep_days_spin.setSuffix(" 天")
        self.keep_days_spin.valueChanged.connect(self.save_settings)
        self.keep_days_spin.setFixedWidth(120)
        
        backup_layout.addWidget(
            self._create_setting_row(
                "退出时自动备份",
                "适合离线环境，关闭程序时自动留下一份可回退快照。",
                self.auto_backup_check,
            )
        )
        backup_layout.addWidget(
            self._create_setting_row(
                "备份目录",
                "统一指定备份文件位置，便于拷贝和归档。",
                backup_dir_panel,
            )
        )
        backup_layout.addWidget(
            self._create_setting_row(
                "保留天数",
                "按时间清理旧备份，避免目录越来越杂乱。",
                self.keep_days_spin,
            )
        )
        
        backup_group.setLayout(backup_layout)
        main_layout.addWidget(backup_group)
        
        operations_group = QGroupBox("备份与恢复")
        operations_group.setObjectName("SectionCard")
        operations_layout = QVBoxLayout()
        operations_layout.setContentsMargins(20, 18, 20, 18)
        operations_layout.setSpacing(14)

        operations_intro = QLabel("把常用备份和低频恢复拆开处理，默认优先保护当前数据。")
        operations_intro.setObjectName("HintText")
        operations_intro.setWordWrap(True)
        operations_layout.addWidget(operations_intro)
        
        backup_action_card = QFrame()
        backup_action_card.setObjectName("SettingRow")
        backup_action_layout = QHBoxLayout(backup_action_card)
        backup_action_layout.setContentsMargins(16, 14, 16, 14)
        backup_action_layout.setSpacing(12)

        backup_text = QVBoxLayout()
        backup_text.setSpacing(2)
        backup_title = QLabel("立即创建备份")
        backup_title.setObjectName("SettingLabel")
        backup_desc = QLabel("在导入、批量删除或调整前手动留档，最稳妥。")
        backup_desc.setObjectName("SettingDesc")
        backup_desc.setWordWrap(True)
        backup_text.addWidget(backup_title)
        backup_text.addWidget(backup_desc)
        
        self.btn_backup_now = QPushButton("立即备份")
        self.btn_backup_now.setMinimumSize(116, 40)
        self.btn_backup_now.setObjectName("PrimaryButton")
        self.btn_backup_now.clicked.connect(self.backup_now)
        backup_action_layout.addLayout(backup_text, 1)
        backup_action_layout.addWidget(self.btn_backup_now, 0, Qt.AlignRight | Qt.AlignVCenter)
        operations_layout.addWidget(backup_action_card)

        danger_group = QGroupBox("恢复与风险操作")
        danger_group.setObjectName("DangerSection")
        danger_layout = QVBoxLayout()
        danger_layout.setContentsMargins(18, 18, 18, 18)
        danger_layout.setSpacing(12)

        operation_hint = QLabel("恢复会直接覆盖当前数据库。只有在确认现有数据可以被替换时再执行。")
        operation_hint.setObjectName("DangerBanner")
        operation_hint.setWordWrap(True)
        danger_layout.addWidget(operation_hint)

        restore_row = QFrame()
        restore_row.setObjectName("DangerRow")
        restore_row_layout = QHBoxLayout(restore_row)
        restore_row_layout.setContentsMargins(16, 14, 16, 14)
        restore_row_layout.setSpacing(12)

        restore_text = QVBoxLayout()
        restore_text.setSpacing(2)
        restore_title = QLabel("从备份恢复")
        restore_title.setObjectName("SettingLabel")
        restore_desc = QLabel("用于故障回退或回到某个稳定时间点，执行后建议立即重启程序。")
        restore_desc.setObjectName("SettingDesc")
        restore_desc.setWordWrap(True)
        restore_text.addWidget(restore_title)
        restore_text.addWidget(restore_desc)
        
        self.btn_restore = QPushButton("恢复备份")
        self.btn_restore.setMinimumSize(116, 40)
        self.btn_restore.setObjectName("DangerButton")
        self.btn_restore.clicked.connect(self.restore_backup)
        restore_row_layout.addLayout(restore_text, 1)
        restore_row_layout.addWidget(self.btn_restore, 0, Qt.AlignRight | Qt.AlignVCenter)
        danger_layout.addWidget(restore_row)
        danger_group.setLayout(danger_layout)
        operations_layout.addWidget(danger_group)

        self.backup_list = QListWidget()
        self.backup_list.setMinimumHeight(220)
        backup_list_label = QLabel("现有备份")
        backup_list_label.setObjectName("HintText")
        operations_layout.addWidget(backup_list_label)
        operations_layout.addWidget(self.backup_list)
        
        operations_group.setLayout(operations_layout)
        main_layout.addWidget(operations_group)
        
        about_group = QGroupBox("关于")
        about_group.setObjectName("SoftCard")
        about_layout = QVBoxLayout()
        about_layout.setContentsMargins(20, 18, 20, 18)
        about_layout.setSpacing(6)
        about_layout.addWidget(self._create_about_line("产品", "技术状态管理助手 V1.0"))
        about_layout.addWidget(self._create_about_line("定位", "面向离线环境的技术状态录入、查询与追溯"))
        about_layout.addWidget(self._create_about_line("原则", "更稳、更清楚、先保护数据，再做风险操作"))
        about_group.setLayout(about_layout)
        main_layout.addWidget(about_group)
        
        main_layout.addStretch()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        scroll_area.setWidget(content)
        root_layout.addWidget(scroll_area)
        self.setLayout(root_layout)
        
        # 加载备份列表
        self.refresh_backup_list()

    def _apply_styles(self):
        self.setStyleSheet(
            f"""
            QGroupBox#SectionCard {{
                background: {THEME['bg_panel']};
                border: 1px solid {THEME['border']};
                border-radius: 16px;
                margin-top: 12px;
                padding: 8px 0 0 0;
            }}
            QGroupBox#SectionCard::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 18px;
                padding: 0 2px;
                color: {THEME['text_muted']};
                font-size: 13px;
                font-weight: 700;
                background: transparent;
            }}
            QFrame#SettingRow, QFrame#DangerRow {{
                background: {THEME['bg_panel_soft']};
                border: 1px solid {THEME['border_soft']};
                border-radius: 12px;
            }}
            QLabel#SettingLabel {{
                color: {THEME['text']};
                font-size: 14px;
                font-weight: 600;
            }}
            QLabel#SettingDesc {{
                color: {THEME['text_muted']};
                font-size: 12px;
            }}
            QGroupBox#DangerSection {{
                background: {THEME['danger_soft']};
                border: 1px solid #f6d3d7;
                border-radius: 16px;
                margin-top: 10px;
                padding: 6px 0 0 0;
            }}
            QGroupBox#DangerSection::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 14px;
                padding: 0 6px;
                color: #b42318;
                font-weight: 700;
                background: transparent;
            }}
            QLabel#DangerBanner {{
                color: #8f1d1d;
                background: #fff7f7;
                border: 1px solid #f3c7ce;
                border-radius: 12px;
                padding: 10px 14px;
                font-size: 12px;
                font-weight: 600;
            }}
            QGroupBox#SoftCard {{
                background: {THEME['bg_panel_soft']};
                border-color: {THEME['border_soft']};
            }}
            QCheckBox {{
                spacing: 8px;
                font-weight: 600;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 6px;
                border: 1px solid #cfd8e3;
                background: #ffffff;
            }}
            QCheckBox::indicator:checked {{
                background: {THEME['accent']};
                border-color: {THEME['accent']};
            }}
            QSpinBox {{
                min-width: 116px;
            }}
            QLineEdit[readOnly="true"] {{
                background: {THEME['bg_toolbar']};
                color: {THEME['text']};
            }}
            QListWidget {{
                padding: 8px;
                background: {THEME['bg_panel']};
                border: 1px solid {THEME['border']};
                border-radius: 14px;
            }}
            QListWidget::item {{
                padding: 10px 12px;
                margin: 2px 0;
                border-radius: 10px;
                border: 1px solid transparent;
            }}
            QListWidget::item:selected {{
                background: {THEME['accent_surface']};
                border-color: {THEME['accent_soft']};
                color: {THEME['text']};
            }}
            """
        )

    def _create_setting_row(self, title, desc, control):
        row = QFrame()
        row.setObjectName("SettingRow")
        layout = QHBoxLayout(row)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(12)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        title_label = QLabel(title)
        title_label.setObjectName("SettingLabel")
        desc_label = QLabel(desc)
        desc_label.setObjectName("SettingDesc")
        desc_label.setWordWrap(True)

        text_layout.addWidget(title_label)
        text_layout.addWidget(desc_label)

        layout.addLayout(text_layout, 1)
        layout.addWidget(control, 0, Qt.AlignRight | Qt.AlignVCenter)
        return row

    def _create_about_line(self, label, value):
        row = QLabel(f"{label}：{value}")
        row.setObjectName("HintText")
        row.setWordWrap(True)
        return row

    def save_settings(self):
        """保存设置"""
        config = {
            'auto_backup': self.auto_backup_check.isChecked(),
            'backup_dir': self.backup_dir_edit.text(),
            'backup_keep_days': self.keep_days_spin.value(),
            'db_path': self.backup_manager.config.get('db_path', 'tsm_data.db'),
            'ui_font_scale': self.font_scale_spin.value() / 100.0,
        }
        self.backup_manager.save_config(config)

    def on_font_scale_changed(self, _value):
        self.save_settings()
        self.font_scale_changed.emit(self.font_scale_spin.value() / 100.0)

    def set_font_scale(self, scale):
        with QSignalBlocker(self.font_scale_spin):
            self.font_scale_spin.setValue(int(round(float(scale) * 100)))

    def select_backup_dir(self):
        """选择备份目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择备份目录")
        if dir_path:
            self.backup_dir_edit.setText(dir_path)
            self.save_settings()

    def backup_now(self):
        """立即备份"""
        try:
            backup_path = self.backup_manager.create_backup()
            QMessageBox.information(self, "成功", f"备份已创建:\n{backup_path}")
            self.refresh_backup_list()
        except Exception as e:
            QMessageBox.critical(self, "备份失败", f"备份过程中发生错误:\n{str(e)}")

    def restore_backup(self):
        """恢复备份"""
        # 选择备份文件
        backup_dir = self.backup_manager.config.get('backup_dir', './backups')
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择备份文件", backup_dir, "Database Files (*.db)"
        )
        
        if file_path:
            reply = QMessageBox.question(
                self, '确认恢复', 
                '恢复备份将覆盖当前数据库！\n确定要继续吗？',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                try:
                    self.backup_manager.restore_backup(file_path)
                    QMessageBox.information(self, "成功", "数据库已恢复！\n请重启程序以加载新数据。")
                except Exception as e:
                    QMessageBox.critical(self, "恢复失败", f"恢复过程中发生错误:\n{str(e)}")

    def refresh_backup_list(self):
        """刷新备份列表"""
        self.backup_list.clear()
        backups = self.backup_manager.list_backups()
        if not backups:
            self.backup_list.addItem("暂无可用备份，创建后会显示在这里")
            self.backup_list.item(0).setFlags(Qt.NoItemFlags)
            return
        for backup in backups:
            size_mb = backup['size'] / (1024 * 1024)
            item_text = f"{backup['filename']} ({size_mb:.2f} MB) - {backup['mtime'].strftime('%Y-%m-%d %H:%M:%S')}"
            self.backup_list.addItem(item_text)
