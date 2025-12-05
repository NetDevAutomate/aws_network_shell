"""Realistic CloudWAN mock data fixtures.

Multi-region CloudWAN architecture:
- Global Network spanning eu-west-1, us-east-1, ap-southeast-2
- Core Network with production, staging, and shared segments
- VPC attachments across regions
- Network Function Groups (NFGs) for inspection
- Comprehensive routing tables and policies
"""

from typing import Any

# =============================================================================
# CLOUDWAN FIXTURES
# =============================================================================

CLOUDWAN_FIXTURES: dict[str, dict[str, Any]] = {
    # Global Production Core Network
    "core-network-0global123": {
        "CoreNetworkId": "core-network-0global123",
        "CoreNetworkArn": "arn:aws:networkmanager::123456789012:core-network/core-network-0global123",
        "GlobalNetworkId": "global-network-0prod123",
        "Description": "Production Global Core Network",
        "CreatedAt": "2024-01-10T08:00:00+00:00",
        "State": "AVAILABLE",
        "Segments": [
            {
                "Name": "production",
                "EdgeLocations": ["eu-west-1", "us-east-1", "ap-southeast-2"],
                "SharedSegments": [],
            },
            {
                "Name": "staging",
                "EdgeLocations": ["us-east-1", "ap-southeast-2"],
                "SharedSegments": [],
            },
            {
                "Name": "shared-services",
                "EdgeLocations": ["eu-west-1", "us-east-1"],
                "SharedSegments": ["production", "staging"],
            },
            {
                "Name": "inspection",
                "EdgeLocations": ["eu-west-1", "us-east-1"],
                "SharedSegments": [],
            },
        ],
        "NetworkFunctionGroups": [
            {
                "Name": "firewall-inspection",
                "RequireAttachmentAcceptance": False,
            },
        ],
        "Edges": [
            {
                "EdgeLocation": "eu-west-1",
                "Asn": 64520,
                "InsideCidrBlocks": ["169.254.0.0/24"],
            },
            {
                "EdgeLocation": "us-east-1",
                "Asn": 64521,
                "InsideCidrBlocks": ["169.254.1.0/24"],
            },
            {
                "EdgeLocation": "ap-southeast-2",
                "Asn": 64522,
                "InsideCidrBlocks": ["169.254.2.0/24"],
            },
        ],
        "Tags": [
            {"Key": "Name", "Value": "production-core-network"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "ManagedBy", "Value": "terraform"},
        ],
    },
}

# =============================================================================
# CLOUDWAN ATTACHMENT FIXTURES
# =============================================================================

