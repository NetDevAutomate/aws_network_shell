
import pytest
from unittest.mock import patch, MagicMock
from aws_network_tools.modules.tgw import TGWClient

class TestTGWRouteTableDetails:
    @pytest.fixture
    def mock_ec2(self):
        with patch("boto3.Session") as mock_session:
            mock_client = MagicMock()
            mock_session.return_value.client.return_value = mock_client
            # Mock get_regions to just return one region to simplify test
            mock_session.return_value.region_name = "us-east-1"
            mock_client.describe_regions.return_value = {"Regions": [{"RegionName": "us-east-1"}]}
            yield mock_client

    def test_discover_fetches_associations_and_propagations(self, mock_ec2):
        # Mock TGW
        mock_ec2.describe_transit_gateways.return_value = {
            "TransitGateways": [
                {
                    "TransitGatewayId": "tgw-123",
                    "State": "available",
                    "Tags": [{"Key": "Name", "Value": "test-tgw"}],
                }
            ]
        }
        
        # Mock Attachments (general TGW attachments)
        mock_ec2.describe_transit_gateway_attachments.return_value = {
            "TransitGatewayAttachments": [
                {
                    "TransitGatewayAttachmentId": "tgw-att-abc",
                    "ResourceId": "vpc-123",
                    "ResourceType": "vpc",
                    "State": "available",
                    "Tags": [{"Key": "Name", "Value": "vpc-att"}],
                }
            ]
        }

        # Mock Route Tables
        mock_ec2.describe_transit_gateway_route_tables.return_value = {
            "TransitGatewayRouteTables": [
                {
                    "TransitGatewayRouteTableId": "tgw-rtb-456",
                    "Tags": [{"Key": "Name", "Value": "test-rtb"}],
                }
            ]
        }

        # Mock Routes
        mock_ec2.search_transit_gateway_routes.return_value = {
            "Routes": [
                {
                    "DestinationCidrBlock": "10.0.0.0/16",
                    "State": "active",
                    "Type": "propagated",
                    "TransitGatewayAttachments": [{"TransitGatewayAttachmentId": "tgw-att-abc", "ResourceType": "vpc"}]
                }
            ]
        }
        
        # Mock Associations
        mock_ec2.get_transit_gateway_route_table_associations.return_value = {
            "Associations": [
                {
                    "TransitGatewayAttachmentId": "tgw-att-abc",
                    "ResourceId": "vpc-123",
                    "ResourceType": "vpc",
                    "State": "associated"
                }
            ]
        }

        # Mock Propagations
        mock_ec2.get_transit_gateway_route_table_propagations.return_value = {
            "TransitGatewayRouteTablePropagations": [
                {
                    "TransitGatewayAttachmentId": "tgw-att-def",
                    "ResourceId": "vpn-456",
                    "ResourceType": "vpn",
                    "State": "enabled"
                }
            ]
        }

        client = TGWClient()
        # Force region to avoid multiple calls if logic differs
        result = client._scan_region("us-east-1")
        
        assert len(result) == 1
        tgw = result[0]
        assert len(tgw["route_tables"]) == 1
        rt = tgw["route_tables"][0]
        
        # These are the assertions that should currently fail
        assert "associations" in rt, "associations key missing in route table data"
        assert "propagations" in rt, "propagations key missing in route table data"
        
        assert len(rt["associations"]) == 1
        assert rt["associations"][0]["id"] == "tgw-att-abc"
        
        assert len(rt["propagations"]) == 1
        assert rt["propagations"][0]["id"] == "tgw-att-def"
