"""Realistic VPC mock data fixtures.

Multi-region VPC architecture:
- eu-west-1: Production environment (10.0.0.0/16)
- us-east-1: Staging environment (10.1.0.0/16)
- ap-southeast-2: Development environment (10.2.0.0/16)

Each VPC includes:
- Public subnets (web tier)
- Private subnets (application tier)
- Database subnets (data tier)
- Complete route tables with appropriate routes
- Security groups for each tier
- Network ACLs
"""

from typing import Any

# =============================================================================
# VPC FIXTURES
# =============================================================================

VPC_FIXTURES: dict[str, dict[str, Any]] = {
    # Production VPC - eu-west-1
    "vpc-0prod1234567890ab": {
        "VpcId": "vpc-0prod1234567890ab",
        "CidrBlock": "10.0.0.0/16",
        "CidrBlockAssociationSet": [
            {
                "AssociationId": "vpc-cidr-assoc-0prod1234",
                "CidrBlock": "10.0.0.0/16",
                "CidrBlockState": {"State": "associated"},
            },
            {
                "AssociationId": "vpc-cidr-assoc-0prod5678",
                "CidrBlock": "100.64.0.0/16",
                "CidrBlockState": {"State": "associated"},
            },
        ],
        "State": "available",
        "IsDefault": False,
        "DhcpOptionsId": "dopt-0prod12345678",
        "InstanceTenancy": "default",
        "OwnerId": "123456789012",
        "Tags": [
            {"Key": "Name", "Value": "production-vpc"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "ManagedBy", "Value": "terraform"},
        ],
        "EnableDnsHostnames": True,
        "EnableDnsSupport": True,
    },
    # Staging VPC - us-east-1
    "vpc-0stag1234567890ab": {
        "VpcId": "vpc-0stag1234567890ab",
        "CidrBlock": "10.1.0.0/16",
        "CidrBlockAssociationSet": [
            {
                "AssociationId": "vpc-cidr-assoc-0stag1234",
                "CidrBlock": "10.1.0.0/16",
                "CidrBlockState": {"State": "associated"},
            },
        ],
        "State": "available",
        "IsDefault": False,
        "DhcpOptionsId": "dopt-0stag12345678",
        "InstanceTenancy": "default",
        "OwnerId": "123456789012",
        "Tags": [
            {"Key": "Name", "Value": "staging-vpc"},
            {"Key": "Environment", "Value": "staging"},
            {"Key": "ManagedBy", "Value": "terraform"},
        ],
        "EnableDnsHostnames": True,
        "EnableDnsSupport": True,
    },
    # Development VPC - ap-southeast-2
    "vpc-0dev01234567890ab": {
        "VpcId": "vpc-0dev01234567890ab",
        "CidrBlock": "10.2.0.0/16",
        "CidrBlockAssociationSet": [
            {
                "AssociationId": "vpc-cidr-assoc-0dev01234",
                "CidrBlock": "10.2.0.0/16",
                "CidrBlockState": {"State": "associated"},
            },
        ],
        "State": "available",
        "IsDefault": False,
        "DhcpOptionsId": "dopt-0dev012345678",
        "InstanceTenancy": "default",
        "OwnerId": "123456789012",
        "Tags": [
            {"Key": "Name", "Value": "development-vpc"},
            {"Key": "Environment", "Value": "development"},
            {"Key": "ManagedBy", "Value": "terraform"},
        ],
        "EnableDnsHostnames": True,
        "EnableDnsSupport": True,
    },
    # Shared Services VPC - eu-west-1
    "vpc-0shared123456789a": {
        "VpcId": "vpc-0shared123456789a",
        "CidrBlock": "10.100.0.0/16",
        "CidrBlockAssociationSet": [
            {
                "AssociationId": "vpc-cidr-assoc-0shared12",
                "CidrBlock": "10.100.0.0/16",
                "CidrBlockState": {"State": "associated"},
            },
        ],
        "State": "available",
        "IsDefault": False,
        "DhcpOptionsId": "dopt-0shared12345",
        "InstanceTenancy": "default",
        "OwnerId": "123456789012",
        "Tags": [
            {"Key": "Name", "Value": "shared-services-vpc"},
            {"Key": "Environment", "Value": "shared"},
            {"Key": "ManagedBy", "Value": "terraform"},
        ],
        "EnableDnsHostnames": True,
        "EnableDnsSupport": True,
    },
}

# =============================================================================
# SUBNET FIXTURES
# =============================================================================

