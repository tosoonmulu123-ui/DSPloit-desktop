"""
Experiments Page — run predefined research experiments.
Port from: ExperimentsView.swift
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QPlainTextEdit, QListWidget, QListWidgetItem, QGroupBox
)
from PySide6.QtCore import Qt, QThread, Signal

from src.core.device_manager import DeviceManager


class ExperimentsPage(QWidget):
    """Run predefined AMFI bypass experiments."""

    def __init__(self, device_mgr: DeviceManager):
        super().__init__()
        self._device_mgr = device_mgr
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("⚗️ Experiments")
        title.setObjectName("title")
        layout.addWidget(title)

        # Experiment list
        exp_group = QGroupBox("Available Experiments")
        exp_layout = QVBoxLayout(exp_group)
        self._exp_list = QListWidget()
        self._exp_list.addItem("🔬 amfid_kill_race — Kill amfid + race load")
        self._exp_list.addItem("🔬 amfid_rc_patch — RemoteCall patch MISValidate")
        self._exp_list.addItem("🔬 amfid_mprotect — mprotect + direct write")
        self._exp_list.addItem("🔬 cryptex_race — Cryptex mount race")
        self._exp_list.addItem("🔬 custom — User-defined experiment")
        exp_layout.addWidget(self._exp_list)
        layout.addWidget(exp_group)

        # Run button
        btn_layout = QHBoxLayout()
        self._run_btn = QPushButton("▶ Run Selected")
        self._run_btn.clicked.connect(self._run_experiment)
        btn_layout.addWidget(self._run_btn)

        self._stop_btn = QPushButton("⏹ Stop")
        self._stop_btn.setEnabled(False)
        btn_layout.addWidget(self._stop_btn)
        layout.addLayout(btn_layout)

        # Output
        self._output = QPlainTextEdit()
        self._output.setReadOnly(True)
        layout.addWidget(self._output)

    def _run_experiment(self):
        """Run selected experiment."""
        item = self._exp_list.currentItem()
        if not item:
            return

        agent = self._device_mgr.agent
        if not agent:
            self._output.appendPlainText("[ERROR] Agent not connected")
            return

        exp_name = item.text().split("—")[0].strip().replace("🔬 ", "")
        self._output.appendPlainText(f"\n═══ Running: {exp_name} ═══")

        from src.core.research_console import ResearchConsole
        from src.research.experiments.exp_amfid_kill_race import ExpAmfidKillRace
        from src.research.experiments.exp_amfid_rc_patch import ExpAmfidRCPatch
        from src.research.experiments.exp_amfid_mprotect import ExpAmfidMprotect
        from src.research.experiments.exp_cryptex_race import ExpCryptexRace

        experiments = {
            "amfid_kill_race": ExpAmfidKillRace,
            "amfid_rc_patch": ExpAmfidRCPatch,
            "amfid_mprotect": ExpAmfidMprotect,
            "cryptex_race": ExpCryptexRace,
        }

        exp_class = experiments.get(exp_name)
        if not exp_class:
            self._output.appendPlainText("[ERROR] Unknown experiment")
            return

        console = ResearchConsole(agent)
        experiment = exp_class().to_experiment()
        result = console.run_experiment(experiment)

        # Display result
        self._output.appendPlainText(f"Completed: {result.completed_steps}/{result.total_steps}")
        if result.panic_at_step is not None:
            self._output.appendPlainText(console.panic_report(result))
        self._output.appendPlainText(f"Log: {result.log_file}")
