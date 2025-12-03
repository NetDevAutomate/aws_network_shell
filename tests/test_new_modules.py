"""Tests for new modules: ENI, Reachability, FlowLogs, VPN"""

import pytest
from unittest.mock import MagicMock, patch
from aws_network_tools.modules.eni import ENIClient
from aws_network_tools.modules.reachability import ReachabilityClient
from aws_network_tools.modules.flowlogs import FlowLogsClient
from aws_network_tools.modules.vpn import VPNClient


class TestENIClient:
    @pytest.fixture
    def client(self):
        with patch("boto3.Session"):
            return ENIClient()

    def test_discover_enis(self, client):
        # Mock ec2 client and paginator
        mock_ec2 = MagicMock()
        client.session.client.return_value = mock_ec2

        paginator = MagicMock()
        mock_ec2.get_paginator.return_value = paginator

        paginator.paginate.return_value = [
            {
                "NetworkInterfaces": [
                    {
                        "NetworkInterfaceId": "eni-123",
                        "Status": "in-use",
                        "InterfaceType": "interface",
                        "SubnetId": "subnet-1",
                        "VpcId": "vpc-1",
                        "TagSet": [{"Key": "Name", "Value": "test-eni"}],
                        "Attachment": {"InstanceId": "i-123"},
                        "Groups": [],
                    }
                ]
            }
        ]

        results = client.discover(["us-east-1"])
        assert len(results) == 1
        assert results[0]["id"] == "eni-123"
        assert results[0]["name"] == "test-eni"
        assert "Instance: i-123" in results[0]["attached_to"]


class TestReachabilityClient:
    @pytest.fixture
    def client(self):
        with patch("boto3.Session"):
            return ReachabilityClient()

    def test_create_path(self, client):
        mock_ec2 = MagicMock()
        client.session.client.return_value = mock_ec2

        mock_ec2.create_network_insights_path.return_value = {
            "NetworkInsightsPath": {"NetworkInsightsPathId": "nip-123"}
        }

        path_id = client.create_path("src", "dst", "tcp", 80)
        assert path_id == "nip-123"
        mock_ec2.create_network_insights_path.assert_called_once()

    def test_create_path_failure(self, client):
        mock_ec2 = MagicMock()
        client.session.client.return_value = mock_ec2
        mock_ec2.create_network_insights_path.side_effect = Exception("AWS Error")

        with pytest.raises(Exception, match="Failed to create path"):
            client.create_path("src", "dst", "tcp", 80)

    def test_start_analysis(self, client):
        mock_ec2 = MagicMock()
        client.session.client.return_value = mock_ec2

        mock_ec2.start_network_insights_analysis.return_value = {
            "NetworkInsightsAnalysis": {"NetworkInsightsAnalysisId": "nia-123"}
        }

        analysis_id = client.start_analysis("nip-123")
        assert analysis_id == "nia-123"


class TestFlowLogsClient:
    @pytest.fixture
    def client(self):
        with patch("boto3.Session"):
            return FlowLogsClient()

    def test_find_log_group(self, client):
        mock_ec2 = MagicMock()
        client.session.client.return_value = mock_ec2

        # Mock ENI details
        mock_ec2.describe_network_interfaces.return_value = {
            "NetworkInterfaces": [{"VpcId": "vpc-1", "SubnetId": "subnet-1"}]
        }

        # Mock Flow Logs
        mock_ec2.describe_flow_logs.return_value = {
            "FlowLogs": [{"LogGroupName": "/aws/vpc/flowlogs"}]
        }

        log_group = client.find_log_group("eni-123")
        assert log_group == "/aws/vpc/flowlogs"

    def test_query_flow_logs(self, client):
        mock_cw = MagicMock()
        client.session.client.return_value = mock_cw

        mock_cw.start_query.return_value = {"queryId": "qid-123"}
        mock_cw.get_query_results.return_value = {
            "status": "Complete",
            "results": [
                [
                    {"field": "@timestamp", "value": "2023-01-01 12:00:00"},
                    {"field": "srcAddr", "value": "1.2.3.4"},
                    {"field": "action", "value": "ACCEPT"},
                ]
            ],
        }

        results = client.query_flow_logs("lg-1", "eni-1", 15)
        assert len(results) == 1
        assert results[0]["srcAddr"] == "1.2.3.4"

    def test_analyze_traffic(self, client):
        mock_cw = MagicMock()
        client.session.client.return_value = mock_cw

        mock_cw.start_query.return_value = {"queryId": "qid-123"}

        # Mock results for two queries: top talkers and rejections
        mock_cw.get_query_results.side_effect = [
            {
                "status": "Complete",
                "results": [
                    [
                        {"field": "srcAddr", "value": "1.2.3.4"},
                        {"field": "dstAddr", "value": "5.6.7.8"},
                        {"field": "total_bytes", "value": "1000"},
                    ]
                ],
            },
            {
                "status": "Complete",
                "results": [[{"field": "rejection_count", "value": "150"}]],
            },
        ]

        results = client.analyze_traffic("lg-1", "eni-1", 15)

        assert len(results["top_talkers"]) == 1
        assert results["top_talkers"][0]["srcAddr"] == "1.2.3.4"

        assert len(results["anomalies"]) == 1
        assert results["anomalies"][0]["type"] == "High Rejection Rate"
        assert "150" in results["anomalies"][0]["description"]


class TestVPNClient:
    @pytest.fixture
    def client(self):
        with patch("boto3.Session"):
            return VPNClient()

    def test_scan_vpn_connections(self, client):
        mock_ec2 = MagicMock()
        client.session.client.return_value = mock_ec2

        mock_ec2.describe_vpn_connections.return_value = {
            "VpnConnections": [
                {
                    "VpnConnectionId": "vpn-123",
                    "Tags": [{"Key": "Name", "Value": "test-vpn"}],
                    "VgwTelemetry": [{"Status": "UP", "OutsideIpAddress": "1.1.1.1"}],
                }
            ]
        }

        # Mock other calls to empty
        mock_ec2.describe_transit_gateway_attachments.return_value = {}

        results = client.get_bgp_neighbors(["us-east-1"])
        assert len(results) == 1
        assert results[0]["resource_id"] == "vpn-123"
        assert results[0]["status"] == "UP"
        assert results[0]["type"] == "VPN"
