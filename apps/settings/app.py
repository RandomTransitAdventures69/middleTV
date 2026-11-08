import sys
import json
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFrame,
    QStackedWidget, QDialog, QInputDialog, QLineEdit, QComboBox, QMessageBox, QScrollArea
)
from PySide6.QtCore import Qt
from core.config import load_config, save_config, load_settings, save_settings, CONFIG_DIR, BASE_DIR
from core.theme import app_stylesheet, get_theme, THEMES


class SettingsRow(QPushButton):
    def __init__(self, title, value="", parent=None):
        super().__init__(parent)
        self.setObjectName("settingsRow")
        self.setMinimumHeight(72)
        self.setFocusPolicy(Qt.StrongFocus)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 16, 0)
        layout.setSpacing(14)
        self.title_label = QLabel(title)
        self.title_label.setObjectName("settingTitle")
        self.value_label = QLabel(value)
        self.value_label.setObjectName("settingValue")
        self.value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        chevron = QLabel("›")
        chevron.setObjectName("settingChevron")
        chevron.setFixedWidth(16)
        layout.addWidget(self.title_label)
        layout.addStretch(1)
        layout.addWidget(self.value_label)
        layout.addWidget(chevron)

    def set_value(self, value):
        self.value_label.setText(value)


class Page(QWidget):
    def __init__(self, title):
        super().__init__()
        self.outer = QVBoxLayout(self)
        self.outer.setContentsMargins(24, 16, 24, 16)
        self.outer.setSpacing(10)
        h = QLabel(title)
        h.setObjectName("pageTitle")
        self.outer.addWidget(h)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        body = QWidget()
        self.layout = QVBoxLayout(body)
        self.layout.setContentsMargins(0, 0, 8, 0)
        self.layout.setSpacing(10)
        self.layout.addStretch(1)
        scroll.setWidget(body)
        self.outer.addWidget(scroll, 1)

    def add_row(self, row):
        self.layout.insertWidget(self.layout.count() - 1, row)


