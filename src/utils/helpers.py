"""
Helper utilities.
Port from: helpers.swift
"""

import struct
from typing import Optional


def hex_str(value: int, width: int = 16) -> str:
    """Format integer as hex string."""
    return f"0x{value:0{width}x}"


def parse_hex(s: str) -> Optional[int]:
    """Parse hex string to integer."""
    try:
        s = s.strip()
        if s.startswith("0x") or s.startswith("0X"):
            return int(s, 16)
        return int(s, 16)
    except ValueError:
        return None


def pack64(value: int) -> bytes:
    """Pack 64-bit value as little-endian bytes."""
    return struct.pack("<Q", value & 0xFFFFFFFFFFFFFFFF)


def unpack64(data: bytes) -> int:
    """Unpack 64-bit little-endian value."""
    return struct.unpack("<Q", data[:8])[0]


def pack32(value: int) -> bytes:
    """Pack 32-bit value as little-endian bytes."""
    return struct.pack("<I", value & 0xFFFFFFFF)


def unpack32(data: bytes) -> int:
    """Unpack 32-bit little-endian value."""
    return struct.unpack("<I", data[:4])[0]


def align(value: int, alignment: int) -> int:
    """Align value up to alignment boundary."""
    return (value + alignment - 1) & ~(alignment - 1)


def human_size(size_bytes: int) -> str:
    """Convert bytes to human-readable size."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"
