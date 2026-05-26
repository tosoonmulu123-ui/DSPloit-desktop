"""
SSH Page — SSH terminal to device.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QPlainTextEdit, QLineEdit
)
from PySide6.QtCore import Qt

from src.core.device_manager import DeviceManager


class SSHPage(QWidget):
    """SSH terminal — execute commands on device."""

    def __init__(self, device_mgr: DeviceManager):
        super().__init__()
        self._device_mgr = device_mgr
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("💻 SSH Terminal")
        title.setObjectName("title")
        layout.addWidget(title)

        # Connect button
        btn_layout = QHBoxLayout()
        self._connect_btn = QPushButton("🔌 Connect SSH")
        self._connect_btn.clicked.connect(self._connect)
        btn_layout.addWidget(self._connect_btn)

        self._disconnect_btn = QPushButton("Disconnect")
        self._disconnect_btn.setEnabled(False)
        self._disconnect_btn.clicked.connect(self._disconnect)
        btn_layout.addWidget(self._disconnect_btn)
        layout.addLayout(btn_layout)

        # Terminal output
        self._terminal = QPlainTextEdit()
        self._terminal.setReadOnly(True)
        layout.addWidget(self._terminal)

        # Command input
        cmd_layout = QHBoxLayout()
        self._cmd_input = QLineEdit()
        self._cmd_input.setPlaceholderText("root# ")
        self._cmd_input.returnPressed.connect(self._execute)
        cmd_layout.addWidget(self._cmd_input)

        exec_btn = QPushButton("Run")
        exec_btn.clicked.connect(self._execute)
        cmd_layout.addWidget(exec_btn)
        layout.addLayout(cmd_layout)

    def _connect(self):
        self._terminal.appendPlainText("Connecting SSH...")
        # Would connect via SessionManager

    def _disconnect(self):
        self._terminal.appendPlainText("Disconnected.")

    def _execute(self):
        cmd = self._cmd_input.text().strip()
        if not cmd:
            return
        self._terminal.appendPlainText(f"root# {cmd}")
        self._cmd_input.clear()

        agent = self._device_mgr.agent
        if agent:
            from src.core.root_executor import RootExecutor
            executor = RootExecutor(agent)
            result = executor.execute(cmd)
            if result.stdout:
                self._terminal.appendPlainText(result.stdout)
            if result.stderr:
                self._terminal.appendPlainText(f"[stderr] {result.stderr}")
