"""Realistic VPN and Direct Connect mock data fixtures.

Hybrid connectivity architecture:
- Site-to-Site VPN to Dublin datacenter
- Site-to-Site VPN to London office
- Direct Connect connection to primary datacenter
- VPN over Direct Connect (backup)

Each connection includes:
- Customer Gateway configurations
- Virtual Private Gateway attachments
- Tunnel status and BGP information
- Routing propagation details
"""

from typing import Any

# =============================================================================
# VPN CONNECTION FIXTURES
# =============================================================================

VPN_CONNECTION_FIXTURES: dict[str, dict[str, Any]] = {
    # Production VPN to Dublin Datacenter
    "vpn-0prod12345678901": {
        "VpnConnectionId": "vpn-0prod12345678901",
        "State": "available",
        "Type": "ipsec.1",
        "CustomerGatewayId": "cgw-0dublin123456789",
        "VpnGatewayId": None,
        "TransitGatewayId": "tgw-0prod12345678901",
        "CoreNetworkArn": None,
        "CustomerGatewayConfiguration": "<?xml version='1.0' encoding='UTF-8'?><!-- Customer Gateway Configuration -->",
        "Options": {
            "EnableAcceleration": False,
            "StaticRoutesOnly": False,
            "LocalIpv4NetworkCidr": "10.0.0.0/16",
            "RemoteIpv4NetworkCidr": "192.168.0.0/16",
            "TunnelInsideIpVersion": "ipv4",
            "TunnelOptions": [
                {
                    "OutsideIpAddress": "52.31.200.10",
                    "TunnelInsideCidr": "169.254.10.0/30",
                    "PreSharedKey": "**hidden**",
                    "Phase1LifetimeSeconds": 28800,
                    "Phase2LifetimeSeconds": 3600,
                    "RekeyMarginTimeSeconds": 540,
                    "RekeyFuzzPercentage": 100,
                    "ReplayWindowSize": 1024,
                    "DpdTimeoutSeconds": 30,
                    "DpdTimeoutAction": "clear",
                    "Phase1EncryptionAlgorithms": [{"Value": "AES256"}],
                    "Phase2EncryptionAlgorithms": [{"Value": "AES256"}],
                    "Phase1IntegrityAlgorithms": [{"Value": "SHA2-256"}],
                    "Phase2IntegrityAlgorithms": [{"Value": "SHA2-256"}],
                    "Phase1DHGroupNumbers": [{"Value": 14}],
                    "Phase2DHGroupNumbers": [{"Value": 14}],
                    "IkeVersions": [{"Value": "ikev2"}],
                    "StartupAction": "add",
                },
                {
                    "OutsideIpAddress": "52.31.200.11",
                    "TunnelInsideCidr": "169.254.10.4/30",
                    "PreSharedKey": "**hidden**",
                    "Phase1LifetimeSeconds": 28800,
                    "Phase2LifetimeSeconds": 3600,
                    "RekeyMarginTimeSeconds": 540,
                    "RekeyFuzzPercentage": 100,
                    "ReplayWindowSize": 1024,
                    "DpdTimeoutSeconds": 30,
                    "DpdTimeoutAction": "clear",
                    "Phase1EncryptionAlgorithms": [{"Value": "AES256"}],
                    "Phase2EncryptionAlgorithms": [{"Value": "AES256"}],
                    "Phase1IntegrityAlgorithms": [{"Value": "SHA2-256"}],
                    "Phase2IntegrityAlgorithms": [{"Value": "SHA2-256"}],
                    "Phase1DHGroupNumbers": [{"Value": 14}],
                    "Phase2DHGroupNumbers": [{"Value": 14}],
                    "IkeVersions": [{"Value": "ikev2"}],
                    "StartupAction": "add",
                },
            ],
        },
        "Routes": [
            {
                "DestinationCidrBlock": "192.168.0.0/16",
                "Source": "static",
                "State": "available",
            },
            {
                "DestinationCidrBlock": "192.168.10.0/24",
                "Source": "static",
                "State": "available",
            },
        ],
        "VgwTelemetry": [
            {
                "OutsideIpAddress": "52.31.200.10",
                "Status": "UP",
                "LastStatusChange": "2024-01-18T15:00:00+00:00",
                "StatusMessage": "Tunnel is up and passing traffic",
                "AcceptedRouteCount": 2,
                "CertificateArn": None,
            },
            {
                "OutsideIpAddress": "52.31.200.11",
                "Status": "UP",
                "LastStatusChange": "2024-01-18T15:02:00+00:00",
                "StatusMessage": "Tunnel is up and passing traffic",
                "AcceptedRouteCount": 2,
                "CertificateArn": None,
            },
        ],
        "Category": "VPN",
        "Tags": [
            {"Key": "Name", "Value": "production-dublin-vpn"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "Location", "Value": "dublin-datacenter"},
        ],
    },
    # Production VPN to London Office
    "vpn-0london123456789": {
        "VpnConnectionId": "vpn-0london123456789",
        "State": "available",
        "Type": "ipsec.1",
        "CustomerGatewayId": "cgw-0london123456789",
        "VpnGatewayId": "vgw-0prod12345678901",
        "TransitGatewayId": None,
        "CoreNetworkArn": None,
        "CustomerGatewayConfiguration": "<?xml version='1.0' encoding='UTF-8'?><!-- Customer Gateway Configuration -->",
        "Options": {
            "EnableAcceleration": False,
            "StaticRoutesOnly": True,
            "LocalIpv4NetworkCidr": "10.0.0.0/16",
            "RemoteIpv4NetworkCidr": "192.168.100.0/24",
            "TunnelInsideIpVersion": "ipv4",
            "TunnelOptions": [
                {
                    "OutsideIpAddress": "52.31.201.20",
                    "TunnelInsideCidr": "169.254.20.0/30",
                    "PreSharedKey": "**hidden**",
                    "Phase1LifetimeSeconds": 28800,
                    "Phase2LifetimeSeconds": 3600,
                    "StartupAction": "add",
                },
                {
                    "OutsideIpAddress": "52.31.201.21",
                    "TunnelInsideCidr": "169.254.20.4/30",
                    "PreSharedKey": "**hidden**",
                    "Phase1LifetimeSeconds": 28800,
                    "Phase2LifetimeSeconds": 3600,
                    "StartupAction": "add",
                },
            ],
        },
        "Routes": [
            {
                "DestinationCidrBlock": "192.168.100.0/24",
                "Source": "static",
                "State": "available",
            },
        ],
        "VgwTelemetry": [
            {
                "OutsideIpAddress": "52.31.201.20",
                "Status": "UP",
                "LastStatusChange": "2024-01-25T10:00:00+00:00",
                "StatusMessage": "Tunnel is up and passing traffic",
                "AcceptedRouteCount": 1,
                "CertificateArn": None,
            },
            {
                "OutsideIpAddress": "52.31.201.21",
                "Status": "DOWN",
                "LastStatusChange": "2024-02-01T08:30:00+00:00",
                "StatusMessage": "IKE negotiation failed",
                "AcceptedRouteCount": 0,
                "CertificateArn": None,
            },
        ],
        "Category": "VPN",
        "Tags": [
            {"Key": "Name", "Value": "production-london-vpn"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "Location", "Value": "london-office"},
        ],
    },
    # CloudWAN VPN Connection
    "vpn-0cloudwan123456789": {
        "VpnConnectionId": "vpn-0cloudwan123456789",
        "State": "available",
        "Type": "ipsec.1",
        "CustomerGatewayId": "cgw-0sydney123456789",
        "VpnGatewayId": None,
        "TransitGatewayId": None,
        "CoreNetworkArn": "arn:aws:networkmanager::123456789012:core-network/core-network-0global123",
        "CustomerGatewayConfiguration": "<?xml version='1.0' encoding='UTF-8'?><!-- Customer Gateway Configuration -->",
        "Options": {
            "EnableAcceleration": True,
            "StaticRoutesOnly": False,
            "LocalIpv4NetworkCidr": "10.2.0.0/16",
            "RemoteIpv4NetworkCidr": "192.168.200.0/24",
            "TunnelInsideIpVersion": "ipv4",
            "TunnelOptions": [
                {
                    "OutsideIpAddress": "52.62.100.30",
                    "TunnelInsideCidr": "169.254.30.0/30",
                    "PreSharedKey": "**hidden**",
                    "StartupAction": "start",
                },
                {
                    "OutsideIpAddress": "52.62.100.31",
                    "TunnelInsideCidr": "169.254.30.4/30",
                    "PreSharedKey": "**hidden**",
                    "StartupAction": "start",
                },
            ],
        },
        "Routes": [],
        "VgwTelemetry": [
            {
                "OutsideIpAddress": "52.62.100.30",
                "Status": "UP",
                "LastStatusChange": "2024-02-20T12:00:00+00:00",
                "StatusMessage": "Tunnel is up and passing traffic",
                "AcceptedRouteCount": 5,
                "CertificateArn": None,
            },
            {
                "OutsideIpAddress": "52.62.100.31",
                "Status": "UP",
                "LastStatusChange": "2024-02-20T12:01:00+00:00",
                "StatusMessage": "Tunnel is up and passing traffic",
                "AcceptedRouteCount": 5,
                "CertificateArn": None,
            },
        ],
        "Category": "VPN",
        "Tags": [
            {"Key": "Name", "Value": "cloudwan-sydney-vpn"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "Location", "Value": "sydney-office"},
        ],
    },
}

