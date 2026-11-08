import platform
import shutil
import sys
from PySide6.QtCore import Qt, QProcess
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QPlainTextEdit, QMessageBox, QLineEdit
from apps.base_app import BaseApp
from core.platform import IS_MAC, IS_WINDOWS, IS_LINUX


class ProcessView(BaseApp):
    def __init__(self, title):
        super().__init__(title)
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(self._read)
        self.process.finished.connect(self._done)
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(10)
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-size: 34px; font-weight: 700;")
        self.status = QLabel("Ready")
        self.status.setObjectName("muted")
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        root.addWidget(self.title_label)
        root.addWidget(self.status)
        root.addWidget(self.output, 1)
        controls = QHBoxLayout()
        self.start_btn = QPushButton("Start")
        self.cancel_btn = QPushButton("Cancel")
        close_btn = QPushButton("Back")
        self.start_btn.clicked.connect(self.start)
        self.cancel_btn.clicked.connect(self.cancel)
        close_btn.clicked.connect(self.close)
        for b in (self.start_btn, self.cancel_btn, close_btn):
            b.setMinimumHeight(50)
            controls.addWidget(b)
        root.addLayout(controls)

    def command(self):
        return None

    def confirm_text(self):
        return "Run this operation?"

    def start(self):
        cmd = self.command()
        if not cmd:
            QMessageBox.information(self, self.windowTitle(), "No supported package manager or update command was detected for this system.")
            return
        if QMessageBox.question(self, "Confirm", self.confirm_text() + "\n\n" + " ".join(cmd), QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
            return
        self.output.clear()
        self.status.setText("Running...")
        self.start_btn.setEnabled(False)
        self.process.start(cmd[0], cmd[1:])

    def _read(self):
        text = bytes(self.process.readAllStandardOutput()).decode("utf-8", errors="replace")
        if text:
            self.output.appendPlainText(text.rstrip("\n"))

    def _done(self, code, _status):
        self.start_btn.setEnabled(True)
        self.status.setText(f"Finished with exit code {code}.")
        if code == 0:
            self.output.appendPlainText("\nCompleted successfully.")
        else:
            self.output.appendPlainText(f"\nOperation failed (exit code {code}).")

    def cancel(self):
        if self.process.state() != QProcess.NotRunning:
            self.process.kill()
            self.status.setText("Cancelled.")


class SystemUpdates(ProcessView):
    def __init__(self):
        super().__init__("System Updates")
        self.status.setText(self.detect_text())

    def detect_text(self):
        cmd = self.command()
        if not cmd:
            return "No supported system package manager was detected."
        return "Detected update command: " + " ".join(cmd)

    def command(self):
        if IS_MAC:
            if shutil.which("brew"):
                return ["brew", "update"]
            return None
        if IS_WINDOWS:
            if shutil.which("winget"):
                return ["winget", "upgrade", "--all", "--include-unknown"]
            return None
        if shutil.which("apt-get"):
            # check mode only; privileged upgrade is explicit and can vary
            return ["apt-get", "-s", "upgrade"]
        if shutil.which("dnf"):
            return ["dnf", "check-update"]
        if shutil.which("pacman"):
            return ["pacman", "-Qu"]
        if shutil.which("zypper"):
            return ["zypper", "list-updates"]
        return None

    def confirm_text(self):
        if IS_LINUX and shutil.which("apt-get"):
            return "This will run a simulated APT upgrade check. Applying upgrades requires administrator authorization and a distribution-specific command."
        return "This will check for updates using the detected package manager. Applying changes may require administrator privileges."


class AppInstaller(BaseApp):
    def __init__(self):
        super().__init__("Application Installer")
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(self._read)
        self.process.finished.connect(self._done)
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(10)
        title = QLabel("Application Installer")
        title.setStyleSheet("font-size: 34px; font-weight: 700;")
        self.status = QLabel(self._backend_status())
        self.status.setObjectName("muted")
        self.status.setWordWrap(True)
        self.query = QLineEdit()
        self.query.setPlaceholderText("Package name (example: vlc, firefox)")
        self.query.setMinimumHeight(52)
        self.output = QPlainTextEdit(); self.output.setReadOnly(True)
        row = QHBoxLayout()
        for label, fn in [("Search", self.search), ("Install", self.install), ("Remove", self.remove), ("Back", self.close)]:
            b = QPushButton(label); b.setMinimumHeight(50); b.clicked.connect(fn); row.addWidget(b)
        root.addWidget(title); root.addWidget(self.status); root.addWidget(self.query); root.addWidget(self.output, 1); root.addLayout(row)

    def _backend(self):
        if IS_MAC and shutil.which("brew"): return "brew"
        if IS_WINDOWS and shutil.which("winget"): return "winget"
        for name in ("apt-cache", "apt-get", "dnf", "pacman"):
            if shutil.which(name.split('-')[0]) or shutil.which(name): return name
        return None

    def _backend_status(self):
        b = self._backend()
        if not b:
            return "No supported package manager detected. Install operations require a supported OS package manager."
        return f"Detected backend: {b}. Install/remove may require administrator authorization; MiddleTV will show the command before running."

    def _run(self, cmd, confirm=True):
        name = self.query.text().strip()
        if not name:
            QMessageBox.information(self, "Application Installer", "Enter a package name first."); return
        full = cmd(name)
        if not full:
            QMessageBox.information(self, "Application Installer", "This action is not supported by the detected backend."); return
        if confirm and QMessageBox.question(self, "Confirm", "Run this command?\n\n" + " ".join(full), QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
            return
        self.output.clear(); self.status.setText("Running: " + " ".join(full))
        self.process.start(full[0], full[1:])

    def search(self):
        b = self._backend(); name = self.query.text().strip()
        def cmd(_):
            if b == "brew": return ["brew", "search", name]
            if b == "winget": return ["winget", "search", name]
            if b and "apt" in b and shutil.which("apt-cache"): return ["apt-cache", "search", name]
            if shutil.which("dnf"): return ["dnf", "search", name]
            if shutil.which("pacman"): return ["pacman", "-Ss", name]
            return None
        self._run(cmd, confirm=False)

    def install(self):
        b = self._backend()
        def cmd(name):
            if b == "brew": return ["brew", "install", name]
            if b == "winget": return ["winget", "install", "--id", name, "-e"]
            if IS_LINUX and shutil.which("apt-get"): return ["pkexec", "apt-get", "install", "-y", name] if shutil.which("pkexec") else None
            if IS_LINUX and shutil.which("dnf"): return ["pkexec", "dnf", "install", "-y", name] if shutil.which("pkexec") else None
            if IS_LINUX and shutil.which("pacman"): return ["pkexec", "pacman", "-S", "--noconfirm", name] if shutil.which("pkexec") else None
            return None
        if IS_LINUX and cmd("x") is None and shutil.which("apt-get"):
            QMessageBox.information(self, "Application Installer", "A graphical privilege prompt (pkexec/polkit) was not found. Install/remove on Linux may need to be run from the MiddleTV Terminal with appropriate authorization.")
            return
        self._run(cmd)

    def remove(self):
        b = self._backend()
        def cmd(name):
            if b == "brew": return ["brew", "uninstall", name]
            if b == "winget": return ["winget", "uninstall", "--id", name, "-e"]
            if IS_LINUX and shutil.which("apt-get"): return ["pkexec", "apt-get", "remove", "-y", name] if shutil.which("pkexec") else None
            if IS_LINUX and shutil.which("dnf"): return ["pkexec", "dnf", "remove", "-y", name] if shutil.which("pkexec") else None
            if IS_LINUX and shutil.which("pacman"): return ["pkexec", "pacman", "-R", "--noconfirm", name] if shutil.which("pkexec") else None
            return None
        self._run(cmd)

    def _read(self):
        text = bytes(self.process.readAllStandardOutput()).decode("utf-8", errors="replace")
        if text:
            self.output.appendPlainText(text.rstrip("\n"))

    def _done(self, code, _status):
        self.output.appendPlainText(f"\n[exit {code}]")
        self.status.setText(self._backend_status())
