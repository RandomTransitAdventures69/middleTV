
import sys

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QComboBox,
    QCheckBox,
    QListWidget,
    QListWidgetItem,
    QStackedWidget,
    QSpinBox,
)

from PySide6.QtCore import Qt


class Installer(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "MiddleTV Installer"
        )

        self.setMinimumSize(
            1000,
            700
        )

        self.current_page = 0

        self.pages = []

        self.setup()


    # =========================================================
    # SETUP
    # =========================================================

    def setup(self):

        root = QVBoxLayout()

        root.setContentsMargins(
            60,
            50,
            60,
            40
        )

        root.setSpacing(
            25
        )


        # -----------------------------------------------------
        # Page stack
        # -----------------------------------------------------

        self.stack = QStackedWidget()

        root.addWidget(
            self.stack
        )


        # -----------------------------------------------------
        # Navigation
        # -----------------------------------------------------

        navigation = QHBoxLayout()

        navigation.setSpacing(
            15
        )


        self.back_button = QPushButton(
            "Back"
        )

        self.next_button = QPushButton(
            "Continue"
        )


        self.back_button.setMinimumSize(
            180,
            60
        )

        self.next_button.setMinimumSize(
            220,
            60
        )


        self.back_button.clicked.connect(
            self.previous_page
        )

        self.next_button.clicked.connect(
            self.next_page
        )


        navigation.addWidget(
            self.back_button
        )

        navigation.addStretch()

        navigation.addWidget(
            self.next_button
        )


        root.addLayout(
            navigation
        )


        self.setLayout(
            root
        )


        self.apply_style()

        self.build_pages()

        self.show_page(
            0
        )


    # =========================================================
    # PAGE HELPERS
    # =========================================================

    def create_page(
        self,
        title,
        description
    ):

        page = QWidget()

        layout = QVBoxLayout()

        layout.setContentsMargins(
            20,
            10,
            20,
            10
        )

        layout.setSpacing(
            25
        )


        title_label = QLabel(
            title
        )

        title_label.setAlignment(
            Qt.AlignCenter
        )

        title_label.setStyleSheet(
            """
            QLabel {
                color: white;
                font-size: 42px;
                font-weight: bold;
            }
            """
        )


        description_label = QLabel(
            description
        )

        description_label.setAlignment(
            Qt.AlignCenter
        )

        description_label.setWordWrap(
            True
        )

        description_label.setStyleSheet(
            """
            QLabel {
                color: rgba(255,255,255,175);
                font-size: 20px;
            }
            """
        )


        layout.addWidget(
            title_label
        )

        layout.addWidget(
            description_label
        )

        layout.addSpacing(
            15
        )


        page.setLayout(
            layout
        )


        self.pages.append(
            page
        )

        self.stack.addWidget(
            page
        )


        return page, layout


    def add_centered(
        self,
        layout,
        widget
    ):

        row = QHBoxLayout()

        row.addStretch()

        row.addWidget(
            widget
        )

        row.addStretch()

        layout.addLayout(
            row
        )


    # =========================================================
    # PAGES
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

        self.build_ready()


    # ---------------------------------------------------------
    # Welcome
    # ---------------------------------------------------------

    def build_welcome(self):

        page, layout = self.create_page(
            "Welcome to MiddleTV",
            "Let's get your TV set up."
        )


        label = QLabel(
            "This installer is currently a "
            "proof of concept.\n\n"
            "Nothing will actually be installed yet."
        )

        label.setAlignment(
            Qt.AlignCenter
        )

        label.setStyleSheet(
            """
            QLabel {
                color: white;
                font-size: 24px;
            }
            """
        )


        self.add_centered(
            layout,
            label
        )


    # ---------------------------------------------------------
    # Region
    # ---------------------------------------------------------

    def build_region(self):

        page, layout = self.create_page(
            "Region",
            "Choose your region and language."
        )


        region = QComboBox()

        region.addItems([
            "United States",
            "Canada",
            "United Kingdom",
            "Australia",
            "Other"
        ])

        region.setMinimumSize(
            400,
            55
        )


        language = QComboBox()

        language.addItems([
            "English",
            "Spanish",
            "French",
            "German",
            "Other"
        ])

        language.setMinimumSize(
            400,
            55
        )


        self.add_centered(
            layout,
            region
        )

        self.add_centered(
            layout,
            language
        )


    # ---------------------------------------------------------
    # Time
    # ---------------------------------------------------------

    def build_time(self):

        page, layout = self.create_page(
            "Time & Date",
            "Choose how MiddleTV should handle time."
        )


        timezone = QComboBox()

        timezone.addItems([
            "Eastern Time",
            "Central Time",
            "Mountain Time",
            "Pacific Time",
            "UTC"
        ])

        timezone.setMinimumSize(
            400,
            55
        )


        automatic = QCheckBox(
            "Set time automatically from the network"
        )

        automatic.setChecked(
            True
        )


        self.add_centered(
            layout,
            timezone
        )

        self.add_centered(
            layout,
            automatic
        )


    # ---------------------------------------------------------
    # Administrator
    # ---------------------------------------------------------

    def build_admin(self):

        page, layout = self.create_page(
            "Administrator Account",
            "Create the administrator account for MiddleTV.\n"
            "A keyboard is required."
        )


        username = QLineEdit()

        username.setPlaceholderText(
            "Username"
        )

        username.setMinimumSize(
            450,
            55
        )


        password = QLineEdit()

        password.setPlaceholderText(
            "Password"
        )

        password.setEchoMode(
            QLineEdit.Password
        )

        password.setMinimumSize(
            450,
            55
        )


        confirm = QLineEdit()

        confirm.setPlaceholderText(
            "Confirm password"
        )

        confirm.setEchoMode(
            QLineEdit.Password
        )

        confirm.setMinimumSize(
            450,
            55
        )


        self.add_centered(
            layout,
            username
        )

        self.add_centered(
            layout,
            password
        )

        self.add_centered(
            layout,
            confirm
        )


    # ---------------------------------------------------------
    # Internet
    # ---------------------------------------------------------

    def build_internet(self):

        page, layout = self.create_page(
            "Internet",
            "MiddleTV can work without Internet access,\n"
            "but some services may require it."
        )


        status = QLabel(
            "Network status\n\n"
            "● Not tested"
        )

        status.setAlignment(
            Qt.AlignCenter
        )

        status.setStyleSheet(
            """
            QLabel {
                color: white;
                font-size: 24px;
            }
            """
        )


        self.add_centered(
            layout,
            status
        )


    # ---------------------------------------------------------
    # Web UI
    # ---------------------------------------------------------

    def build_web_ui(self):

        page, layout = self.create_page(
            "Web Interface",
            "Allow MiddleTV to be configured from another device."
        )


        enabled = QCheckBox(
            "Enable MiddleTV Web UI"
        )

        enabled.setChecked(
            True
        )


        port = QSpinBox()

        port.setRange(
            1,
            65535
        )

        port.setValue(
            8080
        )

        port.setMinimumSize(
            250,
            55
        )


        self.add_centered(
            layout,
            enabled
        )

        self.add_centered(
            layout,
            port
        )


    # ---------------------------------------------------------
    # Remote / CEC
    # ---------------------------------------------------------

    def build_remote(self):

        page, layout = self.create_page(
            "Remote Control",
            "Choose how MiddleTV will be controlled."
        )


        keyboard = QCheckBox(
            "Keyboard"
        )

        keyboard.setChecked(
            True
        )


        cec = QCheckBox(
            "HDMI-CEC"
        )

        remote = QCheckBox(
            "USB / Bluetooth Remote"
        )


        self.add_centered(
            layout,
            keyboard
        )

        self.add_centered(
            layout,
            cec
        )

        self.add_centered(
            layout,
            remote
        )


        shortcut = QLabel(
            "Emergency kiosk escape:\n"
            "Ctrl + Shift + Esc"
        )

        shortcut.setAlignment(
            Qt.AlignCenter
        )

        shortcut.setStyleSheet(
            """
            QLabel {
                color: rgba(255,255,255,150);
                font-size: 18px;
            }
            """
        )


        self.add_centered(
            layout,
            shortcut
        )


    # ---------------------------------------------------------
    # Media
    # ---------------------------------------------------------

    def build_media(self):

        page, layout = self.create_page(
            "Media Servers",
            "Connect MiddleTV to Jellyfin or Plex servers."
        )


        jellyfin = QCheckBox(
            "Jellyfin"
        )

        plex = QCheckBox(
            "Plex"
        )


        jellyfin.setChecked(
            True
        )


        add_server = QPushButton(
            "Add Server"
        )

        add_server.setMinimumSize(
            300,
            55
        )


        self.add_centered(
            layout,
            jellyfin
        )

        self.add_centered(
            layout,
            plex
        )

        self.add_centered(
            layout,
            add_server
        )


    # ---------------------------------------------------------
    # Facts
    # ---------------------------------------------------------

    def build_facts(self):

        page, layout = self.create_page(
            "Loading Screen Facts",
            "Choose what MiddleTV can show while applications load."
        )


        categories = [
            "CompTIA / IT",
            "Trains",
            "History",
            "Geography",
            "Science",
            "Aviation",
            "Transit",
            "Computers",
            "Random",
            "Custom",
        ]


        facts = QListWidget()

        facts.setMinimumSize(
            500,
            260
        )


        for category in categories:

            item = QListWidgetItem(
                category
            )

            item.setCheckState(
                Qt.Checked
            )

            facts.addItem(
                item
            )


        self.add_centered(
            layout,
            facts
        )


    # ---------------------------------------------------------
    # Ready
    # ---------------------------------------------------------

    def build_ready(self):

        page, layout = self.create_page(
            "You're Ready",
            "MiddleTV has everything it needs to begin installation."
        )


        summary = QLabel(
            "Region: United States\n"
            "Language: English\n"
            "Administrator: Configured\n"
            "Web UI: Enabled\n"
            "Remote: Keyboard\n"
            "Media: Jellyfin\n"
            "Facts: Completely Random™"
        )

        summary.setAlignment(
            Qt.AlignCenter
        )

        summary.setStyleSheet(
            """
            QLabel {
                color: white;
                font-size: 21px;
                line-height: 150%;
            }
            """
        )


        self.add_centered(
            layout,
            summary
        )


        self.final_install = QPushButton(
            "Install MiddleTV™"
        )

        self.final_install.setMinimumSize(
            300,
            65
        )

        self.final_install.clicked.connect(
            self.install_poc
        )


        self.add_centered(
            layout,
            self.final_install
        )


    # =========================================================
    # NAVIGATION
    # =========================================================

    def show_page(
        self,
        index
    ):

        self.current_page = index

        self.stack.setCurrentIndex(
            index
        )


        self.back_button.setEnabled(
            index > 0
        )


        if index >= len(
            self.pages
        ) - 1:

            self.next_button.setText(
                "Finish"
            )

        else:

            self.next_button.setText(
                "Continue"
            )


    def next_page(self):

        if self.current_page < (
            len(self.pages) - 1
        ):

            self.show_page(
                self.current_page + 1
            )

        else:

            self.install_poc()


    def previous_page(self):

        if self.current_page > 0:

            self.show_page(
                self.current_page - 1
            )


    # =========================================================
    # POC INSTALL
    # =========================================================

    def install_poc(self):

        print(
            "MIDDLETV INSTALL WOULD HAPPEN HERE™"
        )

        self.next_button.setText(
            "Done™"
        )

        self.next_button.setEnabled(
            False
        )

        self.back_button.setEnabled(
            False


        )


    # =========================================================
    # STYLE
    # =========================================================

    def apply_style(self):

        self.setStyleSheet(
            """
            QWidget {
                background-color: #101014;
            }

            QPushButton {

                color: white;

                background-color:
                    rgba(35, 35, 40, 230);

                border:
                    2px solid
                    rgba(255,255,255,55);

                border-radius:
                    16px;

                padding:
                    10px 20px;

                font-size:
                    20px;

                font-weight:
                    bold;
            }

            QPushButton:hover {

                background-color:
                    rgba(50,75,105,235);

                border:
                    3px solid
                    rgba(90,180,255,230);
            }

            QPushButton:focus {

                background-color:
                    rgba(45,85,130,240);

                border:
                    4px solid
                    rgba(90,190,255,255);
            }

            QLineEdit,
            QComboBox,
            QSpinBox {

                color: white;

                background-color:
                    rgba(30,30,35,230);

                border:
                    2px solid
                    rgba(255,255,255,55);

                border-radius:
                    14px;

                padding:
                    8px 15px;

                font-size:
                    19px;
            }

            QLineEdit:focus,
            QComboBox:focus,
            QSpinBox:focus {

                border:
                    3px solid
                    rgba(90,190,255,255);
            }

            QCheckBox {

                color: white;

                font-size: 20px;

                spacing: 12px;
            }

            QListWidget {

                color: white;

                background-color:
                    rgba(25,25,30,230);

                border:
                    2px solid
                    rgba(255,255,255,55);

                border-radius:
                    16px;

                font-size:
                    19px;
            }
            """
        )


# =============================================================
# MAIN
# =============================================================

if __name__ == "__main__":

    app = QApplication(
        sys.argv
    )

    window = Installer()

    window.show()

    sys.exit(
        app.exec()
    )