SUBNET_FIXTURES: dict[str, dict[str, Any]] = {
    # Production VPC Subnets - eu-west-1
    # Public subnets (web tier)
    "subnet-0pub1a1234567890": {
        "SubnetId": "subnet-0pub1a1234567890",
        "VpcId": "vpc-0prod1234567890ab",
        "CidrBlock": "10.0.1.0/24",
        "AvailabilityZone": "eu-west-1a",
        "AvailabilityZoneId": "euw1-az1",
        "State": "available",
        "MapPublicIpOnLaunch": True,
        "DefaultForAz": False,
        "AvailableIpAddressCount": 251,
        "Tags": [
            {"Key": "Name", "Value": "production-public-eu-west-1a"},
            {"Key": "Tier", "Value": "public"},
            {"Key": "Environment", "Value": "production"},
        ],
    },
    "subnet-0pub1b1234567890": {
        "SubnetId": "subnet-0pub1b1234567890",
        "VpcId": "vpc-0prod1234567890ab",
        "CidrBlock": "10.0.2.0/24",
        "AvailabilityZone": "eu-west-1b",
        "AvailabilityZoneId": "euw1-az2",
        "State": "available",
        "MapPublicIpOnLaunch": True,
        "DefaultForAz": False,
        "AvailableIpAddressCount": 251,
        "Tags": [
            {"Key": "Name", "Value": "production-public-eu-west-1b"},
            {"Key": "Tier", "Value": "public"},
            {"Key": "Environment", "Value": "production"},
        ],
    },
    "subnet-0pub1c1234567890": {
        "SubnetId": "subnet-0pub1c1234567890",
        "VpcId": "vpc-0prod1234567890ab",
        "CidrBlock": "10.0.3.0/24",
        "AvailabilityZone": "eu-west-1c",
        "AvailabilityZoneId": "euw1-az3",
        "State": "available",
        "MapPublicIpOnLaunch": True,
        "DefaultForAz": False,
        "AvailableIpAddressCount": 251,
        "Tags": [
            {"Key": "Name", "Value": "production-public-eu-west-1c"},
            {"Key": "Tier", "Value": "public"},
            {"Key": "Environment", "Value": "production"},
        ],
    },
    # Private subnets (application tier)
    "subnet-0priv1a123456789": {
        "SubnetId": "subnet-0priv1a123456789",
        "VpcId": "vpc-0prod1234567890ab",
        "CidrBlock": "10.0.10.0/24",
        "AvailabilityZone": "eu-west-1a",
        "AvailabilityZoneId": "euw1-az1",
        "State": "available",
        "MapPublicIpOnLaunch": False,
        "DefaultForAz": False,
        "AvailableIpAddressCount": 245,
        "Tags": [
            {"Key": "Name", "Value": "production-private-eu-west-1a"},
            {"Key": "Tier", "Value": "private"},
            {"Key": "Environment", "Value": "production"},
        ],
    },
    "subnet-0priv1b123456789": {
        "SubnetId": "subnet-0priv1b123456789",
        "VpcId": "vpc-0prod1234567890ab",
        "CidrBlock": "10.0.11.0/24",
        "AvailabilityZone": "eu-west-1b",
        "AvailabilityZoneId": "euw1-az2",
        "State": "available",
        "MapPublicIpOnLaunch": False,
        "DefaultForAz": False,
        "AvailableIpAddressCount": 248,
        "Tags": [
            {"Key": "Name", "Value": "production-private-eu-west-1b"},
            {"Key": "Tier", "Value": "private"},
            {"Key": "Environment", "Value": "production"},
        ],
    },
    "subnet-0priv1c123456789": {
        "SubnetId": "subnet-0priv1c123456789",
        "VpcId": "vpc-0prod1234567890ab",
        "CidrBlock": "10.0.12.0/24",
        "AvailabilityZone": "eu-west-1c",
        "AvailabilityZoneId": "euw1-az3",
        "State": "available",
        "MapPublicIpOnLaunch": False,
        "DefaultForAz": False,
        "AvailableIpAddressCount": 250,
        "Tags": [
            {"Key": "Name", "Value": "production-private-eu-west-1c"},
            {"Key": "Tier", "Value": "private"},
            {"Key": "Environment", "Value": "production"},
        ],
    },
    # Database subnets (data tier)
    "subnet-0db1a12345678901": {
        "SubnetId": "subnet-0db1a12345678901",
        "VpcId": "vpc-0prod1234567890ab",
        "CidrBlock": "10.0.20.0/24",
        "AvailabilityZone": "eu-west-1a",
        "AvailabilityZoneId": "euw1-az1",
        "State": "available",
        "MapPublicIpOnLaunch": False,
        "DefaultForAz": False,
        "AvailableIpAddressCount": 250,
        "Tags": [
            {"Key": "Name", "Value": "production-database-eu-west-1a"},
            {"Key": "Tier", "Value": "database"},
            {"Key": "Environment", "Value": "production"},
        ],
    },
    "subnet-0db1b12345678901": {
        "SubnetId": "subnet-0db1b12345678901",
        "VpcId": "vpc-0prod1234567890ab",
        "CidrBlock": "10.0.21.0/24",
        "AvailabilityZone": "eu-west-1b",
        "AvailabilityZoneId": "euw1-az2",
        "State": "available",
        "MapPublicIpOnLaunch": False,
        "DefaultForAz": False,
        "AvailableIpAddressCount": 250,
        "Tags": [
            {"Key": "Name", "Value": "production-database-eu-west-1b"},
            {"Key": "Tier", "Value": "database"},
            {"Key": "Environment", "Value": "production"},
        ],
    },
    # Transit Gateway subnets
    "subnet-0tgw1a1234567890": {
        "SubnetId": "subnet-0tgw1a1234567890",
        "VpcId": "vpc-0prod1234567890ab",
        "CidrBlock": "10.0.254.0/28",
        "AvailabilityZone": "eu-west-1a",
        "AvailabilityZoneId": "euw1-az1",
        "State": "available",
        "MapPublicIpOnLaunch": False,
        "DefaultForAz": False,
        "AvailableIpAddressCount": 11,
        "Tags": [
            {"Key": "Name", "Value": "production-tgw-eu-west-1a"},
            {"Key": "Tier", "Value": "transit"},
            {"Key": "Environment", "Value": "production"},
        ],
    },
    "subnet-0tgw1b1234567890": {
        "SubnetId": "subnet-0tgw1b1234567890",
        "VpcId": "vpc-0prod1234567890ab",
        "CidrBlock": "10.0.254.16/28",
        "AvailabilityZone": "eu-west-1b",
        "AvailabilityZoneId": "euw1-az2",
        "State": "available",
        "MapPublicIpOnLaunch": False,
        "DefaultForAz": False,
        "AvailableIpAddressCount": 11,
        "Tags": [
            {"Key": "Name", "Value": "production-tgw-eu-west-1b"},
            {"Key": "Tier", "Value": "transit"},
            {"Key": "Environment", "Value": "production"},
        ],
    },
    # Staging VPC Subnets - us-east-1
    "subnet-0stgpub1a12345678": {
        "SubnetId": "subnet-0stgpub1a12345678",
        "VpcId": "vpc-0stag1234567890ab",
        "CidrBlock": "10.1.1.0/24",
        "AvailabilityZone": "us-east-1a",
        "AvailabilityZoneId": "use1-az1",
        "State": "available",
        "MapPublicIpOnLaunch": True,
        "DefaultForAz": False,
        "AvailableIpAddressCount": 251,
        "Tags": [
            {"Key": "Name", "Value": "staging-public-us-east-1a"},
            {"Key": "Tier", "Value": "public"},
            {"Key": "Environment", "Value": "staging"},
        ],
    },
    "subnet-0stgpriv1a1234567": {
        "SubnetId": "subnet-0stgpriv1a1234567",
        "VpcId": "vpc-0stag1234567890ab",
        "CidrBlock": "10.1.10.0/24",
        "AvailabilityZone": "us-east-1a",
        "AvailabilityZoneId": "use1-az1",
        "State": "available",
        "MapPublicIpOnLaunch": False,
        "DefaultForAz": False,
        "AvailableIpAddressCount": 249,
        "Tags": [
            {"Key": "Name", "Value": "staging-private-us-east-1a"},
            {"Key": "Tier", "Value": "private"},
            {"Key": "Environment", "Value": "staging"},
        ],
    },
    # Development VPC Subnets - ap-southeast-2
    "subnet-0devpub2a12345678": {
        "SubnetId": "subnet-0devpub2a12345678",
        "VpcId": "vpc-0dev01234567890ab",
        "CidrBlock": "10.2.1.0/24",
        "AvailabilityZone": "ap-southeast-2a",
        "AvailabilityZoneId": "apse2-az1",
        "State": "available",
        "MapPublicIpOnLaunch": True,
        "DefaultForAz": False,
        "AvailableIpAddressCount": 251,
        "Tags": [
            {"Key": "Name", "Value": "development-public-ap-southeast-2a"},
            {"Key": "Tier", "Value": "public"},
            {"Key": "Environment", "Value": "development"},
        ],
    },
    "subnet-0devpriv2a1234567": {
        "SubnetId": "subnet-0devpriv2a1234567",
        "VpcId": "vpc-0dev01234567890ab",
        "CidrBlock": "10.2.10.0/24",
        "AvailabilityZone": "ap-southeast-2a",
        "AvailabilityZoneId": "apse2-az1",
        "State": "available",
        "MapPublicIpOnLaunch": False,
        "DefaultForAz": False,
        "AvailableIpAddressCount": 248,
        "Tags": [
            {"Key": "Name", "Value": "development-private-ap-southeast-2a"},
            {"Key": "Tier", "Value": "private"},
            {"Key": "Environment", "Value": "development"},
        ],
    },
}

