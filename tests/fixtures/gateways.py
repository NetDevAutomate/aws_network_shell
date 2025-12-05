"""Realistic Gateway mock data fixtures (IGW, NAT, EIP, Egress-only IGW).

Gateway resources across multi-region architecture:
- Internet Gateways (IGW) for public internet access
- NAT Gateways for private subnet outbound connectivity
- Elastic IPs (EIP) for NAT gateways and bastion hosts
- Egress-only Internet Gateways for IPv6-only egress

Each gateway includes:
- VPC attachments
- States and status information
- Associated resources (EIPs, ENIs)
- Realistic resource IDs matching route table references
"""

from typing import Any

# =============================================================================
# INTERNET GATEWAY FIXTURES
# =============================================================================

IGW_FIXTURES: dict[str, dict[str, Any]] = {
    # Production VPC Internet Gateway - eu-west-1
    "igw-0prod12345678901": {
        "InternetGatewayId": "igw-0prod12345678901",
        "Attachments": [
            {
                "State": "available",
                "VpcId": "vpc-0prod1234567890ab",
            }
        ],
        "OwnerId": "123456789012",
        "Tags": [
            {"Key": "Name", "Value": "production-igw"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "ManagedBy", "Value": "terraform"},
        ],
    },
    # Staging VPC Internet Gateway - us-east-1
    "igw-0stag12345678901": {
        "InternetGatewayId": "igw-0stag12345678901",
        "Attachments": [
            {
                "State": "available",
                "VpcId": "vpc-0stag1234567890ab",
            }
        ],
        "OwnerId": "123456789012",
        "Tags": [
            {"Key": "Name", "Value": "staging-igw"},
            {"Key": "Environment", "Value": "staging"},
            {"Key": "ManagedBy", "Value": "terraform"},
        ],
    },
    # Development VPC Internet Gateway - ap-southeast-2
    "igw-0dev012345678901": {
        "InternetGatewayId": "igw-0dev012345678901",
        "Attachments": [
            {
                "State": "available",
                "VpcId": "vpc-0dev01234567890ab",
            }
        ],
        "OwnerId": "123456789012",
        "Tags": [
            {"Key": "Name", "Value": "development-igw"},
            {"Key": "Environment", "Value": "development"},
            {"Key": "ManagedBy", "Value": "terraform"},
        ],
    },
    # Shared Services VPC Internet Gateway - eu-west-1
    "igw-0shared123456789": {
        "InternetGatewayId": "igw-0shared123456789",
        "Attachments": [
            {
                "State": "available",
                "VpcId": "vpc-0shared123456789a",
            }
        ],
        "OwnerId": "123456789012",
        "Tags": [
            {"Key": "Name", "Value": "shared-services-igw"},
            {"Key": "Environment", "Value": "shared"},
            {"Key": "ManagedBy", "Value": "terraform"},
        ],
    },
    # Detached IGW (for testing detached state)
    "igw-0detached1234567": {
        "InternetGatewayId": "igw-0detached1234567",
        "Attachments": [],
        "OwnerId": "123456789012",
        "Tags": [
            {"Key": "Name", "Value": "detached-igw"},
            {"Key": "Status", "Value": "pending-deletion"},
        ],
    },
}

# =============================================================================
# ELASTIC IP FIXTURES
# =============================================================================

