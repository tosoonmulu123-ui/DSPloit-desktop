"""
Experiment base class — defines interface for all research experiments.
"""

from abc import ABC, abstractmethod
from typing import List

from src.core.research_console import ResearchStep, Experiment


class ExperimentBase(ABC):
    """Base class for all research experiments."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Experiment name."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """What this experiment tests."""
        ...

    @abstractmethod
    def build_steps(self) -> List[ResearchStep]:
        """Build the list of steps for this experiment."""
        ...

    def to_experiment(self) -> Experiment:
        """Convert to Experiment object for ResearchConsole."""
        return Experiment(
            name=self.name,
            description=self.description,
            steps=self.build_steps(),
        )
