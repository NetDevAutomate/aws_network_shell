"""Tests for IP Resolver"""

import pytest
from unittest.mock import MagicMock, patch
from aws_network_tools.core.ip_resolver import IpResolver


class TestIpResolver:
    @pytest.fixture
    def resolver(self):
        with patch("boto3.Session"):
            return IpResolver()

    def test_resolve_private_ip_found(self, resolver):
        mock_ec2 = MagicMock()
        resolver.session.client.return_value = mock_ec2

        # Mock successful find in first region
        mock_ec2.describe_network_interfaces.side_effect = [
            {
                "NetworkInterfaces": [{"NetworkInterfaceId": "eni-123"}]
            },  # Private IP match
        ]

        eni_id = resolver.resolve_ip("10.0.0.1", ["us-east-1"])
        assert eni_id == "eni-123"

    def test_resolve_public_ip_found(self, resolver):
        mock_ec2 = MagicMock()
        resolver.session.client.return_value = mock_ec2

        # Mock fail private, success public
        mock_ec2.describe_network_interfaces.side_effect = [
            {"NetworkInterfaces": []},  # Private IP fail
            {
                "NetworkInterfaces": [{"NetworkInterfaceId": "eni-456"}]
            },  # Public IP match
        ]

        eni_id = resolver.resolve_ip("1.2.3.4", ["us-east-1"])
        assert eni_id == "eni-456"

    def test_resolve_ip_not_found(self, resolver):
        mock_ec2 = MagicMock()
        resolver.session.client.return_value = mock_ec2

        # Mock fail both
        mock_ec2.describe_network_interfaces.return_value = {"NetworkInterfaces": []}

        eni_id = resolver.resolve_ip("10.0.0.1", ["us-east-1"])
        assert eni_id is None
