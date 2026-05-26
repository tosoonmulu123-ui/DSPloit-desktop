"""
Tools Page — root tools launcher.
Port from: RootDashboardView.swift (Tab 2)
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel, QPushButton, QGroupBox
)
from PySide6.QtCore import Qt

from src.core.device_manager import DeviceManager


class ToolsPage(QWidget):
    """Root tools launcher — quick access to common operations."""

    def __init__(self, device_mgr: DeviceManager):
        super().__init__()
        self._device_mgr = device_mgr
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("🔧 Root Tools")
        title.setObjectName("title")
        layout.addWidget(title)

        # Tool grid
        grid = QGridLayout()
        tools = [
            ("🔑 Respring", self._respring),
            ("🔄 UICache", self._uicache),
            ("💀 Kill SpringBoard", self._kill_sb),
            ("📱 Device Info", self._device_info),
            ("🔒 Lock Device", self._lock),
            ("🗑️ Clear Caches", self._clear_caches),
            ("📋 Process List", self._proc_list),
            ("🔌 Reboot", self._reboot),
        ]

        for i, (label, callback) in enumerate(tools):
            btn = QPushButton(label)
            btn.clicked.connect(callback)
            grid.addWidget(btn, i // 3, i % 3)

        layout.addLayout(grid)
        layout.addStretch()

    def _exec(self, cmd: str):
        agent = self._device_mgr.agent
        if agent:
            agent.send_command(f"EXEC:{cmd}")

    def _respring(self):
        self._exec("killall -9 SpringBoard")

    def _uicache(self):
        self._exec("uicache -a")

    def _kill_sb(self):
        self._exec("killall -9 SpringBoard")

    def _device_info(self):
        self._exec("uname -a")

    def _lock(self):
        self._exec("activator send libactivator.system.sleepbutton")

    def _clear_caches(self):
        self._exec("rm -rf /var/mobile/Library/Caches/*")

    def _proc_list(self):
        self._exec("ps aux")

    def _reboot(self):
        self._exec("reboot")
