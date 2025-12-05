"""Realistic Global Accelerator mock data fixtures.

Global Accelerator architecture:
- Global service (API only in us-west-2)
- Production accelerator with TCP/UDP listeners
- Staging accelerator with health checks
- Multi-region endpoint groups
- Various endpoint types (ALB, NLB, EC2, EIP)

Each accelerator includes:
- Static anycast IP addresses
- DNS names
- Listeners with port ranges
- Endpoint groups per region
- Health check configurations
- Endpoint health states
"""

from typing import Any

# =============================================================================
# GLOBAL ACCELERATOR FIXTURES
# =============================================================================

GLOBAL_ACCELERATOR_FIXTURES: dict[str, dict[str, Any]] = {
    # Production Global Accelerator
    "arn:aws:globalaccelerator::123456789012:accelerator/prod-acc-12345": {
        "AcceleratorArn": "arn:aws:globalaccelerator::123456789012:accelerator/prod-acc-12345",
        "Name": "production-accelerator",
        "IpAddressType": "IPV4",
        "Enabled": True,
        "IpSets": [
            {
                "IpFamily": "IPv4",
                "IpAddresses": ["198.51.100.10", "198.51.100.11"],
            }
        ],
        "DnsName": "a1234567890abcdef.awsglobalaccelerator.com",
        "Status": "DEPLOYED",
        "CreatedTime": "2024-01-15T10:00:00+00:00",
        "LastModifiedTime": "2024-03-10T08:00:00+00:00",
    },
    # Staging Global Accelerator with Dual Stack
    "arn:aws:globalaccelerator::123456789012:accelerator/stag-acc-12345": {
        "AcceleratorArn": "arn:aws:globalaccelerator::123456789012:accelerator/stag-acc-12345",
        "Name": "staging-accelerator",
        "IpAddressType": "DUAL_STACK",
        "Enabled": True,
        "IpSets": [
            {
                "IpFamily": "IPv4",
                "IpAddresses": ["198.51.100.20", "198.51.100.21"],
            },
            {
                "IpFamily": "IPv6",
                "IpAddresses": ["2600:9000:a000::1", "2600:9000:a000::2"],
            },
        ],
        "DnsName": "a1234567890fedcba.awsglobalaccelerator.com",
        "Status": "DEPLOYED",
        "CreatedTime": "2024-02-01T14:00:00+00:00",
        "LastModifiedTime": "2024-03-12T10:00:00+00:00",
    },
    # Development Accelerator (Disabled)
    "arn:aws:globalaccelerator::123456789012:accelerator/dev-acc-012345": {
        "AcceleratorArn": "arn:aws:globalaccelerator::123456789012:accelerator/dev-acc-012345",
        "Name": "development-accelerator",
        "IpAddressType": "IPV4",
        "Enabled": False,
        "IpSets": [
            {
                "IpFamily": "IPv4",
                "IpAddresses": ["198.51.100.30", "198.51.100.31"],
            }
        ],
        "DnsName": "a1234567890aaaaaa.awsglobalaccelerator.com",
        "Status": "DEPLOYED",
        "CreatedTime": "2024-03-01T08:00:00+00:00",
        "LastModifiedTime": "2024-03-05T12:00:00+00:00",
    },
    # In-Progress Accelerator
    "arn:aws:globalaccelerator::123456789012:accelerator/pend-acc-12345": {
        "AcceleratorArn": "arn:aws:globalaccelerator::123456789012:accelerator/pend-acc-12345",
        "Name": "pending-accelerator",
        "IpAddressType": "IPV4",
        "Enabled": False,
        "IpSets": [
            {
                "IpFamily": "IPv4",
                "IpAddresses": ["198.51.100.40", "198.51.100.41"],
            }
        ],
        "DnsName": "a1234567890bbbbbb.awsglobalaccelerator.com",
        "Status": "IN_PROGRESS",
        "CreatedTime": "2024-03-15T10:00:00+00:00",
        "LastModifiedTime": "2024-03-15T10:05:00+00:00",
    },
}

# =============================================================================
# LISTENER FIXTURES
# =============================================================================

