from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from core.config import load_config
from core.theme import app_stylesheet


class BaseApp(QWidget):
    is_middletv_root = True

    def __init__(self, title="MiddleTV App", fullscreen=True):
        super().__init__()
        self.setWindowTitle(title)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.apply_theme()
        if fullscreen:
            self.showFullScreen()

    def apply_theme(self):
        self.setStyleSheet(app_stylesheet(load_config().get("ui_theme", "modern")))

    def handle_back(self):
        # Apps override for internal navigation stacks. Default: close to home.
        self.close()
        return True
