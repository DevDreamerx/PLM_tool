# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGroupBox, QCheckBox, QSpinBox,
                             QLineEdit, QFileDialog, QMessageBox, QFormLayout, QListWidget)
from PyQt5.QtCore import Qt
from utils.backup import BackupManager
import os

class SettingsWidget(QWidget):
    """系统设置界面"""
    
    def __init__(self):
        super().__init__()
        self.backup_manager = BackupManager()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # 1. 备份设置组
        backup_group = QGroupBox("备份设置")
        backup_layout = QFormLayout()
        
        # 自动备份开关
        self.auto_backup_check = QCheckBox("程序退出时自动备份")
        self.auto_backup_check.setChecked(self.backup_manager.config.get('auto_backup', True))
        self.auto_backup_check.stateChanged.connect(self.save_settings)
        
        # 备份目录
        backup_dir_layout = QHBoxLayout()
        self.backup_dir_edit = QLineEdit(self.backup_manager.config.get('backup_dir', './backups'))
        self.backup_dir_edit.setReadOnly(True)
        btn_browse = QPushButton("浏览...")
        btn_browse.clicked.connect(self.select_backup_dir)
        backup_dir_layout.addWidget(self.backup_dir_edit)
        backup_dir_layout.addWidget(btn_browse)
        
        # 保留天数
        self.keep_days_spin = QSpinBox()
        self.keep_days_spin.setRange(1, 30)
        self.keep_days_spin.setValue(self.backup_manager.config.get('backup_keep_days', 7))
        self.keep_days_spin.setSuffix(" 天")
        self.keep_days_spin.valueChanged.connect(self.save_settings)
        
        backup_layout.addRow("", self.auto_backup_check)
        backup_layout.addRow("备份目录:", backup_dir_layout)
        backup_layout.addRow("保留天数:", self.keep_days_spin)
        
        backup_group.setLayout(backup_layout)
        main_layout.addWidget(backup_group)
        
        # 2. 备份操作组
        operations_group = QGroupBox("备份操作")
        operations_layout = QVBoxLayout()
        
        btn_layout = QHBoxLayout()
        
        self.btn_backup_now = QPushButton("立即备份")
        self.btn_backup_now.setFixedSize(120, 40)
        self.btn_backup_now.setStyleSheet("background-color: #52C41A; color: white; font-weight: bold; border-radius: 4px;")
        self.btn_backup_now.clicked.connect(self.backup_now)
        
        self.btn_restore = QPushButton("恢复备份")
        self.btn_restore.setFixedSize(120, 40)
        self.btn_restore.setStyleSheet("background-color: #FAAD14; color: white; font-weight: bold; border-radius: 4px;")
        self.btn_restore.clicked.connect(self.restore_backup)
        
        btn_layout.addWidget(self.btn_backup_now)
        btn_layout.addWidget(self.btn_restore)
        btn_layout.addStretch()
        
        operations_layout.addLayout(btn_layout)
        
        # 备份列表
        self.backup_list = QListWidget()
        self.backup_list.setMaximumHeight(200)
        operations_layout.addWidget(QLabel("现有备份:"))
        operations_layout.addWidget(self.backup_list)
        
        operations_group.setLayout(operations_layout)
        main_layout.addWidget(operations_group)
        
        # 3. 关于信息
        about_group = QGroupBox("关于")
        about_layout = QVBoxLayout()
        about_layout.addWidget(QLabel("技术状态管理助手 V1.0"))
        about_layout.addWidget(QLabel("© 2026 技术状态管理系统"))
        about_group.setLayout(about_layout)
        main_layout.addWidget(about_group)
        
        main_layout.addStretch()
        self.setLayout(main_layout)
        
        # 加载备份列表
        self.refresh_backup_list()

    def save_settings(self):
        """保存设置"""
        config = {
            'auto_backup': self.auto_backup_check.isChecked(),
            'backup_dir': self.backup_dir_edit.text(),
            'backup_keep_days': self.keep_days_spin.value(),
            'db_path': self.backup_manager.config.get('db_path', 'tsm_data.db')
        }
        self.backup_manager.save_config(config)

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
        for backup in backups:
            size_mb = backup['size'] / (1024 * 1024)
            item_text = f"{backup['filename']} ({size_mb:.2f} MB) - {backup['mtime'].strftime('%Y-%m-%d %H:%M:%S')}"
            self.backup_list.addItem(item_text)