LISTENER_FIXTURES: dict[str, list[dict[str, Any]]] = {
    # Production Accelerator Listeners
    "arn:aws:globalaccelerator::123456789012:accelerator/prod-acc-12345": [
        {
            "ListenerArn": "arn:aws:globalaccelerator::123456789012:accelerator/prod-acc-12345/listener/prod-listener-tcp-80",
            "PortRanges": [
                {"FromPort": 80, "ToPort": 80},
                {"FromPort": 443, "ToPort": 443},
            ],
            "Protocol": "TCP",
            "ClientAffinity": "SOURCE_IP",
        },
        {
            "ListenerArn": "arn:aws:globalaccelerator::123456789012:accelerator/prod-acc-12345/listener/prod-listener-udp-53",
            "PortRanges": [
                {"FromPort": 53, "ToPort": 53},
            ],
            "Protocol": "UDP",
            "ClientAffinity": "NONE",
        },
    ],
    # Staging Accelerator Listeners
    "arn:aws:globalaccelerator::123456789012:accelerator/stag-acc-12345": [
        {
            "ListenerArn": "arn:aws:globalaccelerator::123456789012:accelerator/stag-acc-12345/listener/stag-listener-tcp-8080",
            "PortRanges": [
                {"FromPort": 8080, "ToPort": 8080},
            ],
            "Protocol": "TCP",
            "ClientAffinity": "NONE",
        },
    ],
    # Development Accelerator Listeners
    "arn:aws:globalaccelerator::123456789012:accelerator/dev-acc-012345": [
        {
            "ListenerArn": "arn:aws:globalaccelerator::123456789012:accelerator/dev-acc-012345/listener/dev-listener-tcp-3000",
            "PortRanges": [
                {"FromPort": 3000, "ToPort": 3000},
            ],
            "Protocol": "TCP",
            "ClientAffinity": "SOURCE_IP",
        },
    ],
    # Pending Accelerator (no listeners yet)
    "arn:aws:globalaccelerator::123456789012:accelerator/pend-acc-12345": [],
}

# =============================================================================
# ENDPOINT GROUP FIXTURES
# =============================================================================