EIP_FIXTURES: dict[str, dict[str, Any]] = {
    # NAT Gateway 1a EIP
    "eipalloc-0nat1a12345678": {
        "AllocationId": "eipalloc-0nat1a12345678",
        "Domain": "vpc",
        "PublicIp": "52.31.200.10",
        "PublicIpv4Pool": "amazon",
        "NetworkBorderGroup": "eu-west-1",
        "NetworkInterfaceId": "eni-0nat1a123456789ab",
        "NetworkInterfaceOwnerId": "123456789012",
        "PrivateIpAddress": "10.0.1.5",
        "AssociationId": "eipassoc-0nat1a12345",
        "Tags": [
            {"Key": "Name", "Value": "production-nat-1a-eip"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "AZ", "Value": "eu-west-1a"},
        ],
    },
    # NAT Gateway 1b EIP
    "eipalloc-0nat1b12345678": {
        "AllocationId": "eipalloc-0nat1b12345678",
        "Domain": "vpc",
        "PublicIp": "52.31.200.11",
        "PublicIpv4Pool": "amazon",
        "NetworkBorderGroup": "eu-west-1",
        "NetworkInterfaceId": "eni-0nat1b123456789ab",
        "NetworkInterfaceOwnerId": "123456789012",
        "PrivateIpAddress": "10.0.2.5",
        "AssociationId": "eipassoc-0nat1b12345",
        "Tags": [
            {"Key": "Name", "Value": "production-nat-1b-eip"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "AZ", "Value": "eu-west-1b"},
        ],
    },
    # NAT Gateway 1c EIP
    "eipalloc-0nat1c12345678": {
        "AllocationId": "eipalloc-0nat1c12345678",
        "Domain": "vpc",
        "PublicIp": "52.31.200.12",
        "PublicIpv4Pool": "amazon",
        "NetworkBorderGroup": "eu-west-1",
        "NetworkInterfaceId": "eni-0nat1c123456789ab",
        "NetworkInterfaceOwnerId": "123456789012",
        "PrivateIpAddress": "10.0.3.5",
        "AssociationId": "eipassoc-0nat1c12345",
        "Tags": [
            {"Key": "Name", "Value": "production-nat-1c-eip"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "AZ", "Value": "eu-west-1c"},
        ],
    },
    # Bastion Host EIP (already allocated to bastion in ec2.py)
    "eipalloc-0bastion123456": {
        "AllocationId": "eipalloc-0bastion123456",
        "Domain": "vpc",
        "PublicIp": "203.0.113.50",
        "PublicIpv4Pool": "amazon",
        "NetworkBorderGroup": "eu-west-1",
        "NetworkInterfaceId": "eni-0bastion1a1234567",
        "NetworkInterfaceOwnerId": "123456789012",
        "PrivateIpAddress": "10.100.1.10",
        "AssociationId": "eipassoc-0bastion123",
        "Tags": [
            {"Key": "Name", "Value": "shared-bastion-eip"},
            {"Key": "Environment", "Value": "shared"},
            {"Key": "Purpose", "Value": "bastion"},
        ],
    },
    # Staging NAT Gateway EIP
    "eipalloc-0stagnat123456": {
        "AllocationId": "eipalloc-0stagnat123456",
        "Domain": "vpc",
        "PublicIp": "54.205.100.20",
        "PublicIpv4Pool": "amazon",
        "NetworkBorderGroup": "us-east-1",
        "NetworkInterfaceId": "eni-0stagnat1a1234567",
        "NetworkInterfaceOwnerId": "123456789012",
        "PrivateIpAddress": "10.1.1.5",
        "AssociationId": "eipassoc-0stagnat123",
        "Tags": [
            {"Key": "Name", "Value": "staging-nat-eip"},
            {"Key": "Environment", "Value": "staging"},
        ],
    },
    # Development NAT Gateway EIP
    "eipalloc-0devnat1234567": {
        "AllocationId": "eipalloc-0devnat1234567",
        "Domain": "vpc",
        "PublicIp": "3.25.50.30",
        "PublicIpv4Pool": "amazon",
        "NetworkBorderGroup": "ap-southeast-2",
        "NetworkInterfaceId": "eni-0devnat2a123456789",
        "NetworkInterfaceOwnerId": "123456789012",
        "PrivateIpAddress": "10.2.1.5",
        "AssociationId": "eipassoc-0devnat1234",
        "Tags": [
            {"Key": "Name", "Value": "development-nat-eip"},
            {"Key": "Environment", "Value": "development"},
        ],
    },
    # Unallocated/standalone EIP 1
    "eipalloc-0unalloc123456": {
        "AllocationId": "eipalloc-0unalloc123456",
        "Domain": "vpc",
        "PublicIp": "52.31.250.100",
        "PublicIpv4Pool": "amazon",
        "NetworkBorderGroup": "eu-west-1",
        "Tags": [
            {"Key": "Name", "Value": "reserved-eip-1"},
            {"Key": "Status", "Value": "available"},
            {"Key": "Purpose", "Value": "reserved-for-future"},
        ],
    },
    # Unallocated/standalone EIP 2
    "eipalloc-0unalloc234567": {
        "AllocationId": "eipalloc-0unalloc234567",
        "Domain": "vpc",
        "PublicIp": "52.31.250.101",
        "PublicIpv4Pool": "amazon",
        "NetworkBorderGroup": "eu-west-1",
        "Tags": [
            {"Key": "Name", "Value": "reserved-eip-2"},
            {"Key": "Status", "Value": "available"},
        ],
    },
    # ALB EIP (referenced in ELB fixtures)
    "eipalloc-0alb1a12345678": {
        "AllocationId": "eipalloc-0alb1a12345678",
        "Domain": "vpc",
        "PublicIp": "52.31.100.50",
        "PublicIpv4Pool": "amazon",
        "NetworkBorderGroup": "eu-west-1",
        "NetworkInterfaceId": "eni-0alb1a12345678901",
        "NetworkInterfaceOwnerId": "amazon-elb",
        "PrivateIpAddress": "10.0.1.100",
        "AssociationId": "eipassoc-0alb1a12345",
        "Tags": [
            {"Key": "Name", "Value": "production-alb-1a-eip"},
            {"Key": "Environment", "Value": "production"},
        ],
    },
    # ALB EIP 1b
    "eipalloc-0alb1b12345678": {
        "AllocationId": "eipalloc-0alb1b12345678",
        "Domain": "vpc",
        "PublicIp": "52.31.100.51",
        "PublicIpv4Pool": "amazon",
        "NetworkBorderGroup": "eu-west-1",
        "NetworkInterfaceId": "eni-0alb1b12345678901",
        "NetworkInterfaceOwnerId": "amazon-elb",
        "PrivateIpAddress": "10.0.2.100",
        "AssociationId": "eipassoc-0alb1b12345",
        "Tags": [
            {"Key": "Name", "Value": "production-alb-1b-eip"},
            {"Key": "Environment", "Value": "production"},
        ],
    },
}

