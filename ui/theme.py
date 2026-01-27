# -*- coding: utf-8 -*-

THEME = {
    "bg_app": "#f2f5f8",        #应用程序主背景色
    "bg_panel": "#ffffff",      #内容面板背景色
    "bg_nav": "#0b1220",        #导航栏背景色
    "bg_nav_active": "#162236", #导航栏激活项背景色
    "border": "#e1e6ee",        #通用边框色
    "text": "#0f172a",          #主要文本色
    "text_muted": "#64748b",    #次要文本色
    "text_nav": "#cbd5e1",      #导航栏文本色
    "accent": "#2563eb",        #主强调色
    "accent_dark": "#1d4ed8",   #强调色-深
    "accent_soft": "#dbeafe",   #强调色-浅
    "success": "#16a34a",       #成功色
    "warning": "#f59e0b",       #警告色
    "danger": "#ef4444",        #危险色
}


def app_stylesheet():
    """Return the global stylesheet for the application."""
    palette = THEME

    return f"""
        QMainWindow {{
            background-color: {palette['bg_app']};
        }}
        QWidget {{
            font-family: "Source Han Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
            font-size: 13px;
            color: {palette['text']};
        }}
        #NavFrame {{
            background-color: {palette['bg_nav']};
        }}
        #NavTitle {{
            color: #ffffff;     
            font-size: 16px;
            font-weight: 600;
        }}
        #NavSubtitle {{
            color: {palette['text_nav']};
            font-size: 11px;
        }}
        #NavList {{
            border: none;
            background: transparent;
        }}
        #NavList::item {{
            color: {palette['text_nav']};
            padding: 10px 12px;
            margin: 4px 6px;
            border-radius: 8px;
        }}
        #NavList::item:hover {{
            background: rgba(255, 255, 255, 0.08);
        }}
        #NavList::item:selected {{
            background: {palette['bg_nav_active']};
            color: #ffffff;     
            border-left: 3px solid {palette['accent']};
        }}
        #ContentFrame {{
            background-color: {palette['bg_app']};
        }}
        #HeaderFrame {{
            background-color: {palette['bg_panel']};
            border: 1px solid {palette['border']};
            border-radius: 12px;
        }}
        #HeaderTitle {{
            font-size: 18px;
            font-weight: 600;
        }}
        QLabel#PageTitle {{
            font-size: 20px;
            font-weight: 600;
            color: {palette['text']};
        }}
        QGroupBox {{
            border: 1px solid {palette['border']};
            border-radius: 12px;
            margin-top: 12px;
            padding: 12px;
            background-color: {palette['bg_panel']};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 6px;
            color: {palette['text_muted']};
            font-weight: 600;
        }}
        QLineEdit {{
            background-color: {palette['bg_panel']};
            border: 1px solid {palette['border']};
            border-radius: 8px;
            padding: 7px 10px;
        }}
        QLineEdit:focus {{
            border-color: {palette['accent']};
        }}
        QTextEdit {{
            background-color: {palette['bg_panel']};
            border: 1px solid {palette['border']};
            border-radius: 8px;
            padding: 7px 10px;
        }}
        QComboBox, QDateEdit {{
            background-color: {palette['bg_panel']};
            border: 1px solid {palette['border']};
            border-radius: 8px;
            padding: 5px 10px;
        }}
        QSpinBox {{
            background-color: {palette['bg_panel']};
            border: 1px solid {palette['border']};
            border-radius: 8px;
            padding: 5px 10px;
        }}
        QPushButton {{
            background-color: {palette['accent']};
            color: #ffffff;
            border: none;
            border-radius: 8px;
            padding: 7px 16px;
        }}
        QPushButton:hover {{
            background-color: {palette['accent_dark']};
        }}
        QPushButton:disabled {{
            background-color: #cfc8bf;
            color: #ffffff;
        }}
        QPushButton#GhostButton {{
            background: transparent;
            color: {palette['accent']};
            border: 1px solid {palette['accent']};
        }}
        QPushButton#GhostButton:hover {{
            background: {palette['accent_soft']};
            color: {palette['accent_dark']};
        }}
        QPushButton#SuccessButton {{
            background: {palette['success']};
            color: #ffffff;
        }}
        QPushButton#WarningButton {{
            background: {palette['warning']};
            color: #3a2c16;
        }}
        QPushButton#DangerButton {{
            background: {palette['danger']};
            color: #ffffff;
        }}
        QTableWidget {{
            background-color: {palette['bg_panel']};
            border: 1px solid {palette['border']};
            border-radius: 8px;
            gridline-color: #eef2f6;
        }}
        QHeaderView::section {{
            background: #f8fafc;
            padding: 7px 8px;
            border: none;
            border-bottom: 1px solid {palette['border']};
            color: {palette['text_muted']};
            font-weight: 600;
        }}
        QTreeWidget {{
            background-color: #ffffff;
            border: 1px solid {palette['border']};
            border-radius: 8px;
        }}
        QListWidget {{
            background-color: {palette['bg_panel']};
            border: 1px solid {palette['border']};
            border-radius: 8px;
            padding: 4px;
        }}
        QListWidget::item {{
            padding: 6px 8px;
            margin: 2px 4px;
            border-radius: 6px;
        }}
        QListWidget::item:selected {{
            background: {palette['accent_soft']};
            color: {palette['text']};
        }}
        QTabWidget::pane {{
            border: 1px solid {palette['border']};
            border-radius: 8px;
            top: -1px;
            background: {palette['bg_panel']};
        }}
        QTabBar::tab {{
            background: #f8fafc;
            padding: 7px 12px;
            border: 1px solid {palette['border']};
            border-bottom: none;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            margin-right: 4px;
            color: {palette['text_muted']};
        }}
        QTabBar::tab:selected {{
            background: {palette['bg_panel']};
            color: {palette['text']};
        }}
        QStatusBar {{
            background: {palette['bg_panel']};
            border-top: 1px solid {palette['border']};
            color: {palette['text_muted']};
        }}
        QScrollBar:vertical {{
            border: none;
            background: #f1f5f9;
            width: 6px;
            margin: 0px;
        }}
        QScrollBar::handle:vertical {{
            background: #cbd5e1;
            min-height: 20px;
            border-radius: 3px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: #94a3b8;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QScrollBar:horizontal {{
            border: none;
            background: #f1f5f9;
            height: 6px;
            margin: 0px;
        }}
        QScrollBar::handle:horizontal {{
            background: #cbd5e1;
            min-width: 20px;
            border-radius: 3px;
        }}
    """
