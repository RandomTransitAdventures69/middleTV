import json
from pathlib import Path
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView
from apps.base_app import BaseApp


class App(BaseApp):
    def __init__(self):
        super().__init__("Flight Tracker - MiddleTV")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.browser = QWebEngineView()
        layout.addWidget(self.browser)
        # Load optional location config; ADS-B map uses public web view.
        self.load_location()
        self.browser.setUrl(QUrl("https://globe.adsb.lol/"))

    def load_location(self):
        config = Path(__file__).resolve().parent.parent.parent / "config" / "location.json"
        if not config.exists():
            return None
        try:
            with open(config, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return None

    def handle_back(self):
        if self.browser.history().canGoBack():
            self.browser.back()
            return True
        return super().handle_back()
