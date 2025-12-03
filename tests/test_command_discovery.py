"""Binary pass/fail tests for CommandDiscovery.

These tests validate that dynamic discovery produces the exact same
mappings as the previous hardcoded values, ensuring backward compatibility.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from aws_network_tools.shell.discovery import CommandDiscovery


# Legacy hardcoded values - MUST match exactly for backward compatibility
LEGACY_LIST_CMD = {
    "global-network": "show global-networks",
    "vpc": "show vpcs",
    "transit-gateway": "show transit_gateways",
    "firewall": "show firewalls",
    "ec2-instance": "show ec2-instances",
    "elb": "show elbs",
    "vpn": "show vpns",
    "core-network": "show core-networks",
    "route-table": "show route-tables",
}

LEGACY_SET_CMD = {
    "global-network": "set global-network",
    "vpc": "set vpc",
    "transit-gateway": "set tgw",
    "firewall": "set firewall",
    "ec2-instance": "set ec2-instance",
    "elb": "set elb",
    "vpn": "set vpn",
    "core-network": "set core-network",
    "route-table": "set route-table",
}


@pytest.fixture
def discovery():
    """Provide fresh CommandDiscovery instance."""
    return CommandDiscovery()


class TestListCommandDiscovery:
    """Binary tests for list command discovery."""

    def test_all_legacy_list_commands_match(self, discovery):
        """BINARY: All legacy list commands must match exactly."""
        for ctx_type, expected in LEGACY_LIST_CMD.items():
            result = discovery.get_list_command(ctx_type)
            assert result == expected, (
                f"List mismatch for {ctx_type}: got {result}, expected {expected}"
            )

    def test_global_network_list(self, discovery):
        """BINARY: global-network -> show global-networks"""
        assert discovery.get_list_command("global-network") == "show global-networks"

    def test_vpc_list(self, discovery):
        """BINARY: vpc -> show vpcs"""
        assert discovery.get_list_command("vpc") == "show vpcs"

    def test_transit_gateway_list(self, discovery):
        """BINARY: transit-gateway -> show transit_gateways (underscore!)"""
        assert discovery.get_list_command("transit-gateway") == "show transit_gateways"

    def test_firewall_list(self, discovery):
        """BINARY: firewall -> show firewalls"""
        assert discovery.get_list_command("firewall") == "show firewalls"

    def test_ec2_instance_list(self, discovery):
        """BINARY: ec2-instance -> show ec2-instances"""
        assert discovery.get_list_command("ec2-instance") == "show ec2-instances"

    def test_elb_list(self, discovery):
        """BINARY: elb -> show elbs"""
        assert discovery.get_list_command("elb") == "show elbs"

    def test_vpn_list(self, discovery):
        """BINARY: vpn -> show vpns"""
        assert discovery.get_list_command("vpn") == "show vpns"

    def test_core_network_list(self, discovery):
        """BINARY: core-network -> show core-networks"""
        assert discovery.get_list_command("core-network") == "show core-networks"

    def test_route_table_list(self, discovery):
        """BINARY: route-table -> show route-tables"""
        assert discovery.get_list_command("route-table") == "show route-tables"


class TestSetCommandDiscovery:
    """Binary tests for set command discovery."""

    def test_all_legacy_set_commands_match(self, discovery):
        """BINARY: All legacy set commands must match exactly."""
        for ctx_type, expected in LEGACY_SET_CMD.items():
            result = discovery.get_set_command(ctx_type)
            assert result == expected, (
                f"Set mismatch for {ctx_type}: got {result}, expected {expected}"
            )

    def test_transit_gateway_alias(self, discovery):
        """BINARY: transit-gateway must use 'tgw' alias."""
        assert discovery.get_set_command("transit-gateway") == "set tgw"

    def test_vpc_set(self, discovery):
        """BINARY: vpc -> set vpc"""
        assert discovery.get_set_command("vpc") == "set vpc"

    def test_global_network_set(self, discovery):
        """BINARY: global-network -> set global-network"""
        assert discovery.get_set_command("global-network") == "set global-network"


class TestReverseMapping:
    """Binary tests for reverse lookups."""

    def test_reverse_list_mapping(self, discovery):
        """BINARY: Reverse list mappings must work."""
        for ctx_type, list_cmd in LEGACY_LIST_CMD.items():
            result = discovery.get_context_from_list(list_cmd)
            assert result == ctx_type, f"Reverse list failed for {list_cmd}"

    def test_reverse_set_mapping(self, discovery):
        """BINARY: Reverse set mappings must work."""
        for ctx_type, set_cmd in LEGACY_SET_CMD.items():
            result = discovery.get_context_from_set(set_cmd)
            assert result == ctx_type, f"Reverse set failed for {set_cmd}"


class TestEdgeCases:
    """Binary tests for edge cases."""

    def test_none_context_list(self, discovery):
        """BINARY: None context returns None for list."""
        assert discovery.get_list_command(None) is None

    def test_none_context_set(self, discovery):
        """BINARY: None context returns None for set."""
        assert discovery.get_set_command(None) is None

    def test_unknown_context_list(self, discovery):
        """BINARY: Unknown context returns None for list."""
        assert discovery.get_list_command("nonexistent") is None

    def test_unknown_context_set(self, discovery):
        """BINARY: Unknown context returns None for set."""
        assert discovery.get_set_command("nonexistent") is None

    def test_sub_context_direct_match(self, discovery):
        """BINARY: get_sub_context returns context for direct match."""
        assert discovery.get_sub_context("core-network") == "core-network"
        assert discovery.get_sub_context("route-table") == "route-table"

    def test_sub_context_unknown(self, discovery):
        """BINARY: get_sub_context returns None for unknown."""
        assert discovery.get_sub_context("nonexistent") is None


class TestPropertyAccess:
    """Binary tests for property access."""

    def test_context_list_commands_property(self, discovery):
        """BINARY: context_list_commands contains all legacy mappings."""
        list_cmds = discovery.context_list_commands
        for ctx_type, expected in LEGACY_LIST_CMD.items():
            assert ctx_type in list_cmds
            assert list_cmds[ctx_type] == expected

    def test_context_set_commands_property(self, discovery):
        """BINARY: context_set_commands contains all legacy mappings."""
        set_cmds = discovery.context_set_commands
        for ctx_type, expected in LEGACY_SET_CMD.items():
            assert ctx_type in set_cmds
            assert set_cmds[ctx_type] == expected


class TestDeterminism:
    """Binary tests for deterministic behavior."""

    def test_multiple_instances_match(self):
        """BINARY: Multiple instances produce identical results."""
        d1 = CommandDiscovery()
        d2 = CommandDiscovery()
        assert d1.context_list_commands == d2.context_list_commands
        assert d1.context_set_commands == d2.context_set_commands


def run_binary_tests():
    """Run all tests and return binary pass/fail."""
    import subprocess

    result = subprocess.run(
        ["python", "-m", "pytest", __file__, "-v", "--tb=short"],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
    return result.returncode == 0


if __name__ == "__main__":
    success = run_binary_tests()
    sys.exit(0 if success else 1)
