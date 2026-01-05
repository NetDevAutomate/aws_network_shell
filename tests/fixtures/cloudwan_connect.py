"""Realistic CloudWAN Connect Peer and BGP mock data fixtures.

Multi-region SD-WAN and third-party network integration:
- GRE tunnel-based connect peers for SD-WAN integration
- BGP peering configurations with realistic ASN ranges
- Multiple states: AVAILABLE, CREATING, DELETING
- Inside CIDR blocks for tunnel addressing
- Transport attachment references to VPC attachments
- Comprehensive BGP configurations with Core Network and Peer addressing

Connect Peers enable:
- SD-WAN overlay integration with CloudWAN underlay
- Third-party network appliance integration
- Branch office connectivity via SD-WAN gateways
- Multi-vendor network fabric integration
"""

from typing import Any

# =============================================================================
# CLOUDWAN CONNECT PEER FIXTURES
# =============================================================================

CONNECT_PEER_FIXTURES: dict[str, dict[str, Any]] = {
    # Production SD-WAN Connect Peer - us-east-1
    "peer-0sdwan1prod12345": {
        "ConnectPeerId": "peer-0sdwan1prod12345",
        "CoreNetworkId": "core-network-0global123",
        "CoreNetworkArn": "arn:aws:networkmanager::123456789012:core-network/core-network-0global123",
        "ConnectAttachmentId": "attachment-0connect1234",
        "EdgeLocation": "us-east-1",
        "State": "AVAILABLE",
        "CreatedAt": "2024-02-10T12:15:00+00:00",
        "Configuration": {
            "Protocol": "GRE",
            "CoreNetworkAddress": "169.254.1.1",
            "PeerAddress": "198.51.100.25",
            "InsideCidrBlocks": ["169.254.1.0/29"],
            "BgpConfigurations": [
                {
                    "CoreNetworkAsn": 64521,
                    "PeerAsn": 65001,
                    "CoreNetworkAddress": "169.254.1.1",
                    "PeerAddress": "169.254.1.2",
                }
            ],
        },
        "Tags": [
            {"Key": "Name", "Value": "production-sdwan-peer1"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "Vendor", "Value": "viptela"},
            {"Key": "Site", "Value": "us-east-datacenter"},
        ],
    },
    # Production SD-WAN Connect Peer 2 - us-east-1 (Redundant)
    "peer-0sdwan2prod12345": {
        "ConnectPeerId": "peer-0sdwan2prod12345",
        "CoreNetworkId": "core-network-0global123",
        "CoreNetworkArn": "arn:aws:networkmanager::123456789012:core-network/core-network-0global123",
        "ConnectAttachmentId": "attachment-0connect1234",
        "EdgeLocation": "us-east-1",
        "State": "AVAILABLE",
        "CreatedAt": "2024-02-10T12:20:00+00:00",
        "Configuration": {
            "Protocol": "GRE",
            "CoreNetworkAddress": "169.254.1.9",
            "PeerAddress": "198.51.100.26",
            "InsideCidrBlocks": ["169.254.1.8/29"],
            "BgpConfigurations": [
                {
                    "CoreNetworkAsn": 64521,
                    "PeerAsn": 65001,
                    "CoreNetworkAddress": "169.254.1.9",
                    "PeerAddress": "169.254.1.10",
                }
            ],
        },
        "Tags": [
            {"Key": "Name", "Value": "production-sdwan-peer2"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "Vendor", "Value": "viptela"},
            {"Key": "Site", "Value": "us-east-datacenter"},
            {"Key": "Redundancy", "Value": "secondary"},
        ],
    },
    # Staging SD-WAN Connect Peer - eu-west-1
    "peer-0sdwanstag123456": {
        "ConnectPeerId": "peer-0sdwanstag123456",
        "CoreNetworkId": "core-network-0global123",
        "CoreNetworkArn": "arn:aws:networkmanager::123456789012:core-network/core-network-0global123",
        "ConnectAttachmentId": "attachment-0connectstag1",
        "EdgeLocation": "eu-west-1",
        "State": "AVAILABLE",
        "CreatedAt": "2024-02-15T10:00:00+00:00",
        "Configuration": {
            "Protocol": "GRE",
            "CoreNetworkAddress": "169.254.0.1",
            "PeerAddress": "203.0.113.50",
            "InsideCidrBlocks": ["169.254.0.0/29"],
            "BgpConfigurations": [
                {
                    "CoreNetworkAsn": 64520,
                    "PeerAsn": 65002,
                    "CoreNetworkAddress": "169.254.0.1",
                    "PeerAddress": "169.254.0.2",
                }
            ],
        },
        "Tags": [
            {"Key": "Name", "Value": "staging-sdwan-peer"},
            {"Key": "Environment", "Value": "staging"},
            {"Key": "Vendor", "Value": "velocloud"},
            {"Key": "Site", "Value": "dublin-test"},
        ],
    },
    # Development Third-Party Appliance - ap-southeast-2
    "peer-0thirdpartydev123": {
        "ConnectPeerId": "peer-0thirdpartydev123",
        "CoreNetworkId": "core-network-0global123",
        "CoreNetworkArn": "arn:aws:networkmanager::123456789012:core-network/core-network-0global123",
        "ConnectAttachmentId": "attachment-0connectdev12",
        "EdgeLocation": "ap-southeast-2",
        "State": "AVAILABLE",
        "CreatedAt": "2024-02-20T08:30:00+00:00",
        "Configuration": {
            "Protocol": "GRE",
            "CoreNetworkAddress": "169.254.2.1",
            "PeerAddress": "192.0.2.100",
            "InsideCidrBlocks": ["169.254.2.0/29"],
            "BgpConfigurations": [
                {
                    "CoreNetworkAsn": 64522,
                    "PeerAsn": 65100,
                    "CoreNetworkAddress": "169.254.2.1",
                    "PeerAddress": "169.254.2.2",
                }
            ],
        },
        "Tags": [
            {"Key": "Name", "Value": "development-appliance-peer"},
            {"Key": "Environment", "Value": "development"},
            {"Key": "Vendor", "Value": "palo-alto"},
            {"Key": "Site", "Value": "sydney-dev"},
        ],
    },
    # Branch Office Connect Peer - us-east-1 (Private ASN)
    "peer-0branchoffice123": {
        "ConnectPeerId": "peer-0branchoffice123",
        "CoreNetworkId": "core-network-0global123",
        "CoreNetworkArn": "arn:aws:networkmanager::123456789012:core-network/core-network-0global123",
        "ConnectAttachmentId": "attachment-0connectbrnch",
        "EdgeLocation": "us-east-1",
        "State": "AVAILABLE",
        "CreatedAt": "2024-03-01T14:00:00+00:00",
        "Configuration": {
            "Protocol": "GRE",
            "CoreNetworkAddress": "169.254.1.17",
            "PeerAddress": "198.51.100.75",
            "InsideCidrBlocks": ["169.254.1.16/29"],
            "BgpConfigurations": [
                {
                    "CoreNetworkAsn": 64521,
                    "PeerAsn": 64600,
                    "CoreNetworkAddress": "169.254.1.17",
                    "PeerAddress": "169.254.1.18",
                }
            ],
        },
        "Tags": [
            {"Key": "Name", "Value": "branch-office-nyc"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "Vendor", "Value": "cisco-meraki"},
            {"Key": "Site", "Value": "nyc-branch-001"},
            {"Key": "Type", "Value": "branch"},
        ],
    },
    # Multi-BGP Session Connect Peer - eu-west-1 (Dual-stack simulation)
    "peer-0multibgp123456": {
        "ConnectPeerId": "peer-0multibgp123456",
        "CoreNetworkId": "core-network-0global123",
        "CoreNetworkArn": "arn:aws:networkmanager::123456789012:core-network/core-network-0global123",
        "ConnectAttachmentId": "attachment-0connectmulti",
        "EdgeLocation": "eu-west-1",
        "State": "AVAILABLE",
        "CreatedAt": "2024-03-05T09:00:00+00:00",
        "Configuration": {
            "Protocol": "GRE",
            "CoreNetworkAddress": "169.254.0.9",
            "PeerAddress": "203.0.113.100",
            "InsideCidrBlocks": ["169.254.0.8/29", "169.254.0.16/29"],
            "BgpConfigurations": [
                {
                    "CoreNetworkAsn": 64520,
                    "PeerAsn": 65200,
                    "CoreNetworkAddress": "169.254.0.9",
                    "PeerAddress": "169.254.0.10",
                },
                {
                    "CoreNetworkAsn": 64520,
                    "PeerAsn": 65200,
                    "CoreNetworkAddress": "169.254.0.17",
                    "PeerAddress": "169.254.0.18",
                },
            ],
        },
        "Tags": [
            {"Key": "Name", "Value": "multi-bgp-session-peer"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "Vendor", "Value": "fortinet"},
            {"Key": "Site", "Value": "frankfurt-edge"},
            {"Key": "Sessions", "Value": "dual"},
        ],
    },
    # Creating State Connect Peer - ap-southeast-2
    "peer-0creating1234567": {
        "ConnectPeerId": "peer-0creating1234567",
        "CoreNetworkId": "core-network-0global123",
        "CoreNetworkArn": "arn:aws:networkmanager::123456789012:core-network/core-network-0global123",
        "ConnectAttachmentId": "attachment-0connectnew12",
        "EdgeLocation": "ap-southeast-2",
        "State": "CREATING",
        "CreatedAt": "2024-03-10T16:00:00+00:00",
        "Configuration": {
            "Protocol": "GRE",
            "CoreNetworkAddress": "169.254.2.9",
            "PeerAddress": "192.0.2.150",
            "InsideCidrBlocks": ["169.254.2.8/29"],
            "BgpConfigurations": [
                {
                    "CoreNetworkAsn": 64522,
                    "PeerAsn": 65300,
                    "CoreNetworkAddress": "169.254.2.9",
                    "PeerAddress": "169.254.2.10",
                }
            ],
        },
        "Tags": [
            {"Key": "Name", "Value": "new-branch-peer"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "Vendor", "Value": "silver-peak"},
            {"Key": "Site", "Value": "sydney-new-branch"},
        ],
    },
    # Deleting State Connect Peer - us-east-1
    "peer-0deleting1234567": {
        "ConnectPeerId": "peer-0deleting1234567",
        "CoreNetworkId": "core-network-0global123",
        "CoreNetworkArn": "arn:aws:networkmanager::123456789012:core-network/core-network-0global123",
        "ConnectAttachmentId": "attachment-0connectold12",
        "EdgeLocation": "us-east-1",
        "State": "DELETING",
        "CreatedAt": "2023-12-01T10:00:00+00:00",
        "Configuration": {
            "Protocol": "GRE",
            "CoreNetworkAddress": "169.254.1.25",
            "PeerAddress": "198.51.100.200",
            "InsideCidrBlocks": ["169.254.1.24/29"],
            "BgpConfigurations": [
                {
                    "CoreNetworkAsn": 64521,
                    "PeerAsn": 64700,
                    "CoreNetworkAddress": "169.254.1.25",
                    "PeerAddress": "169.254.1.26",
                }
            ],
        },
        "Tags": [
            {"Key": "Name", "Value": "deprecated-branch-peer"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "Vendor", "Value": "legacy-appliance"},
            {"Key": "Site", "Value": "retired-site"},
            {"Key": "Status", "Value": "decommissioning"},
        ],
    },
    # High-ASN Connect Peer - eu-west-1 (4-byte ASN)
    "peer-0highasnpeer1234": {
        "ConnectPeerId": "peer-0highasnpeer1234",
        "CoreNetworkId": "core-network-0global123",
        "CoreNetworkArn": "arn:aws:networkmanager::123456789012:core-network/core-network-0global123",
        "ConnectAttachmentId": "attachment-0connecthigh1",
        "EdgeLocation": "eu-west-1",
        "State": "AVAILABLE",
        "CreatedAt": "2024-03-08T11:00:00+00:00",
        "Configuration": {
            "Protocol": "GRE",
            "CoreNetworkAddress": "169.254.0.25",
            "PeerAddress": "203.0.113.200",
            "InsideCidrBlocks": ["169.254.0.24/29"],
            "BgpConfigurations": [
                {
                    "CoreNetworkAsn": 64520,
                    "PeerAsn": 4200000100,
                    "CoreNetworkAddress": "169.254.0.25",
                    "PeerAddress": "169.254.0.26",
                }
            ],
        },
        "Tags": [
            {"Key": "Name", "Value": "isp-peer-4byte-asn"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "Vendor", "Value": "juniper"},
            {"Key": "Site", "Value": "carrier-interconnect"},
            {"Key": "ASN-Type", "Value": "4-byte"},
        ],
    },
}

