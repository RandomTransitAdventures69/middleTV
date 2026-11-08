import json
import urllib.parse
import urllib.request
from pathlib import Path
from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QMessageBox, QTextBrowser, QLineEdit, QDialog, QDialogButtonBox
from PySide6.QtWebEngineWidgets import QWebEngineView
from apps.base_app import BaseApp
from core.config import CONFIG_DIR, load_config


class App(BaseApp):
    def __init__(self):
        super().__init__("Media Server - MiddleTV")
        self.stack_mode = "list"  # list, browser
        self.server = None
        self._build()
        self.load_server()

    def servers_data(self):
        path = CONFIG_DIR / "media_servers.json"
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {"servers": {}, "active_server": "", "primary_server": ""}
        data.setdefault("servers", {})
        data.setdefault("active_server", "")
        data.setdefault("primary_server", data.get("active_server", ""))
        return data

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(10)
        header = QHBoxLayout()
        self.title = QLabel("Media Server")
        self.title.setStyleSheet("font-size: 34px; font-weight: 700;")
        self.status = QLabel()
        self.status.setObjectName("muted")
        header.addWidget(self.title); header.addStretch(); header.addWidget(self.status)
        root.addLayout(header)

        self.info = QTextBrowser()
        self.info.setMaximumHeight(180)
        root.addWidget(self.info)

        controls = QHBoxLayout()
        self.open_btn = QPushButton("Open Server")
        self.open_btn.setMinimumHeight(50)
        self.open_btn.clicked.connect(self.open_server)
        self.settings_hint = QPushButton("Configure in Settings")
        self.settings_hint.setMinimumHeight(50)
        self.settings_hint.clicked.connect(self._show_config_hint)
        controls.addWidget(self.open_btn); controls.addWidget(self.settings_hint); controls.addStretch()
        root.addLayout(controls)

        self.browser = QWebEngineView()
        root.addWidget(self.browser, 1)
        self.browser.setHtml(self._placeholder_html("Select a configured Plex or Jellyfin server."))

    def _placeholder_html(self, text):
        return f"<html><body style='background:#101014;color:white;font-family:sans-serif;padding:24px;'><h2>MiddleTV Media</h2><p>{text}</p></body></html>"

    def load_server(self):
        cfg = load_config()
        data = self.servers_data()
        servers = data.get("servers", {})
        primary = cfg.get("primary_media_server") or data.get("primary_server") or data.get("active_server")
        if primary and primary in servers:
            self.server = servers[primary]
            self.server["id"] = primary
        elif servers:
            sid = next(iter(servers))
            self.server = servers[sid]; self.server["id"] = sid
        else:
            self.server = None
        self._render()

    def _render(self):
        if not self.server:
            self.setWindowTitle("Media Server - MiddleTV")
            self.title.setText("Jellyfin / Plex")
            self.status.setText("Not configured")
            self.info.setHtml("<p>No media server is configured.</p><p>Open <b>Settings &gt; Media Servers</b> to add a Jellyfin or Plex server URL, choose the server type, and set the primary home-screen tile.</p>")
            self.open_btn.setEnabled(False)
            self.browser.setHtml(self._placeholder_html("No Jellyfin or Plex server configured."))
            return
        kind = (self.server.get("type") or "media server").title()
        name = self.server.get("name", "Server")
        url = self.server.get("url", "")
        self.setWindowTitle(f"{kind} - MiddleTV")
        self.title.setText(f"{kind}: {name}")
        self.status.setText("Configured")
        self.info.setHtml(
            f"<p><b>Type:</b> {kind}</p><p><b>URL:</b> {url}</p>"
            "<p>MiddleTV opens the server's supported web interface in an embedded view for browsing and playback. "
            "Authentication, library browsing, resume/playback behavior, and device support depend on the selected server's web client and your server configuration. "
            "Use Settings to switch between configured Jellyfin and Plex servers.</p>"
        )
        self.open_btn.setEnabled(bool(url))

    def open_server(self):
        if not self.server or not self.server.get("url"):
            return
        url = self.server["url"]
        if not url.startswith(("http://", "https://")):
            url = "http://" + url
        self.browser.setUrl(QUrl(url))
        self.status.setText("Opening server...")

    def _show_config_hint(self):
        QMessageBox.information(self, "Media Servers", "Go to Settings > Media Servers to add Jellyfin/Plex servers, test connections, and choose the primary tile.")

    def handle_back(self):
        if self.browser.history().canGoBack() and self.browser.url().isValid() and self.browser.url().toString() not in ("about:blank", ""):
            self.browser.back(); return True
        self.close(); return True
