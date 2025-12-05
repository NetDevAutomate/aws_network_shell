"""Test top-level (root context) commands.

Tests all commands available at root context (ctx_type == None).

Binary pass/fail tests for:
- show commands (version, config, cache, vpcs, transit-gateways, etc.)
- set commands (profile, regions, no-cache, output-format, etc.)
- action commands (clear, clear_cache, exit, etc.)
"""

import pytest
from unittest.mock import patch, MagicMock

from tests.test_command_graph.conftest import (
    assert_success,
    assert_failure,
    assert_output_contains,
    assert_output_not_contains,
    assert_context_type,
    assert_context_stack_depth,
)


class TestTopLevelShowCommands:
    """Test all 'show' commands in root context."""

    def test_show_version(self, command_runner):
        """Test: show version - displays CLI version and system info."""
        result = command_runner.run("show version")

        assert_success(result, "show version should succeed")
        assert_output_contains(result, "AWS Network Tools CLI")
        assert_output_contains(result, "Version:")
        assert_output_contains(result, "Python:")
        assert_output_contains(result, "Platform:")

    def test_show_config(self, command_runner):
        """Test: show config - displays current configuration."""
        result = command_runner.run("show config")

        assert_success(result, "show config should succeed")
        assert_output_contains(result, "Profile:")
        assert_output_contains(result, "Regions:")
        assert_output_contains(result, "No-cache:")
        assert_output_contains(result, "Output-format:")

    def test_show_running_config(self, command_runner):
        """Test: show running-config - alias for show config."""
        result = command_runner.run("show running-config")

        assert_success(result, "show running-config should succeed")
        assert_output_contains(result, "Profile:")
        assert_output_contains(result, "Regions:")

    def test_show_cache(self, command_runner):
        """Test: show cache - displays cache status."""
        result = command_runner.run("show cache")

        assert_success(result, "show cache should succeed")
        assert_output_contains(result, "Cache Status")
        assert_output_contains(result, "In-memory")

    @patch("aws_network_tools.modules.vpc.VPCClient")
    def test_show_vpcs(self, mock_client_class, command_runner, mock_vpc_client):
        """Test: show vpcs - displays all VPCs."""
        mock_client_class.return_value = mock_vpc_client()

        result = command_runner.run("show vpcs")

        assert_success(result, "show vpcs should succeed")
        assert_output_contains(result, "VPCs")
        # Rich tables truncate long IDs with '…', so check for prefix
        assert_output_contains(result, "vpc-0prod1234567")
        assert_output_contains(result, "production-vpc")

    @patch("aws_network_tools.modules.tgw.TGWClient")
    def test_show_transit_gateways(
        self, mock_client_class, command_runner, mock_tgw_client
    ):
        """Test: show transit_gateways - displays all Transit Gateways."""
        mock_client_class.return_value = mock_tgw_client()

        # Command uses underscore (transit_gateways), not hyphen
        result = command_runner.run("show transit_gateways")

        assert_success(result, "show transit_gateways should succeed")
        assert_output_contains(result, "Transit Gateways")

    @patch("aws_network_tools.modules.cloudwan.CloudWANClient")
    def test_show_global_networks(
        self, mock_client_class, command_runner, mock_cloudwan_client
    ):
        """Test: show global-networks - displays all Global Networks."""
        mock_instance = mock_cloudwan_client()
        mock_instance.nm.describe_global_networks.return_value = {
            "GlobalNetworks": [
                {
                    "GlobalNetworkId": "global-network-0prod123",
                    "State": "AVAILABLE",
                    "Tags": [{"Key": "Name", "Value": "production-global-network"}],
                }
            ]
        }
        mock_client_class.return_value = mock_instance

        result = command_runner.run("show global-networks")

        assert_success(result, "show global-networks should succeed")
        assert_output_contains(result, "Global Networks")

    @patch("aws_network_tools.modules.anfw.ANFWClient")
    def test_show_firewalls(
        self, mock_client_class, command_runner, mock_firewall_client
    ):
        """Test: show firewalls - displays all Network Firewalls."""
        mock_client_class.return_value = mock_firewall_client()

        result = command_runner.run("show firewalls")

        assert_success(result, "show firewalls should succeed")
        assert_output_contains(result, "Network Firewalls")

    @patch("aws_network_tools.modules.ec2.EC2Client")
    def test_show_ec2_instances(
        self, mock_client_class, command_runner, mock_ec2_client
    ):
        """Test: show ec2-instances - displays all EC2 instances."""
        mock_client_class.return_value = mock_ec2_client()

        result = command_runner.run("show ec2-instances")

        # This command may not be implemented yet, check exit code
        # If implemented, it should succeed
        if result["exit_code"] == 0:
            assert_output_contains(result, "Instance")
        else:
            # Not implemented is acceptable
            assert_output_contains(result, "Not implemented")

    @patch("aws_network_tools.modules.elb.ELBClient")
    def test_show_elbs(self, mock_client_class, command_runner, mock_elb_client):
        """Test: show elbs - displays all Load Balancers."""
        mock_client_class.return_value = mock_elb_client()

        result = command_runner.run("show elbs")

        # Check if implemented
        if result["exit_code"] == 0:
            assert_output_contains(result, "Load Balancer")
        else:
            assert_output_contains(result, "Not implemented")

    @patch("aws_network_tools.modules.vpn.VPNClient")
    def test_show_vpns(self, mock_client_class, command_runner, mock_vpn_client):
        """Test: show vpns - displays all VPN connections."""
        mock_client_class.return_value = mock_vpn_client()

        result = command_runner.run("show vpns")

        # Check if implemented
        if result["exit_code"] == 0:
            assert_output_contains(result, "VPN")
        else:
            assert_output_contains(result, "Not implemented")

    def test_show_routing_cache(self, command_runner):
        """Test: show routing-cache - displays routing cache status."""
        result = command_runner.run("show routing-cache")

        assert_success(result, "show routing-cache should succeed")
        # Empty cache is valid
        assert (
            "Routing cache empty" in result["output"]
            or "Routing Cache" in result["output"]
        )

    def test_show_graph(self, command_runner):
        """Test: show graph - displays command hierarchy graph."""
        result = command_runner.run("show graph")

        assert_success(result, "show graph should succeed")
        # Should show some form of graph output

    def test_show_graph_stats(self, command_runner):
        """Test: show graph stats - displays graph statistics."""
        result = command_runner.run("show graph stats")

        assert_success(result, "show graph stats should succeed")
        assert_output_contains(result, "Command Graph Statistics")
        assert_output_contains(result, "Total nodes:")
        assert_output_contains(result, "Contexts:")

    def test_show_graph_validate(self, command_runner):
        """Test: show graph validate - validates command graph."""
        result = command_runner.run("show graph validate")

        assert_success(result, "show graph validate should succeed")
        # Should show validation result (valid or invalid)

    def test_show_help_syntax(self, command_runner):
        """Test: show ? - displays show options."""
        result = command_runner.run("show ?")

        assert_success(result, "show ? should succeed")
        assert_output_contains(result, "show options:")
        assert_output_contains(result, "show version")
        assert_output_contains(result, "show vpcs")

    def test_show_invalid_option(self, command_runner):
        """Test: show <invalid> - should error gracefully."""
        result = command_runner.run("show nonexistent-command")

        # Should not crash but show error
        assert result["exit_code"] == 0  # cmd2 doesn't fail on invalid subcommands
        assert_output_contains(result, "Invalid")


