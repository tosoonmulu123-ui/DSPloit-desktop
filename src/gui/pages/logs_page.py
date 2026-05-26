"""
Logs Page — real-time log viewer.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QPlainTextEdit
)
from PySide6.QtCore import Qt, QTimer
from pathlib import Path

from src.core.device_manager import DeviceManager
from src.utils.logger import Logger


class LogsPage(QWidget):
    """Real-time log viewer — shows all DSPloit PC logs."""

    def __init__(self, device_mgr: DeviceManager):
        super().__init__()
        self._device_mgr = device_mgr
        self._last_pos = 0
        self._setup_ui()

        # Auto-refresh timer
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh_logs)
        self._timer.start(1000)

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("📋 Live Logs")
        title.setObjectName("title")
        layout.addWidget(title)

        # Controls
        btn_layout = QHBoxLayout()
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self._clear)
        btn_layout.addWidget(clear_btn)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

        # Log output
        self._log_view = QPlainTextEdit()
        self._log_view.setReadOnly(True)
        self._log_view.setMaximumBlockCount(10000)
        layout.addWidget(self._log_view)

    def _refresh_logs(self):
        """Read new log entries from session file."""
        logger = Logger.get_instance()
        log_file = logger.session_file
        if log_file.exists():
            try:
                with open(log_file, "r") as f:
                    f.seek(self._last_pos)
                    new_data = f.read()
                    if new_data:
                        self._log_view.appendPlainText(new_data.rstrip())
                        self._last_pos = f.tell()
            except IOError:
                pass

    def _clear(self):
        self._log_view.clear()

    def _save(self):
        pass  # Would save to file
