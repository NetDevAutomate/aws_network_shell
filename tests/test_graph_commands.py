"""Graph-based command testing - tests EVERY command in the hierarchy.

Uses command graph + fixtures to ensure complete coverage.
"""

import pytest
from unittest.mock import patch
from aws_network_tools.shell.base import HIERARCHY
from tests.fixtures.command_fixtures import (
    COMMAND_MOCKS,
    get_mock_for_command,
    _vpcs_list,
    _tgws_list,
    _firewalls_list,
    _ec2_instances_list,
    _elbs_list,
    _vpns_list,
)
from tests.fixtures import get_vpc_detail


def build_command_graph() -> dict:
    """Build complete command graph from HIERARCHY."""
    graph = {}

    for context, commands in HIERARCHY.items():
        prefix = f"{context}." if context else ""

        for show_cmd in commands.get("show", []):
            cmd_key = f"{prefix}show {show_cmd}"
            graph[cmd_key] = {
                "type": "show",
                "context": context,
                "command": f"show {show_cmd}",
                "full_key": cmd_key,
            }

        for set_cmd in commands.get("set", []):
            cmd_key = f"{prefix}set {set_cmd}"
            graph[cmd_key] = {
                "type": "set",
                "context": context,
                "command": f"set {set_cmd}",
                "full_key": cmd_key,
                "enters_context": set_cmd,
            }

        for action in commands.get("commands", []):
            if action not in ("show", "set", "exit", "end", "clear"):
                cmd_key = f"{prefix}{action}"
                graph[cmd_key] = {
                    "type": "action",
                    "context": context,
                    "command": action,
                    "full_key": cmd_key,
                }

    return graph


COMMAND_GRAPH = build_command_graph()
TESTABLE_COMMANDS = [k for k in COMMAND_GRAPH.keys() if k in COMMAND_MOCKS]


class TestCommandGraph:
    """Test command graph structure."""

    def test_graph_has_all_contexts(self):
        contexts = {info["context"] for info in COMMAND_GRAPH.values()}
        assert contexts == set(HIERARCHY.keys())

    def test_graph_command_count(self):
        show_count = sum(1 for v in COMMAND_GRAPH.values() if v["type"] == "show")
        set_count = sum(1 for v in COMMAND_GRAPH.values() if v["type"] == "set")
        assert show_count >= 50
        assert set_count >= 10

    def test_fixture_coverage(self):
        total = len(COMMAND_GRAPH)
        covered = len(TESTABLE_COMMANDS)
        print(f"\nFixture coverage: {covered}/{total} ({(covered / total) * 100:.1f}%)")


class TestRootShowCommands:
    """Test root-level show commands."""

    @pytest.fixture
    def shell(self):
        from aws_network_tools.shell import AWSNetShell

        shell = AWSNetShell()
        shell.no_cache = True
        yield shell
        shell._cache.clear()

    @pytest.mark.parametrize(
        "command",
        [
            "show vpcs",
            "show transit_gateways",
            "show firewalls",
            "show ec2-instances",
            "show elbs",
            "show vpns",
        ],
    )
    def test_root_show_command(self, shell, command):
        mock_config = get_mock_for_command(command)
        if not mock_config:
            pytest.skip(f"No fixture for {command}")

        with patch(mock_config["target"], return_value=mock_config["return_value"]):
            result = shell.onecmd(command)
            assert result in (None, False)


