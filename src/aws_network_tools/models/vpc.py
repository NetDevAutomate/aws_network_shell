"""VPC-related Pydantic models."""

from typing import Optional, Literal
from pydantic import Field, field_validator, ConfigDict
from .base import AWSResource


class RouteModel(AWSResource):
    """Route entry in a route table."""

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(default="route", description="Route identifier")
    destination: str = Field(..., alias="prefix", description="Destination CIDR")
    target: str = Field(..., description="Route target (igw, nat, tgw, etc.)")
    state: Literal["active", "blackhole"] = Field(default="active")
    type: Optional[str] = Field(None, description="Route type")
    region: str = Field(default="")


class RouteTableModel(AWSResource):
    """VPC Route Table."""

    is_main: bool = Field(default=False, description="Is main route table")
    subnets: list[str] = Field(
        default_factory=list, description="Associated subnet IDs"
    )
    routes: list[RouteModel] = Field(default_factory=list)


class SubnetModel(AWSResource):
    """VPC Subnet."""

    cidr: str = Field(..., description="Subnet CIDR block")
    az: str = Field(..., description="Availability zone")
    public: bool = Field(default=False, description="Is public subnet")


class SecurityGroupModel(AWSResource):
    """Security Group."""

    description: Optional[str] = Field(None)
    vpc_id: str = Field(..., description="Parent VPC ID")
    ingress: list[dict] = Field(default_factory=list)
    egress: list[dict] = Field(default_factory=list)


class VPCModel(AWSResource):
    """VPC resource model."""

    cidr: Optional[str] = Field(None, description="Primary CIDR block")
    cidrs: list[str] = Field(default_factory=list, description="All CIDR blocks")
    state: str = Field(default="available")
    is_default: bool = Field(default=False)
    subnets: list[SubnetModel] = Field(default_factory=list)
    route_tables: list[RouteTableModel] = Field(default_factory=list)
    security_groups: list[SecurityGroupModel] = Field(default_factory=list)

    @field_validator("id")
    @classmethod
    def validate_vpc_id(cls, v: str) -> str:
        if not v.startswith("vpc-"):
            raise ValueError(f"VPC ID must start with 'vpc-': {v}")
        return v
