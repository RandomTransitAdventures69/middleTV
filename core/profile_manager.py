import json
from pathlib import Path
from core.config import BASE_DIR, CONFIG_DIR


class ProfileManager:
    def __init__(self):
        self.file = CONFIG_DIR / "profiles.json"
        self.dir = BASE_DIR / "profiles"
        self.dir.mkdir(parents=True, exist_ok=True)
        self.data = self._load()

    def _load(self):
        default = {"active_profile": "default", "profiles": {"default": {"name": "Default", "picture": "", "wallpaper": ""}}}
        if not self.file.exists():
            self._save(default)
            return default
        try:
            with open(self.file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return default
        data.setdefault("active_profile", "default")
        data.setdefault("profiles", {})
        if "default" not in data["profiles"]:
            data["profiles"]["default"] = default["profiles"]["default"]
        return data

    def _save(self, data=None):
        if data is not None:
            self.data = data
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)

    def profiles(self):
        return self.data.get("profiles", {})

    def active_id(self):
        aid = self.data.get("active_profile", "default")
        if aid not in self.profiles():
            aid = "default"
        return aid

    def active(self):
        return self.profiles().get(self.active_id(), {"name": "Default", "picture": "", "wallpaper": ""})

    def set_active(self, profile_id):
        if profile_id in self.profiles():
            self.data["active_profile"] = profile_id
            self._save()
            return True
        return False

    def picture_path(self, picture):
        if not picture:
            return self.dir / ""
        p = Path(picture)
        return p if p.is_absolute() else (self.dir / picture)

    def upsert(self, profile_id, payload):
        self.data.setdefault("profiles", {})[profile_id] = payload
        self._save()

    def delete(self, profile_id):
        if profile_id == "default":
            return False
        profiles = self.profiles()
        if profile_id in profiles:
            del profiles[profile_id]
            if self.active_id() == profile_id:
                self.data["active_profile"] = "default"
            self._save()
            return True
        return False


    # Compatibility aliases for existing code
    def get_profiles(self):
        return self.profiles()

    def get_active_id(self):
        return self.active_id()

    def set_active_profile(self, profile_id):
        return self.set_active(profile_id)

    def add_profile(self, profile_id, name, picture="", wallpaper=""):
        self.upsert(profile_id, {"name": name, "picture": picture, "wallpaper": wallpaper})