ENDPOINT_GROUP_FIXTURES: dict[str, list[dict[str, Any]]] = {
    # Production TCP Listener Endpoint Groups (Multi-Region)
    "arn:aws:globalaccelerator::123456789012:accelerator/prod-acc-12345/listener/prod-listener-tcp-80": [
        {
            "EndpointGroupArn": "arn:aws:globalaccelerator::123456789012:accelerator/prod-acc-12345/listener/prod-listener-tcp-80/endpoint-group/prod-eg-eu-west-1",
            "EndpointGroupRegion": "eu-west-1",
            "TrafficDialPercentage": 100.0,
            "HealthCheckPort": 80,
            "HealthCheckProtocol": "HTTP",
            "HealthCheckPath": "/health",
            "HealthCheckIntervalSeconds": 30,
            "ThresholdCount": 3,
            "EndpointDescriptions": [
                {
                    "EndpointId": "arn:aws:elasticloadbalancing:eu-west-1:123456789012:loadbalancer/app/prod-alb/abc123def456",
                    "Weight": 128,
                    "HealthState": "HEALTHY",
                    "HealthReason": "",
                    "ClientIPPreservationEnabled": True,
                },
                {
                    "EndpointId": "arn:aws:elasticloadbalancing:eu-west-1:123456789012:loadbalancer/net/prod-nlb/xyz789uvw012",
                    "Weight": 128,
                    "HealthState": "HEALTHY",
                    "HealthReason": "",
                    "ClientIPPreservationEnabled": False,
                },
            ],
        },
        {
            "EndpointGroupArn": "arn:aws:globalaccelerator::123456789012:accelerator/prod-acc-12345/listener/prod-listener-tcp-80/endpoint-group/prod-eg-us-east-1",
            "EndpointGroupRegion": "us-east-1",
            "TrafficDialPercentage": 50.0,
            "HealthCheckPort": 80,
            "HealthCheckProtocol": "HTTP",
            "HealthCheckPath": "/health",
            "HealthCheckIntervalSeconds": 30,
            "ThresholdCount": 3,
            "EndpointDescriptions": [
                {
                    "EndpointId": "arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/dr-alb/def456ghi789",
                    "Weight": 64,
                    "HealthState": "HEALTHY",
                    "HealthReason": "",
                    "ClientIPPreservationEnabled": True,
                },
            ],
        },
    ],
    # Production UDP Listener Endpoint Groups
    "arn:aws:globalaccelerator::123456789012:accelerator/prod-acc-12345/listener/prod-listener-udp-53": [
        {
            "EndpointGroupArn": "arn:aws:globalaccelerator::123456789012:accelerator/prod-acc-12345/listener/prod-listener-udp-53/endpoint-group/prod-eg-dns-eu",
            "EndpointGroupRegion": "eu-west-1",
            "TrafficDialPercentage": 100.0,
            "HealthCheckPort": 53,
            "HealthCheckProtocol": "TCP",
            "HealthCheckPath": "",
            "HealthCheckIntervalSeconds": 30,
            "ThresholdCount": 3,
            "EndpointDescriptions": [
                {
                    "EndpointId": "arn:aws:elasticloadbalancing:eu-west-1:123456789012:loadbalancer/net/dns-nlb/nlb123abc456",
                    "Weight": 128,
                    "HealthState": "HEALTHY",
                    "HealthReason": "",
                    "ClientIPPreservationEnabled": False,
                },
            ],
        },
    ],
    # Staging Listener Endpoint Groups
    "arn:aws:globalaccelerator::123456789012:accelerator/stag-acc-12345/listener/stag-listener-tcp-8080": [
        {
            "EndpointGroupArn": "arn:aws:globalaccelerator::123456789012:accelerator/stag-acc-12345/listener/stag-listener-tcp-8080/endpoint-group/stag-eg-us-east-1",
            "EndpointGroupRegion": "us-east-1",
            "TrafficDialPercentage": 100.0,
            "HealthCheckPort": 8080,
            "HealthCheckProtocol": "HTTP",
            "HealthCheckPath": "/health",
            "HealthCheckIntervalSeconds": 10,
            "ThresholdCount": 2,
            "EndpointDescriptions": [
                {
                    "EndpointId": "arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/stag-alb/stag123abc456",
                    "Weight": 128,
                    "HealthState": "HEALTHY",
                    "HealthReason": "",
                    "ClientIPPreservationEnabled": True,
                },
                {
                    "EndpointId": "i-0stag1234567890ab",
                    "Weight": 64,
                    "HealthState": "UNHEALTHY",
                    "HealthReason": "Endpoint is not responding to health checks",
                    "ClientIPPreservationEnabled": False,
                },
            ],
        },
    ],
    # Development Listener Endpoint Groups
    "arn:aws:globalaccelerator::123456789012:accelerator/dev-acc-012345/listener/dev-listener-tcp-3000": [
        {
            "EndpointGroupArn": "arn:aws:globalaccelerator::123456789012:accelerator/dev-acc-012345/listener/dev-listener-tcp-3000/endpoint-group/dev-eg-ap-southeast-2",
            "EndpointGroupRegion": "ap-southeast-2",
            "TrafficDialPercentage": 100.0,
            "HealthCheckPort": 3000,
            "HealthCheckProtocol": "TCP",
            "HealthCheckPath": "",
            "HealthCheckIntervalSeconds": 30,
            "ThresholdCount": 3,
            "EndpointDescriptions": [
                {
                    "EndpointId": "eipalloc-0dev123456789abcd",
                    "Weight": 128,
                    "HealthState": "INITIAL",
                    "HealthReason": "Initial health check in progress",
                    "ClientIPPreservationEnabled": True,
                },
            ],
        },
    ],
}

# =============================================================================
# ACCELERATOR ATTRIBUTES
# =============================================================================

