import json
import urllib.parse
import urllib.request
from pathlib import Path
from PySide6.QtCore import Qt, QUrl, QSize
from PySide6.QtGui import QPixmap
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QWidget, QTextBrowser, QMessageBox, QSplitter
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from apps.base_app import BaseApp
from core.config import load_config, CONFIG_DIR


class App(BaseApp):
    def __init__(self):
        super().__init__("YouTube - MiddleTV")
        self.net = QNetworkAccessManager(self)
        self.results = []
        self._build()
        self._update_status()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(10)
        header = QHBoxLayout()
        title = QLabel("YouTube")
        title.setStyleSheet("font-size: 34px; font-weight: 700;")
        self.status = QLabel()
        self.status.setObjectName("muted")
        header.addWidget(title); header.addStretch(); header.addWidget(self.status)
        root.addLayout(header)

        search = QHBoxLayout()
        self.query = QLineEdit(); self.query.setPlaceholderText("Search YouTube"); self.query.setMinimumHeight(52)
        self.query.returnPressed.connect(self.search)
        btn = QPushButton("Search"); btn.setMinimumHeight(52); btn.clicked.connect(self.search)
        search.addWidget(self.query, 1); search.addWidget(btn)
        root.addLayout(search)

        split = QSplitter(Qt.Horizontal)
        self.list = QListWidget()
        self.list.setIconSize(QSize(320, 180))
        self.list.setSpacing(8)
        self.list.itemActivated.connect(self.open_selected)
        self.list.itemClicked.connect(self.show_details)
        split.addWidget(self.list)

        right = QWidget(); r = QVBoxLayout(right); r.setContentsMargins(8, 0, 0, 0)
        self.details = QTextBrowser(); self.details.setOpenExternalLinks(False)
        self.player = QWebEngineView(); self.player.setMinimumHeight(260)
        controls = QHBoxLayout()
        play = QPushButton("Play"); play.clicked.connect(self.open_selected)
        stop = QPushButton("Stop"); stop.clicked.connect(lambda: self.player.setHtml("<html><body style='background:#111;color:#fff;font-family:sans-serif;'>Playback stopped.</body></html>"))
        for b in (play, stop): b.setMinimumHeight(48); controls.addWidget(b)
        r.addWidget(self.player, 2); r.addLayout(controls); r.addWidget(self.details, 1)
        split.addWidget(right)
        split.setSizes([520, 680])
        root.addWidget(split, 1)

        self.details.setHtml("<p>Configure a YouTube Data API key in Settings &gt; Integrations, then search for videos.</p>")
        self.query.setFocus()

    def _update_status(self):
        key = load_config().get("youtube_api_key", "").strip()
        self.status.setText("API configured" if key else "API key not configured (Settings > Integrations)")

    def search(self):
        key = load_config().get("youtube_api_key", "").strip()
        self._update_status()
        if not key:
            QMessageBox.information(self, "YouTube", "Add a YouTube Data API key in Settings > Integrations.")
            return
        q = self.query.text().strip()
        if not q:
            return
        params = urllib.parse.urlencode({
            "part": "snippet",
            "type": "video",
            "maxResults": 12,
            "q": q,
            "key": key,
            "safeSearch": "moderate",
        })
        url = "https://www.googleapis.com/youtube/v3/search?" + params
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "MiddleTV"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.load(resp)
        except Exception as e:
            QMessageBox.warning(self, "YouTube Search", f"Search failed.\n\n{e}")
            return
        self.list.clear(); self.results = []
        for item in data.get("items", []):
            vid = (((item.get("id") or {}).get("videoId")) or "")
            sn = item.get("snippet") or {}
            if not vid:
                continue
            title = sn.get("title", "Video")
            channel = sn.get("channelTitle", "")
            desc = sn.get("description", "")
            thumb = (((sn.get("thumbnails") or {}).get("medium") or {}).get("url")) or ""
            entry = {"id": vid, "title": title, "channel": channel, "description": desc, "thumb": thumb}
            self.results.append(entry)
            li = QListWidgetItem(f"{title}\n{channel}")
            li.setData(Qt.UserRole, entry)
            li.setToolTip(desc)
            self.list.addItem(li)
            if thumb:
                self._load_thumb(li, thumb)
        if not self.results:
            self.details.setHtml("<p>No results.</p>")

    def _load_thumb(self, item, url):
        req = QNetworkRequest(QUrl(url))
        reply = self.net.get(req)
        def done():
            data = bytes(reply.readAll())
            px = QPixmap(); px.loadFromData(data)
            if not px.isNull():
                item.setIcon(px.scaled(320, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            reply.deleteLater()
        reply.finished.connect(done)

    def show_details(self, item):
        entry = item.data(Qt.UserRole) or {}
        self.details.setHtml(
            f"<h2>{entry.get('title','')}</h2>"
            f"<p><b>Channel:</b> {entry.get('channel','')}</p>"
            f"<p>{entry.get('description','')}</p>"
            f"<p><b>Video ID:</b> {entry.get('id','')}</p>"
        )

    def open_selected(self):
        item = self.list.currentItem()
        if not item:
            return
        entry = item.data(Qt.UserRole) or {}
        vid = entry.get("id")
        if not vid:
            return
        self.show_details(item)
        # YouTube direct media extraction is not assumed; use the official embed player in QtWebEngine.
        embed = QUrl(f"https://www.youtube-nocookie.com/embed/{urllib.parse.quote(vid)}?autoplay=1&rel=0")
        self.player.setUrl(embed)

    def handle_back(self):
        if self.player.url().toString().startswith("https://www.youtube-nocookie.com/embed/"):
            self.player.setHtml("<html><body style='background:#111;color:#fff;font-family:sans-serif;'>Player stopped.</body></html>")
            self.list.setFocus()
            return True
        self.close(); return True
