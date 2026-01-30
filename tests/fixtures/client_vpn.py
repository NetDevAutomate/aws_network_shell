"""Realistic Client VPN mock data fixtures.

Multi-region Client VPN architecture:
- eu-west-1: Production Client VPN with certificate authentication
- us-east-1: Staging Client VPN with federated authentication
- ap-southeast-2: Development Client VPN with split tunneling

Each endpoint includes:
- Client CIDR blocks and DNS servers
- Authentication options (certificate, federated)
- Target network associations across AZs
- Route tables and authorization rules
- Connection logging configuration
- VPN protocol settings (OpenVPN, WireGuard)
"""

from typing import Any

# =============================================================================
# CLIENT VPN ENDPOINT FIXTURES
# =============================================================================

CLIENT_VPN_ENDPOINT_FIXTURES: dict[str, dict[str, Any]] = {
    # Production Client VPN - eu-west-1 (Certificate Auth, Split Tunnel Disabled)
    "cvpn-endpoint-0prod12345": {
        "ClientVpnEndpointId": "cvpn-endpoint-0prod12345",
        "Description": "Production Client VPN - eu-west-1",
        "Status": {
            "Code": "available",
            "Message": "Client VPN endpoint is available",
        },
        "CreationTime": "2024-01-15T10:00:00+00:00",
        "ClientCidrBlock": "172.16.0.0/22",
        "DnsServers": ["10.0.0.2", "10.0.1.2"],
        "SplitTunnel": False,
        "VpnProtocol": "openvpn",
        "TransportProtocol": "tcp",
        "VpnPort": 443,
        "VpcId": "vpc-0prod1234567890ab",
        "SecurityGroupIds": ["sg-0prodcvpn123456789"],
        "ServerCertificateArn": "arn:aws:acm:eu-west-1:123456789012:certificate/prod-server-cert-12345",
        "AuthenticationOptions": [
            {
                "Type": "certificate-authentication",
                "MutualAuthentication": {
                    "ClientRootCertificateChain": "arn:aws:acm:eu-west-1:123456789012:certificate/prod-client-root-12345"
                },
            }
        ],
        "ConnectionLogOptions": {
            "Enabled": True,
            "CloudwatchLogGroup": "vpc/clientvpn/production",
            "CloudwatchLogStream": "connections",
        },
        "Tags": [
            {"Key": "Name", "Value": "production-client-vpn"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "ManagedBy", "Value": "terraform"},
            {"Key": "CostCenter", "Value": "infrastructure"},
        ],
        "SessionTimeoutHours": 24,
        "ClientConnectOptions": {
            "Enabled": False,
        },
        "ClientLoginBannerOptions": {
            "Enabled": True,
            "BannerText": "Welcome to Production VPN. All activity is monitored.",
        },
    },
    # Staging Client VPN - us-east-1 (Federated Auth, Split Tunnel Enabled)
    "cvpn-endpoint-0stag12345": {
        "ClientVpnEndpointId": "cvpn-endpoint-0stag12345",
        "Description": "Staging Client VPN - us-east-1",
        "Status": {
            "Code": "available",
            "Message": "Client VPN endpoint is available",
        },
        "CreationTime": "2024-02-01T14:00:00+00:00",
        "ClientCidrBlock": "172.17.0.0/22",
        "DnsServers": ["10.1.0.2"],
        "SplitTunnel": True,
        "VpnProtocol": "openvpn",
        "TransportProtocol": "udp",
        "VpnPort": 1194,
        "VpcId": "vpc-0stag1234567890ab",
        "SecurityGroupIds": ["sg-0stagcvpn123456789"],
        "ServerCertificateArn": "arn:aws:acm:us-east-1:123456789012:certificate/stag-server-cert-12345",
        "AuthenticationOptions": [
            {
                "Type": "federated-authentication",
                "FederatedAuthentication": {
                    "SAMLProviderArn": "arn:aws:iam::123456789012:saml-provider/staging-okta",
                    "SelfServiceSAMLProviderArn": "arn:aws:iam::123456789012:saml-provider/staging-okta-self-service",
                },
            }
        ],
        "ConnectionLogOptions": {
            "Enabled": True,
            "CloudwatchLogGroup": "vpc/clientvpn/staging",
            "CloudwatchLogStream": "connections",
        },
        "Tags": [
            {"Key": "Name", "Value": "staging-client-vpn"},
            {"Key": "Environment", "Value": "staging"},
            {"Key": "ManagedBy", "Value": "terraform"},
        ],
        "SessionTimeoutHours": 12,
        "ClientConnectOptions": {
            "Enabled": True,
            "LambdaFunctionArn": "arn:aws:lambda:us-east-1:123456789012:function:staging-vpn-connect-handler",
        },
        "ClientLoginBannerOptions": {
            "Enabled": True,
            "BannerText": "Staging Environment - For Testing Only",
        },
    },
    # Development Client VPN - ap-southeast-2 (WireGuard, Certificate Auth)
    "cvpn-endpoint-0dev012345": {
        "ClientVpnEndpointId": "cvpn-endpoint-0dev012345",
        "Description": "Development Client VPN - ap-southeast-2",
        "Status": {
            "Code": "available",
            "Message": "Client VPN endpoint is available",
        },
        "CreationTime": "2024-03-10T08:00:00+00:00",
        "ClientCidrBlock": "172.18.0.0/22",
        "DnsServers": ["10.2.0.2"],
        "SplitTunnel": True,
        "VpnProtocol": "wireguard",
        "TransportProtocol": "udp",
        "VpnPort": 51820,
        "VpcId": "vpc-0dev01234567890ab",
        "SecurityGroupIds": ["sg-0devcvpn1234567890"],
        "ServerCertificateArn": "arn:aws:acm:ap-southeast-2:123456789012:certificate/dev-server-cert-12345",
        "AuthenticationOptions": [
            {
                "Type": "certificate-authentication",
                "MutualAuthentication": {
                    "ClientRootCertificateChain": "arn:aws:acm:ap-southeast-2:123456789012:certificate/dev-client-root-12345"
                },
            }
        ],
        "ConnectionLogOptions": {
            "Enabled": False,
        },
        "Tags": [
            {"Key": "Name", "Value": "development-client-vpn"},
            {"Key": "Environment", "Value": "development"},
            {"Key": "ManagedBy", "Value": "terraform"},
        ],
        "SessionTimeoutHours": 8,
        "ClientConnectOptions": {
            "Enabled": False,
        },
        "ClientLoginBannerOptions": {
            "Enabled": False,
        },
    },
    # Pending Client VPN - showing pending-associate state
    "cvpn-endpoint-0pend12345": {
        "ClientVpnEndpointId": "cvpn-endpoint-0pend12345",
        "Description": "Pending Client VPN Configuration",
        "Status": {
            "Code": "pending-associate",
            "Message": "Waiting for target network association",
        },
        "CreationTime": "2024-03-15T10:00:00+00:00",
        "ClientCidrBlock": "172.19.0.0/22",
        "DnsServers": [],
        "SplitTunnel": True,
        "VpnProtocol": "openvpn",
        "TransportProtocol": "tcp",
        "VpnPort": 443,
        "VpcId": "vpc-0prod1234567890ab",
        "SecurityGroupIds": [],
        "ServerCertificateArn": "arn:aws:acm:eu-west-1:123456789012:certificate/pending-server-cert-12345",
        "AuthenticationOptions": [
            {
                "Type": "certificate-authentication",
                "MutualAuthentication": {
                    "ClientRootCertificateChain": "arn:aws:acm:eu-west-1:123456789012:certificate/pending-client-root-12345"
                },
            }
        ],
        "ConnectionLogOptions": {
            "Enabled": False,
        },
        "Tags": [
            {"Key": "Name", "Value": "pending-client-vpn"},
            {"Key": "Environment", "Value": "test"},
        ],
        "SessionTimeoutHours": 24,
        "ClientConnectOptions": {
            "Enabled": False,
        },
        "ClientLoginBannerOptions": {
            "Enabled": False,
        },
    },
}

