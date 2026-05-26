"""
IOKit Fuzzer — probe IOKit services for vulnerabilities.
Port from: IOKitFuzzer.swift
"""

from typing import List, Optional
from dataclasses import dataclass

from src.usb.agent_comm import AgentComm
from src.utils.logger import Logger


@dataclass
class IOKitService:
    name: str
    class_name: str
    port: int


@dataclass
class FuzzResult:
    service: str
    selector: int
    crashed: bool
    response: str


class IOKitFuzzer:
    """
    Probe IOKit services by sending various selectors.
    Useful for finding new kernel vulnerabilities.
    """

    def __init__(self, agent: AgentComm):
        self._logger = Logger.get_instance()
        self._agent = agent

    def list_services(self) -> List[IOKitService]:
        """List available IOKit services."""
        resp = self._agent.send_command("IOKIT_LIST", timeout=10.0)
        services = []
        if resp.success:
            for line in resp.result.split("\n"):
                parts = line.split(":")
                if len(parts) >= 3:
                    services.append(IOKitService(
                        name=parts[0],
                        class_name=parts[1],
                        port=int(parts[2]) if parts[2].isdigit() else 0,
                    ))
        return services

    def fuzz_selector(self, service: str, selector: int) -> FuzzResult:
        """Send a selector to IOKit service and observe result."""
        self._logger.exploit(f"IOKit fuzz: {service} selector={selector}")
        resp = self._agent.send_command(
            f"IOKIT_CALL:{service}:{selector}",
            timeout=5.0,
        )
        crashed = "TIMEOUT" in resp.result
        return FuzzResult(
            service=service,
            selector=selector,
            crashed=crashed,
            response=resp.result,
        )

    def fuzz_range(self, service: str, start: int, end: int) -> List[FuzzResult]:
        """Fuzz a range of selectors."""
        results = []
        for sel in range(start, end):
            result = self.fuzz_selector(service, sel)
            results.append(result)
            if result.crashed:
                self._logger.warn(f"CRASH at selector {sel}!")
                break
        return results
