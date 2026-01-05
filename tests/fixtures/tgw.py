"""Realistic Transit Gateway mock data fixtures.

Multi-region Transit Gateway architecture:
- eu-west-1: Production TGW with VPC, VPN, and peering attachments
- us-east-1: Staging TGW peered with Production
- Shared Services connectivity via TGW

Includes:
- Transit Gateways with route tables
- VPC attachments
- VPN attachments
- Peering attachments
- Route propagations and associations
"""

from typing import Any

# =============================================================================
# TRANSIT GATEWAY FIXTURES
# =============================================================================

TGW_FIXTURES: dict[str, dict[str, Any]] = {
    # Production Transit Gateway - eu-west-1
    "tgw-0prod12345678901": {
        "TransitGatewayId": "tgw-0prod12345678901",
        "TransitGatewayArn": "arn:aws:ec2:eu-west-1:123456789012:transit-gateway/tgw-0prod12345678901",
        "State": "available",
        "OwnerId": "123456789012",
        "Description": "Production Transit Gateway - eu-west-1",
        "CreationTime": "2024-01-15T10:30:00+00:00",
        "Options": {
            "AmazonSideAsn": 64512,
            "AutoAcceptSharedAttachments": "disable",
            "DefaultRouteTableAssociation": "enable",
            "AssociationDefaultRouteTableId": "tgw-rtb-0proddefault123",
            "DefaultRouteTablePropagation": "enable",
            "PropagationDefaultRouteTableId": "tgw-rtb-0proddefault123",
            "VpnEcmpSupport": "enable",
            "DnsSupport": "enable",
            "MulticastSupport": "disable",
        },
        "Tags": [
            {"Key": "Name", "Value": "production-tgw"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "Region", "Value": "eu-west-1"},
            {"Key": "ManagedBy", "Value": "terraform"},
        ],
    },
    # Staging Transit Gateway - us-east-1
    "tgw-0stag12345678901": {
        "TransitGatewayId": "tgw-0stag12345678901",
        "TransitGatewayArn": "arn:aws:ec2:us-east-1:123456789012:transit-gateway/tgw-0stag12345678901",
        "State": "available",
        "OwnerId": "123456789012",
        "Description": "Staging Transit Gateway - us-east-1",
        "CreationTime": "2024-02-01T14:00:00+00:00",
        "Options": {
            "AmazonSideAsn": 64513,
            "AutoAcceptSharedAttachments": "disable",
            "DefaultRouteTableAssociation": "enable",
            "AssociationDefaultRouteTableId": "tgw-rtb-0stagdefault123",
            "DefaultRouteTablePropagation": "enable",
            "PropagationDefaultRouteTableId": "tgw-rtb-0stagdefault123",
            "VpnEcmpSupport": "enable",
            "DnsSupport": "enable",
            "MulticastSupport": "disable",
        },
        "Tags": [
            {"Key": "Name", "Value": "staging-tgw"},
            {"Key": "Environment", "Value": "staging"},
            {"Key": "Region", "Value": "us-east-1"},
            {"Key": "ManagedBy", "Value": "terraform"},
        ],
    },
    # Inspection TGW for Network Firewall - eu-west-1
    "tgw-0insp12345678901": {
        "TransitGatewayId": "tgw-0insp12345678901",
        "TransitGatewayArn": "arn:aws:ec2:eu-west-1:123456789012:transit-gateway/tgw-0insp12345678901",
        "State": "available",
        "OwnerId": "123456789012",
        "Description": "Inspection Transit Gateway for Network Firewall",
        "CreationTime": "2024-01-20T08:00:00+00:00",
        "Options": {
            "AmazonSideAsn": 64514,
            "AutoAcceptSharedAttachments": "disable",
            "DefaultRouteTableAssociation": "disable",
            "DefaultRouteTablePropagation": "disable",
            "VpnEcmpSupport": "enable",
            "DnsSupport": "enable",
            "MulticastSupport": "disable",
        },
        "Tags": [
            {"Key": "Name", "Value": "inspection-tgw"},
            {"Key": "Environment", "Value": "shared"},
            {"Key": "Purpose", "Value": "network-inspection"},
            {"Key": "ManagedBy", "Value": "terraform"},
        ],
    },
}