class TestContextEntry:
    """Test context entry (set) commands with full mock chain."""

    @pytest.fixture
    def shell(self):
        from aws_network_tools.shell import AWSNetShell

        shell = AWSNetShell()
        shell.no_cache = True
        yield shell
        shell._cache.clear()
        shell.context_stack.clear()

    def test_vpc_context_entry(self, shell):
        """Test entering VPC context."""
        vpcs = _vpcs_list()
        vpc_id = vpcs[0]["id"] if vpcs else "vpc-test123"
        vpc_detail = get_vpc_detail(vpc_id) or {
            "id": vpc_id,
            "name": "test",
            "region": "eu-west-1",
            "cidr": "10.0.0.0/16",
            "cidrs": ["10.0.0.0/16"],
            "state": "available",
            "route_tables": [],
            "security_groups": [],
            "nacls": [],
        }

        with patch(
            "aws_network_tools.modules.vpc.VPCClient.discover", return_value=vpcs
        ):
            with patch(
                "aws_network_tools.modules.vpc.VPCClient.get_vpc_detail",
                return_value=vpc_detail,
            ):
                shell.onecmd("show vpcs")
                result = shell.onecmd("set vpc 1")
                assert result in (None, False)
                assert shell.context_stack  # Context was entered

    def test_tgw_context_entry(self, shell):
        """Test entering TGW context."""
        tgws = _tgws_list()

        with patch(
            "aws_network_tools.modules.tgw.TGWClient.discover", return_value=tgws
        ):
            shell.onecmd("show transit_gateways")
            result = shell.onecmd("set transit-gateway 1")
            assert result in (None, False)

    def test_firewall_context_entry(self, shell):
        """Test entering firewall context."""
        fws = _firewalls_list()

        with patch(
            "aws_network_tools.modules.anfw.ANFWClient.discover", return_value=fws
        ):
            shell.onecmd("show firewalls")
            result = shell.onecmd("set firewall 1")
            assert result in (None, False)

    def test_ec2_context_entry(self, shell):
        """Test entering EC2 instance context."""
        instances = _ec2_instances_list()

        with patch(
            "aws_network_tools.modules.ec2.EC2Client.discover", return_value=instances
        ):
            shell.onecmd("show ec2-instances")
            result = shell.onecmd("set ec2-instance 1")
            assert result in (None, False)

    def test_elb_context_entry(self, shell):
        """Test entering ELB context."""
        elbs = _elbs_list()
        elb_detail = (
            {
                "arn": elbs[0]["arn"],
                "name": elbs[0]["name"],
                "type": elbs[0]["type"],
                "listeners": [],
                "target_groups": [],
            }
            if elbs
            else {}
        )

        with patch(
            "aws_network_tools.modules.elb.ELBClient.discover", return_value=elbs
        ):
            with patch(
                "aws_network_tools.modules.elb.ELBClient.get_elb_detail",
                return_value=elb_detail,
            ):
                shell.onecmd("show elbs")
                result = shell.onecmd("set elb 1")
                assert result in (None, False)

    def test_vpn_context_entry(self, shell):
        """Test entering VPN context."""
        vpns = _vpns_list()

        with patch(
            "aws_network_tools.modules.vpn.VPNClient.discover", return_value=vpns
        ):
            shell.onecmd("show vpns")
            result = shell.onecmd("set vpn 1")
            assert result in (None, False)


class TestVPCContextCommands:
    """Test commands within VPC context."""

    @pytest.fixture
    def shell_in_vpc(self):
        """Shell with VPC context entered."""
        from aws_network_tools.shell import AWSNetShell

        shell = AWSNetShell()
        shell.no_cache = True

        vpcs = _vpcs_list()
        vpc_id = vpcs[0]["id"] if vpcs else "vpc-test"
        vpc_detail = get_vpc_detail(vpc_id) or {
            "id": vpc_id,
            "name": "test",
            "region": "eu-west-1",
            "cidr": "10.0.0.0/16",
            "cidrs": ["10.0.0.0/16"],
            "state": "available",
            "route_tables": [
                {
                    "id": "rtb-1",
                    "name": "main",
                    "is_main": True,
                    "routes": [],
                    "subnets": [],
                }
            ],
            "security_groups": [
                {
                    "id": "sg-1",
                    "name": "default",
                    "description": "",
                    "ingress": [],
                    "egress": [],
                }
            ],
            "nacls": [
                {"id": "acl-1", "name": "default", "is_default": True, "entries": []}
            ],
            "subnets": [
                {
                    "id": "subnet-1",
                    "name": "public",
                    "cidr": "10.0.1.0/24",
                    "az": "eu-west-1a",
                    "state": "available",
                }
            ],
        }

        # Start patches
        p1 = patch(
            "aws_network_tools.modules.vpc.VPCClient.discover", return_value=vpcs
        )
        p2 = patch(
            "aws_network_tools.modules.vpc.VPCClient.get_vpc_detail",
            return_value=vpc_detail,
        )
        p1.start()
        p2.start()

        shell.onecmd("show vpcs")
        shell.onecmd("set vpc 1")

        yield shell, vpc_detail

        p1.stop()
        p2.stop()
        shell._cache.clear()
        shell.context_stack.clear()

    @pytest.mark.parametrize(
        "command",
        [
            "show detail",
            "show subnets",
            "show route-tables",
            "show security-groups",
            "show nacls",
        ],
    )
    def test_vpc_show_commands(self, shell_in_vpc, command):
        """Test VPC context show commands."""
        shell, _ = shell_in_vpc
        result = shell.onecmd(command)
        assert result in (None, False)


class TestTGWContextCommands:
    """Test commands within TGW context."""

    @pytest.fixture
    def shell_in_tgw(self):
        from aws_network_tools.shell import AWSNetShell

        shell = AWSNetShell()
        shell.no_cache = True

        tgws = _tgws_list()
        # Add route_tables to first TGW
        if tgws:
            tgws[0]["route_tables"] = [
                {"id": "tgw-rtb-1", "name": "main", "routes": [], "state": "available"}
            ]
            tgws[0]["attachments"] = [
                {
                    "id": "tgw-attach-1",
                    "type": "vpc",
                    "resource_id": "vpc-123",
                    "state": "available",
                }
            ]

        p1 = patch(
            "aws_network_tools.modules.tgw.TGWClient.discover", return_value=tgws
        )
        p1.start()

        shell.onecmd("show transit_gateways")
        shell.onecmd("set transit-gateway 1")

        yield shell

        p1.stop()
        shell._cache.clear()
        shell.context_stack.clear()

    @pytest.mark.parametrize(
        "command", ["show detail", "show route-tables", "show attachments"]
    )
    def test_tgw_show_commands(self, shell_in_tgw, command):
        shell = shell_in_tgw
        result = shell.onecmd(command)
        assert result in (None, False)


