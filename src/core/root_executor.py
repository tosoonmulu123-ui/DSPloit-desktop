"""
Root Executor — execute commands as root on jailbroken device.
Port from: RootExecutor.swift

After jailbreak, provides interface to run arbitrary commands
on device with root privileges (via SSH or agent).
"""

from typing import Optional, Tuple
from dataclasses import dataclass

from src.usb.agent_comm import AgentComm
from src.utils.logger import Logger


@dataclass
class ExecResult:
    """Result of a remote command execution."""
    exit_code: int
    stdout: str
    stderr: str

    @property
    def success(self) -> bool:
        return self.exit_code == 0


class RootExecutor:
    """
    Execute commands as root on jailbroken device.
    Uses agent command channel or SSH depending on state.
    """

    def __init__(self, agent: AgentComm):
        self._logger = Logger.get_instance()
        self._agent = agent
        self._ssh_session = None  # Set after SSH is available

    def set_ssh(self, ssh_session):
        """Set SSH session for faster execution after jailbreak."""
        self._ssh_session = ssh_session

    def execute(self, command: str, timeout: float = 10.0) -> ExecResult:
        """
        Execute command as root on device.
        Uses SSH if available, falls back to agent.
        """
        self._logger.debug(f"exec: {command}")

        if self._ssh_session:
            return self._exec_ssh(command, timeout)
        return self._exec_agent(command, timeout)

    def _exec_agent(self, command: str, timeout: float) -> ExecResult:
        """Execute via agent command channel."""
        resp = self._agent.send_command(f"EXEC:{command}", timeout=timeout)
        if resp.success:
            # Parse result: "RESULT:exit_code:stdout"
            parts = resp.result.split(":", 2)
            exit_code = int(parts[1]) if len(parts) > 1 else 0
            stdout = parts[2] if len(parts) > 2 else ""
            return ExecResult(exit_code, stdout, "")
        return ExecResult(-1, "", resp.result)

    def _exec_ssh(self, command: str, timeout: float) -> ExecResult:
        """Execute via SSH session."""
        try:
            stdin, stdout, stderr = self._ssh_session.exec_command(
                command, timeout=timeout
            )
            exit_code = stdout.channel.recv_exit_status()
            out = stdout.read().decode("utf-8", errors="replace")
            err = stderr.read().decode("utf-8", errors="replace")
            return ExecResult(exit_code, out, err)
        except Exception as e:
            self._logger.error(f"SSH exec failed: {e}")
            return ExecResult(-1, "", str(e))

    def read_file(self, path: str) -> Optional[str]:
        """Read file contents from device."""
        result = self.execute(f"cat {path}")
        return result.stdout if result.success else None

    def write_file(self, path: str, content: str) -> bool:
        """Write content to file on device."""
        # Escape content for shell
        escaped = content.replace("'", "'\\''")
        result = self.execute(f"printf '%s' '{escaped}' > {path}")
        return result.success

    def file_exists(self, path: str) -> bool:
        """Check if file exists on device."""
        result = self.execute(f"test -f {path} && echo yes || echo no")
        return "yes" in result.stdout

    def chmod(self, path: str, mode: str) -> bool:
        """Change file permissions."""
        result = self.execute(f"chmod {mode} {path}")
        return result.success

    def chown(self, path: str, owner: str) -> bool:
        """Change file ownership."""
        result = self.execute(f"chown {owner} {path}")
        return result.success

    def kill_process(self, pid: int) -> bool:
        """Kill process by PID."""
        result = self.execute(f"kill -9 {pid}")
        return result.success

    def get_pid(self, process_name: str) -> Optional[int]:
        """Get PID of process by name."""
        result = self.execute(f"pgrep {process_name}")
        if result.success and result.stdout.strip():
            try:
                return int(result.stdout.strip().split("\n")[0])
            except ValueError:
                return None
        return None
