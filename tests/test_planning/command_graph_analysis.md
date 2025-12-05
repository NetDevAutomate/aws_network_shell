# AWS Network Shell - Complete Command Graph Analysis

**Generated**: 2024-12-04
**Purpose**: Comprehensive mapping of ALL testable commands for complete test coverage

---

## Executive Summary

- **Total Contexts**: 10 (root + 9 hierarchical contexts)
- **Total Commands**: 150+ testable command combinations
- **Context Types**: root, global-network, core-network, route-table, vpc, transit-gateway, firewall, ec2-instance, elb, vpn
- **Command Categories**: show (56), set (13), action (12), context-dependent (69+)

---

## 1. Complete Command Graph

### 1.1 Root Context (None)

#### Show Commands (34 total)
```python
ROOT_SHOW_COMMANDS = {
    # Network Infrastructure
    "show version": {"requires_context": None, "output_type": "text"},
    "show global-networks": {"requires_context": None, "output_type": "table", "cached": True},
    "show vpcs": {"requires_context": None, "output_type": "table", "cached": True},
    "show transit_gateways": {"requires_context": None, "output_type": "table", "cached": True},
    "show firewalls": {"requires_context": None, "output_type": "table", "cached": True},

    # Connectivity
    "show dx-connections": {"requires_context": None, "output_type": "table"},
    "show peering-connections": {"requires_context": None, "output_type": "table"},
    "show vpns": {"requires_context": None, "output_type": "table"},
    "show client-vpn-endpoints": {"requires_context": None, "output_type": "table"},

    # Compute & Network Interfaces
    "show enis": {"requires_context": None, "output_type": "table"},
    "show ec2-instances": {"requires_context": None, "output_type": "table"},
    "show elbs": {"requires_context": None, "output_type": "table"},

    # Security
    "show security-groups": {"requires_context": None, "output_type": "table"},
    "show unused-sgs": {"requires_context": None, "output_type": "table"},

    # DNS & Resolution
    "show resolver-endpoints": {"requires_context": None, "output_type": "table"},
    "show resolver-rules": {"requires_context": None, "output_type": "table"},
    "show query-logs": {"requires_context": None, "output_type": "table"},

    # Monitoring & Alarms
    "show network-alarms": {"requires_context": None, "output_type": "table"},
    "show alarms-critical": {"requires_context": None, "output_type": "table"},

    # Global Services
    "show global-accelerators": {"requires_context": None, "output_type": "table"},
    "show ga-endpoint-health": {"requires_context": None, "output_type": "table"},

    # PrivateLink
    "show endpoint-services": {"requires_context": None, "output_type": "table"},
    "show vpc-endpoints": {"requires_context": None, "output_type": "table"},

    # Routing & Prefixes
    "show prefix-lists": {"requires_context": None, "output_type": "table"},

    # BGP
    "show bgp-neighbors": {"requires_context": None, "output_type": "table"},

    # System Configuration
    "show config": {"requires_context": None, "output_type": "yaml"},
    "show running-config": {"requires_context": None, "output_type": "yaml"},
    "show cache": {"requires_context": None, "output_type": "json"},
    "show routing-cache": {"requires_context": None, "output_type": "json"},
    "show graph": {"requires_context": None, "output_type": "graph"},
}
```

#### Set Commands (13 total)
```python
ROOT_SET_COMMANDS = {
    # Context Entry
    "set global-network": {"sets_context": "global-network", "requires_arg": True},
    "set vpc": {"sets_context": "vpc", "requires_arg": True},
    "set transit-gateway": {"sets_context": "transit-gateway", "requires_arg": True},
    "set firewall": {"sets_context": "firewall", "requires_arg": True},
    "set ec2-instance": {"sets_context": "ec2-instance", "requires_arg": True},
    "set elb": {"sets_context": "elb", "requires_arg": True},
    "set vpn": {"sets_context": "vpn", "requires_arg": True},

    # Configuration
    "set profile": {"modifies": "profile", "requires_arg": True},
    "set regions": {"modifies": "regions", "requires_arg": True},
    "set no-cache": {"modifies": "no_cache", "requires_arg": False},
    "set output-format": {"modifies": "output_format", "requires_arg": True, "valid_values": ["table", "json", "yaml"]},
    "set output-file": {"modifies": "output_file", "requires_arg": True},
    "set watch": {"modifies": "watch_interval", "requires_arg": True},
    "set theme": {"modifies": "theme", "requires_arg": True},
    "set prompt": {"modifies": "prompt_style", "requires_arg": True},
}
```