# =============================================================================
# TARGET NETWORK ASSOCIATION FIXTURES
# =============================================================================

TARGET_NETWORK_FIXTURES: dict[str, list[dict[str, Any]]] = {
    # Production Client VPN target networks (multi-AZ)
    "cvpn-endpoint-0prod12345": [
        {
            "AssociationId": "cvpn-assoc-0prodaz1123456",
            "ClientVpnEndpointId": "cvpn-endpoint-0prod12345",
            "TargetNetworkId": "subnet-0prodpriv1a12345",
            "VpcId": "vpc-0prod1234567890ab",
            "Status": {
                "Code": "associated",
                "Message": "Target network is associated",
            },
            "SecurityGroups": ["sg-0prodcvpn123456789"],
        },
        {
            "AssociationId": "cvpn-assoc-0prodaz2123456",
            "ClientVpnEndpointId": "cvpn-endpoint-0prod12345",
            "TargetNetworkId": "subnet-0prodpriv1b12345",
            "VpcId": "vpc-0prod1234567890ab",
            "Status": {
                "Code": "associated",
                "Message": "Target network is associated",
            },
            "SecurityGroups": ["sg-0prodcvpn123456789"],
        },
        {
            "AssociationId": "cvpn-assoc-0prodaz3123456",
            "ClientVpnEndpointId": "cvpn-endpoint-0prod12345",
            "TargetNetworkId": "subnet-0prodpriv1c12345",
            "VpcId": "vpc-0prod1234567890ab",
            "Status": {
                "Code": "associated",
                "Message": "Target network is associated",
            },
            "SecurityGroups": ["sg-0prodcvpn123456789"],
        },
    ],
    # Staging Client VPN target networks (single AZ)
    "cvpn-endpoint-0stag12345": [
        {
            "AssociationId": "cvpn-assoc-0stag1a123456",
            "ClientVpnEndpointId": "cvpn-endpoint-0stag12345",
            "TargetNetworkId": "subnet-0stagpriv1a12345",
            "VpcId": "vpc-0stag1234567890ab",
            "Status": {
                "Code": "associated",
                "Message": "Target network is associated",
            },
            "SecurityGroups": ["sg-0stagcvpn123456789"],
        },
    ],
    # Development Client VPN target networks
    "cvpn-endpoint-0dev012345": [
        {
            "AssociationId": "cvpn-assoc-0dev1a1234567",
            "ClientVpnEndpointId": "cvpn-endpoint-0dev012345",
            "TargetNetworkId": "subnet-0devpriv1a123456",
            "VpcId": "vpc-0dev01234567890ab",
            "Status": {
                "Code": "associated",
                "Message": "Target network is associated",
            },
            "SecurityGroups": ["sg-0devcvpn1234567890"],
        },
    ],
    # Pending association
    "cvpn-endpoint-0pend12345": [
        {
            "AssociationId": "cvpn-assoc-0pend1a123456",
            "ClientVpnEndpointId": "cvpn-endpoint-0pend12345",
            "TargetNetworkId": "subnet-0prodpriv1a12345",
            "VpcId": "vpc-0prod1234567890ab",
            "Status": {
                "Code": "associating",
                "Message": "Target network association in progress",
            },
            "SecurityGroups": [],
        },
    ],
}