# =============================================================================
# CUSTOMER GATEWAY FIXTURES
# =============================================================================

CUSTOMER_GATEWAY_FIXTURES: dict[str, dict[str, Any]] = {
    # Dublin Datacenter Customer Gateway
    "cgw-0dublin123456789": {
        "CustomerGatewayId": "cgw-0dublin123456789",
        "State": "available",
        "Type": "ipsec.1",
        "IpAddress": "203.0.113.100",
        "BgpAsn": "65000",
        "BgpAsnExtended": "65000",
        "DeviceName": "Dublin-DC-Firewall-01",
        "Tags": [
            {"Key": "Name", "Value": "dublin-datacenter-cgw"},
            {"Key": "Location", "Value": "dublin"},
            {"Key": "Type", "Value": "datacenter"},
        ],
    },
    # London Office Customer Gateway
    "cgw-0london123456789": {
        "CustomerGatewayId": "cgw-0london123456789",
        "State": "available",
        "Type": "ipsec.1",
        "IpAddress": "198.51.100.50",
        "BgpAsn": "65001",
        "BgpAsnExtended": "65001",
        "DeviceName": "London-Office-Router",
        "Tags": [
            {"Key": "Name", "Value": "london-office-cgw"},
            {"Key": "Location", "Value": "london"},
            {"Key": "Type", "Value": "branch-office"},
        ],
    },
    # Sydney Office Customer Gateway
    "cgw-0sydney123456789": {
        "CustomerGatewayId": "cgw-0sydney123456789",
        "State": "available",
        "Type": "ipsec.1",
        "IpAddress": "203.0.113.200",
        "BgpAsn": "65002",
        "BgpAsnExtended": "65002",
        "DeviceName": "Sydney-Office-Router",
        "Tags": [
            {"Key": "Name", "Value": "sydney-office-cgw"},
            {"Key": "Location", "Value": "sydney"},
            {"Key": "Type", "Value": "branch-office"},
        ],
    },
}

