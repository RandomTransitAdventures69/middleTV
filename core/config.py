import json
import os
from copy import deepcopy
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_CONFIG = {
    "wallpaper": "",
    "theme": "dark",
    "ui_theme": "modern",
    "accent_color": "blue",
    "fullscreen": True,
    "volume": 75,
    "language": "en-US",
    "youtube_api_key": "",
    "spotify_client_id": "",
    "primary_media_server": "",
}

DEFAULT_SETTINGS = {
    "region": "United States",
    "time_zone": "Local",
    "automatic_updates": False,
    "resolution": "Auto",
    "refresh_rate": "Auto",
    "ui_scale": "100%",
    "connection": "Automatic",
    "ip_address": "Automatic",
    "dns": "Automatic",
    "tailscale": False,
    "keyboard": True,
    "hdmi_cec": False,
    "usb_remote": True,
    "bluetooth_remote": False,
    "kiosk_escape": "Ctrl+Shift+Esc",
    "web_interface": False,
    "web_port": "3000",
    "remote_access": False,
    "random_facts": True,
    "notifications_enabled": True,
    "startup_check_installation": True,
}


def _merge(default, data):
    result = deepcopy(default)
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict) and isinstance(result.get(key), dict):
                result[key] = _merge(result[key], value)
            else:
                result[key] = value
    return result


def _load(path, default):
    if not path.exists():
        _save(path, default)
        return deepcopy(default)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return deepcopy(default)
    return _merge(default, data)


def _save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    os.replace(tmp, path)


def load_config():
    return _load(CONFIG_DIR / "config.json", DEFAULT_CONFIG)


def save_config(data):
    _save(CONFIG_DIR / "config.json", _merge(DEFAULT_CONFIG, data))


def load_settings():
    return _load(CONFIG_DIR / "settings.json", DEFAULT_SETTINGS)


def save_settings(data):
    _save(CONFIG_DIR / "settings.json", _merge(DEFAULT_SETTINGS, data))


def load_json(path, default):
    path = Path(path)
    if not path.exists():
        return deepcopy(default)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return deepcopy(default)


def save_json(path, data):
    _save(Path(path), data)
