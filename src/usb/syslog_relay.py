"""
Real-time syslog relay from device to PC.
Captures device logs including kernel messages and panic indicators.
"""

import threading
from typing import Optional, Callable

from pymobiledevice3.lockdown import LockdownClient
from pymobiledevice3.services.syslog import SyslogService

from src.utils.logger import Logger


class SyslogRelay:
    """
    Streams device syslog to PC in real-time.
    Useful for monitoring kernel messages and detecting panics.
    """

    def __init__(self, lockdown: LockdownClient):
        self._logger = Logger.get_instance()
        self._lockdown = lockdown
        self._service: Optional[SyslogService] = None
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._on_message: Optional[Callable[[str], None]] = None
        self._on_panic: Optional[Callable[[], None]] = None

    def set_callbacks(
        self,
        on_message: Optional[Callable[[str], None]] = None,
        on_panic: Optional[Callable[[], None]] = None,
    ):
        """Set callbacks for log messages and panic detection."""
        self._on_message = on_message
        self._on_panic = on_panic

    def start(self) -> bool:
        """Start syslog relay in background thread."""
        try:
            self._service = SyslogService(lockdown=self._lockdown)
            self._running = True
            self._thread = threading.Thread(target=self._relay_loop, daemon=True)
            self._thread.start()
            self._logger.info("Syslog relay started")
            return True
        except Exception as e:
            self._logger.error(f"Syslog relay failed: {e}")
            return False

    def stop(self):
        """Stop syslog relay."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        self._logger.info("Syslog relay stopped")

    def _relay_loop(self):
        """Background thread: read syslog messages."""
        try:
            for msg in self._service.watch():
                if not self._running:
                    break

                line = str(msg).strip()
                if not line:
                    continue

                # Log to PC
                self._logger.debug(f"[SYSLOG] {line}")

                # Callback
                if self._on_message:
                    self._on_message(line)

                # Panic detection
                if self._is_panic_indicator(line):
                    self._logger.error("PANIC DETECTED in syslog!")
                    if self._on_panic:
                        self._on_panic()

        except Exception as e:
            if self._running:
                self._logger.error(f"Syslog relay disconnected: {e}")
                if self._on_panic:
                    self._on_panic()

    def _is_panic_indicator(self, line: str) -> bool:
        """Check if syslog line indicates kernel panic."""
        panic_keywords = [
            "panic",
            "kernel data abort",
            "watchdog timeout",
            "userspace watchdog",
            "EXC_BAD_ACCESS",
        ]
        lower = line.lower()
        return any(kw in lower for kw in panic_keywords)
