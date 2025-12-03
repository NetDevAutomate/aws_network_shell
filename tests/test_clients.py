"""Tests for AWS client modules"""

import pytest
from unittest.mock import patch, MagicMock
from aws_network_tools.modules.vpc import VPCClient
from aws_network_tools.modules.tgw import TGWClient
from aws_network_tools.modules.cloudwan import CloudWANClient
from aws_network_tools.modules.anfw import ANFWClient


class TestVPCClient:
    @pytest.fixture
    def mock_ec2(self):
        with patch("boto3.Session") as mock_session:
            mock_client = MagicMock()
            mock_session.return_value.client.return_value = mock_client
            mock_session.return_value.get_available_regions.return_value = ["eu-west-1"]
            yield mock_client

    def test_init_default(self, mock_ec2):
        client = VPCClient()
        assert client.session is not None

    def test_init_with_profile(self, mock_ec2):
        client = VPCClient(profile="test-profile")
        assert client.session is not None

    def test_discover_returns_list(self, mock_ec2):
        mock_ec2.describe_vpcs.return_value = {
            "Vpcs": [
                {
                    "VpcId": "vpc-123",
                    "CidrBlock": "10.0.0.0/16",
                    "State": "available",
                    "Tags": [{"Key": "Name", "Value": "test-vpc"}],
                }
            ]
        }
        client = VPCClient()
        result = client.discover()
        assert isinstance(result, list)

    def test_get_vpc_detail(self, mock_ec2):
        mock_ec2.describe_route_tables.return_value = {"RouteTables": []}
        mock_ec2.describe_security_groups.return_value = {"SecurityGroups": []}
        mock_ec2.describe_network_acls.return_value = {"NetworkAcls": []}
        mock_ec2.describe_vpcs.return_value = {
            "Vpcs": [{"VpcId": "vpc-123", "CidrBlock": "10.0.0.0/16", "Tags": []}]
        }

        client = VPCClient()
        result = client.get_vpc_detail("vpc-123", "eu-west-1")
        assert result["id"] == "vpc-123"


class TestTGWClient:
    @pytest.fixture
    def mock_ec2(self):
        with patch("boto3.Session") as mock_session:
            mock_client = MagicMock()
            mock_session.return_value.client.return_value = mock_client
            mock_session.return_value.get_available_regions.return_value = ["eu-west-1"]
            yield mock_client

    def test_init(self, mock_ec2):
        client = TGWClient()
        assert client.session is not None

    def test_discover_returns_list(self, mock_ec2):
        mock_ec2.describe_transit_gateways.return_value = {
            "TransitGateways": [
                {
                    "TransitGatewayId": "tgw-123",
                    "State": "available",
                    "Tags": [{"Key": "Name", "Value": "test-tgw"}],
                }
            ]
        }
        mock_ec2.describe_transit_gateway_route_tables.return_value = {
            "TransitGatewayRouteTables": []
        }
        client = TGWClient()
        result = client.discover()
        assert isinstance(result, list)


class TestCloudWANClient:
    @pytest.fixture
    def mock_nm(self):
        with patch("boto3.Session") as mock_session:
            mock_client = MagicMock()
            mock_session.return_value.client.return_value = mock_client
            yield mock_client

    def test_init(self, mock_nm):
        client = CloudWANClient()
        assert client.session is not None

    def test_list_policy_versions(self, mock_nm):
        mock_nm.list_core_network_policy_versions.return_value = {
            "CoreNetworkPolicyVersions": [
                {
                    "PolicyVersionId": 5,
                    "Alias": "LIVE",
                    "ChangeSetState": "EXECUTED",
                    "CreatedAt": "2024-01-01",
                },
                {
                    "PolicyVersionId": 4,
                    "Alias": "",
                    "ChangeSetState": "EXECUTED",
                    "CreatedAt": "2024-01-01",
                },
            ]
        }
        client = CloudWANClient()
        result = client.list_policy_versions("cn-123")
        assert len(result) == 2
        assert result[0]["version"] == 5
        assert result[0]["alias"] == "LIVE"

    def test_get_policy_document(self, mock_nm):
        mock_nm.list_core_network_policy_versions.return_value = {
            "CoreNetworkPolicyVersions": [
                {"PolicyVersionId": 5, "Alias": "LIVE"},
            ]
        }
        mock_nm.get_core_network_policy.return_value = {
            "CoreNetworkPolicy": {"PolicyDocument": '{"version": "2021.12"}'}
        }
        client = CloudWANClient()
        result = client.get_policy_document("cn-123")
        assert result == {"version": "2021.12"}

    def test_get_policy_document_specific_version(self, mock_nm):
        mock_nm.get_core_network_policy.return_value = {
            "CoreNetworkPolicy": {"PolicyDocument": '{"version": "2021.12"}'}
        }
        client = CloudWANClient()
        result = client.get_policy_document("cn-123", version=4)
        assert result == {"version": "2021.12"}

    def test_discover_returns_list(self, mock_nm):
        mock_nm.describe_global_networks.return_value = {"GlobalNetworks": []}
        client = CloudWANClient()
        result = client.discover()
        assert isinstance(result, list)


class TestANFWClient:
    @pytest.fixture
    def mock_nfw(self):
        with patch("boto3.Session") as mock_session:
            mock_client = MagicMock()
            mock_session.return_value.client.return_value = mock_client
            mock_session.return_value.get_available_regions.return_value = ["eu-west-1"]
            yield mock_client

    def test_init(self, mock_nfw):
        client = ANFWClient()
        assert client.session is not None

    def test_discover_returns_list(self, mock_nfw):
        mock_nfw.list_firewalls.return_value = {"Firewalls": []}
        client = ANFWClient()
        result = client.discover()
        assert isinstance(result, list)