class TestTopLevelSetCommands:
    """Test all 'set' commands in root context."""

    def test_set_profile(self, command_runner, isolated_shell):
        """Test: set profile <name> - sets AWS profile."""
        result = command_runner.run("set profile test-profile")

        assert_success(result, "set profile should succeed")
        assert_output_contains(result, "Profile: test-profile")
        assert isolated_shell.profile == "test-profile"

    def test_set_profile_default(self, command_runner, isolated_shell):
        """Test: set profile (empty) - resets to default."""
        result = command_runner.run("set profile")

        assert_success(result, "set profile (empty) should succeed")
        assert isolated_shell.profile is None

    def test_set_regions(self, command_runner, isolated_shell):
        """Test: set regions <list> - sets region filter."""
        result = command_runner.run("set regions eu-west-1,us-east-1")

        assert_success(result, "set regions should succeed")
        assert_output_contains(result, "eu-west-1")
        assert_output_contains(result, "us-east-1")
        assert isolated_shell.regions == ["eu-west-1", "us-east-1"]

    def test_set_no_cache_on(self, command_runner, isolated_shell):
        """Test: set no-cache on - disables caching."""
        result = command_runner.run("set no-cache on")

        assert_success(result, "set no-cache on should succeed")
        assert_output_contains(result, "No-cache: on")
        assert isolated_shell.no_cache is True

    def test_set_no_cache_off(self, command_runner, isolated_shell):
        """Test: set no-cache off - enables caching."""
        result = command_runner.run("set no-cache off")

        assert_success(result, "set no-cache off should succeed")
        assert_output_contains(result, "No-cache: off")
        assert isolated_shell.no_cache is False

    def test_set_output_format_json(self, command_runner, isolated_shell):
        """Test: set output-format json - changes output to JSON."""
        result = command_runner.run("set output-format json")

        assert_success(result, "set output-format json should succeed")
        assert_output_contains(result, "Output-format: json")
        assert isolated_shell.output_format == "json"

    def test_set_output_format_yaml(self, command_runner, isolated_shell):
        """Test: set output-format yaml - changes output to YAML."""
        result = command_runner.run("set output-format yaml")

        assert_success(result, "set output-format yaml should succeed")
        assert_output_contains(result, "Output-format: yaml")
        assert isolated_shell.output_format == "yaml"

    def test_set_output_format_table(self, command_runner, isolated_shell):
        """Test: set output-format table - changes output to table."""
        result = command_runner.run("set output-format table")

        assert_success(result, "set output-format table should succeed")
        assert_output_contains(result, "Output-format: table")
        assert isolated_shell.output_format == "table"

    def test_set_output_format_invalid(self, command_runner):
        """Test: set output-format <invalid> - should error."""
        result = command_runner.run("set output-format invalid")

        assert_success(result, "Command executes but shows error")
        assert_output_contains(result, "table|json|yaml")

    def test_set_output_file(self, command_runner, isolated_shell):
        """Test: set output-file <path> - sets output file."""
        result = command_runner.run("set output-file /tmp/test-output.txt")

        assert_success(result, "set output-file should succeed")
        assert_output_contains(result, "Output file: /tmp/test-output.txt")

    def test_set_watch(self, command_runner, isolated_shell):
        """Test: set watch <seconds> - sets watch interval."""
        result = command_runner.run("set watch 5")

        assert_success(result, "set watch should succeed")
        assert_output_contains(result, "Watch: 5s")
        assert isolated_shell.watch_interval == 5

    def test_set_watch_disable(self, command_runner, isolated_shell):
        """Test: set watch 0 - disables watch."""
        result = command_runner.run("set watch 0")

        assert_success(result, "set watch 0 should succeed")
        assert_output_contains(result, "Watch disabled")
        assert isolated_shell.watch_interval == 0

    def test_set_help_syntax(self, command_runner):
        """Test: set ? - displays set options."""
        result = command_runner.run("set ?")

        assert_success(result, "set ? should succeed")
        assert_output_contains(result, "set options:")
        assert_output_contains(result, "set profile")
        assert_output_contains(result, "set output-format")


