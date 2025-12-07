# AWS Network Shell

**AWS Network Tools CLI - A hierarchical CLI for AWS networking**

## 🌟 Overview

AWS Network Shell provides a comprehensive CLI for managing AWS networking resources with a familiar Cisco IOS-style interface. Navigate through contexts (VPC, Transit Gateway, Firewall, etc.) and execute commands with hierarchical command structures.

## 📊 Command Hierarchy

The CLI uses a hierarchical command structure with 9 contexts and 78+ commands:

### Command Structure (Mermaid Diagram)

```mermaid
graph TD
    classDef root fill:#2d5a27,stroke:#1a3518,color:#fff
    classDef context fill:#1a4a6e,stroke:#0d2840,color:#fff
    classDef show fill:#4a4a8a,stroke:#2d2d5a,color:#fff
    classDef set fill:#6b4c9a,stroke:#3d2a5a,color:#fff
    classDef action fill:#8b4513,stroke:#5a2d0a,color:#fff

    %% Root Context
    root["aws-net"]:::root

    %% Context Entry Commands
    root --> root_set_vpc{"set vpc → vpc"}:::context
    root --> root_set_tgw{"set transit-gateway → transit-gateway"}:::context
    root --> root_set_gn{"set global-network → global-network"}:::context
    root --> root_set_cn{"set core-network → core-network"}:::context
    root --> root_set_fw{"set firewall → firewall"}:::context
    root --> root_set_ec2{"set ec2-instance → ec2-instance"}:::context
    root --> root_set_elb{"set elb → elb"}:::context
    root --> root_set_vpn{"set vpn → vpn"}:::context

    %% VPC Context Subgraph
    subgraph vpc_context["vpc context"]
        vpc_show_detail["show detail"]:::show
        vpc_show_subnets["show subnets"]:::show
        vpc_show_route_tables["show route-tables"]:::show
        vpc_show_security_groups["show security-groups"]:::show
        vpc_find_prefix["find_prefix"]:::action
        vpc_find_null_routes["find_null_routes"]:::action
    end

    root_set_vpc --> vpc_context

    %% Core Network Context Subgraph
    subgraph core_network_context["core-network context"]
        cn_show_segments["show segments"]:::show
        cn_show_policy["show policy"]:::show
        cn_show_routes["show routes"]:::show
        cn_show_blackhole_routes["show blackhole-routes"]:::show
        cn_find_prefix["find_prefix"]:::action
        cn_find_null_routes["find_null_routes"]:::action
    end

    root_set_cn --> core_network_context

    %% Global Network Commands
    root_set_gn --> gn_show_detail["show detail"]:::show
    root_set_gn --> gn_show_core_networks["show core-networks"]:::show

    %% Root-level Commands
    root --> root_show_vpcs["show vpcs"]:::show
    root --> root_show_tgws["show transit_gateways"]:::show
    root --> root_show_instances["show ec2-instances"]:::show
    root --> root_show_vpn["show vpns"]:::show
    root --> root_write["write"]:::action
    root --> root_trace["trace"]:::action
```

### Command Structure (Mermaid Diagrams)

- **Total Contexts**: 9
- **Total Commands**: 103

#### 1. Overview: Context Navigation

```mermaid
graph TD
    classDef root fill:#2d5a27,stroke:#1a3518,color:#fff
    classDef context fill:#1a4a6e,stroke:#0d2840,color:#fff

    root["aws-net"]:::root
    root_set_ec2_instance{"set ec2-instance → ec2-instance"}:::context
    root --> root_set_ec2_instance
    root_set_elb{"set elb → elb"}:::context
    root --> root_set_elb
    root_set_firewall{"set firewall → firewall"}:::context
    root --> root_set_firewall
    root_set_global_network{"set global-network → global-network"}:::context
    root --> root_set_global_network
    root_set_transit_gateway{"set transit-gateway → transit-gateway"}:::context
    root --> root_set_transit_gateway
    root_set_vpc{"set vpc → vpc"}:::context
    root --> root_set_vpc
    root_set_vpn{"set vpn → vpn"}:::context
    root --> root_set_vpn
```

#### 2. Core-Network Context

**Entry**: `set core-network`

