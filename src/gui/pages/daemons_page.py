"""
Daemons Page — daemon control.
Port from: DaemonDisableView.swift
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QGroupBox
)
from PySide6.QtCore import Qt

from src.core.device_manager import DeviceManager


class DaemonsPage(QWidget):
    """Control system daemons — disable for JB detection bypass."""

    def __init__(self, device_mgr: DeviceManager):
        super().__init__()
        self._device_mgr = device_mgr
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("⚙️ Daemon Control")
        title.setObjectName("title")
        layout.addWidget(title)

        # Actions
        btn_layout = QHBoxLayout()
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self._refresh)
        btn_layout.addWidget(refresh_btn)

        stop_btn = QPushButton("⏹ Stop Selected")
        stop_btn.clicked.connect(self._stop_selected)
        btn_layout.addWidget(stop_btn)

        disable_btn = QPushButton("🚫 Disable Selected")
        disable_btn.clicked.connect(self._disable_selected)
        btn_layout.addWidget(disable_btn)
        layout.addLayout(btn_layout)

        # Daemon list
        group = QGroupBox("Running Daemons")
        group_layout = QVBoxLayout(group)
        self._daemon_list = QListWidget()
        group_layout.addWidget(self._daemon_list)
        layout.addWidget(group)

    def _refresh(self):
        self._daemon_list.clear()
        agent = self._device_mgr.agent
        if not agent:
            return
        from src.core.root_executor import RootExecutor
        from src.post_exploit.daemon_manager import DaemonManager
        executor = RootExecutor(agent)
        mgr = DaemonManager(executor)
        for d in mgr.list_daemons():
            status = "🟢" if d.running else "⚪"
            self._daemon_list.addItem(f"{status} {d.name} (pid={d.pid})")

    def _stop_selected(self):
        pass  # Would stop selected daemon

    def _disable_selected(self):
        pass  # Would disable selected daemon
