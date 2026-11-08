from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QPainter, QPainterPath, QColor
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QFileDialog, QInputDialog, QMessageBox, QScrollArea
from apps.base_app import BaseApp
from core.profile_manager import ProfileManager


class App(BaseApp):
    def __init__(self):
        super().__init__("Profiles - MiddleTV")
        self.manager = ProfileManager()
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(40, 30, 40, 30)
        root.setSpacing(18)
        title = QLabel("Who's watching?")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 42px; font-weight: 700;")
        root.addWidget(title)

        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(scroll.NoFrame)
        body = QWidget(); self.cards = QHBoxLayout(body); self.cards.setSpacing(20); self.cards.setAlignment(Qt.AlignCenter)
        scroll.setWidget(body)
        root.addWidget(scroll, 1)

        controls = QHBoxLayout()
        for label, fn in [("Add Profile", self.add_profile), ("Edit Picture", self.edit_picture), ("Delete Profile", self.delete_profile), ("Back", self.close)]:
            b = QPushButton(label); b.setMinimumHeight(52); b.clicked.connect(fn); controls.addWidget(b)
        root.addLayout(controls)
        self.refresh()

    def refresh(self):
        while self.cards.count():
            item = self.cards.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        for pid, profile in self.manager.get_profiles().items():
            self.cards.addWidget(self._card(pid, profile))

    def _circular(self, source, size):
        side = min(source.width(), source.height())
        src = source.copy((source.width()-side)//2, (source.height()-side)//2, side, side).scaled(size, size, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        out = QPixmap(size, size); out.fill(Qt.transparent)
        p = QPainter(out); p.setRenderHint(QPainter.Antialiasing); p.setRenderHint(QPainter.SmoothPixmapTransform)
        path = QPainterPath(); path.addEllipse(0, 0, size, size); p.setClipPath(path); p.drawPixmap(0, 0, src); p.end(); return out

    def _card(self, profile_id, profile):
        btn = QPushButton(); btn.setFixedSize(220, 280); btn.setFocusPolicy(Qt.StrongFocus)
        lay = QVBoxLayout(btn); lay.setContentsMargins(12, 18, 12, 18); lay.setSpacing(10)
        pic = QLabel(); pic.setFixedSize(150, 150); pic.setAlignment(Qt.AlignCenter)
        pic_path = self.manager.picture_path(profile.get("picture", ""))
        px = QPixmap(str(pic_path)) if pic_path.exists() else QPixmap()
        if not px.isNull():
            pic.setPixmap(self._circular(px, 150))
        else:
            pic.setText((profile.get("name", profile_id)[:1] or "?").upper())
            pic.setStyleSheet("font-size: 54px; font-weight: 700; border-radius: 75px; background: rgba(255,255,255,25);")
        name = QLabel(profile.get("name", profile_id)); name.setAlignment(Qt.AlignCenter); name.setStyleSheet("font-size: 22px; font-weight: 700;")
        active = QLabel("Active" if profile_id == self.manager.get_active_id() else ""); active.setAlignment(Qt.AlignCenter); active.setObjectName("muted")
        lay.addStretch(); lay.addWidget(pic, alignment=Qt.AlignCenter); lay.addWidget(name); lay.addWidget(active); lay.addStretch()
        btn.clicked.connect(lambda: self.select_profile(profile_id))
        return btn

    def select_profile(self, profile_id):
        self.manager.set_active_profile(profile_id)
        self.close()

    def add_profile(self):
        name, ok = QInputDialog.getText(self, "New Profile", "Profile name:")
        if not ok or not name.strip(): return
        clean = name.strip()
        pid = clean.lower().replace(" ", "_")
        if pid in self.manager.get_profiles():
            QMessageBox.warning(self, "Profiles", "A profile with that name already exists."); return
        picture, _ = QFileDialog.getOpenFileName(self, "Choose Profile Picture", "", "Images (*.png *.jpg *.jpeg *.webp)")
        self.manager.add_profile(pid, clean, picture or "", "")
        self.refresh()

    def edit_picture(self):
        pid = self.manager.get_active_id()
        picture, _ = QFileDialog.getOpenFileName(self, "Choose Profile Picture", "", "Images (*.png *.jpg *.jpeg *.webp)")
        if picture:
            p = self.manager.get_profiles().get(pid, {})
            p["picture"] = picture
            self.manager.upsert(pid, p)
            self.refresh()

    def delete_profile(self):
        pid = self.manager.get_active_id()
        if pid == "default":
            QMessageBox.information(self, "Profiles", "The default profile cannot be deleted."); return
        if QMessageBox.question(self, "Delete Profile", f"Delete the active profile '{self.manager.active().get('name', pid)}'?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.manager.delete(pid)
            self.refresh()
