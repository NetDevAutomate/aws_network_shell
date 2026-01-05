"""Realistic Elastic Load Balancer mock data fixtures.

Multi-tier load balancing architecture:
- Production ALB for web tier (HTTPS/HTTP)
- Production NLB for internal services (TCP)
- Staging ALB for testing
- Complete listener configurations
- Target groups with health checks
- Target health status

Includes:
- Application Load Balancers (ALB)
- Network Load Balancers (NLB)
- Listeners with rules and SSL certificates
- Target groups with targets and health checks
"""

from typing import Any

# =============================================================================
# ELB FIXTURES (ALB and NLB)
# =============================================================================

ELB_FIXTURES: dict[str, dict[str, Any]] = {
    # Production Application Load Balancer - eu-west-1
    "arn:aws:elasticloadbalancing:eu-west-1:123456789012:loadbalancer/app/production-alb/abc123def456": {
        "LoadBalancerArn": "arn:aws:elasticloadbalancing:eu-west-1:123456789012:loadbalancer/app/production-alb/abc123def456",
        "DNSName": "production-alb-123456789.eu-west-1.elb.amazonaws.com",
        "CanonicalHostedZoneId": "Z32O12XQLNTSW2",
        "CreatedTime": "2024-01-20T09:00:00+00:00",
        "LoadBalancerName": "production-alb",
        "Scheme": "internet-facing",
        "VpcId": "vpc-0prod1234567890ab",
        "State": {"Code": "active"},
        "Type": "application",
        "AvailabilityZones": [
            {
                "ZoneName": "eu-west-1a",
                "SubnetId": "subnet-0pub1a1234567890",
                "LoadBalancerAddresses": [{"IpAddress": "52.31.100.50"}],
            },
            {
                "ZoneName": "eu-west-1b",
                "SubnetId": "subnet-0pub1b1234567890",
                "LoadBalancerAddresses": [{"IpAddress": "52.31.100.51"}],
            },
            {
                "ZoneName": "eu-west-1c",
                "SubnetId": "subnet-0pub1c1234567890",
                "LoadBalancerAddresses": [{"IpAddress": "52.31.100.52"}],
            },
        ],
        "SecurityGroups": ["sg-0prodweb123456789"],
        "IpAddressType": "ipv4",
        "Tags": [
            {"Key": "Name", "Value": "production-alb"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "Tier", "Value": "web"},
        ],
    },
    # Production Network Load Balancer (internal) - eu-west-1
    "arn:aws:elasticloadbalancing:eu-west-1:123456789012:loadbalancer/net/production-nlb/xyz789abc123": {
        "LoadBalancerArn": "arn:aws:elasticloadbalancing:eu-west-1:123456789012:loadbalancer/net/production-nlb/xyz789abc123",
        "DNSName": "production-nlb-internal-789abc123.elb.eu-west-1.amazonaws.com",
        "CanonicalHostedZoneId": "Z2IFOLAFXWLO4F",
        "CreatedTime": "2024-01-22T10:00:00+00:00",
        "LoadBalancerName": "production-nlb",
        "Scheme": "internal",
        "VpcId": "vpc-0prod1234567890ab",
        "State": {"Code": "active"},
        "Type": "network",
        "AvailabilityZones": [
            {
                "ZoneName": "eu-west-1a",
                "SubnetId": "subnet-0priv1a123456789",
                "LoadBalancerAddresses": [{"IpAddress": "10.0.10.200"}],
            },
            {
                "ZoneName": "eu-west-1b",
                "SubnetId": "subnet-0priv1b123456789",
                "LoadBalancerAddresses": [{"IpAddress": "10.0.11.200"}],
            },
        ],
        "IpAddressType": "ipv4",
        "Tags": [
            {"Key": "Name", "Value": "production-nlb-internal"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "Tier", "Value": "application"},
        ],
    },
    # Staging Application Load Balancer - us-east-1
    "arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/staging-alb/def456ghi789": {
        "LoadBalancerArn": "arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/staging-alb/def456ghi789",
        "DNSName": "staging-alb-456789123.us-east-1.elb.amazonaws.com",
        "CanonicalHostedZoneId": "Z35SXDOTRQ7X7K",
        "CreatedTime": "2024-02-02T13:00:00+00:00",
        "LoadBalancerName": "staging-alb",
        "Scheme": "internet-facing",
        "VpcId": "vpc-0stag1234567890ab",
        "State": {"Code": "active"},
        "Type": "application",
        "AvailabilityZones": [
            {
                "ZoneName": "us-east-1a",
                "SubnetId": "subnet-0stgpub1a12345678",
                "LoadBalancerAddresses": [{"IpAddress": "54.85.100.10"}],
            },
        ],
        "SecurityGroups": ["sg-0stagapp123456789a"],
        "IpAddressType": "ipv4",
        "Tags": [
            {"Key": "Name", "Value": "staging-alb"},
            {"Key": "Environment", "Value": "staging"},
        ],
    },
}

