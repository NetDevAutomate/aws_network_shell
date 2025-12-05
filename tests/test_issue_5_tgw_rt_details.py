import pytest
from unittest.mock import MagicMock
from aws_network_tools.modules.tgw import TGWClient


class TestTGWRouteTableDetails:
    def test_discover_fetches_associations_and_propagations(self):
        mock_session = MagicMock()
        mock_client = MagicMock()
        mock_session.client.return_value = mock_client
        mock_session.region_name = "us-east-1"

        mock_client.describe_transit_gateways.return_value = {
            "TransitGateways": [{
                "TransitGatewayId": "tgw-123",
                "State": "available",
                "Tags": [{"Key": "Name", "Value": "test-tgw"}],
            }]
        }

        mock_client.describe_transit_gateway_attachments.return_value = {
            "TransitGatewayAttachments": [{
                "TransitGatewayAttachmentId": "tgw-att-abc",
                "ResourceId": "vpc-123",
                "ResourceType": "vpc",
                "State": "available",
                "Tags": [{"Key": "Name", "Value": "vpc-att"}],
            }]
        }

        mock_client.describe_transit_gateway_route_tables.return_value = {
            "TransitGatewayRouteTables": [{
                "TransitGatewayRouteTableId": "tgw-rtb-456",
                "Tags": [{"Key": "Name", "Value": "test-rtb"}],
            }]
        }

        mock_client.search_transit_gateway_routes.return_value = {
            "Routes": [{
                "DestinationCidrBlock": "10.0.0.0/16",
                "State": "active",
                "Type": "propagated",
                "TransitGatewayAttachments": [{"TransitGatewayAttachmentId": "tgw-att-abc", "ResourceType": "vpc"}]
            }]
        }

        mock_client.get_transit_gateway_route_table_associations.return_value = {
            "Associations": [{
                "TransitGatewayAttachmentId": "tgw-att-abc",
                "ResourceId": "vpc-123",
                "ResourceType": "vpc",
                "State": "associated"
            }]
        }

        mock_client.get_transit_gateway_route_table_propagations.return_value = {
            "TransitGatewayRouteTablePropagations": [{
                "TransitGatewayAttachmentId": "tgw-att-def",
                "ResourceId": "vpn-456",
                "ResourceType": "vpn",
                "State": "enabled"
            }]
        }

        client = TGWClient(session=mock_session)
        result = client._scan_region("us-east-1")

        assert len(result) == 1
        tgw = result[0]
        assert len(tgw["route_tables"]) == 1
        rt = tgw["route_tables"][0]

        assert "associations" in rt
        assert "propagations" in rt
        assert len(rt["associations"]) == 1
        assert len(rt["propagations"]) == 1
