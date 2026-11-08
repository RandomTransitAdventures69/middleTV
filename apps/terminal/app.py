import os
import shutil
from pathlib import Path
from PySide6.QtCore import Qt, QProcess
from PySide6.QtGui import QTextCursor, QKeySequence, QShortcut
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPlainTextEdit, QLineEdit, QPushButton, QMessageBox
from apps.base_app import BaseApp


class App(BaseApp):
    def __init__(self):
        super().__init__("Terminal - MiddleTV")
        self.history = []
        self.history_index = 0
        self.cwd = str(Path.home())
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(self._read_output)
        self.process.finished.connect(self._finished)
        self._build()
        self._banner()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(10)
        header = QHBoxLayout()
        title = QLabel("Terminal")
        title.setStyleSheet("font-size: 34px; font-weight: 700;")
        self.cwd_label = QLabel(self.cwd)
        self.cwd_label.setObjectName("muted")
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_output)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.cwd_label)
        header.addWidget(clear_btn)
        root.addLayout(header)

        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setMinimumHeight(300)
        root.addWidget(self.output, 1)

        input_row = QHBoxLayout()
        prompt = QLabel("$")
        prompt.setStyleSheet("font-size: 20px; font-weight: 700;")
        self.input = QLineEdit()
        self.input.setPlaceholderText("Enter command")
        self.input.setMinimumHeight(54)
        self.input.returnPressed.connect(self.run_command)
        run_btn = QPushButton("Run")
        run_btn.clicked.connect(self.run_command)
        input_row.addWidget(prompt)
        input_row.addWidget(self.input, 1)
        input_row.addWidget(run_btn)
        root.addLayout(input_row)
        self.input.setFocus()
        QShortcut(QKeySequence("Ctrl+L"), self, activated=self.clear_output)

    def _banner(self):
        self._append("MiddleTV Terminal")
        self._append("Commands run in a shell for this session. System-modifying commands may require authorization.")
        self._append(f"Working directory: {self.cwd}\n")

    def _append(self, text):
        self.output.appendPlainText(text.rstrip("\n"))
        self.output.moveCursor(QTextCursor.End)

    def clear_output(self):
        self.output.clear()
        self._banner()

    def run_command(self):
        cmd = self.input.text().strip()
        if not cmd:
            return
        self.history.append(cmd)
        self.history_index = len(self.history)
        self._append(f"$ {cmd}")
        self.input.clear()
        if cmd in ("clear", "cls"):
            self.clear_output()
            return
        if cmd.startswith("cd"):
            self._handle_cd(cmd)
            return
        dangerous = ("rm -rf", "mkfs", "dd ", ":(){", "shutdown", "reboot", "poweroff")
        if any(d in cmd for d in dangerous):
            if QMessageBox.question(self, "Run command?", f"This command may be destructive:\n\n{cmd}\n\nContinue?", QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
                self._append("Cancelled.")
                return
        if self.process.state() != QProcess.NotRunning:
            self._append("A command is already running.")
            return
        shell = os.environ.get("SHELL") or ("/bin/zsh" if Path("/bin/zsh").exists() else "/bin/sh")
        self.process.setWorkingDirectory(self.cwd)
        self.process.start(shell, ["-lc", cmd])

    def _handle_cd(self, cmd):
        parts = cmd.split(maxsplit=1)
        target = parts[1].strip() if len(parts) > 1 else str(Path.home())
        path = Path(target).expanduser()
        if not path.is_absolute():
            path = Path(self.cwd) / path
        try:
            path = path.resolve()
            if path.is_dir():
                self.cwd = str(path)
                self.cwd_label.setText(self.cwd)
            else:
                self._append(f"cd: not a directory: {target}")
        except Exception as e:
            self._append(f"cd: {e}")

    def _read_output(self):
        data = self.process.readAllStandardOutput().data()
        try:
            text = data.decode("utf-8", errors="replace")
        except Exception:
            text = str(data)
        if text:
            self._append(text.rstrip("\n"))

    def _finished(self, code, status):
        self._append(f"[exit {code}]")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up and self.history and self.input.hasFocus():
            self.history_index = max(0, self.history_index - 1)
            self.input.setText(self.history[self.history_index])
            return
        if event.key() == Qt.Key_Down and self.history and self.input.hasFocus():
            self.history_index = min(len(self.history), self.history_index + 1)
            self.input.setText("" if self.history_index == len(self.history) else self.history[self.history_index])
            return
        super().keyPressEvent(event)

    def handle_back(self):
        focus = self.focusWidget()
        if isinstance(focus, QLineEdit) and focus.text():
            focus.clear()
            return True
        self.close()
        return True