# =============================================================================
# TRANSIT GATEWAY ATTACHMENT FIXTURES
# =============================================================================

TGW_ATTACHMENT_FIXTURES: dict[str, dict[str, Any]] = {
    # Production VPC Attachment
    "tgw-attach-0prodvpc12345": {
        "TransitGatewayAttachmentId": "tgw-attach-0prodvpc12345",
        "TransitGatewayId": "tgw-0prod12345678901",
        "TransitGatewayOwnerId": "123456789012",
        "ResourceOwnerId": "123456789012",
        "ResourceType": "vpc",
        "ResourceId": "vpc-0prod1234567890ab",
        "State": "available",
        "Association": {
            "TransitGatewayRouteTableId": "tgw-rtb-0prodspoke1234",
            "State": "associated",
        },
        "CreationTime": "2024-01-16T09:00:00+00:00",
        "Tags": [
            {"Key": "Name", "Value": "production-vpc-attachment"},
            {"Key": "Environment", "Value": "production"},
        ],
    },
    # Staging VPC Attachment (to Production TGW via peering)
    "tgw-attach-0stagvpc12345": {
        "TransitGatewayAttachmentId": "tgw-attach-0stagvpc12345",
        "TransitGatewayId": "tgw-0stag12345678901",
        "TransitGatewayOwnerId": "123456789012",
        "ResourceOwnerId": "123456789012",
        "ResourceType": "vpc",
        "ResourceId": "vpc-0stag1234567890ab",
        "State": "available",
        "Association": {
            "TransitGatewayRouteTableId": "tgw-rtb-0stagdefault123",
            "State": "associated",
        },
        "CreationTime": "2024-02-02T10:00:00+00:00",
        "Tags": [
            {"Key": "Name", "Value": "staging-vpc-attachment"},
            {"Key": "Environment", "Value": "staging"},
        ],
    },
    # Shared Services VPC Attachment
    "tgw-attach-0shared123456": {
        "TransitGatewayAttachmentId": "tgw-attach-0shared123456",
        "TransitGatewayId": "tgw-0prod12345678901",
        "TransitGatewayOwnerId": "123456789012",
        "ResourceOwnerId": "123456789012",
        "ResourceType": "vpc",
        "ResourceId": "vpc-0shared123456789a",
        "State": "available",
        "Association": {
            "TransitGatewayRouteTableId": "tgw-rtb-0prodshared1234",
            "State": "associated",
        },
        "CreationTime": "2024-01-17T11:00:00+00:00",
        "Tags": [
            {"Key": "Name", "Value": "shared-services-attachment"},
            {"Key": "Environment", "Value": "shared"},
        ],
    },
    # VPN Attachment to On-Premises
    "tgw-attach-0vpn0123456789": {
        "TransitGatewayAttachmentId": "tgw-attach-0vpn0123456789",
        "TransitGatewayId": "tgw-0prod12345678901",
        "TransitGatewayOwnerId": "123456789012",
        "ResourceOwnerId": "123456789012",
        "ResourceType": "vpn",
        "ResourceId": "vpn-0prod12345678901",
        "State": "available",
        "Association": {
            "TransitGatewayRouteTableId": "tgw-rtb-0prodvpn12345",
            "State": "associated",
        },
        "CreationTime": "2024-01-18T14:00:00+00:00",
        "Tags": [
            {"Key": "Name", "Value": "onprem-vpn-attachment"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "Destination", "Value": "datacenter-dublin"},
        ],
    },
    # Direct Connect Gateway Attachment
    "tgw-attach-0dxgw123456789": {
        "TransitGatewayAttachmentId": "tgw-attach-0dxgw123456789",
        "TransitGatewayId": "tgw-0prod12345678901",
        "TransitGatewayOwnerId": "123456789012",
        "ResourceOwnerId": "123456789012",
        "ResourceType": "direct-connect-gateway",
        "ResourceId": "dxgw-0prod12345678901",
        "State": "available",
        "Association": {
            "TransitGatewayRouteTableId": "tgw-rtb-0prodvpn12345",
            "State": "associated",
        },
        "CreationTime": "2024-01-19T16:00:00+00:00",
        "Tags": [
            {"Key": "Name", "Value": "dx-gateway-attachment"},
            {"Key": "Environment", "Value": "production"},
        ],
    },
    # Peering Attachment (Production to Staging)
    "tgw-attach-0peer12345678": {
        "TransitGatewayAttachmentId": "tgw-attach-0peer12345678",
        "TransitGatewayId": "tgw-0prod12345678901",
        "TransitGatewayOwnerId": "123456789012",
        "ResourceOwnerId": "123456789012",
        "ResourceType": "peering",
        "ResourceId": "tgw-0stag12345678901",
        "State": "available",
        "Association": {
            "TransitGatewayRouteTableId": "tgw-rtb-0prodpeering12",
            "State": "associated",
        },
        "CreationTime": "2024-02-05T12:00:00+00:00",
        "Tags": [
            {"Key": "Name", "Value": "prod-to-staging-peering"},
            {"Key": "Environment", "Value": "cross-region"},
        ],
    },
    # Inspection VPC Attachment (for Network Firewall)
    "tgw-attach-0insp12345678": {
        "TransitGatewayAttachmentId": "tgw-attach-0insp12345678",
        "TransitGatewayId": "tgw-0insp12345678901",
        "TransitGatewayOwnerId": "123456789012",
        "ResourceOwnerId": "123456789012",
        "ResourceType": "vpc",
        "ResourceId": "vpc-0firewall1234567",
        "State": "available",
        "Association": {
            "TransitGatewayRouteTableId": "tgw-rtb-0inspfw12345",
            "State": "associated",
        },
        "CreationTime": "2024-01-21T10:00:00+00:00",
        "Tags": [
            {"Key": "Name", "Value": "firewall-vpc-attachment"},
            {"Key": "Purpose", "Value": "inspection"},
        ],
    },
}

