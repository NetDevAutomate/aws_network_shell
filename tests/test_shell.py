"""Tests for AWSNetShell (strict hierarchy shell)."""

import pytest
from unittest.mock import patch

from aws_network_tools.shell import (
    AWSNetShell,
    Context,
    HIERARCHY,
)


class TestContext:
    def test_context_creation(self):
        ctx = Context("vpc", "1", "test-vpc", {"id": "vpc-123"})
        assert ctx.type == "vpc"
        assert ctx.ref == "1"
        assert ctx.name == "test-vpc"
        assert ctx.data == {"id": "vpc-123"}

    def test_context_default_data(self):
        ctx = Context("vpc", "1", "test-vpc")
        assert ctx.data == {}


class TestShellBasics:
    @pytest.fixture
    def shell(self):
        with patch("boto3.Session"):
            return AWSNetShell()

    def test_initial_prompt_and_state(self, shell):
        assert shell.prompt == "aws-net> "
        assert shell.context_stack == []
        assert shell.ctx is None
        assert shell.ctx_type is None

    def test_set_profile_and_regions_and_no_cache(self, shell):
        shell.do_set("profile test-profile")
        assert shell.profile == "test-profile"
        shell.do_set("regions eu-west-1, eu-west-2")
        assert shell.regions == ["eu-west-1", "eu-west-2"]
        shell.do_set("no-cache on")
        assert shell.no_cache is True
        shell.do_set("no-cache off")
        assert shell.no_cache is False

    def test_end_and_exit(self, shell):
        shell._enter("vpc", "vpc-1", "my-vpc", {})
        assert shell.ctx_type == "vpc"
        shell.do_exit(None)
        assert shell.ctx is None
        shell._enter("vpc", "vpc-1", "my-vpc", {})
        shell.do_end(None)
        assert shell.ctx is None

    def test_show_and_set_completions_root(self, shell):
        comps_show = shell.complete_show("", "show ", 5, 5)
        assert "vpcs" in comps_show and "transit_gateways" in comps_show
        comps_set = shell.complete_set("", "set ", 4, 4)
        # set options should include profile/regions/no-cache and root navigation
        assert (
            "profile" in comps_set
            and "regions" in comps_set
            and "no-cache" in comps_set
        )

    def test_hierarchy_constant(self):
        assert set(HIERARCHY[None]["show"]) >= {
            "vpcs",
            "transit_gateways",
            "firewalls",
            "global-networks",
            "config",
        }
        # So they won't be in shell.context_commands unless we add them manually in shell.py or move them to a module.
        # For now, let's verify what IS there from modules.


@pytest.mark.skip(reason="Legacy shell tests superseded by AWSNetShell")
class TestShowCommands:
    @pytest.fixture
    def shell(self):
        with patch("boto3.Session"):
            return AWSNetShell()

    def test_top_level_show(self, shell):
        assert "global-networks" in shell.show_commands[None]
        assert "vpcs" in shell.show_commands[None]
        assert "tgws" in shell.show_commands[None]
        assert "firewalls" in shell.show_commands[None]
        assert "config" in shell.show_commands[None]

    def test_core_network_show(self, shell):
        assert "policy-documents" in shell.show_commands["core-network"]
        assert "live-policy" in shell.show_commands["core-network"]
        assert "policy-document" in shell.show_commands["core-network"]
        assert "policy-diff" in shell.show_commands["core-network"]
        assert "route-tables" in shell.show_commands["core-network"]

    def test_vpc_show(self, shell):
        assert "detail" in shell.show_commands["vpc"]
        assert "route-tables" in shell.show_commands["vpc"]
        assert "security-groups" in shell.show_commands["vpc"]
        assert "nacls" in shell.show_commands["vpc"]