# =============================================================================
# TARGET GROUP FIXTURES
# =============================================================================

TARGET_GROUP_FIXTURES: dict[str, dict[str, Any]] = {
    # Production Web Target Group
    "arn:aws:elasticloadbalancing:eu-west-1:123456789012:targetgroup/production-web-tg/abc123456789": {
        "TargetGroupArn": "arn:aws:elasticloadbalancing:eu-west-1:123456789012:targetgroup/production-web-tg/abc123456789",
        "TargetGroupName": "production-web-tg",
        "Protocol": "HTTP",
        "Port": 8080,
        "VpcId": "vpc-0prod1234567890ab",
        "HealthCheckProtocol": "HTTP",
        "HealthCheckPort": "traffic-port",
        "HealthCheckEnabled": True,
        "HealthCheckIntervalSeconds": 30,
        "HealthCheckTimeoutSeconds": 5,
        "HealthyThresholdCount": 2,
        "UnhealthyThresholdCount": 3,
        "HealthCheckPath": "/health",
        "Matcher": {"HttpCode": "200"},
        "LoadBalancerArns": [
            "arn:aws:elasticloadbalancing:eu-west-1:123456789012:loadbalancer/app/production-alb/abc123def456"
        ],
        "TargetType": "instance",
        "IpAddressType": "ipv4",
        "ProtocolVersion": "HTTP1",
        "Tags": [
            {"Key": "Name", "Value": "production-web-tg"},
            {"Key": "Environment", "Value": "production"},
        ],
        "Targets": [
            {
                "Id": "i-0prodweb1a123456789",
                "Port": 8080,
                "AvailabilityZone": "eu-west-1a",
            },
            {
                "Id": "i-0prodweb1b123456789",
                "Port": 8080,
                "AvailabilityZone": "eu-west-1b",
            },
        ],
    },
    # Production API Target Group (IP targets for Lambda)
    "arn:aws:elasticloadbalancing:eu-west-1:123456789012:targetgroup/production-api-tg/def456789abc": {
        "TargetGroupArn": "arn:aws:elasticloadbalancing:eu-west-1:123456789012:targetgroup/production-api-tg/def456789abc",
        "TargetGroupName": "production-api-tg",
        "Protocol": "HTTP",
        "Port": 80,
        "VpcId": "vpc-0prod1234567890ab",
        "HealthCheckProtocol": "HTTP",
        "HealthCheckPort": "traffic-port",
        "HealthCheckEnabled": True,
        "HealthCheckIntervalSeconds": 30,
        "HealthCheckTimeoutSeconds": 5,
        "HealthyThresholdCount": 2,
        "UnhealthyThresholdCount": 2,
        "HealthCheckPath": "/api/health",
        "Matcher": {"HttpCode": "200-299"},
        "LoadBalancerArns": [
            "arn:aws:elasticloadbalancing:eu-west-1:123456789012:loadbalancer/app/production-alb/abc123def456"
        ],
        "TargetType": "ip",
        "IpAddressType": "ipv4",
        "ProtocolVersion": "HTTP1",
        "Tags": [
            {"Key": "Name", "Value": "production-api-tg"},
            {"Key": "Environment", "Value": "production"},
        ],
        "Targets": [
            {
                "Id": "10.0.10.50",
                "Port": 80,
                "AvailabilityZone": "eu-west-1a",
            },
        ],
    },
    # Production Internal NLB Target Group
    "arn:aws:elasticloadbalancing:eu-west-1:123456789012:targetgroup/production-internal-tg/ghi789012def": {
        "TargetGroupArn": "arn:aws:elasticloadbalancing:eu-west-1:123456789012:targetgroup/production-internal-tg/ghi789012def",
        "TargetGroupName": "production-internal-tg",
        "Protocol": "TCP",
        "Port": 5432,
        "VpcId": "vpc-0prod1234567890ab",
        "HealthCheckProtocol": "TCP",
        "HealthCheckPort": "traffic-port",
        "HealthCheckEnabled": True,
        "HealthCheckIntervalSeconds": 30,
        "HealthCheckTimeoutSeconds": 10,
        "HealthyThresholdCount": 3,
        "UnhealthyThresholdCount": 3,
        "LoadBalancerArns": [
            "arn:aws:elasticloadbalancing:eu-west-1:123456789012:loadbalancer/net/production-nlb/xyz789abc123"
        ],
        "TargetType": "ip",
        "IpAddressType": "ipv4",
        "Tags": [
            {"Key": "Name", "Value": "production-internal-tg"},
            {"Key": "Environment", "Value": "production"},
        ],
        "Targets": [
            {
                "Id": "10.0.20.10",
                "Port": 5432,
                "AvailabilityZone": "eu-west-1a",
            },
            {
                "Id": "10.0.21.10",
                "Port": 5432,
                "AvailabilityZone": "eu-west-1b",
            },
        ],
    },
    # Staging Target Group
    "arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/staging-app-tg/jkl012345mno": {
        "TargetGroupArn": "arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/staging-app-tg/jkl012345mno",
        "TargetGroupName": "staging-app-tg",
        "Protocol": "HTTP",
        "Port": 8080,
        "VpcId": "vpc-0stag1234567890ab",
        "HealthCheckProtocol": "HTTP",
        "HealthCheckPort": "8080",
        "HealthCheckEnabled": True,
        "HealthCheckIntervalSeconds": 30,
        "HealthCheckTimeoutSeconds": 5,
        "HealthyThresholdCount": 2,
        "UnhealthyThresholdCount": 3,
        "HealthCheckPath": "/",
        "Matcher": {"HttpCode": "200"},
        "LoadBalancerArns": [
            "arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/staging-alb/def456ghi789"
        ],
        "TargetType": "instance",
        "IpAddressType": "ipv4",
        "ProtocolVersion": "HTTP1",
        "Tags": [
            {"Key": "Name", "Value": "staging-app-tg"},
            {"Key": "Environment", "Value": "staging"},
        ],
        "Targets": [
            {
                "Id": "i-0stagapp1a123456789",
                "Port": 8080,
                "AvailabilityZone": "us-east-1a",
            },
        ],
    },
}

