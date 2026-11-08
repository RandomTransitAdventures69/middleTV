
import sys

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QVBoxLayout,
)

from PySide6.QtCore import Qt

from core.remote_input import RemoteInput
from core.keyboard_remote import KeyboardRemote


class RemoteTest(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Mapple TV Remote Test")
        self.resize(600, 500)

        self.remote = RemoteInput(self)

        self.keyboard_remote = KeyboardRemote(
            self.remote,
            self
        )

        # Listen for remote actions
        self.remote.up.connect(
            lambda: self.show_action("UP")
        )

        self.remote.down.connect(
            lambda: self.show_action("DOWN")
        )

        self.remote.left.connect(
            lambda: self.show_action("LEFT")
        )

        self.remote.right.connect(
            lambda: self.show_action("RIGHT")
        )

        self.remote.select.connect(
            lambda: self.show_action("SELECT")
        )

        self.remote.back.connect(
            lambda: self.show_action("BACK")
        )

        self.remote.home.connect(
            lambda: self.show_action("HOME")
        )

        self.remote.menu.connect(
            lambda: self.show_action("MENU")
        )

        self.remote.play_pause.connect(
            lambda: self.show_action("PLAY / PAUSE")
        )

        self.remote.volume_up.connect(
            lambda: self.show_action("VOLUME UP")
        )

        self.remote.volume_down.connect(
            lambda: self.show_action("VOLUME DOWN")
        )

        self.installEventFilter(
            self.keyboard_remote
        )

        self.setup_ui()

    def setup_ui(self):

        layout = QVBoxLayout()

        title = QLabel(
            "MAPPLE TV REMOTE TEST"
        )

        title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        title.setStyleSheet(
            "font-size:32px;"
            "font-weight:bold;"
        )

        layout.addWidget(title)

        self.action_label = QLabel(
            "Press a key..."
        )

        self.action_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.action_label.setStyleSheet(
            "font-size:28px;"
        )

        layout.addWidget(
            self.action_label
        )

        instructions = QLabel(
            "↑ ↓ ← → = D-Pad\n"
            "Enter = Select\n"
            "Esc = Back\n"
            "H = Home\n"
            "M = Menu\n"
            "Space = Play/Pause\n"
            "+ / - = Volume"
        )

        instructions.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        instructions.setStyleSheet(
            "font-size:20px;"
        )

        layout.addWidget(
            instructions
        )

        self.setLayout(layout)

    def show_action(self, action):

        self.action_label.setText(
            f"REMOTE: {action}"
        )


if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = RemoteTest()

    window.show()

    sys.exit(
        app.exec()
    )