```mermaid
graph LR
    classDef context fill:#1a4a6e,stroke:#0d2840,color:#fff
    classDef show fill:#4a4a8a,stroke:#2d2d5a,color:#fff
    classDef action fill:#8b4513,stroke:#5a2d0a,color:#fff
    classDef set fill:#6b4c9a,stroke:#3d2a5a,color:#fff

    global_network_set_core_network{"set core-network → core-network"}:::context
    core_network_context["core-network context"]:::context
    global_network_set_core_network --> core_network_context
    core_network_show_detail["show detail"]:::show
    core_network_context --> core_network_show_detail
    core_network_show_segments["show segments"]:::show
    core_network_context --> core_network_show_segments
    core_network_show_policy["show policy"]:::show
    core_network_context --> core_network_show_policy
    core_network_show_routes["show routes"]:::show
    core_network_context --> core_network_show_routes
    core_network_show_route_tables["show route-tables"]:::show
    core_network_context --> core_network_show_route_tables
    core_network_show_blackhole_routes["show blackhole-routes"]:::show
    core_network_context --> core_network_show_blackhole_routes
    core_network_show_policy_change_events["show policy-change-events"]:::show
    core_network_context --> core_network_show_policy_change_events
    core_network_show_connect_attachments["show connect-attachments"]:::show
    core_network_context --> core_network_show_connect_attachments
    core_network_show_connect_peers["show connect-peers"]:::show
    core_network_context --> core_network_show_connect_peers
    core_network_show_rib["show rib"]:::show
    core_network_context --> core_network_show_rib
    core_network_do_find_prefix(("find_prefix")):::action
    core_network_context --> core_network_do_find_prefix
    core_network_do_find_null_routes(("find_null_routes")):::action
    core_network_context --> core_network_do_find_null_routes
```

#### 3. Ec2-Instance Context

**Entry**: `set ec2-instance`

```mermaid
graph LR
    classDef context fill:#1a4a6e,stroke:#0d2840,color:#fff
    classDef show fill:#4a4a8a,stroke:#2d2d5a,color:#fff
    classDef action fill:#8b4513,stroke:#5a2d0a,color:#fff
    classDef set fill:#6b4c9a,stroke:#3d2a5a,color:#fff

    root_set_ec2_instance{"set ec2-instance → ec2-instance"}:::context
    ec2_instance_context["ec2-instance context"]:::context
    root_set_ec2_instance --> ec2_instance_context
    ec2_instance_show_detail["show detail"]:::show
    ec2_instance_context --> ec2_instance_show_detail
    ec2_instance_show_security_groups["show security-groups"]:::show
    ec2_instance_context --> ec2_instance_show_security_groups
    ec2_instance_show_enis["show enis"]:::show
    ec2_instance_context --> ec2_instance_show_enis
    ec2_instance_show_routes["show routes"]:::show
    ec2_instance_context --> ec2_instance_show_routes
```

#### 4. Elb Context

**Entry**: `set elb`

```mermaid
graph LR
    classDef context fill:#1a4a6e,stroke:#0d2840,color:#fff
    classDef show fill:#4a4a8a,stroke:#2d2d5a,color:#fff
    classDef action fill:#8b4513,stroke:#5a2d0a,color:#fff
    classDef set fill:#6b4c9a,stroke:#3d2a5a,color:#fff

    root_set_elb{"set elb → elb"}:::context
    elb_context["elb context"]:::context
    root_set_elb --> elb_context
    elb_show_detail["show detail"]:::show
    elb_context --> elb_show_detail
    elb_show_listeners["show listeners"]:::show
    elb_context --> elb_show_listeners
    elb_show_targets["show targets"]:::show
    elb_context --> elb_show_targets
    elb_show_health["show health"]:::show
    elb_context --> elb_show_health
```

#### 5. Firewall Context

**Entry**: `set firewall`

```mermaid
graph LR
    classDef context fill:#1a4a6e,stroke:#0d2840,color:#fff
    classDef show fill:#4a4a8a,stroke:#2d2d5a,color:#fff
    classDef action fill:#8b4513,stroke:#5a2d0a,color:#fff
    classDef set fill:#6b4c9a,stroke:#3d2a5a,color:#fff

    root_set_firewall{"set firewall → firewall"}:::context
    firewall_context["firewall context"]:::context
    root_set_firewall --> firewall_context
    firewall_show_detail["show detail"]:::show
    firewall_context --> firewall_show_detail
    firewall_show_rule_groups["show rule-groups"]:::show
    firewall_context --> firewall_show_rule_groups
    firewall_show_policy["show policy"]:::show
    firewall_context --> firewall_show_policy
```

#### 6. Global-Network Context

**Entry**: `set global-network`

```mermaid
graph LR
    classDef context fill:#1a4a6e,stroke:#0d2840,color:#fff
    classDef show fill:#4a4a8a,stroke:#2d2d5a,color:#fff
    classDef action fill:#8b4513,stroke:#5a2d0a,color:#fff
    classDef set fill:#6b4c9a,stroke:#3d2a5a,color:#fff

    root_set_global_network{"set global-network → global-network"}:::context
    global_network_context["global-network context"]:::context
    root_set_global_network --> global_network_context
    global_network_show_detail["show detail"]:::show
    global_network_context --> global_network_show_detail
    global_network_show_core_networks["show core-networks"]:::show
    global_network_context --> global_network_show_core_networks
```

#### 7. Route-Table Context

**Entry**: `set route-table`

