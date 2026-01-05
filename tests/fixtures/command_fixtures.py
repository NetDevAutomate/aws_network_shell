"""Command-to-fixture mapping for graph-based testing.

Maps every shell command to its fixture data and mock targets.
Uses actual module Client.discover() pattern.
"""

from typing import Any
from . import (
    VPC_FIXTURES,
    SUBNET_FIXTURES,
    ROUTE_TABLE_FIXTURES,
    SECURITY_GROUP_FIXTURES,
    NACL_FIXTURES,
    TGW_FIXTURES,
    TGW_ATTACHMENT_FIXTURES,
    TGW_ROUTE_TABLE_FIXTURES,
    CLOUDWAN_FIXTURES,
    EC2_INSTANCE_FIXTURES,
    ELB_FIXTURES,
    VPN_CONNECTION_FIXTURES,
    NETWORK_FIREWALL_FIXTURES,
    RULE_GROUP_FIXTURES,
    IGW_FIXTURES,
    NAT_GATEWAY_FIXTURES,
    get_vpc_detail,
)


def get_tag_value(resource: dict, key: str = "Name") -> str:
    """Extract tag value from AWS resource."""
    for tag in resource.get("Tags", []):
        if tag.get("Key") == key:
            return tag.get("Value", "")
    return ""


# =============================================================================
# FIXTURE DATA GENERATORS - Match shell's expected format
# =============================================================================


def _vpcs_list():
    """Generate VPC list in shell's expected format."""
    return [
        {
            "id": vpc_id,
            "name": get_tag_value(vpc) or vpc_id,
            "region": "eu-west-1",
            "cidr": vpc["CidrBlock"],
            "cidrs": [vpc["CidrBlock"]],
            "state": vpc["State"],
        }
        for vpc_id, vpc in VPC_FIXTURES.items()
    ]


def _tgws_list():
    """Generate TGW list in shell's expected format."""
    return [
        {
            "id": tgw_id,
            "name": get_tag_value(tgw) or tgw_id,
            "region": "eu-west-1",
            "state": tgw["State"],
            "attachments": [],
            "route_tables": [],
        }
        for tgw_id, tgw in TGW_FIXTURES.items()
    ]


def _global_networks_list():
    """Generate global networks list."""
    return [
        {
            "id": "global-network-0prod123456789",
            "name": "production-global-network",
            "state": "AVAILABLE",
            "description": "Production global network",
        }
    ]


def _core_networks_list():
    """Generate core networks list."""
    return [
        {
            "id": cn_id,
            "name": get_tag_value(cn) or cn_id,
            "global_network_id": cn.get("GlobalNetworkId", "global-network-123"),
            "state": cn.get("State", "AVAILABLE"),
            "segments": ["production", "development"],
            "regions": ["eu-west-1", "us-east-1"],
            "nfgs": [],
            "route_tables": [],
            "policy": {},
        }
        for cn_id, cn in CLOUDWAN_FIXTURES.items()
    ]


def _firewalls_list():
    """Generate firewall list."""
    return [
        {
            "name": fw["FirewallName"],
            "arn": fw["FirewallArn"],
            "region": "eu-west-1",
            "vpc_id": fw["VpcId"],
            "status": fw.get("FirewallStatus", {}).get("Status", "READY"),
            "policy_arn": fw.get("FirewallPolicyArn", ""),
            "rule_groups": [],
        }
        for fw in NETWORK_FIREWALL_FIXTURES.values()
    ]


def _ec2_instances_list():
    """Generate EC2 instances list."""
    return [
        {
            "id": inst_id,
            "name": get_tag_value(inst) or inst_id,
            "region": "eu-west-1",
            "type": inst["InstanceType"],
            "state": inst["State"]["Name"],
            "private_ip": inst.get("PrivateIpAddress"),
            "public_ip": inst.get("PublicIpAddress"),
            "vpc_id": inst.get("VpcId"),
            "subnet_id": inst.get("SubnetId"),
        }
        for inst_id, inst in EC2_INSTANCE_FIXTURES.items()
    ]


