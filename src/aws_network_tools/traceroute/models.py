"""Data models for traceroute."""

from dataclasses import dataclass, field
from typing import Literal

HopType = Literal[
    "eni", "route_table", "cloud_wan_segment", "nfg", "firewall", "destination"
]


@dataclass
class Hop:
    """Single hop in the trace path."""

    seq: int
    type: HopType
    id: str
    name: str = ""
    region: str = ""
    detail: dict = field(default_factory=dict)

    def __str__(self):
        name_str = f" ({self.name})" if self.name else ""
        return f"{self.seq}. [{self.type}] {self.id}{name_str} @ {self.region}"


@dataclass
class SecurityCheck:
    """Security evaluation at a hop."""

    component: str  # sg, nacl, firewall
    id: str
    verdict: Literal["allow", "deny", "unknown"]
    reason: str = ""


@dataclass
class TraceResult:
    """Complete trace result."""

    src_ip: str
    dst_ip: str
    reachable: bool
    hops: list[Hop] = field(default_factory=list)
    security_checks: list[SecurityCheck] = field(default_factory=list)
    blocked_at: Hop | None = None
    blocked_reason: str = ""

    def summary(self) -> str:
        status = (
            "✅ REACHABLE" if self.reachable else f"❌ BLOCKED at {self.blocked_at}"
        )
        lines = [f"Trace: {self.src_ip} → {self.dst_ip}", status, "", "Path:"]
        for hop in self.hops:
            lines.append(f"  {hop}")
        if self.blocked_reason:
            lines.append(f"\nBlocked: {self.blocked_reason}")
        return "\n".join(lines)
