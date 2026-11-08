# MiddleTV™

MiddleTV is a custom fullscreen, TV-style operating system launcher built with Python and PySide6. It turns a standard computer into a dedicated, living-room-ready Smart TV experience.

![MiddleTV Screenshot](https://cdn.discordapp.com/attachments/1537925089406754866/1540834983046811708/IMG_0878.png?ex=6a8e08e7&is=6a8cb767&hm=a0cbd55e3e6098d7e23888f1e38271c85d9595ca792fa9276636d89ec34b3631)

---

## 📺 Overview

MiddleTV bridges the gap between traditional desktop operating systems and modern TV interfaces. Designed from the ground up for big-screen navigation, it minimizes desktop clutter and replaces standard mouse/keyboard interactions with simple, focus-driven control tailored for remotes and gamepads.

### Core Features
* **Fullscreen TV Launcher:** High-contrast, large-format interface optimized for distance viewing.
* **Profile System:** Multi-user support featuring customizable profile pictures and seamless switching.
* **Media Integration:** Built-in integrations for Jellyfin and YouTube.
* **Utility Hub:** Embedded features like Settings, File Navigation, and Flight Tracker™.
* **Customization:** Dynamic wallpaper support and system-wide theme adjustments.
* **Remote & Keyboard Friendly:** First-class spatial navigation designed for arrow keys, standard media remotes, and controllers.
* **First-Run OOBE:** A TV-native Out-Of-Box Experience to guide users through initial setup.

---

## 🛠️ Architecture & Tech Stack

MiddleTV is constructed using standard, cross-platform Python technologies:

* **Language:** Python 3.10+
* **GUI Framework:** PySide6 (Qt for Python)
* **Configuration:** JSON-backed persistent configuration stores

### Entry Point (nerd talk)

The application initializes as a full-screen Qt process:

```python
import sys
from PySide6.QtWidgets import QApplication
from core.launcher import Launcher

def main():
    app = QApplication(sys.argv)

    launcher = Launcher()
    launcher.showFullScreen()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()

    ```
    ## idk man i didnt code it chatgpt+claude (that was fun to work out) did