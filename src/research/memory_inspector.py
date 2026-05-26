"""
Memory Inspector — inspect kernel memory from PC.
NEW feature (not in iOS version).
"""

from typing import Optional, List
from dataclasses import dataclass

from src.usb.agent_comm import AgentComm
from src.utils.logger import Logger
from src.utils.helpers import hex_str


@dataclass
class MemoryRegion:
    """A region of kernel memory."""
    address: int
    size: int
    data: bytes
    label: str = ""


class MemoryInspector:
    """
    Inspect kernel memory from PC via agent.
    Read, dump, and analyze kernel memory regions.
    """

    def __init__(self, agent: AgentComm):
        self._logger = Logger.get_instance()
        self._agent = agent

    def read64(self, address: int) -> Optional[int]:
        """Read 64-bit value from kernel memory."""
        return self._agent.send_kread64(address)

    def read32(self, address: int) -> Optional[int]:
        """Read 32-bit value from kernel memory."""
        resp = self._agent.send_command(f"KREAD32:0x{address:x}")
        if resp.success:
            try:
                return int(resp.result.split(":")[1], 16)
            except (ValueError, IndexError):
                return None
        return None

    def write64(self, address: int, value: int) -> bool:
        """Write 64-bit value to kernel memory."""
        return self._agent.send_kwrite64(address, value)

    def dump(self, address: int, size: int) -> Optional[bytes]:
        """Dump memory region."""
        resp = self._agent.send_command(
            f"KDUMP:0x{address:x}:{size}", timeout=30.0
        )
        if resp.success:
            # Result is hex-encoded bytes
            hex_data = resp.result.split(":")[1] if ":" in resp.result else ""
            try:
                return bytes.fromhex(hex_data)
            except ValueError:
                return None
        return None

    def hexdump(self, address: int, size: int = 64) -> str:
        """Get formatted hexdump of memory region."""
        data = self.dump(address, size)
        if not data:
            return f"Failed to read 0x{address:x}"

        lines = []
        for offset in range(0, len(data), 16):
            chunk = data[offset:offset + 16]
            hex_part = " ".join(f"{b:02x}" for b in chunk)
            ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
            addr = address + offset
            lines.append(f"0x{addr:016x}: {hex_part:<48} {ascii_part}")

        return "\n".join(lines)

    def find_proc(self, pid: int) -> Optional[int]:
        """Find proc struct address for given PID."""
        resp = self._agent.send_command(f"FIND_PROC:{pid}")
        if resp.success:
            try:
                return int(resp.result.split(":")[1], 16)
            except (ValueError, IndexError):
                return None
        return None

    def read_proc_info(self, proc_addr: int) -> dict:
        """Read basic proc struct fields."""
        info = {}
        pid = self.read32(proc_addr + 0x68)  # proc->p_pid
        if pid is not None:
            info["pid"] = pid

        ucred = self.read64(proc_addr + 0xD8)  # proc->p_ucred
        if ucred is not None:
            info["ucred"] = ucred
            uid = self.read32(ucred + 0x18)  # ucred->cr_uid
            if uid is not None:
                info["uid"] = uid

        return info
