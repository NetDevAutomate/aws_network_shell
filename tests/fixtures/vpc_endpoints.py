"""Realistic VPC Endpoints and PrivateLink mock data fixtures.

VPC Endpoint architecture:
- Interface Endpoints (PrivateLink): S3, DynamoDB, Lambda, EC2 API across multiple AZs
- Gateway Endpoints: S3 and DynamoDB with route table associations
- VPC Endpoint Services: Provider-side endpoint services with NLB backends
- Endpoint Connections: Consumer connections to endpoint services

Architecture scenarios:
- Production: Interface endpoints for AWS services with private DNS
- Staging: Mix of interface and gateway endpoints
- Shared Services: Provider endpoint services for shared applications
- Multiple states: available, pending, deleting for testing

Each endpoint includes:
- Multiple ENIs across availability zones (Interface endpoints)
- Security groups and private DNS configuration
- Route table associations (Gateway endpoints)
- Service connections and acceptance requirements
"""

from typing import Any
from datetime import datetime, timezone

# =============================================================================
# INTERFACE VPC ENDPOINT FIXTURES (PrivateLink Consumer)
# =============================================================================

INTERFACE_VPC_ENDPOINT_FIXTURES: dict[str, dict[str, Any]] = {
    # Production - S3 Interface Endpoint (eu-west-1)
    "vpce-0prods3iface123456": {
        "VpcEndpointId": "vpce-0prods3iface123456",
        "VpcEndpointType": "Interface",
        "VpcId": "vpc-0prod1234567890ab",
        "ServiceName": "com.amazonaws.eu-west-1.s3",
        "State": "available",
        "PolicyDocument": None,
        "RouteTableIds": [],
        "SubnetIds": [
            "subnet-0priv1a123456789",
            "subnet-0priv1b123456789",
            "subnet-0priv1c123456789",
        ],
        "Groups": [
            {"GroupId": "sg-0prodapp123456789", "GroupName": "production-app-sg"}
        ],
        "PrivateDnsEnabled": True,
        "RequesterManaged": False,
        "NetworkInterfaceIds": [
            "eni-0prods3ep1a1234567",
            "eni-0prods3ep1b1234567",
            "eni-0prods3ep1c1234567",
        ],
        "DnsEntries": [
            {
                "DnsName": "vpce-0prods3iface123456-abc123.s3.eu-west-1.vpce.amazonaws.com",
                "HostedZoneId": "Z7HUB22UULQXV",
            },
            {
                "DnsName": "vpce-0prods3iface123456-abc123-eu-west-1a.s3.eu-west-1.vpce.amazonaws.com",
                "HostedZoneId": "Z7HUB22UULQXV",
            },
            {
                "DnsName": "vpce-0prods3iface123456-abc123-eu-west-1b.s3.eu-west-1.vpce.amazonaws.com",
                "HostedZoneId": "Z7HUB22UULQXV",
            },
            {
                "DnsName": "vpce-0prods3iface123456-abc123-eu-west-1c.s3.eu-west-1.vpce.amazonaws.com",
                "HostedZoneId": "Z7HUB22UULQXV",
            },
            {
                "DnsName": "bucket.vpce-0prods3iface123456-abc123.s3.eu-west-1.vpce.amazonaws.com"
            },
            {"DnsName": "s3.eu-west-1.amazonaws.com"},
        ],
        "CreationTimestamp": datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc),
        "Tags": [
            {"Key": "Name", "Value": "production-s3-interface-endpoint"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "Service", "Value": "s3"},
        ],
        "OwnerId": "123456789012",
    },
    # Production - DynamoDB Interface Endpoint (eu-west-1)
    "vpce-0proddynamoiface12": {
        "VpcEndpointId": "vpce-0proddynamoiface12",
        "VpcEndpointType": "Interface",
        "VpcId": "vpc-0prod1234567890ab",
        "ServiceName": "com.amazonaws.eu-west-1.dynamodb",
        "State": "available",
        "PolicyDocument": None,
        "RouteTableIds": [],
        "SubnetIds": [
            "subnet-0priv1a123456789",
            "subnet-0priv1b123456789",
        ],
        "Groups": [
            {"GroupId": "sg-0prodapp123456789", "GroupName": "production-app-sg"}
        ],
        "PrivateDnsEnabled": True,
        "RequesterManaged": False,
        "NetworkInterfaceIds": [
            "eni-0proddynep1a123456",
            "eni-0proddynep1b123456",
        ],
        "DnsEntries": [
            {
                "DnsName": "vpce-0proddynamoiface12-def456.dynamodb.eu-west-1.vpce.amazonaws.com",
                "HostedZoneId": "Z7HUB22UULQXV",
            },
            {
                "DnsName": "vpce-0proddynamoiface12-def456-eu-west-1a.dynamodb.eu-west-1.vpce.amazonaws.com",
                "HostedZoneId": "Z7HUB22UULQXV",
            },
            {
                "DnsName": "vpce-0proddynamoiface12-def456-eu-west-1b.dynamodb.eu-west-1.vpce.amazonaws.com",
                "HostedZoneId": "Z7HUB22UULQXV",
            },
            {"DnsName": "dynamodb.eu-west-1.amazonaws.com"},
        ],
        "CreationTimestamp": datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc),
        "Tags": [
            {"Key": "Name", "Value": "production-dynamodb-interface-endpoint"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "Service", "Value": "dynamodb"},
        ],
        "OwnerId": "123456789012",
    },
    # Production - Lambda Interface Endpoint (eu-west-1)
    "vpce-0prodlambdaiface12": {
        "VpcEndpointId": "vpce-0prodlambdaiface12",
        "VpcEndpointType": "Interface",
        "VpcId": "vpc-0prod1234567890ab",
        "ServiceName": "com.amazonaws.eu-west-1.lambda",
        "State": "available",
        "PolicyDocument": None,
        "RouteTableIds": [],
        "SubnetIds": [
            "subnet-0priv1a123456789",
            "subnet-0priv1b123456789",
            "subnet-0priv1c123456789",
        ],
        "Groups": [
            {"GroupId": "sg-0prodapp123456789", "GroupName": "production-app-sg"}
        ],
        "PrivateDnsEnabled": True,
        "RequesterManaged": False,
        "NetworkInterfaceIds": [
            "eni-0prodlambep1a12345",
            "eni-0prodlambep1b12345",
            "eni-0prodlambep1c12345",
        ],
        "DnsEntries": [
            {
                "DnsName": "vpce-0prodlambdaiface12-ghi789.lambda.eu-west-1.vpce.amazonaws.com",
                "HostedZoneId": "Z7HUB22UULQXV",
            },
            {
                "DnsName": "vpce-0prodlambdaiface12-ghi789-eu-west-1a.lambda.eu-west-1.vpce.amazonaws.com",
                "HostedZoneId": "Z7HUB22UULQXV",
            },
            {
                "DnsName": "vpce-0prodlambdaiface12-ghi789-eu-west-1b.lambda.eu-west-1.vpce.amazonaws.com",
                "HostedZoneId": "Z7HUB22UULQXV",
            },
            {
                "DnsName": "vpce-0prodlambdaiface12-ghi789-eu-west-1c.lambda.eu-west-1.vpce.amazonaws.com",
                "HostedZoneId": "Z7HUB22UULQXV",
            },
            {"DnsName": "lambda.eu-west-1.amazonaws.com"},
        ],
        "CreationTimestamp": datetime(2024, 1, 15, 11, 0, 0, tzinfo=timezone.utc),
        "Tags": [
            {"Key": "Name", "Value": "production-lambda-interface-endpoint"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "Service", "Value": "lambda"},
        ],
        "OwnerId": "123456789012",
    },
    # Production - EC2 API Interface Endpoint (eu-west-1)
    "vpce-0prodec2apiface123": {
        "VpcEndpointId": "vpce-0prodec2apiface123",
        "VpcEndpointType": "Interface",
        "VpcId": "vpc-0prod1234567890ab",
        "ServiceName": "com.amazonaws.eu-west-1.ec2",
        "State": "available",
        "PolicyDocument": None,
        "RouteTableIds": [],
        "SubnetIds": [
            "subnet-0priv1a123456789",
            "subnet-0priv1b123456789",
        ],
        "Groups": [
            {"GroupId": "sg-0prodapp123456789", "GroupName": "production-app-sg"}
        ],
        "PrivateDnsEnabled": True,
        "RequesterManaged": False,
        "NetworkInterfaceIds": [
            "eni-0prodec2ep1a123456",
            "eni-0prodec2ep1b123456",
        ],
        "DnsEntries": [
            {
                "DnsName": "vpce-0prodec2apiface123-jkl012.ec2.eu-west-1.vpce.amazonaws.com",
                "HostedZoneId": "Z7HUB22UULQXV",
            },
            {
                "DnsName": "vpce-0prodec2apiface123-jkl012-eu-west-1a.ec2.eu-west-1.vpce.amazonaws.com",
                "HostedZoneId": "Z7HUB22UULQXV",
            },
            {
                "DnsName": "vpce-0prodec2apiface123-jkl012-eu-west-1b.ec2.eu-west-1.vpce.amazonaws.com",
                "HostedZoneId": "Z7HUB22UULQXV",
            },
            {"DnsName": "ec2.eu-west-1.amazonaws.com"},
        ],
        "CreationTimestamp": datetime(2024, 1, 15, 11, 30, 0, tzinfo=timezone.utc),
        "Tags": [
            {"Key": "Name", "Value": "production-ec2-api-interface-endpoint"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "Service", "Value": "ec2"},
        ],
        "OwnerId": "123456789012",
    },
    # Staging - S3 Interface Endpoint (us-east-1) - Pending state
    "vpce-0stags3iface123456": {
        "VpcEndpointId": "vpce-0stags3iface123456",
        "VpcEndpointType": "Interface",
        "VpcId": "vpc-0stag1234567890ab",
        "ServiceName": "com.amazonaws.us-east-1.s3",
        "State": "pending",
        "PolicyDocument": None,
        "RouteTableIds": [],
        "SubnetIds": ["subnet-0stgpriv1a1234567"],
        "Groups": [{"GroupId": "sg-0stagapp123456789a", "GroupName": "staging-app-sg"}],
        "PrivateDnsEnabled": True,
        "RequesterManaged": False,
        "NetworkInterfaceIds": ["eni-0stags3ep1a1234567"],
        "DnsEntries": [
            {
                "DnsName": "vpce-0stags3iface123456-mno345.s3.us-east-1.vpce.amazonaws.com",
                "HostedZoneId": "Z7HUB22UULQXV",
            },
        ],
        "CreationTimestamp": datetime(2024, 2, 1, 14, 0, 0, tzinfo=timezone.utc),
        "Tags": [
            {"Key": "Name", "Value": "staging-s3-interface-endpoint"},
            {"Key": "Environment", "Value": "staging"},
            {"Key": "Service", "Value": "s3"},
        ],
        "OwnerId": "123456789012",
    },
    # Shared Services - Custom Endpoint Service Consumer (eu-west-1)
    "vpce-0sharedappservice12": {
        "VpcEndpointId": "vpce-0sharedappservice12",
        "VpcEndpointType": "Interface",
        "VpcId": "vpc-0prod1234567890ab",
        "ServiceName": "com.amazonaws.vpce.eu-west-1.vpce-svc-0shared1234567890",
        "State": "available",
        "PolicyDocument": None,
        "RouteTableIds": [],
        "SubnetIds": [
            "subnet-0priv1a123456789",
            "subnet-0priv1b123456789",
        ],
        "Groups": [
            {"GroupId": "sg-0prodapp123456789", "GroupName": "production-app-sg"}
        ],
        "PrivateDnsEnabled": False,
        "RequesterManaged": False,
        "NetworkInterfaceIds": [
            "eni-0sharedapp1a123456",
            "eni-0sharedapp1b123456",
        ],
        "DnsEntries": [
            {
                "DnsName": "vpce-0sharedappservice12-pqr678.vpce-svc-0shared1234567890.eu-west-1.vpce.amazonaws.com",
                "HostedZoneId": "Z7HUB22UULQXV",
            },
            {
                "DnsName": "vpce-0sharedappservice12-pqr678-eu-west-1a.vpce-svc-0shared1234567890.eu-west-1.vpce.amazonaws.com",
                "HostedZoneId": "Z7HUB22UULQXV",
            },
            {
                "DnsName": "vpce-0sharedappservice12-pqr678-eu-west-1b.vpce-svc-0shared1234567890.eu-west-1.vpce.amazonaws.com",
                "HostedZoneId": "Z7HUB22UULQXV",
            },
        ],
        "CreationTimestamp": datetime(2024, 1, 20, 9, 0, 0, tzinfo=timezone.utc),
        "Tags": [
            {"Key": "Name", "Value": "production-shared-app-endpoint"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "Service", "Value": "shared-app-service"},
        ],
        "OwnerId": "123456789012",
    },
    # Development - Lambda Interface Endpoint (ap-southeast-2) - Deleting state
    "vpce-0devlambdaiface123": {
        "VpcEndpointId": "vpce-0devlambdaiface123",
        "VpcEndpointType": "Interface",
        "VpcId": "vpc-0dev01234567890ab",
        "ServiceName": "com.amazonaws.ap-southeast-2.lambda",
        "State": "deleting",
        "PolicyDocument": None,
        "RouteTableIds": [],
        "SubnetIds": ["subnet-0devpriv2a1234567"],
        "Groups": [
            {"GroupId": "sg-0devall12345678901", "GroupName": "development-all-sg"}
        ],
        "PrivateDnsEnabled": True,
        "RequesterManaged": False,
        "NetworkInterfaceIds": ["eni-0devlambep2a123456"],
        "DnsEntries": [],
        "CreationTimestamp": datetime(2024, 1, 10, 8, 0, 0, tzinfo=timezone.utc),
        "Tags": [
            {"Key": "Name", "Value": "development-lambda-interface-endpoint"},
            {"Key": "Environment", "Value": "development"},
            {"Key": "Service", "Value": "lambda"},
        ],
        "OwnerId": "123456789012",
    },
}

