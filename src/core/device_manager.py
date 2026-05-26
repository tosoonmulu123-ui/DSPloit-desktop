"""
Device Manager — high-level device state management.
Port from: dspmgr.swift

Manages device connection lifecycle, state transitions, and provides
unified interface for all device operations.
"""

from enum import Enum
from typing import Optional, Callable
from dataclasses import dataclass

from src.usb.device_link import DeviceLink, ConnectedDevice
from src.usb.afc_client import AFCClient
from src.usb.syslog_relay import SyslogRelay
from src.usb.agent_comm import AgentComm, AgentStatus
from src.utils.logger import Logger
from src.utils.device_db import is_supported, get_device_info, is_ios_supported


class DeviceState(Enum):
    """Device state machine."""
    DISCONNECTED = "disconnected"
    CONNECTED = "connected"
    PAIRED = "paired"
    AGENT_DEPLOYED = "agent_deployed"
    AGENT_RUNNING = "agent_running"
    EXPLOITING = "exploiting"
    JAILBROKEN = "jailbroken"
    PANICKED = "panicked"


@dataclass
class DeviceStatus:
    """Current device status snapshot."""
    state: DeviceState
    device: Optional[ConnectedDevice]
    supported: bool
    ios_supported: bool
    agent_status: AgentStatus
    message: str


class DeviceManager:
    """
    High-level device management.
    Coordinates DeviceLink, AFC, Syslog, and AgentComm.
    """

    def __init__(self):
        self._logger = Logger.get_instance()
        self._link = DeviceLink()
        self._afc: Optional[AFCClient] = None
        self._syslog: Optional[SyslogRelay] = None
        self._agent: Optional[AgentComm] = None
        self._state = DeviceState.DISCONNECTED
        self._on_state_change: Optional[Callable[[DeviceState], None]] = None

    @property
    def state(self) -> DeviceState:
        return self._state

    @property
    def device(self) -> Optional[ConnectedDevice]:
        return self._link.device

    @property
    def agent(self) -> Optional[AgentComm]:
        return self._agent

    @property
    def afc(self) -> Optional[AFCClient]:
        return self._afc

    @property
    def link(self) -> DeviceLink:
        return self._link

    def set_state_callback(self, callback: Callable[[DeviceState], None]):
        self._on_state_change = callback

    def _set_state(self, new_state: DeviceState):
        old = self._state
        self._state = new_state
        self._logger.info(f"State: {old.value} -> {new_state.value}")
        if self._on_state_change:
            self._on_state_change(new_state)

    def connect(self, udid: Optional[str] = None) -> bool:
        """Connect to device and initialize services."""
        if not self._link.connect(udid):
            return False

        self._set_state(DeviceState.CONNECTED)

        # Check compatibility
        device = self._link.device
        if device:
            if not is_supported(device.model):
                self._logger.warn(f"Device {device.model} may not be supported")
            if not is_ios_supported(device.ios_version):
                self._logger.warn(f"iOS {device.ios_version} may not be supported")

        # Start AFC
        self._afc = AFCClient(self._link.lockdown)
        if self._afc.connect():
            self._set_state(DeviceState.PAIRED)

        # Start syslog
        self._syslog = SyslogRelay(self._link.lockdown)
        self._syslog.set_callbacks(on_panic=self._on_panic)
        self._syslog.start()

        return True

    def setup_agent(self) -> bool:
        """Initialize agent communication (after agent is deployed)."""
        if not self._afc:
            return False

        self._agent = AgentComm(self._afc)
        if self._agent.check_agent_ready():
            self._set_state(DeviceState.AGENT_RUNNING)
            return True

        self._logger.warn("Agent not ready yet")
        return False

    def disconnect(self):
        """Disconnect from device."""
        if self._syslog:
            self._syslog.stop()
        self._link.disconnect()
        self._agent = None
        self._afc = None
        self._set_state(DeviceState.DISCONNECTED)

    def get_status(self) -> DeviceStatus:
        """Get current device status."""
        device = self._link.device
        return DeviceStatus(
            state=self._state,
            device=device,
            supported=is_supported(device.model) if device else False,
            ios_supported=is_ios_supported(device.ios_version) if device else False,
            agent_status=self._agent.status if self._agent else AgentStatus.NOT_DEPLOYED,
            message=self._state_message(),
        )

    def _state_message(self) -> str:
        messages = {
            DeviceState.DISCONNECTED: "No device connected",
            DeviceState.CONNECTED: "Device connected, initializing...",
            DeviceState.PAIRED: "Device paired, ready for agent deploy",
            DeviceState.AGENT_DEPLOYED: "Agent deployed, starting...",
            DeviceState.AGENT_RUNNING: "Agent running, ready for commands",
            DeviceState.EXPLOITING: "Exploit in progress...",
            DeviceState.JAILBROKEN: "Device jailbroken ✓",
            DeviceState.PANICKED: "Device panicked — check logs",
        }
        return messages.get(self._state, "Unknown state")

    def _on_panic(self):
        """Called when panic is detected."""
        self._set_state(DeviceState.PANICKED)
        self._logger.error("DEVICE PANIC DETECTED")
