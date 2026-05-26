#!/usr/bin/env python3
"""
DSPloit PC — Desktop controller for DSPloit jailbreak tool.
Same exploit, same capabilities. Controlled from PC with panic-safe logging.

Author: Royan
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from src.gui.main_window import MainWindow
from src.utils.logger import Logger


def main():
    """Entry point for DSPloit PC."""
    # Initialize panic-safe logger
    logger = Logger.get_instance()
    logger.info("DSPloit PC starting...")

    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("DSPloit PC")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("DSPloit")

    # High DPI support
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)

    # Create and show main window
    window = MainWindow()
    window.show()

    logger.info("DSPloit PC ready.")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
