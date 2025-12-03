"""Base Pydantic models for AWS resources."""

from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
import re


class CIDRBlock(BaseModel):
    """Validated CIDR block."""

    cidr: str = Field(..., description="CIDR notation (e.g., 10.0.0.0/16)")

    @field_validator("cidr")
    @classmethod
    def validate_cidr(cls, v: str) -> str:
        pattern = r"^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$"
        if not re.match(pattern, v):
            raise ValueError(f"Invalid CIDR format: {v}")
        return v


class AWSResource(BaseModel):
    """Base model for all AWS resources."""

    model_config = ConfigDict(extra="allow")

    id: str = Field(..., description="AWS resource ID")
    name: Optional[str] = Field(None, description="Resource name from tags")
    region: str = Field(..., description="AWS region")

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        if not v or len(v) < 3:
            raise ValueError(f"Invalid resource ID: {v}")
        return v

    def to_dict(self) -> dict:
        """Convert to dict for backward compatibility."""
        return self.model_dump(exclude_none=True)
