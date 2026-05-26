"""
Packages Page — package manager.
Port from: PackageManagerView.swift
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QFileDialog, QGroupBox
)
from PySide6.QtCore import Qt

from src.core.device_manager import DeviceManager


class PackagesPage(QWidget):
    """Package manager — install/remove .deb packages."""

    def __init__(self, device_mgr: DeviceManager):
        super().__init__()
        self._device_mgr = device_mgr
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("📦 Package Manager")
        title.setObjectName("title")
        layout.addWidget(title)

        # Actions
        btn_layout = QHBoxLayout()
        install_btn = QPushButton("📥 Install .deb")
        install_btn.clicked.connect(self._install_deb)
        btn_layout.addWidget(install_btn)

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self._refresh)
        btn_layout.addWidget(refresh_btn)

        remove_btn = QPushButton("🗑️ Remove Selected")
        remove_btn.clicked.connect(self._remove_selected)
        btn_layout.addWidget(remove_btn)
        layout.addLayout(btn_layout)

        # Package list
        pkg_group = QGroupBox("Installed Packages")
        pkg_layout = QVBoxLayout(pkg_group)
        self._pkg_list = QListWidget()
        pkg_layout.addWidget(self._pkg_list)
        layout.addWidget(pkg_group)

    def _install_deb(self):
        """Open file dialog to select and install .deb."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Select .deb package", "", "Debian Package (*.deb)"
        )
        if not path:
            return
        # Would install via DebInstaller

    def _refresh(self):
        """Refresh package list."""
        self._pkg_list.clear()
        agent = self._device_mgr.agent
        if not agent:
            return
        from src.core.root_executor import RootExecutor
        from src.core.session_manager import SessionManager
        from src.post_exploit.dpkg_status import DpkgStatus
        executor = RootExecutor(agent)
        dpkg = DpkgStatus(executor)
        dpkg.refresh()
        for pkg in dpkg.all_packages():
            self._pkg_list.addItem(f"{pkg.name} ({pkg.version})")

    def _remove_selected(self):
        """Remove selected package."""
        item = self._pkg_list.currentItem()
        if item:
            name = item.text().split(" (")[0]
            # Would remove via DebInstaller