def _elbs_list():
    """Generate ELB list."""
    return [
        {
            "arn": elb["LoadBalancerArn"],
            "name": elb["LoadBalancerName"],
            "type": elb["Type"],
            "scheme": elb["Scheme"],
            "state": elb["State"]["Code"],
            "dns_name": elb["DNSName"],
            "vpc_id": elb["VpcId"],
            "region": "eu-west-1",
        }
        for elb in ELB_FIXTURES.values()
    ]


def _vpns_list():
    """Generate VPN list."""
    return [
        {
            "id": vpn_id,
            "name": get_tag_value(vpn) or vpn_id,
            "region": "eu-west-1",
            "state": vpn["State"],
            "type": vpn["Type"],
            "customer_gateway_id": vpn["CustomerGatewayId"],
            "tunnels": vpn.get("VgwTelemetry", []),
        }
        for vpn_id, vpn in VPN_CONNECTION_FIXTURES.items()
    ]


# =============================================================================
# COMMAND MOCK CONFIGURATION - Using actual Client.discover() paths
# =============================================================================

COMMAND_MOCKS: dict[str, dict[str, Any]] = {
    # =========================================================================
    # ROOT LEVEL SHOW COMMANDS - Mock Client.discover()
    # =========================================================================
    "show vpcs": {
        "mock_target": "aws_network_tools.modules.vpc.VPCClient.discover",
        "fixture_data": _vpcs_list,
    },
    "show transit_gateways": {
        "mock_target": "aws_network_tools.modules.tgw.TGWClient.discover",
        "fixture_data": _tgws_list,
    },
    "show global-networks": {
        "mock_target": "aws_network_tools.modules.cloudwan.CloudWANClient.list_global_networks",
        "fixture_data": _global_networks_list,
    },
    "show firewalls": {
        "mock_target": "aws_network_tools.modules.anfw.ANFWClient.discover",
        "fixture_data": _firewalls_list,
    },
    "show ec2-instances": {
        "mock_target": "aws_network_tools.modules.ec2.EC2Client.discover",
        "fixture_data": _ec2_instances_list,
    },
    "show elbs": {
        "mock_target": "aws_network_tools.modules.elb.ELBClient.discover",
        "fixture_data": _elbs_list,
    },
    "show vpns": {
        "mock_target": "aws_network_tools.modules.vpn.VPNClient.discover",
        "fixture_data": _vpns_list,
    },
    # =========================================================================
    # VPC CONTEXT COMMANDS
    # =========================================================================
    "vpc.show detail": {
        "mock_target": "aws_network_tools.modules.vpc.VPCClient.get_vpc_detail",
        "fixture_data": lambda vpc_id=None: get_vpc_detail(
            vpc_id or list(VPC_FIXTURES.keys())[0]
        )
        or {
            "id": vpc_id,
            "name": "test-vpc",
            "region": "eu-west-1",
            "cidr": "10.0.0.0/16",
            "cidrs": ["10.0.0.0/16"],
            "state": "available",
            "route_tables": [],
            "security_groups": [],
            "nacls": [],
        },
    },
    "vpc.show subnets": {
        "mock_target": "aws_network_tools.modules.vpc.VPCClient.get_vpc_detail",
        "fixture_data": lambda: {
            "subnets": [
                {
                    "id": s["SubnetId"],
                    "name": get_tag_value(s),
                    "cidr": s.get("CidrBlock", "10.0.0.0/24"),
                    "az": s["AvailabilityZone"],
                    "state": s["State"],
                }
                for s in list(SUBNET_FIXTURES.values())[:5]
            ]
        },
    },
    "vpc.show route-tables": {
        "mock_target": "aws_network_tools.modules.vpc.VPCClient.get_vpc_detail",
        "fixture_data": lambda: {
            "route_tables": [
                {
                    "id": rt["RouteTableId"],
                    "name": get_tag_value(rt),
                    "is_main": any(a.get("Main") for a in rt.get("Associations", [])),
                    "routes": rt.get("Routes", []),
                    "subnets": [
                        a["SubnetId"]
                        for a in rt.get("Associations", [])
                        if a.get("SubnetId")
                    ],
                }
                for rt in list(ROUTE_TABLE_FIXTURES.values())[:3]
            ]
        },
    },
    "vpc.show security-groups": {
        "mock_target": "aws_network_tools.modules.vpc.VPCClient.get_vpc_detail",
        "fixture_data": lambda: {
            "security_groups": [
                {
                    "id": sg["GroupId"],
                    "name": sg["GroupName"],
                    "description": sg.get("Description", ""),
                    "ingress": [],
                    "egress": [],
                }
                for sg in list(SECURITY_GROUP_FIXTURES.values())[:3]
            ]
        },
    },
    "vpc.show nacls": {
        "mock_target": "aws_network_tools.modules.vpc.VPCClient.get_vpc_detail",
        "fixture_data": lambda: {
            "nacls": [
                {
                    "id": nacl["NetworkAclId"],
                    "name": get_tag_value(nacl),
                    "is_default": nacl.get("IsDefault", False),
                    "entries": [],
                }
                for nacl in list(NACL_FIXTURES.values())[:2]
            ]
        },
    },
    "vpc.show internet-gateways": {
        "mock_target": "aws_network_tools.modules.vpc.VPCClient.get_vpc_detail",
        "fixture_data": lambda: {
            "internet_gateways": [
                {
                    "id": igw["InternetGatewayId"],
                    "name": get_tag_value(igw),
                    "state": "attached",
                }
                for igw in list(IGW_FIXTURES.values())[:1]
            ]
        },
    },
    "vpc.show nat-gateways": {
        "mock_target": "aws_network_tools.modules.vpc.VPCClient.get_vpc_detail",
        "fixture_data": lambda: {
            "nat_gateways": [
                {
                    "id": nat["NatGatewayId"],
                    "name": get_tag_value(nat),
                    "state": nat["State"],
                    "subnet_id": nat["SubnetId"],
                }
                for nat in list(NAT_GATEWAY_FIXTURES.values())[:2]
            ]
        },
    },
    "vpc.show endpoints": {
        "mock_target": "aws_network_tools.modules.vpc.VPCClient.get_vpc_detail",
        "fixture_data": lambda: {"endpoints": []},
    },
    # =========================================================================
    # TRANSIT GATEWAY CONTEXT COMMANDS
    # =========================================================================
    "transit-gateway.show detail": {
        "mock_target": "aws_network_tools.modules.tgw.TGWClient.discover",
        "fixture_data": _tgws_list,
    },
    "transit-gateway.show route-tables": {
        "mock_target": "aws_network_tools.modules.tgw.TGWClient.discover",
        "fixture_data": lambda: [
            {
                "id": "tgw-123",
                "route_tables": [
                    {
                        "id": rt["TransitGatewayRouteTableId"],
                        "name": get_tag_value(rt),
                        "state": rt.get("State", "available"),
                        "routes": [],
                    }
                    for rt in list(TGW_ROUTE_TABLE_FIXTURES.values())[:2]
                ],
            }
        ],
    },
    "transit-gateway.show attachments": {
        "mock_target": "aws_network_tools.modules.tgw.TGWClient.discover",
        "fixture_data": lambda: [
            {
                "id": "tgw-123",
                "attachments": [
                    {
                        "id": att["TransitGatewayAttachmentId"],
                        "type": att["ResourceType"],
                        "resource_id": att.get("ResourceId"),
                        "state": att["State"],
                    }
                    for att in list(TGW_ATTACHMENT_FIXTURES.values())[:3]
                ],
            }
        ],
    },
    # =========================================================================
    # FIREWALL CONTEXT COMMANDS
    # =========================================================================
    "firewall.show detail": {
        "mock_target": "aws_network_tools.modules.anfw.ANFWClient.discover",
        "fixture_data": _firewalls_list,
    },
    "firewall.show rule-groups": {
        "mock_target": "aws_network_tools.modules.anfw.ANFWClient.discover",
        "fixture_data": lambda: [
            {
                "name": "test-fw",
                "rule_groups": [
                    {
                        "name": rg["RuleGroupName"],
                        "arn": rg["RuleGroupArn"],
                        "type": rg["Type"],
                    }
                    for rg in list(RULE_GROUP_FIXTURES.values())[:2]
                ],
            }
        ],
    },
    "firewall.show policy": {
        "mock_target": "aws_network_tools.modules.anfw.ANFWClient.discover",
        "fixture_data": _firewalls_list,
    },
    # =========================================================================
    # EC2 INSTANCE CONTEXT COMMANDS
    # =========================================================================
    "ec2-instance.show detail": {
        "mock_target": "aws_network_tools.modules.ec2.EC2Client.discover",
        "fixture_data": _ec2_instances_list,
    },
    "ec2-instance.show security-groups": {
        "mock_target": "aws_network_tools.modules.ec2.EC2Client.discover",
        "fixture_data": _ec2_instances_list,
    },
    "ec2-instance.show enis": {
        "mock_target": "aws_network_tools.modules.ec2.EC2Client.discover",
        "fixture_data": _ec2_instances_list,
    },
    "ec2-instance.show routes": {
        "mock_target": "aws_network_tools.modules.ec2.EC2Client.discover",
        "fixture_data": _ec2_instances_list,
    },
    # =========================================================================
    # ELB CONTEXT COMMANDS
    # =========================================================================
    "elb.show detail": {
        "mock_target": "aws_network_tools.modules.elb.ELBClient.discover",
        "fixture_data": _elbs_list,
    },
    "elb.show listeners": {
        "mock_target": "aws_network_tools.modules.elb.ELBClient.discover",
        "fixture_data": _elbs_list,
    },
    "elb.show targets": {
        "mock_target": "aws_network_tools.modules.elb.ELBClient.discover",
        "fixture_data": _elbs_list,
    },
    "elb.show health": {
        "mock_target": "aws_network_tools.modules.elb.ELBClient.discover",
        "fixture_data": _elbs_list,
    },
    # =========================================================================
    # VPN CONTEXT COMMANDS
    # =========================================================================
    "vpn.show detail": {
        "mock_target": "aws_network_tools.modules.vpn.VPNClient.discover",
        "fixture_data": _vpns_list,
    },
    "vpn.show tunnels": {
        "mock_target": "aws_network_tools.modules.vpn.VPNClient.discover",
        "fixture_data": _vpns_list,
    },
    # =========================================================================
    # CORE NETWORK CONTEXT COMMANDS
    # =========================================================================
    "core-network.show detail": {
        "mock_target": "aws_network_tools.modules.cloudwan.CloudWANClient.discover",
        "fixture_data": _core_networks_list,
    },
    "core-network.show segments": {
        "mock_target": "aws_network_tools.modules.cloudwan.CloudWANClient.discover",
        "fixture_data": _core_networks_list,
    },
    "core-network.show policy": {
        "mock_target": "aws_network_tools.modules.cloudwan.CloudWANClient.discover",
        "fixture_data": _core_networks_list,
    },
    "core-network.show routes": {
        "mock_target": "aws_network_tools.modules.cloudwan.CloudWANClient.discover",
        "fixture_data": _core_networks_list,
    },
    "core-network.show route-tables": {
        "mock_target": "aws_network_tools.modules.cloudwan.CloudWANClient.discover",
        "fixture_data": _core_networks_list,
    },
    "core-network.show blackhole-routes": {
        "mock_target": "aws_network_tools.modules.cloudwan.CloudWANClient.discover",
        "fixture_data": _core_networks_list,
    },
}


