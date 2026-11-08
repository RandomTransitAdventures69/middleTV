from datetime import datetime
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QVBoxLayout, QLabel
from apps.base_app import BaseApp


class App(BaseApp):
    def __init__(self):
        super().__init__("Clock - MiddleTV")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 60, 60, 60)
        layout.addStretch()
        self.time = QLabel()
        self.time.setAlignment(Qt.AlignCenter)
        self.time.setStyleSheet("font-size: 120px; font-weight: 700;")
        self.date = QLabel()
        self.date.setAlignment(Qt.AlignCenter)
        self.date.setObjectName("muted")
        self.date.setStyleSheet("font-size: 34px;")
        layout.addWidget(self.time)
        layout.addWidget(self.date)
        layout.addStretch()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(1000)
        self.refresh()

    def refresh(self):
        now = datetime.now()
        self.time.setText(now.strftime("%H:%M:%S"))
        self.date.setText(now.strftime("%A, %B %d, %Y"))