# =============================================================================
# GATEWAY VPC ENDPOINT FIXTURES
# =============================================================================

GATEWAY_VPC_ENDPOINT_FIXTURES: dict[str, dict[str, Any]] = {
    # Production - S3 Gateway Endpoint (eu-west-1)
    "vpce-0prods3gateway1234": {
        "VpcEndpointId": "vpce-0prods3gateway1234",
        "VpcEndpointType": "Gateway",
        "VpcId": "vpc-0prod1234567890ab",
        "ServiceName": "com.amazonaws.eu-west-1.s3",
        "State": "available",
        "PolicyDocument": '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":"*","Action":"s3:*","Resource":"*"}]}',
        "RouteTableIds": [
            "rtb-0prodpriv1a123456",
            "rtb-0prodpriv1b123456",
            "rtb-0proddb123456789a",
        ],
        "SubnetIds": [],
        "PrivateDnsEnabled": False,
        "RequesterManaged": False,
        "NetworkInterfaceIds": [],
        "DnsEntries": [],
        "CreationTimestamp": datetime(2024, 1, 10, 9, 0, 0, tzinfo=timezone.utc),
        "Tags": [
            {"Key": "Name", "Value": "production-s3-gateway-endpoint"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "Service", "Value": "s3"},
        ],
        "OwnerId": "123456789012",
    },
    # Production - DynamoDB Gateway Endpoint (eu-west-1)
    "vpce-0proddyngateway123": {
        "VpcEndpointId": "vpce-0proddyngateway123",
        "VpcEndpointType": "Gateway",
        "VpcId": "vpc-0prod1234567890ab",
        "ServiceName": "com.amazonaws.eu-west-1.dynamodb",
        "State": "available",
        "PolicyDocument": '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":"*","Action":"dynamodb:*","Resource":"*"}]}',
        "RouteTableIds": [
            "rtb-0prodpriv1a123456",
            "rtb-0prodpriv1b123456",
        ],
        "SubnetIds": [],
        "PrivateDnsEnabled": False,
        "RequesterManaged": False,
        "NetworkInterfaceIds": [],
        "DnsEntries": [],
        "CreationTimestamp": datetime(2024, 1, 10, 9, 30, 0, tzinfo=timezone.utc),
        "Tags": [
            {"Key": "Name", "Value": "production-dynamodb-gateway-endpoint"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "Service", "Value": "dynamodb"},
        ],
        "OwnerId": "123456789012",
    },
    # Staging - S3 Gateway Endpoint (us-east-1)
    "vpce-0stags3gateway1234": {
        "VpcEndpointId": "vpce-0stags3gateway1234",
        "VpcEndpointType": "Gateway",
        "VpcId": "vpc-0stag1234567890ab",
        "ServiceName": "com.amazonaws.us-east-1.s3",
        "State": "available",
        "PolicyDocument": '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":"*","Action":"s3:*","Resource":"*"}]}',
        "RouteTableIds": ["rtb-0stagpub123456789"],
        "SubnetIds": [],
        "PrivateDnsEnabled": False,
        "RequesterManaged": False,
        "NetworkInterfaceIds": [],
        "DnsEntries": [],
        "CreationTimestamp": datetime(2024, 2, 1, 10, 0, 0, tzinfo=timezone.utc),
        "Tags": [
            {"Key": "Name", "Value": "staging-s3-gateway-endpoint"},
            {"Key": "Environment", "Value": "staging"},
            {"Key": "Service", "Value": "s3"},
        ],
        "OwnerId": "123456789012",
    },
}

