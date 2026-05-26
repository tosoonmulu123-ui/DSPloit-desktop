"""
Crash/panic log reader.
After device reboots from panic, reads crash logs to analyze what happened.
"""

from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime

from pymobiledevice3.lockdown import LockdownClient
from pymobiledevice3.services.crash_reports import CrashReportsManager

from src.utils.logger import Logger


@dataclass
class PanicLog:
    """Parsed panic log entry."""
    timestamp: datetime
    reason: str
    backtrace: List[str]
    faulting_address: Optional[int]
    raw: str


class CrashReader:
    """
    Reads and parses crash/panic logs from device after reboot.
    """

    def __init__(self, lockdown: LockdownClient):
        self._logger = Logger.get_instance()
        self._lockdown = lockdown

    def get_panic_logs(self) -> List[PanicLog]:
        """Retrieve all panic logs from device."""
        try:
            crash_mgr = CrashReportsManager(self._lockdown)
            panics = []

            for report in crash_mgr.ls("/"):
                if "panic" in report.lower() or "Panic" in report:
                    content = crash_mgr.get_file(report)
                    parsed = self._parse_panic(content)
                    if parsed:
                        panics.append(parsed)

            self._logger.info(f"Found {len(panics)} panic logs")
            return panics

        except Exception as e:
            self._logger.error(f"Failed to read crash logs: {e}")
            return []

    def get_latest_panic(self) -> Optional[PanicLog]:
        """Get the most recent panic log."""
        panics = self.get_panic_logs()
        if panics:
            return sorted(panics, key=lambda p: p.timestamp, reverse=True)[0]
        return None

    def _parse_panic(self, raw: str) -> Optional[PanicLog]:
        """Parse raw panic log text."""
        try:
            lines = raw.split("\n")
            reason = ""
            backtrace = []
            fault_addr = None
            timestamp = datetime.now()

            for line in lines:
                if "panic" in line.lower() and not reason:
                    reason = line.strip()
                elif "Fault Address" in line or "far:" in line.lower():
                    # Try to extract faulting address
                    parts = line.split("0x")
                    if len(parts) > 1:
                        try:
                            fault_addr = int(parts[-1].strip().split()[0], 16)
                        except ValueError:
                            pass
                elif line.strip().startswith("0x") or "frame" in line.lower():
                    backtrace.append(line.strip())

            return PanicLog(
                timestamp=timestamp,
                reason=reason,
                backtrace=backtrace,
                faulting_address=fault_addr,
                raw=raw,
            )
        except Exception:
            return None

    def clear_panic_logs(self):
        """Clear panic logs from device (after reading)."""
        try:
            crash_mgr = CrashReportsManager(self._lockdown)
            for report in crash_mgr.ls("/"):
                if "panic" in report.lower():
                    crash_mgr.delete(report)
            self._logger.info("Panic logs cleared")
        except Exception as e:
            self._logger.warn(f"Could not clear panic logs: {e}")