# =============================================================================
# NAT GATEWAY FIXTURES
# =============================================================================

NAT_GATEWAY_FIXTURES: dict[str, dict[str, Any]] = {
    # Production NAT Gateway - eu-west-1a (referenced in route tables)
    "nat-0prod1a12345678": {
        "NatGatewayId": "nat-0prod1a12345678",
        "State": "available",
        "SubnetId": "subnet-0pub1a1234567890",
        "VpcId": "vpc-0prod1234567890ab",
        "CreateTime": "2024-01-20T08:30:00+00:00",
        "ConnectivityType": "public",
        "NatGatewayAddresses": [
            {
                "AllocationId": "eipalloc-0nat1a12345678",
                "NetworkInterfaceId": "eni-0nat1a123456789ab",
                "PrivateIp": "10.0.1.5",
                "PublicIp": "52.31.200.10",
                "AssociationId": "eipassoc-0nat1a12345",
                "IsPrimary": True,
                "Status": "succeeded",
            }
        ],
        "Tags": [
            {"Key": "Name", "Value": "production-nat-1a"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "AZ", "Value": "eu-west-1a"},
            {"Key": "ManagedBy", "Value": "terraform"},
        ],
    },
    # Production NAT Gateway - eu-west-1b (referenced in route tables)
    "nat-0prod1b12345678": {
        "NatGatewayId": "nat-0prod1b12345678",
        "State": "available",
        "SubnetId": "subnet-0pub1b1234567890",
        "VpcId": "vpc-0prod1234567890ab",
        "CreateTime": "2024-01-20T08:35:00+00:00",
        "ConnectivityType": "public",
        "NatGatewayAddresses": [
            {
                "AllocationId": "eipalloc-0nat1b12345678",
                "NetworkInterfaceId": "eni-0nat1b123456789ab",
                "PrivateIp": "10.0.2.5",
                "PublicIp": "52.31.200.11",
                "AssociationId": "eipassoc-0nat1b12345",
                "IsPrimary": True,
                "Status": "succeeded",
            }
        ],
        "Tags": [
            {"Key": "Name", "Value": "production-nat-1b"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "AZ", "Value": "eu-west-1b"},
            {"Key": "ManagedBy", "Value": "terraform"},
        ],
    },
    # Production NAT Gateway - eu-west-1c
    "nat-0prod1c12345678": {
        "NatGatewayId": "nat-0prod1c12345678",
        "State": "available",
        "SubnetId": "subnet-0pub1c1234567890",
        "VpcId": "vpc-0prod1234567890ab",
        "CreateTime": "2024-01-20T08:40:00+00:00",
        "ConnectivityType": "public",
        "NatGatewayAddresses": [
            {
                "AllocationId": "eipalloc-0nat1c12345678",
                "NetworkInterfaceId": "eni-0nat1c123456789ab",
                "PrivateIp": "10.0.3.5",
                "PublicIp": "52.31.200.12",
                "AssociationId": "eipassoc-0nat1c12345",
                "IsPrimary": True,
                "Status": "succeeded",
            }
        ],
        "Tags": [
            {"Key": "Name", "Value": "production-nat-1c"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "AZ", "Value": "eu-west-1c"},
            {"Key": "ManagedBy", "Value": "terraform"},
        ],
    },
    # Staging NAT Gateway - us-east-1a
    "nat-0stag1a123456789": {
        "NatGatewayId": "nat-0stag1a123456789",
        "State": "available",
        "SubnetId": "subnet-0stgpub1a12345678",
        "VpcId": "vpc-0stag1234567890ab",
        "CreateTime": "2024-02-01T10:00:00+00:00",
        "ConnectivityType": "public",
        "NatGatewayAddresses": [
            {
                "AllocationId": "eipalloc-0stagnat123456",
                "NetworkInterfaceId": "eni-0stagnat1a1234567",
                "PrivateIp": "10.1.1.5",
                "PublicIp": "54.205.100.20",
                "AssociationId": "eipassoc-0stagnat123",
                "IsPrimary": True,
                "Status": "succeeded",
            }
        ],
        "Tags": [
            {"Key": "Name", "Value": "staging-nat-1a"},
            {"Key": "Environment", "Value": "staging"},
            {"Key": "ManagedBy", "Value": "terraform"},
        ],
    },
    # Development NAT Gateway - ap-southeast-2a
    "nat-0dev2a1234567890": {
        "NatGatewayId": "nat-0dev2a1234567890",
        "State": "available",
        "SubnetId": "subnet-0devpub2a12345678",
        "VpcId": "vpc-0dev01234567890ab",
        "CreateTime": "2024-02-10T09:00:00+00:00",
        "ConnectivityType": "public",
        "NatGatewayAddresses": [
            {
                "AllocationId": "eipalloc-0devnat1234567",
                "NetworkInterfaceId": "eni-0devnat2a123456789",
                "PrivateIp": "10.2.1.5",
                "PublicIp": "3.25.50.30",
                "AssociationId": "eipassoc-0devnat1234",
                "IsPrimary": True,
                "Status": "succeeded",
            }
        ],
        "Tags": [
            {"Key": "Name", "Value": "development-nat-2a"},
            {"Key": "Environment", "Value": "development"},
            {"Key": "ManagedBy", "Value": "terraform"},
        ],
    },
    # Private NAT Gateway (no public IP, private connectivity only)
    "nat-0private12345678": {
        "NatGatewayId": "nat-0private12345678",
        "State": "available",
        "SubnetId": "subnet-0priv1a123456789",
        "VpcId": "vpc-0prod1234567890ab",
        "CreateTime": "2024-03-01T10:00:00+00:00",
        "ConnectivityType": "private",
        "NatGatewayAddresses": [
            {
                "NetworkInterfaceId": "eni-0privnat123456789",
                "PrivateIp": "10.0.10.200",
                "IsPrimary": True,
                "Status": "succeeded",
            }
        ],
        "Tags": [
            {"Key": "Name", "Value": "production-private-nat"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "Type", "Value": "private"},
        ],
    },
    # NAT Gateway in pending state
    "nat-0pending12345678": {
        "NatGatewayId": "nat-0pending12345678",
        "State": "pending",
        "SubnetId": "subnet-0pub1a1234567890",
        "VpcId": "vpc-0prod1234567890ab",
        "CreateTime": "2024-12-04T12:00:00+00:00",
        "ConnectivityType": "public",
        "NatGatewayAddresses": [
            {
                "AllocationId": "eipalloc-0pending123456",
                "IsPrimary": True,
                "Status": "associating",
            }
        ],
        "Tags": [
            {"Key": "Name", "Value": "production-nat-pending"},
            {"Key": "Status", "Value": "provisioning"},
        ],
    },
    # NAT Gateway being deleted
    "nat-0deleting12345678": {
        "NatGatewayId": "nat-0deleting12345678",
        "State": "deleting",
        "SubnetId": "subnet-0pub1b1234567890",
        "VpcId": "vpc-0prod1234567890ab",
        "CreateTime": "2024-01-10T08:00:00+00:00",
        "DeleteTime": "2024-12-04T12:30:00+00:00",
        "ConnectivityType": "public",
        "NatGatewayAddresses": [
            {
                "AllocationId": "eipalloc-0deleting123456",
                "NetworkInterfaceId": "eni-0deleting123456789",
                "PrivateIp": "10.0.2.50",
                "PublicIp": "52.31.200.99",
                "IsPrimary": True,
                "Status": "disassociating",
            }
        ],
        "Tags": [
            {"Key": "Name", "Value": "old-nat-gateway"},
            {"Key": "Status", "Value": "decommissioning"},
        ],
    },
    # Failed NAT Gateway
    "nat-0failed123456789": {
        "NatGatewayId": "nat-0failed123456789",
        "State": "failed",
        "SubnetId": "subnet-0pub1c1234567890",
        "VpcId": "vpc-0prod1234567890ab",
        "CreateTime": "2024-11-15T10:00:00+00:00",
        "FailureCode": "InsufficientFreeAddressesInSubnet",
        "FailureMessage": "Network vpc-0prod1234567890ab has insufficient free addresses in subnet subnet-0pub1c1234567890 to create this NAT gateway",
        "ConnectivityType": "public",
        "NatGatewayAddresses": [],
        "Tags": [
            {"Key": "Name", "Value": "failed-nat-gateway"},
            {"Key": "Status", "Value": "failed"},
        ],
    },
}