# =============================================================================
# COMMAND DEPENDENCIES
# =============================================================================

COMMAND_DEPENDENCIES: dict[str, list[str]] = {
    "set vpc": ["show vpcs"],
    "set transit-gateway": ["show transit_gateways"],
    "set global-network": ["show global-networks"],
    "set firewall": ["show firewalls"],
    "set ec2-instance": ["show ec2-instances"],
    "set elb": ["show elbs"],
    "set vpn": ["show vpns"],
    "global-network.set core-network": ["show global-networks"],
    "core-network.set route-table": ["core-network.show route-tables"],
    "vpc.set route-table": ["show vpcs", "vpc.show route-tables"],
    "transit-gateway.set route-table": [
        "show transit_gateways",
        "transit-gateway.show route-tables",
    ],
}


def get_mock_for_command(command: str, **context_args) -> dict[str, Any] | None:
    """Get mock configuration for a command."""
    config = COMMAND_MOCKS.get(command)
    if not config:
        return None

    fixture_fn = config["fixture_data"]
    return_value = fixture_fn() if callable(fixture_fn) else fixture_fn

    return {
        "target": config["mock_target"],
        "return_value": return_value,
    }


def get_dependencies(command: str) -> list[str]:
    """Get commands that must be mocked before this command."""
    return COMMAND_DEPENDENCIES.get(command, [])
