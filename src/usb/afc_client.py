"""
AFC (Apple File Conduit) client for file operations on device.
Used for deploying agent and file-based communication before jailbreak.
"""

from typing import Optional
from pathlib import PurePosixPath

from pymobiledevice3.lockdown import LockdownClient
from pymobiledevice3.services.afc import AfcService

from src.utils.logger import Logger


class AFCClient:
    """
    Wrapper around pymobiledevice3 AFC service.
    Provides file read/write on device filesystem (sandboxed areas).
    """

    def __init__(self, lockdown: LockdownClient):
        self._logger = Logger.get_instance()
        self._lockdown = lockdown
        self._afc: Optional[AfcService] = None

    def connect(self) -> bool:
        """Start AFC service."""
        try:
            self._afc = AfcService(lockdown=self._lockdown)
            self._logger.info("AFC service connected")
            return True
        except Exception as e:
            self._logger.error(f"AFC connect failed: {e}")
            return False

    @property
    def connected(self) -> bool:
        return self._afc is not None

    def read_file(self, remote_path: str) -> Optional[bytes]:
        """Read file from device."""
        if not self._afc:
            return None
        try:
            return self._afc.get_file_contents(remote_path)
        except Exception as e:
            self._logger.debug(f"AFC read {remote_path}: {e}")
            return None

    def write_file(self, remote_path: str, data: bytes) -> bool:
        """Write file to device."""
        if not self._afc:
            return False
        try:
            self._afc.set_file_contents(remote_path, data)
            return True
        except Exception as e:
            self._logger.error(f"AFC write {remote_path}: {e}")
            return False

    def file_exists(self, remote_path: str) -> bool:
        """Check if file exists on device."""
        if not self._afc:
            return False
        try:
            self._afc.stat(remote_path)
            return True
        except Exception:
            return False

    def mkdir(self, remote_path: str) -> bool:
        """Create directory on device."""
        if not self._afc:
            return False
        try:
            self._afc.makedirs(remote_path)
            return True
        except Exception as e:
            self._logger.debug(f"AFC mkdir {remote_path}: {e}")
            return False

    def remove(self, remote_path: str) -> bool:
        """Remove file from device."""
        if not self._afc:
            return False
        try:
            self._afc.rm(remote_path)
            return True
        except Exception as e:
            self._logger.debug(f"AFC rm {remote_path}: {e}")
            return False

    def list_dir(self, remote_path: str) -> list:
        """List directory contents."""
        if not self._afc:
            return []
        try:
            return list(self._afc.listdir(remote_path))
        except Exception:
            return []

    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """Upload local file to device."""
        try:
            with open(local_path, "rb") as f:
                data = f.read()
            return self.write_file(remote_path, data)
        except IOError as e:
            self._logger.error(f"Upload failed: {e}")
            return False

    def download_file(self, remote_path: str, local_path: str) -> bool:
        """Download file from device to local."""
        data = self.read_file(remote_path)
        if data is None:
            return False
        try:
            with open(local_path, "wb") as f:
                f.write(data)
            return True
        except IOError as e:
            self._logger.error(f"Download failed: {e}")
            return False
