"""TDD tests for Pydantic models - Binary pass/fail."""

import pytest
from pydantic import ValidationError

from aws_network_tools.models import (
    CIDRBlock,
    VPCModel,
    SubnetModel,
    TGWModel,
    TGWRouteModel,
    CoreNetworkModel,
    EC2InstanceModel,
    ENIModel,
)


class TestCIDRBlock:
    """Binary tests for CIDR validation."""

    def test_valid_cidr(self):
        """BINARY: Valid CIDR must pass."""
        cidr = CIDRBlock(cidr="10.0.0.0/16")
        assert cidr.cidr == "10.0.0.0/16"

    def test_invalid_cidr_format(self):
        """BINARY: Invalid CIDR must raise ValidationError."""
        with pytest.raises(ValidationError):
            CIDRBlock(cidr="invalid")

    def test_invalid_cidr_no_mask(self):
        """BINARY: CIDR without mask must fail."""
        with pytest.raises(ValidationError):
            CIDRBlock(cidr="10.0.0.0")


class TestVPCModel:
    """Binary tests for VPC model."""

    def test_valid_vpc(self):
        """BINARY: Valid VPC must pass."""
        vpc = VPCModel(id="vpc-12345678", region="us-east-1", cidr="10.0.0.0/16")
        assert vpc.id == "vpc-12345678"
        assert vpc.region == "us-east-1"

    def test_invalid_vpc_id_prefix(self):
        """BINARY: VPC ID without 'vpc-' prefix must fail."""
        with pytest.raises(ValidationError):
            VPCModel(id="invalid-123", region="us-east-1")

    def test_vpc_with_subnets(self):
        """BINARY: VPC with nested subnets must work."""
        vpc = VPCModel(
            id="vpc-12345678",
            region="us-east-1",
            subnets=[
                SubnetModel(
                    id="subnet-123",
                    name="public",
                    region="us-east-1",
                    cidr="10.0.1.0/24",
                    az="us-east-1a",
                )
            ],
        )
        assert len(vpc.subnets) == 1
        assert vpc.subnets[0].cidr == "10.0.1.0/24"

    def test_vpc_to_dict(self):
        """BINARY: to_dict must return valid dict."""
        vpc = VPCModel(id="vpc-12345678", region="us-east-1", name="test")
        d = vpc.to_dict()
        assert isinstance(d, dict)
        assert d["id"] == "vpc-12345678"


class TestTGWModel:
    """Binary tests for Transit Gateway model."""

    def test_valid_tgw(self):
        """BINARY: Valid TGW must pass."""
        tgw = TGWModel(id="tgw-12345678", region="us-east-1", name="my-tgw")
        assert tgw.id == "tgw-12345678"

    def test_invalid_tgw_id(self):
        """BINARY: TGW ID without 'tgw-' prefix must fail."""
        with pytest.raises(ValidationError):
            TGWModel(id="invalid-123", region="us-east-1")

    def test_tgw_with_routes(self):
        """BINARY: TGW route model must work."""
        route = TGWRouteModel(
            prefix="10.0.0.0/8",
            target="tgw-attach-123",
            state="active",
            region="us-east-1",
        )
        assert route.prefix == "10.0.0.0/8"
        assert route.state == "active"


class TestCoreNetworkModel:
    """Binary tests for Cloud WAN Core Network model."""

    def test_valid_core_network(self):
        """BINARY: Valid Core Network must pass."""
        cn = CoreNetworkModel(
            id="core-network-123456",
            region="us-west-2",
            global_network_id="global-network-123",
        )
        assert cn.id == "core-network-123456"

    def test_invalid_core_network_id(self):
        """BINARY: Core Network ID without prefix must fail."""
        with pytest.raises(ValidationError):
            CoreNetworkModel(
                id="invalid", region="us-west-2", global_network_id="gn-123"
            )


class TestEC2Model:
    """Binary tests for EC2 Instance model."""

    def test_valid_instance(self):
        """BINARY: Valid EC2 instance must pass."""
        inst = EC2InstanceModel(
            id="i-12345678",
            region="us-east-1",
            instance_type="t3.micro",
            az="us-east-1a",
        )
        assert inst.id == "i-12345678"
        assert inst.type == "t3.micro"

    def test_invalid_instance_id(self):
        """BINARY: Instance ID without 'i-' prefix must fail."""
        with pytest.raises(ValidationError):
            EC2InstanceModel(
                id="invalid",
                region="us-east-1",
                instance_type="t3.micro",
                az="us-east-1a",
            )


class TestENIModel:
    """Binary tests for ENI model."""

    def test_valid_eni(self):
        """BINARY: Valid ENI must pass."""
        eni = ENIModel(
            id="eni-12345678",
            region="us-east-1",
            vpc_id="vpc-123",
            subnet_id="subnet-123",
            private_ip="10.0.1.5",
        )
        assert eni.id == "eni-12345678"
        assert eni.private_ip == "10.0.1.5"

    def test_invalid_eni_id(self):
        """BINARY: ENI ID without 'eni-' prefix must fail."""
        with pytest.raises(ValidationError):
            ENIModel(
                id="invalid",
                region="us-east-1",
                vpc_id="vpc-123",
                subnet_id="subnet-123",
                private_ip="10.0.1.5",
            )


class TestModelBackwardCompatibility:
    """Ensure models work with existing dict-based code."""

    def test_extra_fields_allowed(self):
        """BINARY: Extra fields must be allowed for flexibility."""
        vpc = VPCModel(id="vpc-123", region="us-east-1", custom_field="value")
        assert vpc.model_dump().get("custom_field") == "value"

    def test_optional_fields_default_none(self):
        """BINARY: Optional fields must default correctly."""
        vpc = VPCModel(id="vpc-123", region="us-east-1")
        assert vpc.name is None
        assert vpc.cidrs == []
