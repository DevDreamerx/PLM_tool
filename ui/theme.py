# -*- coding: utf-8 -*-

THEME = {
    "bg_app": "#eff3f8",        #应用程序主背景色
    "bg_panel": "#ffffff",      #内容面板背景色
    "bg_panel_soft": "#f7f9fc", #弱化内容面板背景色
    "bg_panel_tint": "#f4f8ff", #轻强调面板背景色
    "bg_toolbar": "#f6f9fc",    #工具栏背景色
    "bg_nav": "#0b1220",        #导航栏背景色
    "bg_nav_active": "#162236", #导航栏激活项背景色
    "border": "#dbe4ee",        #通用边框色
    "border_soft": "#e5edf5",   #弱化边框色
    "border_strong": "#c7d5e4", #强调边框色
    "text": "#0f172a",          #主要文本色
    "text_muted": "#64748b",    #次要文本色
    "text_subtle": "#8a97a8",   #更弱文本色
    "text_nav": "#cbd5e1",      #导航栏文本色
    "accent": "#2f6fed",        #主强调色
    "accent_dark": "#2459cb",   #强调色-深
    "accent_soft": "#dfeaff",   #强调色-浅
    "accent_surface": "#eef4ff",#强调色-面
    "success": "#16a34a",       #成功色
    "success_soft": "#edf9f1",  #成功色-浅
    "warning": "#f59e0b",       #警告色
    "warning_soft": "#fff6e6",  #警告色-浅
    "danger": "#ef4444",        #危险色
    "danger_soft": "#fff1f2",   #危险色-浅
}


DEFAULT_FONT_SCALE = 1.0
MIN_FONT_SCALE = 0.8
MAX_FONT_SCALE = 1.5
_current_font_scale = DEFAULT_FONT_SCALE


def clamp_font_scale(scale):
    try:
        scale = float(scale)
    except Exception:
        scale = DEFAULT_FONT_SCALE
    return max(MIN_FONT_SCALE, min(MAX_FONT_SCALE, scale))


def set_font_scale(scale):
    global _current_font_scale
    _current_font_scale = clamp_font_scale(scale)
    return _current_font_scale


def get_font_scale():
    return _current_font_scale


def scale_px(px, scale=None):
    if scale is None:
        scale = get_font_scale()
    return max(1, int(round(int(px) * float(scale))))


def scale_pt(pt, scale=None):
    return scale_px(pt, scale)


