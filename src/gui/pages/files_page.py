"""
Files Page — file browser for device filesystem.
Port from: RootFileManagerView.swift
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTreeWidget, QTreeWidgetItem, QLineEdit, QPlainTextEdit
)
from PySide6.QtCore import Qt

from src.core.device_manager import DeviceManager


class FilesPage(QWidget):
    """File browser for device filesystem."""

    def __init__(self, device_mgr: DeviceManager):
        super().__init__()
        self._device_mgr = device_mgr
        self._current_path = "/"
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("📁 File Manager")
        title.setObjectName("title")
        layout.addWidget(title)

        # Path bar
        path_layout = QHBoxLayout()
        self._path_input = QLineEdit("/")
        self._path_input.returnPressed.connect(self._navigate)
        path_layout.addWidget(self._path_input)

        go_btn = QPushButton("Go")
        go_btn.clicked.connect(self._navigate)
        path_layout.addWidget(go_btn)

        up_btn = QPushButton("⬆ Up")
        up_btn.clicked.connect(self._go_up)
        path_layout.addWidget(up_btn)

        layout.addLayout(path_layout)

        # File tree
        self._tree = QTreeWidget()
        self._tree.setHeaderLabels(["Name", "Size", "Permissions", "Owner"])
        self._tree.itemDoubleClicked.connect(self._on_item_double_click)
        layout.addWidget(self._tree)

        # File preview
        self._preview = QPlainTextEdit()
        self._preview.setReadOnly(True)
        self._preview.setMaximumHeight(200)
        layout.addWidget(self._preview)

    def _navigate(self):
        """Navigate to path in input."""
        path = self._path_input.text().strip()
        if path:
            self._current_path = path
            self._load_directory(path)

    def _go_up(self):
        """Navigate to parent directory."""
        parts = self._current_path.rstrip("/").rsplit("/", 1)
        parent = parts[0] if parts[0] else "/"
        self._path_input.setText(parent)
        self._navigate()

    def _load_directory(self, path: str):
        """Load directory listing from device."""
        self._tree.clear()
        agent = self._device_mgr.agent
        if not agent:
            return

        from src.core.root_executor import RootExecutor
        executor = RootExecutor(agent)
        from src.post_exploit.file_manager import FileManager
        from src.core.session_manager import SessionManager
        fm = FileManager(executor, SessionManager())

        entries = fm.list_dir(path)
        for entry in entries:
            item = QTreeWidgetItem([
                ("📁 " if entry.is_dir else "📄 ") + entry.name,
                str(entry.size) if not entry.is_dir else "",
                entry.permissions,
                entry.owner,
            ])
            item.setData(0, Qt.UserRole, entry)
            self._tree.addTopLevelItem(item)

    def _on_item_double_click(self, item: QTreeWidgetItem, column: int):
        """Handle double-click on file/directory."""
        entry = item.data(0, Qt.UserRole)
        if entry and entry.is_dir:
            self._path_input.setText(entry.path)
            self._navigate()
        elif entry:
            # Preview file
            agent = self._device_mgr.agent
            if agent:
                from src.core.root_executor import RootExecutor
                executor = RootExecutor(agent)
                content = executor.read_file(entry.path)
                if content:
                    self._preview.setPlainText(content[:4096])
