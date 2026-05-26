"""
Panic Analyzer — analyze panic logs to determine root cause.
NEW feature (not in iOS version).
"""

from typing import Optional, List
from dataclasses import dataclass
from pathlib import Path

from src.utils.logger import Logger


@dataclass
class PanicAnalysis:
    """Analysis result of a panic event."""
    last_successful_step: str
    panic_step: str
    likely_cause: str
    suggestion: str
    raw_logs: List[str]


class PanicAnalyzer:
    """
    Analyzes panic events to determine what went wrong.
    Correlates PC-side logs with device crash reports.
    """

    # Known panic patterns and their likely causes
    PANIC_PATTERNS = {
        "PPL violation": "Attempted write to PPL-protected memory",
        "kernel data abort": "Invalid kernel memory access",
        "watchdog timeout": "Operation took too long, device watchdog triggered",
        "EXC_BAD_ACCESS": "Accessed unmapped or protected memory",
        "AMFI": "AMFI enforcement blocked the operation",
        "cs_enforcement": "Code signing enforcement triggered",
        "sandbox violation": "Sandbox policy prevented access",
    }

    def __init__(self):
        self._logger = Logger.get_instance()

    def analyze(
        self,
        last_step: str,
        panic_step: str,
        logs: List[str],
        crash_log: Optional[str] = None,
    ) -> PanicAnalysis:
        """Analyze a panic event and provide diagnosis."""
        likely_cause = self._determine_cause(panic_step, logs, crash_log)
        suggestion = self._suggest_fix(panic_step, likely_cause)

        analysis = PanicAnalysis(
            last_successful_step=last_step,
            panic_step=panic_step,
            likely_cause=likely_cause,
            suggestion=suggestion,
            raw_logs=logs,
        )

        self._logger.info(f"Panic analysis: {likely_cause}")
        self._logger.info(f"Suggestion: {suggestion}")
        return analysis

    def _determine_cause(
        self, panic_step: str, logs: List[str], crash_log: Optional[str]
    ) -> str:
        """Determine likely cause from logs and crash report."""
        all_text = " ".join(logs)
        if crash_log:
            all_text += " " + crash_log

        for pattern, cause in self.PANIC_PATTERNS.items():
            if pattern.lower() in all_text.lower():
                return cause

        # Infer from step name
        if "write" in panic_step.lower() or "patch" in panic_step.lower():
            return "Write to protected memory region"
        if "mprotect" in panic_step.lower():
            return "Memory protection change blocked"
        if "amfi" in panic_step.lower():
            return "AMFI enforcement active"

        return "Unknown — check crash log for details"

    def _suggest_fix(self, panic_step: str, cause: str) -> str:
        """Suggest next action based on analysis."""
        if "PPL" in cause:
            return "Try vm_remap approach instead of direct write"
        if "AMFI" in cause:
            return "Try different AMFI bypass method (kill+race, cryptex, or RC patch)"
        if "watchdog" in cause:
            return "Operation too slow — optimize or split into smaller steps"
        if "sandbox" in cause:
            return "Ensure sandbox escape completed before this step"
        if "code signing" in cause:
            return "Need to inject trust cache before loading unsigned code"
        return "Review logs and try alternative approach"
