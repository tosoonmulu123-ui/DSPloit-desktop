"""
Banking Page — jailbreak detection bypass for banking apps.
Port from: MobileBankingView.swift
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QGroupBox
)
from PySide6.QtCore import Qt

from src.core.device_manager import DeviceManager


BANKING_APPS = [
    ("com.bca.myBCA", "myBCA"),
    ("com.mandiri.livin", "Livin by Mandiri"),
    ("com.bni.mobilebanking", "BNI Mobile"),
    ("com.bri.brimo", "BRImo"),
    ("id.co.btn.mobilebanking", "BTN Mobile"),
    ("com.dana.id", "DANA"),
    ("com.gojek.app", "Gojek"),
    ("com.shopee.id", "Shopee"),
    ("com.tokopedia.tkpd", "Tokopedia"),
]


class BankingPage(QWidget):
    """Jailbreak detection bypass for banking apps."""

    def __init__(self, device_mgr: DeviceManager):
        super().__init__()
        self._device_mgr = device_mgr
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("🏦 JB Detection Bypass")
        title.setObjectName("title")
        layout.addWidget(title)

        desc = QLabel("Hide jailbreak from banking/fintech apps")
        desc.setObjectName("subtitle")
        layout.addWidget(desc)

        # App list
        group = QGroupBox("Banking Apps")
        group_layout = QVBoxLayout(group)
        self._app_list = QListWidget()
        for bundle_id, name in BANKING_APPS:
            self._app_list.addItem(f"🏦 {name} ({bundle_id})")
        group_layout.addWidget(self._app_list)
        layout.addWidget(group)

        # Actions
        hide_btn = QPushButton("🛡️ Hide JB for Selected App")
        hide_btn.clicked.connect(self._hide_jb)
        layout.addWidget(hide_btn)

        hide_all_btn = QPushButton("🛡️ Hide JB for All")
        hide_all_btn.clicked.connect(self._hide_all)
        layout.addWidget(hide_all_btn)

        layout.addStretch()

    def _hide_jb(self):
        """Hide jailbreak for selected app."""
        item = self._app_list.currentItem()
        if not item:
            return
        # Would configure tweak to hide JB from this app

    def _hide_all(self):
        """Hide jailbreak from all banking apps."""
        pass  # Would configure for all apps
