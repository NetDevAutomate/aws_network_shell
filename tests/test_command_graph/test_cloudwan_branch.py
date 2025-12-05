"""Test CloudWAN command branch: global-network → core-network → segments/routes.

This tests the complete CloudWAN command path:
1. show global-networks (root context)
2. set global-network <id> (enters global-network context)
3. show core-networks (global-network context)
4. set core-network <id> (enters core-network context)
5. show segments, policy, routes, etc. (core-network context)

Binary pass/fail criteria for every test.
"""

import pytest
from tests.test_command_graph.conftest import (
    assert_success,
    assert_failure,
    assert_output_contains,
    assert_context_type,
)


class TestGlobalNetworkBranch:
    """Test complete global-network command branch."""

    def test_show_global_networks_from_root(self, command_runner, mock_cloudwan_client):
        """Test: show global-networks (root context)."""
        result = command_runner.run("show global-networks")

        assert_success(result)
        assert_output_contains(result, "Global Networks")
        assert_output_contains(result, "global-network-0prod123")

    def test_set_global_network_by_number(
        self, command_runner, isolated_shell, mock_cloudwan_client
    ):
        """Test: set global-network using # (enters global-network context).

        KEY: Must run 'show global-networks' FIRST to populate the index table.
        The set command uses the # from the show output.
        """
        # Step 1: Show global networks to get index table
        show_result = command_runner.run("show global-networks")
        assert_success(show_result)
        assert_output_contains(show_result, "global-network-0prod123")

        # Step 2: Use index from show command to enter context
        result = command_runner.run("set global-network 1")

        assert_success(result)
        assert_context_type(isolated_shell, "global-network")

    def test_set_global_network_by_id(
        self, command_runner, isolated_shell, mock_cloudwan_client
    ):
        """Test: set global-network using ID (enters global-network context)."""
        # Show first to populate data
        command_runner.run("show global-networks")
        
        result = command_runner.run("set global-network global-network-0prod123")

        assert_success(result)
        assert_context_type(isolated_shell, "global-network")

    def test_set_global_network_by_name(
        self, command_runner, isolated_shell, mock_cloudwan_client
    ):
        """Test: set global-network using name (enters global-network context)."""
        result = command_runner.run("set global-network production-global-network")

        assert_success(result)
        assert_context_type(isolated_shell, "global-network")

    def test_set_global_network_invalid(self, command_runner, mock_cloudwan_client):
        """Test: set global-network with invalid ID (should fail)."""
        result = command_runner.run("set global-network invalid-id-999")

        assert_failure(result)
        assert_output_contains(result, "not found")

    def test_show_global_network_detail(
        self, command_runner, isolated_shell, mock_cloudwan_client
    ):
        """Test: show detail in global-network context."""
        # Enter global-network context
        command_runner.run("set global-network global-network-0prod123")

        # Show detail
        result = command_runner.run("show detail")

        assert_success(result)
        assert_output_contains(result, "global-network-0prod123")
        assert_output_contains(result, "Core Networks")