# =============================================================================
# VPN GATEWAY FIXTURES
# =============================================================================

VPN_GATEWAY_FIXTURES: dict[str, dict[str, Any]] = {
    # Production Virtual Private Gateway
    "vgw-0prod12345678901": {
        "VpnGatewayId": "vgw-0prod12345678901",
        "State": "available",
        "Type": "ipsec.1",
        "AmazonSideAsn": 64512,
        "VpcAttachments": [
            {
                "State": "attached",
                "VpcId": "vpc-0prod1234567890ab",
            }
        ],
        "Tags": [
            {"Key": "Name", "Value": "production-vgw"},
            {"Key": "Environment", "Value": "production"},
        ],
    },
    # Shared Services Virtual Private Gateway
    "vgw-0shared123456789": {
        "VpnGatewayId": "vgw-0shared123456789",
        "State": "available",
        "Type": "ipsec.1",
        "AmazonSideAsn": 64513,
        "VpcAttachments": [
            {
                "State": "attached",
                "VpcId": "vpc-0shared123456789a",
            }
        ],
        "Tags": [
            {"Key": "Name", "Value": "shared-services-vgw"},
            {"Key": "Environment", "Value": "shared"},
        ],
    },
}

# =============================================================================
# DIRECT CONNECT GATEWAY FIXTURES
# =============================================================================