# =============================================================================
# VPC ENDPOINT SERVICE FIXTURES (PrivateLink Provider)
# =============================================================================

VPC_ENDPOINT_SERVICE_FIXTURES: dict[str, dict[str, Any]] = {
    # Shared Services - Application Endpoint Service (eu-west-1)
    "vpce-svc-0shared1234567890": {
        "ServiceId": "vpce-svc-0shared1234567890",
        "ServiceName": "com.amazonaws.vpce.eu-west-1.vpce-svc-0shared1234567890",
        "ServiceState": "Available",
        "ServiceType": [{"ServiceType": "Interface"}],
        "AvailabilityZones": ["eu-west-1a", "eu-west-1b"],
        "AcceptanceRequired": True,
        "ManagesVpcEndpoints": False,
        "NetworkLoadBalancerArns": [
            "arn:aws:elasticloadbalancing:eu-west-1:123456789012:loadbalancer/net/production-nlb/xyz789abc123"
        ],
        "GatewayLoadBalancerArns": [],
        "PrivateDnsName": "app.shared-services.internal",
        "PrivateDnsNameConfiguration": {
            "State": "verified",
            "Type": "TXT",
            "Value": "vpce:abc123def456",
            "Name": "app.shared-services.internal",
        },
        "Tags": [
            {"Key": "Name", "Value": "shared-app-service"},
            {"Key": "Environment", "Value": "shared"},
            {"Key": "ManagedBy", "Value": "terraform"},
        ],
    },
    # Shared Services - Database Endpoint Service (eu-west-1)
    "vpce-svc-0shareddb12345678": {
        "ServiceId": "vpce-svc-0shareddb12345678",
        "ServiceName": "com.amazonaws.vpce.eu-west-1.vpce-svc-0shareddb12345678",
        "ServiceState": "Available",
        "ServiceType": [{"ServiceType": "Interface"}],
        "AvailabilityZones": ["eu-west-1a", "eu-west-1b"],
        "AcceptanceRequired": True,
        "ManagesVpcEndpoints": False,
        "NetworkLoadBalancerArns": [
            "arn:aws:elasticloadbalancing:eu-west-1:123456789012:loadbalancer/net/production-nlb/xyz789abc123"
        ],
        "GatewayLoadBalancerArns": [],
        "PrivateDnsName": "db.shared-services.internal",
        "PrivateDnsNameConfiguration": {
            "State": "verified",
            "Type": "TXT",
            "Value": "vpce:def456ghi789",
            "Name": "db.shared-services.internal",
        },
        "Tags": [
            {"Key": "Name", "Value": "shared-db-service"},
            {"Key": "Environment", "Value": "shared"},
            {"Key": "ManagedBy", "Value": "terraform"},
        ],
    },
    # Production - API Endpoint Service (eu-west-1) - No acceptance required
    "vpce-svc-0prodapi123456789": {
        "ServiceId": "vpce-svc-0prodapi123456789",
        "ServiceName": "com.amazonaws.vpce.eu-west-1.vpce-svc-0prodapi123456789",
        "ServiceState": "Available",
        "ServiceType": [{"ServiceType": "Interface"}],
        "AvailabilityZones": ["eu-west-1a", "eu-west-1b", "eu-west-1c"],
        "AcceptanceRequired": False,
        "ManagesVpcEndpoints": False,
        "NetworkLoadBalancerArns": [
            "arn:aws:elasticloadbalancing:eu-west-1:123456789012:loadbalancer/net/production-nlb/xyz789abc123"
        ],
        "GatewayLoadBalancerArns": [],
        "PrivateDnsName": "",
        "PrivateDnsNameConfiguration": {},
        "Tags": [
            {"Key": "Name", "Value": "production-api-service"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "Public", "Value": "true"},
        ],
    },
    # Staging - Test Endpoint Service (us-east-1) - Pending state
    "vpce-svc-0stagtest12345678": {
        "ServiceId": "vpce-svc-0stagtest12345678",
        "ServiceName": "com.amazonaws.vpce.us-east-1.vpce-svc-0stagtest12345678",
        "ServiceState": "Pending",
        "ServiceType": [{"ServiceType": "Interface"}],
        "AvailabilityZones": ["us-east-1a"],
        "AcceptanceRequired": True,
        "ManagesVpcEndpoints": False,
        "NetworkLoadBalancerArns": [
            "arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/net/staging-nlb/mno345pqr678"
        ],
        "GatewayLoadBalancerArns": [],
        "PrivateDnsName": "test.staging.internal",
        "PrivateDnsNameConfiguration": {
            "State": "pending",
            "Type": "TXT",
            "Value": "vpce:stu901vwx234",
            "Name": "test.staging.internal",
        },
        "Tags": [
            {"Key": "Name", "Value": "staging-test-service"},
            {"Key": "Environment", "Value": "staging"},
        ],
    },
}

