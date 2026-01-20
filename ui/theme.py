# -*- coding: utf-8 -*-

THEME = {
    "bg_app": "#f5f1ea",
    "bg_panel": "#ffffff",
    "bg_nav": "#1f242c",
    "bg_nav_active": "#2b323d",
    "border": "#d7d0c6",
    "text": "#22262f",
    "text_muted": "#606572",
    "text_nav": "#cfd6e4",
    "accent": "#e07a5f",
    "accent_dark": "#c9654d",
    "accent_soft": "#f6d9d1",
    "success": "#4c956c",
    "warning": "#e9c46a",
    "danger": "#d1495b",
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
            background-color: {palette['bg_panel']};
        }}
        #HeaderFrame {{
            background-color: {palette['bg_panel']};
            border-bottom: 1px solid {palette['border']};
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
            border-radius: 10px;
            margin-top: 12px;
            padding: 12px;
            background-color: #ffffff;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 6px;
            color: {palette['text_muted']};
            font-weight: 600;
        }}
        QLineEdit {{
            background-color: #ffffff;
            border: 1px solid {palette['border']};
            border-radius: 6px;
            padding: 6px 10px;
        }}
        QLineEdit:focus {{
            border-color: {palette['accent']};
        }}
        QTextEdit {{
            background-color: #ffffff;
            border: 1px solid {palette['border']};
            border-radius: 6px;
            padding: 6px 10px;
        }}
        QComboBox, QDateEdit {{
            background-color: #ffffff;
            border: 1px solid {palette['border']};
            border-radius: 6px;
            padding: 4px 8px;
        }}
        QSpinBox {{
            background-color: #ffffff;
            border: 1px solid {palette['border']};
            border-radius: 6px;
            padding: 4px 8px;
        }}
        QPushButton {{
            background-color: {palette['accent']};
            color: #ffffff;
            border: none;
            border-radius: 6px;
            padding: 6px 14px;
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
            background-color: #ffffff;
            border: 1px solid {palette['border']};
            border-radius: 8px;
            gridline-color: #e6e0d6;
        }}
        QHeaderView::section {{
            background: #f6f2ea;
            padding: 6px 8px;
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
            background-color: #ffffff;
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
            background: #ffffff;
        }}
        QTabBar::tab {{
            background: #f6f2ea;
            padding: 6px 12px;
            border: 1px solid {palette['border']};
            border-bottom: none;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            margin-right: 4px;
            color: {palette['text_muted']};
        }}
        QTabBar::tab:selected {{
            background: #ffffff;
            color: {palette['text']};
        }}
        QStatusBar {{
            background: #ffffff;
            border-top: 1px solid {palette['border']};
            color: {palette['text_muted']};
        }}
        QScrollBar:vertical {{
            border: none;
            background: #f0ece5;
            width: 6px;
            margin: 0px;
        }}
        QScrollBar::handle:vertical {{
            background: #cbbfb2;
            min-height: 20px;
            border-radius: 3px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: #b7ab9e;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QScrollBar:horizontal {{
            border: none;
            background: #f0ece5;
            height: 6px;
            margin: 0px;
        }}
        QScrollBar::handle:horizontal {{
            background: #cbbfb2;
            min-width: 20px;
            border-radius: 3px;
        }}
    """
