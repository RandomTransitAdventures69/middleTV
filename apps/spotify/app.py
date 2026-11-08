import base64
import hashlib
import json
import secrets
import threading
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QMessageBox, QTextBrowser, QLineEdit
from apps.base_app import BaseApp
from core.config import load_config, CONFIG_DIR

try:
    import keyring
except Exception:
    keyring = None

SPOTIFY_AUTH = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN = "https://accounts.spotify.com/api/token"
SPOTIFY_API = "https://api.spotify.com/v1"
REDIRECT_URI = "http://127.0.0.1:8765/callback"
SCOPES = "user-read-private user-read-email playlist-read-private playlist-read-collaborative user-library-read user-read-playback-state user-modify-playback-state"


def _token_path():
    return CONFIG_DIR / "spotify_tokens.json"


def _save_tokens(tokens):
    if keyring is not None:
        try:
            keyring.set_password("MiddleTV", "spotify_tokens", json.dumps(tokens))
            if _token_path().exists():
                _token_path().unlink()
            return
        except Exception:
            pass
    with open(_token_path(), "w", encoding="utf-8") as f:
        json.dump(tokens, f, indent=2)


def _load_tokens():
    if keyring is not None:
        try:
            raw = keyring.get_password("MiddleTV", "spotify_tokens")
            if raw:
                return json.loads(raw)
        except Exception:
            pass
    try:
        with open(_token_path(), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


class _CallbackHandler(BaseHTTPRequestHandler):
    result = {}

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/callback":
            self.send_response(404); self.end_headers(); return
        params = urllib.parse.parse_qs(parsed.query)
        _CallbackHandler.result = {k: v[0] for k, v in params.items()}
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h2>MiddleTV Spotify sign-in complete.</h2><p>You can close this window and return to MiddleTV.</p>")

    def log_message(self, format, *args):
        return


class App(BaseApp):
    def __init__(self):
        super().__init__("Spotify - MiddleTV")
        self.tokens = _load_tokens()
        self._build()
        self.refresh_status()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(10)
        header = QHBoxLayout()
        title = QLabel("Spotify")
        title.setStyleSheet("font-size: 34px; font-weight: 700;")
        self.status = QLabel()
        self.status.setObjectName("muted")
        header.addWidget(title); header.addStretch(); header.addWidget(self.status)
        root.addLayout(header)

        controls = QHBoxLayout()
        for label, fn in [("Sign In", self.sign_in), ("Playlists", self.load_playlists), ("Saved Tracks", self.load_saved_tracks), ("Search", self.search)]:
            b = QPushButton(label); b.setMinimumHeight(48); b.clicked.connect(fn); controls.addWidget(b)
        root.addLayout(controls)

        self.query = QLineEdit(); self.query.setPlaceholderText("Search Spotify"); self.query.setMinimumHeight(48)
        self.query.returnPressed.connect(self.search)
        root.addWidget(self.query)

        self.list = QListWidget()
        self.list.itemActivated.connect(self.show_item)
        root.addWidget(self.list, 1)
        self.details = QTextBrowser()
        self.details.setMaximumHeight(160)
        root.addWidget(self.details)
        self.details.setHtml(self._notes())

    def _notes(self):
        keyring_note = "OS credential storage is not available (keyring module missing); tokens will be stored in a local config file with restricted app access." if keyring is None else "Tokens are stored via the OS credential store when available."
        return (
            "<p>Configure a Spotify Client ID in Settings &gt; Integrations. MiddleTV uses Spotify's supported authorization flow (PKCE). "
            "Playback control requires an active Spotify playback device/app on a supported platform; API access alone does not provide unrestricted local audio playback. "
            f"{keyring_note}</p>"
        )

    def refresh_status(self):
        cfg = load_config()
        cid = cfg.get("spotify_client_id", "").strip()
        if not cid:
            self.status.setText("Client ID not configured")
        elif self.tokens.get("access_token"):
            self.status.setText("Signed in (token saved)")
        else:
            self.status.setText("Client ID configured; sign-in required")

    def sign_in(self):
        cfg = load_config()
        cid = cfg.get("spotify_client_id", "").strip()
        if not cid:
            QMessageBox.information(self, "Spotify", "Add a Spotify Client ID in Settings > Integrations.")
            return
        verifier = secrets.token_urlsafe(64)
        challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
        state = secrets.token_urlsafe(16)
        params = urllib.parse.urlencode({
            "client_id": cid,
            "response_type": "code",
            "redirect_uri": REDIRECT_URI,
            "code_challenge_method": "S256",
            "code_challenge": challenge,
            "scope": SCOPES,
            "state": state,
        })
        url = SPOTIFY_AUTH + "?" + params
        _CallbackHandler.result = {}
        server = HTTPServer(("127.0.0.1", 8765), _CallbackHandler)

        def serve():
            server.handle_request()

        t = threading.Thread(target=serve, daemon=True)
        t.start()
        try:
            webbrowser.open(url)
        except Exception:
            QMessageBox.information(self, "Spotify", f"Open this URL to sign in:\n\n{url}")
        QMessageBox.information(self, "Spotify", "A browser window should open for Spotify authorization. After approving, return to MiddleTV and click OK.")
        t.join(timeout=120)
        try:
            server.server_close()
        except Exception:
            pass
        result = _CallbackHandler.result
        if result.get("state") != state or "code" not in result:
            err = result.get("error_description") or result.get("error") or "Authorization did not complete."
            QMessageBox.warning(self, "Spotify", err)
            return
        code = result["code"]
        body = urllib.parse.urlencode({
            "client_id": cid,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "code_verifier": verifier,
        }).encode()
        try:
            req = urllib.request.Request(SPOTIFY_TOKEN, data=body, headers={"Content-Type": "application/x-www-form-urlencoded"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                tokens = json.load(resp)
        except Exception as e:
            QMessageBox.warning(self, "Spotify", f"Token exchange failed.\n\n{e}")
            return
        _save_tokens(tokens)
        self.tokens = tokens
        self.refresh_status()
        QMessageBox.information(self, "Spotify", "Spotify sign-in completed.")

    def _api(self, path, params=None):
        token = self.tokens.get("access_token")
        if not token:
            QMessageBox.information(self, "Spotify", "Sign in to Spotify first.")
            return None
        url = SPOTIFY_API + path
        if params:
            url += "?" + urllib.parse.urlencode(params)
        try:
            req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                return json.load(resp)
        except Exception as e:
            QMessageBox.warning(self, "Spotify", f"Spotify API request failed.\n\n{e}")
            return None

    def load_playlists(self):
        data = self._api("/me/playlists", {"limit": 30})
        if not data:
            return
        self.list.clear()
        for item in data.get("items", []):
            name = item.get("name", "Playlist")
            owner = ((item.get("owner") or {}).get("display_name")) or ""
            li = QListWidgetItem(f"{name} — {owner}")
            li.setData(Qt.UserRole, {"type": "playlist", "item": item})
            self.list.addItem(li)

    def load_saved_tracks(self):
        data = self._api("/me/tracks", {"limit": 30})
        if not data:
            return
        self.list.clear()
        for item in data.get("items", []):
            track = item.get("track") or {}
            artists = ", ".join(a.get("name", "") for a in track.get("artists") or [])
            li = QListWidgetItem(f"{track.get('name','Track')} — {artists}")
            li.setData(Qt.UserRole, {"type": "track", "item": track})
            self.list.addItem(li)

    def search(self):
        q = self.query.text().strip()
        if not q:
            return
        data = self._api("/search", {"q": q, "type": "track,playlist,album", "limit": 12})
        if not data:
            return
        self.list.clear()
        for track in ((data.get("tracks") or {}).get("items") or []):
            artists = ", ".join(a.get("name", "") for a in track.get("artists") or [])
            li = QListWidgetItem(f"Track: {track.get('name')} — {artists}")
            li.setData(Qt.UserRole, {"type": "track", "item": track})
            self.list.addItem(li)

    def show_item(self, item):
        payload = item.data(Qt.UserRole) or {}
        kind = payload.get("type")
        obj = payload.get("item") or {}
        if kind == "track":
            artists = ", ".join(a.get("name", "") for a in obj.get("artists") or [])
            uri = obj.get("uri", "")
            self.details.setHtml(f"<b>{obj.get('name','')}</b><br>{artists}<br><br>URI: {uri}<br><br>Playback controls require an active Spotify device. MiddleTV does not embed a full Spotify playback SDK in this build.")
        elif kind == "playlist":
            self.details.setHtml(f"<b>{obj.get('name','')}</b><br>{((obj.get('owner') or {}).get('display_name')) or ''}<br><br>{obj.get('description') or ''}")
        else:
            self.details.setPlainText(json.dumps(obj, indent=2)[:4000])
