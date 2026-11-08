import json
import importlib
from pathlib import Path
from core.config import CONFIG_DIR, load_config


class AppManager:
    def __init__(self, wallpaper_callback=None, profile_manager=None):
        self.wallpaper_callback = wallpaper_callback
        self.profile_manager = profile_manager
        self.base = Path(__file__).resolve().parent.parent
        self.config_path = self.base / "config" / "apps.json"
        self.reload()

    def reload(self):
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.apps = json.load(f)
        except Exception:
            self.apps = []

    def _media_label(self):
        servers = {}
        try:
            with open(CONFIG_DIR / "media_servers.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            servers = data.get("servers", {}) or {}
            primary = data.get("primary_server") or data.get("active_server") or ""
        except Exception:
            primary = ""
        cfg = load_config()
        primary = cfg.get("primary_media_server") or primary
        if not servers:
            return "Media Server"
        server = servers.get(primary) or next(iter(servers.values()), {})
        kind = (server.get("type") or server.get("name") or "").lower()
        if "plex" in kind:
            return "Plex"
        if "jellyfin" in kind or server:
            return "Jellyfin"
        return "Media Server"

    def get_apps(self):
        apps = []
        for app in self.apps:
            item = dict(app)
            if item.get("dynamic_media"):
                item["name"] = self._media_label()
            apps.append(item)
        return apps

    def launch(self, module, **kwargs):
        app_module = importlib.import_module(module)
        args = {}
        if module == "apps.settings.app" and self.wallpaper_callback:
            args["wallpaper_callback"] = self.wallpaper_callback
        if self.profile_manager is not None:
            args["profile_manager"] = self.profile_manager
        args.update(kwargs)
        try:
            window = app_module.App(**args)
        except TypeError:
            # Backward compatibility with apps that don't accept new kwargs.
            try:
                window = app_module.App(wallpaper_callback=self.wallpaper_callback) if module == "apps.settings.app" and self.wallpaper_callback else app_module.App()
            except Exception:
                window = app_module.App()
        try:
            window.showFullScreen()
        except Exception:
            window.show()
        return window
