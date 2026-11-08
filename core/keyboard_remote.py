
from PySide6.QtCore import QObject, QEvent, Qt


class KeyboardRemote(QObject):
    """
    Development keyboard remote for Mapple TV OS.

    Converts keyboard keys into RemoteInput actions.
    """

    def __init__(self, remote_input, parent=None):
        super().__init__(parent)

        self.remote = remote_input

    def eventFilter(self, obj, event):

        if event.type() != QEvent.Type.KeyPress:
            return False

        key = event.key()

        # D-pad
        if key == Qt.Key.Key_Up:
            self.remote.up_pressed()
            return True

        if key == Qt.Key.Key_Down:
            self.remote.down_pressed()
            return True

        if key == Qt.Key.Key_Left:
            self.remote.left_pressed()
            return True

        if key == Qt.Key.Key_Right:
            self.remote.right_pressed()
            return True

        # Select
        if key in (
            Qt.Key.Key_Return,
            Qt.Key.Key_Enter
        ):
            self.remote.select_pressed()
            return True

        # Back
        if key == Qt.Key.Key_Escape:
            self.remote.back_pressed()
            return True

        # Home
        if key == Qt.Key.Key_H:
            self.remote.home_pressed()
            return True

        # Menu
        if key == Qt.Key.Key_M:
            self.remote.menu_pressed()
            return True

        # Play / pause
        if key == Qt.Key.Key_Space:
            self.remote.play_pause_pressed()
            return True

        # Volume up
        if key in (
            Qt.Key.Key_Plus,
            Qt.Key.Key_Equal
        ):
            self.remote.volume_up_pressed()
            return True

        # Volume down
        if key == Qt.Key.Key_Minus:
            self.remote.volume_down_pressed()
            return True

        return False
