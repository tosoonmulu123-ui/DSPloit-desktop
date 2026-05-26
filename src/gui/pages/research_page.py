"""
Research Page — step-by-step exploit console.
NEW feature (not in iOS version).
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QPlainTextEdit, QLineEdit, QGroupBox, QListWidget
)
from PySide6.QtCore import Qt

from src.core.device_manager import DeviceManager


class ResearchPage(QWidget):
    """Interactive research console for step-by-step exploit execution."""

    def __init__(self, device_mgr: DeviceManager):
        super().__init__()
        self._device_mgr = device_mgr
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("🔬 Research Console")
        title.setObjectName("title")
        layout.addWidget(title)

        desc = QLabel("Execute exploit steps one-by-one with panic-safe logging")
        desc.setObjectName("subtitle")
        layout.addWidget(desc)

        # Command input
        cmd_layout = QHBoxLayout()
        self._cmd_input = QLineEdit()
        self._cmd_input.setPlaceholderText("Enter command (e.g., KREAD64:0xfffffff007004000)")
        self._cmd_input.returnPressed.connect(self._execute_step)
        cmd_layout.addWidget(self._cmd_input)

        self._exec_btn = QPushButton("Execute")
        self._exec_btn.clicked.connect(self._execute_step)
        cmd_layout.addWidget(self._exec_btn)

        layout.addLayout(cmd_layout)

        # Quick commands
        quick_layout = QHBoxLayout()
        for cmd in ["PING", "KREAD64:", "KWRITE64:", "EXEC:", "PROC_LIST"]:
            btn = QPushButton(cmd)
            btn.clicked.connect(lambda checked, c=cmd: self._insert_cmd(c))
            quick_layout.addWidget(btn)
        layout.addLayout(quick_layout)

        # Output console
        self._console = QPlainTextEdit()
        self._console.setReadOnly(True)
        self._console.setMaximumBlockCount(5000)
        layout.addWidget(self._console)

        # Step history
        history_group = QGroupBox("Step History")
        history_layout = QVBoxLayout(history_group)
        self._history_list = QListWidget()
        history_layout.addWidget(self._history_list)
        layout.addWidget(history_group)

    def _insert_cmd(self, cmd: str):
        self._cmd_input.setText(cmd)
        self._cmd_input.setFocus()

    def _execute_step(self):
        """Execute the entered command as a research step."""
        cmd = self._cmd_input.text().strip()
        if not cmd:
            return

        agent = self._device_mgr.agent
        if not agent:
            self._console.appendPlainText("[ERROR] Agent not connected")
            return

        self._console.appendPlainText(f"\n→ {cmd}")
        self._cmd_input.clear()

        # Execute via agent
        from src.core.research_console import ResearchConsole
        console = ResearchConsole(agent)
        result = console.step(cmd, cmd)

        # Display result
        status_icon = "✅" if result.status.value == "success" else "❌"
        self._console.appendPlainText(f"  {status_icon} {result.result}")
        self._console.appendPlainText(f"  ({result.duration:.3f}s)")

        # Add to history
        self._history_list.addItem(f"{status_icon} {cmd} → {result.result}")
