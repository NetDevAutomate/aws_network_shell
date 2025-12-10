"""Tests for refresh command functionality."""

import pytest
from aws_network_tools.shell.main import AWSNetShell
from io import StringIO
import sys


@pytest.fixture
def shell():
    """Create a shell instance for testing."""
    s = AWSNetShell()
    s.profile = "test-profile"
    return s


class TestRefreshCommand:
    """Test refresh command at all context levels."""

    def test_refresh_all_clears_entire_cache(self, shell):
        """Test 'refresh all' clears all cached data."""
        # Populate cache with test data
        shell._cache = {
            "elbs": [{"id": "elb-1"}],
            "vpcs": [{"id": "vpc-1"}],
            "transit_gateways": [{"id": "tgw-1"}],
        }

        # Capture output
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        shell.onecmd("refresh all")
        output = sys.stdout.getvalue()

        sys.stdout = old_stdout

        # Verify cache is cleared
        assert len(shell._cache) == 0
        assert "Cleared 3 cache entries" in output

    def test_refresh_specific_cache_key(self, shell):
        """Test refreshing specific cache key like 'elbs'."""
        # Populate cache
        shell._cache = {
            "elbs": [{"id": "elb-1"}],
            "vpcs": [{"id": "vpc-1"}],
        }

        old_stdout = sys.stdout
        sys.stdout = StringIO()

        shell.onecmd("refresh elbs")
        output = sys.stdout.getvalue()

        sys.stdout = old_stdout

        # Verify only elbs cache is cleared
        assert "elbs" not in shell._cache
        assert "vpcs" in shell._cache
        assert "Refreshed elbs cache" in output

    def test_refresh_with_alias(self, shell):
        """Test refresh works with aliases like 'elb' -> 'elbs'."""
        shell._cache = {"elbs": [{"id": "elb-1"}]}

        old_stdout = sys.stdout
        sys.stdout = StringIO()

        shell.onecmd("refresh elb")
        output = sys.stdout.getvalue()

        sys.stdout = old_stdout

        assert "elbs" not in shell._cache
        assert "Refreshed elbs cache" in output

    def test_refresh_nonexistent_key(self, shell):
        """Test refresh with non-existent cache key shows message."""
        shell._cache = {"vpcs": [{"id": "vpc-1"}]}

        old_stdout = sys.stdout
        sys.stdout = StringIO()

        shell.onecmd("refresh elbs")
        output = sys.stdout.getvalue()

        sys.stdout = old_stdout

        assert "vpcs" in shell._cache  # Unchanged
        assert "No cached data for elbs" in output

    def test_refresh_current_context_elb(self, shell):
        """Test 'refresh' without args in ELB context clears ELB cache."""
        # Set up ELB context
        shell._cache = {"elbs": [{"id": "elb-1"}]}
        from aws_network_tools.shell.base import Context
        shell.context_stack = [Context("elb", "arn:aws:...", "my-elb", {}, 1)]

        old_stdout = sys.stdout
        sys.stdout = StringIO()

        shell.onecmd("refresh")
        output = sys.stdout.getvalue()

        sys.stdout = old_stdout

        assert "elbs" not in shell._cache
        assert "Refreshed elbs cache" in output

    def test_refresh_current_context_vpc(self, shell):
        """Test refresh in VPC context clears VPC cache."""
        shell._cache = {"vpcs": [{"id": "vpc-1"}]}
        from aws_network_tools.shell.base import Context
        shell.context_stack = [Context("vpc", "vpc-123", "my-vpc", {}, 1)]

        old_stdout = sys.stdout
        sys.stdout = StringIO()

        shell.onecmd("refresh")
        output = sys.stdout.getvalue()

        sys.stdout = old_stdout

        assert "vpcs" not in shell._cache
        assert "Refreshed vpcs cache" in output

    def test_refresh_at_root_level(self, shell):
        """Test refresh at root level with no context shows appropriate message."""
        shell._cache = {}
        shell.context_stack = []

        old_stdout = sys.stdout
        sys.stdout = StringIO()

        shell.onecmd("refresh")
        output = sys.stdout.getvalue()

        sys.stdout = old_stdout

        assert "No cache to refresh in current context" in output

    def test_refresh_multiple_cache_keys(self, shell):
        """Test refreshing multiple cache keys in sequence."""
        shell._cache = {
            "elbs": [{"id": "elb-1"}],
            "vpcs": [{"id": "vpc-1"}],
            "transit_gateways": [{"id": "tgw-1"}],
        }

        old_stdout = sys.stdout
        sys.stdout = StringIO()

        shell.onecmd("refresh elbs")
        shell.onecmd("refresh vpcs")
        output = sys.stdout.getvalue()

        sys.stdout = old_stdout

        assert "elbs" not in shell._cache
        assert "vpcs" not in shell._cache
        assert "transit_gateways" in shell._cache  # Unchanged

    def test_refresh_transit_gateway_context(self, shell):
        """Test refresh in transit-gateway context."""
        shell._cache = {"transit_gateways": [{"id": "tgw-1"}]}
        from aws_network_tools.shell.base import Context
        shell.context_stack = [Context("transit-gateway", "tgw-123", "my-tgw", {}, 1)]

        old_stdout = sys.stdout
        sys.stdout = StringIO()

        shell.onecmd("refresh")
        output = sys.stdout.getvalue()

        sys.stdout = old_stdout

        assert "transit_gateways" not in shell._cache
        assert "Refreshed transit_gateways cache" in output

    def test_refresh_firewall_context(self, shell):
        """Test refresh in firewall context."""
        shell._cache = {"firewalls": [{"id": "fw-1"}]}
        from aws_network_tools.shell.base import Context
        shell.context_stack = [Context("firewall", "fw-123", "my-fw", {}, 1)]

        old_stdout = sys.stdout
        sys.stdout = StringIO()

        shell.onecmd("refresh")
        output = sys.stdout.getvalue()

        sys.stdout = old_stdout

        assert "firewalls" not in shell._cache
        assert "Refreshed firewalls cache" in output

    def test_refresh_with_empty_cache(self, shell):
        """Test refresh when cache is already empty."""
        shell._cache = {}

        old_stdout = sys.stdout
        sys.stdout = StringIO()

        shell.onecmd("refresh all")
        output = sys.stdout.getvalue()

        sys.stdout = old_stdout

        assert "Cleared 0 cache entries" in output

    def test_refresh_command_available_in_all_contexts(self, shell):
        """Test that refresh command is available in all contexts."""
        from aws_network_tools.shell.base import HIERARCHY

        # Check root level
        assert "refresh" in HIERARCHY[None]["commands"]

        # Check all context types
        context_types = [
            "global-network",
            "core-network",
            "route-table",
            "vpc",
            "transit-gateway",
            "firewall",
            "rule-group",
            "ec2-instance",
            "elb",
            "vpn",
        ]

        for ctx_type in context_types:
            assert "refresh" in HIERARCHY[ctx_type]["commands"], \
                f"refresh not in {ctx_type} commands"
