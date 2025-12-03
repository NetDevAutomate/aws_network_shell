"""EC2 and ENI Pydantic models."""

from typing import Optional
from pydantic import Field, field_validator, ConfigDict
from .base import AWSResource


class ENIModel(AWSResource):
    """Elastic Network Interface model."""

    vpc_id: str = Field(..., description="VPC ID")
    subnet_id: str = Field(..., description="Subnet ID")
    private_ip: str = Field(..., description="Primary private IP")
    public_ip: Optional[str] = Field(None, description="Public IP if assigned")
    mac_address: Optional[str] = Field(None)
    interface_type: str = Field(default="interface")
    attachment_id: Optional[str] = Field(None)
    instance_id: Optional[str] = Field(None, description="Attached EC2 instance")

    @field_validator("id")
    @classmethod
    def validate_eni_id(cls, v: str) -> str:
        if not v.startswith("eni-"):
            raise ValueError(f"ENI ID must start with 'eni-': {v}")
        return v


class EC2InstanceModel(AWSResource):
    """EC2 Instance model."""

    model_config = ConfigDict(populate_by_name=True)

    type: str = Field(..., alias="instance_type", description="Instance type")
    state: str = Field(default="running")
    az: str = Field(..., description="Availability zone")
    vpc_id: Optional[str] = Field(None)
    subnet_id: Optional[str] = Field(None)
    private_ip: Optional[str] = Field(None)
    public_ip: Optional[str] = Field(None)
    enis: list[ENIModel] = Field(default_factory=list)
    security_groups: list[dict] = Field(default_factory=list)

    @field_validator("id")
    @classmethod
    def validate_instance_id(cls, v: str) -> str:
        if not v.startswith("i-"):
            raise ValueError(f"Instance ID must start with 'i-': {v}")
        return v
