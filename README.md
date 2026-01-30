# AWS Network Shell

**AWS Network Tools CLI - A hierarchical CLI for AWS networking**

## 🌟 Overview

AWS Network Shell provides a comprehensive CLI for managing AWS networking resources with a familiar Cisco IOS-style interface. Navigate through contexts (VPC, Transit Gateway, Firewall, etc.) and execute commands with hierarchical command structures.

## 🚀 Quick Start

```bash
# Install
pip install -e .

# Launch shell
aws-net-shell

# Or with AWS profile
aws-net-shell -p production

# Run automated workflows
aws-net-runner "show vpcs" "set vpc 1" "show subnets"

# Debug mode for troubleshooting
aws-net-runner --debug "show vpns" "set vpn 1" "show tunnels"
# Logs to: /tmp/aws_net_runner_debug_<timestamp>.log
```

## 📊 Command Hierarchy

The CLI uses a hierarchical command structure with **10 contexts** and **100+ commands**.

### Graph Commands

Explore and validate the command hierarchy:

```bash
# Show command tree
aws-net> show graph

# Show statistics
aws-net> show graph stats
  Total nodes: 103
  Total edges: 145
  Contexts: 10
  Command paths: 78
  Implemented: 100%

# Validate all handlers exist
aws-net> show graph validate
✓ Graph is valid - all handlers implemented

# Export Mermaid diagram
aws-net> show graph mermaid

# Find path to specific command
aws-net> show graph parent find-prefix
Paths to 'find-prefix':
✓ find-prefix
  Context: route-table
  Path: show route-tables → set route-table 1 → find-prefix
```

### Available Graph Operations

- `show graph` - Display command tree structure
- `show graph stats` - Show command statistics
- `show graph validate` - Verify all handlers implemented
- `show graph mermaid` - Generate Mermaid diagram
- `show graph parent <command>` - Show navigation path to command
- `validate-graph` - Run full validation check
- `export-graph [filename]` - Export to markdown file

## 🔥 Network Firewall Commands

Complete AWS Network Firewall inspection and management:

```bash
# List all firewalls
aws-net> show firewalls

# Enter firewall context
aws-net> set firewall 1
aws-net>fi:1>

# Show firewall overview with rule groups
aws-net>fi:1> show firewall
🔥 Network Firewall: prod-firewall-1
├── ID: 12345678-1234-1234-1234-123456789abc
├── Region: us-east-1
├── VPC: vpc-0123456789abcdef0
└── Subnets: subnet-0a1b2c3d4e5f67890, subnet-0f9e8d7c6b5a43210

Rule Groups
┏━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━┓
┃ # ┃ Name                 ┃ Type      ┃ Rules ┃ Capacity ┃
┡━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━┩
│ 1 │ drop-remote-outbound │ STATELESS │     2 │      2/2 │
│ 2 │ allow-domains        │ STATEFUL  │     2 │    2/100 │
└───┴──────────────────────┴───────────┴───────┴──────────┘

# Show policy with rule groups
aws-net>fi:1> show policy

# Show rule groups (with selection index)
aws-net>fi:1> show rule-groups

# Enter rule group context
aws-net>fi:1> set rule-group 1
aws-net>fi:1>ru:1>

# Show detailed rules (STATELESS)
aws-net>fi:1>ru:1> show rule-group
┏━━━┳━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ # ┃ Priority ┃ Actions  ┃ Sources   ┃ Destinations ┃ Protocols ┃ Source Ports ┃ Dest Ports ┃
┡━━━╇━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 1 │        1 │ aws:drop │ 0.0.0.0/0 │ 0.0.0.0/0    │ 6         │ 22           │ 22         │
│ 2 │        2 │ aws:drop │ 0.0.0.0/0 │ 0.0.0.0/0    │ 27        │ Any          │ Any        │
└───┴──────────┴──────────┴───────────┴──────────────┴───────────┴──────────────┴────────────┘

# Show detailed rules (STATEFUL with Suricata format)
aws-net>fi:1> set rule-group 2
aws-net>fi:1>ru:2> show rule-group
  1. pass tcp any any <> $EXTERNAL_NET 443 (msg:"Allowing TCP in port 443"; flow:not_established; sid:892123; rev:1;)
  2. pass tls any any -> $EXTERNAL_NET 443 (tls.sni; dotprefix; content:".amazon.com"; endswith; msg:"Allowing .amazon.com HTTPS requests"; sid:892125; rev:1;)
```

