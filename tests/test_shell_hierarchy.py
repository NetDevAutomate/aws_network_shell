"""TDD tests for strict Cisco IOS-style CLI hierarchy.

Binary pass/fail tests against taylaand+net-dev-Admin profile.
"""

import pytest
from aws_network_tools.shell import AWSNetShell, HIERARCHY

PROFILE = "taylaand+net-dev-Admin"


class TestHierarchyDefinition:
    """Test hierarchy structure is correctly defined."""

    def test_root_level_has_required_show_options(self):
        """Root level must have show options for all resource types."""
        required = {
            "global-networks",
            "vpcs",
            "transit_gateways",
            "firewalls",
            "config",
        }
        actual = set(HIERARCHY[None]["show"])
        assert required.issubset(actual), f"Missing: {required - actual}"

    def test_root_level_has_required_set_options(self):
        """Root level must have set options for navigation."""
        required = {
            "global-network",
            "vpc",
            "transit-gateway",
            "firewall",
            "profile",
            "regions",
        }
        actual = set(HIERARCHY[None]["set"])
        assert required.issubset(actual), f"Missing: {required - actual}"

    def test_global_network_context_has_core_networks(self):
        """Global network context must allow showing core networks."""
        assert "core-networks" in HIERARCHY["global-network"]["show"]
        assert "core-network" in HIERARCHY["global-network"]["set"]

    def test_core_network_context_has_route_tables(self):
        """Core network context must allow showing route tables."""
        assert "route-tables" in HIERARCHY["core-network"]["show"]
        assert "route-table" in HIERARCHY["core-network"]["set"]

    def test_route_table_context_has_routes(self):
        """Route table context must allow showing routes."""
        assert "routes" in HIERARCHY["route-table"]["show"]
        assert "find_prefix" in HIERARCHY["route-table"]["commands"]
        assert "find_null_routes" in HIERARCHY["route-table"]["commands"]

    def test_vpc_context_has_required_show_options(self):
        """VPC context must have all required show options."""
        required = {"detail", "route-tables", "subnets", "security-groups", "nacls"}
        actual = set(HIERARCHY["vpc"]["show"])
        assert required.issubset(actual), f"Missing: {required - actual}"

    def test_tgw_context_has_required_show_options(self):
        """TGW context must have all required show options."""
        required = {"detail", "route-tables", "attachments"}
        actual = set(HIERARCHY["transit-gateway"]["show"])
        assert required.issubset(actual), f"Missing: {required - actual}"

    def test_firewall_context_has_required_show_options(self):
        """Firewall context must have all required show options."""
        required = {"detail", "rule-groups", "policy"}  # Issue #7: policy must be available
        actual = set(HIERARCHY["firewall"]["show"])
        assert required.issubset(actual), f"Missing: {required - actual}"


class TestShellInitialization:
    """Test shell initializes correctly."""

    def test_shell_creates_with_default_state(self):
        """Shell must initialize with empty context stack."""
        shell = AWSNetShell()
        assert shell.context_stack == []
        assert shell.ctx is None
        assert shell.ctx_type is None

    def test_shell_prompt_at_root(self):
        """Shell prompt must be 'aws-net>' at root."""
        shell = AWSNetShell()
        assert shell.prompt == "aws-net> "

    def test_shell_hierarchy_at_root(self):
        """Shell hierarchy must return root hierarchy when no context."""
        shell = AWSNetShell()
        assert shell.hierarchy == HIERARCHY[None]


class TestContextNavigation:
    """Test context navigation works correctly."""

    def test_enter_context_updates_stack(self):
        """Entering context must update context stack."""
        shell = AWSNetShell()
        shell._enter("test-type", "test-id", "test-name", {"key": "value"})

        assert len(shell.context_stack) == 1
        assert shell.ctx_type == "test-type"
        assert shell.ctx_id == "test-id"
        assert shell.ctx.name == "test-name"
        assert shell.ctx.data == {"key": "value"}

    def test_exit_pops_context(self):
        """Exit must pop context from stack."""
        shell = AWSNetShell()
        shell._enter("test-type", "test-id", "test-name", {})
        shell.do_exit(None)

        assert len(shell.context_stack) == 0
        assert shell.ctx is None

    def test_end_clears_all_contexts(self):
        """End must clear entire context stack."""
        shell = AWSNetShell()
        shell._enter("type1", "id1", "name1", {})
        shell._enter("type2", "id2", "name2", {})
        shell.do_end(None)

        assert len(shell.context_stack) == 0

    def test_prompt_updates_with_context(self):
        """Prompt must reflect current context."""
        shell = AWSNetShell()
        shell._enter("global-network", "gn-123", "my-network", {})

        assert "gl:" in shell.prompt
        assert "my-network" in shell.prompt


