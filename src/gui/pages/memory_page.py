"""
Memory Page — kernel memory inspector.
NEW feature (not in iOS version).
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QPlainTextEdit, QLineEdit, QGroupBox, QSpinBox
)
from PySide6.QtCore import Qt

from src.core.device_manager import DeviceManager


class MemoryPage(QWidget):
    """Kernel memory inspector — read/write/dump kernel memory."""

    def __init__(self, device_mgr: DeviceManager):
        super().__init__()
        self._device_mgr = device_mgr
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("🧠 Kernel Memory Inspector")
        title.setObjectName("title")
        layout.addWidget(title)

        # Address input
        addr_layout = QHBoxLayout()
        addr_layout.addWidget(QLabel("Address:"))
        self._addr_input = QLineEdit()
        self._addr_input.setPlaceholderText("0xfffffff007004000")
        addr_layout.addWidget(self._addr_input)

        addr_layout.addWidget(QLabel("Size:"))
        self._size_input = QSpinBox()
        self._size_input.setRange(8, 4096)
        self._size_input.setValue(64)
        self._size_input.setSingleStep(16)
        addr_layout.addWidget(self._size_input)

        layout.addLayout(addr_layout)

        # Action buttons
        btn_layout = QHBoxLayout()
        self._read_btn = QPushButton("Read64")
        self._read_btn.clicked.connect(self._read64)
        btn_layout.addWidget(self._read_btn)

        self._dump_btn = QPushButton("Hexdump")
        self._dump_btn.clicked.connect(self._hexdump)
        btn_layout.addWidget(self._dump_btn)

        self._proc_btn = QPushButton("Find Proc")
        self._proc_btn.clicked.connect(self._find_proc)
        btn_layout.addWidget(self._proc_btn)

        layout.addLayout(btn_layout)

        # Output
        self._output = QPlainTextEdit()
        self._output.setReadOnly(True)
        layout.addWidget(self._output)

    def _get_address(self) -> int:
        """Parse address from input."""
        text = self._addr_input.text().strip()
        try:
            if text.startswith("0x"):
                return int(text, 16)
            return int(text, 16)
        except ValueError:
            return 0

    def _read64(self):
        """Read 64-bit value at address."""
        addr = self._get_address()
        if not addr:
            self._output.appendPlainText("[ERROR] Invalid address")
            return

        agent = self._device_mgr.agent
        if not agent:
            self._output.appendPlainText("[ERROR] Agent not connected")
            return

        from src.research.memory_inspector import MemoryInspector
        inspector = MemoryInspector(agent)
        value = inspector.read64(addr)

        if value is not None:
            self._output.appendPlainText(f"[0x{addr:016x}] = 0x{value:016x}")
        else:
            self._output.appendPlainText(f"[0x{addr:016x}] = READ FAILED")

    def _hexdump(self):
        """Hexdump memory region."""
        addr = self._get_address()
        size = self._size_input.value()
        if not addr:
            return

        agent = self._device_mgr.agent
        if not agent:
            return

        from src.research.memory_inspector import MemoryInspector
        inspector = MemoryInspector(agent)
        dump = inspector.hexdump(addr, size)
        self._output.appendPlainText(f"\n--- Hexdump 0x{addr:x} ({size} bytes) ---")
        self._output.appendPlainText(dump)

    def _find_proc(self):
        """Find proc struct by PID."""
        pid = self._get_address()  # Reuse address field for PID
        agent = self._device_mgr.agent
        if not agent:
            return

        from src.research.memory_inspector import MemoryInspector
        inspector = MemoryInspector(agent)
        proc_addr = inspector.find_proc(pid)
        if proc_addr:
            self._output.appendPlainText(f"proc[{pid}] @ 0x{proc_addr:016x}")
            info = inspector.read_proc_info(proc_addr)
            for k, v in info.items():
                if isinstance(v, int):
                    self._output.appendPlainText(f"  {k} = 0x{v:x}")
                else:
                    self._output.appendPlainText(f"  {k} = {v}")
