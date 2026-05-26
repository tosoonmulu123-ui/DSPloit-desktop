"""
Device compatibility database.
Port from: DeviceCompat.swift, isdebugged.swift, isunsupported.swift
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class DeviceInfo:
    model: str
    chip: str
    supported: bool
    min_ios: str
    max_ios: str
    notes: str = ""


# Device compatibility database
DEVICE_DB = {
    # A11 devices
    "iPhone10,1": DeviceInfo("iPhone 8", "A11", True, "15.0", "18.2"),
    "iPhone10,2": DeviceInfo("iPhone 8 Plus", "A11", True, "15.0", "18.2"),
    "iPhone10,3": DeviceInfo("iPhone X", "A11", True, "15.0", "18.2"),
    "iPhone10,4": DeviceInfo("iPhone 8", "A11", True, "15.0", "18.2"),
    "iPhone10,5": DeviceInfo("iPhone 8 Plus", "A11", True, "15.0", "18.2"),
    "iPhone10,6": DeviceInfo("iPhone X", "A11", True, "15.0", "18.2"),
    # A12 devices
    "iPhone11,2": DeviceInfo("iPhone XS", "A12", True, "15.0", "18.2"),
    "iPhone11,4": DeviceInfo("iPhone XS Max", "A12", True, "15.0", "18.2"),
    "iPhone11,6": DeviceInfo("iPhone XS Max", "A12", True, "15.0", "18.2"),
    "iPhone11,8": DeviceInfo("iPhone XR", "A12", True, "15.0", "18.2"),
    # A13 devices
    "iPhone12,1": DeviceInfo("iPhone 11", "A13", True, "15.0", "18.2"),
    "iPhone12,3": DeviceInfo("iPhone 11 Pro", "A13", True, "15.0", "18.2"),
    "iPhone12,5": DeviceInfo("iPhone 11 Pro Max", "A13", True, "15.0", "18.2"),
    # A14 devices
    "iPhone13,1": DeviceInfo("iPhone 12 mini", "A14", True, "15.0", "18.2"),
    "iPhone13,2": DeviceInfo("iPhone 12", "A14", True, "15.0", "18.2"),
    "iPhone13,3": DeviceInfo("iPhone 12 Pro", "A14", True, "15.0", "18.2"),
    "iPhone13,4": DeviceInfo("iPhone 12 Pro Max", "A14", True, "15.0", "18.2"),
    # A15 devices
    "iPhone14,2": DeviceInfo("iPhone 13 Pro", "A15", True, "15.0", "18.2"),
    "iPhone14,3": DeviceInfo("iPhone 13 Pro Max", "A15", True, "15.0", "18.2"),
    "iPhone14,4": DeviceInfo("iPhone 13 mini", "A15", True, "15.0", "18.2"),
    "iPhone14,5": DeviceInfo("iPhone 13", "A15", True, "15.0", "18.2"),
    "iPhone14,7": DeviceInfo("iPhone 14", "A15", True, "15.0", "18.2"),
    "iPhone14,8": DeviceInfo("iPhone 14 Plus", "A15", True, "15.0", "18.2"),
    # A16 devices
    "iPhone15,2": DeviceInfo("iPhone 14 Pro", "A16", True, "16.0", "18.2"),
    "iPhone15,3": DeviceInfo("iPhone 14 Pro Max", "A16", True, "16.0", "18.2"),
    "iPhone15,4": DeviceInfo("iPhone 15", "A16", True, "16.0", "18.2"),
    "iPhone15,5": DeviceInfo("iPhone 15 Plus", "A16", True, "16.0", "18.2"),
    # A17 devices
    "iPhone16,1": DeviceInfo("iPhone 15 Pro", "A17", True, "17.0", "18.2"),
    "iPhone16,2": DeviceInfo("iPhone 15 Pro Max", "A17", True, "17.0", "18.2"),
}


def is_supported(model_id: str) -> bool:
    """Check if device model is supported."""
    info = DEVICE_DB.get(model_id)
    return info.supported if info else False


def get_device_info(model_id: str) -> Optional[DeviceInfo]:
    """Get device info by model identifier."""
    return DEVICE_DB.get(model_id)


def is_ios_supported(version: str) -> bool:
    """Check if iOS version is in supported range."""
    try:
        parts = version.split(".")
        major = int(parts[0])
        minor = int(parts[1]) if len(parts) > 1 else 0
        # Supported: iOS 15.0 - 18.2
        if major < 15:
            return False
        if major > 18:
            return False
        if major == 18 and minor > 2:
            return False
        return True
    except (ValueError, IndexError):
        return False


def get_chip_for_model(model_id: str) -> str:
    """Get chip type for model."""
    info = DEVICE_DB.get(model_id)
    return info.chip if info else "Unknown"
