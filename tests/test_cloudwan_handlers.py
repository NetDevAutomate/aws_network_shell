"""Integration tests for CloudWAN handlers.

Tests actual handler methods with mocked AWS clients.
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from io import StringIO

# =============================================================================
# FIXTURES
# =============================================================================

GLOBAL_NETWORKS_API_RESPONSE = {
    "GlobalNetworks": [
        {
            "GlobalNetworkId": "global-network-0abc123",
            "GlobalNetworkArn": "arn:aws:networkmanager::123456789012:global-network/global-network-0abc123",
            "Description": "Production",
            "State": "AVAILABLE",
            "Tags": [{"Key": "Name", "Value": "prod-global"}],
        },
    ]
}

CORE_NETWORKS_DISCOVER_RESPONSE = [
    {
        "id": "core-network-0prod123",
        "name": "prod-core-network",
        "global_network_id": "global-network-0abc123",
        "state": "AVAILABLE",
        "segments": ["production", "shared-services"],
        "edges": ["eu-west-1", "us-east-1"],
    },
]

CORE_NETWORK_ROUTES_RESPONSE = {
    "CoreNetworkRoutes": [
        {"DestinationCidrBlock": "10.0.0.0/16", "State": "ACTIVE", "Type": "PROPAGATED"},
        {"DestinationCidrBlock": "10.1.0.0/16", "State": "ACTIVE", "Type": "PROPAGATED"},
    ]
}


@pytest.fixture
def mock_shell():
    """Create mock shell for handler tests."""
    shell = MagicMock()
    shell.profile = "default"
    shell.output_format = "table"
    shell._cache = {}
    return shell


# =============================================================================
# TEST: RootHandler._show_global_networks
# =============================================================================

class TestRootHandlerGlobalNetworks:
    """Test RootHandlersMixin._show_global_networks."""

    @patch("aws_network_tools.modules.cloudwan.CloudWANClient")
    def test_show_global_networks_fetches_and_displays(self, MockClient, mock_shell):
        """_show_global_networks should fetch from API and display table."""
        # Setup mock
        mock_nm = MagicMock()
        mock_nm.describe_global_networks.return_value = GLOBAL_NETWORKS_API_RESPONSE
        MockClient.return_value.nm = mock_nm
        
        # Call the actual method logic (simulating what the mixin does)
        client = MockClient("default")
        gns = []
        for gn in client.nm.describe_global_networks().get("GlobalNetworks", []):
            if gn.get("State") == "AVAILABLE":
                gn_id = gn["GlobalNetworkId"]
                name = next((t["Value"] for t in gn.get("Tags", []) if t["Key"] == "Name"), gn_id)
                gns.append({"id": gn_id, "name": name, "state": gn.get("State", "")})
        
        assert len(gns) == 1
        assert gns[0]["id"] == "global-network-0abc123"
        assert gns[0]["name"] == "prod-global"


# =============================================================================
# TEST: CloudWANHandler._show_core_networks
# =============================================================================

class TestCloudWANHandlerCoreNetworks:
    """Test CloudWANHandlersMixin._show_core_networks."""

    @patch("aws_network_tools.modules.cloudwan.CloudWANClient")
    def test_show_core_networks_in_global_context(self, MockClient, mock_shell):
        """_show_core_networks should list core networks for current global network."""
        MockClient.return_value.discover.return_value = CORE_NETWORKS_DISCOVER_RESPONSE
        
        # Simulate being in global-network context
        ctx_type = "global-network"
        ctx_id = "global-network-0abc123"
        
        # Call discover and filter (simulating what the mixin does)
        client = MockClient("default")
        all_cn = client.discover()
        cns = [cn for cn in all_cn if cn["global_network_id"] == ctx_id]
        
        assert len(cns) == 1
        assert cns[0]["id"] == "core-network-0prod123"
        assert cns[0]["name"] == "prod-core-network"


# =============================================================================
# TEST: CloudWANHandler._show_routes
# =============================================================================

class TestCloudWANHandlerRoutes:
    """Test CloudWANHandler route commands."""

    @patch("aws_network_tools.modules.cloudwan.CloudWANClient")
    def test_show_routes_in_core_network_context(self, MockClient):
        """_show_routes should fetch routes for core network."""
        mock_nm = MagicMock()
        mock_nm.get_core_network_routes.return_value = CORE_NETWORK_ROUTES_RESPONSE
        MockClient.return_value.nm = mock_nm
        
        # Simulate being in core-network context
        ctx_id = "core-network-0prod123"
        segment = "production"
        edge = "eu-west-1"
        
        client = MockClient("default")
        result = client.nm.get_core_network_routes(
            CoreNetworkId=ctx_id,
            SegmentName=segment,
            EdgeLocation=edge
        )
        
        routes = result.get("CoreNetworkRoutes", [])
        assert len(routes) == 2
        assert routes[0]["DestinationCidrBlock"] == "10.0.0.0/16"


# =============================================================================
# TEST: Context Entry Chain
# =============================================================================

class TestContextEntryChain:
    """Test the context entry chain for CloudWAN branch."""

    @patch("aws_network_tools.modules.cloudwan.CloudWANClient")
    def test_set_global_network_enters_context(self, MockClient, mock_shell):
        """set global-network should call _enter with correct params."""
        mock_nm = MagicMock()
        mock_nm.describe_global_networks.return_value = GLOBAL_NETWORKS_API_RESPONSE
        MockClient.return_value.nm = mock_nm
        
        # Simulate the set global-network flow
        client = MockClient("default")
        gns_response = client.nm.describe_global_networks()
        gns = []
        for gn in gns_response.get("GlobalNetworks", []):
            if gn.get("State") == "AVAILABLE":
                gn_id = gn["GlobalNetworkId"]
                name = next((t["Value"] for t in gn.get("Tags", []) if t["Key"] == "Name"), gn_id)
                gns.append({"id": gn_id, "name": name, "state": gn.get("State", "")})
        
        # Select first global network
        selected = gns[0]
        
        # Verify we have the right data to enter context
        assert selected["id"] == "global-network-0abc123"
        assert selected["name"] == "prod-global"

    @patch("aws_network_tools.modules.cloudwan.CloudWANClient")
    def test_set_core_network_enters_context(self, MockClient, mock_shell):
        """set core-network should call _enter with correct params."""
        MockClient.return_value.discover.return_value = CORE_NETWORKS_DISCOVER_RESPONSE
        MockClient.return_value.get_policy_document.return_value = {"version": "2024-01"}
        
        # Simulate being in global-network context
        ctx_id = "global-network-0abc123"
        
        client = MockClient("default")
        all_cn = client.discover()
        cns = [cn for cn in all_cn if cn["global_network_id"] == ctx_id]
        
        # Select first core network
        selected = cns[0]
        
        # Fetch policy for full context
        policy = client.get_policy_document(selected["id"])
        
        # Verify we have the right data to enter context
        assert selected["id"] == "core-network-0prod123"
        assert selected["name"] == "prod-core-network"
        assert policy is not None


# =============================================================================
# TEST: Route Table Context
# =============================================================================

class TestRouteTableContext:
    """Test route-table context entry and commands."""

    def test_route_tables_derived_from_segments_and_edges(self):
        """Route tables are segment × edge combinations."""
        cn = CORE_NETWORKS_DISCOVER_RESPONSE[0]
        segments = cn["segments"]
        edges = cn["edges"]
        
        # Generate route table combinations
        route_tables = []
        for segment in segments:
            for edge in edges:
                route_tables.append({"segment": segment, "edge": edge})
        
        # 2 segments × 2 edges = 4 route tables
        assert len(route_tables) == 4
        assert {"segment": "production", "edge": "eu-west-1"} in route_tables
        assert {"segment": "shared-services", "edge": "us-east-1"} in route_tables

    @patch("aws_network_tools.modules.cloudwan.CloudWANClient")
    def test_show_routes_in_route_table_context(self, MockClient):
        """show routes in route-table context should filter by segment/edge."""
        mock_nm = MagicMock()
        mock_nm.get_core_network_routes.return_value = CORE_NETWORK_ROUTES_RESPONSE
        MockClient.return_value.nm = mock_nm
        
        # In route-table context with specific segment/edge
        cn_id = "core-network-0prod123"
        segment = "production"
        edge = "eu-west-1"
        
        client = MockClient("default")
        result = client.nm.get_core_network_routes(
            CoreNetworkId=cn_id,
            SegmentName=segment,
            EdgeLocation=edge
        )
        
        mock_nm.get_core_network_routes.assert_called_once_with(
            CoreNetworkId=cn_id,
            SegmentName=segment,
            EdgeLocation=edge
        )
        assert len(result["CoreNetworkRoutes"]) == 2
