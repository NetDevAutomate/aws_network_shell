"""Realistic AWS mock data fixtures for comprehensive testing.

This module provides production-quality mock data that mirrors real AWS API responses.
Each fixture includes realistic IDs, names, configurations, and relationships between resources.

Architecture:
- Multi-region setup (eu-west-1, us-east-1, ap-southeast-2)
- Production/Staging/Development environments
- Interconnected VPCs via Transit Gateway and CloudWAN
- Network Firewalls for inspection
- Load balancers with target groups and health checks
"""

from .vpc import (
    VPC_FIXTURES,
    SUBNET_FIXTURES,
    ROUTE_TABLE_FIXTURES,
    SECURITY_GROUP_FIXTURES,
    NACL_FIXTURES,
    get_vpc_by_id,
    get_vpc_detail,
)
from .tgw import (
    TGW_FIXTURES,
    TGW_ATTACHMENT_FIXTURES,
    TGW_ROUTE_TABLE_FIXTURES,
    TGW_PEERING_FIXTURES,
    get_tgw_by_id,
    get_tgw_detail,
)
from .global_network import (
    GLOBAL_NETWORK_FIXTURES,
    get_global_network_by_id,
    get_all_global_networks,
)
from .cloudwan import (
    CLOUDWAN_FIXTURES,
    CLOUDWAN_ATTACHMENT_FIXTURES,
    CLOUDWAN_SEGMENT_FIXTURES,
    get_core_network_by_id,
    get_core_network_detail,
)
from .ec2 import (
    EC2_INSTANCE_FIXTURES,
    ENI_FIXTURES,
    get_instance_by_id,
    get_eni_by_id,
)
from .elb import (
    ELB_FIXTURES,
    TARGET_GROUP_FIXTURES,
    LISTENER_FIXTURES,
    get_elb_by_arn,
    get_elb_detail,
)
from .vpn import (
    VPN_CONNECTION_FIXTURES,
    CUSTOMER_GATEWAY_FIXTURES,
    VPN_GATEWAY_FIXTURES,
    get_vpn_by_id,
    get_vpn_detail,
)
from .firewall import (
    NETWORK_FIREWALL_FIXTURES,
    FIREWALL_POLICY_FIXTURES,
    RULE_GROUP_FIXTURES,
    get_firewall_by_name,
    get_firewall_detail,
)
from .gateways import (
    IGW_FIXTURES,
    NAT_GATEWAY_FIXTURES,
    EIP_FIXTURES,
    EGRESS_ONLY_IGW_FIXTURES,
    get_igw_by_id,
    get_igw_by_vpc,
    get_nat_by_id,
    get_nat_by_vpc,
    get_nat_by_subnet,
    get_nat_by_state,
    get_eip_by_allocation_id,
    get_eip_by_public_ip,
    get_eip_by_eni,
    get_unallocated_eips,
    get_eigw_by_id,
    get_eigw_by_vpc,
    get_all_gateways_by_vpc,
    get_gateway_summary,
)

__all__ = [
    # Global Network
    "GLOBAL_NETWORK_FIXTURES",
    "get_global_network_by_id",
    "get_all_global_networks",
    # VPC
    "VPC_FIXTURES",
    "SUBNET_FIXTURES",
    "ROUTE_TABLE_FIXTURES",
    "SECURITY_GROUP_FIXTURES",
    "NACL_FIXTURES",
    "get_vpc_by_id",
    "get_vpc_detail",
    # TGW
    "TGW_FIXTURES",
    "TGW_ATTACHMENT_FIXTURES",
    "TGW_ROUTE_TABLE_FIXTURES",
    "TGW_PEERING_FIXTURES",
    "get_tgw_by_id",
    "get_tgw_detail",
    # CloudWAN
    "CLOUDWAN_FIXTURES",
    "CLOUDWAN_ATTACHMENT_FIXTURES",
    "CLOUDWAN_SEGMENT_FIXTURES",
    "get_core_network_by_id",
    "get_core_network_detail",
    # EC2
    "EC2_INSTANCE_FIXTURES",
    "ENI_FIXTURES",
    "get_instance_by_id",
    "get_eni_by_id",
    # ELB
    "ELB_FIXTURES",
    "TARGET_GROUP_FIXTURES",
    "LISTENER_FIXTURES",
    "get_elb_by_arn",
    "get_elb_detail",
    # VPN
    "VPN_CONNECTION_FIXTURES",
    "CUSTOMER_GATEWAY_FIXTURES",
    "VPN_GATEWAY_FIXTURES",
    "get_vpn_by_id",
    "get_vpn_detail",
    # Firewall
    "NETWORK_FIREWALL_FIXTURES",
    "FIREWALL_POLICY_FIXTURES",
    "RULE_GROUP_FIXTURES",
    "get_firewall_by_name",
    "get_firewall_detail",
    # Gateways
    "IGW_FIXTURES",
    "NAT_GATEWAY_FIXTURES",
    "EIP_FIXTURES",
    "EGRESS_ONLY_IGW_FIXTURES",
    "get_igw_by_id",
    "get_igw_by_vpc",
    "get_nat_by_id",
    "get_nat_by_vpc",
    "get_nat_by_subnet",
    "get_nat_by_state",
    "get_eip_by_allocation_id",
    "get_eip_by_public_ip",
    "get_eip_by_eni",
    "get_unallocated_eips",
    "get_eigw_by_id",
    "get_eigw_by_vpc",
    "get_all_gateways_by_vpc",
    "get_gateway_summary",
]
