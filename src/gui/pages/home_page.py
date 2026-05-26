"""
Home Page — device info + jailbreak button.
Port from: ContentView.swift (Tab 1)
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QProgressBar
)
from PySide6.QtCore import Qt, QThread, Signal

from src.core.device_manager import DeviceManager, DeviceState


class JailbreakWorker(QThread):
    """Background thread for jailbreak execution."""
    progress = Signal(int, str)
    finished = Signal(bool, str)

    def __init__(self, device_mgr: DeviceManager):
        super().__init__()
        self._device_mgr = device_mgr

    def run(self):
        agent = self._device_mgr.agent
        if not agent:
            self.finished.emit(False, "Agent not running")
            return

        from src.core.exploit_engine import ExploitEngine
        engine = ExploitEngine(agent)
        engine.set_progress_callback(
            lambda step, msg: self.progress.emit(step.value, msg)
        )
        success = engine.run_full_chain()
        msg = "Jailbreak complete!" if success else "Jailbreak failed"
        self.finished.emit(success, msg)


class HomePage(QWidget):
    """Home page with device info and jailbreak button."""

    def __init__(self, device_mgr: DeviceManager):
        super().__init__()
        self._device_mgr = device_mgr
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Title
        title = QLabel("DSPloit PC")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Desktop Jailbreak Controller")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        # Device info group
        device_group = QGroupBox("Device")
        device_layout = QVBoxLayout(device_group)
        self._device_name = QLabel("Not connected")
        self._device_model = QLabel("")
        self._device_ios = QLabel("")
        self._device_status = QLabel("")
        device_layout.addWidget(self._device_name)
        device_layout.addWidget(self._device_model)
        device_layout.addWidget(self._device_ios)
        device_layout.addWidget(self._device_status)
        layout.addWidget(device_group)

        # Deploy agent button
        self._deploy_btn = QPushButton("📦 Deploy Agent")
        self._deploy_btn.setEnabled(False)
        self._deploy_btn.clicked.connect(self._deploy_agent)
        layout.addWidget(self._deploy_btn, alignment=Qt.AlignCenter)

        # Jailbreak button
        self._jb_btn = QPushButton("⚡ JAILBREAK")
        self._jb_btn.setObjectName("jailbreakBtn")
        self._jb_btn.setEnabled(False)
        self._jb_btn.clicked.connect(self._start_jailbreak)
        layout.addWidget(self._jb_btn, alignment=Qt.AlignCenter)

        # Progress
        self._progress = QProgressBar()
        self._progress.setRange(0, 7)
        self._progress.setValue(0)
        self._progress.setVisible(False)
        layout.addWidget(self._progress)

        self._progress_label = QLabel("")
        self._progress_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._progress_label)

        layout.addStretch()

        # Connect state changes
        self._device_mgr.set_state_callback(self._on_state_change)

    def _on_state_change(self, state: DeviceState):
        """Update UI when device state changes."""
        device = self._device_mgr.device
        if device:
            self._device_name.setText(f"📱 {device.name}")
            self._device_model.setText(f"Model: {device.model}")
            self._device_ios.setText(f"iOS: {device.ios_version}")

        self._device_status.setText(f"Status: {state.value}")

        # Enable deploy button when device is paired
        self._deploy_btn.setEnabled(
            state in (DeviceState.PAIRED, DeviceState.AGENT_DEPLOYED)
        )
        # Enable jailbreak when agent is running OR when paired (direct mode)
        self._jb_btn.setEnabled(
            state in (DeviceState.PAIRED, DeviceState.AGENT_RUNNING)
        )

    def _deploy_agent(self):
        """Deploy agent binary to device via AFC."""
        import os
        self._deploy_btn.setEnabled(False)
        self._progress_label.setText("Deploying agent...")

        afc = self._device_mgr.afc
        if not afc:
            self._progress_label.setText("AFC not available")
            self._deploy_btn.setEnabled(True)
            return

        # Find agent binary
        agent_path = None
        for candidate in ["payloads/dsploit_agent_arm64e", "payloads/dsploit_agent_arm64"]:
            if os.path.exists(candidate):
                agent_path = candidate
                break

        if not agent_path:
            self._progress_label.setText("Agent binary not found in payloads/")
            self._deploy_btn.setEnabled(True)
            return

        # Deploy
        from src.exploit.deployer import Deployer
        deployer = Deployer(afc)
        success = deployer.deploy_agent(agent_path)

        if success:
            self._progress_label.setText("Agent deployed! Ready to jailbreak.")
            self._jb_btn.setEnabled(True)
        else:
            self._progress_label.setText("Deploy failed")
            self._deploy_btn.setEnabled(True)

    def _start_jailbreak(self):
        """Start jailbreak process."""
        self._jb_btn.setEnabled(False)
        self._progress.setVisible(True)
        self._progress.setValue(0)

        self._worker = JailbreakWorker(self._device_mgr)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    def _on_progress(self, step: int, message: str):
        self._progress.setValue(step)
        self._progress_label.setText(message)

    def _on_finished(self, success: bool, message: str):
        self._progress_label.setText(message)
        self._jb_btn.setEnabled(not success)
        if success:
            self._device_status.setObjectName("status_ok")
            self._device_status.setText("✅ JAILBROKEN")