CLOUDWAN_ATTACHMENT_FIXTURES: dict[str, dict[str, Any]] = {
    # Production VPC Attachment - eu-west-1
    "attachment-0prodvpc1234": {
        "AttachmentId": "attachment-0prodvpc1234",
        "CoreNetworkId": "core-network-0global123",
        "CoreNetworkArn": "arn:aws:networkmanager::123456789012:core-network/core-network-0global123",
        "AttachmentType": "VPC",
        "State": "AVAILABLE",
        "EdgeLocation": "eu-west-1",
        "ResourceArn": "arn:aws:ec2:eu-west-1:123456789012:vpc/vpc-0prod1234567890ab",
        "AttachmentPolicyRuleNumber": 100,
        "SegmentName": "production",
        "Tags": [
            {"Key": "Name", "Value": "production-vpc-attachment"},
            {"Key": "Environment", "Value": "production"},
        ],
        "ProposedSegmentChange": None,
        "ProposedNetworkFunctionGroupChange": None,
        "CreatedAt": "2024-01-11T09:00:00+00:00",
        "UpdatedAt": "2024-01-11T09:05:00+00:00",
        "VpcOptions": {
            "VpcId": "vpc-0prod1234567890ab",
            "SubnetArns": [
                "arn:aws:ec2:eu-west-1:123456789012:subnet/subnet-0tgw1a1234567890",
                "arn:aws:ec2:eu-west-1:123456789012:subnet/subnet-0tgw1b1234567890",
            ],
            "Ipv6Support": False,
            "ApplianceModeSupport": False,
        },
    },
    # Staging VPC Attachment - us-east-1
    "attachment-0stagvpc1234": {
        "AttachmentId": "attachment-0stagvpc1234",
        "CoreNetworkId": "core-network-0global123",
        "CoreNetworkArn": "arn:aws:networkmanager::123456789012:core-network/core-network-0global123",
        "AttachmentType": "VPC",
        "State": "AVAILABLE",
        "EdgeLocation": "us-east-1",
        "ResourceArn": "arn:aws:ec2:us-east-1:123456789012:vpc/vpc-0stag1234567890ab",
        "AttachmentPolicyRuleNumber": 100,
        "SegmentName": "staging",
        "Tags": [
            {"Key": "Name", "Value": "staging-vpc-attachment"},
            {"Key": "Environment", "Value": "staging"},
        ],
        "ProposedSegmentChange": None,
        "ProposedNetworkFunctionGroupChange": None,
        "CreatedAt": "2024-02-02T11:00:00+00:00",
        "UpdatedAt": "2024-02-02T11:05:00+00:00",
        "VpcOptions": {
            "VpcId": "vpc-0stag1234567890ab",
            "SubnetArns": [
                "arn:aws:ec2:us-east-1:123456789012:subnet/subnet-0stgtgw1a123456",
                "arn:aws:ec2:us-east-1:123456789012:subnet/subnet-0stgtgw1b123456",
            ],
            "Ipv6Support": False,
            "ApplianceModeSupport": False,
        },
    },
    # Shared Services VPC Attachment - eu-west-1
    "attachment-0shared12345": {
        "AttachmentId": "attachment-0shared12345",
        "CoreNetworkId": "core-network-0global123",
        "CoreNetworkArn": "arn:aws:networkmanager::123456789012:core-network/core-network-0global123",
        "AttachmentType": "VPC",
        "State": "AVAILABLE",
        "EdgeLocation": "eu-west-1",
        "ResourceArn": "arn:aws:ec2:eu-west-1:123456789012:vpc/vpc-0shared123456789a",
        "AttachmentPolicyRuleNumber": 100,
        "SegmentName": "shared-services",
        "Tags": [
            {"Key": "Name", "Value": "shared-services-attachment"},
            {"Key": "Environment", "Value": "shared"},
        ],
        "ProposedSegmentChange": None,
        "ProposedNetworkFunctionGroupChange": None,
        "CreatedAt": "2024-01-12T10:00:00+00:00",
        "UpdatedAt": "2024-01-12T10:05:00+00:00",
        "VpcOptions": {
            "VpcId": "vpc-0shared123456789a",
            "SubnetArns": [
                "arn:aws:ec2:eu-west-1:123456789012:subnet/subnet-0sharedtgw1a12",
                "arn:aws:ec2:eu-west-1:123456789012:subnet/subnet-0sharedtgw1b12",
            ],
            "Ipv6Support": False,
            "ApplianceModeSupport": False,
        },
    },
    # Network Firewall VPC Attachment (NFG) - eu-west-1
    "attachment-0firewall123": {
        "AttachmentId": "attachment-0firewall123",
        "CoreNetworkId": "core-network-0global123",
        "CoreNetworkArn": "arn:aws:networkmanager::123456789012:core-network/core-network-0global123",
        "AttachmentType": "VPC",
        "State": "AVAILABLE",
        "EdgeLocation": "eu-west-1",
        "ResourceArn": "arn:aws:ec2:eu-west-1:123456789012:vpc/vpc-0firewall1234567",
        "AttachmentPolicyRuleNumber": 200,
        "SegmentName": "inspection",
        "NetworkFunctionGroupName": "firewall-inspection",
        "Tags": [
            {"Key": "Name", "Value": "firewall-vpc-attachment"},
            {"Key": "Purpose", "Value": "inspection"},
        ],
        "ProposedSegmentChange": None,
        "ProposedNetworkFunctionGroupChange": None,
        "CreatedAt": "2024-01-22T09:00:00+00:00",
        "UpdatedAt": "2024-01-22T09:05:00+00:00",
        "VpcOptions": {
            "VpcId": "vpc-0firewall1234567",
            "SubnetArns": [
                "arn:aws:ec2:eu-west-1:123456789012:subnet/subnet-0fwtgw1a123456",
                "arn:aws:ec2:eu-west-1:123456789012:subnet/subnet-0fwtgw1b123456",
            ],
            "Ipv6Support": False,
            "ApplianceModeSupport": True,
        },
    },
    # VPN Attachment to On-Premises - eu-west-1
    "attachment-0vpn012345678": {
        "AttachmentId": "attachment-0vpn012345678",
        "CoreNetworkId": "core-network-0global123",
        "CoreNetworkArn": "arn:aws:networkmanager::123456789012:core-network/core-network-0global123",
        "AttachmentType": "SITE_TO_SITE_VPN",
        "State": "AVAILABLE",
        "EdgeLocation": "eu-west-1",
        "ResourceArn": "arn:aws:ec2:eu-west-1:123456789012:vpn-connection/vpn-0prod12345678901",
        "AttachmentPolicyRuleNumber": 150,
        "SegmentName": "production",
        "Tags": [
            {"Key": "Name", "Value": "onprem-vpn-attachment"},
            {"Key": "Destination", "Value": "datacenter-dublin"},
        ],
        "ProposedSegmentChange": None,
        "ProposedNetworkFunctionGroupChange": None,
        "CreatedAt": "2024-01-18T15:00:00+00:00",
        "UpdatedAt": "2024-01-18T15:05:00+00:00",
    },
    # Connect Attachment (SD-WAN) - us-east-1
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
    # Transit Gateway Peering Attachment
    "attachment-0tgwpeer1234": {
        "AttachmentId": "attachment-0tgwpeer1234",
        "CoreNetworkId": "core-network-0global123",
        "CoreNetworkArn": "arn:aws:networkmanager::123456789012:core-network/core-network-0global123",
        "AttachmentType": "TRANSIT_GATEWAY_ROUTE_TABLE",
        "State": "AVAILABLE",
        "EdgeLocation": "ap-southeast-2",
        "ResourceArn": "arn:aws:ec2:ap-southeast-2:123456789012:transit-gateway-route-table/tgw-rtb-0dev012345678",
        "AttachmentPolicyRuleNumber": 100,
        "SegmentName": "staging",
        "Tags": [
            {"Key": "Name", "Value": "dev-tgw-peering"},
            {"Key": "Environment", "Value": "development"},
        ],
        "ProposedSegmentChange": None,
        "ProposedNetworkFunctionGroupChange": None,
        "CreatedAt": "2024-02-15T14:00:00+00:00",
        "UpdatedAt": "2024-02-15T14:05:00+00:00",
        "TransitGatewayRouteTableOptions": {
            "TransitGatewayRouteTableArn": "arn:aws:ec2:ap-southeast-2:123456789012:transit-gateway-route-table/tgw-rtb-0dev012345678",
            "PeeringId": "pcx-0dev012345678901",
        },
    },
}