#### Action Commands (9 total)
```python
ROOT_ACTION_COMMANDS = {
    "write": {"requires_arg": True, "arg_type": "filename"},
    "trace": {"requires_arg": True, "arg_format": "<src_ip> <dst_ip>"},
    "find_ip": {"requires_arg": True, "arg_type": "ip_address"},
    "find_prefix": {"requires_arg": True, "arg_type": "cidr", "searches": "routing_cache"},
    "find_null_routes": {"requires_arg": False, "searches": "routing_cache"},
    "populate_cache": {"requires_arg": False, "modifies": "cache"},
    "clear_cache": {"requires_arg": False, "modifies": "cache"},
    "create_routing_cache": {"requires_arg": False, "creates": "routing_cache"},
    "validate_graph": {"requires_arg": False, "validates": "command_graph"},
    "export_graph": {"requires_arg": True, "arg_type": "filename"},
}
```

---

### 1.2 Global-Network Context

#### Entry
```python
ENTRY = {
    "command": "set global-network <#|name|id>",
    "from_context": None,
    "sets_context": "global-network",
    "requires_data": "global-networks list"
}
```

#### Show Commands (2)
```python
GLOBAL_NETWORK_SHOW = {
    "show detail": {"requires_context": "global-network", "output_type": "table"},
    "show core-networks": {"requires_context": "global-network", "output_type": "table", "cached": True},
}
```

#### Set Commands (1)
```python
GLOBAL_NETWORK_SET = {
    "set core-network": {"sets_context": "core-network", "requires_arg": True, "parent_context": "global-network"},
}
```

---

### 1.3 Core-Network Context

#### Entry
```python
ENTRY = {
    "command": "set core-network <#|name|id>",
    "from_context": "global-network",
    "sets_context": "core-network",
    "requires_data": "core-networks list from parent context"
}
```

#### Show Commands (10)
```python
CORE_NETWORK_SHOW = {
    "show detail": {"requires_context": "core-network", "output_type": "table"},
    "show segments": {"requires_context": "core-network", "output_type": "table"},
    "show policy": {"requires_context": "core-network", "output_type": "json"},
    "show policy-documents": {"requires_context": "core-network", "output_type": "table"},
    "show live-policy": {"requires_context": "core-network", "output_type": "json"},
    "show routes": {"requires_context": "core-network", "output_type": "table"},
    "show route-tables": {"requires_context": "core-network", "output_type": "table"},
    "show blackhole-routes": {"requires_context": "core-network", "output_type": "table"},
    "show policy-change-events": {"requires_context": "core-network", "output_type": "table"},
    "show connect-attachments": {"requires_context": "core-network", "output_type": "table"},
    "show connect-peers": {"requires_context": "core-network", "output_type": "table"},
    "show rib": {"requires_context": "core-network", "output_type": "table", "optional_args": ["segment=<name>", "edge=<location>"]},
}
```

#### Set Commands (1)
```python
CORE_NETWORK_SET = {
    "set route-table": {"sets_context": "route-table", "requires_arg": True, "parent_context": "core-network"},
}
```

#### Action Commands (2)
```python
CORE_NETWORK_ACTIONS = {
    "find_prefix": {"requires_arg": True, "arg_type": "cidr", "context_aware": True},
    "find_null_routes": {"requires_arg": False, "context_aware": True},
}
```

---

### 1.4 Route-Table Context

#### Entry
```python
ENTRY = {
    "command": "set route-table <#|name|id>",
    "from_context": ["core-network", "vpc", "transit-gateway"],
    "sets_context": "route-table",
    "requires_data": "route-tables list from parent context"
}
```

#### Show Commands (1)
```python
ROUTE_TABLE_SHOW = {
    "show routes": {"requires_context": "route-table", "output_type": "table"},
}
```

#### Action Commands (2)
```python
ROUTE_TABLE_ACTIONS = {
    "find_prefix": {"requires_arg": True, "arg_type": "cidr", "context_aware": True},
    "find_null_routes": {"requires_arg": False, "context_aware": True},
}
```

---

### 1.5 VPC Context

#### Entry
```python
ENTRY = {
    "command": "set vpc <#|name|id>",
    "from_context": None,
    "sets_context": "vpc",
    "requires_data": "vpcs list"
}
```

