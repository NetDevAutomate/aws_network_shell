"""Tests for global-network → core-network → route-table branch.

Tests the nested context chain:
1. Root: show global-networks
2. set global-network 1 → global-network context
3. show core-networks  
4. set core-network 1 → core-network context
5. show route-tables
6. set route-table 1 → route-table context
7. show routes
"""

import pytest
from unittest.mock import MagicMock, patch

# =============================================================================
# INLINE FIXTURES (from networkmanager API shapes)
# =============================================================================

GLOBAL_NETWORKS = [
    {
        "GlobalNetworkId": "global-network-0abc123def456",
        "GlobalNetworkArn": "arn:aws:networkmanager::123456789012:global-network/global-network-0abc123def456",
        "Description": "Production Global Network",
        "CreatedAt": "2024-01-10T08:00:00+00:00",
        "State": "AVAILABLE",
        "Tags": [{"Key": "Name", "Value": "prod-global-network"}],
    },
    {
        "GlobalNetworkId": "global-network-0xyz789ghi012",
        "GlobalNetworkArn": "arn:aws:networkmanager::123456789012:global-network/global-network-0xyz789ghi012",
        "Description": "Staging Global Network",
        "CreatedAt": "2024-02-15T10:00:00+00:00",
        "State": "AVAILABLE",
        "Tags": [{"Key": "Name", "Value": "staging-global-network"}],
    },
]

CORE_NETWORKS = [
    {
        "CoreNetworkId": "core-network-0prod123456",
        "CoreNetworkArn": "arn:aws:networkmanager::123456789012:core-network/core-network-0prod123456",
        "GlobalNetworkId": "global-network-0abc123def456",
        "Description": "Production Core Network",
        "CreatedAt": "2024-01-10T09:00:00+00:00",
        "State": "AVAILABLE",
        "Segments": [
            {"Name": "production", "EdgeLocations": ["eu-west-1", "us-east-1"], "SharedSegments": []},
            {"Name": "shared-services", "EdgeLocations": ["eu-west-1", "us-east-1"], "SharedSegments": ["production"]},
        ],
        "Edges": [
            {"EdgeLocation": "eu-west-1", "Asn": 64520, "InsideCidrBlocks": ["169.254.0.0/24"]},
            {"EdgeLocation": "us-east-1", "Asn": 64521, "InsideCidrBlocks": ["169.254.1.0/24"]},
        ],
        "Tags": [{"Key": "Name", "Value": "prod-core-network"}],
    },
]

CORE_NETWORK_ROUTES = [
    {"DestinationCidrBlock": "10.0.0.0/16", "Destinations": [{"CoreNetworkAttachmentId": "attachment-001", "SegmentName": "production"}], "Type": "PROPAGATED", "State": "ACTIVE"},
    {"DestinationCidrBlock": "10.1.0.0/16", "Destinations": [{"CoreNetworkAttachmentId": "attachment-002", "SegmentName": "production"}], "Type": "PROPAGATED", "State": "ACTIVE"},
    {"DestinationCidrBlock": "10.2.0.0/16", "Destinations": [], "Type": "PROPAGATED", "State": "BLACKHOLE"},
]


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def mock_shell():
    """Create mock shell with required attributes."""
    shell = MagicMock()
    shell.profile = "default"
    shell.current_context = None
    shell.context_data = {}
    return shell


# =============================================================================
# TEST: ROOT - show global-networks
# =============================================================================

class TestRootShowGlobalNetworks:
    """Test show global-networks at root level."""

    def test_show_global_networks_calls_api(self):
        """show global-networks should call describe_global_networks."""
        with patch("aws_network_tools.modules.cloudwan.CloudWANClient") as MockClient:
            mock_nm = MagicMock()
            mock_nm.describe_global_networks.return_value = {"GlobalNetworks": GLOBAL_NETWORKS}
            MockClient.return_value.nm = mock_nm
            
            from aws_network_tools.modules.cloudwan import CloudWANClient
            client = CloudWANClient("default")
            result = client.nm.describe_global_networks()
            
            assert "GlobalNetworks" in result
            assert len(result["GlobalNetworks"]) == 2

    def test_global_networks_have_required_fields(self):
        """Global networks should have id, name, state."""
        for gn in GLOBAL_NETWORKS:
            assert "GlobalNetworkId" in gn
            assert "State" in gn
            assert gn["State"] == "AVAILABLE"


