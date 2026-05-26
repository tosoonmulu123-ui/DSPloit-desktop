"""
Panic-safe logger for DSPloit PC.
Every log entry is flushed immediately — if device panics, logs survive on PC.

Port from: Logger.swift
"""

import os
import sys
import logging
import datetime
from pathlib import Path
from typing import Optional


class Logger:
    """Singleton panic-safe logger. Flushes every write immediately."""

    _instance: Optional["Logger"] = None
    _log_dir: Path = Path("logs")

    @classmethod
    def get_instance(cls) -> "Logger":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if Logger._instance is not None:
            raise RuntimeError("Use Logger.get_instance()")

        self._log_dir.mkdir(exist_ok=True)

        # Session log file
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self._session_file = self._log_dir / f"session_{timestamp}.txt"
        self._file_handle = open(self._session_file, "a", buffering=1)  # Line buffered

        # Console handler
        self._console_handler = logging.StreamHandler(sys.stdout)
        self._console_handler.setLevel(logging.DEBUG)

        # Python logging integration
        self._logger = logging.getLogger("dsploit")
        self._logger.setLevel(logging.DEBUG)
        self._logger.addHandler(self._console_handler)

        self.info(f"Log session: {self._session_file}")

    def _write(self, level: str, message: str):
        """Write log entry with immediate flush (panic-safe)."""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        entry = f"[{timestamp}] [{level}] {message}"

        # Write to file and flush immediately
        self._file_handle.write(entry + "\n")
        self._file_handle.flush()
        os.fsync(self._file_handle.fileno())

        # Also print to console
        print(entry)

    def info(self, message: str):
        self._write("INFO", message)

    def warn(self, message: str):
        self._write("WARN", message)

    def error(self, message: str):
        self._write("ERROR", message)

    def debug(self, message: str):
        self._write("DEBUG", message)

    def exploit(self, message: str):
        """Special level for exploit steps — always flushed."""
        self._write("EXPLOIT", message)

    def step(self, step_num: int, total: int, message: str):
        """Log a numbered step (for research console)."""
        self._write("STEP", f"[{step_num}/{total}] {message}")

    def panic(self, last_step: str, panic_step: str):
        """Log panic event with context."""
        self._write("PANIC", f"Device disconnected!")
        self._write("PANIC", f"Last success: {last_step}")
        self._write("PANIC", f"Panic step: {panic_step}")

    def start_experiment(self, name: str) -> Path:
        """Start a new experiment log file. Returns path to log."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        exp_file = self._log_dir / f"{timestamp}_{name}.txt"
        self._write("EXPERIMENT", f"Started: {name} → {exp_file}")
        return exp_file

    @property
    def session_file(self) -> Path:
        return self._session_file

    def close(self):
        if self._file_handle:
            self._file_handle.close()