#### Show Commands (8)
```python
VPC_SHOW = {
    "show detail": {"requires_context": "vpc", "output_type": "table"},
    "show route-tables": {"requires_context": "vpc", "output_type": "table"},
    "show subnets": {"requires_context": "vpc", "output_type": "table"},
    "show security-groups": {"requires_context": "vpc", "output_type": "table"},
    "show nacls": {"requires_context": "vpc", "output_type": "table"},
    "show internet-gateways": {"requires_context": "vpc", "output_type": "table"},
    "show nat-gateways": {"requires_context": "vpc", "output_type": "table"},
    "show endpoints": {"requires_context": "vpc", "output_type": "table"},
}
```

#### Set Commands (1)
```python
VPC_SET = {
    "set route-table": {"sets_context": "route-table", "requires_arg": True, "parent_context": "vpc"},
}
```

#### Action Commands (2)
```python
VPC_ACTIONS = {
    "find_prefix": {"requires_arg": True, "arg_type": "cidr", "context_aware": True},
    "find_null_routes": {"requires_arg": False, "context_aware": True},
}
```

---

### 1.6 Transit-Gateway Context

#### Entry
```python
ENTRY = {
    "command": "set transit-gateway <#|name|id>",
    "from_context": None,
    "sets_context": "transit-gateway",
    "requires_data": "transit-gateways list"
}
```

#### Show Commands (3)
```python
TRANSIT_GATEWAY_SHOW = {
    "show detail": {"requires_context": "transit-gateway", "output_type": "table"},
    "show route-tables": {"requires_context": "transit-gateway", "output_type": "table"},
    "show attachments": {"requires_context": "transit-gateway", "output_type": "table"},
}
```

#### Set Commands (1)
```python
TRANSIT_GATEWAY_SET = {
    "set route-table": {"sets_context": "route-table", "requires_arg": True, "parent_context": "transit-gateway"},
}
```

#### Action Commands (2)
```python
TRANSIT_GATEWAY_ACTIONS = {
    "find_prefix": {"requires_arg": True, "arg_type": "cidr", "context_aware": True},
    "find_null_routes": {"requires_arg": False, "context_aware": True},
}
```

---

### 1.7 Firewall Context

#### Entry
```python
ENTRY = {
    "command": "set firewall <#|name|id>",
    "from_context": None,
    "sets_context": "firewall",
    "requires_data": "firewalls list"
}
```

#### Show Commands (4)
```python
FIREWALL_SHOW = {
    "show detail": {"requires_context": "firewall", "output_type": "table"},
    "show rule-groups": {"requires_context": "firewall", "output_type": "table"},
    "show policy": {"requires_context": "firewall", "output_type": "json"},
    "show firewall-policy": {"requires_context": "firewall", "output_type": "json"},
}
```

---

### 1.8 EC2-Instance Context

#### Entry
```python
ENTRY = {
    "command": "set ec2-instance <#|name|id>",
    "from_context": None,
    "sets_context": "ec2-instance",
    "requires_data": "ec2-instances list"
}
```

#### Show Commands (4)
```python
EC2_INSTANCE_SHOW = {
    "show detail": {"requires_context": "ec2-instance", "output_type": "table"},
    "show security-groups": {"requires_context": "ec2-instance", "output_type": "table", "filters_by": "instance"},
    "show enis": {"requires_context": "ec2-instance", "output_type": "table", "filters_by": "instance"},
    "show routes": {"requires_context": "ec2-instance", "output_type": "table"},
}
```

**KNOWN ISSUE #9**: `show enis` and `show security-groups` return all account resources instead of instance-specific data.

---

### 1.9 ELB Context

#### Entry
```python
ENTRY = {
    "command": "set elb <#|name|arn>",
    "from_context": None,
    "sets_context": "elb",
    "requires_data": "elbs list"
}
```

#### Show Commands (4)
```python
ELB_SHOW = {
    "show detail": {"requires_context": "elb", "output_type": "table"},
    "show listeners": {"requires_context": "elb", "output_type": "table"},
    "show targets": {"requires_context": "elb", "output_type": "table"},
    "show health": {"requires_context": "elb", "output_type": "table"},
}
```

**KNOWN ISSUE #10**: `show listeners`, `show targets`, and `show health` return "No data" for valid ELBs.