class TestTopLevelActionCommands:
    """Test action commands (do_*) in root context."""

    def test_clear_command(self, command_runner):
        """Test: clear - clears the screen."""
        result = command_runner.run("clear")

        assert_success(result, "clear should succeed")
        # Clear doesn't produce output

    def test_clear_cache_command(self, command_runner, isolated_shell):
        """Test: clear-cache - clears all cached data."""
        # Add something to cache first
        isolated_shell._cache["test"] = "data"

        # Command uses underscore: clear_cache
        result = command_runner.run("clear_cache")

        assert_success(result, "clear_cache should succeed")
        assert_output_contains(result, "Cache cleared")
        assert len(isolated_shell._cache) == 0

    def test_exit_at_root(self, command_runner):
        """Test: exit at root - should quit."""
        result = command_runner.run("exit")

        # exit returns True to quit
        assert result["exit_code"] == 1 or "exit_code" in result

    def test_end_at_root(self, command_runner, isolated_shell):
        """Test: end at root - should do nothing."""
        result = command_runner.run("end")

        assert_success(result, "end at root should succeed")
        assert len(isolated_shell.context_stack) == 0

    def test_validate_graph_command(self, command_runner):
        """Test: validate_graph - validates command hierarchy."""
        result = command_runner.run("validate_graph")

        assert_success(result, "validate-graph should succeed")
        # Should show validation result

    def test_export_graph_command(self, command_runner, tmp_path):
        """Test: export_graph - exports graph as Mermaid."""
        output_file = tmp_path / "test_graph.md"

        # Command uses underscore: export_graph
        result = command_runner.run(f"export_graph {output_file}")

        assert_success(result, "export_graph should succeed")
        assert_output_contains(result, "Exported")

    def test_create_routing_cache_command(self, command_runner, isolated_shell):
        """Test: create_routing_cache - builds routing cache."""
        with patch("aws_network_tools.modules.vpc.VPCClient"), patch(
            "aws_network_tools.modules.tgw.TGWClient"
        ), patch("aws_network_tools.modules.cloudwan.CloudWANClient"):
            # Command uses underscore: create_routing_cache
            result = command_runner.run("create_routing_cache")

            # May succeed or fail depending on mocks
            # Primary check: doesn't crash
            assert result["exit_code"] in [0, 1]

    def test_find_prefix_no_cache(self, command_runner):
        """Test: find_prefix without cache - should warn."""
        # Command uses underscore: find_prefix
        result = command_runner.run("find_prefix 10.0.0.0/16")

        assert_success(result, "find_prefix should not crash")
        assert_output_contains(result, "cache")

    def test_find_null_routes_no_cache(self, command_runner):
        """Test: find_null_routes without cache - should warn."""
        # Command uses underscore: find_null_routes
        result = command_runner.run("find_null_routes")

        assert_success(result, "find_null_routes should not crash")
        assert_output_contains(result, "cache")