# =============================================================================
# EGRESS-ONLY INTERNET GATEWAY FIXTURES (IPv6)
# =============================================================================

EGRESS_ONLY_IGW_FIXTURES: dict[str, dict[str, Any]] = {
    # Production VPC Egress-only IGW - eu-west-1
    "eigw-0prod12345678901": {
        "EgressOnlyInternetGatewayId": "eigw-0prod12345678901",
        "Attachments": [
            {
                "State": "attached",
                "VpcId": "vpc-0prod1234567890ab",
            }
        ],
        "Tags": [
            {"Key": "Name", "Value": "production-eigw"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "Protocol", "Value": "ipv6"},
        ],
    },
    # Staging VPC Egress-only IGW - us-east-1
    "eigw-0stag12345678901": {
        "EgressOnlyInternetGatewayId": "eigw-0stag12345678901",
        "Attachments": [
            {
                "State": "attached",
                "VpcId": "vpc-0stag1234567890ab",
            }
        ],
        "Tags": [
            {"Key": "Name", "Value": "staging-eigw"},
            {"Key": "Environment", "Value": "staging"},
            {"Key": "Protocol", "Value": "ipv6"},
        ],
    },
    # Development VPC Egress-only IGW - ap-southeast-2
    "eigw-0dev012345678901": {
        "EgressOnlyInternetGatewayId": "eigw-0dev012345678901",
        "Attachments": [
            {
                "State": "attached",
                "VpcId": "vpc-0dev01234567890ab",
            }
        ],
        "Tags": [
            {"Key": "Name", "Value": "development-eigw"},
            {"Key": "Environment", "Value": "development"},
            {"Key": "Protocol", "Value": "ipv6"},
        ],
    },
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_igw_by_id(igw_id: str) -> dict[str, Any] | None:
    """Get Internet Gateway fixture by ID."""
    return IGW_FIXTURES.get(igw_id)


def get_igw_by_vpc(vpc_id: str) -> dict[str, Any] | None:
    """Get Internet Gateway attached to a VPC."""
    for igw in IGW_FIXTURES.values():
        if igw.get("Attachments"):
            for attachment in igw["Attachments"]:
                if attachment.get("VpcId") == vpc_id:
                    return igw
    return None


def get_nat_by_id(nat_id: str) -> dict[str, Any] | None:
    """Get NAT Gateway fixture by ID."""
    return NAT_GATEWAY_FIXTURES.get(nat_id)


def get_nat_by_vpc(vpc_id: str) -> list[dict[str, Any]]:
    """Get all NAT Gateways in a VPC."""
    return [nat for nat in NAT_GATEWAY_FIXTURES.values() if nat.get("VpcId") == vpc_id]


def get_nat_by_subnet(subnet_id: str) -> list[dict[str, Any]]:
    """Get all NAT Gateways in a subnet."""
    return [
        nat for nat in NAT_GATEWAY_FIXTURES.values() if nat.get("SubnetId") == subnet_id
    ]


def get_nat_by_state(state: str) -> list[dict[str, Any]]:
    """Get NAT Gateways by state (available, pending, deleting, deleted, failed)."""
    return [nat for nat in NAT_GATEWAY_FIXTURES.values() if nat.get("State") == state]


def get_eip_by_allocation_id(allocation_id: str) -> dict[str, Any] | None:
    """Get Elastic IP fixture by allocation ID."""
    return EIP_FIXTURES.get(allocation_id)


def get_eip_by_public_ip(public_ip: str) -> dict[str, Any] | None:
    """Get Elastic IP fixture by public IP address."""
    for eip in EIP_FIXTURES.values():
        if eip.get("PublicIp") == public_ip:
            return eip
    return None


def get_eip_by_eni(eni_id: str) -> dict[str, Any] | None:
    """Get Elastic IP associated with a network interface."""
    for eip in EIP_FIXTURES.values():
        if eip.get("NetworkInterfaceId") == eni_id:
            return eip
    return None


def get_unallocated_eips() -> list[dict[str, Any]]:
    """Get all unallocated Elastic IPs (not associated with any resource)."""
    return [
        eip
        for eip in EIP_FIXTURES.values()
        if not eip.get("NetworkInterfaceId") and not eip.get("InstanceId")
    ]


def get_eigw_by_id(eigw_id: str) -> dict[str, Any] | None:
    """Get Egress-only Internet Gateway fixture by ID."""
    return EGRESS_ONLY_IGW_FIXTURES.get(eigw_id)


def get_eigw_by_vpc(vpc_id: str) -> dict[str, Any] | None:
    """Get Egress-only Internet Gateway attached to a VPC."""
    for eigw in EGRESS_ONLY_IGW_FIXTURES.values():
        if eigw.get("Attachments"):
            for attachment in eigw["Attachments"]:
                if attachment.get("VpcId") == vpc_id:
                    return eigw
    return None


def get_all_gateways_by_vpc(vpc_id: str) -> dict[str, Any]:
    """Get all gateway resources for a VPC (IGW, NAT, Egress-only IGW)."""
    return {
        "internet_gateway": get_igw_by_vpc(vpc_id),
        "nat_gateways": get_nat_by_vpc(vpc_id),
        "egress_only_igw": get_eigw_by_vpc(vpc_id),
    }


def get_gateway_summary() -> dict[str, int]:
    """Get summary counts of all gateway resources."""
    return {
        "internet_gateways": len(IGW_FIXTURES),
        "nat_gateways": len(NAT_GATEWAY_FIXTURES),
        "elastic_ips": len(EIP_FIXTURES),
        "egress_only_igws": len(EGRESS_ONLY_IGW_FIXTURES),
        "nat_available": len([n for n in NAT_GATEWAY_FIXTURES.values() if n["State"] == "available"]),
        "nat_pending": len([n for n in NAT_GATEWAY_FIXTURES.values() if n["State"] == "pending"]),
        "nat_deleting": len([n for n in NAT_GATEWAY_FIXTURES.values() if n["State"] == "deleting"]),
        "nat_failed": len([n for n in NAT_GATEWAY_FIXTURES.values() if n["State"] == "failed"]),
        "eip_allocated": len([e for e in EIP_FIXTURES.values() if e.get("NetworkInterfaceId")]),
        "eip_unallocated": len(get_unallocated_eips()),
    }