def app_stylesheet(font_scale=None):
    """Return the global stylesheet for the application."""
    palette = THEME
    if font_scale is None:
        font_scale = get_font_scale()

    return f"""
        QMainWindow {{
            background-color: {palette['bg_app']};
        }}
        QWidget#Workspace {{
            background: transparent;
        }}
        QWidget {{
            font-family: "Source Han Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
            font-size: {scale_px(13, font_scale)}px;
            color: {palette['text']};
        }}
        #NavFrame {{
            background-color: {palette['bg_nav']};
        }}
        #NavTitle {{
            color: #ffffff;     
            font-size: {scale_px(16, font_scale)}px;
            font-weight: 600;
        }}
        #NavSubtitle {{
            color: {palette['text_nav']};
            font-size: {scale_px(11, font_scale)}px;
        }}
        #NavList {{
            border: none;
            background: transparent;
        }}
        #NavList::item {{
            color: {palette['text_nav']};
            padding: 11px 12px;
            margin: 4px 6px;
            border-radius: 10px;
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
            border-radius: 18px;
        }}
        #HeaderTitle {{
            font-size: {scale_px(20, font_scale)}px;
            font-weight: 700;
        }}
        #HeaderSummary {{
            color: {palette['text_muted']};
            font-size: {scale_px(12, font_scale)}px;
        }}
        QLabel#PageIntro {{
            color: {palette['text_muted']};
            font-size: {scale_px(14, font_scale)}px;
            padding: 0 4px 2px 4px;
        }}
        QLabel#HintText {{
            color: {palette['text_muted']};
            font-size: {scale_px(12, font_scale)}px;
        }}
        QLabel#SummaryBanner {{
            color: {palette['text']};
            background: {palette['accent_surface']};
            border: 1px solid {palette['accent_soft']};
            border-radius: 14px;
            padding: 12px 16px;
            font-size: {scale_px(13, font_scale)}px;
            font-weight: 600;
        }}
        QLabel#PageTitle {{
            font-size: {scale_px(20, font_scale)}px;
            font-weight: 700;
            color: {palette['text']};
        }}
        QGroupBox, QFrame#SectionCard, QFrame#SoftCard, QFrame#ToolbarPanel, QGroupBox#SectionCard, QGroupBox#SoftCard {{
            border: 1px solid {palette['border']};
            border-radius: 18px;
            margin-top: 12px;
            padding: 12px;
            background-color: {palette['bg_panel']};
        }}
        QFrame#SectionCard, QFrame#SoftCard, QFrame#ToolbarPanel, QGroupBox#SectionCard, QGroupBox#SoftCard {{
            margin-top: 0;
            padding: 0;
        }}
        QFrame#SoftCard, QGroupBox#SoftCard {{
            background: {palette['bg_panel_soft']};
            border-color: {palette['border_soft']};
        }}
        QFrame#ToolbarPanel {{
            background: {palette['bg_toolbar']};
            border-color: {palette['border_soft']};
        }}
        QGroupBox::title, QGroupBox#SectionCard::title, QGroupBox#SoftCard::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 14px;
            padding: 0 6px;
            color: {palette['text_muted']};
            font-weight: 600;
            background: {palette['bg_app']};
            border-radius: 8px;
        }}
        QLineEdit, QDateEdit, QComboBox, QSpinBox {{
            background-color: {palette['bg_panel']};
            border: 1px solid {palette['border']};
            border-radius: 12px;
            padding: 7px 12px;
            min-height: {scale_px(28, font_scale)}px;
        }}
        QLineEdit:focus, QTextEdit:focus, QDateEdit:focus, QComboBox:focus, QSpinBox:focus {{
            border-color: {palette['accent']};
            background-color: {palette['bg_panel_tint']};
        }}
        QTextEdit {{
            background-color: {palette['bg_panel']};
            border: 1px solid {palette['border']};
            border-radius: 14px;
            padding: 10px 12px;
        }}
        QPushButton {{
            background-color: {palette['accent']};
            color: #ffffff;
            border: none;
            border-radius: 12px;
            padding: 8px 16px;
            min-height: {scale_px(28, font_scale)}px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background-color: {palette['accent_dark']};
        }}
        QPushButton:disabled {{
            background-color: #dbe4ee;
            color: #94a3b8;
        }}
        QPushButton#GhostButton {{
            background: {palette['bg_panel']};
            color: {palette['text']};
            border: 1px solid {palette['border_strong']};
        }}
        QPushButton#GhostButton:hover {{
            background: {palette['bg_toolbar']};
            color: {palette['text']};
            border-color: #9fb6d1;
        }}
        QPushButton#PrimaryButton {{
            background: {palette['accent']};
            color: #ffffff;
            border: none;
            font-weight: 700;
        }}
        QPushButton#PrimaryButton:hover {{
            background: {palette['accent_dark']};
        }}
        QPushButton#SuccessButton {{
            background: {palette['success']};
            color: #ffffff;
        }}
        QPushButton#SuccessButton:hover {{
            background: #12823b;
        }}
        QPushButton#WarningButton {{
            background: {palette['warning_soft']};
            color: #7c4a03;
            border: 1px solid #f4d39a;
        }}
        QPushButton#WarningButton:hover {{
            background: #fde9be;
            color: #6b3f05;
        }}
        QPushButton#DangerButton {{
            background: {palette['danger']};
            color: #ffffff;
        }}
        QPushButton#DangerButton:hover {{
            background: #dc2626;
        }}
        QTableWidget {{
            background-color: {palette['bg_panel']};
            border: 1px solid {palette['border']};
            border-radius: 14px;
            gridline-color: #eef2f6;
        }}
        QHeaderView::section {{
            background: {palette['bg_toolbar']};
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
            border-radius: 14px;
            padding: 6px;
        }}
        QListWidget::item {{
            padding: 8px 10px;
            margin: 2px 4px;
            border-radius: 10px;
        }}
        QListWidget::item:selected {{
            background: {palette['accent_surface']};
            color: {palette['text']};
            border: 1px solid {palette['accent_soft']};
        }}
        QTabWidget::pane {{
            border: 1px solid {palette['border']};
            border-radius: 12px;
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
        QStatusBar QLabel {{
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