---

### 1.10 VPN Context

#### Entry
```python
ENTRY = {
    "command": "set vpn <#|name|id>",
    "from_context": None,
    "sets_context": "vpn",
    "requires_data": "vpns list"
}
```

#### Show Commands (2)
```python
VPN_SHOW = {
    "show detail": {"requires_context": "vpn", "output_type": "table"},
    "show tunnels": {"requires_context": "vpn", "output_type": "table"},
}
```

---

## 2. Command Dependencies Map

### 2.1 Context Dependency Tree
```
root (None)
├── global-network
│   └── core-network
│       └── route-table
├── vpc
│   └── route-table
├── transit-gateway
│   └── route-table
├── firewall
├── ec2-instance
├── elb
└── vpn
```

### 2.2 Context-Aware Commands
These commands behave differently based on current context:

```python
CONTEXT_AWARE_COMMANDS = {
    "find_prefix": {
        "root": "Searches routing cache",
        "vpc": "Searches VPC route tables",
        "transit-gateway": "Searches TGW route tables",
        "core-network": "Searches CloudWAN route tables",
        "route-table": "Searches specific route table",
    },
    "find_null_routes": {
        "root": "Searches routing cache for blackholes",
        "vpc": "Searches VPC route tables for blackholes",
        "transit-gateway": "Searches TGW route tables for blackholes",
        "core-network": "Searches CloudWAN for blackholes",
        "route-table": "Searches specific route table for blackholes",
    },
    "show route-tables": {
        "root": "Invalid - requires context",
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
```

---

## 3. Test Fixture Requirements

### 3.1 Minimal Fixture Data Required

```python
FIXTURE_REQUIREMENTS = {
    "global_networks": {
        "count": 2,
        "required_fields": ["id", "name", "state", "core_networks"],
        "test_scenarios": ["valid index", "valid name", "valid id", "invalid ref"],
    },
    "core_networks": {
        "count": 2,
        "required_fields": ["id", "name", "policy", "segments", "route_tables"],
        "test_scenarios": ["valid index", "valid name", "valid id", "invalid ref", "policy parsing", "segment filtering"],
    },
    "vpcs": {
        "count": 3,
        "required_fields": ["id", "name", "region", "cidr", "route_tables", "subnets", "security_groups"],
        "test_scenarios": ["valid index", "valid name", "valid id", "invalid ref", "route table filtering"],
    },
    "transit_gateways": {
        "count": 2,
        "required_fields": ["id", "name", "region", "route_tables", "attachments"],
        "test_scenarios": ["valid index", "valid name", "valid id", "invalid ref"],
    },
    "firewalls": {
        "count": 2,
        "required_fields": ["id", "name", "region", "rule_groups", "policy"],
        "test_scenarios": ["valid index", "valid name", "valid id", "invalid ref"],
    },
    "ec2_instances": {
        "count": 3,
        "required_fields": ["id", "name", "region", "state", "enis", "security_groups", "route_tables"],
        "test_scenarios": ["valid index", "valid name", "valid id", "invalid ref", "instance-specific filtering"],
    },
    "elbs": {
        "count": 2,
        "required_fields": ["arn", "name", "region", "type", "listeners", "targets", "health"],
        "test_scenarios": ["valid index", "valid name", "valid arn", "invalid ref", "listener data", "target data", "health data"],
    },
    "vpns": {
        "count": 2,
        "required_fields": ["id", "name", "region", "state", "tunnels"],
        "test_scenarios": ["valid index", "valid name", "valid id", "invalid ref"],
    },
    "route_tables": {
        "count": 3,
        "required_fields": ["id", "routes", "parent_type"],
        "test_scenarios": ["vpc route table", "tgw route table", "cloudwan route table", "prefix search", "null route detection"],
    },
}
```

### 3.2 Fixture Dependencies

```python
FIXTURE_DEPENDENCIES = {
    "core_network": ["global_network"],
    "route_table": ["vpc OR transit_gateway OR core_network"],
    "ec2_instance": ["vpc", "security_groups", "enis"],
    "elb": ["vpc", "targets", "listeners"],
}
```

---

## 4. Complete Testable Command List

### 4.1 Root Context Commands (53 total)