```mermaid
graph LR
    classDef context fill:#1a4a6e,stroke:#0d2840,color:#fff
    classDef show fill:#4a4a8a,stroke:#2d2d5a,color:#fff
    classDef action fill:#8b4513,stroke:#5a2d0a,color:#fff
    classDef set fill:#6b4c9a,stroke:#3d2a5a,color:#fff

    core_network_set_route_table{"set route-table → route-table"}:::context
    route_table_context["route-table context"]:::context
    core_network_set_route_table --> route_table_context
    route_table_show_routes["show routes"]:::show
    route_table_context --> route_table_show_routes
    route_table_do_find_prefix(("find_prefix")):::action
    route_table_context --> route_table_do_find_prefix
    route_table_do_find_null_routes(("find_null_routes")):::action
    route_table_context --> route_table_do_find_null_routes
```

#### 8. Transit-Gateway Context

**Entry**: `set transit-gateway`

```mermaid
graph LR
    classDef context fill:#1a4a6e,stroke:#0d2840,color:#fff
    classDef show fill:#4a4a8a,stroke:#2d2d5a,color:#fff
    classDef action fill:#8b4513,stroke:#5a2d0a,color:#fff
    classDef set fill:#6b4c9a,stroke:#3d2a5a,color:#fff

    root_set_transit_gateway{"set transit-gateway → transit-gateway"}:::context
    transit_gateway_context["transit-gateway context"]:::context
    root_set_transit_gateway --> transit_gateway_context
    transit_gateway_show_detail["show detail"]:::show
    transit_gateway_context --> transit_gateway_show_detail
    transit_gateway_show_route_tables["show route-tables"]:::show
    transit_gateway_context --> transit_gateway_show_route_tables
    transit_gateway_show_attachments["show attachments"]:::show
    transit_gateway_context --> transit_gateway_show_attachments
    transit_gateway_do_find_prefix(("find_prefix")):::action
    transit_gateway_context --> transit_gateway_do_find_prefix
    transit_gateway_do_find_null_routes(("find_null_routes")):::action
    transit_gateway_context --> transit_gateway_do_find_null_routes
```

#### 9. Vpc Context

**Entry**: `set vpc`

```mermaid
graph LR
    classDef context fill:#1a4a6e,stroke:#0d2840,color:#fff
    classDef show fill:#4a4a8a,stroke:#2d2d5a,color:#fff
    classDef action fill:#8b4513,stroke:#5a2d0a,color:#fff
    classDef set fill:#6b4c9a,stroke:#3d2a5a,color:#fff

    root_set_vpc{"set vpc → vpc"}:::context
    vpc_context["vpc context"]:::context
    root_set_vpc --> vpc_context
    vpc_show_detail["show detail"]:::show
    vpc_context --> vpc_show_detail
    vpc_show_route_tables["show route-tables"]:::show
    vpc_context --> vpc_show_route_tables
    vpc_show_subnets["show subnets"]:::show
    vpc_context --> vpc_show_subnets
    vpc_show_security_groups["show security-groups"]:::show
    vpc_context --> vpc_show_security_groups
    vpc_show_nacls["show nacls"]:::show
    vpc_context --> vpc_show_nacls
    vpc_show_internet_gateways["show internet-gateways"]:::show
    vpc_context --> vpc_show_internet_gateways
    vpc_show_nat_gateways["show nat-gateways"]:::show
    vpc_context --> vpc_show_nat_gateways
    vpc_show_endpoints["show endpoints"]:::show
    vpc_context --> vpc_show_endpoints
    vpc_do_find_prefix(("find_prefix")):::action
    vpc_context --> vpc_do_find_prefix
    vpc_do_find_null_routes(("find_null_routes")):::action
    vpc_context --> vpc_do_find_null_routes
```

#### 10. Vpn Context

**Entry**: `set vpn`

```mermaid
graph LR
    classDef context fill:#1a4a6e,stroke:#0d2840,color:#fff
    classDef show fill:#4a4a8a,stroke:#2d2d5a,color:#fff
    classDef action fill:#8b4513,stroke:#5a2d0a,color:#fff
    classDef set fill:#6b4c9a,stroke:#3d2a5a,color:#fff

    root_set_vpn{"set vpn → vpn"}:::context
    vpn_context["vpn context"]:::context
    root_set_vpn --> vpn_context
    vpn_show_detail["show detail"]:::show
    vpn_context --> vpn_show_detail
    vpn_show_tunnels["show tunnels"]:::show
    vpn_context --> vpn_show_tunnels
```

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

## 📊 Commands by Category

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

### 2024-12-05
- ✅ ELB commands implementation (listeners, targets, health)
- ✅ VPN context commands (detail, tunnels)
- ✅ Firewall policy command
- ✅ Core-network commands registration fix
- ✅ Direct resource selection without show command
- ✅ Automated issue resolution workflow
- ✅ Consolidated CLI to aws-net-shell only
- ✅ Multi-level context prompt fix
- ✅ Comprehensive testing framework with pexpect integration
- ✅ Graph-based command testing

### 2024-12-02
- ✅ Comprehensive command graph with context navigation
- ✅ Dynamic command discovery (78+ commands)
- ✅ Command graph Mermaid diagrams
- ✅ Test coverage: 77+ commands

---

**Note:** This README is comprehensive and includes the command hierarchy in Mermaid diagram format based on `docs/command-hierarchy-split.md` structure.