class TestResolveResource:
    """Test resource resolution by index, name, or ID."""

    def test_resolve_by_index(self):
        """Must resolve resource by 1-based index."""
        shell = AWSNetShell()
        items = [{"id": "a", "name": "first"}, {"id": "b", "name": "second"}]

        assert shell._resolve(items, "1") == items[0]
        assert shell._resolve(items, "2") == items[1]

    def test_resolve_by_id(self):
        """Must resolve resource by exact ID."""
        shell = AWSNetShell()
        items = [{"id": "vpc-123", "name": "my-vpc"}]

        assert shell._resolve(items, "vpc-123") == items[0]

    def test_resolve_by_name(self):
        """Must resolve resource by name (case-insensitive)."""
        shell = AWSNetShell()
        items = [{"id": "vpc-123", "name": "MyVPC"}]

        assert shell._resolve(items, "myvpc") == items[0]
        assert shell._resolve(items, "MYVPC") == items[0]

    def test_resolve_returns_none_for_invalid(self):
        """Must return None for invalid reference."""
        shell = AWSNetShell()
        items = [{"id": "a", "name": "first"}]

        assert shell._resolve(items, "99") is None
        assert shell._resolve(items, "nonexistent") is None


@pytest.mark.integration
class TestCloudWANIntegration:
    """Integration tests for Cloud WAN navigation against live AWS."""

    @pytest.fixture
    def shell(self):
        """Create shell with test profile."""
        s = AWSNetShell()
        s.profile = PROFILE
        return s

    def test_show_global_networks_returns_data(self, shell):
        """show global-networks must return at least one network."""
        shell._show_global_networks(None)
        gns = shell._cache.get("global-network", [])

        assert len(gns) >= 1, "Expected at least 1 global network"
        assert "id" in gns[0]
        assert "name" in gns[0]

    def test_set_global_network_enters_context(self, shell):
        """set global-network must enter global-network context."""
        shell._show_global_networks(None)
        shell._set_global_network("1")

        assert shell.ctx_type == "global-network"

    def test_show_core_networks_in_context(self, shell):
        """show core-networks must work in global-network context."""
        shell._show_global_networks(None)
        shell._set_global_network("1")
        shell._show_core_networks(None)

        cns = shell._cache.get(f"core-network:{shell.ctx_id}", [])
        assert len(cns) >= 1, "Expected at least 1 core network"

    def test_set_core_network_enters_context(self, shell):
        """set core-network must enter core-network context."""
        shell._show_global_networks(None)
        shell._set_global_network("1")
        shell._show_core_networks(None)
        shell._set_core_network("1")

        assert shell.ctx_type == "core-network"

    def test_show_route_tables_in_core_network(self, shell):
        """show route-tables must work in core-network context."""
        shell._show_global_networks(None)
        shell._set_global_network("1")
        shell._show_core_networks(None)
        shell._set_core_network("1")
        shell._show_route_tables(None)

        rts = shell._cache.get(f"route-table:{shell.ctx_id}", [])
        assert len(rts) >= 1, "Expected at least 1 route table"

    def test_set_route_table_enters_context(self, shell):
        """set route-table must enter route-table context."""
        shell._show_global_networks(None)
        shell._set_global_network("1")
        shell._show_core_networks(None)
        shell._set_core_network("1")
        shell._show_route_tables(None)
        shell._set_route_table("1")

        assert shell.ctx_type == "route-table"

    def test_show_routes_in_route_table(self, shell):
        """show routes must display routes in route-table context."""
        shell._show_global_networks(None)
        shell._set_global_network("1")
        shell._show_core_networks(None)
        shell._set_core_network("1")
        shell._show_route_tables(None)
        shell._set_route_table("1")

        routes = shell.ctx.data.get("routes", [])
        assert len(routes) >= 1, "Expected at least 1 route"


@pytest.mark.integration
class TestVPCIntegration:
    """Integration tests for VPC navigation against live AWS."""

    @pytest.fixture
    def shell(self):
        s = AWSNetShell()
        s.profile = PROFILE
        return s

    def test_show_vpcs_returns_data(self, shell):
        """show vpcs must return at least one VPC."""
        shell._show_vpcs(None)
        vpcs = shell._cache.get("vpc", [])

        assert len(vpcs) >= 1, "Expected at least 1 VPC"
        assert "id" in vpcs[0]

    def test_set_vpc_enters_context(self, shell):
        """set vpc must enter vpc context."""
        shell._show_vpcs(None)
        shell._set_vpc("1")

        assert shell.ctx_type == "vpc"

    def test_show_subnets_in_vpc_context(self, shell):
        """show subnets must work in VPC context."""
        shell._show_vpcs(None)
        # Find a VPC with subnets (named VPCs are more likely to have them)
        vpcs = shell._cache.get("vpc", [])
        named_vpc = next((v for v in vpcs if v.get("name")), vpcs[0])
        idx = vpcs.index(named_vpc) + 1
        shell._set_vpc(str(idx))
        shell._show_subnets(None)
        # Test passes if no exception - some VPCs may have no subnets
        assert shell.ctx_type == "vpc"

    def test_show_security_groups_in_vpc_context(self, shell):
        """show security-groups must work in VPC context."""
        shell._show_vpcs(None)
        shell._set_vpc("1")
        shell._show_security_groups(None)
        assert shell.ctx_type == "vpc"

    def test_show_nacls_in_vpc_context(self, shell):
        """show nacls must work in VPC context."""
        shell._show_vpcs(None)
        shell._set_vpc("1")
        shell._show_nacls(None)
        assert shell.ctx_type == "vpc"