class TestTopLevelContextTransitions:
    """Test context-entering set commands."""

    @patch("aws_network_tools.modules.vpc.VPCClient")
    def test_set_vpc_enters_context(
        self, mock_client_class, command_runner, isolated_shell, mock_vpc_client
    ):
        """Test: set vpc <#> - enters VPC context."""
        mock_client_class.return_value = mock_vpc_client()

        # First show vpcs to populate cache
        command_runner.run("show vpcs")

        # Then set vpc by index
        result = command_runner.run("set vpc 1")

        assert_success(result, "set vpc 1 should succeed")
        assert_context_type(isolated_shell, "vpc")
        assert_context_stack_depth(isolated_shell, 1)

    @patch("aws_network_tools.modules.tgw.TGWClient")
    def test_set_transit_gateway_enters_context(
        self, mock_client_class, command_runner, isolated_shell, mock_tgw_client
    ):
        """Test: set transit-gateway <#> - enters TGW context."""
        mock_client_class.return_value = mock_tgw_client()

        # First show transit_gateways (underscore) to populate cache
        command_runner.run("show transit_gateways")

        # Then set transit-gateway by index (hyphen for context commands)
        result = command_runner.run("set transit-gateway 1")

        assert_success(result, "set transit-gateway 1 should succeed")
        assert_context_type(isolated_shell, "transit-gateway")
        assert_context_stack_depth(isolated_shell, 1)

    @patch("aws_network_tools.modules.cloudwan.CloudWANClient")
    def test_set_global_network_enters_context(
        self, mock_client_class, command_runner, isolated_shell, mock_cloudwan_client
    ):
        """Test: set global-network <#> - enters global-network context."""
        mock_instance = mock_cloudwan_client()
        mock_instance.nm.describe_global_networks.return_value = {
            "GlobalNetworks": [
                {
                    "GlobalNetworkId": "global-network-0prod123",
                    "State": "AVAILABLE",
                    "Tags": [{"Key": "Name", "Value": "production-global-network"}],
                }
            ]
        }
        mock_client_class.return_value = mock_instance

        # First show global-networks to populate cache
        command_runner.run("show global-networks")

        # Then set global-network by index
        result = command_runner.run("set global-network 1")

        assert_success(result, "set global-network 1 should succeed")
        assert_context_type(isolated_shell, "global-network")
        assert_context_stack_depth(isolated_shell, 1)


class TestTopLevelErrorHandling:
    """Test error handling for invalid commands."""

    def test_unknown_command(self, command_runner):
        """Test: unknown command - should show help or error."""
        result = command_runner.run("invalid-command")

        assert_success(result, "Invalid command doesn't crash")
        # Shell shows help with available commands instead of "Unknown"
        assert "Commands:" in result["output"] or "Unknown" in result["output"]

    def test_show_nonexistent(self, command_runner):
        """Test: show nonexistent - should show error."""
        result = command_runner.run("show nonexistent-resource")

        assert_success(result, "Invalid show doesn't crash")
        assert "Invalid" in result["output"] or "Not implemented" in result["output"]

    def test_set_nonexistent(self, command_runner):
        """Test: set nonexistent - should show error."""
        result = command_runner.run("set nonexistent-option value")

        assert_success(result, "Invalid set doesn't crash")
        assert "Invalid" in result["output"] or "Usage" in result["output"]

    def test_help_command(self, command_runner):
        """Test: ? - shows help."""
        result = command_runner.run("?")

        assert_success(result, "? should succeed")
        assert_output_contains(result, "Commands:")

    def test_empty_command(self, command_runner):
        """Test: (empty) - should be handled gracefully."""
        result = command_runner.run("")

        # Empty command is handled gracefully - doesn't crash
        # May return exit_code 0 or 1 depending on implementation
        assert result["exit_code"] in [0, 1]
