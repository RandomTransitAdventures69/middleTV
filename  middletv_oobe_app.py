
import sys
import json
import hashlib
import secrets

from pathlib import Path

from PySide6.QtCore import Qt, QTime
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
    QComboBox,
    QCheckBox,
    QLineEdit,
    QSpinBox,
    QListWidget,
    QListWidgetItem,
)


class App(QWidget):
    """
    MiddleTV™ Out-of-Box Experience.

    Proof-of-concept first-run wizard:
        Welcome
        Region
        Time
        Administrator
        Internet
        Web UI
        Remote / CEC
        Jellyfin / Plex
        Loading Facts
        Finish

    The UI is fully usable now. On Finish it writes config/oobe.json.
    It does not install packages, create Linux users, or modify the OS.
    """

    def __init__(self, wallpaper_callback=None):
        super().__init__()

        self.wallpaper_callback = wallpaper_callback

        self.setWindowTitle("MiddleTV™ Setup")
        self.setMinimumSize(1100, 700)

        self.page_index = 0
        self.pages = []

        self.data = {
            "region": "United States",
            "language": "English",
            "timezone": "Eastern Time",
            "automatic_time": True,

            "admin": {
                "username": "",
                "password_hash": "",
                "is_admin": True,
            },

            "internet": {
                "mode": "Not configured",
            },

            "web_ui": {
                "enabled": True,
                "port": 8080,
            },

            "remote": {
                "keyboard": True,
                "cec": True,
                "usb_remote": False,
                "bluetooth_remote": False,
            },

            "media": {
                "jellyfin": True,
                "plex": False,
            },

            "facts": {
                "comptia": True,
                "trains": True,
                "history": True,
                "geography": True,
                "science": True,
                "aviation": True,
                "transit": True,
                "computers": True,
                "random": True,
                "custom": True,
            },
        }

        self.setup()

    # =========================================================
    # SETUP
    # =========================================================

    def setup(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(60, 45, 60, 40)
        root.setSpacing(20)

        self.stack = QStackedWidget()
        root.addWidget(self.stack, 1)

        navigation = QHBoxLayout()
        navigation.setSpacing(14)

        self.back_button = QPushButton("Back")
        self.next_button = QPushButton("Continue")

        self.back_button.setMinimumSize(190, 60)
        self.next_button.setMinimumSize(230, 60)

        self.back_button.clicked.connect(self.previous_page)
        self.next_button.clicked.connect(self.next_page)

        navigation.addWidget(self.back_button)
        navigation.addStretch()
        navigation.addWidget(self.next_button)

        root.addLayout(navigation)

        self.apply_style()
        self.build_pages()
        self.show_page(0)

    # =========================================================
    # PAGE HELPERS
    # =========================================================

    def page(self, title, subtitle):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(25, 10, 25, 10)
        layout.setSpacing(22)

        heading = QLabel(title)
        heading.setObjectName("pageTitle")
        heading.setAlignment(Qt.AlignCenter)

        description = QLabel(subtitle)
        description.setObjectName("pageDescription")
        description.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)

        layout.addWidget(heading)
        layout.addWidget(description)
        layout.addSpacing(10)

        self.pages.append(widget)
        self.stack.addWidget(widget)

        return widget, layout

    def centered(self, layout, widget):
        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(widget)
        row.addStretch()
        layout.addLayout(row)

    # =========================================================
    # BUILD PAGES
    # =========================================================

    def build_pages(self):
        self.build_welcome()
        self.build_region()
        self.build_time()
        self.build_admin()
        self.build_internet()
        self.build_web_ui()
        self.build_remote()
        self.build_media()
        self.build_facts()
        self.build_finish()

    # ---------------------------------------------------------
    # Welcome
    # ---------------------------------------------------------

    def build_welcome(self):
        page, layout = self.page(
            "Welcome to MiddleTV™",
            "Let's get your TV set up."
        )

        logo = QLabel("middleTV OS")
        logo.setObjectName("logo")

        sub = QLabel(
            "A TV-first Linux experience for media, remotes, "
            "users, and questionable loading facts™."
        )
        sub.setObjectName("bodyText")
        sub.setAlignment(Qt.AlignCenter)
        sub.setWordWrap(True)

        self.centered(layout, logo)
        self.centered(layout, sub)

        hint = QLabel(
            "Use Arrow Keys + Enter to navigate. "
            "Escape goes back."
        )
        hint.setObjectName("muted")
        hint.setAlignment(Qt.AlignCenter)

        self.centered(layout, hint)
        layout.addStretch()

    # ---------------------------------------------------------
    # Region
    # ---------------------------------------------------------

    def build_region(self):
        page, layout = self.page(
            "Region",
            "Choose the region and language used by MiddleTV."
        )

        region = QComboBox()
        region.addItems([
            "United States",
            "Canada",
            "United Kingdom",
            "Australia",
            "New Zealand",
            "Other",
        ])
        region.setCurrentText(self.data["region"])
        region.setMinimumSize(440, 58)

        language = QComboBox()
        language.addItems([
            "English",
            "Spanish",
            "French",
            "German",
            "Other",
        ])
        language.setCurrentText(self.data["language"])
        language.setMinimumSize(440, 58)

        self.region_combo = region
        self.language_combo = language

        self.centered(layout, region)
        self.centered(layout, language)

        label1 = QLabel("Region")
        label2 = QLabel("Language")

        label1.setObjectName("fieldLabel")
        label2.setObjectName("fieldLabel")

        self.centered(layout, label1)
        self.centered(layout, label2)

        layout.addStretch()

    # ---------------------------------------------------------
    # Time
    # ---------------------------------------------------------

    def build_time(self):
        page, layout = self.page(
            "Time & Date",
            "Choose how MiddleTV should handle the system clock."
        )

        timezone = QComboBox()
        timezone.addItems([
            "Eastern Time",
            "Central Time",
            "Mountain Time",
            "Pacific Time",
            "Alaska Time",
            "Hawaii Time",
            "UTC",
        ])
        timezone.setCurrentText(self.data["timezone"])
        timezone.setMinimumSize(440, 58)

        automatic = QCheckBox(
            "Set time automatically from the network"
        )
        automatic.setChecked(self.data["automatic_time"])

        clock = QLabel(
            "Current time: " + QTime.currentTime().toString("h:mm AP")
        )
        clock.setObjectName("bodyText")
        clock.setAlignment(Qt.AlignCenter)

        self.timezone_combo = timezone
        self.automatic_time = automatic

        self.centered(layout, timezone)
        self.centered(layout, clock)
        self.centered(layout, automatic)

        layout.addStretch()

    # ---------------------------------------------------------
    # Administrator
    # ---------------------------------------------------------

    def build_admin(self):
        page, layout = self.page(
            "Create Administrator",
            "A physical keyboard is required to create the "
            "administrator account."
        )

        warning = QLabel(
            "This account will manage MiddleTV settings, users, "
            "servers, and system configuration."
        )
        warning.setObjectName("warning")
        warning.setAlignment(Qt.AlignCenter)
        warning.setWordWrap(True)

        self.admin_username = QLineEdit()
        self.admin_username.setPlaceholderText("Administrator username")
        self.admin_username.setMinimumSize(470, 58)

        self.admin_password = QLineEdit()
        self.admin_password.setPlaceholderText("Password")
        self.admin_password.setEchoMode(QLineEdit.Password)
        self.admin_password.setMinimumSize(470, 58)

        self.admin_confirm = QLineEdit()
        self.admin_confirm.setPlaceholderText("Confirm password")
        self.admin_confirm.setEchoMode(QLineEdit.Password)
        self.admin_confirm.setMinimumSize(470, 58)

        self.centered(layout, warning)
        self.centered(layout, self.admin_username)
        self.centered(layout, self.admin_password)
        self.centered(layout, self.admin_confirm)

        self.admin_username.setFocus()

        layout.addStretch()

    # ---------------------------------------------------------
    # Internet
    # ---------------------------------------------------------

    def build_internet(self):
        page, layout = self.page(
            "Internet",
            "MiddleTV can work offline, but Internet access enables "
            "updates, weather, media services, and other features."
        )

        status = QLabel(
            "● Not tested"
        )
        status.setObjectName("status")
        status.setAlignment(Qt.AlignCenter)

        ethernet = QPushButton("Ethernet")
        wifi = QPushButton("Wi-Fi")
        skip = QPushButton("Continue Offline")

        for button in (ethernet, wifi, skip):
            button.setMinimumSize(260, 58)

        ethernet.clicked.connect(
            lambda: status.setText("● Ethernet selected")
        )
        wifi.clicked.connect(
            lambda: status.setText("● Wi-Fi selected")
        )
        skip.clicked.connect(
            lambda: status.setText("● Offline mode selected")
        )

        self.centered(layout, status)
        self.centered(layout, ethernet)
        self.centered(layout, wifi)
        self.centered(layout, skip)

        layout.addStretch()

    # ---------------------------------------------------------
    # Web UI
    # ---------------------------------------------------------

    def build_web_ui(self):
        page, layout = self.page(
            "Web Interface",
            "Allow MiddleTV to be configured from another device."
        )

        enabled = QCheckBox(
            "Enable MiddleTV Web UI"
        )
        enabled.setChecked(self.data["web_ui"]["enabled"])

        port = QSpinBox()
        port.setRange(1, 65535)
        port.setValue(self.data["web_ui"]["port"])
        port.setMinimumSize(250, 58)

        self.web_enabled = enabled
        self.web_port = port

        self.centered(layout, enabled)
        self.centered(layout, port)

        layout.addStretch()

    # ---------------------------------------------------------
    # Remote / CEC
    # ---------------------------------------------------------

    def build_remote(self):
        page, layout = self.page(
            "Remote Control & HDMI-CEC",
            "Choose how MiddleTV will be controlled."
        )

        keyboard = QCheckBox("Keyboard")
        keyboard.setChecked(True)

        cec = QCheckBox("HDMI-CEC")
        cec.setChecked(True)

        usb = QCheckBox("USB / Bluetooth Remote")
        usb.setChecked(False)

        self.remote_keyboard = keyboard
        self.remote_cec = cec
        self.remote_usb = usb

        self.centered(layout, keyboard)
        self.centered(layout, cec)
        self.centered(layout, usb)

        shortcut = QLabel(
            "Development / kiosk escape: Ctrl + Shift + Esc"
        )
        shortcut.setObjectName("muted")
        shortcut.setAlignment(Qt.AlignCenter)

        self.centered(layout, shortcut)

        layout.addStretch()

    # ---------------------------------------------------------
    # Media
    # ---------------------------------------------------------

    def build_media(self):
        page, layout = self.page(
            "Media Servers",
            "Choose which media platforms MiddleTV should configure."
        )

        jellyfin = QCheckBox("Jellyfin")
        jellyfin.setChecked(True)

        plex = QCheckBox("Plex")
        plex.setChecked(False)

        add_note = QLabel(
            "Server addresses can be configured after setup."
        )
        add_note.setObjectName("muted")
        add_note.setAlignment(Qt.AlignCenter)

        self.media_jellyfin = jellyfin
        self.media_plex = plex

        self.centered(layout, jellyfin)
        self.centered(layout, plex)
        self.centered(layout, add_note)

        layout.addStretch()

    # ---------------------------------------------------------
    # Facts
    # ---------------------------------------------------------

    def build_facts(self):
        page, layout = self.page(
            "Loading Screen Facts™",
            "Choose the kinds of facts MiddleTV may show while apps load."
        )

        categories = [
            ("CompTIA / IT", "comptia"),
            ("Trains", "trains"),
            ("History", "history"),
            ("Geography", "geography"),
            ("Science", "science"),
            ("Aviation", "aviation"),
            ("Transit", "transit"),
            ("Computers", "computers"),
            ("Random", "random"),
            ("Custom", "custom"),
        ]

        facts = QListWidget()
        facts.setMinimumSize(500, 300)
        facts.setFocusPolicy(Qt.StrongFocus)

        for label, key in categories:
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, key)
            item.setCheckState(
                Qt.Checked
                if self.data["facts"].get(key, True)
                else Qt.Unchecked
            )
            facts.addItem(item)

        self.fact_list = facts
        self.centered(layout, facts)

        random_hint = QLabel(
            "The default behavior can be completely random™."
        )
        random_hint.setObjectName("muted")
        random_hint.setAlignment(Qt.AlignCenter)

        self.centered(layout, random_hint)
        layout.addStretch()

    # ---------------------------------------------------------
    # Finish
    # ---------------------------------------------------------

    def build_finish(self):
        page, layout = self.page(
            "You're Ready™",
            "Review complete. MiddleTV can now finish setup."
        )

        self.summary = QLabel()
        self.summary.setObjectName("summary")
        self.summary.setAlignment(Qt.AlignCenter)
        self.summary.setWordWrap(True)

        self.centered(layout, self.summary)

        self.finish_button = QPushButton(
            "Finish Setup"
        )
        self.finish_button.setMinimumSize(300, 65)
        self.finish_button.clicked.connect(
            self.finish_setup
        )

        self.centered(layout, self.finish_button)
        layout.addStretch()

    # =========================================================
    # VALIDATION / DATA
    # =========================================================

    def hash_password(self, password):
        salt = secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            200_000,
        )
        return (
            salt.hex()
            + ":"
            + digest.hex()
        )

    def validate_admin(self):
        username = self.admin_username.text().strip()
        password = self.admin_password.text()
        confirm = self.admin_confirm.text()

        if not username:
            return False, "Enter an administrator username."

        if not password:
            return False, "Enter an administrator password."

        if password != confirm:
            return False, "The passwords do not match."

        if len(password) < 8:
            return False, "Use at least 8 characters for the password."

        self.data["admin"]["username"] = username
        self.data["admin"]["password_hash"] = (
            self.hash_password(password)
        )

        return True, ""

    def collect_data(self):
        self.data["region"] = self.region_combo.currentText()
        self.data["language"] = self.language_combo.currentText()
        self.data["timezone"] = self.timezone_combo.currentText()
        self.data["automatic_time"] = self.automatic_time.isChecked()

        self.data["web_ui"]["enabled"] = (
            self.web_enabled.isChecked()
        )
        self.data["web_ui"]["port"] = (
            self.web_port.value()
        )

        self.data["remote"]["keyboard"] = (
            self.remote_keyboard.isChecked()
        )
        self.data["remote"]["cec"] = (
            self.remote_cec.isChecked()
        )
        self.data["remote"]["usb_remote"] = (
            self.remote_usb.isChecked()
        )

        self.data["media"]["jellyfin"] = (
            self.media_jellyfin.isChecked()
        )
        self.data["media"]["plex"] = (
            self.media_plex.isChecked()
        )

        for index in range(self.fact_list.count()):
            item = self.fact_list.item(index)
            key = item.data(Qt.UserRole)
            self.data["facts"][key] = (
                item.checkState() == Qt.Checked
            )

    # =========================================================
    # NAVIGATION
    # =========================================================

    def show_page(self, index):
        self.page_index = index
        self.stack.setCurrentIndex(index)

        self.back_button.setEnabled(index > 0)

        if index == len(self.pages) - 1:
            self.next_button.setText("Finish")
            self.collect_data()
            self.update_summary()
        else:
            self.next_button.setText("Continue")

    def next_page(self):
        if self.page_index == 3:
            ok, message = self.validate_admin()
            if not ok:
                self.summary_message(message)
                return

        if self.page_index < len(self.pages) - 1:
            self.show_page(self.page_index + 1)
        else:
            self.finish_setup()

    def previous_page(self):
        if self.page_index > 0:
            self.show_page(self.page_index - 1)

    def summary_message(self, message):
        label = QLabel(message, self)
        label.setObjectName("errorOverlay")
        label.setAlignment(Qt.AlignCenter)
        label.show()
        label.raise_()

        # Keep the message visible without building another dialog.
        label.adjustSize()
        label.move(
            (self.width() - label.width()) // 2,
            self.height() // 2 - 25
        )

        label.setAutoFillBackground(False)

    def update_summary(self):
        admin_name = (
            self.data["admin"]["username"]
            or "Not configured"
        )

        media = []
        if self.data["media"]["jellyfin"]:
            media.append("Jellyfin")
        if self.data["media"]["plex"]:
            media.append("Plex")

        if not media:
            media_text = "None"
        else:
            media_text = " + ".join(media)

        enabled_facts = sum(
            1
            for enabled in self.data["facts"].values()
            if enabled
        )

        self.summary.setText(
            f"Region: {self.data['region']}\\n"
            f"Language: {self.data['language']}\\n"
            f"Time zone: {self.data['timezone']}\\n"
            f"Administrator: {admin_name}\\n"
            f"Web UI: "
            f"{'Enabled' if self.data['web_ui']['enabled'] else 'Disabled'}\\n"
            f"Remote / CEC: "
            f"{'Enabled' if self.data['remote']['cec'] else 'Disabled'}\\n"
            f"Media: {media_text}\\n"
            f"Fact lists: {enabled_facts} enabled"
        )

    # =========================================================
    # FINISH / SAVE
    # =========================================================

    def config_file(self):
        config_dir = (
            Path(__file__).resolve().parent.parent.parent
            / "config"
        )
        config_dir.mkdir(
            parents=True,
            exist_ok=True
        )
        return config_dir / "oobe.json"

    def finish_setup(self):
        self.collect_data()

        self.data["setup_complete"] = True

        try:
            with open(self.config_file(), "w") as file:
                json.dump(
                    self.data,
                    file,
                    indent=4
                )
        except OSError as error:
            self.summary_message(
                f"Could not save setup: {error}"
            )
            return

        print("MIDDLETV OOBE COMPLETE™")

        self.close()

    # =========================================================
    # STYLE
    # =========================================================

    def apply_style(self):
        self.setStyleSheet("""
            QWidget {
                background: #06131b;
                color: white;
                font-family: Arial;
            }

            QLabel#pageTitle {
                font-size: 44px;
                font-weight: 800;
            }

            QLabel#pageDescription {
                color: rgba(255,255,255,165);
                font-size: 20px;
            }

            QLabel#logo {
                color: white;
                font-size: 54px;
                font-weight: 900;
            }

            QLabel#bodyText {
                color: rgba(255,255,255,210);
                font-size: 21px;
                max-width: 760px;
            }

            QLabel#muted {
                color: rgba(255,255,255,115);
                font-size: 16px;
            }

            QLabel#warning {
                color: #ffd27a;
                font-size: 17px;
                max-width: 720px;
            }

            QLabel#summary {
                color: white;
                background: rgba(20,35,45,225);
                border: 2px solid rgba(255,255,255,35);
                border-radius: 20px;
                padding: 28px;
                font-size: 20px;
                min-width: 560px;
            }

            QLabel#status {
                color: #79c8ff;
                font-size: 24px;
                font-weight: 700;
            }

            QLabel#fieldLabel {
                color: rgba(255,255,255,130);
                font-size: 14px;
            }

            QLineEdit,
            QComboBox,
            QSpinBox {
                color: white;
                background: rgba(25,35,45,235);
                border: 2px solid rgba(255,255,255,45);
                border-radius: 15px;
                padding: 10px 15px;
                font-size: 19px;
            }

            QLineEdit:focus,
            QComboBox:focus,
            QSpinBox:focus {
                background: rgba(22,100,155,235);
                border: 4px solid #79c8ff;
            }

            QCheckBox {
                color: white;
                font-size: 20px;
                spacing: 12px;
                padding: 8px;
            }

            QCheckBox:focus {
                color: #ffffff;
                background: rgba(22,100,155,210);
                border: 3px solid #79c8ff;
                border-radius: 12px;
            }

            QListWidget {
                color: white;
                background: rgba(20,32,42,235);
                border: 2px solid rgba(255,255,255,35);
                border-radius: 20px;
                padding: 10px;
                font-size: 19px;
            }

            QListWidget::item {
                padding: 12px;
                border-radius: 11px;
            }

            QListWidget::item:selected {
                background: #1687e8;
                border: 3px solid #79c8ff;
            }

            QPushButton {
                color: white;
                background: rgba(25,35,45,235);
                border: 2px solid rgba(255,255,255,45);
                border-radius: 16px;
                padding: 10px 18px;
                font-size: 19px;
                font-weight: 700;
            }

            QPushButton:hover {
                background: rgba(45,70,100,235);
                border: 3px solid rgba(90,180,255,230);
            }

            QPushButton:focus {
                background: #1687e8;
                border: 4px solid #79c8ff;
            }

            QPushButton:disabled {
                color: rgba(255,255,255,70);
                background: rgba(25,25,30,150);
                border: 2px solid rgba(255,255,255,18);
            }
        """)

    # =========================================================
    # KEYBOARD
    # =========================================================

    def keyPressEvent(self, event):
        # Development/kiosk escape.
        if (
            event.key() == Qt.Key_Escape
            and event.modifiers()
            == (Qt.ControlModifier | Qt.ShiftModifier)
        ):
            self.close()
            return

        # Normal Back.
        if event.key() == Qt.Key_Escape:
            self.previous_page()
            return

        super().keyPressEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = App()
    window.showFullScreen()

    sys.exit(app.exec())