@pytest.mark.integration
class TestTGWIntegration:
    """Integration tests for TGW navigation against live AWS."""

    @pytest.fixture
    def shell(self):
        s = AWSNetShell()
        s.profile = PROFILE
        return s

    def test_show_tgws_returns_data(self, shell):
        """show tgws must return at least one TGW."""
        shell._show_tgws(None)
        tgws = shell._cache.get("tgw", [])

        assert len(tgws) >= 1, "Expected at least 1 TGW"
        assert "id" in tgws[0]

    def test_set_tgw_enters_context(self, shell):
        """set tgw must enter tgw context."""
        shell._show_tgws(None)
        shell._set_tgw("1")

        assert shell.ctx_type == "tgw"

    def test_show_tgw_route_tables_in_context(self, shell):
        """show route-tables must work in TGW context."""
        shell._show_tgws(None)
        shell._set_tgw("1")
        shell._show_tgw_route_tables()
        # Test passes if no exception
        assert shell.ctx_type == "tgw"

    def test_show_attachments_in_tgw_context(self, shell):
        """show attachments must work in TGW context."""
        shell._show_tgws(None)
        shell._set_tgw("1")
        shell._show_attachments(None)
        assert shell.ctx_type == "tgw"


@pytest.mark.integration
class TestFirewallIntegration:
    """Integration tests for Network Firewall navigation against live AWS."""

    @pytest.fixture
    def shell(self):
        s = AWSNetShell()
        s.profile = PROFILE
        return s

    def test_show_firewalls_returns_data(self, shell):
        """show firewalls must return at least one firewall."""
        shell._show_firewalls(None)
        fws = shell._cache.get("firewall", [])

        assert len(fws) >= 1, "Expected at least 1 firewall"

    def test_set_firewall_enters_context(self, shell):
        """set firewall must enter firewall context."""
        shell._show_firewalls(None)
        shell._set_firewall("1")

        assert shell.ctx_type == "firewall"

    def test_show_rule_groups_in_firewall_context(self, shell):
        """show rule-groups must work in firewall context."""
        shell._show_firewalls(None)
        shell._set_firewall("1")
        shell._show_rule_groups(None)
        assert shell.ctx_type == "firewall"

    def test_show_policy_in_firewall_context(self, shell):
        """show policy must work in firewall context (Issue #7)."""
        shell._show_firewalls(None)
        shell._set_firewall("1")
        # This should NOT raise an error or display "Must be in core-network context"
        shell._show_policy(None)
        assert shell.ctx_type == "firewall"

    def test_firewall_policy_data_structure(self, shell):
        """Firewall policy must have correct data structure for display."""
        shell._show_firewalls(None)
        shell._set_firewall("1")

        policy = shell.ctx.data.get("policy", {})
        # Policy must have name for display
        assert "name" in policy, "Policy must have 'name' field"
        # Policy must have arn for display
        assert "arn" in policy, "Policy must have 'arn' field"
        # Stateless default actions must be a dict with expected keys
        stateless_defaults = policy.get("stateless_default_actions", {})
        assert isinstance(stateless_defaults, dict), "stateless_default_actions must be a dict"
        assert "full_packets" in stateless_defaults, "stateless_default_actions must have 'full_packets'"
        assert "fragmented" in stateless_defaults, "stateless_default_actions must have 'fragmented'"
        # Stateful engine options must exist
        assert "stateful_engine_options" in policy, "Policy must have 'stateful_engine_options'"
        engine_opts = policy.get("stateful_engine_options", {})
        assert "rule_order" in engine_opts, "stateful_engine_options must have 'rule_order'"
        assert "stream_exception_policy" in engine_opts, "stateful_engine_options must have 'stream_exception_policy'"


class TestGraphValidation:
    """Test command graph validation catches HIERARCHY drift."""

    def test_validate_graph_passes(self):
        """validate_graph must pass with no errors."""
        from aws_network_tools.shell.graph import validate_graph

        result = validate_graph(AWSNetShell)
        assert result.valid, f"Graph validation failed: {result.errors}"

    def test_build_graph_creates_nodes(self):
        """build_graph must create command nodes from HIERARCHY."""
        from aws_network_tools.shell.graph import build_graph

        graph = build_graph(AWSNetShell)
        stats = graph.stats()
        assert stats["total_nodes"] > 0, "Graph should have nodes"
        assert stats["contexts"] > 0, "Graph should have contexts"

    def test_graph_has_all_hierarchy_contexts(self):
        """Graph must include all contexts from HIERARCHY."""
        from aws_network_tools.shell.graph import build_graph

        graph = build_graph(AWSNetShell)
        stats = graph.stats()
        # HIERARCHY has root (None) + named contexts
        hierarchy_contexts = len([k for k in HIERARCHY.keys() if k is not None])
        assert stats["contexts"] >= hierarchy_contexts


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
