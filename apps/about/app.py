from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout
from apps.base_app import BaseApp


class App(BaseApp):
    def __init__(self):
        super().__init__("About - MiddleTV")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(80, 64, 80, 64)
        layout.setSpacing(18)
        layout.addStretch()
        title = QLabel("middleTV OS")
        title.setStyleSheet("font-size: 52px; font-weight: 700;")
        title.setAlignment(Qt.AlignCenter)
        version = QLabel("Version 0.1 (developer build)")
        version.setObjectName("muted")
        version.setAlignment(Qt.AlignCenter)
        desc = QLabel(
            "A fullscreen, TV-oriented launcher and system experience built with Python and PySide6.\n"
            "Navigate with keyboard arrows/Enter/Escape, remote Back, or a controller where supported."
        )
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        desc.setStyleSheet("font-size: 22px;")
        back = QPushButton("Back to Home")
        back.setFixedWidth(280)
        back.clicked.connect(self.close)
        for w in (title, version, desc):
            layout.addWidget(w)
        layout.addSpacing(18)
        layout.addWidget(back, alignment=Qt.AlignCenter)
        layout.addStretch()
