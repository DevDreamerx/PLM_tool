# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, QFrame,
                             QHBoxLayout)
from PyQt5.QtCore import Qt, pyqtSignal, QSize

class GlobalRail(QWidget):
    """一级导航栏 (侧边图标栏)"""
    
    # 信号: 发送选中的模块索引
    module_changed = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.setFixedWidth(64)
        self.setObjectName("GlobalRail") # 设置对象名以便用更具体的选择器
        self.setAutoFillBackground(True) # 确保背景可被填充
        # 使用具体选择器覆盖全局样式
        self.setStyleSheet("""
            #GlobalRail {
                background-color: #151825;
            }
        """)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 10)
        layout.setSpacing(10)
        
        # Logo 区域 - 极简白块图标
        logo_container = QWidget()
        logo_container.setFixedHeight(50)
        logo_l = QVBoxLayout(logo_container)
        logo_l.setAlignment(Qt.AlignCenter)
        
        logo = QLabel("TSM")
        logo.setFixedSize(36, 24)
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet("""
            color: #ffffff; 
            font-weight: bold; 
            font-size: 14px;
            letter-spacing: 1px;
        """)
        logo_l.addWidget(logo)
        layout.addWidget(logo_container)
        
        # 导航组件
        self.items = [
            ("工作台", "H"), # Home
            ("项目", "P"),   # Project
            ("排期", "S"),   # Schedule
            ("报表", "R"),   # Report
            ("设置", "●")    # Dot/Setting
        ]
        
        self.buttons = []
        
        for i, (label, text) in enumerate(self.items):
            btn = QPushButton(text)
            btn.setFixedSize(64, 44) # 宽度占满侧边栏
            btn.setToolTip(label)
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            
            # 样式升级: 侧边线条指示器
            btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    background-color: transparent;
                    color: #d7d9e8;
                    font-family: Arial, sans-serif;
                    font-size: 15px; 
                    font-weight: bold;
                    border-left: 3px solid transparent;
                }
                QPushButton:hover {
                    color: #ffffff;
                    background-color: rgba(255, 255, 255, 0.12);
                }
                QPushButton:checked {
                    border-left: 3px solid #9fd1ff;
                    color: #ffffff;
                    background-color: rgba(255, 255, 255, 0.18);
                }
            """)
            btn.clicked.connect(lambda checked, idx=i: self.module_changed.emit(idx))
            
            layout.addWidget(btn)
            self.buttons.append(btn)
            
        layout.addStretch()
        
        # 底部帮助按钮 - 弱化
        btn_help = QPushButton("?")
        btn_help.setFixedSize(32, 32)
        btn_help.setStyleSheet("""
            border: 1px solid #3c4252; 
            border-radius: 16px; 
            color: #cfd2e6; 
            font-weight: bold;
            background-color: transparent;
        """)
        
        h_layout = QHBoxLayout()
        h_layout.setAlignment(Qt.AlignCenter)
        h_layout.addWidget(btn_help)
        help_wrapper = QWidget()
        help_wrapper.setLayout(h_layout)
        
        layout.addWidget(help_wrapper)

        # 默认选中第一个
        if self.buttons:
            self.buttons[0].setChecked(True)