DIRECT_CONNECT_GATEWAY_FIXTURES: dict[str, dict[str, Any]] = {
    # Production Direct Connect Gateway
    "dxgw-0prod12345678901": {
        "DirectConnectGatewayId": "dxgw-0prod12345678901",
        "DirectConnectGatewayName": "production-dxgw",
        "AmazonSideAsn": 64515,
        "OwnerAccount": "123456789012",
        "DirectConnectGatewayState": "available",
        "StateChangeError": None,
    },
}

# =============================================================================
# DIRECT CONNECT CONNECTION FIXTURES
# =============================================================================

DIRECT_CONNECT_CONNECTION_FIXTURES: dict[str, dict[str, Any]] = {
    # 10 Gbps Direct Connect to Dublin Datacenter
    "dxcon-0dublin123456789": {
        "ConnectionId": "dxcon-0dublin123456789",
        "ConnectionName": "dublin-datacenter-dx",
        "ConnectionState": "available",
        "Region": "eu-west-1",
        "Location": "EqLD5",
        "Bandwidth": "10Gbps",
        "Vlan": 100,
        "PartnerName": "Equinix",
        "LoaIssueTime": "2024-01-10T08:00:00+00:00",
        "LagId": None,
        "AwsDevice": "EqLD5-12ab34cd56ef78gh",
        "JumboFrameCapable": True,
        "AwsDeviceV2": "EqLD5-12ab34cd56ef78gh",
        "AwsLogicalDeviceId": "EqLD5-12ab34cd56ef78gh-1",
        "HasLogicalRedundancy": "unknown",
        "Tags": [
            {"Key": "Name", "Value": "dublin-datacenter-dx"},
            {"Key": "Location", "Value": "dublin"},
            {"Key": "Speed", "Value": "10Gbps"},
        ],
        "ProviderName": "Equinix",
        "MacSecCapable": True,
        "PortEncryptionStatus": "not_encrypted",
        "EncryptionMode": None,
    },
}

# =============================================================================
# DIRECT CONNECT VIRTUAL INTERFACE FIXTURES
# =============================================================================