# =============================================================================
# CLIENT VPN ROUTE FIXTURES
# =============================================================================

CLIENT_VPN_ROUTE_FIXTURES: dict[str, list[dict[str, Any]]] = {
    # Production Client VPN routes
    "cvpn-endpoint-0prod12345": [
        {
            "ClientVpnEndpointId": "cvpn-endpoint-0prod12345",
            "DestinationCidr": "10.0.0.0/16",
            "TargetSubnet": "subnet-0prodpriv1a12345",
            "Type": "add-route",
            "Origin": "add-route",
            "Status": {
                "Code": "active",
                "Message": "Route is active",
            },
            "Description": "VPC CIDR route",
        },
        {
            "ClientVpnEndpointId": "cvpn-endpoint-0prod12345",
            "DestinationCidr": "10.10.0.0/16",
            "TargetSubnet": "subnet-0prodpriv1a12345",
            "Type": "add-route",
            "Origin": "add-route",
            "Status": {
                "Code": "active",
                "Message": "Route is active",
            },
            "Description": "On-premises network route",
        },
        {
            "ClientVpnEndpointId": "cvpn-endpoint-0prod12345",
            "DestinationCidr": "0.0.0.0/0",
            "TargetSubnet": "subnet-0prodpriv1a12345",
            "Type": "nat",
            "Origin": "add-route",
            "Status": {
                "Code": "active",
                "Message": "Route is active",
            },
            "Description": "Internet route via NAT",
        },
    ],
    # Staging Client VPN routes (split tunnel enabled - specific routes only)
    "cvpn-endpoint-0stag12345": [
        {
            "ClientVpnEndpointId": "cvpn-endpoint-0stag12345",
            "DestinationCidr": "10.1.0.0/16",
            "TargetSubnet": "subnet-0stagpriv1a12345",
            "Type": "add-route",
            "Origin": "add-route",
            "Status": {
                "Code": "active",
                "Message": "Route is active",
            },
            "Description": "Staging VPC CIDR",
        },
        {
            "ClientVpnEndpointId": "cvpn-endpoint-0stag12345",
            "DestinationCidr": "10.0.0.0/16",
            "TargetSubnet": "subnet-0stagpriv1a12345",
            "Type": "add-route",
            "Origin": "add-route",
            "Status": {
                "Code": "active",
                "Message": "Route is active",
            },
            "Description": "Production VPC CIDR access",
        },
    ],
    # Development Client VPN routes
    "cvpn-endpoint-0dev012345": [
        {
            "ClientVpnEndpointId": "cvpn-endpoint-0dev012345",
            "DestinationCidr": "10.2.0.0/16",
            "TargetSubnet": "subnet-0devpriv1a123456",
            "Type": "add-route",
            "Origin": "add-route",
            "Status": {
                "Code": "active",
                "Message": "Route is active",
            },
            "Description": "Development VPC CIDR",
        },
    ],
    # Pending endpoint (no routes yet)
    "cvpn-endpoint-0pend12345": [],
}