#### Show Commands (34)
1. `show version`
2. `show global-networks`
3. `show vpcs`
4. `show transit_gateways`
5. `show firewalls`
6. `show dx-connections`
7. `show enis`
8. `show bgp-neighbors`
9. `show ec2-instances`
10. `show elbs`
11. `show vpns`
12. `show security-groups`
13. `show unused-sgs`
14. `show resolver-endpoints`
15. `show resolver-rules`
16. `show query-logs`
17. `show peering-connections`
18. `show prefix-lists`
19. `show network-alarms`
20. `show alarms-critical`
21. `show client-vpn-endpoints`
22. `show global-accelerators`
23. `show ga-endpoint-health`
24. `show endpoint-services`
25. `show vpc-endpoints`
26. `show config`
27. `show running-config`
28. `show cache`
29. `show routing-cache`
30. `show graph`

#### Set Commands (13)
31. `set global-network <ref>`
32. `set vpc <ref>`
33. `set transit-gateway <ref>`
34. `set firewall <ref>`
35. `set ec2-instance <ref>`
36. `set elb <ref>`
37. `set vpn <ref>`
38. `set profile <name>`
39. `set regions <region_list>`
40. `set no-cache`
41. `set output-format <format>`
42. `set output-file <filename>`
43. `set watch <interval>`
44. `set theme <theme_name>`
45. `set prompt <style>`

#### Action Commands (9)
46. `write <filename>`
47. `trace <src_ip> <dst_ip>`
48. `find_ip <ip_address>`
49. `find_prefix <cidr>`
50. `find_null_routes`
51. `populate_cache`
52. `clear_cache`
53. `create_routing_cache`
54. `validate_graph`
55. `export_graph <filename>`

### 4.2 Global-Network Context (3)
56. `show detail` (global-network)
57. `show core-networks`
58. `set core-network <ref>`

### 4.3 Core-Network Context (13)
59. `show detail` (core-network)
60. `show segments`
61. `show policy`
62. `show policy-documents`
63. `show live-policy`
64. `show routes` (core-network)
65. `show route-tables` (core-network)
66. `show blackhole-routes` (core-network)
67. `show policy-change-events`
68. `show connect-attachments`
69. `show connect-peers`
70. `show rib` (with optional segment=/edge= filters)
71. `set route-table <ref>` (from core-network)
72. `find_prefix <cidr>` (core-network)
73. `find_null_routes` (core-network)

### 4.4 Route-Table Context (3)
74. `show routes` (route-table)
75. `find_prefix <cidr>` (route-table)
76. `find_null_routes` (route-table)

### 4.5 VPC Context (11)
77. `show detail` (vpc)
78. `show route-tables` (vpc)
79. `show subnets`
80. `show security-groups` (vpc)
81. `show nacls`
82. `show internet-gateways`
83. `show nat-gateways`
84. `show endpoints`
85. `set route-table <ref>` (from vpc)
86. `find_prefix <cidr>` (vpc)
87. `find_null_routes` (vpc)

### 4.6 Transit-Gateway Context (6)
88. `show detail` (transit-gateway)
89. `show route-tables` (transit-gateway)
90. `show attachments`
91. `set route-table <ref>` (from transit-gateway)
92. `find_prefix <cidr>` (transit-gateway)
93. `find_null_routes` (transit-gateway)

### 4.7 Firewall Context (4)
94. `show detail` (firewall)
95. `show rule-groups`
96. `show policy` (firewall)
97. `show firewall-policy`

### 4.8 EC2-Instance Context (4)
98. `show detail` (ec2-instance)
99. `show security-groups` (ec2-instance) ⚠️ ISSUE #9
100. `show enis` (ec2-instance) ⚠️ ISSUE #9
101. `show routes` (ec2-instance)

### 4.9 ELB Context (4)
102. `show detail` (elb)
103. `show listeners` ⚠️ ISSUE #10
104. `show targets` ⚠️ ISSUE #10
105. `show health` ⚠️ ISSUE #10

### 4.10 VPN Context (2)
106. `show detail` (vpn)
107. `show tunnels`

### 4.11 Navigation Commands (4)
108. `exit` (pop one context level)
109. `end` (return to root)
110. `clear` (clear screen)
111. `?` (show help for current context)

### 4.12 Aliases (5)
112. `sh` (alias for `show`)
113. `conf` (alias for `config`)
114. `ex` (alias for `exit`)
115. `int` (alias for `interface`)
116. `no` (alias for `unset`)