# =============================================================================
# CLOUDWAN SEGMENT FIXTURES
# =============================================================================

CLOUDWAN_SEGMENT_FIXTURES: dict[str, dict[str, Any]] = {
    "production": {
        "Name": "production",
        "Description": "Production workload segment",
        "EdgeLocations": ["eu-west-1", "us-east-1", "ap-southeast-2"],
        "SharedSegments": [],
        "RequireAttachmentAcceptance": True,
        "IsolateAttachments": False,
        "Tags": [
            {"Key": "Name", "Value": "production-segment"},
            {"Key": "Environment", "Value": "production"},
        ],
    },
    "staging": {
        "Name": "staging",
        "Description": "Staging and testing segment",
        "EdgeLocations": ["us-east-1", "ap-southeast-2"],
        "SharedSegments": [],
        "RequireAttachmentAcceptance": False,
        "IsolateAttachments": False,
        "Tags": [
            {"Key": "Name", "Value": "staging-segment"},
            {"Key": "Environment", "Value": "staging"},
        ],
    },
    "shared-services": {
        "Name": "shared-services",
        "Description": "Shared services accessible by all segments",
        "EdgeLocations": ["eu-west-1", "us-east-1"],
        "SharedSegments": ["production", "staging"],
        "RequireAttachmentAcceptance": False,
        "IsolateAttachments": False,
        "Tags": [
            {"Key": "Name", "Value": "shared-services-segment"},
            {"Key": "Environment", "Value": "shared"},
        ],
    },
    "inspection": {
        "Name": "inspection",
        "Description": "Network firewall inspection segment",
        "EdgeLocations": ["eu-west-1", "us-east-1"],
        "SharedSegments": [],
        "RequireAttachmentAcceptance": True,
        "IsolateAttachments": True,
        "Tags": [
            {"Key": "Name", "Value": "inspection-segment"},
            {"Key": "Purpose", "Value": "security"},
        ],
    },
}

