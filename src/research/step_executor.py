"""
Step Executor — execute individual research steps with full control.
Provides fine-grained control over step execution for debugging.
"""

from typing import Optional, List
from dataclasses import dataclass

from src.usb.agent_comm import AgentComm
from src.core.research_console import ResearchConsole, ResearchStep, StepStatus
from src.utils.logger import Logger


class StepExecutor:
    """
    Execute steps one at a time with manual control.
    For interactive research sessions.
    """

    def __init__(self, agent: AgentComm):
        self._logger = Logger.get_instance()
        self._console = ResearchConsole(agent)
        self._agent = agent
        self._history: List[ResearchStep] = []

    @property
    def history(self) -> List[ResearchStep]:
        return self._history

    @property
    def last_step(self) -> Optional[ResearchStep]:
        return self._history[-1] if self._history else None

    def execute(self, name: str, command: str, timeout: float = 10.0) -> ResearchStep:
        """Execute a single step and record in history."""
        result = self._console.step(name, command, timeout)
        self._history.append(result)
        return result

    def kread64(self, address: int) -> Optional[int]:
        """Convenience: read 64-bit kernel value."""
        step = self.execute(
            f"kread64(0x{address:x})",
            f"KREAD64:0x{address:x}",
        )
        if step.status == StepStatus.SUCCESS:
            try:
                return int(step.result.split(":")[1], 16)
            except (ValueError, IndexError):
                return None
        return None

    def kwrite64(self, address: int, value: int) -> bool:
        """Convenience: write 64-bit kernel value."""
        step = self.execute(
            f"kwrite64(0x{address:x}, 0x{value:x})",
            f"KWRITE64:0x{address:x}:0x{value:x}",
        )
        return step.status == StepStatus.SUCCESS

    def exec_on_device(self, command: str) -> Optional[str]:
        """Execute shell command on device."""
        step = self.execute(f"exec({command})", f"EXEC:{command}")
        if step.status == StepStatus.SUCCESS:
            return step.result
        return None

    def clear_history(self):
        """Clear step history."""
        self._history = []