ACCELERATOR_ATTRIBUTES: dict[str, dict[str, Any]] = {
    # Production Accelerator Attributes
    "arn:aws:globalaccelerator::123456789012:accelerator/prod-acc-12345": {
        "AcceleratorArn": "arn:aws:globalaccelerator::123456789012:accelerator/prod-acc-12345",
        "FlowLogsEnabled": True,
        "FlowLogsS3Bucket": "prod-globalaccelerator-flow-logs",
        "FlowLogsS3Prefix": "production/",
    },
    # Staging Accelerator Attributes
    "arn:aws:globalaccelerator::123456789012:accelerator/stag-acc-12345": {
        "AcceleratorArn": "arn:aws:globalaccelerator::123456789012:accelerator/stag-acc-12345",
        "FlowLogsEnabled": True,
        "FlowLogsS3Bucket": "stag-globalaccelerator-flow-logs",
        "FlowLogsS3Prefix": "staging/",
    },
    # Development Accelerator Attributes
    "arn:aws:globalaccelerator::123456789012:accelerator/dev-acc-012345": {
        "AcceleratorArn": "arn:aws:globalaccelerator::123456789012:accelerator/dev-acc-012345",
        "FlowLogsEnabled": False,
        "FlowLogsS3Bucket": "",
        "FlowLogsS3Prefix": "",
    },
    # Pending Accelerator Attributes
    "arn:aws:globalaccelerator::123456789012:accelerator/pend-acc-12345": {
        "AcceleratorArn": "arn:aws:globalaccelerator::123456789012:accelerator/pend-acc-12345",
        "FlowLogsEnabled": False,
        "FlowLogsS3Bucket": "",
        "FlowLogsS3Prefix": "",
    },
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_accelerator_by_arn(arn: str) -> dict[str, Any] | None:
    """Get Global Accelerator by ARN.

    Args:
        arn: Accelerator ARN

    Returns:
        Accelerator data or None if not found
    """
    return GLOBAL_ACCELERATOR_FIXTURES.get(arn)


def get_accelerator_by_name(name: str) -> dict[str, Any] | None:
    """Get Global Accelerator by name.

    Args:
        name: Accelerator name

    Returns:
        Accelerator data or None if not found
    """
    for acc in GLOBAL_ACCELERATOR_FIXTURES.values():
        if acc.get("Name") == name:
            return acc
    return None


def get_enabled_accelerators() -> list[dict[str, Any]]:
    """Get all enabled accelerators.

    Returns:
        List of enabled accelerators
    """
    return [
        acc
        for acc in GLOBAL_ACCELERATOR_FIXTURES.values()
        if acc.get("Enabled", False)
    ]


def get_accelerators_by_status(status: str) -> list[dict[str, Any]]:
    """Get accelerators by deployment status.

    Args:
        status: Status (DEPLOYED, IN_PROGRESS)

    Returns:
        List of accelerators with matching status
    """
    return [
        acc for acc in GLOBAL_ACCELERATOR_FIXTURES.values() if acc.get("Status") == status
    ]


def get_listeners(accelerator_arn: str) -> list[dict[str, Any]]:
    """Get listeners for an accelerator.

    Args:
        accelerator_arn: Accelerator ARN

    Returns:
        List of listeners
    """
    return LISTENER_FIXTURES.get(accelerator_arn, [])


def get_endpoint_groups(listener_arn: str) -> list[dict[str, Any]]:
    """Get endpoint groups for a listener.

    Args:
        listener_arn: Listener ARN

    Returns:
        List of endpoint groups
    """
    return ENDPOINT_GROUP_FIXTURES.get(listener_arn, [])


def get_accelerator_attributes(accelerator_arn: str) -> dict[str, Any] | None:
    """Get accelerator attributes.

    Args:
        accelerator_arn: Accelerator ARN

    Returns:
        Accelerator attributes or None if not found
    """
    return ACCELERATOR_ATTRIBUTES.get(accelerator_arn)


def get_endpoints_by_health_state(health_state: str) -> list[dict[str, Any]]:
    """Get all endpoints with a specific health state.

    Args:
        health_state: Health state (HEALTHY, UNHEALTHY, INITIAL)

    Returns:
        List of endpoints with matching health state
    """
    endpoints = []
    for endpoint_groups in ENDPOINT_GROUP_FIXTURES.values():
        for group in endpoint_groups:
            for ep in group.get("EndpointDescriptions", []):
                if ep.get("HealthState") == health_state:
                    endpoints.append(
                        {
                            "endpoint": ep,
                            "endpoint_group_arn": group["EndpointGroupArn"],
                            "region": group["EndpointGroupRegion"],
                        }
                    )
    return endpoints


def get_unhealthy_endpoints() -> list[dict[str, Any]]:
    """Get all unhealthy endpoints across all accelerators.

    Returns:
        List of unhealthy endpoints with context
    """
    return get_endpoints_by_health_state("UNHEALTHY")


def get_endpoint_groups_by_region(region: str) -> list[dict[str, Any]]:
    """Get all endpoint groups in a specific region.

    Args:
        region: AWS region

    Returns:
        List of endpoint groups in the region
    """
    groups = []
    for endpoint_groups in ENDPOINT_GROUP_FIXTURES.values():
        for group in endpoint_groups:
            if group.get("EndpointGroupRegion") == region:
                groups.append(group)
    return groups


def get_listeners_by_protocol(protocol: str) -> list[dict[str, Any]]:
    """Get all listeners using a specific protocol.

    Args:
        protocol: Protocol (TCP, UDP)

    Returns:
        List of listeners with matching protocol
    """
    listeners = []
    for acc_listeners in LISTENER_FIXTURES.values():
        for listener in acc_listeners:
            if listener.get("Protocol") == protocol:
                listeners.append(listener)
    return listeners


def get_accelerators_with_flow_logs() -> list[dict[str, Any]]:
    """Get all accelerators with flow logs enabled.

    Returns:
        List of accelerators with flow logs enabled
    """
    enabled_arns = [
        arn
        for arn, attrs in ACCELERATOR_ATTRIBUTES.items()
        if attrs.get("FlowLogsEnabled", False)
    ]
    return [
        acc
        for arn, acc in GLOBAL_ACCELERATOR_FIXTURES.items()
        if arn in enabled_arns
    ]


def get_all_accelerators() -> list[dict[str, Any]]:
    """Get all Global Accelerators.

    Returns:
        List of all accelerators
    """
    return list(GLOBAL_ACCELERATOR_FIXTURES.values())


def get_endpoint_groups_with_traffic_dial_below(
    percentage: float,
) -> list[dict[str, Any]]:
    """Get endpoint groups with traffic dial below specified percentage.

    Args:
        percentage: Traffic dial percentage threshold

    Returns:
        List of endpoint groups with traffic dial below threshold
    """
    groups = []
    for endpoint_groups in ENDPOINT_GROUP_FIXTURES.values():
        for group in endpoint_groups:
            if group.get("TrafficDialPercentage", 100.0) < percentage:
                groups.append(group)
    return groups


def count_endpoints_by_type() -> dict[str, int]:
    """Count endpoints by type (ALB, NLB, EC2, EIP).

    Returns:
        Dictionary with counts for each endpoint type
    """
    counts = {"alb": 0, "nlb": 0, "ec2": 0, "eip": 0, "other": 0}

    for endpoint_groups in ENDPOINT_GROUP_FIXTURES.values():
        for group in endpoint_groups:
            for ep in group.get("EndpointDescriptions", []):
                endpoint_id = ep.get("EndpointId", "")
                if "loadbalancer/app/" in endpoint_id:
                    counts["alb"] += 1
                elif "loadbalancer/net/" in endpoint_id:
                    counts["nlb"] += 1
                elif endpoint_id.startswith("i-"):
                    counts["ec2"] += 1
                elif endpoint_id.startswith("eipalloc-"):
                    counts["eip"] += 1
                else:
                    counts["other"] += 1

    return counts


def get_dual_stack_accelerators() -> list[dict[str, Any]]:
    """Get accelerators with dual stack (IPv4 and IPv6) support.

    Returns:
        List of dual stack accelerators
    """
    return [
        acc
        for acc in GLOBAL_ACCELERATOR_FIXTURES.values()
        if acc.get("IpAddressType") == "DUAL_STACK"
    ]
