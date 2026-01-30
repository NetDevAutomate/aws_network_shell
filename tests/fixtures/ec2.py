"""Realistic EC2 and ENI mock data fixtures.

Multi-tier application architecture:
- Production web tier (ALB targets)
- Production application tier
- Production database tier (RDS instances)
- Shared services bastion hosts
- Staging application servers

Each instance includes:
- Realistic ENIs with private/public IPs
- Security group associations
- Proper subnet placement
- Instance metadata
"""

from typing import Any

# =============================================================================
# EC2 INSTANCE FIXTURES
# =============================================================================

EC2_INSTANCE_FIXTURES: dict[str, dict[str, Any]] = {
    # Production Web Server 1 - eu-west-1a
    "i-0prodweb1a123456789": {
        "InstanceId": "i-0prodweb1a123456789",
        "InstanceType": "t3.medium",
        "State": {"Code": 16, "Name": "running"},
        "StateReason": None,
        "LaunchTime": "2024-01-20T08:00:00+00:00",
        "ImageId": "ami-0prodweb123456789",
        "KeyName": "production-keypair",
        "Placement": {
            "AvailabilityZone": "eu-west-1a",
            "GroupName": "",
            "Tenancy": "default",
        },
        "VpcId": "vpc-0prod1234567890ab",
        "SubnetId": "subnet-0priv1a123456789",
        "PrivateIpAddress": "10.0.10.10",
        "PublicIpAddress": None,
        "PrivateDnsName": "ip-10-0-10-10.eu-west-1.compute.internal",
        "PublicDnsName": "",
        "Architecture": "x86_64",
        "Platform": "linux",
        "RootDeviceType": "ebs",
        "RootDeviceName": "/dev/xvda",
        "NetworkInterfaces": [
            {
                "NetworkInterfaceId": "eni-0prodweb1a1234567",
                "SubnetId": "subnet-0priv1a123456789",
                "VpcId": "vpc-0prod1234567890ab",
                "Description": "Primary network interface",
                "PrivateIpAddress": "10.0.10.10",
                "PrivateIpAddresses": [
                    {"Primary": True, "PrivateIpAddress": "10.0.10.10"}
                ],
                "Attachment": {
                    "AttachmentId": "eni-attach-0prodweb1a12",
                    "DeviceIndex": 0,
                    "Status": "attached",
                    "AttachTime": "2024-01-20T08:00:00+00:00",
                    "DeleteOnTermination": True,
                },
                "Groups": [
                    {
                        "GroupId": "sg-0prodapp123456789",
                        "GroupName": "production-app-sg",
                    }
                ],
                "SourceDestCheck": True,
                "Status": "in-use",
            }
        ],
        "SecurityGroups": [
            {"GroupId": "sg-0prodapp123456789", "GroupName": "production-app-sg"}
        ],
        "IamInstanceProfile": {
            "Arn": "arn:aws:iam::123456789012:instance-profile/production-web-profile",
            "Id": "AKIAIOSFODNN7EXAMPLE",  # pragma: allowlist secret
        },
        "Tags": [
            {"Key": "Name", "Value": "production-web-1a"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "Tier", "Value": "web"},
            {"Key": "AZ", "Value": "eu-west-1a"},
        ],
        "Monitoring": {"State": "enabled"},
        "EbsOptimized": True,
        "CpuOptions": {"CoreCount": 1, "ThreadsPerCore": 2},
        "MetadataOptions": {
            "State": "applied",
            "HttpTokens": "required",
            "HttpPutResponseHopLimit": 1,
            "HttpEndpoint": "enabled",
        },
    },
    # Production Web Server 2 - eu-west-1b
    "i-0prodweb1b123456789": {
        "InstanceId": "i-0prodweb1b123456789",
        "InstanceType": "t3.medium",
        "State": {"Code": 16, "Name": "running"},
        "StateReason": None,
        "LaunchTime": "2024-01-20T08:05:00+00:00",
        "ImageId": "ami-0prodweb123456789",
        "KeyName": "production-keypair",
        "Placement": {
            "AvailabilityZone": "eu-west-1b",
            "GroupName": "",
            "Tenancy": "default",
        },
        "VpcId": "vpc-0prod1234567890ab",
        "SubnetId": "subnet-0priv1b123456789",
        "PrivateIpAddress": "10.0.11.10",
        "PublicIpAddress": None,
        "PrivateDnsName": "ip-10-0-11-10.eu-west-1.compute.internal",
        "PublicDnsName": "",
        "Architecture": "x86_64",
        "Platform": "linux",
        "RootDeviceType": "ebs",
        "RootDeviceName": "/dev/xvda",
        "NetworkInterfaces": [
            {
                "NetworkInterfaceId": "eni-0prodweb1b1234567",
                "SubnetId": "subnet-0priv1b123456789",
                "VpcId": "vpc-0prod1234567890ab",
                "Description": "Primary network interface",
                "PrivateIpAddress": "10.0.11.10",
                "PrivateIpAddresses": [
                    {"Primary": True, "PrivateIpAddress": "10.0.11.10"}
                ],
                "Attachment": {
                    "AttachmentId": "eni-attach-0prodweb1b12",
                    "DeviceIndex": 0,
                    "Status": "attached",
                    "AttachTime": "2024-01-20T08:05:00+00:00",
                    "DeleteOnTermination": True,
                },
                "Groups": [
                    {
                        "GroupId": "sg-0prodapp123456789",
                        "GroupName": "production-app-sg",
                    }
                ],
                "SourceDestCheck": True,
                "Status": "in-use",
            }
        ],
        "SecurityGroups": [
            {"GroupId": "sg-0prodapp123456789", "GroupName": "production-app-sg"}
        ],
        "IamInstanceProfile": {
            "Arn": "arn:aws:iam::123456789012:instance-profile/production-web-profile",
            "Id": "AKIAIOSFODNN7EXAMPLE",  # pragma: allowlist secret
        },
        "Tags": [
            {"Key": "Name", "Value": "production-web-1b"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "Tier", "Value": "web"},
            {"Key": "AZ", "Value": "eu-west-1b"},
        ],
        "Monitoring": {"State": "enabled"},
        "EbsOptimized": True,
        "CpuOptions": {"CoreCount": 1, "ThreadsPerCore": 2},
        "MetadataOptions": {
            "State": "applied",
            "HttpTokens": "required",
            "HttpPutResponseHopLimit": 1,
            "HttpEndpoint": "enabled",
        },
    },
    # Shared Services Bastion Host - eu-west-1a
    "i-0bastion1a123456789": {
        "InstanceId": "i-0bastion1a123456789",
        "InstanceType": "t3.micro",
        "State": {"Code": 16, "Name": "running"},
        "StateReason": None,
        "LaunchTime": "2024-01-15T10:00:00+00:00",
        "ImageId": "ami-0bastion123456789",
        "KeyName": "shared-keypair",
        "Placement": {
            "AvailabilityZone": "eu-west-1a",
            "GroupName": "",
            "Tenancy": "default",
        },
        "VpcId": "vpc-0shared123456789a",
        "SubnetId": "subnet-0sharedpub1a1234",
        "PrivateIpAddress": "10.100.1.10",
        "PublicIpAddress": "203.0.113.50",
        "PrivateDnsName": "ip-10-100-1-10.eu-west-1.compute.internal",
        "PublicDnsName": "ec2-203-0-113-50.eu-west-1.compute.amazonaws.com",
        "Architecture": "x86_64",
        "Platform": "linux",
        "RootDeviceType": "ebs",
        "RootDeviceName": "/dev/xvda",
        "NetworkInterfaces": [
            {
                "NetworkInterfaceId": "eni-0bastion1a1234567",
                "SubnetId": "subnet-0sharedpub1a1234",
                "VpcId": "vpc-0shared123456789a",
                "Description": "Primary network interface",
                "PrivateIpAddress": "10.100.1.10",
                "PrivateIpAddresses": [
                    {
                        "Primary": True,
                        "PrivateIpAddress": "10.100.1.10",
                        "Association": {
                            "PublicIp": "203.0.113.50",
                            "PublicDnsName": "ec2-203-0-113-50.eu-west-1.compute.amazonaws.com",
                            "IpOwnerId": "amazon",
                        },
                    }
                ],
                "Attachment": {
                    "AttachmentId": "eni-attach-0bastion1a12",
                    "DeviceIndex": 0,
                    "Status": "attached",
                    "AttachTime": "2024-01-15T10:00:00+00:00",
                    "DeleteOnTermination": True,
                },
                "Groups": [
                    {
                        "GroupId": "sg-0sharedbastion1234",
                        "GroupName": "shared-bastion-sg",
                    }
                ],
                "SourceDestCheck": True,
                "Status": "in-use",
            }
        ],
        "SecurityGroups": [
            {"GroupId": "sg-0sharedbastion1234", "GroupName": "shared-bastion-sg"}
        ],
        "IamInstanceProfile": {
            "Arn": "arn:aws:iam::123456789012:instance-profile/bastion-profile",
            "Id": "AKIAIOSFODNN7EXAMPLE",  # pragma: allowlist secret
        },
        "Tags": [
            {"Key": "Name", "Value": "shared-bastion-1a"},
            {"Key": "Environment", "Value": "shared"},
            {"Key": "Purpose", "Value": "bastion"},
        ],
        "Monitoring": {"State": "enabled"},
        "EbsOptimized": False,
        "CpuOptions": {"CoreCount": 1, "ThreadsPerCore": 2},
        "MetadataOptions": {
            "State": "applied",
            "HttpTokens": "required",
            "HttpPutResponseHopLimit": 1,
            "HttpEndpoint": "enabled",
        },
    },
    # Staging Application Server - us-east-1a
    "i-0stagapp1a123456789": {
        "InstanceId": "i-0stagapp1a123456789",
        "InstanceType": "t3.small",
        "State": {"Code": 16, "Name": "running"},
        "StateReason": None,
        "LaunchTime": "2024-02-02T12:00:00+00:00",
        "ImageId": "ami-0stagapp123456789",
        "KeyName": "staging-keypair",
        "Placement": {
            "AvailabilityZone": "us-east-1a",
            "GroupName": "",
            "Tenancy": "default",
        },
        "VpcId": "vpc-0stag1234567890ab",
        "SubnetId": "subnet-0stgpriv1a1234567",
        "PrivateIpAddress": "10.1.10.10",
        "PublicIpAddress": None,
        "PrivateDnsName": "ip-10-1-10-10.us-east-1.compute.internal",
        "PublicDnsName": "",
        "Architecture": "x86_64",
        "Platform": "linux",
        "RootDeviceType": "ebs",
        "RootDeviceName": "/dev/xvda",
        "NetworkInterfaces": [
            {
                "NetworkInterfaceId": "eni-0stagapp1a1234567",
                "SubnetId": "subnet-0stgpriv1a1234567",
                "VpcId": "vpc-0stag1234567890ab",
                "Description": "Primary network interface",
                "PrivateIpAddress": "10.1.10.10",
                "PrivateIpAddresses": [
                    {"Primary": True, "PrivateIpAddress": "10.1.10.10"}
                ],
                "Attachment": {
                    "AttachmentId": "eni-attach-0stagapp1a12",
                    "DeviceIndex": 0,
                    "Status": "attached",
                    "AttachTime": "2024-02-02T12:00:00+00:00",
                    "DeleteOnTermination": True,
                },
                "Groups": [
                    {
                        "GroupId": "sg-0stagapp123456789a",
                        "GroupName": "staging-app-sg",
                    }
                ],
                "SourceDestCheck": True,
                "Status": "in-use",
            }
        ],
        "SecurityGroups": [
            {"GroupId": "sg-0stagapp123456789a", "GroupName": "staging-app-sg"}
        ],
        "IamInstanceProfile": {
            "Arn": "arn:aws:iam::123456789012:instance-profile/staging-app-profile",
            "Id": "AKIAIOSFODNN7EXAMPLE",  # pragma: allowlist secret
        },
        "Tags": [
            {"Key": "Name", "Value": "staging-app-1a"},
            {"Key": "Environment", "Value": "staging"},
            {"Key": "Tier", "Value": "application"},
        ],
        "Monitoring": {"State": "disabled"},
        "EbsOptimized": False,
        "CpuOptions": {"CoreCount": 1, "ThreadsPerCore": 2},
        "MetadataOptions": {
            "State": "applied",
            "HttpTokens": "optional",
            "HttpPutResponseHopLimit": 1,
            "HttpEndpoint": "enabled",
        },
    },
    # Development Test Server - ap-southeast-2a
    "i-0devtest2a123456789": {
        "InstanceId": "i-0devtest2a123456789",
        "InstanceType": "t3.micro",
        "State": {"Code": 80, "Name": "stopped"},
        "StateReason": {
            "Code": "Client.UserInitiatedShutdown",
            "Message": "Client.UserInitiatedShutdown: User initiated shutdown",
        },
        "LaunchTime": "2024-02-10T08:00:00+00:00",
        "ImageId": "ami-0devtest123456789",
        "KeyName": "development-keypair",
        "Placement": {
            "AvailabilityZone": "ap-southeast-2a",
            "GroupName": "",
            "Tenancy": "default",
        },
        "VpcId": "vpc-0dev01234567890ab",
        "SubnetId": "subnet-0devpriv2a1234567",
        "PrivateIpAddress": "10.2.10.10",
        "PublicIpAddress": None,
        "PrivateDnsName": "ip-10-2-10-10.ap-southeast-2.compute.internal",
        "PublicDnsName": "",
        "Architecture": "x86_64",
        "Platform": "linux",
        "RootDeviceType": "ebs",
        "RootDeviceName": "/dev/xvda",
        "NetworkInterfaces": [
            {
                "NetworkInterfaceId": "eni-0devtest2a1234567",
                "SubnetId": "subnet-0devpriv2a1234567",
                "VpcId": "vpc-0dev01234567890ab",
                "Description": "Primary network interface",
                "PrivateIpAddress": "10.2.10.10",
                "PrivateIpAddresses": [
                    {"Primary": True, "PrivateIpAddress": "10.2.10.10"}
                ],
                "Attachment": {
                    "AttachmentId": "eni-attach-0devtest2a12",
                    "DeviceIndex": 0,
                    "Status": "attached",
                    "AttachTime": "2024-02-10T08:00:00+00:00",
                    "DeleteOnTermination": True,
                },
                "Groups": [
                    {
                        "GroupId": "sg-0devall12345678901",
                        "GroupName": "development-all-sg",
                    }
                ],
                "SourceDestCheck": True,
                "Status": "in-use",
            }
        ],
        "SecurityGroups": [
            {"GroupId": "sg-0devall12345678901", "GroupName": "development-all-sg"}
        ],
        "Tags": [
            {"Key": "Name", "Value": "development-test-2a"},
            {"Key": "Environment", "Value": "development"},
        ],
        "Monitoring": {"State": "disabled"},
        "EbsOptimized": False,
        "CpuOptions": {"CoreCount": 1, "ThreadsPerCore": 1},
        "MetadataOptions": {
            "State": "applied",
            "HttpTokens": "optional",
            "HttpPutResponseHopLimit": 1,
            "HttpEndpoint": "enabled",
        },
    },
}