# =============================================================================
# LISTENER FIXTURES
# =============================================================================

LISTENER_FIXTURES: dict[str, dict[str, Any]] = {
    # Production ALB HTTPS Listener
    "arn:aws:elasticloadbalancing:eu-west-1:123456789012:listener/app/production-alb/abc123def456/https443": {
        "ListenerArn": "arn:aws:elasticloadbalancing:eu-west-1:123456789012:listener/app/production-alb/abc123def456/https443",
        "LoadBalancerArn": "arn:aws:elasticloadbalancing:eu-west-1:123456789012:loadbalancer/app/production-alb/abc123def456",
        "Port": 443,
        "Protocol": "HTTPS",
        "Certificates": [
            {
                "CertificateArn": "arn:aws:acm:eu-west-1:123456789012:certificate/prod-cert-123456"
            }
        ],
        "SslPolicy": "ELBSecurityPolicy-TLS13-1-2-2021-06",
        "DefaultActions": [
            {
                "Type": "forward",
                "TargetGroupArn": "arn:aws:elasticloadbalancing:eu-west-1:123456789012:targetgroup/production-web-tg/abc123456789",
                "Order": 1,
            }
        ],
        "Rules": [
            {
                "RuleArn": "arn:aws:elasticloadbalancing:eu-west-1:123456789012:listener-rule/app/production-alb/abc123def456/https443/rule1",
                "Priority": "10",
                "Conditions": [
                    {
                        "Field": "path-pattern",
                        "Values": ["/api/*"],
                    }
                ],
                "Actions": [
                    {
                        "Type": "forward",
                        "TargetGroupArn": "arn:aws:elasticloadbalancing:eu-west-1:123456789012:targetgroup/production-api-tg/def456789abc",
                    }
                ],
                "IsDefault": False,
            },
            {
                "RuleArn": "arn:aws:elasticloadbalancing:eu-west-1:123456789012:listener-rule/app/production-alb/abc123def456/https443/default",
                "Priority": "default",
                "Conditions": [],
                "Actions": [
                    {
                        "Type": "forward",
                        "TargetGroupArn": "arn:aws:elasticloadbalancing:eu-west-1:123456789012:targetgroup/production-web-tg/abc123456789",
                    }
                ],
                "IsDefault": True,
            },
        ],
    },
    # Production ALB HTTP Listener (redirect to HTTPS)
    "arn:aws:elasticloadbalancing:eu-west-1:123456789012:listener/app/production-alb/abc123def456/http80": {
        "ListenerArn": "arn:aws:elasticloadbalancing:eu-west-1:123456789012:listener/app/production-alb/abc123def456/http80",
        "LoadBalancerArn": "arn:aws:elasticloadbalancing:eu-west-1:123456789012:loadbalancer/app/production-alb/abc123def456",
        "Port": 80,
        "Protocol": "HTTP",
        "DefaultActions": [
            {
                "Type": "redirect",
                "RedirectConfig": {
                    "Protocol": "HTTPS",
                    "Port": "443",
                    "StatusCode": "HTTP_301",
                },
                "Order": 1,
            }
        ],
    },
    # Production NLB TCP Listener
    "arn:aws:elasticloadbalancing:eu-west-1:123456789012:listener/net/production-nlb/xyz789abc123/tcp5432": {
        "ListenerArn": "arn:aws:elasticloadbalancing:eu-west-1:123456789012:listener/net/production-nlb/xyz789abc123/tcp5432",
        "LoadBalancerArn": "arn:aws:elasticloadbalancing:eu-west-1:123456789012:loadbalancer/net/production-nlb/xyz789abc123",
        "Port": 5432,
        "Protocol": "TCP",
        "DefaultActions": [
            {
                "Type": "forward",
                "TargetGroupArn": "arn:aws:elasticloadbalancing:eu-west-1:123456789012:targetgroup/production-internal-tg/ghi789012def",
                "Order": 1,
            }
        ],
    },
    # Staging ALB HTTPS Listener
    "arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/staging-alb/def456ghi789/https443": {
        "ListenerArn": "arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/staging-alb/def456ghi789/https443",
        "LoadBalancerArn": "arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/staging-alb/def456ghi789",
        "Port": 443,
        "Protocol": "HTTPS",
        "Certificates": [
            {
                "CertificateArn": "arn:aws:acm:us-east-1:123456789012:certificate/staging-cert-456789"
            }
        ],
        "SslPolicy": "ELBSecurityPolicy-TLS13-1-2-2021-06",
        "DefaultActions": [
            {
                "Type": "forward",
                "TargetGroupArn": "arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/staging-app-tg/jkl012345mno",
                "Order": 1,
            }
        ],
    },
}

