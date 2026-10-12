"""VPN tunnel display tests (Issue #6).

Validates that:
1. Entering a VPN context loads tunnel telemetry through VPNClient.get_vpn_detail
2. Each tunnel carries outside_ip, status, status_message, accepted_routes
3. `show tunnels` and `show detail` render UP and DOWN tunnels

boto3 is mocked at the Session boundary, so the real get_vpn_detail()
extraction code runs against tests/fixtures/vpn.py, where the first VPN has
two UP tunnels and the second has one UP and one DOWN.
"""

from unittest.mock import MagicMock, patch

import pytest

from aws_network_tools.shell.main import AWSNetShell
from tests.fixtures import VPN_CONNECTION_FIXTURES
from tests.fixtures.command_fixtures import _vpns_list

REQUIRED_TUNNEL_FIELDS = ("outside_ip", "status", "status_message", "accepted_routes")


def _fake_ec2_client(*_args, **_kwargs) -> MagicMock:
    """EC2 client whose describe_vpn_connections answers from the fixtures."""

    def describe_vpn_connections(VpnConnectionIds=None, **_):
        return {
            "VpnConnections": [
                VPN_CONNECTION_FIXTURES[v]
                for v in VpnConnectionIds or []
                if v in VPN_CONNECTION_FIXTURES
            ]
        }

    client = MagicMock()
    client.describe_vpn_connections.side_effect = describe_vpn_connections
    return client


@pytest.fixture
def shell(capsys):
    """Shell with VPN discovery and the boto3 session mocked."""
    session = MagicMock()
    session.region_name = "eu-west-1"
    session.client.side_effect = _fake_ec2_client

    with (
        patch("aws_network_tools.core.base.boto3.Session", return_value=session),
        patch(
            "aws_network_tools.modules.vpn.VPNClient.discover",
            return_value=_vpns_list(),
        ),
    ):
        s = AWSNetShell()
        s.no_cache = True
        s.onecmd("show vpns")
        capsys.readouterr()  # discard the listing
        yield s
        s.context_stack.clear()


def _enter_vpn(shell, index: int):
    shell.onecmd(f"set vpn {index}")
    assert shell.ctx_type == "vpn", "set vpn must enter the vpn context"
    return shell.ctx.data["tunnels"]


def test_vpn_tunnel_data_extraction(shell):
    """Context entry maps VgwTelemetry into tunnel dicts with the required fields."""
    tunnels = _enter_vpn(shell, 1)

    assert isinstance(tunnels, list)
    assert len(tunnels) == 2
    for tunnel in tunnels:
        for field in REQUIRED_TUNNEL_FIELDS:
            assert field in tunnel, f"Tunnel missing required field: {field}"
    assert tunnels[0]["outside_ip"] == "52.31.200.10"
    assert tunnels[0]["accepted_routes"] == 2


def test_tunnel_status_for_up_and_down(shell):
    """VPN 1 is fully UP; VPN 2 has a DOWN tunnel (per fixtures)."""
    up_tunnels = _enter_vpn(shell, 1)
    assert {t["status"] for t in up_tunnels} == {"UP"}

    shell.onecmd("exit")
    assert shell.ctx is None

    mixed_tunnels = _enter_vpn(shell, 2)
    assert {t["status"] for t in mixed_tunnels} == {"UP", "DOWN"}


def test_show_tunnels_renders_each_tunnel(shell, capsys):
    """show tunnels prints one row per tunnel with IP and status."""
    _enter_vpn(shell, 2)
    shell.onecmd("show tunnels")
    out = capsys.readouterr().out

    assert "VPN Tunnels" in out
    assert "52.31.201.20" in out
    assert "52.31.201.21" in out
    assert "UP" in out
    assert "DOWN" in out


def test_show_detail_includes_tunnel_summary(shell, capsys):
    """show detail prints the tunnel count and each tunnel's status/IP."""
    _enter_vpn(shell, 1)
    shell.onecmd("show detail")
    out = capsys.readouterr().out

    assert "Tunnels (2)" in out
    assert "52.31.200.10" in out
    assert "52.31.200.11" in out
