from PySide6.QtGui import QColor

THEMES = {
    "modern": {
        "name": "Modern",
        "overlay": "rgba(8, 10, 16, 60)",
        "panel": "rgba(18, 20, 28, 188)",
        "panel_strong": "rgba(14, 16, 24, 228)",
        "tile": "rgba(18, 20, 28, 175)",
        "tile_hover": "rgba(34, 52, 78, 215)",
        "tile_focus": "rgba(28, 52, 86, 232)",
        "text": "#ffffff",
        "muted": "rgba(255,255,255,160)",
        "border": "rgba(255,255,255,48)",
        "focus": "rgba(90,190,255,255)",
        "focus_glow": "rgba(90,190,255,120)",
        "accent": "#3fa9ff",
        "font": "",
        "radius": 18,
    },
    "aero": {
        "name": "Aero",
        "overlay": "rgba(180, 220, 255, 28)",
        "panel": "rgba(225, 242, 255, 135)",
        "panel_strong": "rgba(235, 248, 255, 190)",
        "tile": "rgba(220, 240, 255, 118)",
        "tile_hover": "rgba(235, 248, 255, 165)",
        "tile_focus": "rgba(245, 252, 255, 195)",
        "text": "#0f2236",
        "muted": "rgba(15,34,54,165)",
        "border": "rgba(255,255,255,170)",
        "focus": "rgba(70,170,255,255)",
        "focus_glow": "rgba(120,210,255,130)",
        "accent": "#2a8cff",
        "font": "",
        "radius": 20,
    },
    "terminal": {
        "name": "Terminal",
        "overlay": "rgba(0, 0, 0, 165)",
        "panel": "rgba(0, 18, 0, 210)",
        "panel_strong": "rgba(0, 12, 0, 235)",
        "tile": "rgba(0, 24, 0, 188)",
        "tile_hover": "rgba(0, 48, 0, 215)",
        "tile_focus": "rgba(0, 58, 0, 235)",
        "text": "#78ff78",
        "muted": "rgba(120,255,120,150)",
        "border": "rgba(90,255,90,85)",
        "focus": "rgba(120,255,120,255)",
        "focus_glow": "rgba(120,255,120,90)",
        "accent": "#78ff78",
        "font": "Menlo, Consolas, 'DejaVu Sans Mono', monospace",
        "radius": 8,
    },
}


def get_theme(name):
    return THEMES.get((name or "modern").lower(), THEMES["modern"])


def qcolor(value):
    if isinstance(value, QColor):
        return value
    if isinstance(value, str) and value.startswith("rgba"):
        nums = value[value.find("(") + 1 : value.find(")")].split(",")
        return QColor(int(nums[0]), int(nums[1]), int(nums[2]), int(nums[3]))
    return QColor(value)


def app_stylesheet(theme_name):
    t = get_theme(theme_name)
    font = f"font-family: {t['font']};" if t["font"] else ""
    r = t["radius"]
    return f"""
    QWidget {{ background: transparent; color: {t['text']}; {font} }}
    QLabel {{ color: {t['text']}; background: transparent; {font} }}
    QLabel#muted, QLabel[muted="true"] {{ color: {t['muted']}; }}
    QFrame#panel, QWidget#panel {{
        background: {t['panel']};
        border: 1px solid {t['border']};
        border-radius: {r}px;
    }}
    QPushButton {{
        color: {t['text']};
        background: {t['tile']};
        border: 2px solid {t['border']};
        border-radius: {r}px;
        padding: 10px 18px;
        font-size: 18px;
        font-weight: 600;
        {font}
    }}
    QPushButton:hover {{ background: {t['tile_hover']}; border: 2px solid {t['focus']}; }}
    QPushButton:focus {{ background: {t['tile_focus']}; border: 3px solid {t['focus']}; outline: none; }}
    QPushButton:pressed {{ background: {t['tile_focus']}; }}
    QLineEdit, QTextEdit, QPlainTextEdit, QListWidget, QTreeView, QComboBox {{
        color: {t['text']};
        background: {t['panel_strong']};
        border: 2px solid {t['border']};
        border-radius: 12px;
        padding: 8px 12px;
        selection-background-color: {t['accent']};
        {font}
    }}
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QListWidget:focus, QTreeView:focus, QComboBox:focus {{
        border: 3px solid {t['focus']};
    }}
    QScrollBar:vertical {{ background: transparent; width: 12px; }}
    QScrollBar::handle:vertical {{ background: {t['border']}; border-radius: 6px; min-height: 30px; }}
    """