DIRECT_CONNECT_VIF_FIXTURES: dict[str, dict[str, Any]] = {
    # Private VIF to Production DXGW
    "dxvif-0prod12345678901": {
        "VirtualInterfaceId": "dxvif-0prod12345678901",
        "VirtualInterfaceName": "production-private-vif",
        "VirtualInterfaceType": "private",
        "VirtualInterfaceState": "available",
        "ConnectionId": "dxcon-0dublin123456789",
        "DirectConnectGatewayId": "dxgw-0prod12345678901",
        "Vlan": 101,
        "Asn": 65000,
        "AmazonSideAsn": 64515,
        "AuthKey": "**hidden**",
        "AmazonAddress": "169.254.100.1/30",
        "CustomerAddress": "169.254.100.2/30",
        "AddressFamily": "ipv4",
        "VirtualGatewayId": None,
        "Region": "eu-west-1",
        "AwsDeviceV2": "EqLD5-12ab34cd56ef78gh-1",
        "AwsLogicalDeviceId": "EqLD5-12ab34cd56ef78gh-1",
        "Tags": [
            {"Key": "Name", "Value": "production-private-vif"},
            {"Key": "Environment", "Value": "production"},
        ],
        "SiteLinkEnabled": False,
        "BgpPeers": [
            {
                "BgpPeerId": "dxpeer-0prod1234567",
                "Asn": 65000,
                "AuthKey": "**hidden**",
                "AddressFamily": "ipv4",
                "AmazonAddress": "169.254.100.1/30",
                "CustomerAddress": "169.254.100.2/30",
                "BgpPeerState": "available",
                "BgpStatus": "up",
                "AwsDeviceV2": "EqLD5-12ab34cd56ef78gh-1",
                "AwsLogicalDeviceId": "EqLD5-12ab34cd56ef78gh-1",
            }
        ],
    },
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_vpn_by_id(vpn_id: str) -> dict[str, Any] | None:
    """Get VPN connection fixture by ID."""
    return VPN_CONNECTION_FIXTURES.get(vpn_id)


def get_vpn_detail(vpn_id: str) -> dict[str, Any] | None:
    """Get comprehensive VPN detail with customer gateway and routing."""
    vpn = VPN_CONNECTION_FIXTURES.get(vpn_id)
    if not vpn:
        return None

    # Get associated customer gateway
    cgw_id = vpn.get("CustomerGatewayId")
    customer_gateway = CUSTOMER_GATEWAY_FIXTURES.get(cgw_id) if cgw_id else None

    # Get associated VPN gateway if present
    vgw_id = vpn.get("VpnGatewayId")
    vpn_gateway = VPN_GATEWAY_FIXTURES.get(vgw_id) if vgw_id else None

    return {
        "vpn_connection": vpn,
        "customer_gateway": customer_gateway,
        "vpn_gateway": vpn_gateway,
        "tunnels": vpn.get("VgwTelemetry", []),
        "routes": vpn.get("Routes", []),
    }


def get_customer_gateway_by_id(cgw_id: str) -> dict[str, Any] | None:
    """Get customer gateway by ID."""
    return CUSTOMER_GATEWAY_FIXTURES.get(cgw_id)


def get_vpn_gateway_by_id(vgw_id: str) -> dict[str, Any] | None:
    """Get VPN gateway by ID."""
    return VPN_GATEWAY_FIXTURES.get(vgw_id)


def get_dxgw_by_id(dxgw_id: str) -> dict[str, Any] | None:
    """Get Direct Connect gateway by ID."""
    return DIRECT_CONNECT_GATEWAY_FIXTURES.get(dxgw_id)


def get_dx_connection_by_id(dx_id: str) -> dict[str, Any] | None:
    """Get Direct Connect connection by ID."""
    return DIRECT_CONNECT_CONNECTION_FIXTURES.get(dx_id)


def get_dx_vif_by_id(vif_id: str) -> dict[str, Any] | None:
    """Get Direct Connect virtual interface by ID."""
    return DIRECT_CONNECT_VIF_FIXTURES.get(vif_id)


def get_vpns_by_tgw(tgw_id: str) -> list[dict[str, Any]]:
    """Get all VPN connections attached to a Transit Gateway."""
    return [
        vpn
        for vpn in VPN_CONNECTION_FIXTURES.values()
        if vpn.get("TransitGatewayId") == tgw_id
    ]


def get_vpns_by_vgw(vgw_id: str) -> list[dict[str, Any]]:
    """Get all VPN connections attached to a VPN Gateway."""
    return [
        vpn
        for vpn in VPN_CONNECTION_FIXTURES.values()
        if vpn.get("VpnGatewayId") == vgw_id
    ]
