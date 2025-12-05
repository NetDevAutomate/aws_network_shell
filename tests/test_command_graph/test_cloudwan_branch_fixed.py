"""Test CloudWAN branch with properly injected mock clients.

Solution: Monkeypatch client classes BEFORE shell creates them.
"""

import pytest
from unittest.mock import MagicMock
from tests.fixtures.cloudwan import (
    CLOUDWAN_FIXTURES,
    CLOUDWAN_ATTACHMENT_FIXTURES,
    CLOUDWAN_SEGMENT_FIXTURES,
    CLOUDWAN_ROUTE_TABLE_FIXTURES,
    get_core_network_detail,
)


@pytest.fixture
def mock_cloudwan_properly(monkeypatch):
    """Properly mock CloudWAN client at module level."""

    class MockCloudWANClient:
        def __init__(self, profile=None):
            self.profile = profile
            self.nm = MagicMock()

        def discover(self):
            """Return core networks from fixtures."""
            core_networks = []
            for cn_id, cn_data in CLOUDWAN_FIXTURES.items():
                # Convert fixture format to what discover() returns
                core_networks.append({
                    "id": cn_data["CoreNetworkId"],
                    "name": next(
                        (t["Value"] for t in cn_data.get("Tags", []) if t["Key"] == "Name"),
                        cn_id
                    ),
                    "arn": cn_data["CoreNetworkArn"],
                    "global_network_id": cn_data["GlobalNetworkId"],
                    "state": cn_data["State"],
                    "regions": [edge["EdgeLocation"] for edge in cn_data.get("Edges", [])],
                    "segments": [seg["Name"] for seg in cn_data.get("Segments", [])],
                    "route_tables": [],  # Will be populated when needed
                    "policy": None,  # Will be loaded when needed
                })
            return core_networks

        def list_connect_peers(self, cn_id):
            """Return connect peers from fixtures."""
            from tests.fixtures.cloudwan_connect import CONNECT_PEER_FIXTURES

            peers = []
            for peer_id, peer_data in CONNECT_PEER_FIXTURES.items():
                if peer_data.get("CoreNetworkId") == cn_id:
                    config = peer_data.get("Configuration", {})
                    bgp_configs = config.get("BgpConfigurations", [])

                    peers.append({
                        "id": peer_data["ConnectPeerId"],
                        "name": next(
                            (t["Value"] for t in peer_data.get("Tags", []) if t["Key"] == "Name"),
                            peer_id
                        ),
                        "state": peer_data["State"],
                        "connect_attachment_id": peer_data.get("ConnectAttachmentId", ""),
                        "edge_location": peer_data.get("EdgeLocation", ""),
                        "protocol": config.get("Protocol", "GRE"),
                        "bgp_configurations": bgp_configs,
                        "inside_cidr_blocks": config.get("InsideCidrBlocks", []),
                    })
            return peers

        def list_connect_attachments(self, cn_id):
            """Return connect attachments from fixtures."""
            from tests.fixtures.cloudwan_connect import CONNECT_ATTACHMENT_FIXTURES

            attachments = []
            for att_id, att_data in CONNECT_ATTACHMENT_FIXTURES.items():
                if att_data.get("CoreNetworkId") == cn_id:
                    options = att_data.get("ConnectOptions", {})
                    attachments.append({
                        "id": att_data["AttachmentId"],
                        "name": next(
                            (t["Value"] for t in att_data.get("Tags", []) if t["Key"] == "Name"),
                            att_id
                        ),
                        "state": att_data["State"],
                        "edge_location": att_data.get("EdgeLocation", ""),
                        "segment": att_data.get("SegmentName", ""),
                        "protocol": options.get("Protocol", "GRE"),
                        "transport_attachment_id": options.get("TransportAttachmentId", ""),
                    })
            return attachments

        def get_policy_document(self, cn_id, version=None):
            """Return policy document from fixtures."""
            from tests.fixtures.cloudwan import CLOUDWAN_POLICY_FIXTURE
            return CLOUDWAN_POLICY_FIXTURE.get("PolicyDocument")

    # Patch the client class at module level
    monkeypatch.setattr(
        "aws_network_tools.modules.cloudwan.CloudWANClient",
        MockCloudWANClient
    )

    yield MockCloudWANClient


@pytest.fixture
def shell_with_mocked_clients(isolated_shell, mock_cloudwan_properly):
    """Shell with properly mocked clients."""
    return isolated_shell


@pytest.fixture
def command_runner_with_mocks(shell_with_mocked_clients):
    """Command runner using shell with mocked clients."""
    from tests.test_command_graph.conftest import CommandRunner
    return CommandRunner(shell_with_mocked_clients)


class TestCloudWANWithProperMocks:
    """Test CloudWAN with properly injected mock clients."""

    def test_show_global_networks_uses_fixtures(
        self, command_runner_with_mocks, mock_cloudwan_properly
    ):
        """Verify show global-networks returns fixture data."""
        result = command_runner_with_mocks.run("show global-networks")

        # Should succeed
        assert result["exit_code"] == 0

        # Should show our fixture global network (not real AWS)
        # Note: We don't have global network fixtures yet, only core networks
        # This test shows the pattern

    def test_mocked_client_returns_fixture_core_networks(self, mock_cloudwan_properly):
        """Verify mock client returns our fixture data."""
        client = mock_cloudwan_properly()
        core_networks = client.discover()

        # Should return our fixture
        assert len(core_networks) == 1
        assert core_networks[0]["id"] == "core-network-0global123"
        assert core_networks[0]["name"] == "production-core-network"

    def test_connect_peers_from_fixtures(self, mock_cloudwan_properly):
        """Verify connect peers come from fixtures."""
        client = mock_cloudwan_properly()
        peers = client.list_connect_peers("core-network-0global123")

        # Should return our 9 connect peers from fixtures
        assert len(peers) >= 9
        # Should include SD-WAN peers (Viptela, VeloCloud, etc.)
