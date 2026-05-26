"""
Configuration management for DSPloit PC.
"""

import json
from pathlib import Path
from typing import Any, Optional


DEFAULT_CONFIG = {
    "usb_timeout": 5.0,
    "poll_interval": 0.5,
    "agent_path_on_device": "/var/tmp/.dsploit_agent",
    "cmd_file": "/var/tmp/.dsploit_cmd",
    "result_file": "/var/tmp/.dsploit_result",
    "log_file": "/var/tmp/.dsploit_log",
    "ssh_port": 2222,
    "ssh_user": "root",
    "ssh_password": "alpine",
    "auto_ssh_after_jailbreak": True,
    "step_delay": 0.1,
    "panic_timeout": 10.0,
    "log_dir": "logs",
    "theme": "dark",
}


class Config:
    """Application configuration with file persistence."""

    _instance: Optional["Config"] = None
    _config_path = Path("config.json")

    @classmethod
    def get_instance(cls) -> "Config":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._data = dict(DEFAULT_CONFIG)
        self._load()

    def _load(self):
        """Load config from file if exists."""
        if self._config_path.exists():
            try:
                with open(self._config_path, "r") as f:
                    saved = json.load(f)
                self._data.update(saved)
            except (json.JSONDecodeError, IOError):
                pass

    def save(self):
        """Save config to file."""
        with open(self._config_path, "w") as f:
            json.dump(self._data, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any):
        self._data[key] = value
        self.save()

    @property
    def usb_timeout(self) -> float:
        return self._data["usb_timeout"]

    @property
    def poll_interval(self) -> float:
        return self._data["poll_interval"]

    @property
    def agent_path(self) -> str:
        return self._data["agent_path_on_device"]

    @property
    def cmd_file(self) -> str:
        return self._data["cmd_file"]

    @property
    def result_file(self) -> str:
        return self._data["result_file"]

    @property
    def log_file_path(self) -> str:
        return self._data["log_file"]

    @property
    def ssh_port(self) -> int:
        return self._data["ssh_port"]

    @property
    def ssh_user(self) -> str:
        return self._data["ssh_user"]

    @property
    def ssh_password(self) -> str:
        return self._data["ssh_password"]

    @property
    def panic_timeout(self) -> float:
        return self._data["panic_timeout"]
