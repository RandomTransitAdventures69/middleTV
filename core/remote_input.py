
from PySide6.QtCore import QObject, Signal


class RemoteInput(QObject):
    """
    Central input layer for Mapple TV OS.

    Hardware-specific input should eventually be translated
    into these standard TV actions.

    The rest of the OS should NOT need to know what kind
    of remote is being used.
    """

    up = Signal()
    down = Signal()
    left = Signal()
    right = Signal()

    select = Signal()
    back = Signal()
    home = Signal()
    menu = Signal()

    play_pause = Signal()

    volume_up = Signal()
    volume_down = Signal()
    mute = Signal()

    channel_up = Signal()
    channel_down = Signal()

    power = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.enabled = True


    def enable(self):
        """Enable remote input."""
        self.enabled = True


    def disable(self):
        """Disable remote input."""
        self.enabled = False


    def send(self, action):
        """
        Send a standard TV action.

        Example:

            remote.send("up")
            remote.send("select")
            remote.send("back")
        """

        if not self.enabled:
            return


        actions = {
            "up": self.up,
            "down": self.down,
            "left": self.left,
            "right": self.right,

            "select": self.select,
            "back": self.back,
            "home": self.home,
            "menu": self.menu,

            "play_pause": self.play_pause,

            "volume_up": self.volume_up,
            "volume_down": self.volume_down,
            "mute": self.mute,

            "channel_up": self.channel_up,
            "channel_down": self.channel_down,

            "power": self.power,
        }


        signal = actions.get(action)


        if signal is not None:
            signal.emit()


    def up_pressed(self):
        self.send("up")


    def down_pressed(self):
        self.send("down")


    def left_pressed(self):
        self.send("left")


    def right_pressed(self):
        self.send("right")


    def select_pressed(self):
        self.send("select")


    def back_pressed(self):
        self.send("back")


    def home_pressed(self):
        self.send("home")


    def menu_pressed(self):
        self.send("menu")


    def play_pause_pressed(self):
        self.send("play_pause")


    def volume_up_pressed(self):
        self.send("volume_up")


    def volume_down_pressed(self):
        self.send("volume_down")


    def mute_pressed(self):
        self.send("mute")


    def channel_up_pressed(self):
        self.send("channel_up")


    def channel_down_pressed(self):
        self.send("channel_down")


    def power_pressed(self):
        self.send("power")