# =============================================================================
# ENI FIXTURES
# =============================================================================

ENI_FIXTURES: dict[str, dict[str, Any]] = {
    # Production Web Server 1a ENI (from EC2 instance above)
    "eni-0prodweb1a1234567": {
        "NetworkInterfaceId": "eni-0prodweb1a1234567",
        "SubnetId": "subnet-0priv1a123456789",
        "VpcId": "vpc-0prod1234567890ab",
        "AvailabilityZone": "eu-west-1a",
        "Description": "Primary network interface",
        "OwnerId": "123456789012",
        "PrivateIpAddress": "10.0.10.10",
        "PrivateDnsName": "ip-10-0-10-10.eu-west-1.compute.internal",
        "PrivateIpAddresses": [{"Primary": True, "PrivateIpAddress": "10.0.10.10"}],
        "MacAddress": "02:11:22:33:44:aa",
        "Status": "in-use",
        "SourceDestCheck": True,
        "InterfaceType": "interface",
        "Groups": [
            {"GroupId": "sg-0prodapp123456789", "GroupName": "production-app-sg"}
        ],
        "Attachment": {
            "AttachmentId": "eni-attach-0prodweb1a12",
            "DeviceIndex": 0,
            "InstanceId": "i-0prodweb1a123456789",
            "InstanceOwnerId": "123456789012",
            "Status": "attached",
            "AttachTime": "2024-01-20T08:00:00+00:00",
            "DeleteOnTermination": True,
        },
        "TagSet": [
            {"Key": "Name", "Value": "production-web-1a-eni"},
            {"Key": "Environment", "Value": "production"},
        ],
    },
    # Production ALB ENI 1a
    "eni-0alb1a12345678901": {
        "NetworkInterfaceId": "eni-0alb1a12345678901",
        "SubnetId": "subnet-0pub1a1234567890",
        "VpcId": "vpc-0prod1234567890ab",
        "AvailabilityZone": "eu-west-1a",
        "Description": "ELB app/production-alb/abc123def456",
        "OwnerId": "123456789012",
        "PrivateIpAddress": "10.0.1.100",
        "PrivateDnsName": "ip-10-0-1-100.eu-west-1.compute.internal",
        "PrivateIpAddresses": [
            {
                "Primary": True,
                "PrivateIpAddress": "10.0.1.100",
                "Association": {
                    "PublicIp": "52.31.100.50",
                    "PublicDnsName": "ec2-52-31-100-50.eu-west-1.compute.amazonaws.com",
                    "IpOwnerId": "amazon",
                },
            }
        ],
        "MacAddress": "02:aa:bb:cc:dd:11",
        "Status": "in-use",
        "SourceDestCheck": True,
        "InterfaceType": "network_load_balancer",
        "Groups": [
            {"GroupId": "sg-0prodweb123456789", "GroupName": "production-web-alb-sg"}
        ],
        "Attachment": {
            "AttachmentId": "ela-attach-0alb1a123",
            "DeviceIndex": 1,
            "InstanceOwnerId": "amazon-elb",
            "Status": "attached",
        },
        "TagSet": [
            {"Key": "Name", "Value": "production-alb-1a-eni"},
            {"Key": "Environment", "Value": "production"},
        ],
        "RequesterManaged": True,
        "RequesterId": "amazon-elb",
    },
    # Production ALB ENI 1b
    "eni-0alb1b12345678901": {
        "NetworkInterfaceId": "eni-0alb1b12345678901",
        "SubnetId": "subnet-0pub1b1234567890",
        "VpcId": "vpc-0prod1234567890ab",
        "AvailabilityZone": "eu-west-1b",
        "Description": "ELB app/production-alb/abc123def456",
        "OwnerId": "123456789012",
        "PrivateIpAddress": "10.0.2.100",
        "PrivateDnsName": "ip-10-0-2-100.eu-west-1.compute.internal",
        "PrivateIpAddresses": [
            {
                "Primary": True,
                "PrivateIpAddress": "10.0.2.100",
                "Association": {
                    "PublicIp": "52.31.100.51",
                    "PublicDnsName": "ec2-52-31-100-51.eu-west-1.compute.amazonaws.com",
                    "IpOwnerId": "amazon",
                },
            }
        ],
        "MacAddress": "02:aa:bb:cc:dd:22",
        "Status": "in-use",
        "SourceDestCheck": True,
        "InterfaceType": "network_load_balancer",
        "Groups": [
            {"GroupId": "sg-0prodweb123456789", "GroupName": "production-web-alb-sg"}
        ],
        "Attachment": {
            "AttachmentId": "ela-attach-0alb1b123",
            "DeviceIndex": 1,
            "InstanceOwnerId": "amazon-elb",
            "Status": "attached",
        },
        "TagSet": [
            {"Key": "Name", "Value": "production-alb-1b-eni"},
            {"Key": "Environment", "Value": "production"},
        ],
        "RequesterManaged": True,
        "RequesterId": "amazon-elb",
    },
    # Bastion Host ENI
    "eni-0bastion1a1234567": {
        "NetworkInterfaceId": "eni-0bastion1a1234567",
        "SubnetId": "subnet-0sharedpub1a1234",
        "VpcId": "vpc-0shared123456789a",
        "AvailabilityZone": "eu-west-1a",
        "Description": "Primary network interface",
        "OwnerId": "123456789012",
        "PrivateIpAddress": "10.100.1.10",
        "PrivateDnsName": "ip-10-100-1-10.eu-west-1.compute.internal",
        "PrivateIpAddresses": [
            {
                "Primary": True,
                "PrivateIpAddress": "10.100.1.10",
                "Association": {
                    "PublicIp": "203.0.113.50",
                    "PublicDnsName": "ec2-203-0-113-50.eu-west-1.compute.amazonaws.com",
                    "IpOwnerId": "amazon",
                },
            }
        ],
        "MacAddress": "02:55:66:77:88:99",
        "Status": "in-use",
        "SourceDestCheck": True,
        "InterfaceType": "interface",
        "Groups": [
            {"GroupId": "sg-0sharedbastion1234", "GroupName": "shared-bastion-sg"}
        ],
        "Attachment": {
            "AttachmentId": "eni-attach-0bastion1a12",
            "DeviceIndex": 0,
            "InstanceId": "i-0bastion1a123456789",
            "InstanceOwnerId": "123456789012",
            "Status": "attached",
            "AttachTime": "2024-01-15T10:00:00+00:00",
            "DeleteOnTermination": True,
        },
        "TagSet": [
            {"Key": "Name", "Value": "shared-bastion-1a-eni"},
            {"Key": "Environment", "Value": "shared"},
        ],
    },
    # Lambda ENI (for VPC Lambda function)
    "eni-0lambda123456789ab": {
        "NetworkInterfaceId": "eni-0lambda123456789ab",
        "SubnetId": "subnet-0priv1a123456789",
        "VpcId": "vpc-0prod1234567890ab",
        "AvailabilityZone": "eu-west-1a",
        "Description": "AWS Lambda VPC ENI-production-function-abc123",
        "OwnerId": "123456789012",
        "PrivateIpAddress": "10.0.10.50",
        "PrivateDnsName": "ip-10-0-10-50.eu-west-1.compute.internal",
        "PrivateIpAddresses": [{"Primary": True, "PrivateIpAddress": "10.0.10.50"}],
        "MacAddress": "02:99:88:77:66:55",
        "Status": "in-use",
        "SourceDestCheck": True,
        "InterfaceType": "lambda",
        "Groups": [
            {"GroupId": "sg-0prodapp123456789", "GroupName": "production-app-sg"}
        ],
        "Attachment": {
            "AttachmentId": "ela-attach-0lambda123",
            "DeviceIndex": 1,
            "InstanceOwnerId": "amazon-aws",
            "Status": "attached",
        },
        "TagSet": [
            {"Key": "Name", "Value": "production-lambda-eni"},
            {"Key": "aws:lambda:function-name", "Value": "production-function"},
        ],
        "RequesterManaged": True,
        "RequesterId": "amazon-aws",
    },
    # RDS ENI (for RDS instance in database subnet)
    "eni-0rds1a12345678901": {
        "NetworkInterfaceId": "eni-0rds1a12345678901",
        "SubnetId": "subnet-0db1a12345678901",
        "VpcId": "vpc-0prod1234567890ab",
        "AvailabilityZone": "eu-west-1a",
        "Description": "RDSNetworkInterface",
        "OwnerId": "123456789012",
        "PrivateIpAddress": "10.0.20.10",
        "PrivateDnsName": "ip-10-0-20-10.eu-west-1.compute.internal",
        "PrivateIpAddresses": [{"Primary": True, "PrivateIpAddress": "10.0.20.10"}],
        "MacAddress": "02:44:55:66:77:88",
        "Status": "in-use",
        "SourceDestCheck": True,
        "InterfaceType": "interface",
        "Groups": [
            {"GroupId": "sg-0proddb1234567890", "GroupName": "production-db-sg"}
        ],
        "Attachment": {
            "AttachmentId": "eni-attach-0rds1a1234",
            "DeviceIndex": 1,
            "InstanceOwnerId": "amazon-rds",
            "Status": "attached",
        },
        "TagSet": [
            {"Key": "Name", "Value": "production-rds-1a-eni"},
            {"Key": "Environment", "Value": "production"},
        ],
        "RequesterManaged": True,
        "RequesterId": "amazon-rds",
    },
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_instance_by_id(instance_id: str) -> dict[str, Any] | None:
    """Get EC2 instance fixture by ID."""
    return EC2_INSTANCE_FIXTURES.get(instance_id)


def get_eni_by_id(eni_id: str) -> dict[str, Any] | None:
    """Get ENI fixture by ID."""
    return ENI_FIXTURES.get(eni_id)


def get_instances_by_vpc(vpc_id: str) -> list[dict[str, Any]]:
    """Get all EC2 instances in a VPC."""
    return [i for i in EC2_INSTANCE_FIXTURES.values() if i["VpcId"] == vpc_id]


def get_enis_by_vpc(vpc_id: str) -> list[dict[str, Any]]:
    """Get all ENIs in a VPC."""
    return [eni for eni in ENI_FIXTURES.values() if eni["VpcId"] == vpc_id]


def get_enis_by_subnet(subnet_id: str) -> list[dict[str, Any]]:
    """Get all ENIs in a subnet."""
    return [eni for eni in ENI_FIXTURES.values() if eni["SubnetId"] == subnet_id]


def get_instance_enis(instance_id: str) -> list[dict[str, Any]]:
    """Get all ENIs attached to an instance."""
    return [
        eni
        for eni in ENI_FIXTURES.values()
        if eni.get("Attachment", {}).get("InstanceId") == instance_id
    ]
