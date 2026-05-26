"""
iOS version parsing and comparison utilities.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class IOSVersion:
    major: int
    minor: int
    patch: int = 0

    @classmethod
    def parse(cls, version_str: str) -> Optional["IOSVersion"]:
        """Parse iOS version string like '18.2.1'."""
        try:
            parts = version_str.split(".")
            major = int(parts[0])
            minor = int(parts[1]) if len(parts) > 1 else 0
            patch = int(parts[2]) if len(parts) > 2 else 0
            return cls(major, minor, patch)
        except (ValueError, IndexError):
            return None

    def __str__(self) -> str:
        if self.patch:
            return f"{self.major}.{self.minor}.{self.patch}"
        return f"{self.major}.{self.minor}"

    def __lt__(self, other: "IOSVersion") -> bool:
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)

    def __le__(self, other: "IOSVersion") -> bool:
        return (self.major, self.minor, self.patch) <= (other.major, other.minor, other.patch)

    def __gt__(self, other: "IOSVersion") -> bool:
        return (self.major, self.minor, self.patch) > (other.major, other.minor, other.patch)

    def __ge__(self, other: "IOSVersion") -> bool:
        return (self.major, self.minor, self.patch) >= (other.major, other.minor, other.patch)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, IOSVersion):
            return False
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)

    @property
    def is_supported(self) -> bool:
        """Check if this iOS version is supported by DSPloit."""
        min_ver = IOSVersion(15, 0, 0)
        max_ver = IOSVersion(18, 2, 0)
        return min_ver <= self <= max_ver