# =============================================================================
# AUTHORIZATION RULE FIXTURES
# =============================================================================

AUTHORIZATION_RULE_FIXTURES: dict[str, list[dict[str, Any]]] = {
    # Production Client VPN authorization rules
    "cvpn-endpoint-0prod12345": [
        {
            "ClientVpnEndpointId": "cvpn-endpoint-0prod12345",
            "DestinationCidr": "10.0.0.0/16",
            "GroupId": "S-1-5-21-prod-engineering",
            "AccessAll": False,
            "Status": {
                "Code": "active",
                "Message": "Authorization rule is active",
            },
            "Description": "Engineering team VPC access",
        },
        {
            "ClientVpnEndpointId": "cvpn-endpoint-0prod12345",
            "DestinationCidr": "10.10.0.0/16",
            "GroupId": "S-1-5-21-prod-operations",
            "AccessAll": False,
            "Status": {
                "Code": "active",
                "Message": "Authorization rule is active",
            },
            "Description": "Operations team on-premises access",
        },
        {
            "ClientVpnEndpointId": "cvpn-endpoint-0prod12345",
            "DestinationCidr": "0.0.0.0/0",
            "GroupId": "",
            "AccessAll": True,
            "Status": {
                "Code": "active",
                "Message": "Authorization rule is active",
            },
            "Description": "Internet access for all authenticated users",
        },
    ],
    # Staging Client VPN authorization rules (all users access)
    "cvpn-endpoint-0stag12345": [
        {
            "ClientVpnEndpointId": "cvpn-endpoint-0stag12345",
            "DestinationCidr": "0.0.0.0/0",
            "GroupId": "",
            "AccessAll": True,
            "Status": {
                "Code": "active",
                "Message": "Authorization rule is active",
            },
            "Description": "Full access for authenticated users",
        },
    ],
    # Development Client VPN authorization rules
    "cvpn-endpoint-0dev012345": [
        {
            "ClientVpnEndpointId": "cvpn-endpoint-0dev012345",
            "DestinationCidr": "10.2.0.0/16",
            "GroupId": "",
            "AccessAll": True,
            "Status": {
                "Code": "active",
                "Message": "Authorization rule is active",
            },
            "Description": "Dev VPC access for all",
        },
    ],
    # Pending endpoint
    "cvpn-endpoint-0pend12345": [],
}

