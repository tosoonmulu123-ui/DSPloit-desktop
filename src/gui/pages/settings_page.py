"""
Settings Page — application settings.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QSpinBox, QGroupBox, QFormLayout, QCheckBox
)
from PySide6.QtCore import Qt

from src.core.device_manager import DeviceManager
from src.utils.config import Config


class SettingsPage(QWidget):
    """Application settings."""

    def __init__(self, device_mgr: DeviceManager):
        super().__init__()
        self._device_mgr = device_mgr
        self._config = Config.get_instance()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("⚙️ Settings")
        title.setObjectName("title")
        layout.addWidget(title)

        # SSH settings
        ssh_group = QGroupBox("SSH")
        ssh_form = QFormLayout(ssh_group)
        self._ssh_port = QSpinBox()
        self._ssh_port.setRange(1, 65535)
        self._ssh_port.setValue(self._config.ssh_port)
        ssh_form.addRow("Port:", self._ssh_port)

        self._ssh_user = QLineEdit(self._config.ssh_user)
        ssh_form.addRow("User:", self._ssh_user)

        self._ssh_pass = QLineEdit(self._config.ssh_password)
        self._ssh_pass.setEchoMode(QLineEdit.Password)
        ssh_form.addRow("Password:", self._ssh_pass)
        layout.addWidget(ssh_group)

        # Timing settings
        timing_group = QGroupBox("Timing")
        timing_form = QFormLayout(timing_group)
        self._panic_timeout = QSpinBox()
        self._panic_timeout.setRange(5, 120)
        self._panic_timeout.setValue(int(self._config.panic_timeout))
        timing_form.addRow("Panic timeout (s):", self._panic_timeout)
        layout.addWidget(timing_group)

        # Options
        opts_group = QGroupBox("Options")
        opts_layout = QVBoxLayout(opts_group)
        self._auto_ssh = QCheckBox("Auto-connect SSH after jailbreak")
        self._auto_ssh.setChecked(True)
        opts_layout.addWidget(self._auto_ssh)
        layout.addWidget(opts_group)

        # Save button
        save_btn = QPushButton("💾 Save Settings")
        save_btn.clicked.connect(self._save)
        layout.addWidget(save_btn)

        layout.addStretch()

    def _save(self):
        self._config.set("ssh_port", self._ssh_port.value())
        self._config.set("ssh_user", self._ssh_user.text())
        self._config.set("ssh_password", self._ssh_pass.text())
        self._config.set("panic_timeout", float(self._panic_timeout.value()))
