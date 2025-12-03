"""TDD tests for VPC-nested resources: IGW, NAT GW, VPC Endpoints (AWSNetShell)."""

import pytest
from aws_network_tools.shell import AWSNetShell, HIERARCHY

PROFILE = "taylaand+net-dev-Admin"


class TestVPCHierarchy:
    """Test VPC context has new resource types."""

    def test_internet_gateways_in_vpc_show(self):
        """show internet-gateways must be in VPC context."""
        assert "internet-gateways" in HIERARCHY["vpc"]["show"]

    def test_nat_gateways_in_vpc_show(self):
        """show nat-gateways must be in VPC context."""
        assert "nat-gateways" in HIERARCHY["vpc"]["show"]

    def test_endpoints_in_vpc_show(self):
        """show endpoints must be in VPC context."""
        assert "endpoints" in HIERARCHY["vpc"]["show"]


class TestVPCResourceHandlers:
    """Test VPC resource show handlers exist."""

    def test_show_internet_gateways_handler_exists(self):
        """_show_internet_gateways handler must exist."""
        shell = AWSNetShell()
        assert hasattr(shell, "_show_internet_gateways")

    def test_show_nat_gateways_handler_exists(self):
        """_show_nat_gateways handler must exist."""
        shell = AWSNetShell()
        assert hasattr(shell, "_show_nat_gateways")

    def test_show_endpoints_handler_exists(self):
        """_show_endpoints handler must exist."""
        shell = AWSNetShell()
        assert hasattr(shell, "_show_endpoints")


@pytest.mark.integration
class TestVPCResourcesIntegration:
    """Integration tests for VPC resources against live AWS."""

    @pytest.fixture
    def shell_in_vpc(self):
        """Create shell in VPC context."""
        s = AWSNetShell()
        s.profile = PROFILE
        s._show_vpcs(None)
        # Find a VPC with resources (named VPCs more likely)
        vpcs = s._cache.get("vpc", [])
        named = next(
            (v for v in vpcs if v.get("name") and "vpc-" in v.get("name", "")), vpcs[0]
        )
        idx = vpcs.index(named) + 1
        s._set_vpc(str(idx))
        return s

    def test_show_internet_gateways_no_error(self, shell_in_vpc):
        """show internet-gateways must not raise in VPC context."""
        shell_in_vpc._show_internet_gateways(None)
        assert shell_in_vpc.ctx_type == "vpc"

    def test_show_nat_gateways_no_error(self, shell_in_vpc):
        """show nat-gateways must not raise in VPC context."""
        shell_in_vpc._show_nat_gateways(None)
        assert shell_in_vpc.ctx_type == "vpc"

    def test_show_endpoints_no_error(self, shell_in_vpc):
        """show endpoints must not raise in VPC context."""
        shell_in_vpc._show_endpoints(None)
        assert shell_in_vpc.ctx_type == "vpc"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