# =============================================================================
# VPC ENDPOINT CONNECTION FIXTURES
# =============================================================================

VPC_ENDPOINT_CONNECTION_FIXTURES: dict[str, list[dict[str, Any]]] = {
    # Connections to shared-app-service
    "vpce-svc-0shared1234567890": [
        {
            "VpcEndpointId": "vpce-0sharedappservice12",
            "ServiceId": "vpce-svc-0shared1234567890",
            "VpcEndpointOwner": "123456789012",
            "VpcEndpointState": "available",
            "CreationTimestamp": datetime(2024, 1, 20, 9, 15, 0, tzinfo=timezone.utc),
            "DnsEntries": [
                {
                    "DnsName": "vpce-0sharedappservice12-pqr678.vpce-svc-0shared1234567890.eu-west-1.vpce.amazonaws.com"
                }
            ],
            "NetworkLoadBalancerArns": [
                "arn:aws:elasticloadbalancing:eu-west-1:123456789012:loadbalancer/net/production-nlb/xyz789abc123"
            ],
        },
        {
            "VpcEndpointId": "vpce-0stagappconnect1234",
            "ServiceId": "vpce-svc-0shared1234567890",
            "VpcEndpointOwner": "123456789012",
            "VpcEndpointState": "pendingAcceptance",
            "CreationTimestamp": datetime(2024, 2, 1, 15, 0, 0, tzinfo=timezone.utc),
            "DnsEntries": [],
            "NetworkLoadBalancerArns": [
                "arn:aws:elasticloadbalancing:eu-west-1:123456789012:loadbalancer/net/production-nlb/xyz789abc123"
            ],
        },
    ],
    # Connections to shared-db-service
    "vpce-svc-0shareddb12345678": [
        {
            "VpcEndpointId": "vpce-0proddbconnect12345",
            "ServiceId": "vpce-svc-0shareddb12345678",
            "VpcEndpointOwner": "123456789012",
            "VpcEndpointState": "available",
            "CreationTimestamp": datetime(2024, 1, 22, 10, 0, 0, tzinfo=timezone.utc),
            "DnsEntries": [
                {
                    "DnsName": "vpce-0proddbconnect12345-yz.vpce-svc-0shareddb12345678.eu-west-1.vpce.amazonaws.com"
                }
            ],
            "NetworkLoadBalancerArns": [
                "arn:aws:elasticloadbalancing:eu-west-1:123456789012:loadbalancer/net/production-nlb/xyz789abc123"
            ],
        },
    ],
    # Connections to production-api-service (no acceptance required)
    "vpce-svc-0prodapi123456789": [
        {
            "VpcEndpointId": "vpce-0prodapiconnect123",
            "ServiceId": "vpce-svc-0prodapi123456789",
            "VpcEndpointOwner": "123456789012",
            "VpcEndpointState": "available",
            "CreationTimestamp": datetime(2024, 1, 25, 11, 0, 0, tzinfo=timezone.utc),
            "DnsEntries": [
                {
                    "DnsName": "vpce-0prodapiconnect123-ab.vpce-svc-0prodapi123456789.eu-west-1.vpce.amazonaws.com"
                }
            ],
            "NetworkLoadBalancerArns": [
                "arn:aws:elasticloadbalancing:eu-west-1:123456789012:loadbalancer/net/production-nlb/xyz789abc123"
            ],
        },
        {
            "VpcEndpointId": "vpce-0stagapiconnect1234",
            "ServiceId": "vpce-svc-0prodapi123456789",
            "VpcEndpointOwner": "123456789012",
            "VpcEndpointState": "available",
            "CreationTimestamp": datetime(2024, 2, 1, 12, 0, 0, tzinfo=timezone.utc),
            "DnsEntries": [
                {
                    "DnsName": "vpce-0stagapiconnect1234-cd.vpce-svc-0prodapi123456789.eu-west-1.vpce.amazonaws.com"
                }
            ],
            "NetworkLoadBalancerArns": [
                "arn:aws:elasticloadbalancing:eu-west-1:123456789012:loadbalancer/net/production-nlb/xyz789abc123"
            ],
        },
        {
            "VpcEndpointId": "vpce-0devapiconnect12345",
            "ServiceId": "vpce-svc-0prodapi123456789",
            "VpcEndpointOwner": "987654321098",
            "VpcEndpointState": "rejected",
            "CreationTimestamp": datetime(2024, 1, 28, 9, 0, 0, tzinfo=timezone.utc),
            "DnsEntries": [],
            "NetworkLoadBalancerArns": [
                "arn:aws:elasticloadbalancing:eu-west-1:123456789012:loadbalancer/net/production-nlb/xyz789abc123"
            ],
            "RejectionReason": "Security policy violation",
        },
    ],
    # No connections yet for staging-test-service (Pending state)
    "vpce-svc-0stagtest12345678": [],
}