# =============================================================================
# ROUTE TABLE FIXTURES
# =============================================================================

ROUTE_TABLE_FIXTURES: dict[str, dict[str, Any]] = {
    # Production VPC - Public Route Table
    "rtb-0prodpub123456789": {
        "RouteTableId": "rtb-0prodpub123456789",
        "VpcId": "vpc-0prod1234567890ab",
        "Routes": [
            {
                "DestinationCidrBlock": "10.0.0.0/16",
                "GatewayId": "local",
                "Origin": "CreateRouteTable",
                "State": "active",
            },
            {
                "DestinationCidrBlock": "0.0.0.0/0",
                "GatewayId": "igw-0prod12345678901",
                "Origin": "CreateRoute",
                "State": "active",
            },
            {
                "DestinationCidrBlock": "10.1.0.0/16",
                "TransitGatewayId": "tgw-0prod12345678901",
                "Origin": "CreateRoute",
                "State": "active",
            },
            {
                "DestinationCidrBlock": "10.2.0.0/16",
                "TransitGatewayId": "tgw-0prod12345678901",
                "Origin": "CreateRoute",
                "State": "active",
            },
        ],
        "Associations": [
            {
                "RouteTableAssociationId": "rtbassoc-0pub1a1234",
                "RouteTableId": "rtb-0prodpub123456789",
                "SubnetId": "subnet-0pub1a1234567890",
                "AssociationState": {"State": "associated"},
            },
            {
                "RouteTableAssociationId": "rtbassoc-0pub1b1234",
                "RouteTableId": "rtb-0prodpub123456789",
                "SubnetId": "subnet-0pub1b1234567890",
                "AssociationState": {"State": "associated"},
            },
            {
                "RouteTableAssociationId": "rtbassoc-0pub1c1234",
                "RouteTableId": "rtb-0prodpub123456789",
                "SubnetId": "subnet-0pub1c1234567890",
                "AssociationState": {"State": "associated"},
            },
        ],
        "Tags": [
            {"Key": "Name", "Value": "production-public-rt"},
            {"Key": "Environment", "Value": "production"},
        ],
    },
    # Production VPC - Private Route Table (AZ-a with NAT Gateway)
    "rtb-0prodpriv1a123456": {
        "RouteTableId": "rtb-0prodpriv1a123456",
        "VpcId": "vpc-0prod1234567890ab",
        "Routes": [
            {
                "DestinationCidrBlock": "10.0.0.0/16",
                "GatewayId": "local",
                "Origin": "CreateRouteTable",
                "State": "active",
            },
            {
                "DestinationCidrBlock": "0.0.0.0/0",
                "NatGatewayId": "nat-0prod1a12345678",
                "Origin": "CreateRoute",
                "State": "active",
            },
            {
                "DestinationCidrBlock": "10.1.0.0/16",
                "TransitGatewayId": "tgw-0prod12345678901",
                "Origin": "CreateRoute",
                "State": "active",
            },
            {
                "DestinationCidrBlock": "10.2.0.0/16",
                "TransitGatewayId": "tgw-0prod12345678901",
                "Origin": "CreateRoute",
                "State": "active",
            },
            {
                "DestinationCidrBlock": "10.100.0.0/16",
                "TransitGatewayId": "tgw-0prod12345678901",
                "Origin": "CreateRoute",
                "State": "active",
            },
        ],
        "Associations": [
            {
                "RouteTableAssociationId": "rtbassoc-0priv1a123",
                "RouteTableId": "rtb-0prodpriv1a123456",
                "SubnetId": "subnet-0priv1a123456789",
                "AssociationState": {"State": "associated"},
            },
        ],
        "Tags": [
            {"Key": "Name", "Value": "production-private-rt-1a"},
            {"Key": "Environment", "Value": "production"},
        ],
    },
    # Production VPC - Private Route Table (AZ-b with NAT Gateway)
    "rtb-0prodpriv1b123456": {
        "RouteTableId": "rtb-0prodpriv1b123456",
        "VpcId": "vpc-0prod1234567890ab",
        "Routes": [
            {
                "DestinationCidrBlock": "10.0.0.0/16",
                "GatewayId": "local",
                "Origin": "CreateRouteTable",
                "State": "active",
            },
            {
                "DestinationCidrBlock": "0.0.0.0/0",
                "NatGatewayId": "nat-0prod1b12345678",
                "Origin": "CreateRoute",
                "State": "active",
            },
            {
                "DestinationCidrBlock": "10.1.0.0/16",
                "TransitGatewayId": "tgw-0prod12345678901",
                "Origin": "CreateRoute",
                "State": "active",
            },
        ],
        "Associations": [
            {
                "RouteTableAssociationId": "rtbassoc-0priv1b123",
                "RouteTableId": "rtb-0prodpriv1b123456",
                "SubnetId": "subnet-0priv1b123456789",
                "AssociationState": {"State": "associated"},
            },
        ],
        "Tags": [
            {"Key": "Name", "Value": "production-private-rt-1b"},
            {"Key": "Environment", "Value": "production"},
        ],
    },
    # Production VPC - Database Route Table (isolated)
    "rtb-0proddb123456789a": {
        "RouteTableId": "rtb-0proddb123456789a",
        "VpcId": "vpc-0prod1234567890ab",
        "Routes": [
            {
                "DestinationCidrBlock": "10.0.0.0/16",
                "GatewayId": "local",
                "Origin": "CreateRouteTable",
                "State": "active",
            },
        ],
        "Associations": [
            {
                "RouteTableAssociationId": "rtbassoc-0db1a1234",
                "RouteTableId": "rtb-0proddb123456789a",
                "SubnetId": "subnet-0db1a12345678901",
                "AssociationState": {"State": "associated"},
            },
            {
                "RouteTableAssociationId": "rtbassoc-0db1b1234",
                "RouteTableId": "rtb-0proddb123456789a",
                "SubnetId": "subnet-0db1b12345678901",
                "AssociationState": {"State": "associated"},
            },
        ],
        "Tags": [
            {"Key": "Name", "Value": "production-database-rt"},
            {"Key": "Environment", "Value": "production"},
        ],
    },
    # Production VPC - Transit Gateway Route Table
    "rtb-0prodtgw123456789": {
        "RouteTableId": "rtb-0prodtgw123456789",
        "VpcId": "vpc-0prod1234567890ab",
        "Routes": [
            {
                "DestinationCidrBlock": "10.0.0.0/16",
                "GatewayId": "local",
                "Origin": "CreateRouteTable",
                "State": "active",
            },
            {
                "DestinationCidrBlock": "0.0.0.0/0",
                "TransitGatewayId": "tgw-0prod12345678901",
                "Origin": "CreateRoute",
                "State": "active",
            },
        ],
        "Associations": [
            {
                "RouteTableAssociationId": "rtbassoc-0tgw1a1234",
                "RouteTableId": "rtb-0prodtgw123456789",
                "SubnetId": "subnet-0tgw1a1234567890",
                "AssociationState": {"State": "associated"},
            },
            {
                "RouteTableAssociationId": "rtbassoc-0tgw1b1234",
                "RouteTableId": "rtb-0prodtgw123456789",
                "SubnetId": "subnet-0tgw1b1234567890",
                "AssociationState": {"State": "associated"},
            },
        ],
        "Tags": [
            {"Key": "Name", "Value": "production-tgw-rt"},
            {"Key": "Environment", "Value": "production"},
        ],
    },
    # Staging VPC - Public Route Table
    "rtb-0stagpub123456789": {
        "RouteTableId": "rtb-0stagpub123456789",
        "VpcId": "vpc-0stag1234567890ab",
        "Routes": [
            {
                "DestinationCidrBlock": "10.1.0.0/16",
                "GatewayId": "local",
                "Origin": "CreateRouteTable",
                "State": "active",
            },
            {
                "DestinationCidrBlock": "0.0.0.0/0",
                "GatewayId": "igw-0stag12345678901",
                "Origin": "CreateRoute",
                "State": "active",
            },
        ],
        "Associations": [
            {
                "RouteTableAssociationId": "rtbassoc-0stagpub1a",
                "RouteTableId": "rtb-0stagpub123456789",
                "SubnetId": "subnet-0stgpub1a12345678",
                "AssociationState": {"State": "associated"},
            },
        ],
        "Tags": [
            {"Key": "Name", "Value": "staging-public-rt"},
            {"Key": "Environment", "Value": "staging"},
        ],
    },
    # Development VPC - Public Route Table
    "rtb-0devpub1234567890": {
        "RouteTableId": "rtb-0devpub1234567890",
        "VpcId": "vpc-0dev01234567890ab",
        "Routes": [
            {
                "DestinationCidrBlock": "10.2.0.0/16",
                "GatewayId": "local",
                "Origin": "CreateRouteTable",
                "State": "active",
            },
            {
                "DestinationCidrBlock": "0.0.0.0/0",
                "GatewayId": "igw-0dev012345678901",
                "Origin": "CreateRoute",
                "State": "active",
            },
        ],
        "Associations": [
            {
                "RouteTableAssociationId": "rtbassoc-0devpub2a",
                "RouteTableId": "rtb-0devpub1234567890",
                "SubnetId": "subnet-0devpub2a12345678",
                "AssociationState": {"State": "associated"},
            },
        ],
        "Tags": [
            {"Key": "Name", "Value": "development-public-rt"},
            {"Key": "Environment", "Value": "development"},
        ],
    },
}

