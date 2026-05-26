"""
Session Manager — SSH tunnel management after jailbreak.
Manages SSH connection to device for post-jailbreak operations.
"""

import time
from typing import Optional

import paramiko

from src.utils.logger import Logger
from src.utils.config import Config


class SessionManager:
    """
    Manages SSH session to jailbroken device.
    After jailbreak deploys dropbear, this provides SSH access.
    """

    def __init__(self):
        self._logger = Logger.get_instance()
        self._config = Config.get_instance()
        self._client: Optional[paramiko.SSHClient] = None
        self._connected = False

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def client(self) -> Optional[paramiko.SSHClient]:
        return self._client

    def connect(self, host: str = "localhost", port: Optional[int] = None) -> bool:
        """Connect to device via SSH (through USB tunnel)."""
        if port is None:
            port = self._config.ssh_port

        try:
            self._client = paramiko.SSHClient()
            self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self._client.connect(
                hostname=host,
                port=port,
                username=self._config.ssh_user,
                password=self._config.ssh_password,
                timeout=10.0,
                look_for_keys=False,
            )
            self._connected = True
            self._logger.info(f"SSH connected to {host}:{port}")
            return True
        except Exception as e:
            self._logger.error(f"SSH connect failed: {e}")
            self._connected = False
            return False

    def disconnect(self):
        """Close SSH connection."""
        if self._client:
            self._client.close()
            self._client = None
        self._connected = False
        self._logger.info("SSH disconnected")

    def exec_command(self, command: str, timeout: float = 10.0) -> tuple:
        """Execute command via SSH. Returns (exit_code, stdout, stderr)."""
        if not self._client:
            return (-1, "", "Not connected")
        try:
            stdin, stdout, stderr = self._client.exec_command(command, timeout=timeout)
            exit_code = stdout.channel.recv_exit_status()
            out = stdout.read().decode("utf-8", errors="replace")
            err = stderr.read().decode("utf-8", errors="replace")
            return (exit_code, out, err)
        except Exception as e:
            self._logger.error(f"SSH exec error: {e}")
            return (-1, "", str(e))

    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """Upload file via SFTP."""
        if not self._client:
            return False
        try:
            sftp = self._client.open_sftp()
            sftp.put(local_path, remote_path)
            sftp.close()
            return True
        except Exception as e:
            self._logger.error(f"SFTP upload failed: {e}")
            return False

    def download_file(self, remote_path: str, local_path: str) -> bool:
        """Download file via SFTP."""
        if not self._client:
            return False
        try:
            sftp = self._client.open_sftp()
            sftp.get(remote_path, local_path)
            sftp.close()
            return True
        except Exception as e:
            self._logger.error(f"SFTP download failed: {e}")
            return False
