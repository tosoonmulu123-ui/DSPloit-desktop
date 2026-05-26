"""
Compatibility Page — device compatibility info.
Port from: DeviceCompatibilityView.swift
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QGroupBox
)
from PySide6.QtCore import Qt

from src.core.device_manager import DeviceManager
from src.utils.device_db import DEVICE_DB


class CompatPage(QWidget):
    """Device compatibility information."""

    def __init__(self, device_mgr: DeviceManager):
        super().__init__()
        self._device_mgr = device_mgr
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("📱 Device Compatibility")
        title.setObjectName("title")
        layout.addWidget(title)

        # Table
        self._table = QTableWidget()
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels(
            ["Model ID", "Name", "Chip", "iOS Range", "Status"]
        )
        self._table.setRowCount(len(DEVICE_DB))

        for i, (model_id, info) in enumerate(DEVICE_DB.items()):
            self._table.setItem(i, 0, QTableWidgetItem(model_id))
            self._table.setItem(i, 1, QTableWidgetItem(info.model))
            self._table.setItem(i, 2, QTableWidgetItem(info.chip))
            self._table.setItem(i, 3, QTableWidgetItem(
                f"{info.min_ios} - {info.max_ios}"
            ))
            status = "✅ Supported" if info.supported else "❌ Not supported"
            self._table.setItem(i, 4, QTableWidgetItem(status))

        self._table.resizeColumnsToContents()
        layout.addWidget(self._table)
