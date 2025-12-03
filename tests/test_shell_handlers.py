"""Tests for modular shell handlers."""

from unittest.mock import patch

from aws_network_tools.shell import AWSNetShell, Context, HIERARCHY
from aws_network_tools.shell.base import AWSNetShellBase, ALIASES
from aws_network_tools.shell.handlers import (
    RootHandlersMixin,
    CloudWANHandlersMixin,
    VPCHandlersMixin,
    VPNHandlersMixin,
    ELBHandlersMixin,
    UtilityHandlersMixin,
)


class TestShellBase:
    """Tests for AWSNetShellBase."""

    def test_init(self):
        shell = AWSNetShellBase()
        assert shell.profile is None
        assert shell.regions == []
        assert shell.no_cache is False
        assert shell.output_format == "table"
        assert shell.context_stack == []

    def test_ctx_property_empty(self):
        shell = AWSNetShellBase()
        assert shell.ctx is None
        assert shell.ctx_type is None
        assert shell.ctx_id == ""

    def test_ctx_property_with_context(self):
        shell = AWSNetShellBase()
        shell.context_stack.append(Context("vpc", "vpc-123", "my-vpc", {}))
        assert shell.ctx is not None
        assert shell.ctx_type == "vpc"
        assert shell.ctx_id == "vpc-123"

    def test_hierarchy_root(self):
        shell = AWSNetShellBase()
        assert "global-networks" in shell.hierarchy["show"]
        assert "vpcs" in shell.hierarchy["show"]
        assert "global-network" in shell.hierarchy["set"]

    def test_hierarchy_vpc_context(self):
        shell = AWSNetShellBase()
        shell.context_stack.append(Context("vpc", "vpc-123", "my-vpc", {}))
        assert "detail" in shell.hierarchy["show"]
        assert "subnets" in shell.hierarchy["show"]

    def test_update_prompt_root(self):
        shell = AWSNetShellBase()
        shell._update_prompt()
        assert shell.prompt == "aws-net> "

    def test_update_prompt_with_context(self):
        shell = AWSNetShellBase()
        shell._enter("vpc", "vpc-123", "my-vpc")
        assert "vp:my-vpc" in shell.prompt

    def test_enter_context(self):
        shell = AWSNetShellBase()
        shell._enter("vpc", "vpc-123", "my-vpc", {"id": "vpc-123"})
        assert len(shell.context_stack) == 1
        assert shell.ctx.type == "vpc"
        assert shell.ctx.ref == "vpc-123"
        assert shell.ctx.name == "my-vpc"

    def test_exit_context(self):
        shell = AWSNetShellBase()
        shell._enter("vpc", "vpc-123", "my-vpc")
        shell.do_exit(None)
        assert len(shell.context_stack) == 0

    def test_end_clears_all(self):
        shell = AWSNetShellBase()
        shell._enter("global-network", "gn-1", "gn")
        shell._enter("core-network", "cn-1", "cn")
        shell.do_end(None)
        assert len(shell.context_stack) == 0

    def test_resolve_by_index(self):
        shell = AWSNetShellBase()
        items = [{"id": "vpc-1", "name": "first"}, {"id": "vpc-2", "name": "second"}]
        result = shell._resolve(items, "1")
        assert result["id"] == "vpc-1"

    def test_resolve_by_id(self):
        shell = AWSNetShellBase()
        items = [{"id": "vpc-1", "name": "first"}, {"id": "vpc-2", "name": "second"}]
        result = shell._resolve(items, "vpc-2")
        assert result["name"] == "second"

    def test_resolve_by_name(self):
        shell = AWSNetShellBase()
        items = [{"id": "vpc-1", "name": "first"}, {"id": "vpc-2", "name": "second"}]
        result = shell._resolve(items, "first")
        assert result["id"] == "vpc-1"

    def test_resolve_not_found(self):
        shell = AWSNetShellBase()
        items = [{"id": "vpc-1", "name": "first"}]
        result = shell._resolve(items, "nonexistent")
        assert result is None