# =============================================================================
# TRANSIT GATEWAY ROUTE TABLE FIXTURES
# =============================================================================

TGW_ROUTE_TABLE_FIXTURES: dict[str, dict[str, Any]] = {
    # Production Default Route Table
    "tgw-rtb-0proddefault123": {
        "TransitGatewayRouteTableId": "tgw-rtb-0proddefault123",
        "TransitGatewayId": "tgw-0prod12345678901",
        "State": "available",
        "DefaultAssociationRouteTable": True,
        "DefaultPropagationRouteTable": True,
        "CreationTime": "2024-01-15T10:30:00+00:00",
        "Tags": [
            {"Key": "Name", "Value": "production-default-rt"},
            {"Key": "Type", "Value": "default"},
        ],
        "Routes": [
            {
                "DestinationCidrBlock": "10.0.0.0/16",
                "TransitGatewayAttachments": [
                    {
                        "ResourceId": "vpc-0prod1234567890ab",
                        "TransitGatewayAttachmentId": "tgw-attach-0prodvpc12345",
                        "ResourceType": "vpc",
                    }
                ],
                "Type": "propagated",
                "State": "active",
            },
            {
                "DestinationCidrBlock": "10.100.0.0/16",
                "TransitGatewayAttachments": [
                    {
                        "ResourceId": "vpc-0shared123456789a",
                        "TransitGatewayAttachmentId": "tgw-attach-0shared123456",
                        "ResourceType": "vpc",
                    }
                ],
                "Type": "propagated",
                "State": "active",
            },
            {
                "DestinationCidrBlock": "192.168.0.0/16",
                "TransitGatewayAttachments": [
                    {
                        "ResourceId": "vpn-0prod12345678901",
                        "TransitGatewayAttachmentId": "tgw-attach-0vpn0123456789",
                        "ResourceType": "vpn",
                    }
                ],
                "Type": "propagated",
                "State": "active",
            },
            {
                "DestinationCidrBlock": "10.1.0.0/16",
                "TransitGatewayAttachments": [
                    {
                        "ResourceId": "tgw-0stag12345678901",
                        "TransitGatewayAttachmentId": "tgw-attach-0peer12345678",
                        "ResourceType": "peering",
                    }
                ],
                "Type": "static",
                "State": "active",
            },
        ],
        "Associations": [
            {
                "TransitGatewayAttachmentId": "tgw-attach-0prodvpc12345",
                "ResourceId": "vpc-0prod1234567890ab",
                "ResourceType": "vpc",
                "State": "associated",
            },
        ],
        "Propagations": [
            {
                "TransitGatewayAttachmentId": "tgw-attach-0prodvpc12345",
                "ResourceId": "vpc-0prod1234567890ab",
                "ResourceType": "vpc",
                "State": "enabled",
            },
            {
                "TransitGatewayAttachmentId": "tgw-attach-0shared123456",
                "ResourceId": "vpc-0shared123456789a",
                "ResourceType": "vpc",
                "State": "enabled",
            },
            {
                "TransitGatewayAttachmentId": "tgw-attach-0vpn0123456789",
                "ResourceId": "vpn-0prod12345678901",
                "ResourceType": "vpn",
                "State": "enabled",
            },
        ],
    },
    # Production Spoke Route Table
    "tgw-rtb-0prodspoke1234": {
        "TransitGatewayRouteTableId": "tgw-rtb-0prodspoke1234",
        "TransitGatewayId": "tgw-0prod12345678901",
        "State": "available",
        "DefaultAssociationRouteTable": False,
        "DefaultPropagationRouteTable": False,
        "CreationTime": "2024-01-16T09:00:00+00:00",
        "Tags": [
            {"Key": "Name", "Value": "production-spoke-rt"},
            {"Key": "Type", "Value": "spoke"},
        ],
        "Routes": [
            {
                "DestinationCidrBlock": "0.0.0.0/0",
                "TransitGatewayAttachments": [
                    {
                        "ResourceId": "vpc-0firewall1234567",
                        "TransitGatewayAttachmentId": "tgw-attach-0insp12345678",
                        "ResourceType": "vpc",
                    }
                ],
                "Type": "static",
                "State": "active",
            },
            {
                "DestinationCidrBlock": "10.100.0.0/16",
                "TransitGatewayAttachments": [
                    {
                        "ResourceId": "vpc-0shared123456789a",
                        "TransitGatewayAttachmentId": "tgw-attach-0shared123456",
                        "ResourceType": "vpc",
                    }
                ],
                "Type": "propagated",
                "State": "active",
            },
        ],
        "Associations": [
            {
                "TransitGatewayAttachmentId": "tgw-attach-0prodvpc12345",
                "ResourceId": "vpc-0prod1234567890ab",
                "ResourceType": "vpc",
                "State": "associated",
            },
        ],
        "Propagations": [
            {
                "TransitGatewayAttachmentId": "tgw-attach-0shared123456",
                "ResourceId": "vpc-0shared123456789a",
                "ResourceType": "vpc",
                "State": "enabled",
            },
        ],
    },
    # Production Shared Services Route Table
    "tgw-rtb-0prodshared1234": {
        "TransitGatewayRouteTableId": "tgw-rtb-0prodshared1234",
        "TransitGatewayId": "tgw-0prod12345678901",
        "State": "available",
        "DefaultAssociationRouteTable": False,
        "DefaultPropagationRouteTable": False,
        "CreationTime": "2024-01-17T11:00:00+00:00",
        "Tags": [
            {"Key": "Name", "Value": "production-shared-rt"},
            {"Key": "Type", "Value": "shared-services"},
        ],
        "Routes": [
            {
                "DestinationCidrBlock": "10.0.0.0/16",
                "TransitGatewayAttachments": [
                    {
                        "ResourceId": "vpc-0prod1234567890ab",
                        "TransitGatewayAttachmentId": "tgw-attach-0prodvpc12345",
                        "ResourceType": "vpc",
                    }
                ],
                "Type": "propagated",
                "State": "active",
            },
            {
                "DestinationCidrBlock": "192.168.0.0/16",
                "TransitGatewayAttachments": [
                    {
                        "ResourceId": "vpn-0prod12345678901",
                        "TransitGatewayAttachmentId": "tgw-attach-0vpn0123456789",
                        "ResourceType": "vpn",
                    }
                ],
                "Type": "propagated",
                "State": "active",
            },
        ],
        "Associations": [
            {
                "TransitGatewayAttachmentId": "tgw-attach-0shared123456",
                "ResourceId": "vpc-0shared123456789a",
                "ResourceType": "vpc",
                "State": "associated",
            },
        ],
        "Propagations": [
            {
                "TransitGatewayAttachmentId": "tgw-attach-0prodvpc12345",
                "ResourceId": "vpc-0prod1234567890ab",
                "ResourceType": "vpc",
                "State": "enabled",
            },
            {
                "TransitGatewayAttachmentId": "tgw-attach-0vpn0123456789",
                "ResourceId": "vpn-0prod12345678901",
                "ResourceType": "vpn",
                "State": "enabled",
            },
        ],
    },
    # Production VPN Route Table
    "tgw-rtb-0prodvpn12345": {
        "TransitGatewayRouteTableId": "tgw-rtb-0prodvpn12345",
        "TransitGatewayId": "tgw-0prod12345678901",
        "State": "available",
        "DefaultAssociationRouteTable": False,
        "DefaultPropagationRouteTable": False,
        "CreationTime": "2024-01-18T14:00:00+00:00",
        "Tags": [
            {"Key": "Name", "Value": "production-vpn-rt"},
            {"Key": "Type", "Value": "vpn"},
        ],
        "Routes": [
            {
                "DestinationCidrBlock": "10.0.0.0/16",
                "TransitGatewayAttachments": [
                    {
                        "ResourceId": "vpc-0prod1234567890ab",
                        "TransitGatewayAttachmentId": "tgw-attach-0prodvpc12345",
                        "ResourceType": "vpc",
                    }
                ],
                "Type": "propagated",
                "State": "active",
            },
            {
                "DestinationCidrBlock": "10.100.0.0/16",
                "TransitGatewayAttachments": [
                    {
                        "ResourceId": "vpc-0shared123456789a",
                        "TransitGatewayAttachmentId": "tgw-attach-0shared123456",
                        "ResourceType": "vpc",
                    }
                ],
                "Type": "propagated",
                "State": "active",
            },
        ],
        "Associations": [
            {
                "TransitGatewayAttachmentId": "tgw-attach-0vpn0123456789",
                "ResourceId": "vpn-0prod12345678901",
                "ResourceType": "vpn",
                "State": "associated",
            },
            {
                "TransitGatewayAttachmentId": "tgw-attach-0dxgw123456789",
                "ResourceId": "dxgw-0prod12345678901",
                "ResourceType": "direct-connect-gateway",
                "State": "associated",
            },
        ],
        "Propagations": [
            {
                "TransitGatewayAttachmentId": "tgw-attach-0prodvpc12345",
                "ResourceId": "vpc-0prod1234567890ab",
                "ResourceType": "vpc",
                "State": "enabled",
            },
            {
                "TransitGatewayAttachmentId": "tgw-attach-0shared123456",
                "ResourceId": "vpc-0shared123456789a",
                "ResourceType": "vpc",
                "State": "enabled",
            },
        ],
    },
    # Production Peering Route Table
    "tgw-rtb-0prodpeering12": {
        "TransitGatewayRouteTableId": "tgw-rtb-0prodpeering12",
        "TransitGatewayId": "tgw-0prod12345678901",
        "State": "available",
        "DefaultAssociationRouteTable": False,
        "DefaultPropagationRouteTable": False,
        "CreationTime": "2024-02-05T12:00:00+00:00",
        "Tags": [
            {"Key": "Name", "Value": "production-peering-rt"},
            {"Key": "Type", "Value": "peering"},
        ],
        "Routes": [
            {
                "DestinationCidrBlock": "10.0.0.0/16",
                "TransitGatewayAttachments": [
                    {
                        "ResourceId": "vpc-0prod1234567890ab",
                        "TransitGatewayAttachmentId": "tgw-attach-0prodvpc12345",
                        "ResourceType": "vpc",
                    }
                ],
                "Type": "propagated",
                "State": "active",
            },
            {
                "DestinationCidrBlock": "10.100.0.0/16",
                "TransitGatewayAttachments": [
                    {
                        "ResourceId": "vpc-0shared123456789a",
                        "TransitGatewayAttachmentId": "tgw-attach-0shared123456",
                        "ResourceType": "vpc",
                    }
                ],
                "Type": "propagated",
                "State": "active",
            },
        ],
        "Associations": [
            {
                "TransitGatewayAttachmentId": "tgw-attach-0peer12345678",
                "ResourceId": "tgw-0stag12345678901",
                "ResourceType": "peering",
                "State": "associated",
            },
        ],
        "Propagations": [
            {
                "TransitGatewayAttachmentId": "tgw-attach-0prodvpc12345",
                "ResourceId": "vpc-0prod1234567890ab",
                "ResourceType": "vpc",
                "State": "enabled",
            },
            {
                "TransitGatewayAttachmentId": "tgw-attach-0shared123456",
                "ResourceId": "vpc-0shared123456789a",
                "ResourceType": "vpc",
                "State": "enabled",
            },
        ],
    },
    # Staging Default Route Table
    "tgw-rtb-0stagdefault123": {
        "TransitGatewayRouteTableId": "tgw-rtb-0stagdefault123",
        "TransitGatewayId": "tgw-0stag12345678901",
        "State": "available",
        "DefaultAssociationRouteTable": True,
        "DefaultPropagationRouteTable": True,
        "CreationTime": "2024-02-01T14:00:00+00:00",
        "Tags": [
            {"Key": "Name", "Value": "staging-default-rt"},
            {"Key": "Type", "Value": "default"},
        ],
        "Routes": [
            {
                "DestinationCidrBlock": "10.1.0.0/16",
                "TransitGatewayAttachments": [
                    {
                        "ResourceId": "vpc-0stag1234567890ab",
                        "TransitGatewayAttachmentId": "tgw-attach-0stagvpc12345",
                        "ResourceType": "vpc",
                    }
                ],
                "Type": "propagated",
                "State": "active",
            },
            {
                "DestinationCidrBlock": "10.0.0.0/16",
                "TransitGatewayAttachments": [
                    {
                        "ResourceId": "tgw-0prod12345678901",
                        "TransitGatewayAttachmentId": "tgw-attach-0stagpeer1234",
                        "ResourceType": "peering",
                    }
                ],
                "Type": "static",
                "State": "active",
            },
        ],
        "Associations": [
            {
                "TransitGatewayAttachmentId": "tgw-attach-0stagvpc12345",
                "ResourceId": "vpc-0stag1234567890ab",
                "ResourceType": "vpc",
                "State": "associated",
            },
        ],
        "Propagations": [
            {
                "TransitGatewayAttachmentId": "tgw-attach-0stagvpc12345",
                "ResourceId": "vpc-0stag1234567890ab",
                "ResourceType": "vpc",
                "State": "enabled",
            },
        ],
    },
    # Inspection Firewall Route Table
    "tgw-rtb-0inspfw12345": {
        "TransitGatewayRouteTableId": "tgw-rtb-0inspfw12345",
        "TransitGatewayId": "tgw-0insp12345678901",
        "State": "available",
        "DefaultAssociationRouteTable": False,
        "DefaultPropagationRouteTable": False,
        "CreationTime": "2024-01-21T10:00:00+00:00",
        "Tags": [
            {"Key": "Name", "Value": "inspection-firewall-rt"},
            {"Key": "Type", "Value": "firewall"},
        ],
        "Routes": [
            {
                "DestinationCidrBlock": "10.0.0.0/8",
                "TransitGatewayAttachments": [
                    {
                        "ResourceId": "vpc-0prod1234567890ab",
                        "TransitGatewayAttachmentId": "tgw-attach-0prodvpc12345",
                        "ResourceType": "vpc",
                    }
                ],
                "Type": "static",
                "State": "active",
            },
        ],
        "Associations": [
            {
                "TransitGatewayAttachmentId": "tgw-attach-0insp12345678",
                "ResourceId": "vpc-0firewall1234567",
                "ResourceType": "vpc",
                "State": "associated",
            },
        ],
        "Propagations": [],
    },
}

