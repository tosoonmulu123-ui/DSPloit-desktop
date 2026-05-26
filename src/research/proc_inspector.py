"""
Process Inspector — inspect running processes on device.
"""

from typing import Optional, List, Dict
from dataclasses import dataclass

from src.usb.agent_comm import AgentComm
from src.utils.logger import Logger


@dataclass
class ProcessInfo:
    pid: int
    name: str
    uid: int
    proc_addr: int


class ProcInspector:
    """Inspect running processes via kernel memory."""

    def __init__(self, agent: AgentComm):
        self._logger = Logger.get_instance()
        self._agent = agent

    def list_processes(self) -> List[ProcessInfo]:
        """Get list of running processes."""
        resp = self._agent.send_command("PROC_LIST", timeout=15.0)
        if not resp.success:
            return []

        processes = []
        for line in resp.result.split("\n"):
            parts = line.split(":")
            if len(parts) >= 4:
                try:
                    processes.append(ProcessInfo(
                        pid=int(parts[0]),
                        name=parts[1],
                        uid=int(parts[2]),
                        proc_addr=int(parts[3], 16),
                    ))
                except ValueError:
                    continue
        return processes

    def find_by_name(self, name: str) -> Optional[ProcessInfo]:
        """Find process by name."""
        for proc in self.list_processes():
            if proc.name == name:
                return proc
        return None

    def find_by_pid(self, pid: int) -> Optional[ProcessInfo]:
        """Find process by PID."""
        for proc in self.list_processes():
            if proc.pid == pid:
                return proc
        return None