# =============================================================================
# TEST: GLOBAL-NETWORK CONTEXT - show core-networks
# =============================================================================

class TestGlobalNetworkContext:
    """Test commands in global-network context."""

    def test_enter_global_network_context(self, mock_shell):
        """set global-network should set context data."""
        gn = GLOBAL_NETWORKS[0]
        mock_shell.current_context = "global-network"
        mock_shell.context_data["global_network"] = gn
        mock_shell.context_data["global_network_id"] = gn["GlobalNetworkId"]
        
        assert mock_shell.current_context == "global-network"
        assert mock_shell.context_data["global_network_id"] == "global-network-0abc123def456"

    def test_show_core_networks_in_context(self):
        """show core-networks should list core networks for global network."""
        with patch("aws_network_tools.modules.cloudwan.CloudWANClient") as MockClient:
            mock_nm = MagicMock()
            mock_nm.list_core_networks.return_value = {
                "CoreNetworks": [{"CoreNetworkId": cn["CoreNetworkId"], "State": cn["State"]} for cn in CORE_NETWORKS]
            }
            mock_nm.get_core_network.return_value = {"CoreNetwork": CORE_NETWORKS[0]}
            MockClient.return_value.nm = mock_nm
            
            from aws_network_tools.modules.cloudwan import CloudWANClient
            client = CloudWANClient("default")
            result = client.nm.list_core_networks()
            
            assert len(result["CoreNetworks"]) >= 1


# =============================================================================
# TEST: CORE-NETWORK CONTEXT
# =============================================================================

class TestCoreNetworkContext:
    """Test commands in core-network context."""

    def test_enter_core_network_context(self, mock_shell):
        """set core-network should set context data."""
        cn = CORE_NETWORKS[0]
        mock_shell.current_context = "core-network"
        mock_shell.context_data["core_network"] = cn
        mock_shell.context_data["core_network_id"] = cn["CoreNetworkId"]
        
        assert mock_shell.current_context == "core-network"
        assert mock_shell.context_data["core_network_id"] == "core-network-0prod123456"

    def test_core_network_has_segments(self, mock_shell):
        """Core network should have segments (become route tables)."""
        cn = CORE_NETWORKS[0]
        mock_shell.context_data["core_network"] = cn
        
        segments = cn.get("Segments", [])
        assert len(segments) >= 1
        assert segments[0]["Name"] == "production"

    def test_show_route_tables_lists_segment_edge_combos(self, mock_shell):
        """show route-tables should list segment/edge combinations."""
        cn = CORE_NETWORKS[0]
        mock_shell.context_data["core_network"] = cn
        
        # Route tables = segment × edge combinations
        route_tables = []
        for segment in cn.get("Segments", []):
            for edge in segment.get("EdgeLocations", []):
                route_tables.append({"segment": segment["Name"], "edge": edge})
        
        assert len(route_tables) >= 2  # production has 2 edges

    def test_show_routes_calls_api(self):
        """show routes should call get_core_network_routes."""
        with patch("aws_network_tools.modules.cloudwan.CloudWANClient") as MockClient:
            mock_nm = MagicMock()
            mock_nm.get_core_network_routes.return_value = {"CoreNetworkRoutes": CORE_NETWORK_ROUTES}
            MockClient.return_value.nm = mock_nm
            
            from aws_network_tools.modules.cloudwan import CloudWANClient
            client = CloudWANClient("default")
            result = client.nm.get_core_network_routes(
                CoreNetworkId="core-network-0prod123456",
                SegmentName="production",
                EdgeLocation="eu-west-1"
            )
            
            assert len(result["CoreNetworkRoutes"]) == 3


# =============================================================================
# TEST: ROUTE-TABLE CONTEXT (nested under core-network)
# =============================================================================