# =============================================================================
# CLOUDWAN ROUTE TABLE FIXTURES (by segment and region)
# =============================================================================

CLOUDWAN_ROUTE_TABLE_FIXTURES: dict[str, dict[str, Any]] = {
    # Production Segment - eu-west-1
    "production-eu-west-1": {
        "CoreNetworkId": "core-network-0global123",
        "SegmentName": "production",
        "EdgeLocation": "eu-west-1",
        "Routes": [
            {
                "DestinationCidrBlock": "10.0.0.0/16",
                "Destinations": [
                    {
                        "AttachmentId": "attachment-0prodvpc1234",
                        "ResourceType": "VPC",
                        "ResourceId": "vpc-0prod1234567890ab",
                    }
                ],
                "Type": "PROPAGATED",
                "State": "ACTIVE",
            },
            {
                "DestinationCidrBlock": "192.168.0.0/16",
                "Destinations": [
                    {
                        "AttachmentId": "attachment-0vpn012345678",
                        "ResourceType": "VPN",
                        "ResourceId": "vpn-0prod12345678901",
                    }
                ],
                "Type": "PROPAGATED",
                "State": "ACTIVE",
            },
            {
                "DestinationCidrBlock": "10.100.0.0/16",
                "Destinations": [
                    {
                        "AttachmentId": "attachment-0shared12345",
                        "ResourceType": "VPC",
                        "ResourceId": "vpc-0shared123456789a",
                        "SegmentName": "shared-services",
                    }
                ],
                "Type": "STATIC",
                "State": "ACTIVE",
            },
            {
                "DestinationCidrBlock": "0.0.0.0/0",
                "Destinations": [
                    {
                        "AttachmentId": "attachment-0firewall123",
                        "ResourceType": "VPC",
                        "ResourceId": "vpc-0firewall1234567",
                        "NetworkFunctionGroupName": "firewall-inspection",
                    }
                ],
                "Type": "STATIC",
                "State": "ACTIVE",
            },
        ],
    },
    # Production Segment - us-east-1
    "production-us-east-1": {
        "CoreNetworkId": "core-network-0global123",
        "SegmentName": "production",
        "EdgeLocation": "us-east-1",
        "Routes": [
            {
                "DestinationCidrBlock": "10.0.0.0/16",
                "Destinations": [
                    {
                        "CoreNetworkEdge": "eu-west-1",
                        "Type": "CORE_NETWORK_EDGE",
                    }
                ],
                "Type": "PROPAGATED",
                "State": "ACTIVE",
            },
            {
                "DestinationCidrBlock": "10.100.0.0/16",
                "Destinations": [
                    {
                        "SegmentName": "shared-services",
                        "Type": "SEGMENT",
                    }
                ],
                "Type": "STATIC",
                "State": "ACTIVE",
            },
        ],
    },
    # Staging Segment - us-east-1
    "staging-us-east-1": {
        "CoreNetworkId": "core-network-0global123",
        "SegmentName": "staging",
        "EdgeLocation": "us-east-1",
        "Routes": [
            {
                "DestinationCidrBlock": "10.1.0.0/16",
                "Destinations": [
                    {
                        "AttachmentId": "attachment-0stagvpc1234",
                        "ResourceType": "VPC",
                        "ResourceId": "vpc-0stag1234567890ab",
                    }
                ],
                "Type": "PROPAGATED",
                "State": "ACTIVE",
            },
            {
                "DestinationCidrBlock": "10.100.0.0/16",
                "Destinations": [
                    {
                        "SegmentName": "shared-services",
                        "Type": "SEGMENT",
                    }
                ],
                "Type": "STATIC",
                "State": "ACTIVE",
            },
        ],
    },
    # Shared Services Segment - eu-west-1
    "shared-services-eu-west-1": {
        "CoreNetworkId": "core-network-0global123",
        "SegmentName": "shared-services",
        "EdgeLocation": "eu-west-1",
        "Routes": [
            {
                "DestinationCidrBlock": "10.100.0.0/16",
                "Destinations": [
                    {
                        "AttachmentId": "attachment-0shared12345",
                        "ResourceType": "VPC",
                        "ResourceId": "vpc-0shared123456789a",
                    }
                ],
                "Type": "PROPAGATED",
                "State": "ACTIVE",
            },
            {
                "DestinationCidrBlock": "10.0.0.0/16",
                "Destinations": [
                    {
                        "SegmentName": "production",
                        "Type": "SEGMENT",
                    }
                ],
                "Type": "STATIC",
                "State": "ACTIVE",
            },
            {
                "DestinationCidrBlock": "10.1.0.0/16",
                "Destinations": [
                    {
                        "SegmentName": "staging",
                        "Type": "SEGMENT",
                    }
                ],
                "Type": "STATIC",
                "State": "ACTIVE",
            },
        ],
    },
    # Inspection Segment - eu-west-1
    "inspection-eu-west-1": {
        "CoreNetworkId": "core-network-0global123",
        "SegmentName": "inspection",
        "EdgeLocation": "eu-west-1",
        "Routes": [
            {
                "DestinationCidrBlock": "10.0.0.0/8",
                "Destinations": [
                    {
                        "SegmentName": "production",
                        "Type": "SEGMENT",
                    }
                ],
                "Type": "STATIC",
                "State": "ACTIVE",
            },
            {
                "DestinationCidrBlock": "0.0.0.0/0",
                "Destinations": [
                    {
                        "AttachmentId": "attachment-0prodvpc1234",
                        "ResourceType": "VPC",
                        "ResourceId": "vpc-0prod1234567890ab",
                    }
                ],
                "Type": "STATIC",
                "State": "ACTIVE",
            },
        ],
    },
}