class App(QWidget):
    is_middletv_root = True

    def __init__(self, wallpaper_callback=None):
        super().__init__()
        self.wallpaper_callback = wallpaper_callback
        self.setWindowTitle("Settings - MiddleTV")
        self.rows = {}
        self._build()
        self.apply_style()

    def servers_file(self):
        return CONFIG_DIR / "media_servers.json"

    def load_servers(self):
        try:
            with open(self.servers_file(), "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {"active_server": "", "primary_server": "", "servers": {}}
        data.setdefault("active_server", "")
        data.setdefault("primary_server", data.get("active_server", ""))
        data.setdefault("servers", {})
        return data

    def save_servers(self, data):
        data.setdefault("primary_server", data.get("active_server", ""))
        with open(self.servers_file(), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        cfg = load_config()
        cfg["primary_media_server"] = data.get("primary_server") or data.get("active_server") or ""
        save_config(cfg)

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(40, 30, 40, 30)
        root.setSpacing(16)
        title = QLabel("Settings")
        title.setObjectName("appTitle")
        root.addWidget(title)

        main = QHBoxLayout()
        main.setSpacing(18)
        sidebar = QFrame()
        sidebar.setObjectName("settingsSidebar")
        sidebar.setFixedWidth(280)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(10, 10, 10, 10)
        side.setSpacing(6)
        self.stack = QStackedWidget()
        self.stack.setObjectName("settingsContent")
        self.cat_buttons = []
        cats = ["Appearance", "Profiles", "Media Servers", "Applications", "System", "Integrations", "Notifications"]
        for i, name in enumerate(cats):
            b = QPushButton(name)
            b.setObjectName("categoryButton")
            b.setMinimumHeight(52)
            b.setFocusPolicy(Qt.StrongFocus)
            b.clicked.connect(lambda checked=False, idx=i: self.show_category(idx))
            side.addWidget(b)
            self.cat_buttons.append(b)
        side.addStretch(1)
        main.addWidget(sidebar)
        main.addWidget(self.stack, 1)
        root.addLayout(main, 1)

        bottom = QHBoxLayout()
        bottom.addStretch(1)
        back = QPushButton("Back")
        back.setObjectName("secondaryButton")
        back.setMinimumHeight(52)
        back.clicked.connect(self.close)
        bottom.addWidget(back)
        root.addLayout(bottom)

        self._build_pages()
        self.show_category(0)
        self.cat_buttons[0].setFocus()

    def row(self, page, title, value="", fn=None):
        r = SettingsRow(title, value)
        if fn:
            r.clicked.connect(fn)
        page.add_row(r)
        self.rows[title] = r
        return r

    def _build_pages(self):
        cfg = load_config()
        settings = load_settings()
        # Appearance
        p = Page("Appearance")
        self.row(p, "UI Theme", THEMES.get(cfg.get("ui_theme", "modern"), THEMES["modern"])["name"], self.choose_theme)
        self.row(p, "Wallpaper", Path(cfg.get("wallpaper") or "Not set").name or "Not set", self.open_appearance)
        self.row(p, "UI Scale", settings.get("ui_scale", "100%"), lambda: self.choose_setting("UI Scale", "ui_scale", ["90%", "100%", "110%", "125%", "150%"], settings))
        self.row(p, "Focus Appearance", "Theme default", lambda: QMessageBox.information(self, "Focus Appearance", "Focus styling follows the selected UI theme."))
        self.row(p, "Screensaver", "Not configured", lambda: QMessageBox.information(self, "Screensaver", "Screensaver configuration is not implemented in this build."))
        self.row(p, "Startup Behavior", "Show startup screen" if settings.get("startup_check_installation", True) else "Skip installation check", self.toggle_startup_check)
        self.stack.addWidget(p)
        # Profiles
        p = Page("Profiles")
        self.row(p, "Manage Profiles", "Open profile manager", self.open_profiles)
        self.row(p, "Active Profile", self.active_profile_name(), self.choose_active_profile)
        self.row(p, "Profile-specific Settings", "Wallpaper/preferences follow profile where configured", lambda: QMessageBox.information(self, "Profiles", "Profile switching is supported. Per-application preference storage can be extended in app modules."))
        self.stack.addWidget(p)
        # Media Servers
        p = Page("Media Servers")
        self.row(p, "Jellyfin / Plex Status", self.media_status(), self.open_media_app)
        self.row(p, "Add or Edit Server", "Manage saved servers", self.manage_servers)
        self.row(p, "Primary Media Tile", cfg.get("primary_media_server") or "Automatic", self.choose_primary_server)
        self.row(p, "Test Connection", "Run a basic URL check", self.test_media_connection)
        self.stack.addWidget(p)
        # Applications
        p = Page("Applications")
        self.row(p, "Installed MiddleTV Apps", "About, Settings, Files, Profiles, Clock, Media, Flight Tracker, YouTube, Spotify, Terminal", None)
        self.row(p, "Application Installation", "Open installer", self.open_app_installer)
        self.row(p, "Application Settings", "YouTube/Spotify/Media are in Integrations and Media Servers", None)
        self.stack.addWidget(p)
        # System
        p = Page("System")
        self.row(p, "System Information", self.system_summary(), self.show_system_info)
        self.row(p, "System Updates", "Check and apply OS updates", self.open_system_updates)
        self.row(p, "Package Management", "Use System Updates / App Installer", None)
        self.row(p, "Network Status", settings.get("connection", "Automatic"), lambda: self.choose_setting("Connection", "connection", ["Automatic", "Ethernet", "Wi-Fi", "Offline"], settings))
        self.row(p, "Storage Information", "Available in System Information", self.show_system_info)
        self.stack.addWidget(p)
        # Integrations
        p = Page("Integrations")
        self.row(p, "YouTube API Key", "Configured" if cfg.get("youtube_api_key") else "Not configured", self.set_youtube_key)
        self.row(p, "Spotify Client ID", "Configured" if cfg.get("spotify_client_id") else "Not configured", self.set_spotify_client_id)
        self.row(p, "Spotify Sign In", "Open Spotify app to authenticate", self.open_spotify)
        self.stack.addWidget(p)
        # Notifications
        p = Page("Notifications")
        enabled = settings.get("notifications_enabled", True)
        self.row(p, "In-App Notifications", "On" if enabled else "Off", self.toggle_notifications)
        self.row(p, "System Notifications", "Depends on operating system support", None)
        self.stack.addWidget(p)

    def show_category(self, index):
        self.stack.setCurrentIndex(index)
        for i, b in enumerate(self.cat_buttons):
            b.setProperty("active", i == index)
            b.style().unpolish(b)
            b.style().polish(b)

    def choose_theme(self):
        cfg = load_config()
        names = [THEMES[k]["name"] for k in THEMES]
        keys = list(THEMES.keys())
        cur = cfg.get("ui_theme", "modern")
        idx = keys.index(cur) if cur in keys else 0
        choice, ok = QInputDialog.getItem(self, "UI Theme", "Theme:", names, idx, False)
        if ok:
            cfg["ui_theme"] = keys[names.index(choice)]
            save_config(cfg)
            self.rows["UI Theme"].set_value(choice)
            self.apply_style()

    def open_appearance(self):
        from apps.settings.appearance import Appearance
        self._child = Appearance(self.wallpaper_callback)
        self._child.showFullScreen()

    def toggle_startup_check(self):
        s = load_settings()
        s["startup_check_installation"] = not s.get("startup_check_installation", True)
        save_settings(s)
        self.rows["Startup Behavior"].set_value("Show startup screen" if s["startup_check_installation"] else "Skip installation check")

    def choose_setting(self, title, key, choices, settings=None):
        s = load_settings() if settings is None else settings
        cur = s.get(key, choices[0])
        idx = choices.index(cur) if cur in choices else 0
        choice, ok = QInputDialog.getItem(self, title, title + ":", choices, idx, False)
        if ok:
            s[key] = choice
            save_settings(s)
            if title in self.rows:
                self.rows[title].set_value(choice)

    def active_profile_name(self):
        try:
            from core.profile_manager import ProfileManager
            return ProfileManager().active().get("name", "Default")
        except Exception:
            return "Default"

    def open_profiles(self):
        from apps.profiles.app import App as ProfilesApp
        self._profiles = ProfilesApp()
        self._profiles.showFullScreen()

    def choose_active_profile(self):
        from core.profile_manager import ProfileManager
        pm = ProfileManager()
        profiles = pm.profiles()
        ids = list(profiles.keys())
        names = [profiles[i].get("name", i) for i in ids]
        if not ids:
            return
        idx = ids.index(pm.active_id()) if pm.active_id() in ids else 0
        choice, ok = QInputDialog.getItem(self, "Active Profile", "Profile:", names, idx, False)
        if ok:
            pm.set_active(ids[names.index(choice)])
            self.rows["Active Profile"].set_value(choice)

    def media_status(self):
        data = self.load_servers()
        servers = data.get("servers", {})
        if not servers:
            return "No servers configured"
        active = data.get("active_server") or next(iter(servers))
        s = servers.get(active, {})
        return f"{s.get('name','Server')} ({s.get('type','media')})"

    def open_media_app(self):
        from apps.media_server.app import App as MediaApp
        self._media = MediaApp()
        self._media.showFullScreen()

    def manage_servers(self):
        data = self.load_servers()
        dialog = QDialog(self)
        dialog.setWindowTitle("Media Servers")
        dialog.setMinimumWidth(620)
        layout = QVBoxLayout(dialog)
        combo = QComboBox(); combo.setMinimumHeight(50)
        ids = []
        def reload_combo():
            combo.clear(); ids.clear()
            d = self.load_servers()
            for sid, s in d.get("servers", {}).items():
                combo.addItem(f"{s.get('name', sid)} - {s.get('type', 'server')} ({s.get('url','')})", sid)
                ids.append(sid)
        reload_combo()
        layout.addWidget(QLabel("Saved servers"))
        layout.addWidget(combo)
        buttons = QHBoxLayout()
        for label, fn in [("Add", None), ("Use", None), ("Remove", None), ("Close", dialog.accept)]:
            b = QPushButton(label); b.setMinimumHeight(48); buttons.addWidget(b)
            if label == "Close": b.clicked.connect(fn)
            if label == "Add": b.clicked.connect(lambda: self._add_server(dialog, reload_combo))
            if label == "Use": b.clicked.connect(lambda: self._use_server(combo.currentData(), dialog, reload_combo))
            if label == "Remove": b.clicked.connect(lambda: self._remove_server(combo.currentData(), reload_combo))
        layout.addLayout(buttons)
        dialog.setStyleSheet(self.dialog_style())
        dialog.exec()
        self.rows["Jellyfin / Plex Status"].set_value(self.media_status())

    def _add_server(self, parent, reload_cb):
        name, ok = QInputDialog.getText(parent, "Server Name", "Name:")
        if not ok or not name.strip(): return
        url, ok = QInputDialog.getText(parent, "Server URL", "URL (http://...):")
        if not ok or not url.strip(): return
        types = ["Jellyfin", "Plex"]
        kind, ok = QInputDialog.getItem(parent, "Server Type", "Type:", types, 0, False)
        if not ok: return
        d = self.load_servers()
        sid = name.strip().lower().replace(' ', '_')
        base = sid; n = 2
        while sid in d['servers']:
            sid = f"{base}_{n}"; n += 1
        if not url.startswith(('http://','https://')): url = 'http://' + url
        d['servers'][sid] = {"name": name.strip(), "url": url.rstrip('/'), "type": kind.lower()}
        d['active_server'] = d.get('active_server') or sid
        d['primary_server'] = d.get('primary_server') or sid
        self.save_servers(d); reload_cb()

    def _use_server(self, sid, parent, reload_cb):
        if not sid: return
        d = self.load_servers(); d['active_server'] = sid; d['primary_server'] = sid; self.save_servers(d); reload_cb()
        QMessageBox.information(parent, "Media Servers", "Active server updated.")

    def _remove_server(self, sid, reload_cb):
        if not sid: return
        d = self.load_servers(); d['servers'].pop(sid, None)
        if d.get('active_server') == sid: d['active_server'] = next(iter(d['servers']), '')
        if d.get('primary_server') == sid: d['primary_server'] = d.get('active_server', '')
        self.save_servers(d); reload_cb()

    def choose_primary_server(self):
        d = self.load_servers(); servers = d.get('servers', {})
        if not servers:
            QMessageBox.information(self, "Media Servers", "Configure a Jellyfin or Plex server first."); return
        ids = list(servers.keys()); names = [servers[i].get('name', i) for i in ids]
        idx = ids.index(d.get('primary_server','')) if d.get('primary_server','') in ids else 0
        choice, ok = QInputDialog.getItem(self, "Primary Media Tile", "Server:", names, idx, False)
        if ok:
            d['primary_server'] = ids[names.index(choice)]; d['active_server'] = d['primary_server']; self.save_servers(d)
            self.rows["Primary Media Tile"].set_value(choice)

    def test_media_connection(self):
        d = self.load_servers(); servers = d.get('servers', {})
        sid = d.get('active_server') or (next(iter(servers)) if servers else '')
        if not sid or sid not in servers:
            QMessageBox.information(self, "Test Connection", "No media server is configured."); return
        s = servers[sid]; url = s.get('url','')
        try:
            import urllib.request
            req = urllib.request.Request(url, headers={'User-Agent': 'MiddleTV'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                status = getattr(resp, 'status', 200)
            QMessageBox.information(self, "Test Connection", f"Reached {s.get('name', 'server')} at {url}\nHTTP status: {status}")
        except Exception as e:
            QMessageBox.warning(self, "Test Connection", f"Could not reach {url}\n\n{e}")

    def open_app_installer(self):
        from apps.settings.system_tools import AppInstaller
        self._installer = AppInstaller(); self._installer.showFullScreen()

    def open_system_updates(self):
        from apps.settings.system_tools import SystemUpdates
        self._updates = SystemUpdates(); self._updates.showFullScreen()

    def system_summary(self):
        import platform
        return f"{platform.system()} {platform.release()}"

    def show_system_info(self):
        import platform, shutil
        total, used, free = shutil.disk_usage(Path.home())
        msg = (
            f"OS: {platform.system()} {platform.release()}\n"
            f"Machine: {platform.machine()}\n"
            f"Python: {platform.python_version()}\n"
            f"Home storage free: {free // (1024**3)} GiB / {total // (1024**3)} GiB\n"
            f"Config: {CONFIG_DIR}"
        )
        QMessageBox.information(self, "System Information", msg)

    def set_youtube_key(self):
        cfg = load_config()
        val, ok = QInputDialog.getText(self, "YouTube API Key", "API key:", QLineEdit.Normal, cfg.get("youtube_api_key", ""))
        if ok:
            cfg["youtube_api_key"] = val.strip(); save_config(cfg)
            self.rows["YouTube API Key"].set_value("Configured" if cfg["youtube_api_key"] else "Not configured")

    def set_spotify_client_id(self):
        cfg = load_config()
        val, ok = QInputDialog.getText(self, "Spotify Client ID", "Client ID:", QLineEdit.Normal, cfg.get("spotify_client_id", ""))
        if ok:
            cfg["spotify_client_id"] = val.strip(); save_config(cfg)
            self.rows["Spotify Client ID"].set_value("Configured" if cfg["spotify_client_id"] else "Not configured")
            QMessageBox.information(self, "Spotify", "Client ID saved. Open the Spotify app to complete sign-in when OAuth is configured.")

    def open_spotify(self):
        from apps.spotify.app import App as SpotifyApp
        self._spotify = SpotifyApp(); self._spotify.showFullScreen()

    def toggle_notifications(self):
        s = load_settings(); s["notifications_enabled"] = not s.get("notifications_enabled", True); save_settings(s)
        self.rows["In-App Notifications"].set_value("On" if s["notifications_enabled"] else "Off")

    def handle_back(self):
        self.close(); return True

    def dialog_style(self):
        return app_stylesheet(load_config().get("ui_theme", "modern"))

    def apply_style(self):
        self.setAttribute(Qt.WA_StyledBackground, True)
        theme = load_config().get("ui_theme", "modern")
        t = get_theme(theme)
        self.setStyleSheet(app_stylesheet(theme) + f"""
            QLabel#appTitle {{ font-size: 42px; font-weight: 700; }}
            QLabel#pageTitle {{ font-size: 28px; font-weight: 700; padding-bottom: 8px; }}
            QFrame#settingsSidebar {{ background: {t['panel']}; border: 1px solid {t['border']}; border-radius: 18px; }}
            QStackedWidget#settingsContent {{ background: {t['panel_strong']}; border: 1px solid {t['border']}; border-radius: 18px; }}
            QPushButton#categoryButton {{ color: {t['muted']}; background: transparent; border: 1px solid transparent; border-radius: 10px; text-align: left; padding: 0 14px; }}
            QPushButton#categoryButton[active=\"true\"] {{ color: {t['text']}; background: {t['tile_focus']}; border-color: {t['focus']}; }}
            QPushButton#settingsRow {{ text-align: left; padding: 0; border-radius: 12px; }}
            QLabel#settingTitle {{ color: {t['text']}; font-size: 19px; font-weight: 600; background: transparent; }}
            QLabel#settingValue {{ color: {t['muted']}; font-size: 16px; background: transparent; }}
            QLabel#settingChevron {{ color: {t['accent']}; font-size: 26px; background: transparent; }}
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App(); window.show(); sys.exit(app.exec())