# =============================================================================
# CONNECTION LOG FIXTURES
# =============================================================================

CLIENT_VPN_CONNECTIONS: dict[str, list[dict[str, Any]]] = {
    # Production Client VPN active connections
    "cvpn-endpoint-0prod12345": [
        {
            "ConnectionId": "cvpn-connection-0prod001",
            "ClientVpnEndpointId": "cvpn-endpoint-0prod12345",
            "Username": "john.doe@company.com",
            "ClientIp": "172.16.0.10",
            "Status": {
                "Code": "active",
                "Message": "Connection active",
            },
            "ConnectionEstablishedTime": "2024-03-15T09:00:00+00:00",
            "IngressBytes": 1024000,
            "EgressBytes": 2048000,
            "IngressPackets": 1500,
            "EgressPackets": 3000,
            "CommonName": "john.doe",
        },
        {
            "ConnectionId": "cvpn-connection-0prod002",
            "ClientVpnEndpointId": "cvpn-endpoint-0prod12345",
            "Username": "jane.smith@company.com",
            "ClientIp": "172.16.0.11",
            "Status": {
                "Code": "active",
                "Message": "Connection active",
            },
            "ConnectionEstablishedTime": "2024-03-15T08:30:00+00:00",
            "IngressBytes": 512000,
            "EgressBytes": 1024000,
            "IngressPackets": 800,
            "EgressPackets": 1600,
            "CommonName": "jane.smith",
        },
    ],
    # Staging Client VPN connections
    "cvpn-endpoint-0stag12345": [
        {
            "ConnectionId": "cvpn-connection-0stag001",
            "ClientVpnEndpointId": "cvpn-endpoint-0stag12345",
            "Username": "tester@company.com",
            "ClientIp": "172.17.0.10",
            "Status": {
                "Code": "active",
                "Message": "Connection active",
            },
            "ConnectionEstablishedTime": "2024-03-15T10:00:00+00:00",
            "IngressBytes": 256000,
            "EgressBytes": 512000,
            "IngressPackets": 400,
            "EgressPackets": 800,
            "CommonName": "tester",
        },
    ],
    # Development Client VPN connections
    "cvpn-endpoint-0dev012345": [],
    # Pending endpoint
    "cvpn-endpoint-0pend12345": [],
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_endpoint_by_id(endpoint_id: str) -> dict[str, Any] | None:
    """Get Client VPN endpoint by ID.

    Args:
        endpoint_id: Client VPN endpoint ID

    Returns:
        Endpoint data or None if not found
    """
    return CLIENT_VPN_ENDPOINT_FIXTURES.get(endpoint_id)


def get_endpoints_by_vpc(vpc_id: str) -> list[dict[str, Any]]:
    """Get all Client VPN endpoints in a VPC.

    Args:
        vpc_id: VPC ID

    Returns:
        List of endpoints in the VPC
    """
    return [
        ep for ep in CLIENT_VPN_ENDPOINT_FIXTURES.values() if ep.get("VpcId") == vpc_id
    ]


def get_endpoints_by_status(status: str) -> list[dict[str, Any]]:
    """Get Client VPN endpoints by status.

    Args:
        status: Status code (available, pending-associate, deleting)

    Returns:
        List of endpoints with matching status
    """
    return [
        ep
        for ep in CLIENT_VPN_ENDPOINT_FIXTURES.values()
        if ep.get("Status", {}).get("Code") == status
    ]


def get_target_networks(endpoint_id: str) -> list[dict[str, Any]]:
    """Get target network associations for an endpoint.

    Args:
        endpoint_id: Client VPN endpoint ID

    Returns:
        List of target network associations
    """
    return TARGET_NETWORK_FIXTURES.get(endpoint_id, [])


def get_routes(endpoint_id: str) -> list[dict[str, Any]]:
    """Get routes for an endpoint.

    Args:
        endpoint_id: Client VPN endpoint ID

    Returns:
        List of routes
    """
    return CLIENT_VPN_ROUTE_FIXTURES.get(endpoint_id, [])


def get_authorization_rules(endpoint_id: str) -> list[dict[str, Any]]:
    """Get authorization rules for an endpoint.

    Args:
        endpoint_id: Client VPN endpoint ID

    Returns:
        List of authorization rules
    """
    return AUTHORIZATION_RULE_FIXTURES.get(endpoint_id, [])


def get_active_connections(endpoint_id: str) -> list[dict[str, Any]]:
    """Get active connections for an endpoint.

    Args:
        endpoint_id: Client VPN endpoint ID

    Returns:
        List of active connections
    """
    return CLIENT_VPN_CONNECTIONS.get(endpoint_id, [])


def get_endpoints_with_split_tunnel() -> list[dict[str, Any]]:
    """Get all endpoints with split tunneling enabled.

    Returns:
        List of endpoints with split tunnel enabled
    """
    return [
        ep
        for ep in CLIENT_VPN_ENDPOINT_FIXTURES.values()
        if ep.get("SplitTunnel", False)
    ]


def get_endpoints_by_protocol(protocol: str) -> list[dict[str, Any]]:
    """Get endpoints by VPN protocol.

    Args:
        protocol: VPN protocol (openvpn, wireguard)

    Returns:
        List of endpoints using the specified protocol
    """
    return [
        ep
        for ep in CLIENT_VPN_ENDPOINT_FIXTURES.values()
        if ep.get("VpnProtocol", "").lower() == protocol.lower()
    ]


def get_endpoints_by_auth_type(auth_type: str) -> list[dict[str, Any]]:
    """Get endpoints by authentication type.

    Args:
        auth_type: Authentication type (certificate-authentication, federated-authentication)

    Returns:
        List of endpoints using the specified auth type
    """
    endpoints = []
    for ep in CLIENT_VPN_ENDPOINT_FIXTURES.values():
        auth_options = ep.get("AuthenticationOptions", [])
        if any(opt.get("Type") == auth_type for opt in auth_options):
            endpoints.append(ep)
    return endpoints


def get_all_endpoints() -> list[dict[str, Any]]:
    """Get all Client VPN endpoints.

    Returns:
        List of all endpoints
    """
    return list(CLIENT_VPN_ENDPOINT_FIXTURES.values())


def get_multi_az_endpoints() -> list[dict[str, Any]]:
    """Get endpoints with multi-AZ target network associations.

    Returns:
        List of endpoints with 2+ target networks
    """
    return [
        ep
        for ep in CLIENT_VPN_ENDPOINT_FIXTURES.values()
        if len(TARGET_NETWORK_FIXTURES.get(ep["ClientVpnEndpointId"], [])) >= 2
    ]