class TestAWSNetShell:
    """Tests for composed shell class."""

    def test_inherits_all_mixins(self):
        shell = AWSNetShell()
        # Check methods from different mixins exist
        assert hasattr(shell, "_show_vpcs")  # RootHandlersMixin
        assert hasattr(shell, "_show_core_networks")  # CloudWANHandlersMixin
        assert hasattr(shell, "_set_vpc")  # VPCHandlersMixin
        assert hasattr(shell, "_set_transit_gateway")  # TGWHandlersMixin
        assert hasattr(shell, "_show_ec2_instances")  # EC2HandlersMixin
        assert hasattr(shell, "_set_firewall")  # FirewallHandlersMixin
        assert hasattr(shell, "do_trace")  # UtilityHandlersMixin

    def test_cached_method(self):
        shell = AWSNetShell()
        shell._cache = {}
        with patch("aws_network_tools.core.run_with_spinner") as mock_spinner:
            mock_spinner.return_value = [{"id": "test"}]
            result = shell._cached("test-key", lambda: [{"id": "test"}], "Loading")
            assert result == [{"id": "test"}]
            # Second call should use cache (no_cache=False by default)
            result2 = shell._cached("test-key", lambda: [{"id": "other"}], "Loading")
            assert result2 == [{"id": "test"}]

    def test_emit_json(self, capsys):
        shell = AWSNetShell()
        shell.output_format = "json"
        shell._emit_json_or_table({"key": "value"}, lambda: None)
        # JSON output goes to rich console, not captured by capsys

    def test_do_show_invalid(self, capsys):
        shell = AWSNetShell()
        shell.do_show("invalid-command")
        # Should print error about invalid command

    def test_do_set_invalid(self, capsys):
        shell = AWSNetShell()
        shell.do_set("invalid-option")
        # Should print error about invalid option

    def test_complete_show_root(self):
        shell = AWSNetShell()
        completions = shell.complete_show("vp", "show vp", 5, 7)
        assert "vpcs" in completions

    def test_complete_set_root(self):
        shell = AWSNetShell()
        completions = shell.complete_set("pro", "set pro", 4, 7)
        assert "profile" in completions


class TestHierarchy:
    """Tests for HIERARCHY structure."""

    def test_root_hierarchy_exists(self):
        assert None in HIERARCHY
        assert "show" in HIERARCHY[None]
        assert "set" in HIERARCHY[None]
        assert "commands" in HIERARCHY[None]

    def test_all_contexts_have_required_keys(self):
        for ctx_type, config in HIERARCHY.items():
            assert "show" in config, f"{ctx_type} missing 'show'"
            assert "set" in config, f"{ctx_type} missing 'set'"
            assert "commands" in config, f"{ctx_type} missing 'commands'"

    def test_vpc_context(self):
        assert "vpc" in HIERARCHY
        assert "detail" in HIERARCHY["vpc"]["show"]
        assert "subnets" in HIERARCHY["vpc"]["show"]
        assert "security-groups" in HIERARCHY["vpc"]["show"]

    def test_transit_gateway_context(self):
        assert "transit-gateway" in HIERARCHY
        assert "detail" in HIERARCHY["transit-gateway"]["show"]
        assert "route-tables" in HIERARCHY["transit-gateway"]["show"]
        assert "route-table" in HIERARCHY["transit-gateway"]["set"]

    def test_core_network_context(self):
        assert "core-network" in HIERARCHY
        assert "rib" in HIERARCHY["core-network"]["show"]
        assert "connect-peers" in HIERARCHY["core-network"]["show"]


class TestMixinIsolation:
    """Tests that mixins can be used independently."""

    def test_root_mixin_methods(self):
        """RootHandlersMixin should have all root-level handlers."""
        assert hasattr(RootHandlersMixin, "_show_config")
        assert hasattr(RootHandlersMixin, "_show_vpcs")
        assert hasattr(RootHandlersMixin, "_set_profile")

    def test_cloudwan_mixin_methods(self):
        """CloudWANHandlersMixin should have Cloud WAN handlers."""
        assert hasattr(CloudWANHandlersMixin, "_show_core_networks")
        assert hasattr(CloudWANHandlersMixin, "_show_rib")
        assert hasattr(CloudWANHandlersMixin, "_show_segments")
        assert hasattr(CloudWANHandlersMixin, "_show_policy")
        assert hasattr(CloudWANHandlersMixin, "do_find_prefix")

    def test_vpc_mixin_methods(self):
        """VPCHandlersMixin should have VPC handlers."""
        assert hasattr(VPCHandlersMixin, "_set_vpc")
        assert hasattr(VPCHandlersMixin, "_show_subnets")
        assert hasattr(VPCHandlersMixin, "_show_nacls")

    def test_utility_mixin_methods(self):
        """UtilityHandlersMixin should have utility commands."""
        assert hasattr(UtilityHandlersMixin, "do_trace")
        assert hasattr(UtilityHandlersMixin, "do_find_ip")
        assert hasattr(UtilityHandlersMixin, "do_run")

    def test_vpn_mixin_methods(self):
        """VPNHandlersMixin should have VPN handlers."""
        assert hasattr(VPNHandlersMixin, "_set_vpn")
        assert hasattr(VPNHandlersMixin, "_show_vpns")
        assert hasattr(VPNHandlersMixin, "_show_tunnels")

    def test_elb_mixin_methods(self):
        """ELBHandlersMixin should have ELB handlers."""
        assert hasattr(ELBHandlersMixin, "_set_elb")
        assert hasattr(ELBHandlersMixin, "_show_elbs")
        assert hasattr(ELBHandlersMixin, "_show_listeners")
        assert hasattr(ELBHandlersMixin, "_show_targets")
        assert hasattr(ELBHandlersMixin, "_show_health")


