"""Transit Gateway Pydantic models."""

from typing import Optional, Literal
from pydantic import Field, field_validator
from .base import AWSResource


class TGWRouteModel(AWSResource):
    """TGW Route entry."""

    id: str = Field(default="route", description="Route identifier")
    prefix: str = Field(..., description="Destination CIDR")
    target: str = Field(..., description="Attachment ID")
    target_type: Optional[str] = Field(None, description="vpc, vpn, peering, etc.")
    state: Literal["active", "blackhole"] = Field(default="active")
    type: Optional[str] = Field(None, description="propagated or static")
    region: str = Field(default="")


class TGWRouteTableModel(AWSResource):
    """TGW Route Table."""

    routes: list[TGWRouteModel] = Field(default_factory=list)
    associations: list[str] = Field(
        default_factory=list, description="Associated attachment IDs"
    )
    propagations: list[str] = Field(
        default_factory=list, description="Propagating attachment IDs"
    )


class TGWAttachmentModel(AWSResource):
    """TGW Attachment."""

    type: str = Field(..., description="vpc, vpn, peering, connect, etc.")
    state: str = Field(default="available")
    resource_id: Optional[str] = Field(None, description="Attached resource ID")
    resource_owner: Optional[str] = Field(None, description="Resource owner account")


class TGWModel(AWSResource):
    """Transit Gateway model."""

    state: str = Field(default="available")
    asn: Optional[int] = Field(None, description="Amazon side ASN")
    attachments: list[TGWAttachmentModel] = Field(default_factory=list)
    route_tables: list[TGWRouteTableModel] = Field(default_factory=list)

    @field_validator("id")
    @classmethod
    def validate_tgw_id(cls, v: str) -> str:
        if not v.startswith("tgw-"):
            raise ValueError(f"TGW ID must start with 'tgw-': {v}")
        return v