class TestRouteTableContext:
    """Test commands in route-table context."""

    def test_enter_route_table_context(self, mock_shell):
        """set route-table should set segment/edge context."""
        cn = CORE_NETWORKS[0]
        mock_shell.current_context = "route-table"
        mock_shell.context_data["core_network"] = cn
        mock_shell.context_data["segment"] = "production"
        mock_shell.context_data["edge"] = "eu-west-1"
        
        assert mock_shell.current_context == "route-table"
        assert mock_shell.context_data["segment"] == "production"
        assert mock_shell.context_data["edge"] == "eu-west-1"

    def test_show_routes_in_route_table(self, mock_shell):
        """show routes should show routes for specific segment/edge."""
        mock_shell.context_data["segment"] = "production"
        mock_shell.context_data["edge"] = "eu-west-1"
        
        # Filter routes for this segment
        routes = [r for r in CORE_NETWORK_ROUTES if r["State"] == "ACTIVE"]
        assert len(routes) == 2

    def test_find_prefix_action(self, mock_shell):
        """find_prefix should search routes in route table."""
        mock_shell.current_context = "route-table"
        mock_shell.context_data["segment"] = "production"
        
        # Search for 10.0.0.0/16
        matching = [r for r in CORE_NETWORK_ROUTES if "10.0" in r["DestinationCidrBlock"]]
        assert len(matching) >= 1

    def test_find_null_routes_action(self, mock_shell):
        """find_null_routes should find blackhole routes."""
        mock_shell.current_context = "route-table"
        
        blackholes = [r for r in CORE_NETWORK_ROUTES if r["State"] == "BLACKHOLE"]
        assert len(blackholes) == 1
        assert blackholes[0]["DestinationCidrBlock"] == "10.2.0.0/16"


# =============================================================================
# TEST: FULL BRANCH TRAVERSAL
# =============================================================================

class TestFullBranchTraversal:
    """Test complete traversal: root → global-network → core-network → route-table."""

    def test_full_navigation_chain(self, mock_shell):
        """Navigate entire branch and verify context at each level."""
        # Step 1: Root - show global-networks
        assert mock_shell.current_context is None
        gns = GLOBAL_NETWORKS
        assert len(gns) >= 1
        
        # Step 2: set global-network 1
        gn = gns[0]
        mock_shell.current_context = "global-network"
        mock_shell.context_data["global_network"] = gn
        mock_shell.context_data["global_network_id"] = gn["GlobalNetworkId"]
        assert mock_shell.current_context == "global-network"
        
        # Step 3: show core-networks (in global-network context)
        cns = CORE_NETWORKS
        assert len(cns) >= 1
        
        # Step 4: set core-network 1
        cn = cns[0]
        mock_shell.current_context = "core-network"
        mock_shell.context_data["core_network"] = cn
        mock_shell.context_data["core_network_id"] = cn["CoreNetworkId"]
        assert mock_shell.current_context == "core-network"
        
        # Step 5: show route-tables (segments × edges)
        segments = cn.get("Segments", [])
        assert len(segments) >= 1
        
        # Step 6: set route-table 1 (first segment/edge combo)
        segment = segments[0]
        edge = segment["EdgeLocations"][0]
        mock_shell.current_context = "route-table"
        mock_shell.context_data["segment"] = segment["Name"]
        mock_shell.context_data["edge"] = edge
        assert mock_shell.current_context == "route-table"
        
        # Step 7: show routes
        routes = CORE_NETWORK_ROUTES
        assert len(routes) >= 1
        
        # Verify full context chain is preserved
        assert mock_shell.context_data.get("global_network_id") == "global-network-0abc123def456"
        assert mock_shell.context_data.get("core_network_id") == "core-network-0prod123456"
        assert mock_shell.context_data.get("segment") == "production"
        assert mock_shell.context_data.get("edge") == "eu-west-1"

    def test_exit_back_through_contexts(self, mock_shell):
        """Test exiting back through context chain."""
        # Start at route-table level
        mock_shell.current_context = "route-table"
        mock_shell.context_data = {
            "global_network_id": "global-network-0abc123def456",
            "core_network_id": "core-network-0prod123456",
            "segment": "production",
            "edge": "eu-west-1",
        }
        
        # Exit to core-network
        mock_shell.current_context = "core-network"
        del mock_shell.context_data["segment"]
        del mock_shell.context_data["edge"]
        assert mock_shell.current_context == "core-network"
        assert "core_network_id" in mock_shell.context_data
        
        # Exit to global-network
        mock_shell.current_context = "global-network"
        del mock_shell.context_data["core_network_id"]
        assert mock_shell.current_context == "global-network"
        assert "global_network_id" in mock_shell.context_data
        
        # Exit to root
        mock_shell.current_context = None
        mock_shell.context_data = {}
        assert mock_shell.current_context is None