# =============================================================================
# TARGET HEALTH FIXTURES
# =============================================================================

TARGET_HEALTH_FIXTURES: dict[str, list[dict[str, Any]]] = {
    # Production Web Target Group Health
    "arn:aws:elasticloadbalancing:eu-west-1:123456789012:targetgroup/production-web-tg/abc123456789": [
        {
            "Target": {
                "Id": "i-0prodweb1a123456789",
                "Port": 8080,
                "AvailabilityZone": "eu-west-1a",
            },
            "HealthCheckPort": "8080",
            "TargetHealth": {
                "State": "healthy",
                "Reason": None,
                "Description": None,
            },
        },
        {
            "Target": {
                "Id": "i-0prodweb1b123456789",
                "Port": 8080,
                "AvailabilityZone": "eu-west-1b",
            },
            "HealthCheckPort": "8080",
            "TargetHealth": {
                "State": "healthy",
                "Reason": None,
                "Description": None,
            },
        },
    ],
    # Production API Target Group Health (Lambda)
    "arn:aws:elasticloadbalancing:eu-west-1:123456789012:targetgroup/production-api-tg/def456789abc": [
        {
            "Target": {
                "Id": "10.0.10.50",
                "Port": 80,
                "AvailabilityZone": "eu-west-1a",
            },
            "HealthCheckPort": "80",
            "TargetHealth": {
                "State": "healthy",
                "Reason": None,
                "Description": None,
            },
        },
    ],
    # Production Internal NLB Target Group Health
    "arn:aws:elasticloadbalancing:eu-west-1:123456789012:targetgroup/production-internal-tg/ghi789012def": [
        {
            "Target": {
                "Id": "10.0.20.10",
                "Port": 5432,
                "AvailabilityZone": "eu-west-1a",
            },
            "HealthCheckPort": "5432",
            "TargetHealth": {
                "State": "healthy",
                "Reason": None,
                "Description": None,
            },
        },
        {
            "Target": {
                "Id": "10.0.21.10",
                "Port": 5432,
                "AvailabilityZone": "eu-west-1b",
            },
            "HealthCheckPort": "5432",
            "TargetHealth": {
                "State": "unhealthy",
                "Reason": "Target.Timeout",
                "Description": "Connection to target timed out",
            },
        },
    ],
    # Staging Target Group Health
    "arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/staging-app-tg/jkl012345mno": [
        {
            "Target": {
                "Id": "i-0stagapp1a123456789",
                "Port": 8080,
                "AvailabilityZone": "us-east-1a",
            },
            "HealthCheckPort": "8080",
            "TargetHealth": {
                "State": "healthy",
                "Reason": None,
                "Description": None,
            },
        },
    ],
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_elb_by_arn(elb_arn: str) -> dict[str, Any] | None:
    """Get ELB fixture by ARN."""
    return ELB_FIXTURES.get(elb_arn)


def get_elb_detail(elb_arn: str) -> dict[str, Any] | None:
    """Get comprehensive ELB detail with listeners, target groups, and health."""
    elb = ELB_FIXTURES.get(elb_arn)
    if not elb:
        return None

    # Gather associated listeners
    listeners = [
        lis for lis in LISTENER_FIXTURES.values() if lis["LoadBalancerArn"] == elb_arn
    ]

    # Gather associated target groups
    target_groups = [
        tg
        for tg in TARGET_GROUP_FIXTURES.values()
        if elb_arn in tg.get("LoadBalancerArns", [])
    ]

    # Gather target health for each target group
    target_health = {}
    for tg in target_groups:
        tg_arn = tg["TargetGroupArn"]
        target_health[tg_arn] = TARGET_HEALTH_FIXTURES.get(tg_arn, [])

    return {
        "load_balancer": elb,
        "listeners": listeners,
        "target_groups": target_groups,
        "target_health": target_health,
    }


def get_target_group_by_arn(tg_arn: str) -> dict[str, Any] | None:
    """Get target group by ARN."""
    return TARGET_GROUP_FIXTURES.get(tg_arn)


def get_target_health(tg_arn: str) -> list[dict[str, Any]]:
    """Get target health for a target group."""
    return TARGET_HEALTH_FIXTURES.get(tg_arn, [])


def get_listeners_by_elb(elb_arn: str) -> list[dict[str, Any]]:
    """Get all listeners for a load balancer."""
    return [
        lis for lis in LISTENER_FIXTURES.values() if lis["LoadBalancerArn"] == elb_arn
    ]


def get_target_groups_by_vpc(vpc_id: str) -> list[dict[str, Any]]:
    """Get all target groups in a VPC."""
    return [tg for tg in TARGET_GROUP_FIXTURES.values() if tg["VpcId"] == vpc_id]