# =============================================================================
# EXPANDED CLOUDWAN CONNECT ATTACHMENT FIXTURES
# =============================================================================

CONNECT_ATTACHMENT_FIXTURES: dict[str, dict[str, Any]] = {
    # Production Connect Attachment - us-east-1 (already exists in cloudwan.py)
    "attachment-0connect1234": {
        "AttachmentId": "attachment-0connect1234",
        "CoreNetworkId": "core-network-0global123",
        "CoreNetworkArn": "arn:aws:networkmanager::123456789012:core-network/core-network-0global123",
        "AttachmentType": "CONNECT",
        "State": "AVAILABLE",
        "EdgeLocation": "us-east-1",
        "ResourceArn": "arn:aws:networkmanager::123456789012:attachment/attachment-0stagvpc1234",
        "AttachmentPolicyRuleNumber": 100,
        "SegmentName": "staging",
        "Tags": [
            {"Key": "Name", "Value": "sdwan-connect-attachment"},
            {"Key": "Type", "Value": "sd-wan"},
        ],
        "ProposedSegmentChange": None,
        "ProposedNetworkFunctionGroupChange": None,
        "CreatedAt": "2024-02-10T12:00:00+00:00",
        "UpdatedAt": "2024-02-10T12:05:00+00:00",
        "ConnectOptions": {
            "Protocol": "GRE",
            "TransportAttachmentId": "attachment-0stagvpc1234",
        },
    },
    # Staging Connect Attachment - eu-west-1
    "attachment-0connectstag1": {
        "AttachmentId": "attachment-0connectstag1",
        "CoreNetworkId": "core-network-0global123",
        "CoreNetworkArn": "arn:aws:networkmanager::123456789012:core-network/core-network-0global123",
        "AttachmentType": "CONNECT",
        "State": "AVAILABLE",
        "EdgeLocation": "eu-west-1",
        "ResourceArn": "arn:aws:networkmanager::123456789012:attachment/attachment-0shared12345",
        "AttachmentPolicyRuleNumber": 100,
        "SegmentName": "staging",
        "Tags": [
            {"Key": "Name", "Value": "staging-sdwan-connect"},
            {"Key": "Environment", "Value": "staging"},
            {"Key": "Type", "Value": "sd-wan"},
        ],
        "ProposedSegmentChange": None,
        "ProposedNetworkFunctionGroupChange": None,
        "CreatedAt": "2024-02-15T09:45:00+00:00",
        "UpdatedAt": "2024-02-15T09:50:00+00:00",
        "ConnectOptions": {
            "Protocol": "GRE",
            "TransportAttachmentId": "attachment-0shared12345",
        },
    },
    # Development Connect Attachment - ap-southeast-2
    "attachment-0connectdev12": {
        "AttachmentId": "attachment-0connectdev12",
        "CoreNetworkId": "core-network-0global123",
        "CoreNetworkArn": "arn:aws:networkmanager::123456789012:core-network/core-network-0global123",
        "AttachmentType": "CONNECT",
        "State": "AVAILABLE",
        "EdgeLocation": "ap-southeast-2",
        "ResourceArn": "arn:aws:networkmanager::123456789012:attachment/attachment-0tgwpeer1234",
        "AttachmentPolicyRuleNumber": 100,
        "SegmentName": "staging",
        "Tags": [
            {"Key": "Name", "Value": "dev-third-party-connect"},
            {"Key": "Environment", "Value": "development"},
            {"Key": "Type", "Value": "third-party-appliance"},
        ],
        "ProposedSegmentChange": None,
        "ProposedNetworkFunctionGroupChange": None,
        "CreatedAt": "2024-02-20T08:00:00+00:00",
        "UpdatedAt": "2024-02-20T08:05:00+00:00",
        "ConnectOptions": {
            "Protocol": "GRE",
            "TransportAttachmentId": "attachment-0tgwpeer1234",
        },
    },
    # Branch Office Connect Attachment - us-east-1
    "attachment-0connectbrnch": {
        "AttachmentId": "attachment-0connectbrnch",
        "CoreNetworkId": "core-network-0global123",
        "CoreNetworkArn": "arn:aws:networkmanager::123456789012:core-network/core-network-0global123",
        "AttachmentType": "CONNECT",
        "State": "AVAILABLE",
        "EdgeLocation": "us-east-1",
        "ResourceArn": "arn:aws:networkmanager::123456789012:attachment/attachment-0stagvpc1234",
        "AttachmentPolicyRuleNumber": 100,
        "SegmentName": "production",
        "Tags": [
            {"Key": "Name", "Value": "branch-office-connect"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "Type", "Value": "branch-sd-wan"},
        ],
        "ProposedSegmentChange": None,
        "ProposedNetworkFunctionGroupChange": None,
        "CreatedAt": "2024-03-01T13:45:00+00:00",
        "UpdatedAt": "2024-03-01T13:50:00+00:00",
        "ConnectOptions": {
            "Protocol": "GRE",
            "TransportAttachmentId": "attachment-0stagvpc1234",
        },
    },
    # Multi-BGP Connect Attachment - eu-west-1
    "attachment-0connectmulti": {
        "AttachmentId": "attachment-0connectmulti",
        "CoreNetworkId": "core-network-0global123",
        "CoreNetworkArn": "arn:aws:networkmanager::123456789012:core-network/core-network-0global123",
        "AttachmentType": "CONNECT",
        "State": "AVAILABLE",
        "EdgeLocation": "eu-west-1",
        "ResourceArn": "arn:aws:networkmanager::123456789012:attachment/attachment-0prodvpc1234",
        "AttachmentPolicyRuleNumber": 100,
        "SegmentName": "production",
        "Tags": [
            {"Key": "Name", "Value": "multi-session-connect"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "Type", "Value": "dual-bgp"},
        ],
        "ProposedSegmentChange": None,
        "ProposedNetworkFunctionGroupChange": None,
        "CreatedAt": "2024-03-05T08:45:00+00:00",
        "UpdatedAt": "2024-03-05T08:50:00+00:00",
        "ConnectOptions": {
            "Protocol": "GRE",
            "TransportAttachmentId": "attachment-0prodvpc1234",
        },
    },
    # Creating Connect Attachment - ap-southeast-2
    "attachment-0connectnew12": {
        "AttachmentId": "attachment-0connectnew12",
        "CoreNetworkId": "core-network-0global123",
        "CoreNetworkArn": "arn:aws:networkmanager::123456789012:core-network/core-network-0global123",
        "AttachmentType": "CONNECT",
        "State": "CREATING",
        "EdgeLocation": "ap-southeast-2",
        "ResourceArn": "arn:aws:networkmanager::123456789012:attachment/attachment-0tgwpeer1234",
        "AttachmentPolicyRuleNumber": 100,
        "SegmentName": "production",
        "Tags": [
            {"Key": "Name", "Value": "new-branch-connect"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "Type", "Value": "branch-expansion"},
        ],
        "ProposedSegmentChange": None,
        "ProposedNetworkFunctionGroupChange": None,
        "CreatedAt": "2024-03-10T15:45:00+00:00",
        "UpdatedAt": "2024-03-10T15:50:00+00:00",
        "ConnectOptions": {
            "Protocol": "GRE",
            "TransportAttachmentId": "attachment-0tgwpeer1234",
        },
    },
    # Deleting Connect Attachment - us-east-1
    "attachment-0connectold12": {
        "AttachmentId": "attachment-0connectold12",
        "CoreNetworkId": "core-network-0global123",
        "CoreNetworkArn": "arn:aws:networkmanager::123456789012:core-network/core-network-0global123",
        "AttachmentType": "CONNECT",
        "State": "DELETING",
        "EdgeLocation": "us-east-1",
        "ResourceArn": "arn:aws:networkmanager::123456789012:attachment/attachment-0stagvpc1234",
        "AttachmentPolicyRuleNumber": 100,
        "SegmentName": "production",
        "Tags": [
            {"Key": "Name", "Value": "deprecated-connect"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "Status", "Value": "decommissioned"},
        ],
        "ProposedSegmentChange": None,
        "ProposedNetworkFunctionGroupChange": None,
        "CreatedAt": "2023-12-01T09:45:00+00:00",
        "UpdatedAt": "2024-03-10T17:00:00+00:00",
        "ConnectOptions": {
            "Protocol": "GRE",
            "TransportAttachmentId": "attachment-0stagvpc1234",
        },
    },
    # High-ASN Connect Attachment - eu-west-1
    "attachment-0connecthigh1": {
        "AttachmentId": "attachment-0connecthigh1",
        "CoreNetworkId": "core-network-0global123",
        "CoreNetworkArn": "arn:aws:networkmanager::123456789012:core-network/core-network-0global123",
        "AttachmentType": "CONNECT",
        "State": "AVAILABLE",
        "EdgeLocation": "eu-west-1",
        "ResourceArn": "arn:aws:networkmanager::123456789012:attachment/attachment-0shared12345",
        "AttachmentPolicyRuleNumber": 100,
        "SegmentName": "production",
        "Tags": [
            {"Key": "Name", "Value": "isp-interconnect-connect"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "Type", "Value": "carrier-interconnect"},
        ],
        "ProposedSegmentChange": None,
        "ProposedNetworkFunctionGroupChange": None,
        "CreatedAt": "2024-03-08T10:45:00+00:00",
        "UpdatedAt": "2024-03-08T10:50:00+00:00",
        "ConnectOptions": {
            "Protocol": "GRE",
            "TransportAttachmentId": "attachment-0shared12345",
        },
    },
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_connect_peer_by_id(peer_id: str) -> dict[str, Any] | None:
    """Get Connect Peer fixture by ID."""
    return CONNECT_PEER_FIXTURES.get(peer_id)


def get_connect_peers_by_attachment(attachment_id: str) -> list[dict[str, Any]]:
    """Get all Connect Peers for a specific Connect attachment."""
    return [
        peer
        for peer in CONNECT_PEER_FIXTURES.values()
        if peer["ConnectAttachmentId"] == attachment_id
    ]


def get_connect_peers_by_core_network(core_network_id: str) -> list[dict[str, Any]]:
    """Get all Connect Peers for a Core Network."""
    return [
        peer
        for peer in CONNECT_PEER_FIXTURES.values()
        if peer["CoreNetworkId"] == core_network_id
    ]


def get_connect_peers_by_edge_location(edge_location: str) -> list[dict[str, Any]]:
    """Get all Connect Peers in a specific edge location (region)."""
    return [
        peer
        for peer in CONNECT_PEER_FIXTURES.values()
        if peer["EdgeLocation"] == edge_location
    ]


def get_connect_peers_by_state(state: str) -> list[dict[str, Any]]:
    """Get all Connect Peers with a specific state (AVAILABLE, CREATING, DELETING)."""
    return [peer for peer in CONNECT_PEER_FIXTURES.values() if peer["State"] == state]


def get_connect_peers_by_asn(peer_asn: int) -> list[dict[str, Any]]:
    """Get all Connect Peers with a specific peer ASN."""
    peers = []
    for peer in CONNECT_PEER_FIXTURES.values():
        for bgp in peer.get("Configuration", {}).get("BgpConfigurations", []):
            if bgp.get("PeerAsn") == peer_asn:
                peers.append(peer)
                break
    return peers


def get_connect_attachment_by_id(attachment_id: str) -> dict[str, Any] | None:
    """Get Connect Attachment fixture by ID."""
    return CONNECT_ATTACHMENT_FIXTURES.get(attachment_id)


def get_connect_attachments_by_core_network(
    core_network_id: str,
) -> list[dict[str, Any]]:
    """Get all Connect Attachments for a Core Network."""
    return [
        att
        for att in CONNECT_ATTACHMENT_FIXTURES.values()
        if att["CoreNetworkId"] == core_network_id
    ]


def get_connect_attachments_by_transport(
    transport_attachment_id: str,
) -> list[dict[str, Any]]:
    """Get all Connect Attachments using a specific transport attachment."""
    return [
        att
        for att in CONNECT_ATTACHMENT_FIXTURES.values()
        if att.get("ConnectOptions", {}).get("TransportAttachmentId")
        == transport_attachment_id
    ]


def get_connect_attachments_by_segment(segment_name: str) -> list[dict[str, Any]]:
    """Get all Connect Attachments in a specific segment."""
    return [
        att
        for att in CONNECT_ATTACHMENT_FIXTURES.values()
        if att.get("SegmentName") == segment_name
    ]


def get_bgp_configuration_summary() -> dict[str, Any]:
    """Get summary of all BGP configurations across all Connect Peers."""
    summary = {
        "total_peers": len(CONNECT_PEER_FIXTURES),
        "total_bgp_sessions": 0,
        "asn_distribution": {},
        "protocol_types": {},
        "edge_location_distribution": {},
        "state_distribution": {},
    }

    for peer in CONNECT_PEER_FIXTURES.values():
        # Count BGP sessions
        bgp_configs = peer.get("Configuration", {}).get("BgpConfigurations", [])
        summary["total_bgp_sessions"] += len(bgp_configs)

        # Track ASNs
        for bgp in bgp_configs:
            peer_asn = bgp.get("PeerAsn")
            summary["asn_distribution"][peer_asn] = (
                summary["asn_distribution"].get(peer_asn, 0) + 1
            )

        # Protocol distribution
        protocol = peer.get("Configuration", {}).get("Protocol", "UNKNOWN")
        summary["protocol_types"][protocol] = (
            summary["protocol_types"].get(protocol, 0) + 1
        )

        # Edge location distribution
        location = peer.get("EdgeLocation", "UNKNOWN")
        summary["edge_location_distribution"][location] = (
            summary["edge_location_distribution"].get(location, 0) + 1
        )

        # State distribution
        state = peer.get("State", "UNKNOWN")
        summary["state_distribution"][state] = (
            summary["state_distribution"].get(state, 0) + 1
        )

    return summary


def get_redundant_peers() -> dict[str, list[dict[str, Any]]]:
    """Identify redundant Connect Peer configurations (same attachment, different peers)."""
    attachment_peers: dict[str, list[dict[str, Any]]] = {}

    for peer in CONNECT_PEER_FIXTURES.values():
        attachment_id = peer["ConnectAttachmentId"]
        if attachment_id not in attachment_peers:
            attachment_peers[attachment_id] = []
        attachment_peers[attachment_id].append(peer)

    # Return only attachments with multiple peers (redundant configurations)
    return {k: v for k, v in attachment_peers.items() if len(v) > 1}


def get_peers_requiring_4byte_asn_support() -> list[dict[str, Any]]:
    """Get all Connect Peers using 4-byte ASN format (ASN > 65535)."""
    peers = []
    for peer in CONNECT_PEER_FIXTURES.values():
        for bgp in peer.get("Configuration", {}).get("BgpConfigurations", []):
            if bgp.get("PeerAsn", 0) > 65535:
                peers.append(peer)
                break
    return peers
