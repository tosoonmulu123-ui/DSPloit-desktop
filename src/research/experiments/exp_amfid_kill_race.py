"""
Experiment: AMFI bypass via amfid kill + race condition.

Strategy:
1. Kill amfid process
2. Race to load unsigned code before launchd respawns amfid
3. If timing is right, code loads without AMFI check
"""

from typing import List
from src.research.experiment_base import ExperimentBase
from src.core.research_console import ResearchStep


class ExpAmfidKillRace(ExperimentBase):
    @property
    def name(self) -> str:
        return "amfid_kill_race"

    @property
    def description(self) -> str:
        return "Bypass AMFI by killing amfid and racing to load code"

    def build_steps(self) -> List[ResearchStep]:
        return [
            ResearchStep(
                name="Find amfid PID",
                command="FIND_PROC_BY_NAME:amfid",
                timeout=5.0,
            ),
            ResearchStep(
                name="Prepare payload for loading",
                command="PREPARE_UNSIGNED_PAYLOAD",
                timeout=5.0,
            ),
            ResearchStep(
                name="Kill amfid",
                command="KILL_PROC:amfid",
                timeout=3.0,
            ),
            ResearchStep(
                name="Race: load unsigned code",
                command="RACE_LOAD_PAYLOAD",
                timeout=2.0,
                description="Must execute before launchd respawns amfid",
            ),
            ResearchStep(
                name="Verify code loaded",
                command="VERIFY_PAYLOAD_LOADED",
                timeout=5.0,
            ),
        ]
