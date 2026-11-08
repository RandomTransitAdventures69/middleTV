import json
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QComboBox, QWidget
from apps.base_app import BaseApp
from core.config import load_config, save_config, load_settings, save_settings
from core.theme import THEMES


class Appearance(BaseApp):
    def __init__(self, wallpaper_callback=None):
        super().__init__("Appearance - MiddleTV")
        self.wallpaper_callback = wallpaper_callback
        self.root = Path(__file__).resolve().parent.parent.parent
        self.config_file = self.root / "config" / "config.json"
        self.selected_wallpaper = None
        self._build()
        self.load_current()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(56, 44, 56, 44)
        layout.setSpacing(18)
        title = QLabel("Appearance")
        title.setStyleSheet("font-size: 42px; font-weight: 700;")
        desc = QLabel("Choose the UI theme and wallpaper used across MiddleTV.")
        desc.setObjectName("muted")
        desc.setWordWrap(True)

        theme_row = QHBoxLayout()
        theme_label = QLabel("UI Theme")
        self.theme_combo = QComboBox()
        self.theme_combo.setMinimumHeight(52)
        for key, meta in THEMES.items():
            self.theme_combo.addItem(meta["name"], key)
        theme_row.addWidget(theme_label)
        theme_row.addWidget(self.theme_combo, 1)

        self.preview = QLabel("No wallpaper selected")
        self.preview.setObjectName("panel")
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setMinimumSize(680, 320)

        choose = QPushButton("Choose wallpaper")
        choose.clicked.connect(self.choose_wallpaper)
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.apply_changes)
        back = QPushButton("Back")
        back.clicked.connect(self.close)
        buttons = QHBoxLayout()
        buttons.setSpacing(12)
        buttons.addWidget(choose)
        buttons.addWidget(apply_btn)
        buttons.addStretch()
        buttons.addWidget(back)

        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addLayout(theme_row)
        layout.addWidget(self.preview, stretch=1)
        layout.addLayout(buttons)

    def load_current(self):
        config = load_config()
        self.selected_wallpaper = config.get("wallpaper") or ""
        idx = self.theme_combo.findData(config.get("ui_theme", "modern"))
        if idx >= 0:
            self.theme_combo.setCurrentIndex(idx)
        if self.selected_wallpaper:
            self.show_preview(self.selected_wallpaper)

    def choose_wallpaper(self):
        file, _ = QFileDialog.getOpenFileName(self, "Choose Wallpaper", str(Path.home()), "Images (*.png *.jpg *.jpeg *.bmp *.webp)")
        if file:
            self.selected_wallpaper = file
            self.show_preview(file)

    def show_preview(self, file):
        pixmap = QPixmap(file)
        if pixmap.isNull():
            self.preview.setText("Unable to load wallpaper")
            self.preview.setPixmap(QPixmap())
            return
        self.preview.setPixmap(pixmap.scaled(self.preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def resizeEvent(self, event):
        if self.selected_wallpaper:
            self.show_preview(self.selected_wallpaper)
        super().resizeEvent(event)

    def apply_changes(self):
        config = load_config()
        config["ui_theme"] = self.theme_combo.currentData() or "modern"
        if self.selected_wallpaper:
            config["wallpaper"] = self.selected_wallpaper
        save_config(config)
        self.apply_theme()
        if self.wallpaper_callback and self.selected_wallpaper:
            self.wallpaper_callback(self.selected_wallpaper)