# =============================================================================
# ENI FIXTURES FOR VPC ENDPOINTS
# =============================================================================

VPC_ENDPOINT_ENI_FIXTURES: dict[str, dict[str, Any]] = {
    # Production S3 Interface Endpoint ENIs
    "eni-0prods3ep1a1234567": {
        "NetworkInterfaceId": "eni-0prods3ep1a1234567",
        "SubnetId": "subnet-0priv1a123456789",
        "VpcId": "vpc-0prod1234567890ab",
        "AvailabilityZone": "eu-west-1a",
        "Description": "VPC Endpoint Interface vpce-0prods3iface123456",
        "Groups": [
            {"GroupId": "sg-0prodapp123456789", "GroupName": "production-app-sg"}
        ],
        "PrivateIpAddress": "10.0.10.100",
        "PrivateIpAddresses": [
            {
                "Primary": True,
                "PrivateIpAddress": "10.0.10.100",
            }
        ],
        "RequesterManaged": True,
        "Status": "in-use",
        "InterfaceType": "vpc_endpoint",
        "RequesterId": "AKIAIOSFODNN7EXAMPLE",  # pragma: allowlist secret
        "VpcEndpointId": "vpce-0prods3iface123456",
    },
    "eni-0prods3ep1b1234567": {
        "NetworkInterfaceId": "eni-0prods3ep1b1234567",
        "SubnetId": "subnet-0priv1b123456789",
        "VpcId": "vpc-0prod1234567890ab",
        "AvailabilityZone": "eu-west-1b",
        "Description": "VPC Endpoint Interface vpce-0prods3iface123456",
        "Groups": [
            {"GroupId": "sg-0prodapp123456789", "GroupName": "production-app-sg"}
        ],
        "PrivateIpAddress": "10.0.11.100",
        "PrivateIpAddresses": [
            {
                "Primary": True,
                "PrivateIpAddress": "10.0.11.100",
            }
        ],
        "RequesterManaged": True,
        "Status": "in-use",
        "InterfaceType": "vpc_endpoint",
        "RequesterId": "AKIAIOSFODNN7EXAMPLE",  # pragma: allowlist secret
        "VpcEndpointId": "vpce-0prods3iface123456",
    },
    "eni-0prods3ep1c1234567": {
        "NetworkInterfaceId": "eni-0prods3ep1c1234567",
        "SubnetId": "subnet-0priv1c123456789",
        "VpcId": "vpc-0prod1234567890ab",
        "AvailabilityZone": "eu-west-1c",
        "Description": "VPC Endpoint Interface vpce-0prods3iface123456",
        "Groups": [
            {"GroupId": "sg-0prodapp123456789", "GroupName": "production-app-sg"}
        ],
        "PrivateIpAddress": "10.0.12.100",
        "PrivateIpAddresses": [
            {
                "Primary": True,
                "PrivateIpAddress": "10.0.12.100",
            }
        ],
        "RequesterManaged": True,
        "Status": "in-use",
        "InterfaceType": "vpc_endpoint",
        "RequesterId": "AKIAIOSFODNN7EXAMPLE",  # pragma: allowlist secret
        "VpcEndpointId": "vpce-0prods3iface123456",
    },
    # Production DynamoDB Interface Endpoint ENIs
    "eni-0proddynep1a123456": {
        "NetworkInterfaceId": "eni-0proddynep1a123456",
        "SubnetId": "subnet-0priv1a123456789",
        "VpcId": "vpc-0prod1234567890ab",
        "AvailabilityZone": "eu-west-1a",
        "Description": "VPC Endpoint Interface vpce-0proddynamoiface12",
        "Groups": [
            {"GroupId": "sg-0prodapp123456789", "GroupName": "production-app-sg"}
        ],
        "PrivateIpAddress": "10.0.10.101",
        "PrivateIpAddresses": [
            {
                "Primary": True,
                "PrivateIpAddress": "10.0.10.101",
            }
        ],
        "RequesterManaged": True,
        "Status": "in-use",
        "InterfaceType": "vpc_endpoint",
        "RequesterId": "AKIAIOSFODNN7EXAMPLE",  # pragma: allowlist secret
        "VpcEndpointId": "vpce-0proddynamoiface12",
    },
    "eni-0proddynep1b123456": {
        "NetworkInterfaceId": "eni-0proddynep1b123456",
        "SubnetId": "subnet-0priv1b123456789",
        "VpcId": "vpc-0prod1234567890ab",
        "AvailabilityZone": "eu-west-1b",
        "Description": "VPC Endpoint Interface vpce-0proddynamoiface12",
        "Groups": [
            {"GroupId": "sg-0prodapp123456789", "GroupName": "production-app-sg"}
        ],
        "PrivateIpAddress": "10.0.11.101",
        "PrivateIpAddresses": [
            {
                "Primary": True,
                "PrivateIpAddress": "10.0.11.101",
            }
        ],
        "RequesterManaged": True,
        "Status": "in-use",
        "InterfaceType": "vpc_endpoint",
        "RequesterId": "AKIAIOSFODNN7EXAMPLE",  # pragma: allowlist secret
        "VpcEndpointId": "vpce-0proddynamoiface12",
    },
    # Production Lambda Interface Endpoint ENIs
    "eni-0prodlambep1a12345": {
        "NetworkInterfaceId": "eni-0prodlambep1a12345",
        "SubnetId": "subnet-0priv1a123456789",
        "VpcId": "vpc-0prod1234567890ab",
        "AvailabilityZone": "eu-west-1a",
        "Description": "VPC Endpoint Interface vpce-0prodlambdaiface12",
        "Groups": [
            {"GroupId": "sg-0prodapp123456789", "GroupName": "production-app-sg"}
        ],
        "PrivateIpAddress": "10.0.10.102",
        "PrivateIpAddresses": [
            {
                "Primary": True,
                "PrivateIpAddress": "10.0.10.102",
            }
        ],
        "RequesterManaged": True,
        "Status": "in-use",
        "InterfaceType": "vpc_endpoint",
        "RequesterId": "AKIAIOSFODNN7EXAMPLE",  # pragma: allowlist secret
        "VpcEndpointId": "vpce-0prodlambdaiface12",
    },
    "eni-0prodlambep1b12345": {
        "NetworkInterfaceId": "eni-0prodlambep1b12345",
        "SubnetId": "subnet-0priv1b123456789",
        "VpcId": "vpc-0prod1234567890ab",
        "AvailabilityZone": "eu-west-1b",
        "Description": "VPC Endpoint Interface vpce-0prodlambdaiface12",
        "Groups": [
            {"GroupId": "sg-0prodapp123456789", "GroupName": "production-app-sg"}
        ],
        "PrivateIpAddress": "10.0.11.102",
        "PrivateIpAddresses": [
            {
                "Primary": True,
                "PrivateIpAddress": "10.0.11.102",
            }
        ],
        "RequesterManaged": True,
        "Status": "in-use",
        "InterfaceType": "vpc_endpoint",
        "RequesterId": "AKIAIOSFODNN7EXAMPLE",  # pragma: allowlist secret
        "VpcEndpointId": "vpce-0prodlambdaiface12",
    },
    "eni-0prodlambep1c12345": {
        "NetworkInterfaceId": "eni-0prodlambep1c12345",
        "SubnetId": "subnet-0priv1c123456789",
        "VpcId": "vpc-0prod1234567890ab",
        "AvailabilityZone": "eu-west-1c",
        "Description": "VPC Endpoint Interface vpce-0prodlambdaiface12",
        "Groups": [
            {"GroupId": "sg-0prodapp123456789", "GroupName": "production-app-sg"}
        ],
        "PrivateIpAddress": "10.0.12.102",
        "PrivateIpAddresses": [
            {
                "Primary": True,
                "PrivateIpAddress": "10.0.12.102",
            }
        ],
        "RequesterManaged": True,
        "Status": "in-use",
        "InterfaceType": "vpc_endpoint",
        "RequesterId": "AKIAIOSFODNN7EXAMPLE",  # pragma: allowlist secret
        "VpcEndpointId": "vpce-0prodlambdaiface12",
    },
    # Production EC2 API Interface Endpoint ENIs
    "eni-0prodec2ep1a123456": {
        "NetworkInterfaceId": "eni-0prodec2ep1a123456",
        "SubnetId": "subnet-0priv1a123456789",
        "VpcId": "vpc-0prod1234567890ab",
        "AvailabilityZone": "eu-west-1a",
        "Description": "VPC Endpoint Interface vpce-0prodec2apiface123",
        "Groups": [
            {"GroupId": "sg-0prodapp123456789", "GroupName": "production-app-sg"}
        ],
        "PrivateIpAddress": "10.0.10.103",
        "PrivateIpAddresses": [
            {
                "Primary": True,
                "PrivateIpAddress": "10.0.10.103",
            }
        ],
        "RequesterManaged": True,
        "Status": "in-use",
        "InterfaceType": "vpc_endpoint",
        "RequesterId": "AKIAIOSFODNN7EXAMPLE",  # pragma: allowlist secret
        "VpcEndpointId": "vpce-0prodec2apiface123",
    },
    "eni-0prodec2ep1b123456": {
        "NetworkInterfaceId": "eni-0prodec2ep1b123456",
        "SubnetId": "subnet-0priv1b123456789",
        "VpcId": "vpc-0prod1234567890ab",
        "AvailabilityZone": "eu-west-1b",
        "Description": "VPC Endpoint Interface vpce-0prodec2apiface123",
        "Groups": [
            {"GroupId": "sg-0prodapp123456789", "GroupName": "production-app-sg"}
        ],
        "PrivateIpAddress": "10.0.11.103",
        "PrivateIpAddresses": [
            {
                "Primary": True,
                "PrivateIpAddress": "10.0.11.103",
            }
        ],
        "RequesterManaged": True,
        "Status": "in-use",
        "InterfaceType": "vpc_endpoint",
        "RequesterId": "AKIAIOSFODNN7EXAMPLE",  # pragma: allowlist secret
        "VpcEndpointId": "vpce-0prodec2apiface123",
    },
    # Shared Services - Custom App Service ENIs
    "eni-0sharedapp1a123456": {
        "NetworkInterfaceId": "eni-0sharedapp1a123456",
        "SubnetId": "subnet-0priv1a123456789",
        "VpcId": "vpc-0prod1234567890ab",
        "AvailabilityZone": "eu-west-1a",
        "Description": "VPC Endpoint Interface vpce-0sharedappservice12",
        "Groups": [
            {"GroupId": "sg-0prodapp123456789", "GroupName": "production-app-sg"}
        ],
        "PrivateIpAddress": "10.0.10.150",
        "PrivateIpAddresses": [
            {
                "Primary": True,
                "PrivateIpAddress": "10.0.10.150",
            }
        ],
        "RequesterManaged": True,
        "Status": "in-use",
        "InterfaceType": "vpc_endpoint",
        "RequesterId": "AKIAIOSFODNN7EXAMPLE",  # pragma: allowlist secret
        "VpcEndpointId": "vpce-0sharedappservice12",
    },
    "eni-0sharedapp1b123456": {
        "NetworkInterfaceId": "eni-0sharedapp1b123456",
        "SubnetId": "subnet-0priv1b123456789",
        "VpcId": "vpc-0prod1234567890ab",
        "AvailabilityZone": "eu-west-1b",
        "Description": "VPC Endpoint Interface vpce-0sharedappservice12",
        "Groups": [
            {"GroupId": "sg-0prodapp123456789", "GroupName": "production-app-sg"}
        ],
        "PrivateIpAddress": "10.0.11.150",
        "PrivateIpAddresses": [
            {
                "Primary": True,
                "PrivateIpAddress": "10.0.11.150",
            }
        ],
        "RequesterManaged": True,
        "Status": "in-use",
        "InterfaceType": "vpc_endpoint",
        "RequesterId": "AKIAIOSFODNN7EXAMPLE",  # pragma: allowlist secret
        "VpcEndpointId": "vpce-0sharedappservice12",
    },
    # Staging S3 Interface Endpoint ENI (pending state)
    "eni-0stags3ep1a1234567": {
        "NetworkInterfaceId": "eni-0stags3ep1a1234567",
        "SubnetId": "subnet-0stgpriv1a1234567",
        "VpcId": "vpc-0stag1234567890ab",
        "AvailabilityZone": "us-east-1a",
        "Description": "VPC Endpoint Interface vpce-0stags3iface123456",
        "Groups": [{"GroupId": "sg-0stagapp123456789a", "GroupName": "staging-app-sg"}],
        "PrivateIpAddress": "10.1.10.100",
        "PrivateIpAddresses": [
            {
                "Primary": True,
                "PrivateIpAddress": "10.1.10.100",
            }
        ],
        "RequesterManaged": True,
        "Status": "in-use",
        "InterfaceType": "vpc_endpoint",
        "RequesterId": "AKIAIOSFODNN7EXAMPLE",  # pragma: allowlist secret
        "VpcEndpointId": "vpce-0stags3iface123456",
    },
    # Development Lambda Interface Endpoint ENI (deleting state)
    "eni-0devlambep2a123456": {
        "NetworkInterfaceId": "eni-0devlambep2a123456",
        "SubnetId": "subnet-0devpriv2a1234567",
        "VpcId": "vpc-0dev01234567890ab",
        "AvailabilityZone": "ap-southeast-2a",
        "Description": "VPC Endpoint Interface vpce-0devlambdaiface123",
        "Groups": [
            {"GroupId": "sg-0devall12345678901", "GroupName": "development-all-sg"}
        ],
        "PrivateIpAddress": "10.2.10.100",
        "PrivateIpAddresses": [
            {
                "Primary": True,
                "PrivateIpAddress": "10.2.10.100",
            }
        ],
        "RequesterManaged": True,
        "Status": "available",
        "InterfaceType": "vpc_endpoint",
        "RequesterId": "AKIAIOSFODNN7EXAMPLE",  # pragma: allowlist secret
        "VpcEndpointId": "vpce-0devlambdaiface123",
    },
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_vpc_endpoint_by_id(endpoint_id: str) -> dict[str, Any] | None:
    """Get VPC endpoint by ID (interface or gateway)."""
    endpoint = INTERFACE_VPC_ENDPOINT_FIXTURES.get(endpoint_id)
    if endpoint:
        return endpoint
    return GATEWAY_VPC_ENDPOINT_FIXTURES.get(endpoint_id)


def get_interface_endpoints_by_vpc(vpc_id: str) -> list[dict[str, Any]]:
    """Get all interface VPC endpoints in a VPC."""
    return [
        ep for ep in INTERFACE_VPC_ENDPOINT_FIXTURES.values() if ep["VpcId"] == vpc_id
    ]


def get_gateway_endpoints_by_vpc(vpc_id: str) -> list[dict[str, Any]]:
    """Get all gateway VPC endpoints in a VPC."""
    return [
        ep for ep in GATEWAY_VPC_ENDPOINT_FIXTURES.values() if ep["VpcId"] == vpc_id
    ]


def get_all_endpoints_by_vpc(vpc_id: str) -> list[dict[str, Any]]:
    """Get all VPC endpoints (interface and gateway) in a VPC."""
    return get_interface_endpoints_by_vpc(vpc_id) + get_gateway_endpoints_by_vpc(vpc_id)


def get_endpoint_service_by_id(service_id: str) -> dict[str, Any] | None:
    """Get VPC endpoint service by ID."""
    return VPC_ENDPOINT_SERVICE_FIXTURES.get(service_id)


def get_endpoint_connections(service_id: str) -> list[dict[str, Any]]:
    """Get all endpoint connections for a service."""
    return VPC_ENDPOINT_CONNECTION_FIXTURES.get(service_id, [])


def get_eni_by_id(eni_id: str) -> dict[str, Any] | None:
    """Get ENI fixture by ID."""
    return VPC_ENDPOINT_ENI_FIXTURES.get(eni_id)


def get_enis_by_endpoint(endpoint_id: str) -> list[dict[str, Any]]:
    """Get all ENIs for a VPC endpoint."""
    return [
        eni
        for eni in VPC_ENDPOINT_ENI_FIXTURES.values()
        if eni.get("VpcEndpointId") == endpoint_id
    ]


def get_endpoints_by_service(service_name: str) -> list[dict[str, Any]]:
    """Get all VPC endpoints consuming a specific service."""
    return [
        ep
        for ep in INTERFACE_VPC_ENDPOINT_FIXTURES.values()
        if ep["ServiceName"] == service_name
    ]


def get_endpoints_by_state(state: str) -> list[dict[str, Any]]:
    """Get all VPC endpoints in a specific state."""
    interface_eps = [
        ep for ep in INTERFACE_VPC_ENDPOINT_FIXTURES.values() if ep["State"] == state
    ]
    gateway_eps = [
        ep for ep in GATEWAY_VPC_ENDPOINT_FIXTURES.values() if ep["State"] == state
    ]
    return interface_eps + gateway_eps


def get_endpoint_services_by_state(state: str) -> list[dict[str, Any]]:
    """Get all endpoint services in a specific state."""
    return [
        svc
        for svc in VPC_ENDPOINT_SERVICE_FIXTURES.values()
        if svc["ServiceState"] == state
    ]


def get_connections_by_state(state: str) -> list[dict[str, Any]]:
    """Get all endpoint connections in a specific state."""
    connections = []
    for conn_list in VPC_ENDPOINT_CONNECTION_FIXTURES.values():
        for conn in conn_list:
            if conn.get("VpcEndpointState") == state:
                connections.append(conn)
    return connections


def get_endpoint_detail(endpoint_id: str) -> dict[str, Any] | None:
    """Get comprehensive endpoint detail with ENIs and connections."""
    endpoint = get_vpc_endpoint_by_id(endpoint_id)
    if not endpoint:
        return None

    # Get associated ENIs
    enis = get_enis_by_endpoint(endpoint_id)

    # If this is a consumer endpoint, check if it's connected to any services
    service_connection = None
    for service_id, connections in VPC_ENDPOINT_CONNECTION_FIXTURES.items():
        for conn in connections:
            if conn["VpcEndpointId"] == endpoint_id:
                service_connection = {
                    "service_id": service_id,
                    "connection": conn,
                    "service": VPC_ENDPOINT_SERVICE_FIXTURES.get(service_id),
                }
                break
        if service_connection:
            break

    return {
        "endpoint": endpoint,
        "enis": enis,
        "service_connection": service_connection,
    }


def get_endpoint_service_detail(service_id: str) -> dict[str, Any] | None:
    """Get comprehensive endpoint service detail with connections."""
    service = VPC_ENDPOINT_SERVICE_FIXTURES.get(service_id)
    if not service:
        return None

    # Get all connections to this service
    connections = VPC_ENDPOINT_CONNECTION_FIXTURES.get(service_id, [])

    return {
        "service": service,
        "connections": connections,
        "total_connections": len(connections),
        "available_connections": len(
            [c for c in connections if c.get("VpcEndpointState") == "available"]
        ),
        "pending_connections": len(
            [c for c in connections if c.get("VpcEndpointState") == "pendingAcceptance"]
        ),
        "rejected_connections": len(
            [c for c in connections if c.get("VpcEndpointState") == "rejected"]
        ),
    }