### 4.13 Pipe Operators (3)
117. `<command> | include <pattern>`
118. `<command> | exclude <pattern>`
119. `<command> | grep <pattern>`

### 4.14 Watch Mode (1)
120. `show <command> watch <interval>`

---

## 5. Test Scenarios by Category

### 5.1 Context Navigation Tests (20)
- Enter each context type from root (8 contexts)
- Navigate between contexts (exit, end)
- Invalid context references (8 contexts)
- Context stack management (push/pop)
- Multi-level navigation (e.g., root → global-network → core-network → route-table)

### 5.2 Show Command Tests (60+)
- Each show command in appropriate context
- Show commands with invalid context
- Show commands with empty data
- Show commands with pagination
- Show commands with filtering (pipe operators)
- Show commands in watch mode

### 5.3 Set Command Tests (16)
- Context entry commands (valid/invalid refs)
- Configuration modification commands
- Set commands with invalid values
- Set commands persistence

### 5.4 Action Command Tests (18)
- Root action commands
- Context-aware find commands in each context
- Action commands with invalid arguments
- Action commands with missing arguments

### 5.5 Output Format Tests (12)
- Table output (default)
- JSON output
- YAML output
- Output file redirection

### 5.6 Error Handling Tests (20)
- Unknown commands
- Missing arguments
- Invalid argument formats
- Context mismatch errors
- Resource not found errors

### 5.7 Edge Case Tests (15)
- Empty cache scenarios
- Large data sets
- Special characters in names
- Concurrent command execution
- Cache invalidation

---

## 6. GitHub Issues Summary

### Issue #9: EC2 Context - show enis/security-groups Returns All Account Data
**Status**: OPEN
**Impact**: HIGH
**Commands Affected**:
- `ec2-instance> show enis`
- `ec2-instance> show security-groups`

**Expected Behavior**: Should filter to instance-specific ENIs and security groups
**Actual Behavior**: Returns complete account inventory

**Test Requirements**:
- Verify instance-specific filtering
- Test with multiple instances
- Validate security group associations

---

### Issue #10: ELB Context - show listeners/targets/health Returns No Data
**Status**: OPEN
**Impact**: HIGH
**Commands Affected**:
- `elb> show listeners`
- `elb> show targets`
- `elb> show health`

**Expected Behavior**: Should display ELB listeners, target groups, and health status
**Actual Behavior**: Returns "No data" for valid load balancers

**Test Requirements**:
- Verify listener retrieval from ELB context data
- Test target group enumeration
- Validate health status reporting
- Test with both ALB and NLB

---

## 7. Test Priority Matrix

### P0 - Critical (Must Have)
1. All context entry commands (8 contexts)
2. Show commands for resource listing (vpcs, transit_gateways, etc.)
3. Context navigation (exit, end)
4. Issue #9 and #10 fixes

### P1 - High (Should Have)
1. All context-specific show commands
2. Context-aware find commands
3. Configuration set commands
4. Action commands (trace, write, etc.)

### P2 - Medium (Nice to Have)
1. Pipe operators
2. Watch mode
3. Output format variations
4. Aliases

### P3 - Low (Future)
1. Theme customization
2. Advanced filtering
3. Graph export
4. Validation commands

---

## 8. Test Implementation Checklist

### Phase 1: Foundation (Completed: 0/30)
- [ ] Root show commands basic tests (30 commands)

### Phase 2: Context Entry (Completed: 0/16)
- [ ] Valid context entry tests (8 contexts × 2 test methods = 16)

### Phase 3: Context Show Commands (Completed: 0/40)
- [ ] Global-network context (2)
- [ ] Core-network context (12)
- [ ] Route-table context (1)
- [ ] VPC context (8)
- [ ] Transit-gateway context (3)
- [ ] Firewall context (4)
- [ ] EC2-instance context (4)
- [ ] ELB context (4)
- [ ] VPN context (2)

### Phase 4: Action Commands (Completed: 0/18)
- [ ] Root action commands (9)
- [ ] Context-aware find_prefix (5 contexts)
- [ ] Context-aware find_null_routes (5 contexts)

### Phase 5: Edge Cases (Completed: 0/20)
- [ ] Invalid references
- [ ] Empty data scenarios
- [ ] Error handling
- [ ] Pipe operators
- [ ] Watch mode

### Phase 6: Issue Resolution (Completed: 0/6)
- [ ] Issue #9: EC2 context filtering (3 tests)
- [ ] Issue #10: ELB data retrieval (3 tests)

