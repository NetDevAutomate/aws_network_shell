"""Realistic Global Network mock data fixtures.

Global Networks are the top-level container for CloudWAN Core Networks.
Each Global Network can contain multiple Core Networks.

Architecture:
- Production Global Network containing production core network
- Staging Global Network for testing
- Development Global Network for dev environments
"""

from typing import Any

# =============================================================================
# GLOBAL NETWORK FIXTURES
# =============================================================================

GLOBAL_NETWORK_FIXTURES: dict[str, dict[str, Any]] = {
    # Production Global Network - Contains our production core network
    "global-network-0prod123": {
        "GlobalNetworkId": "global-network-0prod123",
        "GlobalNetworkArn": "arn:aws:networkmanager::123456789012:global-network/global-network-0prod123",
        "Description": "Production Global Network",
        "CreatedAt": "2024-01-10T08:00:00+00:00",
        "State": "AVAILABLE",
        "Tags": [
            {"Key": "Name", "Value": "production-global-network"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "ManagedBy", "Value": "terraform"},
        ],
    },
    # Staging Global Network
    "global-network-0stag456": {
        "GlobalNetworkId": "global-network-0stag456",
        "GlobalNetworkArn": "arn:aws:networkmanager::123456789012:global-network/global-network-0stag456",
        "Description": "Staging Global Network",
        "CreatedAt": "2024-02-01T10:00:00+00:00",
        "State": "AVAILABLE",
        "Tags": [
            {"Key": "Name", "Value": "staging-global-network"},
            {"Key": "Environment", "Value": "staging"},
        ],
    },
    # Development Global Network
    "global-network-0dev0789": {
        "GlobalNetworkId": "global-network-0dev0789",
        "GlobalNetworkArn": "arn:aws:networkmanager::123456789012:global-network/global-network-0dev0789",
        "Description": "Development Global Network",
        "CreatedAt": "2024-02-15T12:00:00+00:00",
        "State": "AVAILABLE",
        "Tags": [
            {"Key": "Name", "Value": "development-global-network"},
            {"Key": "Environment", "Value": "development"},
        ],
    },
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_global_network_by_id(global_network_id: str) -> dict[str, Any] | None:
    """Get Global Network fixture by ID."""
    return GLOBAL_NETWORK_FIXTURES.get(global_network_id)


def get_all_global_networks() -> list[dict[str, Any]]:
    """Get all Global Network fixtures."""
    return list(GLOBAL_NETWORK_FIXTURES.values())


def get_global_networks_by_state(state: str) -> list[dict[str, Any]]:
    """Get Global Networks by state."""
    return [
        gn for gn in GLOBAL_NETWORK_FIXTURES.values()
        if gn.get("State") == state
    ]
