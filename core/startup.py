from pathlib import Path
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QFrame
from core.config import BASE_DIR, load_config, load_settings
from core.theme import app_stylesheet


class StartupScreen(QWidget):
    def __init__(self, on_done):
        super().__init__()
        self.on_done = on_done
        self.setWindowTitle("MiddleTV")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.steps = []
        self.index = 0
        self.status = QLabel("Initializing MiddleTV.")
        self.status.setObjectName("muted")
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(14)
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet(app_stylesheet(load_config().get("ui_theme", "modern")) + """
            QProgressBar { background: rgba(255,255,255,30); border: none; border-radius: 7px; }
            QProgressBar::chunk { background: rgba(90,190,255,230); border-radius: 7px; }
        """)
        root = QVBoxLayout(self)
        root.setContentsMargins(80, 80, 80, 80)
        root.addStretch()
        card = QFrame()
        card.setObjectName("panel")
        card.setMaximumWidth(760)
        inner = QVBoxLayout(card)
        inner.setContentsMargins(36, 34, 36, 34)
        inner.setSpacing(14)
        title = QLabel("middleTV OS")
        title.setStyleSheet("font-size: 42px; font-weight: 700;")
        subtitle = QLabel("Starting your TV experience")
        subtitle.setObjectName("muted")
        subtitle.setStyleSheet("font-size: 20px;")
        inner.addWidget(title)
        inner.addWidget(subtitle)
        inner.addSpacing(10)
        inner.addWidget(self.status)
        inner.addWidget(self.progress)
        root.addWidget(card, alignment=Qt.AlignCenter)
        root.addStretch()

    def run(self):
        config = load_config()
        settings = load_settings()
        self.steps = [
            ("Checking required files.", lambda: self._check_installation(settings)),
            ("Loading configuration.", lambda: (load_config(), load_settings())),
            ("Loading profiles.", self._load_profiles),
            ("Initializing integrations.", self._check_integrations),
            ("Starting MiddleTV.", lambda: None),
        ]
        self.progress.setRange(0, len(self.steps))
        self.index = 0
        QTimer.singleShot(120, self._next)

    def _next(self):
        if self.index >= len(self.steps):
            self.progress.setValue(len(self.steps))
            self.on_done()
            return
        message, fn = self.steps[self.index]
        self.status.setText(message)
        try:
            result = fn()
            if isinstance(result, tuple) and len(result) == 2:
                ok, detail = result
                if not ok and detail:
                    self.status.setText(detail)
        except Exception as e:
            self.status.setText(f"{message} ({e})")
        self.index += 1
        self.progress.setValue(self.index)
        QTimer.singleShot(140, self._next)

    def _check_installation(self, settings):
        if not settings.get("startup_check_installation", True):
            return True, None
        required = [BASE_DIR / "main.py", BASE_DIR / "core" / "launcher.py", BASE_DIR / "config"]
        missing = [p.name for p in required if not p.exists()]
        if missing:
            return False, "Installation check found missing files: " + ", ".join(missing)
        return True, None

    def _load_profiles(self):
        from core.profile_manager import ProfileManager
        ProfileManager()

    def _check_integrations(self):
        config = load_config()
        _ = config.get("youtube_api_key", "")
        _ = config.get("spotify_client_id", "")