# =============================================================================
# SECURITY GROUP FIXTURES
# =============================================================================

SECURITY_GROUP_FIXTURES: dict[str, dict[str, Any]] = {
    # Production - Web Tier Security Group (ALB)
    "sg-0prodweb123456789": {
        "GroupId": "sg-0prodweb123456789",
        "GroupName": "production-web-alb-sg",
        "Description": "Security group for production ALB",
        "VpcId": "vpc-0prod1234567890ab",
        "IpPermissions": [
            {
                "IpProtocol": "tcp",
                "FromPort": 443,
                "ToPort": 443,
                "IpRanges": [
                    {"CidrIp": "0.0.0.0/0", "Description": "HTTPS from internet"}
                ],
            },
            {
                "IpProtocol": "tcp",
                "FromPort": 80,
                "ToPort": 80,
                "IpRanges": [
                    {
                        "CidrIp": "0.0.0.0/0",
                        "Description": "HTTP redirect from internet",
                    }
                ],
            },
        ],
        "IpPermissionsEgress": [
            {
                "IpProtocol": "-1",
                "IpRanges": [
                    {"CidrIp": "0.0.0.0/0", "Description": "Allow all outbound"}
                ],
            },
        ],
        "Tags": [
            {"Key": "Name", "Value": "production-web-alb-sg"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "Tier", "Value": "web"},
        ],
    },
    # Production - Application Tier Security Group
    "sg-0prodapp123456789": {
        "GroupId": "sg-0prodapp123456789",
        "GroupName": "production-app-sg",
        "Description": "Security group for production application servers",
        "VpcId": "vpc-0prod1234567890ab",
        "IpPermissions": [
            {
                "IpProtocol": "tcp",
                "FromPort": 8080,
                "ToPort": 8080,
                "UserIdGroupPairs": [
                    {
                        "GroupId": "sg-0prodweb123456789",
                        "Description": "HTTP from ALB",
                    }
                ],
            },
            {
                "IpProtocol": "tcp",
                "FromPort": 22,
                "ToPort": 22,
                "IpRanges": [
                    {
                        "CidrIp": "10.100.0.0/16",
                        "Description": "SSH from shared services",
                    }
                ],
            },
        ],
        "IpPermissionsEgress": [
            {
                "IpProtocol": "-1",
                "IpRanges": [
                    {"CidrIp": "0.0.0.0/0", "Description": "Allow all outbound"}
                ],
            },
        ],
        "Tags": [
            {"Key": "Name", "Value": "production-app-sg"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "Tier", "Value": "application"},
        ],
    },
    # Production - Database Tier Security Group
    "sg-0proddb1234567890": {
        "GroupId": "sg-0proddb1234567890",
        "GroupName": "production-db-sg",
        "Description": "Security group for production database",
        "VpcId": "vpc-0prod1234567890ab",
        "IpPermissions": [
            {
                "IpProtocol": "tcp",
                "FromPort": 5432,
                "ToPort": 5432,
                "UserIdGroupPairs": [
                    {
                        "GroupId": "sg-0prodapp123456789",
                        "Description": "PostgreSQL from application tier",
                    }
                ],
            },
            {
                "IpProtocol": "tcp",
                "FromPort": 5432,
                "ToPort": 5432,
                "IpRanges": [
                    {
                        "CidrIp": "10.100.10.0/24",
                        "Description": "PostgreSQL from bastion",
                    }
                ],
            },
        ],
        "IpPermissionsEgress": [
            {
                "IpProtocol": "-1",
                "IpRanges": [
                    {"CidrIp": "0.0.0.0/0", "Description": "Allow all outbound"}
                ],
            },
        ],
        "Tags": [
            {"Key": "Name", "Value": "production-db-sg"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "Tier", "Value": "database"},
        ],
    },
    # Shared Services - Bastion Security Group
    "sg-0sharedbastion1234": {
        "GroupId": "sg-0sharedbastion1234",
        "GroupName": "shared-bastion-sg",
        "Description": "Security group for bastion hosts",
        "VpcId": "vpc-0shared123456789a",
        "IpPermissions": [
            {
                "IpProtocol": "tcp",
                "FromPort": 22,
                "ToPort": 22,
                "IpRanges": [
                    {
                        "CidrIp": "203.0.113.0/24",
                        "Description": "SSH from corporate IP range",
                    }
                ],
            },
        ],
        "IpPermissionsEgress": [
            {
                "IpProtocol": "tcp",
                "FromPort": 22,
                "ToPort": 22,
                "IpRanges": [
                    {
                        "CidrIp": "10.0.0.0/8",
                        "Description": "SSH to all internal networks",
                    }
                ],
            },
            {
                "IpProtocol": "tcp",
                "FromPort": 443,
                "ToPort": 443,
                "IpRanges": [{"CidrIp": "0.0.0.0/0", "Description": "HTTPS outbound"}],
            },
        ],
        "Tags": [
            {"Key": "Name", "Value": "shared-bastion-sg"},
            {"Key": "Environment", "Value": "shared"},
            {"Key": "Purpose", "Value": "bastion"},
        ],
    },
    # Staging - Application Security Group
    "sg-0stagapp123456789a": {
        "GroupId": "sg-0stagapp123456789a",
        "GroupName": "staging-app-sg",
        "Description": "Security group for staging application",
        "VpcId": "vpc-0stag1234567890ab",
        "IpPermissions": [
            {
                "IpProtocol": "tcp",
                "FromPort": 8080,
                "ToPort": 8080,
                "IpRanges": [
                    {"CidrIp": "0.0.0.0/0", "Description": "HTTP from anywhere"}
                ],
            },
            {
                "IpProtocol": "tcp",
                "FromPort": 22,
                "ToPort": 22,
                "IpRanges": [
                    {"CidrIp": "10.0.0.0/8", "Description": "SSH from internal"}
                ],
            },
        ],
        "IpPermissionsEgress": [
            {
                "IpProtocol": "-1",
                "IpRanges": [
                    {"CidrIp": "0.0.0.0/0", "Description": "Allow all outbound"}
                ],
            },
        ],
        "Tags": [
            {"Key": "Name", "Value": "staging-app-sg"},
            {"Key": "Environment", "Value": "staging"},
        ],
    },
    # Development - Permissive Security Group
    "sg-0devall12345678901": {
        "GroupId": "sg-0devall12345678901",
        "GroupName": "development-all-sg",
        "Description": "Permissive security group for development",
        "VpcId": "vpc-0dev01234567890ab",
        "IpPermissions": [
            {
                "IpProtocol": "-1",
                "IpRanges": [
                    {"CidrIp": "10.0.0.0/8", "Description": "All from internal"}
                ],
            },
        ],
        "IpPermissionsEgress": [
            {
                "IpProtocol": "-1",
                "IpRanges": [
                    {"CidrIp": "0.0.0.0/0", "Description": "Allow all outbound"}
                ],
            },
        ],
        "Tags": [
            {"Key": "Name", "Value": "development-all-sg"},
            {"Key": "Environment", "Value": "development"},
        ],
    },
}

