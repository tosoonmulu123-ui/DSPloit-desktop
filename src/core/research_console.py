"""
Research Console — step-by-step exploit execution with panic-safe logging.
NEW feature (not in iOS version).

This is the core value-add of DSPloit PC:
- Execute exploit steps one at a time
- Log EVERY step to PC before execution
- If device panics, know exactly which step caused it
- Binary search for exact instruction that triggers PPL/panic
"""

import time
from typing import Optional, List, Callable
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum

from src.usb.agent_comm import AgentComm, AgentResponse
from src.utils.logger import Logger


class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    PANIC = "panic"
    SKIPPED = "skipped"


@dataclass
class ResearchStep:
    """A single research step."""
    name: str
    command: str
    description: str = ""
    timeout: float = 10.0
    status: StepStatus = StepStatus.PENDING
    result: str = ""
    duration: float = 0.0


@dataclass
class Experiment:
    """A research experiment = ordered list of steps."""
    name: str
    description: str
    steps: List[ResearchStep] = field(default_factory=list)
    created: str = ""


@dataclass
class ExperimentResult:
    """Result of running an experiment."""
    experiment: Experiment
    completed_steps: int
    total_steps: int
    panic_at_step: Optional[int]
    last_success: Optional[str]
    panic_step: Optional[str]
    log_file: Path
    duration: float


class ResearchConsole:
    """
    Execute exploit steps one-by-one with panic-safe logging.
    The key feature of DSPloit PC.
    """

    def __init__(self, agent: AgentComm):
        self._logger = Logger.get_instance()
        self._agent = agent
        self._on_step_complete: Optional[Callable[[int, StepStatus, str], None]] = None
        self._on_panic: Optional[Callable[[str, str], None]] = None

    def set_callbacks(
        self,
        on_step: Optional[Callable[[int, StepStatus, str], None]] = None,
        on_panic: Optional[Callable[[str, str], None]] = None,
    ):
        """Set callbacks for step completion and panic events."""
        self._on_step_complete = on_step
        self._on_panic = on_panic

    def step(self, name: str, command: str, timeout: float = 10.0) -> ResearchStep:
        """
        Execute a single research step with panic-safe logging.

        1. Log step name + command to PC file (FLUSH)
        2. Send command to device agent
        3. Wait for result (or timeout = panic)
        4. Log result to PC file (FLUSH)
        5. Return result
        """
        step = ResearchStep(name=name, command=command, timeout=timeout)

        # Log BEFORE execution (panic-safe)
        self._logger.exploit(f"STEP: {name}")
        self._logger.exploit(f"  CMD: {command}")
        step.status = StepStatus.RUNNING

        # Execute
        start = time.time()
        resp = self._agent.send_command(command, timeout=timeout)
        step.duration = time.time() - start

        if resp.success:
            step.status = StepStatus.SUCCESS
            step.result = resp.result
            self._logger.exploit(f"  RESULT: {resp.result} ✓ ({step.duration:.2f}s)")
        elif "TIMEOUT" in resp.result:
            step.status = StepStatus.PANIC
            step.result = "DEVICE DISCONNECTED (panic)"
            self._logger.panic(last_step="(previous)", panic_step=name)
        else:
            step.status = StepStatus.FAILED
            step.result = resp.result
            self._logger.exploit(f"  FAILED: {resp.result} ✗")

        return step

    def run_experiment(self, experiment: Experiment) -> ExperimentResult:
        """
        Run all steps of an experiment with full logging.
        Stops on first failure/panic.
        """
        log_file = self._logger.start_experiment(experiment.name)
        self._logger.exploit(f"═══ EXPERIMENT: {experiment.name} ═══")
        self._logger.exploit(f"    {experiment.description}")
        self._logger.exploit(f"    Steps: {len(experiment.steps)}")
        self._logger.exploit("═" * 50)

        start_time = time.time()
        completed = 0
        last_success_name = None
        panic_step_name = None
        panic_at = None

        for i, step_def in enumerate(experiment.steps):
            self._logger.step(i + 1, len(experiment.steps), step_def.name)

            result = self.step(step_def.name, step_def.command, step_def.timeout)
            experiment.steps[i] = result

            if self._on_step_complete:
                self._on_step_complete(i, result.status, result.result)

            if result.status == StepStatus.SUCCESS:
                completed += 1
                last_success_name = result.name
            elif result.status == StepStatus.PANIC:
                panic_at = i
                panic_step_name = result.name
                if self._on_panic:
                    self._on_panic(last_success_name or "none", panic_step_name)
                break
            else:
                # Failed but not panic — stop experiment
                break

        duration = time.time() - start_time

        # Generate report
        report = ExperimentResult(
            experiment=experiment,
            completed_steps=completed,
            total_steps=len(experiment.steps),
            panic_at_step=panic_at,
            last_success=last_success_name,
            panic_step=panic_step_name,
            log_file=log_file,
            duration=duration,
        )

        self._log_report(report)
        return report

    def panic_report(self, result: ExperimentResult) -> str:
        """Generate human-readable panic report."""
        lines = [
            "",
            "⚠️  PANIC REPORT",
            "├── Experiment: " + result.experiment.name,
            f"├── Completed: {result.completed_steps}/{result.total_steps} steps",
            f"├── Last success: {result.last_success or 'none'}",
            f"├── Panic step: {result.panic_step or 'none'}",
            f"├── Duration: {result.duration:.2f}s",
            f"└── Log: {result.log_file}",
            "",
        ]
        return "\n".join(lines)

    def _log_report(self, result: ExperimentResult):
        """Log experiment result."""
        self._logger.exploit("═" * 50)
        if result.panic_at_step is not None:
            self._logger.exploit(self.panic_report(result))
        else:
            self._logger.exploit(
                f"EXPERIMENT COMPLETE: {result.completed_steps}/{result.total_steps} steps"
            )
        self._logger.exploit(f"Log saved: {result.log_file}")
