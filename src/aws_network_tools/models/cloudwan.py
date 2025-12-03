"""Cloud WAN Pydantic models."""

from typing import Optional, Literal
from pydantic import Field, field_validator
from .base import AWSResource


class CloudWANRouteModel(AWSResource):
    """Cloud WAN route entry."""

    id: str = Field(default="route", description="Route identifier")
    prefix: str = Field(..., description="Destination CIDR")
    target: str = Field(..., description="Attachment ID")
    target_type: Optional[str] = Field(None, description="vpc, connect, etc.")
    state: Literal["ACTIVE", "BLACKHOLE", "active", "blackhole"] = Field(
        default="ACTIVE"
    )
    type: Optional[str] = Field(None, description="propagated or static")
    region: str = Field(default="")


class SegmentModel(AWSResource):
    """Cloud WAN Segment."""

    id: str = Field(default="segment", description="Segment identifier")
    edge_locations: list[str] = Field(default_factory=list)
    isolate_attachments: bool = Field(default=False)
    require_attachment_acceptance: bool = Field(default=False)


class CoreNetworkModel(AWSResource):
    """Cloud WAN Core Network model."""

    global_network_id: str = Field(..., description="Parent global network ID")
    global_network_name: Optional[str] = Field(None)
    state: str = Field(default="AVAILABLE")
    segments: list[str] = Field(default_factory=list, description="Segment names")
    regions: list[str] = Field(default_factory=list, description="Edge locations")
    nfgs: list[str] = Field(default_factory=list, description="Network function groups")
    route_tables: list[dict] = Field(default_factory=list)
    policy: Optional[dict] = Field(None, description="Live policy document")

    @field_validator("id")
    @classmethod
    def validate_cn_id(cls, v: str) -> str:
        if not v.startswith("core-network-"):
            raise ValueError(f"Core Network ID must start with 'core-network-': {v}")
        return v