# =============================================================================
# CLOUDWAN POLICY FIXTURE
# =============================================================================

CLOUDWAN_POLICY_FIXTURE: dict[str, Any] = {
    "PolicyDocument": {
        "version": "2021.12",
        "core-network-configuration": {
            "asn-ranges": ["64512-64555"],
            "edge-locations": [
                {"location": "eu-west-1"},
                {"location": "us-east-1"},
                {"location": "ap-southeast-2"},
            ],
            "vpn-ecmp-support": True,
        },
        "segments": [
            {
                "name": "production",
                "description": "Production workload segment",
                "require-attachment-acceptance": True,
                "isolate-attachments": False,
            },
            {
                "name": "staging",
                "description": "Staging and testing segment",
                "require-attachment-acceptance": False,
                "isolate-attachments": False,
            },
            {
                "name": "shared-services",
                "description": "Shared services segment",
                "require-attachment-acceptance": False,
                "isolate-attachments": False,
            },
            {
                "name": "inspection",
                "description": "Network firewall inspection segment",
                "require-attachment-acceptance": True,
                "isolate-attachments": True,
            },
        ],
        "network-function-groups": [
            {
                "name": "firewall-inspection",
                "description": "Network firewall inspection NFG",
                "require-attachment-acceptance": False,
            }
        ],
        "segment-actions": [
            {
                "action": "share",
                "mode": "attachment-route",
                "segment": "shared-services",
                "share-with": ["production", "staging"],
            },
            {
                "action": "send-via",
                "mode": "dual-hop",
                "segment": "production",
                "via": {
                    "network-function-groups": ["firewall-inspection"],
                },
                "when-sent-to": {
                    "segments": ["*"],
                },
            },
        ],
        "attachment-policies": [
            {
                "rule-number": 100,
                "conditions": [
                    {
                        "type": "tag-value",
                        "key": "Environment",
                        "operator": "equals",
                        "value": "production",
                    }
                ],
                "action": {
                    "association-method": "constant",
                    "segment": "production",
                },
            },
            {
                "rule-number": 110,
                "conditions": [
                    {
                        "type": "tag-value",
                        "key": "Environment",
                        "operator": "equals",
                        "value": "staging",
                    }
                ],
                "action": {
                    "association-method": "constant",
                    "segment": "staging",
                },
            },
            {
                "rule-number": 120,
                "conditions": [
                    {
                        "type": "tag-value",
                        "key": "Environment",
                        "operator": "equals",
                        "value": "shared",
                    }
                ],
                "action": {
                    "association-method": "constant",
                    "segment": "shared-services",
                },
            },
            {
                "rule-number": 200,
                "conditions": [
                    {
                        "type": "tag-value",
                        "key": "Purpose",
                        "operator": "equals",
                        "value": "inspection",
                    }
                ],
                "action": {
                    "association-method": "constant",
                    "segment": "inspection",
                    "network-function-group": "firewall-inspection",
                },
            },
        ],
    },
    "PolicyVersionId": 1,
    "ChangeSetState": "READY_TO_EXECUTE",
    "Description": "Production CloudWAN policy with inspection",
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_core_network_by_id(core_network_id: str) -> dict[str, Any] | None:
    """Get Core Network fixture by ID."""
    return CLOUDWAN_FIXTURES.get(core_network_id)


def get_core_network_detail(core_network_id: str) -> dict[str, Any] | None:
    """Get comprehensive Core Network detail with all associated resources."""
    core_network = CLOUDWAN_FIXTURES.get(core_network_id)
    if not core_network:
        return None

    # Gather associated attachments
    attachments = [
        a
        for a in CLOUDWAN_ATTACHMENT_FIXTURES.values()
        if a["CoreNetworkId"] == core_network_id
    ]

    # Get segments
    segments = list(CLOUDWAN_SEGMENT_FIXTURES.values())

    # Get route tables
    route_tables = list(CLOUDWAN_ROUTE_TABLE_FIXTURES.values())

    # Get policy
    policy = CLOUDWAN_POLICY_FIXTURE

    return {
        "core_network": core_network,
        "attachments": attachments,
        "segments": segments,
        "route_tables": route_tables,
        "policy": policy,
    }


def get_attachments_by_core_network(core_network_id: str) -> list[dict[str, Any]]:
    """Get all attachments for a Core Network."""
    return [
        a
        for a in CLOUDWAN_ATTACHMENT_FIXTURES.values()
        if a["CoreNetworkId"] == core_network_id
    ]


def get_attachments_by_segment(segment_name: str) -> list[dict[str, Any]]:
    """Get all attachments for a specific segment."""
    return [
        a
        for a in CLOUDWAN_ATTACHMENT_FIXTURES.values()
        if a.get("SegmentName") == segment_name
    ]


def get_route_table_by_segment_and_region(
    segment_name: str, edge_location: str
) -> dict[str, Any] | None:
    """Get route table for specific segment and region."""
    key = f"{segment_name}-{edge_location}"
    return CLOUDWAN_ROUTE_TABLE_FIXTURES.get(key)


def get_attachment_by_id(attachment_id: str) -> dict[str, Any] | None:
    """Get CloudWAN attachment by ID."""
    return CLOUDWAN_ATTACHMENT_FIXTURES.get(attachment_id)