@pytest.mark.skip(reason="Legacy shell tests superseded by AWSNetShell")
class TestAWSNetShell:
    @pytest.fixture
    def shell(self):
        with patch("boto3.Session"):
            shell = AWSNetShell()
            return shell

    def test_initial_prompt(self, shell):
        assert shell.prompt == "aws-net> "

    def test_initial_context(self, shell):
        assert shell.context_stack == []
        assert shell.ctx is None
        assert shell.ctx_type is None

    def test_update_prompt_with_context(self, shell):
        shell.context_stack = [Context("vpc", "1", "test-vpc", {})]
        shell._update_prompt()
        assert "vp:test-vpc" in shell.prompt

    def test_update_prompt_nested_context(self, shell):
        shell.context_stack = [
            Context("global-network", "1", "gn-name", {}),
            Context("core-network", "1", "cn-name", {}),
        ]
        shell._update_prompt()
        assert "gl:gn-name" in shell.prompt
        assert "co:cn-name" in shell.prompt

    def test_ctx_property(self, shell):
        assert shell.ctx is None
        shell.context_stack = [Context("vpc", "1", "test", {})]
        assert shell.ctx.type == "vpc"

    def test_ctx_type_property(self, shell):
        assert shell.ctx_type is None
        shell.context_stack = [Context("vpc", "1", "test", {})]
        assert shell.ctx_type == "vpc"

    def test_do_exit_at_top(self, shell):
        result = shell.do_exit(None)
        assert result is True  # Should exit shell

    def test_do_exit_in_context(self, shell):
        shell.context_stack = [Context("vpc", "1", "test", {})]
        result = shell.do_exit(None)
        assert result is None
        assert shell.context_stack == []

    def test_do_end(self, shell):
        shell.context_stack = [
            Context("global-network", "1", "gn", {}),
            Context("core-network", "1", "cn", {}),
        ]
        shell.do_end(None)
        assert shell.context_stack == []
        assert shell.prompt == "aws-net> "

    def test_do_clear(self, shell):
        with patch("os.system") as mock_system:
            shell.do_clear(None)
            mock_system.assert_called_once()

    def test_do_set_profile(self, shell):
        shell.do_set("profile test-profile")
        assert shell.profile == "test-profile"

    def test_do_set_no_cache(self, shell):
        shell.do_set("no-cache on")
        assert shell.no_cache is True
        shell.do_set("no-cache off")
        assert shell.no_cache is False

    def test_do_set_regions(self, shell):
        shell.do_set("regions eu-west-1, eu-west-2")
        assert shell.regions == ["eu-west-1", "eu-west-2"]

    def test_do_set_regions_clear(self, shell):
        shell.regions = ["eu-west-1"]
        shell.do_set("regions")
        assert shell.regions == []

    def test_complete_set(self, shell):
        completions = shell.complete_set("", "set ", 4, 4)
        assert "profile" in completions
        assert "no-cache" in completions
        assert "cache-timeout" in completions
        assert "regions" in completions

    def test_complete_set_no_cache(self, shell):
        completions = shell.complete_set("", "set no-cache ", 13, 13)
        assert "on" in completions
        assert "off" in completions

    def test_complete_show_top_level(self, shell):
        completions = shell.complete_show("", "show ", 5, 5)
        assert "global-networks" in completions
        assert "vpcs" in completions

    def test_complete_show_in_vpc(self, shell):
        shell.context_stack = [Context("vpc", "1", "test", {})]
        completions = shell.complete_show("", "show ", 5, 5)
        assert "detail" in completions
        assert "route-tables" in completions

    def test_hidden_commands_top_level(self, shell):
        # Context-specific commands should be hidden at top level
        assert "core_network" in shell.hidden_commands
        assert "route_table" in shell.hidden_commands
        assert "find_prefix" in shell.hidden_commands

    def test_hidden_commands_in_context(self, shell):
        shell.context_stack = [Context("core-network", "1", "cn", {})]
        shell._update_prompt()
        # route-table should be visible in core-network context
        assert "route_table" not in shell.hidden_commands

    def test_resolve_helper(self, shell):
        items = [{"name": "test", "id": "123"}, {"name": "other", "id": "456"}]
        assert shell._resolve(items, "1", "name", "id") == items[0]
        assert shell._resolve(items, "test", "name", "id") == items[0]
        assert shell._resolve(items, "123", "name", "id") == items[0]
        assert shell._resolve(items, "nonexistent", "name", "id") is None

    def test_resolve_policy_version_live(self, shell, sample_policy_versions):
        shell.context_stack = [Context("core-network", "1", "cn", {"id": "cn-123"})]
        version = shell._resolve_policy_version("LIVE", sample_policy_versions)
        assert version == 5

    def test_resolve_policy_version_by_index(self, shell, sample_policy_versions):
        shell.context_stack = [Context("core-network", "1", "cn", {"id": "cn-123"})]
        version = shell._resolve_policy_version("1", sample_policy_versions)
        assert version == 5  # First item

    def test_resolve_policy_version_by_number(self, shell, sample_policy_versions):
        shell.context_stack = [Context("core-network", "1", "cn", {"id": "cn-123"})]
        version = shell._resolve_policy_version("4", sample_policy_versions)
        assert version == 4


@pytest.mark.skip(reason="Legacy shell tests superseded by AWSNetShell")
class TestShellNavigation:
    @pytest.fixture
    def shell_with_data(self):
        with patch("boto3.Session"):
            shell = AWSNetShell()
            shell._cache = {
                "vpcs": [{"id": "vpc-123", "name": "test-vpc", "region": "eu-west-1"}],
                "tgws": [
                    {
                        "id": "tgw-123",
                        "name": "test-tgw",
                        "region": "eu-west-1",
                        "route_tables": [],
                    }
                ],
                "firewalls": [
                    {
                        "name": "test-fw",
                        "arn": "arn:...",
                        "region": "eu-west-1",
                        "rule_groups": [],
                    }
                ],
                "global_networks": [
                    {
                        "id": "gn-123",
                        "name": "test-gn",
                        "core_networks": [
                            {
                                "id": "cn-123",
                                "name": "test-cn",
                                "route_tables": [],
                                "regions": [],
                                "segments": [],
                            }
                        ],
                    }
                ],
            }
            return shell

    def test_do_global_network(self, shell_with_data):
        shell_with_data.do_global_network("1")
        assert shell_with_data.ctx_type == "global-network"
        assert "gl:" in shell_with_data.prompt

    def test_do_global_network_not_found(self, shell_with_data, capsys):
        shell_with_data.do_global_network("999")
        assert shell_with_data.ctx is None

    def test_do_core_network_requires_context(self, shell_with_data, capsys):
        shell_with_data.do_core_network("1")
        # Should print error - not in global-network context

    def test_do_core_network_in_context(self, shell_with_data):
        shell_with_data.do_global_network("1")
        shell_with_data.do_core_network("1")
        assert shell_with_data.ctx_type == "core-network"

    def test_do_tgw(self, shell_with_data):
        shell_with_data.do_tgw("1")
        assert shell_with_data.ctx_type == "tgw"

    def test_do_firewall(self, shell_with_data):
        shell_with_data.do_firewall("1")
        assert shell_with_data.ctx_type == "firewall"

    def test_navigation_requires_top_level(self, shell_with_data, capsys):
        shell_with_data.do_tgw("1")
        shell_with_data.do_vpc("1")  # Should fail - already in context
        assert shell_with_data.ctx_type == "tgw"  # Still in tgw
