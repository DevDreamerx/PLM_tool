# -*- coding: utf-8 -*-
import sys
import os
import traceback
from datetime import datetime

# 确保能找到 ui 和 db 模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, PYQT_VERSION_STR, QT_VERSION_STR
from ui.main_window import MainWindow
from ui.theme import app_stylesheet, set_font_scale
from utils.backup import BackupManager

def log_startup(message):
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "startup.log")
    with open(log_path, "a", encoding="utf-8") as handle:
        handle.write(message + "\n")

def resource_path(relative_path: str) -> str:
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def main():
    os.environ.setdefault("QT_OPENGL", "software")
    QApplication.setAttribute(Qt.AA_UseSoftwareOpenGL, True)
    app = QApplication(sys.argv)
    
    # 设置全局样式
    app.setStyle("Fusion")

    font_scale = BackupManager().config.get("ui_font_scale", 1.0)
    set_font_scale(font_scale)
    app.setStyleSheet(app_stylesheet(font_scale))

    app_icon_path = resource_path("app.ico")
    if os.path.exists(app_icon_path):
        app.setWindowIcon(QIcon(app_icon_path))

    log_startup(
        f"[{datetime.now().isoformat()}] PyQt5={PYQT_VERSION_STR} Qt={QT_VERSION_STR} "
        f"QT_OPENGL={os.environ.get('QT_OPENGL')}"
    )
    
    try:
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception:
        log_startup("Unhandled exception:\n" + traceback.format_exc())
        raise

if __name__ == "__main__":
    main()