# =============================================================================
# NETWORK ACL FIXTURES
# =============================================================================

NACL_FIXTURES: dict[str, dict[str, Any]] = {
    # Production VPC - Public NACL
    "acl-0prodpub123456789": {
        "NetworkAclId": "acl-0prodpub123456789",
        "VpcId": "vpc-0prod1234567890ab",
        "IsDefault": False,
        "Entries": [
            # Inbound rules
            {
                "RuleNumber": 100,
                "Protocol": "6",  # TCP
                "RuleAction": "allow",
                "Egress": False,
                "CidrBlock": "0.0.0.0/0",
                "PortRange": {"From": 443, "To": 443},
            },
            {
                "RuleNumber": 110,
                "Protocol": "6",
                "RuleAction": "allow",
                "Egress": False,
                "CidrBlock": "0.0.0.0/0",
                "PortRange": {"From": 80, "To": 80},
            },
            {
                "RuleNumber": 120,
                "Protocol": "6",
                "RuleAction": "allow",
                "Egress": False,
                "CidrBlock": "0.0.0.0/0",
                "PortRange": {"From": 1024, "To": 65535},
            },
            {
                "RuleNumber": 32767,
                "Protocol": "-1",
                "RuleAction": "deny",
                "Egress": False,
                "CidrBlock": "0.0.0.0/0",
            },
            # Outbound rules
            {
                "RuleNumber": 100,
                "Protocol": "6",
                "RuleAction": "allow",
                "Egress": True,
                "CidrBlock": "0.0.0.0/0",
                "PortRange": {"From": 443, "To": 443},
            },
            {
                "RuleNumber": 110,
                "Protocol": "6",
                "RuleAction": "allow",
                "Egress": True,
                "CidrBlock": "0.0.0.0/0",
                "PortRange": {"From": 80, "To": 80},
            },
            {
                "RuleNumber": 120,
                "Protocol": "6",
                "RuleAction": "allow",
                "Egress": True,
                "CidrBlock": "0.0.0.0/0",
                "PortRange": {"From": 1024, "To": 65535},
            },
            {
                "RuleNumber": 32767,
                "Protocol": "-1",
                "RuleAction": "deny",
                "Egress": True,
                "CidrBlock": "0.0.0.0/0",
            },
        ],
        "Associations": [
            {
                "NetworkAclAssociationId": "aclassoc-0pub1a123",
                "NetworkAclId": "acl-0prodpub123456789",
                "SubnetId": "subnet-0pub1a1234567890",
            },
            {
                "NetworkAclAssociationId": "aclassoc-0pub1b123",
                "NetworkAclId": "acl-0prodpub123456789",
                "SubnetId": "subnet-0pub1b1234567890",
            },
            {
                "NetworkAclAssociationId": "aclassoc-0pub1c123",
                "NetworkAclId": "acl-0prodpub123456789",
                "SubnetId": "subnet-0pub1c1234567890",
            },
        ],
        "Tags": [
            {"Key": "Name", "Value": "production-public-nacl"},
            {"Key": "Environment", "Value": "production"},
        ],
    },
    # Production VPC - Private NACL
    "acl-0prodpriv12345678": {
        "NetworkAclId": "acl-0prodpriv12345678",
        "VpcId": "vpc-0prod1234567890ab",
        "IsDefault": False,
        "Entries": [
            # Inbound rules
            {
                "RuleNumber": 100,
                "Protocol": "6",
                "RuleAction": "allow",
                "Egress": False,
                "CidrBlock": "10.0.0.0/16",
                "PortRange": {"From": 8080, "To": 8080},
            },
            {
                "RuleNumber": 110,
                "Protocol": "6",
                "RuleAction": "allow",
                "Egress": False,
                "CidrBlock": "10.100.0.0/16",
                "PortRange": {"From": 22, "To": 22},
            },
            {
                "RuleNumber": 120,
                "Protocol": "6",
                "RuleAction": "allow",
                "Egress": False,
                "CidrBlock": "0.0.0.0/0",
                "PortRange": {"From": 1024, "To": 65535},
            },
            {
                "RuleNumber": 32767,
                "Protocol": "-1",
                "RuleAction": "deny",
                "Egress": False,
                "CidrBlock": "0.0.0.0/0",
            },
            # Outbound rules
            {
                "RuleNumber": 100,
                "Protocol": "-1",
                "RuleAction": "allow",
                "Egress": True,
                "CidrBlock": "0.0.0.0/0",
            },
            {
                "RuleNumber": 32767,
                "Protocol": "-1",
                "RuleAction": "deny",
                "Egress": True,
                "CidrBlock": "0.0.0.0/0",
            },
        ],
        "Associations": [
            {
                "NetworkAclAssociationId": "aclassoc-0priv1a12",
                "NetworkAclId": "acl-0prodpriv12345678",
                "SubnetId": "subnet-0priv1a123456789",
            },
            {
                "NetworkAclAssociationId": "aclassoc-0priv1b12",
                "NetworkAclId": "acl-0prodpriv12345678",
                "SubnetId": "subnet-0priv1b123456789",
            },
            {
                "NetworkAclAssociationId": "aclassoc-0priv1c12",
                "NetworkAclId": "acl-0prodpriv12345678",
                "SubnetId": "subnet-0priv1c123456789",
            },
        ],
        "Tags": [
            {"Key": "Name", "Value": "production-private-nacl"},
            {"Key": "Environment", "Value": "production"},
        ],
    },
    # Production VPC - Database NACL (restrictive)
    "acl-0proddb1234567890": {
        "NetworkAclId": "acl-0proddb1234567890",
        "VpcId": "vpc-0prod1234567890ab",
        "IsDefault": False,
        "Entries": [
            # Inbound rules
            {
                "RuleNumber": 100,
                "Protocol": "6",
                "RuleAction": "allow",
                "Egress": False,
                "CidrBlock": "10.0.10.0/24",
                "PortRange": {"From": 5432, "To": 5432},
            },
            {
                "RuleNumber": 110,
                "Protocol": "6",
                "RuleAction": "allow",
                "Egress": False,
                "CidrBlock": "10.0.11.0/24",
                "PortRange": {"From": 5432, "To": 5432},
            },
            {
                "RuleNumber": 120,
                "Protocol": "6",
                "RuleAction": "allow",
                "Egress": False,
                "CidrBlock": "10.0.12.0/24",
                "PortRange": {"From": 5432, "To": 5432},
            },
            {
                "RuleNumber": 130,
                "Protocol": "6",
                "RuleAction": "allow",
                "Egress": False,
                "CidrBlock": "10.100.10.0/24",
                "PortRange": {"From": 5432, "To": 5432},
            },
            {
                "RuleNumber": 32767,
                "Protocol": "-1",
                "RuleAction": "deny",
                "Egress": False,
                "CidrBlock": "0.0.0.0/0",
            },
            # Outbound rules
            {
                "RuleNumber": 100,
                "Protocol": "6",
                "RuleAction": "allow",
                "Egress": True,
                "CidrBlock": "10.0.0.0/16",
                "PortRange": {"From": 1024, "To": 65535},
            },
            {
                "RuleNumber": 110,
                "Protocol": "6",
                "RuleAction": "allow",
                "Egress": True,
                "CidrBlock": "10.100.0.0/16",
                "PortRange": {"From": 1024, "To": 65535},
            },
            {
                "RuleNumber": 32767,
                "Protocol": "-1",
                "RuleAction": "deny",
                "Egress": True,
                "CidrBlock": "0.0.0.0/0",
            },
        ],
        "Associations": [
            {
                "NetworkAclAssociationId": "aclassoc-0db1a1234",
                "NetworkAclId": "acl-0proddb1234567890",
                "SubnetId": "subnet-0db1a12345678901",
            },
            {
                "NetworkAclAssociationId": "aclassoc-0db1b1234",
                "NetworkAclId": "acl-0proddb1234567890",
                "SubnetId": "subnet-0db1b12345678901",
            },
        ],
        "Tags": [
            {"Key": "Name", "Value": "production-database-nacl"},
            {"Key": "Environment", "Value": "production"},
        ],
    },
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_vpc_by_id(vpc_id: str) -> dict[str, Any] | None:
    """Get VPC fixture by ID."""
    return VPC_FIXTURES.get(vpc_id)


def get_vpc_detail(vpc_id: str) -> dict[str, Any] | None:
    """Get comprehensive VPC detail with all associated resources."""
    vpc = VPC_FIXTURES.get(vpc_id)
    if not vpc:
        return None

    # Gather associated subnets
    subnets = [s for s in SUBNET_FIXTURES.values() if s["VpcId"] == vpc_id]

    # Gather associated route tables
    route_tables = [rt for rt in ROUTE_TABLE_FIXTURES.values() if rt["VpcId"] == vpc_id]

    # Gather associated security groups
    security_groups = [
        sg for sg in SECURITY_GROUP_FIXTURES.values() if sg["VpcId"] == vpc_id
    ]

    # Gather associated NACLs
    nacls = [nacl for nacl in NACL_FIXTURES.values() if nacl["VpcId"] == vpc_id]

    return {
        "vpc": vpc,
        "subnets": subnets,
        "route_tables": route_tables,
        "security_groups": security_groups,
        "nacls": nacls,
    }


def get_subnets_by_vpc(vpc_id: str) -> list[dict[str, Any]]:
    """Get all subnets for a VPC."""
    return [s for s in SUBNET_FIXTURES.values() if s["VpcId"] == vpc_id]


def get_route_tables_by_vpc(vpc_id: str) -> list[dict[str, Any]]:
    """Get all route tables for a VPC."""
    return [rt for rt in ROUTE_TABLE_FIXTURES.values() if rt["VpcId"] == vpc_id]


def get_security_groups_by_vpc(vpc_id: str) -> list[dict[str, Any]]:
    """Get all security groups for a VPC."""
    return [sg for sg in SECURITY_GROUP_FIXTURES.values() if sg["VpcId"] == vpc_id]


def get_nacls_by_vpc(vpc_id: str) -> list[dict[str, Any]]:
    """Get all NACLs for a VPC."""
    return [nacl for nacl in NACL_FIXTURES.values() if nacl["VpcId"] == vpc_id]