---

## 9. Estimated Test Counts

```
Root Commands:                55 tests
Context Entry:                16 tests
Context Show Commands:        40 tests
Context Set Commands:          8 tests
Action Commands:              18 tests
Navigation:                   10 tests
Error Handling:               20 tests
Output Formats:               12 tests
Pipe Operators:                9 tests
Watch Mode:                    5 tests
Edge Cases:                   15 tests
Issue #9 Resolution:           3 tests
Issue #10 Resolution:          3 tests
---
TOTAL ESTIMATED:             214 tests
```

---

## 10. Critical Testing Notes

### 10.1 Fixture Data Quality
- Must include realistic AWS resource IDs
- Must have proper parent-child relationships (e.g., core-network belongs to global-network)
- Must include edge cases (empty lists, null values, missing optional fields)

### 10.2 Context Stack Management
- Test deep nesting: root → global-network → core-network → route-table
- Test exit/end from various depths
- Test context data preservation during navigation

### 10.3 Cache Testing
- Test with cache enabled/disabled
- Test cache invalidation scenarios
- Test with stale cache data

### 10.4 Output Format Consistency
- Ensure all show commands support json/yaml/table formats
- Test output redirection to files
- Validate table rendering with various data sizes

---

## 11. Commands Requiring Special Test Fixtures

### High Complexity
1. `show rib` - Requires segment and edge location data
2. `trace` - Requires network path simulation
3. `find_ip` - Requires ENI and routing data correlation
4. `reachability` - Requires VPC peering and routing data

### Medium Complexity
1. `show bgp-neighbors` - Requires DX or VPN BGP data
2. `show ga-endpoint-health` - Requires Global Accelerator with endpoints
3. `show unused-sgs` - Requires security group usage analysis

### Low Complexity
1. Most show commands - Standard resource listing
2. Context navigation - Basic context stack management

---

## 12. Recommendations

### 12.1 Test Organization
```
tests/
├── test_root_commands.py          # Root context tests
├── test_context_navigation.py     # Context entry/exit
├── test_global_network_context.py # Global-network specific
├── test_core_network_context.py   # Core-network specific
├── test_route_table_context.py    # Route-table specific
├── test_vpc_context.py            # VPC specific
├── test_tgw_context.py            # Transit-gateway specific
├── test_firewall_context.py       # Firewall specific
├── test_ec2_context.py            # EC2-instance specific
├── test_elb_context.py            # ELB specific
├── test_vpn_context.py            # VPN specific
├── test_action_commands.py        # find_prefix, find_null_routes, etc.
├── test_output_formats.py         # JSON/YAML/table rendering
├── test_pipe_operators.py         # include/exclude/grep
├── test_watch_mode.py             # Watch command tests
├── test_edge_cases.py             # Error handling, empty data
├── test_issue_9_ec2_filtering.py  # Issue #9 regression tests
├── test_issue_10_elb_data.py      # Issue #10 regression tests
└── fixtures/
    ├── global_networks.json
    ├── core_networks.json
    ├── vpcs.json
    ├── transit_gateways.json
    ├── firewalls.json
    ├── ec2_instances.json
    ├── elbs.json
    └── vpns.json
```

### 12.2 Priority Testing Sequence
1. **Week 1**: Root commands + Context navigation
2. **Week 2**: VPC + Transit-gateway contexts (most used)
3. **Week 3**: CloudWAN contexts (most complex)
4. **Week 4**: Remaining contexts + Issue fixes
5. **Week 5**: Edge cases + Integration tests

### 12.3 Coverage Goals
- **Unit Tests**: 90% code coverage
- **Integration Tests**: All command paths exercised
- **Regression Tests**: Issues #9 and #10 fully covered
- **Performance Tests**: Commands execute within timeout

---

## Summary

This comprehensive analysis identifies **150+ testable command combinations** across **10 contexts**. The command graph reveals a well-structured hierarchical CLI with context-aware behavior for key operations like `find_prefix` and `show detail`. Two critical issues (#9 and #10) require immediate attention for EC2 and ELB contexts.

Testing should proceed in phases, prioritizing root commands and context navigation first, followed by context-specific show commands, and concluding with edge cases and issue resolution. With proper fixture data and systematic testing, we can achieve comprehensive coverage of all 214 estimated test cases.