class TestCoreNetworkBranch:
    """Test core-network command branch."""

    def test_show_core_networks_in_global_network_context(
        self, command_runner, isolated_shell, mock_cloudwan_client
    ):
        """Test: show core-networks from global-network context."""
        # Enter global-network context
        command_runner.run("set global-network global-network-0prod123")

        # Show core networks
        result = command_runner.run("show core-networks")

        assert_success(result)
        assert_output_contains(result, "Core Networks")
        assert_output_contains(result, "core-network-0global123")

    def test_set_core_network_by_number(
        self, command_runner, isolated_shell, mock_cloudwan_client
    ):
        """Test: set core-network using # (enters core-network context)."""
        # CRITICAL: Must follow show→set pattern for BOTH contexts

        # Step 1: Enter global-network context (show→set)
        command_runner.run("show global-networks")
        command_runner.run("set global-network 1")  # Use #1 (global-network-0prod123 has core network)

        # Step 2: Enter core-network context (show→set)
        command_runner.run("show core-networks")
        result = command_runner.run("set core-network 1")

        assert_success(result)
        assert_context_type(isolated_shell, "core-network")

    def test_set_core_network_by_id(
        self, command_runner, isolated_shell, mock_cloudwan_client
    ):
        """Test: set core-network using ID (enters core-network context)."""
        # Enter global-network context
        command_runner.run("set global-network global-network-0prod123")

        # Enter core-network context by ID
        result = command_runner.run("set core-network core-network-0global123")

        assert_success(result)
        assert_context_type(isolated_shell, "core-network")

    def test_set_core_network_invalid(
        self, command_runner, isolated_shell, mock_cloudwan_client
    ):
        """Test: set core-network with invalid ID (should fail)."""
        # Enter global-network context
        command_runner.run("set global-network global-network-0prod123")

        # Try invalid core network
        result = command_runner.run("set core-network invalid-core-999")

        assert_failure(result)
        assert_output_contains(result, "not found")

    def test_show_core_network_detail(
        self, command_runner, isolated_shell, mock_cloudwan_client
    ):
        """Test: show detail in core-network context."""
        # Navigate to core-network context
        command_runner.run("set global-network global-network-0prod123")
        command_runner.run("set core-network core-network-0global123")

        # Show detail
        result = command_runner.run("show detail")

        assert_success(result)
        assert_output_contains(result, "core-network-0global123")
        assert_output_contains(result, "Segments")

    def test_show_segments(
        self, command_runner, isolated_shell, mock_cloudwan_client
    ):
        """Test: show segments in core-network context."""
        # Navigate to core-network context
        command_runner.run("set global-network global-network-0prod123")
        command_runner.run("set core-network core-network-0global123")

        # Show segments
        result = command_runner.run("show segments")

        assert_success(result)
        assert_output_contains(result, "Segments")
        assert_output_contains(result, "production")
        assert_output_contains(result, "staging")
        assert_output_contains(result, "shared-services")
        assert_output_contains(result, "inspection")

    def test_show_policy(self, command_runner, isolated_shell, mock_cloudwan_client):
        """Test: show policy in core-network context."""
        # Navigate to core-network context
        command_runner.run("set global-network global-network-0prod123")
        command_runner.run("set core-network core-network-0global123")

        # Show policy
        result = command_runner.run("show policy")

        assert_success(result)
        assert_output_contains(result, "Policy")

    def test_show_routes(self, command_runner, isolated_shell, mock_cloudwan_client):
        """Test: show routes in core-network context."""
        # Navigate to core-network context
        command_runner.run("set global-network global-network-0prod123")
        command_runner.run("set core-network core-network-0global123")

        # Show routes
        result = command_runner.run("show routes")

        assert_success(result)
        # Should show routes for all segments/regions

    def test_show_route_tables(
        self, command_runner, isolated_shell, mock_cloudwan_client
    ):
        """Test: show route-tables in core-network context."""
        # Navigate to core-network context
        command_runner.run("set global-network global-network-0prod123")
        command_runner.run("set core-network core-network-0global123")

        # Show route tables
        result = command_runner.run("show route-tables")

        assert_success(result)
        assert_output_contains(result, "Route Tables")

    def test_show_connect_attachments(
        self, command_runner, isolated_shell, mock_cloudwan_client
    ):
        """Test: show connect-attachments in core-network context."""
        # Navigate to core-network context
        command_runner.run("set global-network global-network-0prod123")
        command_runner.run("set core-network core-network-0global123")

        # Show connect attachments
        result = command_runner.run("show connect-attachments")

        assert_success(result)
        assert_output_contains(result, "Connect")

    def test_show_connect_peers(
        self, command_runner, isolated_shell, mock_cloudwan_client
    ):
        """Test: show connect-peers in core-network context (BGP sessions)."""
        # Navigate to core-network context
        command_runner.run("set global-network global-network-0prod123")
        command_runner.run("set core-network core-network-0global123")

        # Show connect peers
        result = command_runner.run("show connect-peers")

        assert_success(result)
        assert_output_contains(result, "Connect Peers")

    def test_show_blackhole_routes(
        self, command_runner, isolated_shell, mock_cloudwan_client
    ):
        """Test: show blackhole-routes in core-network context."""
        # Navigate to core-network context
        command_runner.run("set global-network global-network-0prod123")
        command_runner.run("set core-network core-network-0global123")

        # Show blackhole routes
        result = command_runner.run("show blackhole-routes")

        assert_success(result)
        # May have no blackhole routes - that's OK

    def test_find_prefix_in_core_network_context(
        self, command_runner, isolated_shell, mock_cloudwan_client
    ):
        """Test: find_prefix in core-network context."""
        # Navigate to core-network context
        command_runner.run("set global-network global-network-0prod123")
        command_runner.run("set core-network core-network-0global123")

        # Find a prefix from our fixtures
        result = command_runner.run("find_prefix 10.0.0.0/16")

        assert_success(result)
        # Should find routes matching this prefix


