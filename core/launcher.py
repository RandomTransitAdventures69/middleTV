import json
import subprocess
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, QSize, QPoint, QTimer
from PySide6.QtGui import QPixmap, QPainter, QPainterPath, QColor, QIcon
from PySide6.QtWidgets import QWidget, QPushButton, QGridLayout, QVBoxLayout, QHBoxLayout, QLabel, QFrame

from core.app_manager import AppManager
from core.config import BASE_DIR, load_config, save_config, CONFIG_DIR
from core.notification_manager import NotificationManager
from core.profile_manager import ProfileManager
from core.theme import get_theme, app_stylesheet, qcolor


class Launcher(QWidget):
    is_middletv_root = True

    def __init__(self):
        super().__init__()
        self.windows = []
        self.profile_manager = ProfileManager()
        self.config = load_config()
        self.wallpaper = None
        self.setWindowTitle("MiddleTV")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.notifications = NotificationManager(self)
        self.manager = AppManager(
            wallpaper_callback=self.reload_wallpaper,
            profile_manager=self.profile_manager,
        )
        self.grid = QGridLayout()
        self.clock_label = QLabel()
        self.profile_button = QPushButton()
        self._build_ui()
        self.apply_theme()
        self.load_wallpaper()
        self.update_profile_button()
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)
        self.update_clock()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(44, 34, 44, 40)
        root.setSpacing(22)

        header = QHBoxLayout()
        header.setSpacing(16)
        title = QLabel("middleTV OS")
        title.setObjectName("osLabel")
        title.setStyleSheet("font-size: 44px; font-weight: 700; letter-spacing: 0.5px;")
        header.addWidget(title)
        header.addStretch()
        self.clock_label.setObjectName("muted")
        self.clock_label.setStyleSheet("font-size: 20px; font-weight: 600;")
        header.addWidget(self.clock_label)
        self.profile_button.setMinimumHeight(72)
        self.profile_button.setMinimumWidth(220)
        self.profile_button.setFocusPolicy(Qt.StrongFocus)
        self.profile_button.clicked.connect(self.open_profiles)
        header.addWidget(self.profile_button)
        root.addLayout(header)

        self.grid.setHorizontalSpacing(18)
        self.grid.setVerticalSpacing(18)
        self.grid_container = QWidget()
        self.grid_container.setLayout(self.grid)
        root.addWidget(self.grid_container, 1)
        self.populate_grid()

    def populate_grid(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        apps = self.manager.get_apps()
        cols = self._grid_columns(len(apps))
        for i, app in enumerate(apps):
            btn = QPushButton(app["name"])
            btn.setProperty("tile", True)
            btn.setMinimumSize(220, 138)
            btn.setSizePolicy(btn.sizePolicy().horizontalPolicy(), btn.sizePolicy().verticalPolicy())
            btn.setFocusPolicy(Qt.StrongFocus)
            btn.clicked.connect(lambda checked=False, a=app: self.open_app(a))
            self.grid.addWidget(btn, i // cols, i % cols)
        for c in range(cols):
            self.grid.setColumnStretch(c, 1)

    def _grid_columns(self, count):
        w = max(self.width(), 1280)
        if w >= 2200:
            cols = 6
        elif w >= 1700:
            cols = 5
        elif w >= 1280:
            cols = 4
        else:
            cols = 3
        # avoid awkward single-item last rows when reasonable
        if count == 10 and cols > 5:
            cols = 5
        return max(2, cols)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.populate_grid()

    def apply_theme(self):
        self.config = load_config()
        theme_name = self.config.get("ui_theme", "modern")
        self.setStyleSheet(app_stylesheet(theme_name) + self._launcher_qss(theme_name))

    def _launcher_qss(self, theme_name):
        t = get_theme(theme_name)
        scanlines = ""
        if theme_name == "terminal":
            scanlines = "background-image: repeating-linear-gradient(to bottom, rgba(120,255,120,14), rgba(120,255,120,14) 1px, rgba(0,0,0,0) 1px, rgba(0,0,0,0) 4px);"
        return f"""
        QLabel#osLabel {{ color: {t['text']}; }}
        QPushButton[tile=\"true\"] {{
            min-height: 138px;
            text-align: left;
            padding: 22px;
            font-size: 24px;
            font-weight: 700;
            background: {t['tile']};
            border: 2px solid {t['border']};
            border-radius: {t['radius']}px;
            {scanlines}
        }}
        QPushButton[tile=\"true\"]:hover {{ background: {t['tile_hover']}; border: 2px solid {t['focus']}; }}
        QPushButton[tile=\"true\"]:focus {{ background: {t['tile_focus']}; border: 4px solid {t['focus']}; }}
        QPushButton#profileButton {{
            border-radius: 36px;
            padding-left: 10px;
            padding-right: 18px;
            font-size: 18px;
            background: {t['panel']};
        }}
        """

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        if self.wallpaper and not self.wallpaper.isNull():
            scaled = self.wallpaper.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
        else:
            t = get_theme(self.config.get("ui_theme", "modern"))
            painter.fillRect(self.rect(), QColor(16, 16, 20) if t["name"] != "Terminal" else QColor(0, 8, 0))
        overlay = qcolor(get_theme(self.config.get("ui_theme", "modern"))["overlay"])
        painter.fillRect(self.rect(), overlay)
        if self.config.get("ui_theme") == "terminal":
            painter.fillRect(self.rect(), QColor(0, 255, 120, 8))
        painter.end()

    def get_config_file(self):
        return BASE_DIR / "config" / "config.json"

    def load_wallpaper(self):
        self.config = load_config()
        active = self.profile_manager.active()
        theme = self.config.get("ui_theme", "modern")
        theme_defaults = self.config.get("theme_wallpapers", {}) or {}
        wallpaper = active.get("wallpaper") or self.config.get("wallpaper") or theme_defaults.get(theme) or ""
        if wallpaper and Path(wallpaper).exists():
            pm = QPixmap(wallpaper)
            self.wallpaper = pm if not pm.isNull() else None
        else:
            self.wallpaper = None
        self.update()

    def reload_wallpaper(self, wallpaper_path):
        path = Path(wallpaper_path)
        if not path.exists():
            return
        pm = QPixmap(str(path))
        if pm.isNull():
            return
        self.wallpaper = pm
        self.update()
        if load_config().get("notifications_enabled", True) is not False:
            self.notifications.show("Wallpaper updated", "Your new wallpaper is now active.")

    def update_clock(self):
        self.clock_label.setText(datetime.now().strftime("%a %H:%M"))

    def update_profile_button(self):
        active = self.profile_manager.active()
        name = active.get("name", "Default")
        self.profile_button.setObjectName("profileButton")
        self.profile_button.setText(f"  {name}")
        self.profile_button.setIcon(self._profile_icon(active.get("picture", ""), name))
        self.profile_button.setIconSize(QSize(52, 52))

    def _profile_icon(self, picture, name):
        size = 52
        result = QPixmap(size, size)
        result.fill(Qt.transparent)
        painter = QPainter(result)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.setClipPath(path)
        pic_path = self.profile_manager.picture_path(picture)
        src = QPixmap(str(pic_path)) if pic_path.exists() else QPixmap()
        if not src.isNull():
            side = min(src.width(), src.height())
            src = src.copy((src.width() - side) // 2, (src.height() - side) // 2, side, side)
            painter.drawPixmap(0, 0, src.scaled(size, size, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        else:
            t = get_theme(self.config.get("ui_theme", "modern"))
            painter.fillRect(result.rect(), qcolor(t["tile_hover"]))
            painter.setPen(qcolor(t["text"]))
            painter.drawText(result.rect(), Qt.AlignCenter, (name[:1] or "?").upper())
        painter.end()
        return QIcon(result)

    def open_profiles(self):
        self.open_app({"name": "Profiles", "module": "apps.profiles.app"})

    def open_app(self, app):
        self.hide()
        try:
            if "module" in app:
                window = self.manager.launch(app["module"], launcher=self)
                if window is None:
                    raise RuntimeError("launch returned None")
                self.windows.append(window)
                window.destroyed.connect(lambda *_: self._on_child_closed(window))
                # also hook closeEvent for QWidget windows
                orig = getattr(window, "closeEvent", None)
                def _close(event, w=window, o=orig):
                    try:
                        if o:
                            o(event)
                        else:
                            event.accept()
                    finally:
                        QTimer.singleShot(0, lambda: self._on_child_closed(w))
                window.closeEvent = _close
                return
            if "command" in app:
                proc = subprocess.Popen(app["command"], shell=True)
                self.windows.append(proc)
                self.show()
                return
        except Exception as e:
            self.show()
            self.notifications.error(f"Could not launch {app.get('name', 'app')}: {e}")
            return
        self.show()

    def _on_child_closed(self, window):
        if window in self.windows:
            try:
                self.windows.remove(window)
            except ValueError:
                pass
        self.apply_theme()
        self.load_wallpaper()
        self.update_profile_button()
        self.populate_grid()
        if not self.isVisible():
            self.showFullScreen()
        self.raise_()
        self.activateWindow()

    def handle_back(self):
        # On home screen, Escape/Back should not quit MiddleTV.
        return True
