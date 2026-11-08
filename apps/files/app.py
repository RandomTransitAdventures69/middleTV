import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileSystemModel, QTreeView, QMessageBox
from PySide6.QtCore import Qt, QDir, QUrl
from PySide6.QtGui import QDesktopServices
from apps.base_app import BaseApp
from core.config import BASE_DIR

START_PATH = Path.home() / "MiddleTV" / "Files"


class App(BaseApp):
    def __init__(self, wallpaper_callback=None):
        super().__init__("Files - MiddleTV")
        self.wallpaper_callback = wallpaper_callback
        START_PATH.mkdir(parents=True, exist_ok=True)
        self.current_path = START_PATH
        self.model = QFileSystemModel()
        self.view = QTreeView()
        self.path_label = QLabel()
        self.back_button = QPushButton("Up")
        self._build()
        self.apply_theme()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(30, 24, 30, 24)
        root.setSpacing(14)
        header = QHBoxLayout()
        title = QLabel("Files")
        title.setStyleSheet("font-size: 38px; font-weight: 700;")
        self.path_label.setObjectName("muted")
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.path_label)
        root.addLayout(header)

        self.model.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot)
        self.model.setRootPath(str(START_PATH))
        self.view.setModel(self.model)
        self.view.setRootIndex(self.model.index(str(START_PATH)))
        self.view.setFocusPolicy(Qt.StrongFocus)
        self.view.setSortingEnabled(True)
        for col in (1, 2, 3):
            self.view.setColumnHidden(col, True)
        self.view.doubleClicked.connect(self.open_item)
        root.addWidget(self.view, 1)

        controls = QHBoxLayout()
        self.back_button.setMinimumHeight(54)
        home_button = QPushButton("Home Folder")
        open_button = QPushButton("Open")
        refresh_button = QPushButton("Refresh")
        for b in (self.back_button, home_button, open_button, refresh_button):
            b.setMinimumHeight(54)
            b.setFocusPolicy(Qt.StrongFocus)
        self.back_button.clicked.connect(self.go_up)
        home_button.clicked.connect(self.go_home)
        open_button.clicked.connect(self.open_selected)
        refresh_button.clicked.connect(self.refresh)
        controls.addWidget(self.back_button)
        controls.addWidget(home_button)
        controls.addStretch()
        controls.addWidget(open_button)
        controls.addWidget(refresh_button)
        root.addLayout(controls)
        self.update_path()
        self.view.setFocus()

    def open_item(self, index):
        if not index.isValid():
            return
        path = Path(self.model.filePath(index))
        if path.is_dir():
            self.current_path = path
            self.view.setRootIndex(self.model.index(str(path)))
            self.update_path()
        else:
            self.open_file(path)

    def open_selected(self):
        idx = self.view.currentIndex()
        if idx.isValid():
            self.open_item(idx)

    def open_file(self, path):
        try:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
        except Exception as error:
            QMessageBox.warning(self, "Files", f"Could not open:\n\n{path}\n\n{error}")

    def go_up(self):
        if self.current_path == START_PATH:
            return
        parent = self.current_path.parent
        try:
            parent.relative_to(START_PATH)
        except ValueError:
            parent = START_PATH
        self.current_path = parent
        self.view.setRootIndex(self.model.index(str(parent)))
        self.update_path()

    def go_home(self):
        self.current_path = START_PATH
        self.view.setRootIndex(self.model.index(str(START_PATH)))
        self.update_path()

    def refresh(self):
        self.model.setRootPath(str(self.current_path))
        self.view.setRootIndex(self.model.index(str(self.current_path)))
        self.update_path()

    def update_path(self):
        self.path_label.setText(str(self.current_path))
        self.back_button.setEnabled(self.current_path != START_PATH)

    def handle_back(self):
        if self.current_path != START_PATH:
            self.go_up()
            return True
        self.close()
        return True