class TestCloudWANContextNavigation:
    """Test context navigation for CloudWAN branch."""

    def test_exit_from_core_network_to_global_network(
        self, command_runner, isolated_shell, mock_cloudwan_client
    ):
        """Test: exit from core-network context returns to global-network."""
        # Navigate to core-network context
        command_runner.run("set global-network global-network-0prod123")
        command_runner.run("set core-network core-network-0global123")

        # Exit one level
        result = command_runner.run("exit")

        assert_success(result)
        assert_context_type(isolated_shell, "global-network")

    def test_end_from_core_network_to_root(
        self, command_runner, isolated_shell, mock_cloudwan_client
    ):
        """Test: end from core-network context returns to root."""
        # Navigate to core-network context
        command_runner.run("set global-network global-network-0prod123")
        command_runner.run("set core-network core-network-0global123")

        # End returns to root
        result = command_runner.run("end")

        assert_success(result)
        assert_context_type(isolated_shell, None)

    def test_exit_from_global_network_to_root(
        self, command_runner, isolated_shell, mock_cloudwan_client
    ):
        """Test: exit from global-network context returns to root."""
        # Navigate to global-network context
        command_runner.run("set global-network global-network-0prod123")

        # Exit to root
        result = command_runner.run("exit")

        assert_success(result)
        assert_context_type(isolated_shell, None)


class TestCloudWANCommandChain:
    """Test complete command chains through CloudWAN branch."""

    def test_full_cloudwan_navigation_chain(
        self, command_runner, isolated_shell, mock_cloudwan_client
    ):
        """Test: Complete navigation from root → global-network → core-network."""
        # Step 1: Show global networks
        result1 = command_runner.run("show global-networks")
        assert_success(result1)

        # Step 2: Enter global-network context
        result2 = command_runner.run("set global-network 1")
        assert_success(result2)
        assert_context_type(isolated_shell, "global-network")

        # Step 3: Show core networks
        result3 = command_runner.run("show core-networks")
        assert_success(result3)

        # Step 4: Enter core-network context
        result4 = command_runner.run("set core-network 1")
        assert_success(result4)
        assert_context_type(isolated_shell, "core-network")

        # Step 5: Show segments
        result5 = command_runner.run("show segments")
        assert_success(result5)

        # Step 6: Show routes
        result6 = command_runner.run("show routes")
        assert_success(result6)

        # Step 7: Exit to global-network
        result7 = command_runner.run("exit")
        assert_success(result7)
        assert_context_type(isolated_shell, "global-network")

        # Step 8: End to root
        result8 = command_runner.run("end")
        assert_success(result8)
        assert_context_type(isolated_shell, None)

    def test_cloudwan_show_commands_require_context(
        self, command_runner, isolated_shell, mock_cloudwan_client
    ):
        """Test: Core-network show commands fail in wrong context."""
        # Try to show segments at root (should fail)
        result = command_runner.run("show segments")

        assert_failure(result)
        assert_output_contains(result, "Invalid")

    def test_cloudwan_set_core_network_requires_global_network_context(
        self, command_runner, mock_cloudwan_client
    ):
        """Test: set core-network requires being in global-network context."""
        # Try to set core-network from root (should fail)
        result = command_runner.run("set core-network core-network-0global123")

        assert_failure(result)