# =============================================================================
# TRANSIT GATEWAY PEERING FIXTURES
# =============================================================================

TGW_PEERING_FIXTURES: dict[str, dict[str, Any]] = {
    # Production to Staging Peering (Requester side)
    "tgw-attach-0peer12345678": {
        "TransitGatewayAttachmentId": "tgw-attach-0peer12345678",
        "RequesterTgwInfo": {
            "TransitGatewayId": "tgw-0prod12345678901",
            "OwnerId": "123456789012",
            "Region": "eu-west-1",
        },
        "AccepterTgwInfo": {
            "TransitGatewayId": "tgw-0stag12345678901",
            "OwnerId": "123456789012",
            "Region": "us-east-1",
        },
        "Status": {
            "Code": "available",
            "Message": "Peering attachment is available",
        },
        "State": "available",
        "CreationTime": "2024-02-05T12:00:00+00:00",
        "Tags": [
            {"Key": "Name", "Value": "prod-to-staging-peering"},
            {"Key": "Side", "Value": "requester"},
        ],
    },
    # Staging to Production Peering (Accepter side)
    "tgw-attach-0stagpeer1234": {
        "TransitGatewayAttachmentId": "tgw-attach-0stagpeer1234",
        "RequesterTgwInfo": {
            "TransitGatewayId": "tgw-0prod12345678901",
            "OwnerId": "123456789012",
            "Region": "eu-west-1",
        },
        "AccepterTgwInfo": {
            "TransitGatewayId": "tgw-0stag12345678901",
            "OwnerId": "123456789012",
            "Region": "us-east-1",
        },
        "Status": {
            "Code": "available",
            "Message": "Peering attachment is available",
        },
        "State": "available",
        "CreationTime": "2024-02-05T12:05:00+00:00",
        "Tags": [
            {"Key": "Name", "Value": "staging-to-prod-peering"},
            {"Key": "Side", "Value": "accepter"},
        ],
    },
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_tgw_by_id(tgw_id: str) -> dict[str, Any] | None:
    """Get Transit Gateway fixture by ID."""
    return TGW_FIXTURES.get(tgw_id)


def get_tgw_detail(tgw_id: str) -> dict[str, Any] | None:
    """Get comprehensive TGW detail with all associated resources."""
    tgw = TGW_FIXTURES.get(tgw_id)
    if not tgw:
        return None

    # Gather associated attachments
    attachments = [
        a for a in TGW_ATTACHMENT_FIXTURES.values() if a["TransitGatewayId"] == tgw_id
    ]

    # Gather associated route tables
    route_tables = [
        rt
        for rt in TGW_ROUTE_TABLE_FIXTURES.values()
        if rt["TransitGatewayId"] == tgw_id
    ]

    # Gather associated peerings
    peerings = [
        p
        for p in TGW_PEERING_FIXTURES.values()
        if p.get("RequesterTgwInfo", {}).get("TransitGatewayId") == tgw_id
        or p.get("AccepterTgwInfo", {}).get("TransitGatewayId") == tgw_id
    ]

    return {
        "transit_gateway": tgw,
        "attachments": attachments,
        "route_tables": route_tables,
        "peerings": peerings,
    }


def get_attachments_by_tgw(tgw_id: str) -> list[dict[str, Any]]:
    """Get all attachments for a Transit Gateway."""
    return [
        a for a in TGW_ATTACHMENT_FIXTURES.values() if a["TransitGatewayId"] == tgw_id
    ]


def get_route_tables_by_tgw(tgw_id: str) -> list[dict[str, Any]]:
    """Get all route tables for a Transit Gateway."""
    return [
        rt
        for rt in TGW_ROUTE_TABLE_FIXTURES.values()
        if rt["TransitGatewayId"] == tgw_id
    ]


def get_attachment_by_id(attachment_id: str) -> dict[str, Any] | None:
    """Get TGW attachment by ID."""
    return TGW_ATTACHMENT_FIXTURES.get(attachment_id)


def get_route_table_by_id(route_table_id: str) -> dict[str, Any] | None:
    """Get TGW route table by ID."""
    return TGW_ROUTE_TABLE_FIXTURES.get(route_table_id)
