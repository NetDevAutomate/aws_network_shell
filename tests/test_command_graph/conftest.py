"""Comprehensive fixtures and mocks for command graph testing.

This module provides:
1. Isolated shell instances per test
2. Mocked boto3 clients with fixture data
3. Helper functions for command execution
4. Binary pass/fail assertion helpers
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from io import StringIO
from rich.console import Console

# Import fixtures from main fixtures module
from tests.fixtures import (
    GLOBAL_NETWORK_FIXTURES,
    VPC_FIXTURES,
    SUBNET_FIXTURES,
    ROUTE_TABLE_FIXTURES,
    SECURITY_GROUP_FIXTURES,
    NACL_FIXTURES,
    TGW_FIXTURES,
    TGW_ATTACHMENT_FIXTURES,
    TGW_ROUTE_TABLE_FIXTURES,
    CLOUDWAN_FIXTURES,
    CLOUDWAN_ATTACHMENT_FIXTURES,
    CLOUDWAN_SEGMENT_FIXTURES,
    EC2_INSTANCE_FIXTURES,
    ENI_FIXTURES,
    ELB_FIXTURES,
    TARGET_GROUP_FIXTURES,
    LISTENER_FIXTURES,
    VPN_CONNECTION_FIXTURES,
    CUSTOMER_GATEWAY_FIXTURES,
    VPN_GATEWAY_FIXTURES,
    NETWORK_FIREWALL_FIXTURES,
    FIREWALL_POLICY_FIXTURES,
    RULE_GROUP_FIXTURES,
    IGW_FIXTURES,
    NAT_GATEWAY_FIXTURES,
    get_global_network_by_id,
    get_vpc_detail,
    get_tgw_detail,
    get_core_network_detail,
    get_elb_detail,
    get_vpn_detail,
    get_firewall_detail,
)


@pytest.fixture
def mock_console():
    """Create a mock console that captures output."""
    output = StringIO()
    console = Console(file=output, force_terminal=True, width=120, no_color=True)
    console._output = output
    return console


@pytest.fixture
def isolated_shell():
    """Provide isolated shell instance per test with no caching."""
    from aws_network_tools.shell.main import AWSNetShell

    shell = AWSNetShell()
    shell.no_cache = True
    shell.output_format = "table"
    yield shell
    # Cleanup
    shell._cache.clear()
    shell.context_stack.clear()


@pytest.fixture
def command_runner(isolated_shell):
    """Provide a helper to run commands and capture output."""

    class CommandRunner:
        def __init__(self, shell):
            self.shell = shell
            self.last_output = None
            self.last_exit_code = None

        def run(self, command: str) -> dict:
            """Run a command and return result with exit_code and output."""
            output = StringIO()
            temp_console = Console(file=output, force_terminal=False, no_color=True)

            # Patch all console instances in shell modules
            patches = []
            try:
                # Patch main console
                patch_main = patch("aws_network_tools.shell.main.console", temp_console)
                patches.append(patch_main)
                patch_main.start()

                # Patch root handler console
                patch_root = patch(
                    "aws_network_tools.shell.handlers.root.console", temp_console
                )
                patches.append(patch_root)
                patch_root.start()

                # Execute command
                result = self.shell.onecmd(command)
                self.last_exit_code = 1 if result else 0
                self.last_output = output.getvalue()

                return {
                    "exit_code": self.last_exit_code,
                    "output": self.last_output,
                    "success": self.last_exit_code == 0,
                }
            except Exception as e:
                self.last_exit_code = 1
                self.last_output = str(e)
                return {
                    "exit_code": 1,
                    "output": self.last_output,
                    "success": False,
                    "error": e,
                }
            finally:
                # Stop all patches
                for p in patches:
                    try:
                        p.stop()
                    except Exception:
                        pass

        def run_chain(self, commands: list[str]) -> list[dict]:
            """Run a chain of commands and return results."""
            results = []
            for cmd in commands:
                result = self.run(cmd)
                results.append(result)
                if not result["success"]:
                    break  # Stop on first failure
            return results

    return CommandRunner(isolated_shell)


@pytest.fixture
def mock_vpc_client():
    """Mock VPC client returning fixture data."""

    class MockVPCClient:
        def __init__(self, profile=None):
            self.profile = profile

        def discover(self):
            """Return all VPCs as list."""
            vpcs = []
            for vpc_id, vpc_data in VPC_FIXTURES.items():
                vpcs.append(
                    {
                        "id": vpc_data["VpcId"],
                        "name": next(
                            (
                                t["Value"]
                                for t in vpc_data.get("Tags", [])
                                if t["Key"] == "Name"
                            ),
                            vpc_id,
                        ),
                        "cidr": vpc_data["CidrBlock"],
                        "cidrs": [
                            assoc["CidrBlock"]
                            for assoc in vpc_data.get("CidrBlockAssociationSet", [])
                        ],
                        "region": self._get_region_from_id(vpc_id),
                        "state": vpc_data["State"],
                    }
                )
            return vpcs

        def get_vpc_detail(self, vpc_id, region=None):
            """Return detailed VPC information."""
            return get_vpc_detail(vpc_id)

        def _get_region_from_id(self, vpc_id: str) -> str:
            """Extract region from VPC ID pattern."""
            if "prod" in vpc_id:
                return "eu-west-1"
            elif "stag" in vpc_id:
                return "us-east-1"
            elif "dev" in vpc_id:
                return "ap-southeast-2"
            return "us-east-1"

    return MockVPCClient


@pytest.fixture
def mock_tgw_client():
    """Mock Transit Gateway client returning fixture data."""

    class MockTGWClient:
        def __init__(self, profile=None):
            self.profile = profile

        def discover(self):
            """Return all Transit Gateways as list."""
            tgws = []
            for tgw_id, tgw_data in TGW_FIXTURES.items():
                tgws.append(
                    {
                        "id": tgw_data["TransitGatewayId"],
                        "name": next(
                            (
                                t["Value"]
                                for t in tgw_data.get("Tags", [])
                                if t["Key"] == "Name"
                            ),
                            tgw_id,
                        ),
                        "region": self._get_region_from_id(tgw_id),
                        "state": tgw_data["State"],
                        "route_tables": [],
                        "attachments": [],
                    }
                )
            return tgws

        def _get_region_from_id(self, tgw_id: str) -> str:
            """Extract region from TGW ID pattern."""
            if "prod" in tgw_id:
                return "eu-west-1"
            return "us-east-1"

    return MockTGWClient


@pytest.fixture
def mock_cloudwan_client():
    """Mock CloudWAN client returning fixture data."""

    class MockCloudWANClient:
        def __init__(self, profile=None):
            self.profile = profile
            self.nm = MagicMock()
            self._setup_nm_client()

        def _setup_nm_client(self):
            """Setup nm client to return fixture data."""
            # Mock describe_global_networks - return ALL global networks from fixtures
            def mock_describe_global_networks():
                return {"GlobalNetworks": list(GLOBAL_NETWORK_FIXTURES.values())}

            self.nm.describe_global_networks = mock_describe_global_networks

        def discover(self):
            """Return all Core Networks as list (format expected by cloudwan module)."""
            core_networks = []
            for cn_id, cn_data in CLOUDWAN_FIXTURES.items():
                # Format matches what CloudWANClient.discover() returns
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
                    "segments": [seg for seg in cn_data.get("Segments", [])],
                    "route_tables": [],
                    "policy": None,
                    "core_networks": [],  # For compatibility
                })
            return core_networks

        def list_connect_peers(self, cn_id):
            """Return connect peers from fixtures."""
            from tests.fixtures.cloudwan_connect import CONNECT_PEER_FIXTURES

            peers = []
            for peer_id, peer_data in CONNECT_PEER_FIXTURES.items():
                if peer_data.get("CoreNetworkId") == cn_id:
                    config = peer_data.get("Configuration", {})
                    peers.append({
                        "id": peer_data["ConnectPeerId"],
                        "name": next(
                            (t["Value"] for t in peer_data.get("Tags", []) if t["Key"] == "Name"),
                            peer_id
                        ),
                        "state": peer_data["State"],
                        "edge_location": peer_data.get("EdgeLocation", ""),
                        "protocol": config.get("Protocol", "GRE"),
                        "bgp_configurations": config.get("BgpConfigurations", []),
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
                    })
            return attachments

        def get_core_network_detail(self, cn_id):
            """Return detailed core network info (per Nova Premier).

            This is CRITICAL for context entry - cloudwan module calls this
            to get full detail before entering context.
            """
            from tests.fixtures.cloudwan import get_core_network_detail
            return get_core_network_detail(cn_id)

        def get_policy_document(self, cn_id):
            """Return policy document for core network.

            Handler calls this to get policy when entering context.
            """
            cn_data = CLOUDWAN_FIXTURES.get(cn_id)
            if not cn_data:
                return None
            # Return the policy from fixture
            return cn_data.get("Policy", {})

    return MockCloudWANClient


@pytest.fixture
def mock_ec2_client():
    """Mock EC2 client returning fixture data."""

    class MockEC2Client:
        def __init__(self, profile=None):
            self.profile = profile

        def discover(self):
            """Return all EC2 instances as list."""
            instances = []
            for instance_id, instance_data in EC2_INSTANCE_FIXTURES.items():
                instances.append(
                    {
                        "id": instance_data["InstanceId"],
                        "name": next(
                            (
                                t["Value"]
                                for t in instance_data.get("Tags", [])
                                if t["Key"] == "Name"
                            ),
                            instance_id,
                        ),
                        "type": instance_data["InstanceType"],
                        "state": instance_data["State"]["Name"],
                        "az": instance_data["Placement"]["AvailabilityZone"],
                        "region": instance_data["Placement"]["AvailabilityZone"][:-1],
                        "vpc_id": instance_data["VpcId"],
                        "subnet_id": instance_data["SubnetId"],
                        "private_ip": instance_data["PrivateIpAddress"],
                    }
                )
            return instances

    return MockEC2Client


@pytest.fixture
def mock_elb_client():
    """Mock ELB client returning fixture data."""

    class MockELBClient:
        def __init__(self, profile=None):
            self.profile = profile

        def discover(self):
            """Return all ELBs as list."""
            elbs = []
            for elb_arn, elb_data in ELB_FIXTURES.items():
                elbs.append(
                    {
                        "arn": elb_data["LoadBalancerArn"],
                        "name": elb_data["LoadBalancerName"],
                        "type": elb_data["Type"],
                        "scheme": elb_data["Scheme"],
                        "state": elb_data["State"]["Code"],
                        "vpc_id": elb_data["VpcId"],
                        "dns_name": elb_data["DNSName"],
                        "region": self._get_region_from_arn(elb_arn),
                    }
                )
            return elbs

        def _get_region_from_arn(self, arn: str) -> str:
            """Extract region from ARN."""
            parts = arn.split(":")
            return parts[3] if len(parts) > 3 else "us-east-1"

    return MockELBClient


@pytest.fixture
def mock_vpn_client():
    """Mock VPN client returning fixture data."""

    class MockVPNClient:
        def __init__(self, profile=None):
            self.profile = profile

        def discover(self):
            """Return all VPN connections as list."""
            vpns = []
            for vpn_id, vpn_data in VPN_CONNECTION_FIXTURES.items():
                vpns.append(
                    {
                        "id": vpn_data["VpnConnectionId"],
                        "name": next(
                            (
                                t["Value"]
                                for t in vpn_data.get("Tags", [])
                                if t["Key"] == "Name"
                            ),
                            vpn_id,
                        ),
                        "state": vpn_data["State"],
                        "type": vpn_data["Type"],
                        "category": vpn_data.get("Category", "VPN"),
                    }
                )
            return vpns

    return MockVPNClient


@pytest.fixture
def mock_firewall_client():
    """Mock Network Firewall client returning fixture data."""

    class MockANFWClient:
        def __init__(self, profile=None):
            self.profile = profile

        def discover(self):
            """Return all firewalls as list."""
            firewalls = []
            for fw_name, fw_data in NETWORK_FIREWALL_FIXTURES.items():
                firewalls.append(
                    {
                        "name": fw_data["FirewallName"],
                        "arn": fw_data["FirewallArn"],
                        "region": self._get_region_from_arn(fw_data["FirewallArn"]),
                        "vpc_id": fw_data["VpcId"],
                    }
                )
            return firewalls

        def _get_region_from_arn(self, arn: str) -> str:
            """Extract region from ARN."""
            parts = arn.split(":")
            return parts[3] if len(parts) > 3 else "us-east-1"

    return MockANFWClient


@pytest.fixture(autouse=True)
def mock_all_clients(
    monkeypatch,
    mock_vpc_client,
    mock_tgw_client,
    mock_cloudwan_client,
    mock_ec2_client,
    mock_elb_client,
    mock_vpn_client,
    mock_firewall_client,
):
    """AUTOMATICALLY mock all AWS clients for every test.

    This is the CRITICAL fixture that makes all tests work!
    Uses monkeypatch to inject mock clients at module level.
    """
    # Patch all client classes at module level
    monkeypatch.setattr("aws_network_tools.modules.vpc.VPCClient", mock_vpc_client)
    monkeypatch.setattr("aws_network_tools.modules.tgw.TGWClient", mock_tgw_client)
    monkeypatch.setattr("aws_network_tools.modules.cloudwan.CloudWANClient", mock_cloudwan_client)
    monkeypatch.setattr("aws_network_tools.modules.ec2.EC2Client", mock_ec2_client)
    monkeypatch.setattr("aws_network_tools.modules.elb.ELBClient", mock_elb_client)
    monkeypatch.setattr("aws_network_tools.modules.vpn.VPNClient", mock_vpn_client)
    monkeypatch.setattr("aws_network_tools.modules.anfw.ANFWClient", mock_firewall_client)

    yield


# =============================================================================
# Helper Functions
# =============================================================================


def assert_success(result: dict, message: str = "Command should succeed"):
    """Assert command succeeded (binary pass)."""
    assert result["exit_code"] == 0, f"{message}: {result.get('output', '')}"


def assert_failure(result: dict, message: str = "Command should fail"):
    """Assert command failed (binary fail)."""
    assert result["exit_code"] != 0, f"{message}: {result.get('output', '')}"


def assert_output_contains(result: dict, text: str):
    """Assert output contains specific text (data validation)."""
    assert text in result["output"], f"Expected '{text}' in output:\n{result['output']}"


def assert_output_not_contains(result: dict, text: str):
    """Assert output does not contain specific text."""
    assert (
        text not in result["output"]
    ), f"Did not expect '{text}' in output:\n{result['output']}"


def assert_context_type(shell, expected_ctx_type: str):
    """Assert shell is in expected context."""
    assert (
        shell.ctx_type == expected_ctx_type
    ), f"Expected context '{expected_ctx_type}', got '{shell.ctx_type}'"


def assert_context_stack_depth(shell, expected_depth: int):
    """Assert context stack has expected depth."""
    actual_depth = len(shell.context_stack)
    assert (
        actual_depth == expected_depth
    ), f"Expected stack depth {expected_depth}, got {actual_depth}"
