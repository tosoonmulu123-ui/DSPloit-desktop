"""
PC ↔ Agent communication protocol.
File-based via AFC before jailbreak, SSH after jailbreak.

Protocol:
  PC writes command to:  /var/tmp/.dsploit_cmd
  Agent reads, executes, writes result to: /var/tmp/.dsploit_result
  Agent appends logs to: /var/tmp/.dsploit_log
  PC polls result + log files
"""

import time
from enum import Enum
from typing import Optional, Tuple
from dataclasses import dataclass

from src.usb.afc_client import AFCClient
from src.utils.logger import Logger
from src.utils.config import Config


class AgentStatus(Enum):
    NOT_DEPLOYED = "not_deployed"
    DEPLOYED = "deployed"
    RUNNING = "running"
    READY = "ready"
    BUSY = "busy"
    DISCONNECTED = "disconnected"


@dataclass
class AgentResponse:
    """Response from agent."""
    success: bool
    result: str
    logs: list  # List of log lines since last command


class AgentComm:
    """
    Communication layer between PC and on-device agent.
    Uses file-based protocol via AFC.
    """

    def __init__(self, afc: AFCClient):
        self._logger = Logger.get_instance()
        self._afc = afc
        self._config = Config.get_instance()
        self._status = AgentStatus.NOT_DEPLOYED
        self._last_log_offset = 0

    @property
    def status(self) -> AgentStatus:
        return self._status

    def check_agent_ready(self) -> bool:
        """Check if agent is running and ready for commands."""
        result = self._afc.read_file(self._config.result_file)
        if result and b"READY" in result:
            self._status = AgentStatus.READY
            return True
        return False

    def send_command(self, command: str, timeout: Optional[float] = None) -> AgentResponse:
        """
        Send command to agent and wait for response.
        Returns AgentResponse with result and logs.
        Timeout = None means use config panic_timeout.
        """
        if timeout is None:
            timeout = self._config.panic_timeout

        self._logger.exploit(f"CMD → {command}")

        # Clear previous result
        self._afc.write_file(self._config.result_file, b"")

        # Write command
        self._afc.write_file(self._config.cmd_file, command.encode("utf-8"))
        self._status = AgentStatus.BUSY

        # Poll for result
        start = time.time()
        while time.time() - start < timeout:
            # Read result
            result_data = self._afc.read_file(self._config.result_file)
            if result_data and len(result_data) > 0:
                result_str = result_data.decode("utf-8", errors="replace").strip()
                if result_str and result_str != "":
                    # Got response
                    logs = self._read_new_logs()
                    self._status = AgentStatus.READY

                    success = result_str.startswith("RESULT:") or result_str == "OK"
                    self._logger.exploit(f"RSP ← {result_str}")

                    return AgentResponse(
                        success=success,
                        result=result_str,
                        logs=logs,
                    )

            # Read logs while waiting
            self._stream_logs()
            time.sleep(self._config.poll_interval)

        # Timeout — likely panic
        self._status = AgentStatus.DISCONNECTED
        logs = self._read_new_logs()
        self._logger.panic(
            last_step="(see log)",
            panic_step=command,
        )

        return AgentResponse(
            success=False,
            result="TIMEOUT:device_disconnected",
            logs=logs,
        )

    def send_ping(self) -> bool:
        """Quick ping to check agent is alive."""
        resp = self.send_command("PING", timeout=3.0)
        return resp.success and "PONG" in resp.result

    def send_kread64(self, address: int) -> Optional[int]:
        """Read 64-bit kernel value."""
        resp = self.send_command(f"KREAD64:0x{address:x}")
        if resp.success and resp.result.startswith("RESULT:"):
            try:
                return int(resp.result.split(":")[1], 16)
            except ValueError:
                return None
        return None

    def send_kwrite64(self, address: int, value: int) -> bool:
        """Write 64-bit kernel value."""
        resp = self.send_command(f"KWRITE64:0x{address:x}:0x{value:x}")
        return resp.success

    def send_exploit_run(self) -> AgentResponse:
        """Trigger darksword exploit."""
        return self.send_command("EXPLOIT_RUN", timeout=30.0)

    def send_full_chain(self) -> AgentResponse:
        """Run full 7-step jailbreak chain."""
        return self.send_command("FULL_CHAIN", timeout=120.0)

    def _read_new_logs(self) -> list:
        """Read new log entries from agent log file."""
        data = self._afc.read_file(self._config.log_file_path)
        if not data:
            return []

        text = data.decode("utf-8", errors="replace")
        lines = text.split("\n")

        new_lines = lines[self._last_log_offset:]
        self._last_log_offset = len(lines)

        return [l for l in new_lines if l.strip()]

    def _stream_logs(self):
        """Stream new logs to PC logger."""
        new_logs = self._read_new_logs()
        for line in new_logs:
            self._logger.exploit(f"[AGENT] {line}")
