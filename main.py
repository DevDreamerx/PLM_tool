# -*- coding: utf-8 -*-
import sys
import os

# 确保能找到 ui 和 db 模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from ui.main_window import MainWindow
from ui.theme import app_stylesheet

def resource_path(relative_path: str) -> str:
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def main():
    app = QApplication(sys.argv)
    
    # 设置全局样式
    app.setStyle("Fusion")
    app.setStyleSheet(app_stylesheet())

    app_icon_path = resource_path("app.ico")
    if os.path.exists(app_icon_path):
        app.setWindowIcon(QIcon(app_icon_path))
    
    window = MainWindow()
    if os.path.exists(app_icon_path):
        window.setWindowIcon(QIcon(app_icon_path))
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
