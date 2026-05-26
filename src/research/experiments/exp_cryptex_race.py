"""
Experiment: AMFI bypass via cryptex race condition.

Strategy:
1. Create fake cryptex mount point
2. Place unsigned binary in cryptex path
3. Race mount/unmount to confuse AMFI validation
"""

from typing import List
from src.research.experiment_base import ExperimentBase
from src.core.research_console import ResearchStep


class ExpCryptexRace(ExperimentBase):
    @property
    def name(self) -> str:
        return "cryptex_race"

    @property
    def description(self) -> str:
        return "Bypass AMFI via cryptex mount race condition"

    def build_steps(self) -> List[ResearchStep]:
        return [
            ResearchStep(
                name="Create fake cryptex directory",
                command="EXEC:mkdir -p /private/var/tmp/cryptex_fake",
                timeout=5.0,
            ),
            ResearchStep(
                name="Deploy unsigned binary to cryptex path",
                command="DEPLOY_TO_CRYPTEX_PATH",
                timeout=5.0,
            ),
            ResearchStep(
                name="Setup mount race",
                command="SETUP_CRYPTEX_RACE",
                timeout=5.0,
            ),
            ResearchStep(
                name="Trigger race (mount + exec)",
                command="TRIGGER_CRYPTEX_RACE",
                timeout=10.0,
            ),
            ResearchStep(
                name="Verify execution",
                command="VERIFY_CRYPTEX_EXEC",
                timeout=5.0,
            ),
        ]
