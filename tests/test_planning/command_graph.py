"""Complete command graph for AWS Network Shell testing.

This module provides programmatic access to the complete command structure
for test generation and validation.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class Command:
    """Represents a single testable command."""
    name: str
    context: Optional[str]
    requires_arg: bool
    arg_type: Optional[str] = None
    output_type: Optional[str] = None
    sets_context: Optional[str] = None
    modifies: Optional[str] = None
    cached: bool = False
    context_aware: bool = False
    valid_values: Optional[List[str]] = None
    optional_args: Optional[List[str]] = None


# Root context commands
ROOT_SHOW_COMMANDS: List[Command] = [
    Command("show version", None, False, output_type="text"),
    Command("show global-networks", None, False, output_type="table", cached=True),
    Command("show vpcs", None, False, output_type="table", cached=True),
    Command("show transit_gateways", None, False, output_type="table", cached=True),
    Command("show firewalls", None, False, output_type="table", cached=True),
    Command("show dx-connections", None, False, output_type="table"),
    Command("show enis", None, False, output_type="table"),
    Command("show bgp-neighbors", None, False, output_type="table"),
    Command("show ec2-instances", None, False, output_type="table"),
    Command("show elbs", None, False, output_type="table"),
    Command("show vpns", None, False, output_type="table"),
    Command("show security-groups", None, False, output_type="table"),
    Command("show unused-sgs", None, False, output_type="table"),
    Command("show resolver-endpoints", None, False, output_type="table"),
    Command("show resolver-rules", None, False, output_type="table"),
    Command("show query-logs", None, False, output_type="table"),
    Command("show peering-connections", None, False, output_type="table"),
    Command("show prefix-lists", None, False, output_type="table"),
    Command("show network-alarms", None, False, output_type="table"),
    Command("show alarms-critical", None, False, output_type="table"),
    Command("show client-vpn-endpoints", None, False, output_type="table"),
    Command("show global-accelerators", None, False, output_type="table"),
    Command("show ga-endpoint-health", None, False, output_type="table"),
    Command("show endpoint-services", None, False, output_type="table"),
    Command("show vpc-endpoints", None, False, output_type="table"),
    Command("show config", None, False, output_type="yaml"),
    Command("show running-config", None, False, output_type="yaml"),
    Command("show cache", None, False, output_type="json"),
    Command("show routing-cache", None, False, output_type="json"),
    Command("show graph", None, False, output_type="graph"),
]

ROOT_SET_COMMANDS: List[Command] = [
    Command("set global-network", None, True, arg_type="ref", sets_context="global-network"),
    Command("set vpc", None, True, arg_type="ref", sets_context="vpc"),
    Command("set transit-gateway", None, True, arg_type="ref", sets_context="transit-gateway"),
    Command("set firewall", None, True, arg_type="ref", sets_context="firewall"),
    Command("set ec2-instance", None, True, arg_type="ref", sets_context="ec2-instance"),
    Command("set elb", None, True, arg_type="ref", sets_context="elb"),
    Command("set vpn", None, True, arg_type="ref", sets_context="vpn"),
    Command("set profile", None, True, arg_type="name", modifies="profile"),
    Command("set regions", None, True, arg_type="region_list", modifies="regions"),
    Command("set no-cache", None, False, modifies="no_cache"),
    Command("set output-format", None, True, arg_type="format", modifies="output_format",
            valid_values=["table", "json", "yaml"]),
    Command("set output-file", None, True, arg_type="filename", modifies="output_file"),
    Command("set watch", None, True, arg_type="interval", modifies="watch_interval"),
    Command("set theme", None, True, arg_type="theme_name", modifies="theme"),
    Command("set prompt", None, True, arg_type="style", modifies="prompt_style"),
]

ROOT_ACTION_COMMANDS: List[Command] = [
    Command("write", None, True, arg_type="filename"),
    Command("trace", None, True, arg_type="src_dst_ips"),
    Command("find_ip", None, True, arg_type="ip_address"),
    Command("find_prefix", None, True, arg_type="cidr", context_aware=True),
    Command("find_null_routes", None, False, context_aware=True),
    Command("populate_cache", None, False),
    Command("clear_cache", None, False),
    Command("create_routing_cache", None, False),
    Command("validate_graph", None, False),
    Command("export_graph", None, True, arg_type="filename"),
]

# Global-network context
GLOBAL_NETWORK_COMMANDS: List[Command] = [
    Command("show detail", "global-network", False, output_type="table"),
    Command("show core-networks", "global-network", False, output_type="table", cached=True),
    Command("set core-network", "global-network", True, arg_type="ref", sets_context="core-network"),
]

# Core-network context
CORE_NETWORK_COMMANDS: List[Command] = [
    Command("show detail", "core-network", False, output_type="table"),
    Command("show segments", "core-network", False, output_type="table"),
    Command("show policy", "core-network", False, output_type="json"),
    Command("show policy-documents", "core-network", False, output_type="table"),
    Command("show live-policy", "core-network", False, output_type="json"),
    Command("show routes", "core-network", False, output_type="table"),
    Command("show route-tables", "core-network", False, output_type="table"),
    Command("show blackhole-routes", "core-network", False, output_type="table"),
    Command("show policy-change-events", "core-network", False, output_type="table"),
    Command("show connect-attachments", "core-network", False, output_type="table"),
    Command("show connect-peers", "core-network", False, output_type="table"),
    Command("show rib", "core-network", False, output_type="table",
            optional_args=["segment=<name>", "edge=<location>"]),
    Command("set route-table", "core-network", True, arg_type="ref", sets_context="route-table"),
    Command("find_prefix", "core-network", True, arg_type="cidr", context_aware=True),
    Command("find_null_routes", "core-network", False, context_aware=True),
]

# Route-table context
ROUTE_TABLE_COMMANDS: List[Command] = [
    Command("show routes", "route-table", False, output_type="table"),
    Command("find_prefix", "route-table", True, arg_type="cidr", context_aware=True),
    Command("find_null_routes", "route-table", False, context_aware=True),
]

# VPC context
VPC_COMMANDS: List[Command] = [
    Command("show detail", "vpc", False, output_type="table"),
    Command("show route-tables", "vpc", False, output_type="table"),
    Command("show subnets", "vpc", False, output_type="table"),
    Command("show security-groups", "vpc", False, output_type="table"),
    Command("show nacls", "vpc", False, output_type="table"),
    Command("show internet-gateways", "vpc", False, output_type="table"),
    Command("show nat-gateways", "vpc", False, output_type="table"),
    Command("show endpoints", "vpc", False, output_type="table"),
    Command("set route-table", "vpc", True, arg_type="ref", sets_context="route-table"),
    Command("find_prefix", "vpc", True, arg_type="cidr", context_aware=True),
    Command("find_null_routes", "vpc", False, context_aware=True),
]

# Transit-gateway context
TRANSIT_GATEWAY_COMMANDS: List[Command] = [
    Command("show detail", "transit-gateway", False, output_type="table"),
    Command("show route-tables", "transit-gateway", False, output_type="table"),
    Command("show attachments", "transit-gateway", False, output_type="table"),
    Command("set route-table", "transit-gateway", True, arg_type="ref", sets_context="route-table"),
    Command("find_prefix", "transit-gateway", True, arg_type="cidr", context_aware=True),
    Command("find_null_routes", "transit-gateway", False, context_aware=True),
]

# Firewall context
FIREWALL_COMMANDS: List[Command] = [
    Command("show detail", "firewall", False, output_type="table"),
    Command("show rule-groups", "firewall", False, output_type="table"),
    Command("show policy", "firewall", False, output_type="json"),
    Command("show firewall-policy", "firewall", False, output_type="json"),
]

# EC2-instance context
EC2_INSTANCE_COMMANDS: List[Command] = [
    Command("show detail", "ec2-instance", False, output_type="table"),
    Command("show security-groups", "ec2-instance", False, output_type="table"),
    Command("show enis", "ec2-instance", False, output_type="table"),
    Command("show routes", "ec2-instance", False, output_type="table"),
]

# ELB context
ELB_COMMANDS: List[Command] = [
    Command("show detail", "elb", False, output_type="table"),
    Command("show listeners", "elb", False, output_type="table"),
    Command("show targets", "elb", False, output_type="table"),
    Command("show health", "elb", False, output_type="table"),
]

# VPN context
VPN_COMMANDS: List[Command] = [
    Command("show detail", "vpn", False, output_type="table"),
    Command("show tunnels", "vpn", False, output_type="table"),
]

# Navigation commands (context-independent)
NAVIGATION_COMMANDS: List[Command] = [
    Command("exit", None, False),
    Command("end", None, False),
    Command("clear", None, False),
    Command("?", None, False),
]

# Complete command registry
ALL_COMMANDS: Dict[str, List[Command]] = {
    None: ROOT_SHOW_COMMANDS + ROOT_SET_COMMANDS + ROOT_ACTION_COMMANDS + NAVIGATION_COMMANDS,
    "global-network": GLOBAL_NETWORK_COMMANDS,
    "core-network": CORE_NETWORK_COMMANDS,
    "route-table": ROUTE_TABLE_COMMANDS,
    "vpc": VPC_COMMANDS,
    "transit-gateway": TRANSIT_GATEWAY_COMMANDS,
    "firewall": FIREWALL_COMMANDS,
    "ec2-instance": EC2_INSTANCE_COMMANDS,
    "elb": ELB_COMMANDS,
    "vpn": VPN_COMMANDS,
}


# Known issues tracking
KNOWN_ISSUES: Dict[str, Dict[str, Any]] = {
    "issue_9": {
        "number": 9,
        "title": "EC2 context show enis/security-groups returns all account data",
        "status": "OPEN",
        "severity": "HIGH",
        "affected_commands": [
            "ec2-instance> show enis",
            "ec2-instance> show security-groups",
        ],
        "expected": "Filter to instance-specific resources",
        "actual": "Returns complete account inventory",
    },
    "issue_10": {
        "number": 10,
        "title": "ELB commands return no output",
        "status": "OPEN",
        "severity": "HIGH",
        "affected_commands": [
            "elb> show listeners",
            "elb> show targets",
            "elb> show health",
        ],
        "expected": "Display ELB listeners, targets, and health data",
        "actual": "Returns 'No data' for valid load balancers",
    },
}


# Context hierarchy
CONTEXT_HIERARCHY: Dict[str, Dict[str, Any]] = {
    None: {
        "children": [
            "global-network",
            "vpc",
            "transit-gateway",
            "firewall",
            "ec2-instance",
            "elb",
            "vpn",
        ],
    },
    "global-network": {
        "parent": None,
        "children": ["core-network"],
    },
    "core-network": {
        "parent": "global-network",
        "children": ["route-table"],
    },
    "vpc": {
        "parent": None,
        "children": ["route-table"],
    },
    "transit-gateway": {
        "parent": None,
        "children": ["route-table"],
    },
    "route-table": {
        "parent": ["vpc", "transit-gateway", "core-network"],
        "children": [],
    },
    "firewall": {
        "parent": None,
        "children": [],
    },
    "ec2-instance": {
        "parent": None,
        "children": [],
    },
    "elb": {
        "parent": None,
        "children": [],
    },
    "vpn": {
        "parent": None,
        "children": [],
    },
}


# Context-aware command behaviors
CONTEXT_AWARE_BEHAVIORS: Dict[str, Dict[str, str]] = {
    "find_prefix": {
        None: "Searches routing cache",
        "vpc": "Searches VPC route tables",
        "transit-gateway": "Searches TGW route tables",
        "core-network": "Searches CloudWAN route tables",
        "route-table": "Searches specific route table",
    },
    "find_null_routes": {
        None: "Searches routing cache for blackholes",
        "vpc": "Searches VPC route tables for blackholes",
        "transit-gateway": "Searches TGW route tables for blackholes",
        "core-network": "Searches CloudWAN for blackholes",
        "route-table": "Searches specific route table for blackholes",
    },
    "show route-tables": {
        "vpc": "Shows VPC route tables",
        "transit-gateway": "Shows TGW route tables",
        "core-network": "Shows CloudWAN route tables",
        "ec2-instance": "Shows instance-associated route tables",
    },
    "show detail": {
        "global-network": "Shows global network details",
        "core-network": "Shows core network details with policy",
        "vpc": "Shows VPC CIDR, subnets, gateways",
        "transit-gateway": "Shows TGW configuration and ASN",
        "firewall": "Shows firewall configuration",
        "ec2-instance": "Shows instance state and networking",
        "elb": "Shows load balancer configuration",
        "vpn": "Shows VPN tunnels and status",
    },
}


# Helper functions
def get_commands_for_context(context: Optional[str] = None) -> List[Command]:
    """Get all commands available in a specific context."""
    return ALL_COMMANDS.get(context, [])


def get_show_commands(context: Optional[str] = None) -> List[Command]:
    """Get only show commands for a specific context."""
    return [cmd for cmd in get_commands_for_context(context) if cmd.name.startswith("show")]


def get_set_commands(context: Optional[str] = None) -> List[Command]:
    """Get only set commands for a specific context."""
    return [cmd for cmd in get_commands_for_context(context) if cmd.name.startswith("set")]


def get_action_commands(context: Optional[str] = None) -> List[Command]:
    """Get action commands (not show/set) for a specific context."""
    commands = get_commands_for_context(context)
    return [cmd for cmd in commands if not cmd.name.startswith(("show", "set", "exit", "end", "clear", "?"))]


def get_context_entry_commands() -> List[Command]:
    """Get all commands that set a new context."""
    all_cmds = []
    for context_cmds in ALL_COMMANDS.values():
        all_cmds.extend(context_cmds)
    return [cmd for cmd in all_cmds if cmd.sets_context]


def get_commands_requiring_args() -> List[Command]:
    """Get all commands that require arguments."""
    all_cmds = []
    for context_cmds in ALL_COMMANDS.values():
        all_cmds.extend(context_cmds)
    return [cmd for cmd in all_cmds if cmd.requires_arg]


def get_context_aware_commands() -> List[Command]:
    """Get all commands with context-aware behavior."""
    all_cmds = []
    for context_cmds in ALL_COMMANDS.values():
        all_cmds.extend(context_cmds)
    return [cmd for cmd in all_cmds if cmd.context_aware]


def count_total_commands() -> int:
    """Count total unique testable commands."""
    all_cmds = []
    for context_cmds in ALL_COMMANDS.values():
        all_cmds.extend(context_cmds)
    # Deduplicate by (name, context) tuple
    unique = set((cmd.name, cmd.context) for cmd in all_cmds)
    return len(unique)


def get_issue_affected_commands(issue_key: str) -> List[str]:
    """Get list of commands affected by a known issue."""
    issue = KNOWN_ISSUES.get(issue_key, {})
    return issue.get("affected_commands", [])


# Statistics
def print_command_statistics():
    """Print comprehensive command statistics."""
    print("AWS Network Shell - Command Graph Statistics")
    print("=" * 60)
    print(f"Total Contexts: {len(ALL_COMMANDS)}")
    print(f"Total Unique Commands: {count_total_commands()}")
    print()

    for context, commands in ALL_COMMANDS.items():
        ctx_name = context or "root"
        show_cmds = [c for c in commands if c.name.startswith("show")]
        set_cmds = [c for c in commands if c.name.startswith("set")]
        action_cmds = [c for c in commands if not c.name.startswith(("show", "set", "exit", "end", "clear", "?"))]

        print(f"{ctx_name.upper()} Context:")
        print(f"  Show commands: {len(show_cmds)}")
        print(f"  Set commands: {len(set_cmds)}")
        print(f"  Action commands: {len(action_cmds)}")
        print(f"  Total: {len(commands)}")
        print()

    print(f"Context Entry Commands: {len(get_context_entry_commands())}")
    print(f"Commands Requiring Args: {len(get_commands_requiring_args())}")
    print(f"Context-Aware Commands: {len(get_context_aware_commands())}")
    print()
    print(f"Known Issues: {len(KNOWN_ISSUES)}")
    for issue_key, issue_data in KNOWN_ISSUES.items():
        print(f"  - Issue #{issue_data['number']}: {issue_data['title']}")
        print(f"    Affected Commands: {len(issue_data['affected_commands'])}")


if __name__ == "__main__":
    print_command_statistics()