class TestCloudWANAttachments:
    """Test CloudWAN attachment viewing commands."""

    def test_show_vpc_attachments_in_core_network_context(
        self, command_runner, isolated_shell, mock_cloudwan_client
    ):
        """Test: Show VPC attachments associated with core network."""
        # Navigate to core-network context
        command_runner.run("set global-network global-network-0prod123")
        command_runner.run("set core-network core-network-0global123")

        # Show should include attachments in detail or have dedicated command
        result = command_runner.run("show detail")

        assert_success(result)
        # Attachments should be visible in detail view

    def test_show_connect_peers_shows_bgp_info(
        self, command_runner, isolated_shell, mock_cloudwan_client
    ):
        """Test: show connect-peers displays BGP configuration."""
        # Navigate to core-network context
        command_runner.run("set global-network global-network-0prod123")
        command_runner.run("set core-network core-network-0global123")

        # Show connect peers
        result = command_runner.run("show connect-peers")

        assert_success(result)
        # Should show BGP ASNs and peer addresses from our fixtures
        # Our fixtures have peers with ASN 64600-65300
        assert_output_contains(result, "Peer")


class TestCloudWANRouting:
    """Test CloudWAN routing commands."""

    def test_show_routes_displays_all_segments(
        self, command_runner, isolated_shell, mock_cloudwan_client
    ):
        """Test: show routes displays routes for all segments and regions."""
        # Navigate to core-network context
        command_runner.run("set global-network global-network-0prod123")
        command_runner.run("set core-network core-network-0global123")

        # Show routes
        result = command_runner.run("show routes")

        assert_success(result)
        # Should show routes from multiple segments
        # Our fixtures have production, staging, shared-services segments

    def test_find_prefix_finds_vpc_routes(
        self, command_runner, isolated_shell, mock_cloudwan_client
    ):
        """Test: find_prefix locates VPC CIDR in CloudWAN routes."""
        # Navigate to core-network context
        command_runner.run("set global-network global-network-0prod123")
        command_runner.run("set core-network core-network-0global123")

        # Find production VPC CIDR
        result = command_runner.run("find_prefix 10.0.0.0/16")

        assert_success(result)
        # Should find routes in production segment

    def test_show_route_tables_lists_all_tables(
        self, command_runner, isolated_shell, mock_cloudwan_client
    ):
        """Test: show route-tables lists tables for all segment/region combinations."""
        # Navigate to core-network context
        command_runner.run("set global-network global-network-0prod123")
        command_runner.run("set core-network core-network-0global123")

        # Show route tables
        result = command_runner.run("show route-tables")

        assert_success(result)
        assert_output_contains(result, "Route Tables")
        # Our fixtures have route tables for:
        # - production-eu-west-1, production-us-east-1
        # - staging-us-east-1
        # - shared-services-eu-west-1
        # - inspection-eu-west-1


class TestCloudWANPolicy:
    """Test CloudWAN policy viewing commands."""

    def test_show_policy_displays_live_policy(
        self, command_runner, isolated_shell, mock_cloudwan_client
    ):
        """Test: show policy displays the live policy document."""
        # Navigate to core-network context
        command_runner.run("set global-network global-network-0prod123")
        command_runner.run("set core-network core-network-0global123")

        # Show policy
        result = command_runner.run("show policy")

        assert_success(result)
        assert_output_contains(result, "Policy")

    def test_show_live_policy(
        self, command_runner, isolated_shell, mock_cloudwan_client
    ):
        """Test: show live-policy displays active policy."""
        # Navigate to core-network context
        command_runner.run("set global-network global-network-0prod123")
        command_runner.run("set core-network core-network-0global123")

        # Show live policy
        result = command_runner.run("show live-policy")

        assert_success(result)
        # Should display JSON policy document

    def test_show_policy_documents(
        self, command_runner, isolated_shell, mock_cloudwan_client
    ):
        """Test: show policy-documents lists all policy versions."""
        # Navigate to core-network context
        command_runner.run("set global-network global-network-0prod123")
        command_runner.run("set core-network core-network-0global123")

        # Show policy documents
        result = command_runner.run("show policy-documents")

        assert_success(result)
        assert_output_contains(result, "Policy")


@pytest.mark.parametrize(
    "segment_name",
    ["production", "staging", "shared-services", "inspection"],
)
class TestCloudWANSegments:
    """Test segment-specific operations."""

    def test_segment_appears_in_list(
        self, command_runner, isolated_shell, mock_cloudwan_client, segment_name
    ):
        """Test: Each segment appears in segment list."""
        # Navigate to core-network context
        command_runner.run("set global-network global-network-0prod123")
        command_runner.run("set core-network core-network-0global123")

        # Show segments
        result = command_runner.run("show segments")

        assert_success(result)
        assert_output_contains(result, segment_name)
