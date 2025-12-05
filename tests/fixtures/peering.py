"""Realistic VPC Peering Connection mock data fixtures.

VPC Peering Architecture:
- Intra-region peering: Production to Shared Services (eu-west-1)
- Cross-region peering: Production (eu-west-1) to Staging (us-east-1)
- Cross-account peering: Production to Partner account
- Various states: active, pending-acceptance, provisioning, failed

Each peering connection includes:
- VPC Peering Connection ID
- Status (Code and Message)
- Requester VPC information (VPC ID, CIDR, Owner, Region)
- Accepter VPC information (VPC ID, CIDR, Owner, Region)
- DNS resolution options
- Peering options
- Tags with naming and metadata
"""

from typing import Any

# =============================================================================
# VPC PEERING CONNECTION FIXTURES
# =============================================================================

VPC_PEERING_FIXTURES: dict[str, dict[str, Any]] = {
    # Intra-region Peering - Production to Shared Services (eu-west-1)
    "pcx-0prod2shared12345": {
        "VpcPeeringConnectionId": "pcx-0prod2shared12345",
        "Status": {
            "Code": "active",
            "Message": "Active",
        },
        "RequesterVpcInfo": {
            "VpcId": "vpc-0prod1234567890ab",
            "CidrBlock": "10.0.0.0/16",
            "CidrBlockSet": [
                {"CidrBlock": "10.0.0.0/16"},
                {"CidrBlock": "100.64.0.0/16"},
            ],
            "OwnerId": "123456789012",
            "Region": "eu-west-1",
            "PeeringOptions": {
                "AllowDnsResolutionFromRemoteVpc": True,
                "AllowEgressFromLocalClassicLinkToRemoteVpc": False,
                "AllowEgressFromLocalVpcToRemoteClassicLink": False,
            },
        },
        "AccepterVpcInfo": {
            "VpcId": "vpc-0shared123456789a",
            "CidrBlock": "10.100.0.0/16",
            "CidrBlockSet": [
                {"CidrBlock": "10.100.0.0/16"},
            ],
            "OwnerId": "123456789012",
            "Region": "eu-west-1",
            "PeeringOptions": {
                "AllowDnsResolutionFromRemoteVpc": True,
                "AllowEgressFromLocalClassicLinkToRemoteVpc": False,
                "AllowEgressFromLocalVpcToRemoteClassicLink": False,
            },
        },
        "Tags": [
            {"Key": "Name", "Value": "production-to-shared-services"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "Type", "Value": "intra-region"},
            {"Key": "ManagedBy", "Value": "terraform"},
        ],
    },
    # Cross-region Peering - Production (eu-west-1) to Staging (us-east-1)
    "pcx-0prod2staging1234": {
        "VpcPeeringConnectionId": "pcx-0prod2staging1234",
        "Status": {
            "Code": "active",
            "Message": "Active",
        },
        "RequesterVpcInfo": {
            "VpcId": "vpc-0prod1234567890ab",
            "CidrBlock": "10.0.0.0/16",
            "CidrBlockSet": [
                {"CidrBlock": "10.0.0.0/16"},
                {"CidrBlock": "100.64.0.0/16"},
            ],
            "OwnerId": "123456789012",
            "Region": "eu-west-1",
            "PeeringOptions": {
                "AllowDnsResolutionFromRemoteVpc": True,
                "AllowEgressFromLocalClassicLinkToRemoteVpc": False,
                "AllowEgressFromLocalVpcToRemoteClassicLink": False,
            },
        },
        "AccepterVpcInfo": {
            "VpcId": "vpc-0stag1234567890ab",
            "CidrBlock": "10.1.0.0/16",
            "CidrBlockSet": [
                {"CidrBlock": "10.1.0.0/16"},
            ],
            "OwnerId": "123456789012",
            "Region": "us-east-1",
            "PeeringOptions": {
                "AllowDnsResolutionFromRemoteVpc": True,
                "AllowEgressFromLocalClassicLinkToRemoteVpc": False,
                "AllowEgressFromLocalVpcToRemoteClassicLink": False,
            },
        },
        "Tags": [
            {"Key": "Name", "Value": "production-to-staging"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "Type", "Value": "cross-region"},
            {"Key": "ManagedBy", "Value": "terraform"},
        ],
    },
    # Cross-account Peering - Production to Partner Account (pending-acceptance)
    "pcx-0prod2partner1234": {
        "VpcPeeringConnectionId": "pcx-0prod2partner1234",
        "Status": {
            "Code": "pending-acceptance",
            "Message": "Pending Acceptance by 210987654321",
        },
        "RequesterVpcInfo": {
            "VpcId": "vpc-0prod1234567890ab",
            "CidrBlock": "10.0.0.0/16",
            "CidrBlockSet": [
                {"CidrBlock": "10.0.0.0/16"},
            ],
            "OwnerId": "123456789012",
            "Region": "eu-west-1",
            "PeeringOptions": {
                "AllowDnsResolutionFromRemoteVpc": False,
                "AllowEgressFromLocalClassicLinkToRemoteVpc": False,
                "AllowEgressFromLocalVpcToRemoteClassicLink": False,
            },
        },
        "AccepterVpcInfo": {
            "VpcId": "vpc-0partner12345678",
            "CidrBlock": "10.50.0.0/16",
            "CidrBlockSet": [
                {"CidrBlock": "10.50.0.0/16"},
            ],
            "OwnerId": "210987654321",
            "Region": "eu-west-1",
            "PeeringOptions": {
                "AllowDnsResolutionFromRemoteVpc": False,
                "AllowEgressFromLocalClassicLinkToRemoteVpc": False,
                "AllowEgressFromLocalVpcToRemoteClassicLink": False,
            },
        },
        "Tags": [
            {"Key": "Name", "Value": "production-to-partner"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "Type", "Value": "cross-account"},
            {"Key": "ManagedBy", "Value": "terraform"},
        ],
    },
    # Shared Services to Development (provisioning)
    "pcx-0shared2dev123456": {
        "VpcPeeringConnectionId": "pcx-0shared2dev123456",
        "Status": {
            "Code": "provisioning",
            "Message": "Provisioning",
        },
        "RequesterVpcInfo": {
            "VpcId": "vpc-0shared123456789a",
            "CidrBlock": "10.100.0.0/16",
            "CidrBlockSet": [
                {"CidrBlock": "10.100.0.0/16"},
            ],
            "OwnerId": "123456789012",
            "Region": "eu-west-1",
            "PeeringOptions": {
                "AllowDnsResolutionFromRemoteVpc": True,
                "AllowEgressFromLocalClassicLinkToRemoteVpc": False,
                "AllowEgressFromLocalVpcToRemoteClassicLink": False,
            },
        },
        "AccepterVpcInfo": {
            "VpcId": "vpc-0dev01234567890ab",
            "CidrBlock": "10.2.0.0/16",
            "CidrBlockSet": [
                {"CidrBlock": "10.2.0.0/16"},
            ],
            "OwnerId": "123456789012",
            "Region": "ap-southeast-2",
            "PeeringOptions": {
                "AllowDnsResolutionFromRemoteVpc": True,
                "AllowEgressFromLocalClassicLinkToRemoteVpc": False,
                "AllowEgressFromLocalVpcToRemoteClassicLink": False,
            },
        },
        "Tags": [
            {"Key": "Name", "Value": "shared-services-to-development"},
            {"Key": "Environment", "Value": "shared"},
            {"Key": "Type", "Value": "cross-region"},
            {"Key": "ManagedBy", "Value": "terraform"},
        ],
    },
    # Failed Peering - Staging to Development (CIDR overlap)
    "pcx-0stag2dev12345678": {
        "VpcPeeringConnectionId": "pcx-0stag2dev12345678",
        "Status": {
            "Code": "failed",
            "Message": "VPC CIDR blocks overlap",
        },
        "RequesterVpcInfo": {
            "VpcId": "vpc-0stag1234567890ab",
            "CidrBlock": "10.1.0.0/16",
            "CidrBlockSet": [
                {"CidrBlock": "10.1.0.0/16"},
            ],
            "OwnerId": "123456789012",
            "Region": "us-east-1",
            "PeeringOptions": {
                "AllowDnsResolutionFromRemoteVpc": False,
                "AllowEgressFromLocalClassicLinkToRemoteVpc": False,
                "AllowEgressFromLocalVpcToRemoteClassicLink": False,
            },
        },
        "AccepterVpcInfo": {
            "VpcId": "vpc-0dev01234567890ab",
            "CidrBlock": "10.2.0.0/16",
            "CidrBlockSet": [
                {"CidrBlock": "10.2.0.0/16"},
            ],
            "OwnerId": "123456789012",
            "Region": "ap-southeast-2",
            "PeeringOptions": {
                "AllowDnsResolutionFromRemoteVpc": False,
                "AllowEgressFromLocalClassicLinkToRemoteVpc": False,
                "AllowEgressFromLocalVpcToRemoteClassicLink": False,
            },
        },
        "Tags": [
            {"Key": "Name", "Value": "staging-to-development-failed"},
            {"Key": "Environment", "Value": "staging"},
            {"Key": "Type", "Value": "cross-region"},
            {"Key": "Status", "Value": "failed"},
        ],
    },
    # Cross-account Peering - Production to Vendor (active, no DNS resolution)
    "pcx-0prod2vendor12345": {
        "VpcPeeringConnectionId": "pcx-0prod2vendor12345",
        "Status": {
            "Code": "active",
            "Message": "Active",
        },
        "RequesterVpcInfo": {
            "VpcId": "vpc-0prod1234567890ab",
            "CidrBlock": "10.0.0.0/16",
            "CidrBlockSet": [
                {"CidrBlock": "10.0.0.0/16"},
            ],
            "OwnerId": "123456789012",
            "Region": "eu-west-1",
            "PeeringOptions": {
                "AllowDnsResolutionFromRemoteVpc": False,
                "AllowEgressFromLocalClassicLinkToRemoteVpc": False,
                "AllowEgressFromLocalVpcToRemoteClassicLink": False,
            },
        },
        "AccepterVpcInfo": {
            "VpcId": "vpc-0vendor123456789",
            "CidrBlock": "172.16.0.0/16",
            "CidrBlockSet": [
                {"CidrBlock": "172.16.0.0/16"},
            ],
            "OwnerId": "345678901234",
            "Region": "eu-west-1",
            "PeeringOptions": {
                "AllowDnsResolutionFromRemoteVpc": False,
                "AllowEgressFromLocalClassicLinkToRemoteVpc": False,
                "AllowEgressFromLocalVpcToRemoteClassicLink": False,
            },
        },
        "Tags": [
            {"Key": "Name", "Value": "production-to-vendor"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "Type", "Value": "cross-account"},
            {"Key": "VendorName", "Value": "DataProvider Inc"},
            {"Key": "ManagedBy", "Value": "terraform"},
        ],
    },
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_peering_by_id(pcx_id: str) -> dict[str, Any] | None:
    """Get VPC peering connection fixture by ID."""
    return VPC_PEERING_FIXTURES.get(pcx_id)


def get_active_peerings() -> list[dict[str, Any]]:
    """Get all active VPC peering connections."""
    return [
        pcx for pcx in VPC_PEERING_FIXTURES.values()
        if pcx["Status"]["Code"] == "active"
    ]


def get_peerings_by_status(status: str) -> list[dict[str, Any]]:
    """Get VPC peering connections by status code.

    Valid statuses: active, pending-acceptance, provisioning, failed, deleting, deleted
    """
    return [
        pcx for pcx in VPC_PEERING_FIXTURES.values()
        if pcx["Status"]["Code"] == status
    ]


def get_peerings_by_vpc(vpc_id: str) -> list[dict[str, Any]]:
    """Get all VPC peering connections for a specific VPC (requester or accepter)."""
    return [
        pcx for pcx in VPC_PEERING_FIXTURES.values()
        if pcx["RequesterVpcInfo"]["VpcId"] == vpc_id
        or pcx["AccepterVpcInfo"]["VpcId"] == vpc_id
    ]


def get_intra_region_peerings(region: str) -> list[dict[str, Any]]:
    """Get intra-region VPC peering connections."""
    return [
        pcx for pcx in VPC_PEERING_FIXTURES.values()
        if pcx["RequesterVpcInfo"]["Region"] == region
        and pcx["AccepterVpcInfo"]["Region"] == region
    ]


def get_cross_region_peerings() -> list[dict[str, Any]]:
    """Get cross-region VPC peering connections."""
    return [
        pcx for pcx in VPC_PEERING_FIXTURES.values()
        if pcx["RequesterVpcInfo"]["Region"] != pcx["AccepterVpcInfo"]["Region"]
    ]


def get_cross_account_peerings() -> list[dict[str, Any]]:
    """Get cross-account VPC peering connections."""
    return [
        pcx for pcx in VPC_PEERING_FIXTURES.values()
        if pcx["RequesterVpcInfo"]["OwnerId"] != pcx["AccepterVpcInfo"]["OwnerId"]
    ]


def get_peerings_with_dns_resolution() -> list[dict[str, Any]]:
    """Get VPC peering connections with DNS resolution enabled."""
    return [
        pcx for pcx in VPC_PEERING_FIXTURES.values()
        if (pcx["RequesterVpcInfo"]["PeeringOptions"]["AllowDnsResolutionFromRemoteVpc"]
            or pcx["AccepterVpcInfo"]["PeeringOptions"]["AllowDnsResolutionFromRemoteVpc"])
    ]


def get_peerings_by_owner(owner_id: str) -> list[dict[str, Any]]:
    """Get VPC peering connections where account is requester or accepter."""
    return [
        pcx for pcx in VPC_PEERING_FIXTURES.values()
        if pcx["RequesterVpcInfo"]["OwnerId"] == owner_id
        or pcx["AccepterVpcInfo"]["OwnerId"] == owner_id
    ]


def format_peering_for_display(pcx: dict[str, Any]) -> dict[str, Any]:
    """Format peering connection data for display/testing.

    Returns simplified structure matching module output format.
    """
    requester = pcx["RequesterVpcInfo"]
    accepter = pcx["AccepterVpcInfo"]
    status = pcx["Status"]

    name = None
    for tag in pcx.get("Tags", []):
        if tag["Key"] == "Name":
            name = tag["Value"]
            break

    return {
        "id": pcx["VpcPeeringConnectionId"],
        "name": name,
        "status": status["Code"],
        "status_message": status["Message"],
        "requester_vpc": requester["VpcId"],
        "requester_cidr": requester["CidrBlock"],
        "requester_owner": requester["OwnerId"],
        "requester_region": requester["Region"],
        "accepter_vpc": accepter["VpcId"],
        "accepter_cidr": accepter["CidrBlock"],
        "accepter_owner": accepter["OwnerId"],
        "accepter_region": accepter["Region"],
    }


def get_all_peerings_for_display() -> list[dict[str, Any]]:
    """Get all VPC peering connections formatted for display."""
    return [format_peering_for_display(pcx) for pcx in VPC_PEERING_FIXTURES.values()]