class TestAliases:
    """Tests for command aliases."""

    def test_aliases_defined(self):
        """ALIASES should contain common shortcuts."""
        assert "sh" in ALIASES
        assert ALIASES["sh"] == "show"
        assert "ex" in ALIASES
        assert ALIASES["ex"] == "exit"

    def test_precmd_expands_alias(self):
        """precmd should expand aliases."""
        import cmd2

        shell = AWSNetShellBase()
        result = shell.precmd(cmd2.Statement("sh vpcs"))
        assert "show vpcs" in str(result)

    def test_precmd_no_expansion_for_full_command(self):
        """precmd should not modify full commands."""
        import cmd2

        shell = AWSNetShellBase()
        result = shell.precmd(cmd2.Statement("show vpcs"))
        assert "show vpcs" in str(result)


class TestPipeOperators:
    """Tests for pipe operators."""

    def test_apply_pipe_filter_include(self):
        """_apply_pipe_filter should filter with include."""
        shell = AWSNetShellBase()
        output = "line1 prod\nline2 dev\nline3 prod"
        result = shell._apply_pipe_filter(output, "include prod")
        assert "line1 prod" in result
        assert "line3 prod" in result
        assert "line2 dev" not in result

    def test_apply_pipe_filter_exclude(self):
        """_apply_pipe_filter should filter with exclude."""
        shell = AWSNetShellBase()
        output = "line1 prod\nline2 dev\nline3 prod"
        result = shell._apply_pipe_filter(output, "exclude prod")
        assert "line2 dev" in result
        assert "line1 prod" not in result

    def test_apply_pipe_filter_grep(self):
        """_apply_pipe_filter should support grep alias."""
        shell = AWSNetShellBase()
        output = "vpc-123\nvpc-456\ntgw-789"
        result = shell._apply_pipe_filter(output, "grep vpc")
        assert "vpc-123" in result
        assert "vpc-456" in result
        assert "tgw-789" not in result


class TestNewContexts:
    """Tests for VPN and ELB contexts."""

    def test_vpn_context_in_hierarchy(self):
        """VPN context should be in HIERARCHY."""
        assert "vpn" in HIERARCHY
        assert "tunnels" in HIERARCHY["vpn"]["show"]
        assert "detail" in HIERARCHY["vpn"]["show"]

    def test_elb_context_in_hierarchy(self):
        """ELB context should be in HIERARCHY."""
        assert "elb" in HIERARCHY
        assert "listeners" in HIERARCHY["elb"]["show"]
        assert "targets" in HIERARCHY["elb"]["show"]
        assert "health" in HIERARCHY["elb"]["show"]

    def test_root_has_vpns_and_elbs(self):
        """Root context should have vpns and elbs show commands."""
        assert "vpns" in HIERARCHY[None]["show"]
        assert "elbs" in HIERARCHY[None]["show"]
        assert "vpn" in HIERARCHY[None]["set"]
        assert "elb" in HIERARCHY[None]["set"]

    def test_running_config_in_hierarchy(self):
        """Root context should have running-config show command."""
        assert "running-config" in HIERARCHY[None]["show"]
        assert "config" in HIERARCHY[None]["show"]


class TestRunningConfig:
    """Tests for show running-config command."""

    def test_running_config_alias(self):
        """_show_running_config should be alias for _show_config."""
        shell = AWSNetShell()
        assert hasattr(shell, "_show_running_config")
        assert hasattr(shell, "_show_config")
        # They should be the same method
        assert shell._show_running_config == shell._show_config