### Firewall Commands Summary

- **Contexts**: firewall → rule-group (2-level hierarchy)
- **Commands**: show firewall, show rule-groups, show policy, set rule-group, show rule-group
- **Display**: Complete rule details including ports, protocols, actions, and Suricata rules
- **Navigation**: Index-based selection for easy context switching

## 🔌 VPN Commands

Complete Site-to-Site VPN tunnel inspection and management:

```bash
# List all VPN connections
aws-net> show vpns
                                 Site-to-Site VPN Connections
┏━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━┓
┃ # ┃ Name           ┃ ID              ┃ State     ┃ Type    ┃ Region    ┃
┡━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━┩
│ 1 │ corporate-vpn  │ vpn-0abcdef123… │ available │ ipsec.1 │ us-east-1 │
└───┴────────────────┴─────────────────┴───────────┴─────────┴───────────┘

# Enter VPN context
aws-net> set vpn 1
aws-net>vp:1>

# Show VPN overview with tunnel summary
aws-net>vp:1> show detail
       VPN: corporate-vpn
┏━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Field ┃ Value                 ┃
┡━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━┩
│ id    │ vpn-0abcdef123456789a │
│ state │ available             │
│ type  │ ipsec.1               │
└───────┴───────────────────────┘

Tunnels (2):
  UP 203.0.113.10
  UP 203.0.113.20

# Show detailed tunnel status
aws-net>vp:1> show tunnels
            VPN Tunnels: corporate-vpn
┏━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Outside IP   ┃ Status ┃ Status Message ┃ Routes ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ 203.0.113.10 │ UP     │ 3 BGP ROUTES   │      3 │
│ 203.0.113.20 │ UP     │ 3 BGP ROUTES   │      3 │
└──────────────┴────────┴────────────────┴────────┘
```

### VPN Commands Summary

- **Context**: vpn (1-level hierarchy)
- **Commands**: show detail, show tunnels
- **Display**: IPSec tunnel status with outside IPs, BGP route counts, status messages
- **Status Colors**: Green (UP), Red (DOWN) for immediate visual identification
- **Data Source**: AWS VgwTelemetry with tunnel health and BGP session information

## 📁 Repository Structure

```
aws_net_shell/
├── src/
│   └── aws_network_tools/
│       ├── cli.py                    # CLI entry point
│       ├── core/                     # Core functionality
│       │   ├── base.py              # Base shell class
│       │   ├── graph.py             # Command graph logic
│       │   ├── ip_resolver.py       # IP address resolution
│       │   ├── spinner.py           # Loading spinners
│       │   └── renderer.py          # Output rendering
│       ├── models/                   # Data models
│       ├── modules/                  # AWS service modules
│       ├── shell/                   # Shell implementation
│       │   ├── base.py              # Base shell handlers
│       │   ├── graph.py             # Graph command implementation
│       │   ├── handlers/            # Command handlers by context
│       │   └── main.py              # Main shell entry
│       └── traceroute/              # Traceroute functionality
├── tests/                           # Test suite
│   ├── conftest.py                 # Pytest fixtures
│   ├── test_shell.py               # Shell tests
│   └── test_*.py                   # Unit tests
├── docs/                           # Documentation
│   ├── command-hierarchy-split.md  # Split command diagrams
│   ├── command-hierarchy-flow.md   # Context flow diagrams
│   └── README.md                   # This file
├── README.md                      # Main documentation
├── pyproject.toml                 # Project configuration
└── quick_test.sh                  # Quick test script
```

## 🚀 Installation & Setup

```bash
# Clone repository
cd /Users/taylaand/code/personal/aws_net_shell

# Install dependencies
pip install -e .

# Run AWS network shell
aws-net-shell

# Or with specific profile
aws-net-shell -p production
```

## 🧪 Testing

### Run Tests

```bash
# Run all unit tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Quick test script
./quick_test.sh
```