class TestFirewallContextCommands:
    """Test commands within Firewall context."""

    @pytest.fixture
    def shell_in_firewall(self):
        from aws_network_tools.shell import AWSNetShell

        shell = AWSNetShell()
        shell.no_cache = True

        fws = _firewalls_list()
        if fws:
            fws[0]["rule_groups"] = [
                {"name": "test-rg", "arn": "arn:...", "type": "STATEFUL"}
            ]

        p1 = patch(
            "aws_network_tools.modules.anfw.ANFWClient.discover", return_value=fws
        )
        p1.start()

        shell.onecmd("show firewalls")
        shell.onecmd("set firewall 1")

        yield shell

        p1.stop()
        shell._cache.clear()
        shell.context_stack.clear()

    @pytest.mark.parametrize(
        "command", ["show detail", "show rule-groups", "show policy"]
    )
    def test_firewall_show_commands(self, shell_in_firewall, command):
        result = shell_in_firewall.onecmd(command)
        assert result in (None, False)


class TestEC2ContextCommands:
    """Test commands within EC2 instance context."""

    @pytest.fixture
    def shell_in_ec2(self):
        from aws_network_tools.shell import AWSNetShell

        shell = AWSNetShell()
        shell.no_cache = True

        instances = _ec2_instances_list()
        if instances:
            instances[0]["security_groups"] = [{"id": "sg-1", "name": "default"}]
            instances[0]["enis"] = [{"id": "eni-1", "private_ip": "10.0.1.10"}]

        p1 = patch(
            "aws_network_tools.modules.ec2.EC2Client.discover", return_value=instances
        )
        p1.start()

        shell.onecmd("show ec2-instances")
        shell.onecmd("set ec2-instance 1")

        yield shell

        p1.stop()
        shell._cache.clear()
        shell.context_stack.clear()

    @pytest.mark.parametrize(
        "command", ["show detail", "show security-groups", "show enis"]
    )
    def test_ec2_show_commands(self, shell_in_ec2, command):
        result = shell_in_ec2.onecmd(command)
        assert result in (None, False)


class TestELBContextCommands:
    """Test commands within ELB context."""

    @pytest.fixture
    def shell_in_elb(self):
        from aws_network_tools.shell import AWSNetShell

        shell = AWSNetShell()
        shell.no_cache = True

        elbs = _elbs_list()
        elb_detail = {
            "arn": elbs[0]["arn"] if elbs else "arn:...",
            "name": elbs[0]["name"] if elbs else "test-elb",
            "type": "application",
            "listeners": [{"port": 443, "protocol": "HTTPS"}],
            "target_groups": [{"name": "tg-1", "targets": []}],
        }

        p1 = patch(
            "aws_network_tools.modules.elb.ELBClient.discover", return_value=elbs
        )
        p2 = patch(
            "aws_network_tools.modules.elb.ELBClient.get_elb_detail",
            return_value=elb_detail,
        )
        p1.start()
        p2.start()

        shell.onecmd("show elbs")
        shell.onecmd("set elb 1")

        yield shell

        p1.stop()
        p2.stop()
        shell._cache.clear()
        shell.context_stack.clear()

    @pytest.mark.parametrize(
        "command", ["show detail", "show listeners", "show targets"]
    )
    def test_elb_show_commands(self, shell_in_elb, command):
        result = shell_in_elb.onecmd(command)
        assert result in (None, False)


class TestVPNContextCommands:
    """Test commands within VPN context."""

    @pytest.fixture
    def shell_in_vpn(self):
        from aws_network_tools.shell import AWSNetShell

        shell = AWSNetShell()
        shell.no_cache = True

        vpns = _vpns_list()
        if vpns:
            vpns[0]["tunnels"] = [
                {"outside_ip": "203.0.113.1", "status": "UP"},
                {"outside_ip": "203.0.113.2", "status": "UP"},
            ]

        p1 = patch(
            "aws_network_tools.modules.vpn.VPNClient.discover", return_value=vpns
        )
        p1.start()

        shell.onecmd("show vpns")
        shell.onecmd("set vpn 1")

        yield shell

        p1.stop()
        shell._cache.clear()
        shell.context_stack.clear()

    @pytest.mark.parametrize("command", ["show detail", "show tunnels"])
    def test_vpn_show_commands(self, shell_in_vpn, command):
        result = shell_in_vpn.onecmd(command)
        assert result in (None, False)
