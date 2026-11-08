import sys
from PySide6.QtWidgets import QApplication
from core.config import load_config
from core.launcher import Launcher
from core.navigation import NavigationController
from core.startup import StartupScreen
from core.theme import app_stylesheet


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(app_stylesheet(load_config().get("ui_theme", "modern")))

    nav = NavigationController()
    app.installEventFilter(nav)
    app._navigation_controller = nav

    holder = {}

    def show_launcher():
        launcher = Launcher()
        holder["launcher"] = launcher
        launcher.showFullScreen()

    startup = StartupScreen(show_launcher)
    holder["startup"] = startup
    startup.showFullScreen()
    startup.run()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
