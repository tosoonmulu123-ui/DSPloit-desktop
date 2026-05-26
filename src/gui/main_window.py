"""
Main Window — DSPloit PC main application window.
Tab-based layout matching iOS app structure.
"""

from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QStatusBar, QLabel, QVBoxLayout, QWidget
)
from PySide6.QtCore import Qt, QTimer

from src.gui.theme import DARK_THEME
from src.gui.pages.home_page import HomePage
from src.gui.pages.research_page import ResearchPage
from src.gui.pages.memory_page import MemoryPage
from src.gui.pages.experiments_page import ExperimentsPage
from src.gui.pages.tools_page import ToolsPage
from src.gui.pages.files_page import FilesPage
from src.gui.pages.packages_page import PackagesPage
from src.gui.pages.daemons_page import DaemonsPage
from src.gui.pages.ssh_page import SSHPage
from src.gui.pages.logs_page import LogsPage
from src.gui.pages.settings_page import SettingsPage
from src.core.device_manager import DeviceManager


class MainWindow(QMainWindow):
    """DSPloit PC main window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("DSPloit PC — Desktop Jailbreak Controller")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet(DARK_THEME)

        # Core
        self._device_mgr = DeviceManager()

        # Setup UI
        self._setup_ui()
        self._setup_statusbar()

        # Auto-detect device
        self._detect_timer = QTimer(self)
        self._detect_timer.timeout.connect(self._check_device)
        self._detect_timer.start(3000)

    def _setup_ui(self):
        """Setup tabbed interface."""
        self._tabs = QTabWidget()
        self._tabs.setTabPosition(QTabWidget.West)

        # Create pages
        self._home = HomePage(self._device_mgr)
        self._research = ResearchPage(self._device_mgr)
        self._memory = MemoryPage(self._device_mgr)
        self._experiments = ExperimentsPage(self._device_mgr)
        self._tools = ToolsPage(self._device_mgr)
        self._files = FilesPage(self._device_mgr)
        self._packages = PackagesPage(self._device_mgr)
        self._daemons = DaemonsPage(self._device_mgr)
        self._ssh = SSHPage(self._device_mgr)
        self._logs = LogsPage(self._device_mgr)
        self._settings = SettingsPage(self._device_mgr)

        # Add tabs
        self._tabs.addTab(self._home, "🏠 Home")
        self._tabs.addTab(self._research, "🔬 Research")
        self._tabs.addTab(self._memory, "🧠 Memory")
        self._tabs.addTab(self._experiments, "⚗️ Experiments")
        self._tabs.addTab(self._tools, "🔧 Tools")
        self._tabs.addTab(self._files, "📁 Files")
        self._tabs.addTab(self._packages, "📦 Packages")
        self._tabs.addTab(self._daemons, "⚙️ Daemons")
        self._tabs.addTab(self._ssh, "💻 SSH")
        self._tabs.addTab(self._logs, "📋 Logs")
        self._tabs.addTab(self._settings, "⚙️ Settings")

        self.setCentralWidget(self._tabs)

    def _setup_statusbar(self):
        """Setup status bar."""
        self._statusbar = QStatusBar()
        self.setStatusBar(self._statusbar)

        self._status_label = QLabel("No device connected")
        self._statusbar.addWidget(self._status_label)

    def _check_device(self):
        """Periodic device detection."""
        if not self._device_mgr.device:
            devices = self._device_mgr.link.scan()
            if devices:
                self._device_mgr.connect(devices[0])
                self._update_status()

    def _update_status(self):
        """Update status bar with device info."""
        status = self._device_mgr.get_status()
        self._status_label.setText(status.message)