### Test Coverage

- **Root commands**: 42 commands
- **Context commands**: 35+ commands
- **Total coverage**: 77+ commands
- **Contexts**: 9 (global-network, vpc, transit-gateway, firewall, ec2-instance, elb, vpn, core-network, route-table)

## 📖 Usage Examples

### Basic Commands

```bash
aws-net> show vpcs
aws-net> show global-networks
aws-net> set vpc 1
aws-net> show detail
```

### Context Navigation

```bash
# Enter VPC context
aws-net> set vpc 1
vpc> show subnets
vpc> show route-tables
vpc> exit

# Enter Transit Gateway context
aws-net> set transit-gateway 1
tgw> show attachments
tgw> show route-tables
tgw> exit
```

### AWS Operations

```bash
# Trace between IPs
aws-net> trace 192.168.1.10 10.0.0.5

# Find IP address
aws-net> find_ip 10.1.32.100

# Find null routes
aws-net> find_null_routes
```

### Cache Management

```bash
# Scenario: ELBs haven't finished provisioning yet
aws-net> show elbs
No load balancers found

# Wait for provisioning, then refresh cache
aws-net> refresh elb
Refreshed elb cache

# Now re-fetch will get latest data
aws-net> show elbs
┏━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ # ┃ Name      ┃ Type        ┃ State   ┃
┡━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━┩
│ 1 │ prod-alb  │ application │ active  │
└───┴───────────┴─────────────┴─────────┘

# Refresh current context data (when inside a context)
aws-net> set elb 1
elb:1> refresh
Refreshed elb cache

# Clear all caches
aws-net> refresh all
Cleared 5 cache entries
```

## 📊 Commands by Category

### Cache Management (2)

- `clear_cache` - Clear all cached data permanently
- `refresh [target|all]` - Refresh cached data selectively
  - `refresh` - Refresh current context (e.g., in ELB context, clears ELB cache)
  - `refresh elb` - Clear and re-fetch ELB data on next `show elbs`
  - `refresh vpcs` - Clear and re-fetch VPC data
  - `refresh all` - Clear all caches globally

### Show Commands (34)

- Network Resources: `vpcs`, `transit_gateways`, `firewalls`, `elbs`, `vpns`
- Compute: `ec2-instances`, `enis`
- Connectivity: `dx-connections`, `peering-connections`
- Security: `security-groups`, `rule-groups`, `unused-sgs`
- DNS: `resolver-endpoints`, `resolver-rules`
- Monitoring: `network-alarms`, `alarms-critical`
- Global: `global-networks`, `global-accelerators`
- System: `config`, `cache`, `routing-cache`

### Set Commands (8 Contexts)

- `vpc`, `transit-gateway`, `global-network`, `core-network`
- `firewall`, `ec2-instance`, `elb`, `vpn`

### Action Commands (9)

- `write <file>`, `trace <src> <dst>`, `find_ip <ip>`
- `find_prefix <cidr>`, `find_null_routes`
- `reachability`, `populate_cache`, `clear_cache`
- `create-routing-cache`, `export_graph`

### Cache Commands Explained

#### `populate_cache` - General Topology Cache

**Purpose**: Pre-fetch ALL topology data across all modules for comprehensive analysis

**What it caches**:

- VPCs, subnets, route tables, security groups, NACLs
- Transit Gateways, attachments, peerings, route tables
- Cloud WAN (global networks, core networks, segments, attachments)
- EC2 instances, ENIs
- ELBs, listeners, target groups
- VPNs, Direct Connect connections, Firewalls
- All discoverable resources across all regions

**Use Case**: Warm cache before comprehensive analysis or demos
**Duration**: 30-60 seconds depending on account size

```bash
aws-net> populate_cache
Populating topology cache...
  → Discovering VPCs...
  → Discovering Transit Gateways...
  → Discovering Cloud WAN...
  → Discovering EC2 instances...
Cache populated
```

---

#### `create_routing_cache` - Specialized Routing Cache

**Purpose**: Build specialized cache of ONLY routing data for fast route lookups and analysis

**What it caches**:

- VPC route table entries (all route tables across all VPCs)
- Transit Gateway route table entries (all TGW route tables)
- Cloud WAN route table entries (by core network, segment, and region)

**Enables Commands**:

- `find_prefix <cidr>` - Find which route tables contain a prefix
- `find_null_routes` - Find blackhole/null routes across all routing domains
- `show routing-cache <filter>` - View cached routes with filtering

**Use Case**: Fast routing troubleshooting and analysis without fetching data
**Duration**: 10-20 seconds

```bash
aws-net> create_routing_cache
Building routing cache...
  VPC routes: 373
  Transit Gateway routes: 50
  Cloud WAN routes: 300
```

**View Cached Routes**:

```bash
# Summary
aws-net> show routing-cache

# Detailed views
aws-net> show routing-cache vpc              # All VPC route table entries
aws-net> show routing-cache transit-gateway  # All Transit Gateway routes
aws-net> show routing-cache cloud-wan        # All Cloud WAN routes (by segment/region)
aws-net> show routing-cache all              # Everything (comprehensive view)
```

---

#### Comparison

| Feature | populate_cache | create_routing_cache |
|---------|----------------|----------------------|
| **Scope** | Everything | Routes only |
| **Purpose** | General topology | Routing analysis |
| **Speed** | Slower (30-60s) | Faster (10-20s) |
| **Data** | All resources | Route tables only |
| **Enables** | All show commands | find_prefix, routing-cache commands |
| **When to use** | Before exploration/demos | Before routing troubleshooting |

**Recommendation**:

- Use `populate_cache` for general exploration and comprehensive analysis
- Use `create_routing_cache` specifically for routing troubleshooting and prefix searches

## 🔧 Configuration

Default configuration in `pyproject.toml`:

- **Timeout**: 120 seconds per command
- **Regions**: All enabled regions
- **Cache**: Enabled by default
- **Output**: Rich formatted tables

## 🎯 Development

### Adding New Commands

1. Add handler in `src/aws_network_tools/shell/handlers/`
2. Update `HIERARCHY` dict in `src/aws_network_tools/shell/base.py`
3. Run tests: `pytest tests/`

### Testing New Features

```bash
# Run all tests
pytest tests/ -v
```

## 📦 Dependencies

Core dependencies:

- **boto3**: AWS SDK
- **rich**: Terminal formatting
- **cmd2**: Shell framework
- **pytest**: Testing framework

See `pyproject.toml` for full dependency list.

## 📄 License

MIT License - see LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add comprehensive tests
4. Submit a pull request

## 📝 Changelog

### 2024-12-08

- ✅ VPN tunnel inspection: show tunnels displays VgwTelemetry data with UP/DOWN status
- ✅ VPN detail view: show detail includes tunnel summary with outside IPs and BGP routes
- ✅ Debug logging: AWS-net-runner --debug flag with comprehensive logging to /tmp/
- ✅ Network Firewall enhancements: rule-group context with detailed rule inspection
- ✅ Enhanced firewall commands: show firewall, show rule-groups with indexes
- ✅ STATELESS rules: Complete display with ports, protocols, actions
- ✅ STATEFUL rules: Suricata rule format display
- ✅ Graph commands: stats, validate, mermaid, parent path lookup
- ✅ Persistent routing cache with SQLite (save/load commands)
- ✅ Enhanced routing cache display: vpc, transit-gateway, cloud-wan filters
- ✅ Terminal width detection for proper Rich table rendering
- ✅ AWS-net-runner tool for programmatic shell execution

### 2024-12-05

- ✅ ELB commands implementation (listeners, targets, health)
- ✅ VPN context commands (detail, tunnels)
- ✅ Firewall policy command
- ✅ Core-network commands registration fix
- ✅ Direct resource selection without show command
- ✅ Automated issue resolution workflow
- ✅ Consolidated CLI to AWS-net-shell only
- ✅ Multi-level context prompt fix
- ✅ Comprehensive testing framework with pexpect integration
- ✅ Graph-based command testing

### 2024-12-02

- ✅ Comprehensive command graph with context navigation
- ✅ Dynamic command discovery (78+ commands)
- ✅ Command graph Mermaid diagrams
- ✅ Test coverage: 77+ commands
