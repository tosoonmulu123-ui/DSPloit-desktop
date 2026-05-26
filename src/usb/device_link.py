"""
Device link — pymobiledevice3 wrapper for USB device detection and pairing.
"""

import time
import asyncio
from typing import Optional, List, Callable
from dataclasses import dataclass

from pymobiledevice3.usbmux import list_devices
from pymobiledevice3.lockdown import LockdownClient, create_using_usbmux
from pymobiledevice3.exceptions import (
    MuxException,
    PairingError,
)

from src.utils.logger import Logger


def _run_async(coro):
    """Run async function synchronously."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, coro)
                return future.result()
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


@dataclass
class ConnectedDevice:
    """Represents a connected iOS device."""
    udid: str
    name: str
    model: str
    ios_version: str
    chip: str
    serial: str
    lockdown: Optional[LockdownClient] = None


class DeviceLink:
    """
    Manages USB connection to iOS device via pymobiledevice3.
    Handles detection, pairing, and basic device info retrieval.
    """

    def __init__(self):
        self._logger = Logger.get_instance()
        self._device: Optional[ConnectedDevice] = None
        self._lockdown: Optional[LockdownClient] = None
        self._on_connect: Optional[Callable] = None
        self._on_disconnect: Optional[Callable] = None

    @property
    def connected(self) -> bool:
        return self._device is not None

    @property
    def device(self) -> Optional[ConnectedDevice]:
        return self._device

    @property
    def lockdown(self) -> Optional[LockdownClient]:
        return self._lockdown

    def set_callbacks(self, on_connect: Callable, on_disconnect: Callable):
        """Set connection/disconnection callbacks."""
        self._on_connect = on_connect
        self._on_disconnect = on_disconnect

    def scan(self) -> List[str]:
        """Scan for connected USB devices. Returns list of UDIDs."""
        try:
            devices = _run_async(list_devices())
            return [d.serial for d in devices]
        except Exception as e:
            self._logger.error(f"USB scan failed: {e}")
            return []

    def connect(self, udid: Optional[str] = None) -> bool:
        """
        Connect to device. If udid is None, connects to first available.
        Returns True on success.
        """
        try:
            self._logger.info(f"Connecting to device (udid={udid or 'auto'})...")

            if udid:
                self._lockdown = _run_async(create_using_usbmux(serial=udid))
            else:
                self._lockdown = _run_async(create_using_usbmux())

            # Read device info
            all_values = self._lockdown.all_values
            self._device = ConnectedDevice(
                udid=all_values.get("UniqueDeviceID", ""),
                name=all_values.get("DeviceName", "Unknown"),
                model=all_values.get("ProductType", "Unknown"),
                ios_version=all_values.get("ProductVersion", "0.0"),
                chip=all_values.get("HardwareModel", "Unknown"),
                serial=all_values.get("SerialNumber", ""),
                lockdown=self._lockdown,
            )

            self._logger.info(
                f"Connected: {self._device.name} "
                f"({self._device.model}) "
                f"iOS {self._device.ios_version}"
            )

            if self._on_connect:
                self._on_connect(self._device)

            return True

        except PairingError:
            self._logger.error("Device not paired. Trust this computer on device.")
            return False
        except MuxException as e:
            self._logger.error(f"USB connection failed: {e}")
            return False
        except Exception as e:
            self._logger.error(f"Connection error: {e}")
            return False

    def disconnect(self):
        """Disconnect from device."""
        if self._device:
            self._logger.info(f"Disconnecting from {self._device.name}")
            self._device = None
            self._lockdown = None
            if self._on_disconnect:
                self._on_disconnect()

    def is_device_alive(self) -> bool:
        """Check if device is still connected (not panicked)."""
        if not self._lockdown:
            return False
        try:
            # Quick query to check connection
            self._lockdown.all_values
            return True
        except Exception:
            return False

    def wait_for_device(self, timeout: float = 30.0) -> bool:
        """Wait for a device to appear on USB. Returns True if found."""
        self._logger.info(f"Waiting for device (timeout={timeout}s)...")
        start = time.time()
        while time.time() - start < timeout:
            devices = self.scan()
            if devices:
                return self.connect(devices[0])
            time.sleep(1.0)
        self._logger.warn("No device found within timeout.")
        return False
