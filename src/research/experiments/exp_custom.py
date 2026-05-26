"""
Custom Experiment — user-defined step sequences.
Allows creating experiments at runtime from the GUI.
"""

from typing import List
from src.research.experiment_base import ExperimentBase
from src.core.research_console import ResearchStep


class ExpCustom(ExperimentBase):
    """User-defined custom experiment."""

    def __init__(self, exp_name: str, exp_description: str, steps: List[ResearchStep]):
        self._name = exp_name
        self._description = exp_description
        self._steps = steps

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    def build_steps(self) -> List[ResearchStep]:
        return self._steps
