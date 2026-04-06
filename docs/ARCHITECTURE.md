# AWS Network Tools - Architecture & Codemap

**Version**: 2.0.0
**Last Updated**: 2026-04-06

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Module Breakdown](#module-breakdown)
4. [Class Diagrams](#class-diagrams)
5. [Application Lifecycle](#application-lifecycle)
6. [Data Flow](#data-flow)
7. [Core Workflows](#core-workflows)
8. [Deep-Dive: Traceroute Architecture](#deep-dive-traceroute-architecture)
9. [Deep-Dive: Caching Architecture](#deep-dive-caching-architecture)
10. [Deep-Dive: Context Navigation](#deep-dive-context-navigation)
11. [Adding a New Service Module](#adding-a-new-service-module)
12. [Extension Guide](#extension-guide)
13. [Interfaces & Contracts](#interfaces--contracts)
14. [Testing Architecture](#testing-architecture)
15. [Configuration System](#configuration-system)
16. [Performance Optimizations](#performance-optimizations)
17. [Security Considerations](#security-considerations)
18. [Troubleshooting & Debugging](#troubleshooting--debugging)
19. [Appendix](#appendix)

---

## Overview

AWS Network Tools is a Cisco IOS-style hierarchical CLI for AWS networking resources. The system provides intuitive navigation through AWS network infrastructure with context-aware commands, intelligent caching, and rich visualizations.

### Key Design Principles

1. **Hierarchical Context Management**: Navigate resources like Cisco IOS (enter/exit contexts)
2. **Mixin-Based Architecture**: Composable handlers for each AWS service
3. **Smart Caching**: Multi-level caching with TTL and account safety
4. **Rich UI**: Terminal-based tables, spinners, and colored output
5. **Extensibility**: Module interface for adding new AWS services

### Technology Stack

- **CLI Framework**: cmd2 (command parsing, completion, aliases)
- **UI/Display**: Rich (tables, colors, spinners, theming)
- **AWS SDK**: boto3 with custom retry/timeout configuration
- **Models**: Pydantic for validation and type safety
- **Caching**: File-based JSON cache with TTL

---

## System Architecture

### High-Level Component Diagram

```mermaid
graph TB
    subgraph "User Interface Layer"
        CLI[CLI Entry Point<br/>aws-net-shell]
        Runner[Automation Runner<br/>aws-net-runner]
    end

    subgraph "Shell Layer"
        Base[AWSNetShellBase<br/>Context Management]
        Main[AWSNetShell<br/>Command Routing]
        Handlers[Handler Mixins<br/>Root, CloudWAN, VPC, etc.]
    end

    subgraph "Core Services"
        Cache[Cache System<br/>TTL + Account Safety]
        Display[Display/Renderer<br/>Tables & Formatting]
        Logger[Logging System<br/>Debug + Audit]
        Spinner[UI Feedback<br/>Progress Indicators]
    end

    subgraph "AWS Integration Layer"
        Modules[Service Modules<br/>CloudWAN, VPC, TGW, etc.]
        Models[Data Models<br/>Pydantic Validation]
        BaseClient[BaseClient<br/>boto3 + Config]
    end

    subgraph "External Systems"
        AWS[AWS APIs<br/>CloudWAN, EC2, NetworkManager]
        FileCache[(File Cache<br/>~/.cache/aws-network-tools)]
    end

    CLI --> Main
    Runner --> Main
    Main --> Base
    Main --> Handlers
    Handlers --> Cache
    Handlers --> Display
    Handlers --> Modules
    Modules --> BaseClient
    Modules --> Models
    BaseClient --> AWS
    Cache --> FileCache
    Modules --> Logger
    Main --> Spinner

    style CLI fill:#2d5a27
    style Runner fill:#2d5a27
    style Main fill:#1a4a6e
    style Modules fill:#4a4a8a
    style AWS fill:#ff9900
```

### Directory Structure

```
src/aws_network_tools/
├── cli/                    # Entry points & automation
│   ├── runner.py          # aws-net-runner (non-interactive)
│   └── __init__.py
├── config/                 # Configuration management
│   └── __init__.py        # Theme, prompt, cache settings
├── core/                   # Foundation services
│   ├── base.py            # BaseClient, Context, ModuleInterface
│   ├── cache.py           # File-based cache with TTL
│   ├── cache_db.py        # Database-backed cache (future)
│   ├── decorators.py      # @requires_context, @cached, etc.
│   ├── display.py         # Base display classes
│   ├── ip_resolver.py     # IP/CIDR utilities
│   ├── logging.py         # Structured logging setup
│   ├── renderer.py        # Table rendering engine
│   └── spinner.py         # Progress indicators
├── models/                 # Data validation
│   ├── base.py            # AWSResource, CIDRBlock
│   ├── cloudwan.py        # CoreNetwork, Segment, etc.
│   ├── ec2.py             # Instance, ENI, SecurityGroup
│   ├── tgw.py             # TransitGateway, Attachment
│   └── vpc.py             # VPC, Subnet, RouteTable
├── modules/                # AWS service clients
│   ├── cloudwan.py        # Cloud WAN operations
│   ├── vpc.py             # VPC operations
│   ├── tgw.py             # Transit Gateway operations
│   ├── ec2.py             # EC2 instance operations
│   ├── anfw.py            # Network Firewall operations
│   ├── elb.py             # Load Balancer operations
│   ├── vpn.py             # Site-to-Site VPN operations
│   ├── eni.py             # ENI operations
│   ├── security.py        # Security Groups & NACLs
│   ├── flowlogs.py        # VPC Flow Logs
│   ├── traceroute.py      # Network path tracing
│   └── [15+ other AWS services]
├── shell/                  # CLI implementation
│   ├── base.py            # AWSNetShellBase (context stack, navigation)
│   ├── main.py            # AWSNetShell (command routing)
│   ├── handlers/          # Service-specific command handlers
│   │   ├── root.py        # Root-level commands (show, set, trace)
│   │   ├── cloudwan.py    # CloudWAN context commands
│   │   ├── vpc.py         # VPC context commands
│   │   ├── tgw.py         # Transit Gateway commands
│   │   ├── ec2.py         # EC2 instance commands
│   │   ├── firewall.py    # Firewall context commands
│   │   ├── elb.py         # Load Balancer commands
│   │   ├── vpn.py         # VPN context commands
│   │   └── utilities.py   # Cache, config, graph commands
│   ├── arguments.py       # Argument parsing helpers
│   ├── discovery.py       # Resource discovery utilities
│   └── graph.py           # Command hierarchy graph operations
├── themes/                 # UI theming
│   └── __init__.py        # Theme loading (Catppuccin, Dracula)
└── traceroute/            # Network path analysis
    ├── engine.py          # Path tracing engine
    ├── topology.py        # Topology builder
    ├── models.py          # Hop, Path models
    └── staleness.py       # Cache freshness checks
```

---

## Module Breakdown

### 1. Core Layer (`core/`)

#### `base.py` - Foundation Classes

**Classes**:

- `BaseClient` - Boto3 session management with custom config
  - Handles AWS credentials (profile or default)
  - Standardized retry/timeout configuration
  - Thread pool concurrency control

- `Context` - Shell execution context (dataclass)
  - `type`: Context name (vpc, transit-gateway, etc.)
  - `ref`: Resource identifier (ID or ARN)
  - `name`: Human-readable name
  - `data`: Full resource detail dictionary
  - `selection_index`: User's selection number (1-based)

- `ModuleInterface` - Abstract interface for AWS service modules
  - Defines module contract: name, commands, context_commands, show_commands
  - `execute()` method for command dispatching

**Purpose**: Provides base abstractions used across all layers

#### `cache.py` - File-Based Caching

```mermaid
graph LR
    A[Cache Request] --> B{Cache Exists?}
    B -->|Yes| C{Not Expired?}
    B -->|No| E[Fetch from AWS]
    C -->|Yes| D{Same Account?}
    C -->|No| E
    D -->|Yes| F[Return Cached]
    D -->|No| E
    E --> G[Cache Result]
    G --> F

    style F fill:#2d5a27
    style E fill:#ff9900
```

**Classes**:

- `Cache(namespace)` - Namespace-isolated cache
  - `get(ignore_expiry, current_account)` - Retrieve with validation
  - `set(data, ttl_seconds, account_id)` - Store with metadata
  - `clear()` - Delete cache file
  - `get_info()` - Cache metadata (age, TTL, expiry status)

**Features**:

- TTL-based expiration (default 15min, configurable)
- Account safety (auto-clear on account switch)
- Namespace isolation (separate cache per service)
- ISO 8601 timestamps with timezone awareness

**Storage**: `~/.cache/aws-network-tools/{namespace}.json`

#### `decorators.py` - Command Decorators

**Functions**:

- `@requires_context(ctx_type)` - Ensure command runs in correct context
- `@cached(key, ttl)` - Auto-cache function results
- `@spinner(message)` - Show progress spinner during execution

#### `display.py` & `renderer.py` - UI Components

**Classes**:

- `BaseDisplay` - Abstract display interface
  - Defines `show_detail()`, `render_table()` methods
  - Used by service-specific display classes

- `TableRenderer` - Advanced table rendering
  - Nested tables support
  - Column auto-sizing
  - Rich formatting integration

#### `spinner.py` - Progress Feedback

**Functions**:

- `run_with_spinner(fn, message)` - Execute with progress indicator
- Handles exceptions and displays errors gracefully

#### `ip_resolver.py` - Network Utilities

**Functions**:

- IP address parsing and validation
- CIDR manipulation and comparison
- Subnet calculations

---

### 2. Models Layer (`models/`)

Pydantic-based data validation for AWS resources.

```mermaid
classDiagram
    class AWSResource {
        +str id
        +str name
        +str region
        +validate_id()
        +to_dict()
    }

    class VPC {
        +str vpc_id
        +list~CIDRBlock~ cidr_blocks
        +list~Subnet~ subnets
        +list~RouteTable~ route_tables
    }

    class CoreNetwork {
        +str id
        +str arn
        +str global_network_id
        +list~Segment~ segments
        +dict policy
    }

    class TransitGateway {
        +str id
        +int asn
        +list~Attachment~ attachments
        +list~RouteTable~ route_tables
    }

    AWSResource <|-- VPC
    AWSResource <|-- CoreNetwork
    AWSResource <|-- TransitGateway

    style AWSResource fill:#4a4a8a
```

**Purpose**:

- Type-safe data structures
- Automatic validation on construction
- Backward compatibility via `to_dict()`

---

### 3. Modules Layer (`modules/`)

AWS service clients - one module per AWS service.

#### Module Architecture Pattern

```mermaid
graph TB
    subgraph "Module Structure"
        Client[Client Class<br/>AWS API calls]
        Display[Display Class<br/>Terminal rendering]
        Module[Module Class<br/>ModuleInterface impl]
    end

    subgraph "External Dependencies"
        BaseClient[core.BaseClient]
        BaseDisplay[core.BaseDisplay]
        ModuleInterface[core.ModuleInterface]
        Models[models.*]
    end

    Client --> BaseClient
    Display --> BaseDisplay
    Module --> ModuleInterface
    Client --> Models
    Display --> Models
    Module --> Client
    Module --> Display

    style Client fill:#1a4a6e
    style Display fill:#4a4a8a
    style Module fill:#6b4c9a
```

#### Example: CloudWAN Module (`modules/cloudwan.py`)

**Classes**:

1. **`CloudWANClient(BaseClient)`** - AWS API operations
   - `list_global_networks()` → Global Networks
   - `get_core_network(id)` → Core Network details
   - `get_policy(id, version)` → Policy document
   - `list_attachments(id)` → VPC/VPN/Connect attachments
   - `get_routes(id, segment, edge)` → Route tables
   - Multi-region support with concurrent fetching

2. **`CloudWANDisplay(BaseDisplay)`** - Terminal rendering
   - `show_detail(data)` → Core Network overview table
   - `render_segments(segments)` → Segment configuration
   - `render_routes(routes)` → Route table with colors
   - `render_policy(policy)` → Formatted policy YAML

3. **`CloudWANModule(ModuleInterface)`** - Shell integration
   - Declares commands: `global-network`, `core-network`
   - Defines show options per context
   - Implements command execution and context navigation

**Similar patterns for**: VPC, TGW, EC2, Firewall, ELB, VPN, etc.

---

### 4. Shell Layer (`shell/`)

#### Command Processing Flow

```mermaid
sequenceDiagram
    participant User
    participant cmd2
    participant Main as AWSNetShell
    participant Handler as HandlerMixin
    participant Module as ServiceModule
    participant Cache
    participant AWS

    User->>cmd2: Enter command
    cmd2->>cmd2: Parse & expand aliases
    cmd2->>Main: do_show/do_set/do_[cmd]
    Main->>Main: Validate context
    Main->>Main: Parse arguments

    alt Show Command
        Main->>Handler: _show_[resource]()
        Handler->>Cache: Check cache
        alt Cache Hit
            Cache-->>Handler: Return cached data
        else Cache Miss
            Handler->>Module: fetch()
            Module->>AWS: API call
            AWS-->>Module: Response
            Module-->>Handler: Processed data
            Handler->>Cache: Store result
        end
        Handler->>Main: Data
        Main->>Main: _emit_json_or_table()
        Main-->>User: Render output
    end

    alt Set Command
        Main->>Handler: _set_[resource](value)
        Handler->>Handler: Resolve index/id/name
        Handler->>Module: get_detail()
        Module->>AWS: API call
        AWS-->>Module: Detail response
        Module-->>Handler: Full data
        Handler->>Main: _enter(ctx_type, ref, name, data)
        Main->>Main: Update context_stack
        Main->>Main: _update_prompt()
        Main-->>User: New prompt display
    end
```

#### `base.py` - AWSNetShellBase

**Core Responsibilities**:

1. **Context Stack Management**
   - `context_stack: list[Context]` - Navigation history
   - `_enter(ctx_type, ref, name, data, index)` - Push context
   - `_exit()` / `_end()` - Pop/clear contexts

2. **Prompt Rendering**
   - `_update_prompt()` - Generate colored prompts
   - Theme-based styling (short vs long format)
   - Multi-line hierarchical display

3. **Command Hierarchy**
   - `HIERARCHY` dict - Valid commands per context
   - `hierarchy` property - Current context's valid commands
   - Validation and help generation

4. **Resource Resolution**
   - `_resolve(items, val)` - Find by index/ID/name
   - 1-based indexing for user convenience

5. **Utility Commands**
   - `do_exit()`, `do_end()`, `do_clear()`
   - `do_clear_cache()`, `do_refresh()`
   - `do_help()`, `default()` (error handling)

#### `main.py` - AWSNetShell

**Mixin Composition**:

```python
class AWSNetShell(
    RootHandlersMixin,      # Root-level: show, set, trace, find_ip
    CloudWANHandlersMixin,  # CloudWAN contexts
    VPCHandlersMixin,       # VPC contexts
    TGWHandlersMixin,       # Transit Gateway contexts
    EC2HandlersMixin,       # EC2 instance contexts
    FirewallHandlersMixin,  # Firewall contexts
    VPNHandlersMixin,       # VPN contexts
    ELBHandlersMixin,       # Load Balancer contexts
    UtilityHandlersMixin,   # Config, cache, graph utilities
    AWSNetShellBase,        # Base context management
):
```

**Key Methods**:

- `_cached(key, fetch_fn, msg)` - Cache wrapper with spinner
- `_emit_json_or_table(data, render_fn)` - Format-aware output
- `do_show(args)` - Route show commands to handlers
- `do_set(args)` - Route set commands to handlers
- `do_find_prefix(args)` - Context-aware prefix search
- `do_find_null_routes()` - Context-aware blackhole detection

#### Handler Mixins (`shell/handlers/`)

Each handler mixin provides commands for a specific AWS service or context.

**Pattern**:

```python
class ServiceHandlersMixin:
    def _show_[resource](self, args):
        """Show resource list or details"""
        data = self._cached("key", lambda: Module().fetch())
        # Render table or JSON

    def _set_[resource](self, val):
        """Enter resource context"""
        items = self._cache.get("key", [])
        item = self._resolve(items, val)
        detail = Module().get_detail(item['id'])
        self._enter("context-type", item['id'], item['name'], detail)
```

**Handler Overview**:

| Handler | Contexts | Commands | AWS Services |
|---------|----------|----------|--------------|
| `root.py` | None (root) | show vpcs, set vpc, trace, find_ip | Multiple |
| `cloudwan.py` | global-network, core-network, route-table | show routes, policy, segments | NetworkManager, CloudWAN |
| `vpc.py` | vpc | show subnets, route-tables, nacls | EC2 (VPC APIs) |
| `tgw.py` | transit-gateway | show attachments, route-tables | EC2 (TGW APIs) |
| `ec2.py` | ec2-instance | show detail, security-groups, enis | EC2 |
| `firewall.py` | firewall, rule-group | show rules, policy | NetworkFirewall |
| `elb.py` | elb | show listeners, targets, health | ELBv2 |
| `vpn.py` | vpn | show tunnels, detail | EC2 (VPN APIs) |
| `utilities.py` | N/A | populate_cache, show cache, graph | Local operations |

---

## Class Diagrams

### Shell Class Hierarchy

`AWSNetShell` is assembled through multiple inheritance. The nine handler mixins each own their domain's commands; `AWSNetShellBase` owns all shared state.

```mermaid
classDiagram
    direction TB

    class AWSNetShellBase {
        +profile: str
        +regions: list[str]
        +no_cache: bool
        +output_format: str
        +context_stack: list[Context]
        +_cache: dict
        +theme: dict
        +config: AppConfig
        +ctx: Context
        +ctx_type: str
        +ctx_id: str
        +hierarchy: dict
        +_enter(ctx_type, res_id, name, data, index)
        +_exit()
        +_resolve(items, val) dict
        +_update_prompt()
        +_sync_runtime_config()
        +precmd(line) Statement
        +do_exit(args)
        +do_end(args)
        +do_refresh(args)
        +do_clear_cache(args)
        +do_help(args)
        +default(stmt)
    }

    class RootHandlersMixin {
        +_show_vpcs(args)
        +_show_transit_gateways(args)
        +_show_firewalls(args)
        +_show_elbs(args)
        +_show_vpns(args)
        +_show_ec2_instances(args)
        +_show_global_networks(args)
        +_show_enis(args)
        +_show_security_groups(args)
        +_show_version(args)
        +_show_config(args)
        +_show_regions(args)
        +do_find_prefix(args)
        +do_find_null_routes(args)
        +do_trace(args)
    }

    class CloudWANHandlersMixin {
        +_show_segments(args)
        +_show_policy_documents(args)
        +_show_live_policy(args)
        +_show_cloudwan_route_tables(args)
        +_show_cloudwan_routes(args)
        +_show_blackhole_routes(args)
        +_show_core_networks(args)
        +_show_connect_attachments(args)
        +_show_rib(args)
        +_set_global_network(val)
        +_set_core_network(val)
        +_set_cloudwan_route_table(val)
        +_cloudwan_find_prefix(prefix)
        +_cloudwan_find_null_routes()
    }

    class VPCHandlersMixin {
        +_show_vpc_route_tables(args)
        +_show_subnets(args)
        +_show_nacls(args)
        +_show_internet_gateways(args)
        +_show_nat_gateways(args)
        +_show_endpoints(args)
        +_set_vpc(val)
        +_set_vpc_route_table(val)
        +_vpc_find_prefix(prefix)
        +_vpc_find_null_routes()
    }

    class TGWHandlersMixin {
        +_show_transit_gateway_route_tables(args)
        +_show_tgw_attachments(args)
        +_set_transit_gateway(val)
        +_set_tgw_route_table(val)
        +_tgw_find_prefix(prefix)
        +_tgw_find_null_routes()
    }

    class EC2HandlersMixin {
        +_show_ec2_security_groups(args)
        +_show_ec2_enis(args)
        +_show_ec2_routes(args)
        +_set_ec2_instance(val)
    }

    class FirewallHandlersMixin {
        +_show_firewall_rule_groups(args)
        +_show_firewall_policy(args)
        +_set_firewall(val)
        +_set_rule_group(val)
    }

    class ELBHandlersMixin {
        +_show_elb_listeners(args)
        +_show_elb_targets(args)
        +_show_elb_health(args)
        +_set_elb(val)
    }

    class VPNHandlersMixin {
        +_show_vpn_tunnels(args)
        +_set_vpn(val)
    }

    class UtilityHandlersMixin {
        +do_populate_cache(args)
        +do_find_ip(args)
        +do_write(args)
        +do_validate_graph(args)
        +do_export_graph(args)
        +_show_cache(args)
        +_show_routing_cache(args)
        +_show_graph(args)
        +_set_profile(val)
        +_set_regions(val)
        +_set_theme(val)
        +_set_output_format(val)
    }

    class AWSNetShell {
        +_cached(key, fetch_fn, msg) Any
        +_emit_json_or_table(data, render_fn)
        +_run_with_pipe(fn, pipe_filter)
        +_watch_loop(fn, interval)
        +do_show(args)
        +do_set(args)
        +do_find_prefix(args)
        +do_find_null_routes(args)
        +complete_show(text, line, begidx, endidx)
        +complete_set(text, line, begidx, endidx)
    }

    AWSNetShell --|> RootHandlersMixin
    AWSNetShell --|> CloudWANHandlersMixin
    AWSNetShell --|> VPCHandlersMixin
    AWSNetShell --|> TGWHandlersMixin
    AWSNetShell --|> EC2HandlersMixin
    AWSNetShell --|> FirewallHandlersMixin
    AWSNetShell --|> VPNHandlersMixin
    AWSNetShell --|> ELBHandlersMixin
    AWSNetShell --|> UtilityHandlersMixin
    AWSNetShell --|> AWSNetShellBase
```

### BaseClient Hierarchy

Every module's Client class inherits `BaseClient`, which provides the configured boto3 session and region resolution.

```mermaid
classDiagram
    direction TB

    class BaseClient {
        +profile: str
        +session: boto3.Session
        +max_workers: int
        +client(service, region_name) boto3.Client
        +get_regions() list[str]
    }

    class CloudWANClient {
        +_nm_region: str
        +nm: boto3.Client
        +list_global_networks() list[dict]
        +get_core_network(id) dict
        +list_core_networks(gn_id) list[dict]
        +list_attachments(cn_id) list[dict]
        +get_routes(cn_id, segment, edge) list[dict]
        +get_rib(cn_id, segment, edge) list[dict]
        +list_policy_versions(cn_id) list[dict]
        +get_policy_change_events(cn_id) list[dict]
    }

    class VPCClient {
        +discover(regions) list[dict]
        +get_vpc_detail(vpc_id, region) dict
        +get_route_tables(vpc_id, region) list[dict]
        +get_subnets(vpc_id, region) list[dict]
        +get_nacls(vpc_id, region) list[dict]
        +get_security_groups(vpc_id, region) list[dict]
        +get_nat_gateways(vpc_id, region) list[dict]
        +get_endpoints(vpc_id, region) list[dict]
    }

    class TGWClient {
        +discover(regions) list[dict]
        +get_route_tables(tgw_id, region) list[dict]
        +get_attachments(tgw_id, region) list[dict]
        +get_routes(rt_id, region) list[dict]
    }

    class EC2Client {
        +discover(regions) list[dict]
        +get_instance_detail(instance_id, region) dict
    }

    class ANFWClient {
        +discover(regions) list[dict]
        +get_firewall_detail(arn, region) dict
        +get_rule_group(arn, region) dict
        +get_policy(arn, region) dict
    }

    class ELBClient {
        +discover(regions) list[dict]
        +get_elb_detail(arn, region) dict
        +get_listeners(arn, region) list[dict]
        +get_target_groups(arn, region) list[dict]
        +get_target_health(tg_arn, region) list[dict]
    }

    class VPNClient {
        +discover(regions) list[dict]
        +get_vpn_detail(vpn_id, region) dict
        +get_tunnels(vpn_id, region) list[dict]
    }

    class ENIClient {
        +discover(regions) list[dict]
        +find_by_ip(ip, regions) dict
    }

    BaseClient <|-- CloudWANClient
    BaseClient <|-- VPCClient
    BaseClient <|-- TGWClient
    BaseClient <|-- EC2Client
    BaseClient <|-- ANFWClient
    BaseClient <|-- ELBClient
    BaseClient <|-- VPNClient
    BaseClient <|-- ENIClient
```

### Display Hierarchy

Each module's Display class wraps Rich console output. All inherit `BaseDisplay` which provides the `route_table()` helper and cache info panel.

```mermaid
classDiagram
    direction TB

    class BaseDisplay {
        +console: Console
        +print_cache_info(cache_info)
        +route_table(title, routes, columns) Table
    }

    class CloudWANDisplay {
        +show_detail(cn_data)
        +show_segments(segments)
        +show_routes(routes)
        +show_policy(policy)
        +show_attachments(attachments)
        +show_rib(rib_entries)
    }

    class VPCDisplay {
        +show_detail(vpc_data)
        +show_route_tables(route_tables)
        +show_subnets(subnets)
        +show_nacls(nacls)
        +show_security_groups(sgs)
    }

    class TGWDisplay {
        +show_tgw_detail(tgw_data)
        +show_route_tables(route_tables)
        +show_routes(routes)
        +show_attachments(attachments)
    }

    class ANFWDisplay {
        +show_firewall_detail(fw_data)
        +show_rule_group(rule_group)
        +show_policy(policy)
    }

    class ELBDisplay {
        +show_elb_detail(elb_data)
        +show_listeners(listeners)
        +show_target_groups(tgs)
        +show_target_health(health)
    }

    class VPNDisplay {
        +show_vpn_detail(vpn_data)
        +show_tunnels(tunnels)
    }

    class ENIDisplay {
        +show_enis(enis)
        +show_eni_detail(eni)
    }

    BaseDisplay <|-- CloudWANDisplay
    BaseDisplay <|-- VPCDisplay
    BaseDisplay <|-- TGWDisplay
    BaseDisplay <|-- ANFWDisplay
    BaseDisplay <|-- ELBDisplay
    BaseDisplay <|-- VPNDisplay
    BaseDisplay <|-- ENIDisplay
```

### Model Hierarchy

Pydantic models enforce ID format validation at construction time via `field_validator`. All models use `ConfigDict(extra="allow")` for forward-compatible AWS API responses.

```mermaid
classDiagram
    direction TB

    class AWSResource {
        +id: str
        +name: Optional[str]
        +region: str
        +validate_id(v) str
        +to_dict() dict
    }

    class CIDRBlock {
        +cidr: str
        +validate_cidr(v) str
    }

    class VPCModel {
        +cidr: Optional[str]
        +cidrs: list[str]
        +state: str
        +is_default: bool
        +subnets: list[SubnetModel]
        +route_tables: list[RouteTableModel]
        +security_groups: list[SecurityGroupModel]
        +validate_vpc_id(v) str
    }

    class SubnetModel {
        +cidr: str
        +az: str
        +public: bool
    }

    class RouteTableModel {
        +is_main: bool
        +subnets: list[str]
        +routes: list[RouteModel]
    }

    class RouteModel {
        +destination: str
        +target: str
        +state: Literal[active, blackhole]
        +type: Optional[str]
    }

    class SecurityGroupModel {
        +description: Optional[str]
        +vpc_id: str
        +ingress: list[dict]
        +egress: list[dict]
    }

    class CoreNetworkModel {
        +global_network_id: str
        +global_network_name: Optional[str]
        +state: str
        +segments: list[str]
        +regions: list[str]
        +route_tables: list[dict]
        +policy: Optional[dict]
        +validate_cn_id(v) str
    }

    class SegmentModel {
        +edge_locations: list[str]
        +isolate_attachments: bool
        +require_attachment_acceptance: bool
    }

    class CloudWANRouteModel {
        +prefix: str
        +target: str
        +target_type: Optional[str]
        +state: Literal[ACTIVE, BLACKHOLE]
        +type: Optional[str]
    }

    class TGWModel {
        +state: str
        +asn: Optional[int]
        +attachments: list[TGWAttachmentModel]
        +route_tables: list[TGWRouteTableModel]
        +validate_tgw_id(v) str
    }

    class TGWRouteTableModel {
        +routes: list[TGWRouteModel]
        +associations: list[str]
        +propagations: list[str]
    }

    class TGWAttachmentModel {
        +type: str
        +state: str
        +resource_id: Optional[str]
        +resource_owner: Optional[str]
    }

    class EC2InstanceModel {
        +type: str
        +state: str
        +az: str
        +vpc_id: Optional[str]
        +subnet_id: Optional[str]
        +private_ip: Optional[str]
        +enis: list[ENIModel]
        +security_groups: list[dict]
        +validate_instance_id(v) str
    }

    class ENIModel {
        +vpc_id: str
        +subnet_id: str
        +private_ip: str
        +public_ip: Optional[str]
        +mac_address: Optional[str]
        +interface_type: str
        +instance_id: Optional[str]
        +validate_eni_id(v) str
    }

    AWSResource <|-- VPCModel
    AWSResource <|-- SubnetModel
    AWSResource <|-- RouteTableModel
    AWSResource <|-- RouteModel
    AWSResource <|-- SecurityGroupModel
    AWSResource <|-- CoreNetworkModel
    AWSResource <|-- SegmentModel
    AWSResource <|-- CloudWANRouteModel
    AWSResource <|-- TGWModel
    AWSResource <|-- TGWRouteTableModel
    AWSResource <|-- TGWAttachmentModel
    AWSResource <|-- EC2InstanceModel
    AWSResource <|-- ENIModel
    VPCModel *-- SubnetModel
    VPCModel *-- RouteTableModel
    VPCModel *-- SecurityGroupModel
    RouteTableModel *-- RouteModel
    TGWModel *-- TGWAttachmentModel
    TGWModel *-- TGWRouteTableModel
    EC2InstanceModel *-- ENIModel
```

### ModuleInterface and Implementations

```mermaid
classDiagram
    direction TB

    class ModuleInterface {
        <<abstract>>
        +name: str
        +commands: dict[str,str]
        +context_commands: dict[str,list[str]]
        +show_commands: dict[str,list[str]]
        +execute(shell, command, args)*
    }

    class CloudWANModule {
        +name = "cloudwan"
        +commands: global-network
        +execute(shell, command, args)
        -_enter_global_network(shell, args)
        -_enter_core_network(shell, args)
    }

    class VPCModule {
        +name = "vpc"
        +commands: vpc
        +execute(shell, command, args)
    }

    class TGWModule {
        +name = "tgw"
        +commands: transit-gateway
        +execute(shell, command, args)
    }

    class ANFWModule {
        +name = "anfw"
        +commands: firewall
        +execute(shell, command, args)
    }

    class ELBModule {
        +name = "elb"
        +commands: elb
        +execute(shell, command, args)
    }

    class VPNModule {
        +name = "vpn"
        +commands: vpn
        +execute(shell, command, args)
    }

    class ENIModule {
        +name = "eni"
        +commands: eni
        +execute(shell, command, args)
    }

    ModuleInterface <|-- CloudWANModule
    ModuleInterface <|-- VPCModule
    ModuleInterface <|-- TGWModule
    ModuleInterface <|-- ANFWModule
    ModuleInterface <|-- ELBModule
    ModuleInterface <|-- VPNModule
    ModuleInterface <|-- ENIModule
```

---

## Application Lifecycle

### Startup Flow

From the `main()` entry point through to the interactive loop.

```mermaid
flowchart TD
    A([aws-net-shell invoked]) --> B[argparse: profile, no-cache, format]
    B --> C[AWSNetShell instantiated]
    C --> D[AWSNetShellBase.__init__]
    D --> E[cmd2.Cmd.__init__]
    E --> F[Load AppConfig\n~/.aws-network-tools/config.json]
    F --> G[load_theme: catppuccin-mocha etc]
    G --> H[RuntimeConfig.set_profile / set_regions]
    H --> I[Hide internal cmd2 commands]
    I --> J[_update_prompt: render aws-net> ]
    J --> K[Apply CLI args: profile, no_cache, format]
    K --> L[shell.cmdloop]
    L --> M([User prompt displayed])

    style A fill:#2d5a27
    style M fill:#4a4a8a
```

### Command Lifecycle

Full path from keystroke to rendered output.

```mermaid
sequenceDiagram
    participant U as User
    participant cmd2 as cmd2.Cmd
    participant Base as AWSNetShellBase
    participant Main as AWSNetShell
    participant Handler as HandlerMixin
    participant Cache as _cache dict
    participant FileCache as Cache class
    participant Module as ServiceClient
    participant AWS as AWS API

    U->>cmd2: Enter command text
    cmd2->>Base: precmd(line)
    Base->>Base: Expand alias (sh→show, ex→exit)
    Base-->>cmd2: Expanded statement
    cmd2->>Main: do_show(args) or do_set(args)

    alt show command
        Main->>Main: Parse opt, arg, watch, pipe
        Main->>Main: Validate opt in hierarchy["show"]
        Main->>Handler: _show_{opt}(arg)
        Handler->>Cache: key in self._cache?
        alt Memory cache hit
            Cache-->>Handler: Cached list
        else Memory cache miss
            Handler->>Main: _cached(key, fetch_fn, msg)
            Main->>Module: fetch_fn() via run_with_spinner
            Module->>FileCache: Cache.get(current_account)
            alt File cache hit
                FileCache-->>Module: Cached data
            else File cache miss
                Module->>AWS: boto3 API call
                AWS-->>Module: Response
                Module->>FileCache: Cache.set(data, ttl, account_id)
            end
            Module-->>Main: Processed list
            Main->>Cache: _cache[key] = data
        end
        Handler->>Main: _emit_json_or_table(data, render_fn)
        Main-->>U: Table / JSON / YAML output
    end

    alt set command
        Main->>Main: Parse opt, val
        Main->>Main: Validate opt in hierarchy["set"]
        Main->>Handler: _set_{opt}(val)
        Handler->>Cache: Look up list from _cache
        Handler->>Base: _resolve(items, val)
        Base-->>Handler: Matched resource dict
        Handler->>Module: get_detail(id, region)
        Module->>AWS: Detail API call
        AWS-->>Module: Full resource data
        Handler->>Base: _enter(ctx_type, ref, name, data, idx)
        Base->>Base: context_stack.append(Context)
        Base->>Base: _update_prompt()
        Base-->>U: New prompt rendered
    end

    Note over Base: postcmd hooks run after every command
```

### Session Lifecycle

State changes that affect the whole session rather than a single command.

```mermaid
stateDiagram-v2
    [*] --> Fresh: Shell starts

    Fresh --> ProfileSet: set profile <name>
    ProfileSet --> Fresh: RuntimeConfig updated\n_cache cleared

    Fresh --> RegionScoped: set regions us-east-1,eu-west-1
    RegionScoped --> Fresh: set regions (empty clears scope)

    Fresh --> NoCacheMode: set no-cache on
    NoCacheMode --> Fresh: set no-cache off

    Fresh --> OutputChanged: set output-format json|yaml|table
    OutputChanged --> Fresh: (persists for session)

    Fresh --> ThemeChanged: set theme dracula|catppuccin-mocha
    ThemeChanged --> Fresh: Prompt recoloured immediately

    Fresh --> InContext: set vpc|tgw|firewall|elb|vpn|etc
    InContext --> InContext: set route-table|rule-group\n(deeper context)
    InContext --> Fresh: exit (pop one level)\nor end (return to root)
```

### User Context State Diagram

Complete view of all navigable states and their available commands.

```mermaid
stateDiagram-v2
    [*] --> Root: Shell start

    state Root {
        [*] --> root_idle
        root_idle: show vpcs|tgws|elbs|firewalls|vpns|ec2-instances|global-networks|enis|...
        root_idle: set vpc|transit-gateway|firewall|elb|vpn|ec2-instance|global-network
        root_idle: trace|find_ip|find_prefix|find_null_routes|populate_cache
    }

    Root --> GlobalNetwork: set global-network N
    Root --> VPC: set vpc N
    Root --> TransitGateway: set transit-gateway N
    Root --> Firewall: set firewall N
    Root --> ELB: set elb N
    Root --> EC2Instance: set ec2-instance N
    Root --> VPN: set vpn N

    state GlobalNetwork {
        [*] --> gn_idle
        gn_idle: show detail|core-networks
        gn_idle: set core-network N
    }

    GlobalNetwork --> CoreNetwork: set core-network N
    GlobalNetwork --> Root: exit

    state CoreNetwork {
        [*] --> cn_idle
        cn_idle: show detail|segments|routes|route-tables|blackhole-routes
        cn_idle: show policy-documents|live-policy|connect-attachments|connect-peers|rib
        cn_idle: set route-table N
        cn_idle: find_prefix|find_null_routes
    }

    CoreNetwork --> CloudWANRouteTable: set route-table N
    CoreNetwork --> GlobalNetwork: exit
    CoreNetwork --> Root: end

    state CloudWANRouteTable {
        [*] --> cwrt_idle
        cwrt_idle: show routes
        cwrt_idle: find_prefix|find_null_routes
    }

    CloudWANRouteTable --> CoreNetwork: exit
    CloudWANRouteTable --> Root: end

    state VPC {
        [*] --> vpc_idle
        vpc_idle: show detail|route-tables|subnets|security-groups|nacls
        vpc_idle: show internet-gateways|nat-gateways|endpoints
        vpc_idle: set route-table N
        vpc_idle: find_prefix|find_null_routes
    }

    VPC --> VPCRouteTable: set route-table N
    VPC --> Root: exit
    VPC --> Root: end

    state VPCRouteTable {
        [*] --> vpcrt_idle
        vpcrt_idle: show routes
        vpcrt_idle: find_prefix|find_null_routes
    }

    VPCRouteTable --> VPC: exit
    VPCRouteTable --> Root: end

    state TransitGateway {
        [*] --> tgw_idle
        tgw_idle: show detail|route-tables|attachments
        tgw_idle: set route-table N
        tgw_idle: find_prefix|find_null_routes
    }

    TransitGateway --> TGWRouteTable: set route-table N
    TransitGateway --> Root: exit
    TransitGateway --> Root: end

    state TGWRouteTable {
        [*] --> tgwrt_idle
        tgwrt_idle: show routes
        tgwrt_idle: find_prefix|find_null_routes
    }

    TGWRouteTable --> TransitGateway: exit
    TGWRouteTable --> Root: end

    state Firewall {
        [*] --> fw_idle
        fw_idle: show detail|firewall|rule-groups|policy
        fw_idle: set rule-group N
    }

    Firewall --> RuleGroup: set rule-group N
    Firewall --> Root: exit

    state RuleGroup {
        [*] --> rg_idle
        rg_idle: show rule-group
    }

    RuleGroup --> Firewall: exit
    RuleGroup --> Root: end

    state ELB {
        [*] --> elb_idle
        elb_idle: show detail|listeners|targets|health
    }
    ELB --> Root: exit

    state EC2Instance {
        [*] --> ec2_idle
        ec2_idle: show detail|security-groups|enis|routes
    }
    EC2Instance --> Root: exit

    state VPN {
        [*] --> vpn_idle
        vpn_idle: show detail|tunnels
    }
    VPN --> Root: exit
```

---

## Data Flow

### Command Execution Pipeline

```mermaid
flowchart TB
    Start([User Input]) --> Parse[Parse Command<br/>cmd2.onecmd]
    Parse --> Alias{Alias?<br/>sh→show}
    Alias -->|Yes| Expand[Expand Alias]
    Alias -->|No| Route
    Expand --> Route[Route to Handler<br/>do_show/do_set]

    Route --> Validate{Valid in<br/>Context?}
    Validate -->|No| Error1[Error: Invalid command]
    Validate -->|Yes| Handler[Execute Handler Method]

    Handler --> CacheCheck{Check Cache}
    CacheCheck -->|Hit| Return[Return Cached]
    CacheCheck -->|Miss| Fetch[Fetch from AWS]

    Fetch --> Process[Process Response]
    Process --> CacheStore[Store in Cache]
    CacheStore --> Return

    Return --> Format{Output Format}
    Format -->|JSON| JSON[Render JSON]
    Format -->|YAML| YAML[Render YAML]
    Format -->|Table| Table[Render Table]

    JSON --> Output
    YAML --> Output
    Table --> Output
    Output([Display to User])

    Error1 --> Output

    style Start fill:#2d5a27
    style Fetch fill:#ff9900
    style Output fill:#4a4a8a
```

### Context Navigation Flow

```mermaid
stateDiagram-v2
    [*] --> Root: Shell Start

    Root --> GlobalNetwork: set global-network 1
    GlobalNetwork --> CoreNetwork: set core-network 1
    CoreNetwork --> RouteTable: set route-table 1

    Root --> VPC: set vpc 1
    Root --> TransitGateway: set transit-gateway 1
    Root --> Firewall: set firewall 1
    Root --> EC2Instance: set ec2-instance 1
    Root --> ELB: set elb 1
    Root --> VPN: set vpn 1

    VPC --> VPCRouteTable: set route-table 1
    TransitGateway --> TGWRouteTable: set route-table 1
    Firewall --> RuleGroup: set rule-group 1

    RouteTable --> CoreNetwork: exit
    VPCRouteTable --> VPC: exit
    TGWRouteTable --> TransitGateway: exit
    RuleGroup --> Firewall: exit

    CoreNetwork --> GlobalNetwork: exit
    GlobalNetwork --> Root: exit

    VPC --> Root: exit
    TransitGateway --> Root: exit
    Firewall --> Root: exit
    EC2Instance --> Root: exit
    ELB --> Root: exit
    VPN --> Root: exit

    CoreNetwork --> Root: end
    RouteTable --> Root: end
    VPCRouteTable --> Root: end
    TGWRouteTable --> Root: end
    RuleGroup --> Root: end

    note right of Root
        Refresh command available
        at ALL levels
    end note
```

### Cache Architecture

```mermaid
graph TB
    subgraph "Memory Cache Layer"
        MemCache[shell._cache<br/>Dict~str,Any~]
        RefreshCmd[refresh command<br/>Clear specific keys]
    end

    subgraph "File Cache Layer"
        FileCache[Cache class<br/>JSON files]
        TTL[TTL Manager<br/>15min default]
        AccountCheck[Account Validator]
    end

    subgraph "Storage"
        CacheDir[(~/.cache/<br/>aws-network-tools/)]
        ConfigFile[config.json<br/>TTL settings]
    end

    subgraph "Modules"
        CloudWAN[CloudWAN Module]
        VPC[VPC Module]
        TGW[TGW Module]
        Other[Other Modules]
    end

    RefreshCmd --> MemCache
    MemCache --> FileCache
    FileCache --> TTL
    FileCache --> AccountCheck
    FileCache --> CacheDir
    ConfigFile --> TTL

    CloudWAN --> MemCache
    VPC --> MemCache
    TGW --> MemCache
    Other --> MemCache

    style RefreshCmd fill:#2d5a27
    style MemCache fill:#1a4a6e
    style FileCache fill:#4a4a8a
```

**Two-Level Caching**:

1. **Memory Cache** (`self._cache`) - Session-scoped, cleared by refresh
2. **File Cache** (`Cache` class) - Persistent, TTL + account-aware

**Cache Keys**:

- `vpcs`, `transit_gateways`, `firewalls`, `elb`, `vpns`, `ec2_instances`
- `global_networks`, `core_networks`, `enis`
- Namespaced by service type

---

## Core Workflows

### Workflow 1: Resource Discovery & Selection

```mermaid
sequenceDiagram
    actor User
    participant Shell
    participant Handler
    participant Cache
    participant Module
    participant AWS

    User->>Shell: show elbs
    Shell->>Handler: _show_elbs()
    Handler->>Cache: get("elb")

    alt Cache Miss
        Cache-->>Handler: None
        Handler->>Module: ELBClient.discover()
        Module->>AWS: describe_load_balancers()
        AWS-->>Module: ELB list
        Module-->>Handler: Processed ELBs
        Handler->>Cache: set("elb", data)
    else Cache Hit
        Cache-->>Handler: Cached ELBs
    end

    Handler->>Handler: Render table with indices
    Handler-->>User: Display table

    User->>Shell: set elb 2
    Shell->>Handler: _set_elb("2")
    Handler->>Handler: _resolve(elbs, "2")
    Handler->>Module: ELBClient.get_elb_detail(arn)
    Module->>AWS: describe_load_balancers(LoadBalancerArns=[arn])
    AWS-->>Module: Full ELB detail
    Module-->>Handler: ELB detail
    Handler->>Shell: _enter("elb", arn, name, detail, 2)
    Shell->>Shell: context_stack.append(Context(...))
    Shell->>Shell: _update_prompt()
    Shell-->>User: elb:2> prompt
```

### Workflow 2: Context-Aware Commands

**Scenario**: User runs `find_prefix 10.0.0.0/16` in different contexts

```mermaid
graph TD
    Start[find_prefix 10.0.0.0/16] --> CheckCtx{Current Context?}

    CheckCtx -->|route-table| RT[Search in current<br/>route table only]
    CheckCtx -->|core-network| CN[Search all CloudWAN<br/>route tables]
    CheckCtx -->|transit-gateway| TGW[Search all TGW<br/>route tables]
    CheckCtx -->|vpc| VPC[Search all VPC<br/>route tables]
    CheckCtx -->|root| Cache[Search routing<br/>cache database]

    RT --> Display[Display matched routes]
    CN --> Display
    TGW --> Display
    VPC --> Display
    Cache --> Display

    Display --> End([User sees results])

    style Start fill:#2d5a27
    style Display fill:#4a4a8a
```

**Implementation**: `main.py:316-363` - `do_find_prefix()` dispatches based on `ctx_type`

### Workflow 3: Cache Refresh

```mermaid
sequenceDiagram
    actor User
    participant Shell
    participant MemCache
    participant FileCache

    Note over User,FileCache: Scenario: ELBs provisioning

    User->>Shell: show elbs
    Shell->>MemCache: get("elb")
    MemCache->>FileCache: Cache.get()
    FileCache-->>MemCache: Empty (no ELBs yet)
    MemCache-->>User: "No load balancers found"

    Note over User: Wait for provisioning...

    User->>Shell: refresh elb
    Shell->>MemCache: del _cache["elb"]
    MemCache-->>User: "Refreshed elb cache"

    User->>Shell: show elbs
    Shell->>MemCache: get("elb") → None
    Shell->>Shell: fetch_fn() → ELBClient.discover()
    Shell->>AWS: API call
    AWS-->>Shell: New ELBs
    Shell->>MemCache: _cache["elb"] = new_data
    Shell-->>User: Display ELB table
```

---

## Deep-Dive: Traceroute Architecture

The `trace` command performs a deterministic, API-driven hop-by-hop network path analysis. Unlike ICMP traceroute, it reads AWS control-plane data: route tables, attachment configurations, and the ENI index. No packets are sent.

### Component Relationships

```mermaid
graph TB
    subgraph "Shell Layer"
        RootHandler[RootHandlersMixin\ndo_trace]
    end

    subgraph "Traceroute Engine"
        Engine[AWSTraceroute\ntrace src dst]
        Discovery[TopologyDiscovery\ndiscover]
        Topology[NetworkTopology\n- eni_index\n- route_tables\n- tgws\n- vpcs\n- cwan_attachments]
        Staleness[StalenessChecker\nis_stale]
        Models[Hop / TraceResult]
    end

    subgraph "Core Infrastructure"
        FileCache[Cache class\ntopology namespace]
    end

    subgraph "AWS APIs"
        NM[NetworkManager API]
        EC2[EC2 API regions]
    end

    RootHandler --> Engine
    Engine --> Discovery
    Discovery --> Staleness
    Staleness --> EC2
    Discovery --> FileCache
    Discovery --> NM
    Discovery --> EC2
    Discovery --> Topology
    Engine --> Topology
    Engine --> Models

    style Engine fill:#1a4a6e
    style Topology fill:#4a4a8a
    style FileCache fill:#2d5a27
```

### Step-by-Step Trace Algorithm

```mermaid
flowchart TD
    Start([trace src_ip dst_ip]) --> T1[_ensure_topology\nload or discover NetworkTopology]

    T1 --> T2[_find_eni_cached src_ip\nLook up eni_index]
    T2 --> T3[_find_eni_cached dst_ip\nLook up eni_index]

    T3 --> T4{Both ENIs found?}
    T4 -->|No| FAIL1([blocked: IP not in topology])
    T4 -->|Yes| T5[Emit Hop 1: source ENI]

    T5 --> T6[_get_route_table_cached subnet_id\nCheck topology.route_tables]
    T6 --> T7[Emit Hop 2: source route table]

    T7 --> T8[_find_best_route routes dst_ip\nLongest prefix match]
    T8 --> T9{Route found?}
    T9 -->|No| FAIL2([blocked: no route to dst])
    T9 -->|Yes| T10{Route target type?}

    T10 -->|local + same VPC| DIRECT[Emit Hop N: destination ENI\nreachable = True]
    T10 -->|core_network_arn present| CW[_trace_via_cloudwan\nWalk CWAN attachments\n& segment route tables]
    T10 -->|tgw- prefix| TGW[_trace_via_tgw\nWalk TGW route tables\n& VPC attachment]
    T10 -->|other| FAIL3([blocked: unsupported target])

    CW --> RESULT([TraceResult with hop list])
    TGW --> RESULT
    DIRECT --> RESULT

    style Start fill:#2d5a27
    style RESULT fill:#4a4a8a
    style FAIL1 fill:#8b0000
    style FAIL2 fill:#8b0000
    style FAIL3 fill:#8b0000
```

### Topology Discovery

`TopologyDiscovery.discover()` runs concurrently across all regions using a `ThreadPoolExecutor` (20 workers). It builds the `NetworkTopology` dataclass which is then serialised to the `topology` cache namespace.

**Discovery sequence**:

1. Fetch account ID (STS GetCallerIdentity)
2. Enumerate enabled regions
3. Per-region (concurrent): fetch VPCs, TGW route tables, ENIs, subnet-to-route-table mappings
4. Fetch Cloud WAN global networks, core networks, attachments, live policy
5. Build `eni_index`: `{ip: {eni_id, vpc_id, subnet_id, region}}` for O(1) IP lookups
6. Serialise to `~/.cache/aws-network-tools/topology.json`

**Staleness checking** (`StalenessChecker`): Before using cached topology, the engine samples up to 5 regions and compares current TGW/VPC counts against saved markers. A count change invalidates the cache and triggers a full re-discovery.

---

## Deep-Dive: Caching Architecture

The system uses three independent cache layers. Each layer has a distinct scope and invalidation mechanism.

### Three-Layer Overview

```mermaid
graph TB
    subgraph "L1: Memory Cache"
        direction LR
        MC[self._cache\ndict in AWSNetShell\nSession-scoped]
        MCKeys["Keys: vpcs, elbs, transit_gateways,\nfirewalls, global_networks, core_networks,\nenis, security_groups, route53_resolver,\npeering_connections, prefix_lists ..."]
        MCInv[Invalidated by:\nrefresh command\nprofile switch]
    end

    subgraph "L2: File Cache"
        direction LR
        FC[Cache class\nJSON files per namespace\nPersists across restarts]
        FCKeys["~/.cache/aws-network-tools/\n  cloudwan.json\n  topology.json\n  [namespace].json"]
        FCInv[Invalidated by:\nTTL expiry (default 15min)\naccount_id mismatch\nclear_cache command]
    end

    subgraph "L3: Routing Cache"
        direction LR
        RC[Routing Cache\nPre-computed route tables\nAll services cross-referenced]
        RCKeys["Built by: populate_cache command\nUsed by: find_prefix at root level\nStored via topology Cache namespace"]
        RCInv[Invalidated by:\nmanual populate_cache\nTopology staleness check]
    end

    Handler --> MC
    MC -->|Miss| Fetch
    Fetch --> FC
    FC -->|Miss| AWS[AWS API]
    AWS --> FC
    FC --> MC

    RootFindPrefix[find_prefix at root] --> RC
    RC -->|Miss| populate_cache
    populate_cache --> RC

    style MC fill:#1a4a6e
    style FC fill:#4a4a8a
    style RC fill:#6b4c9a
```

### Cache Class Internals

```mermaid
flowchart LR
    A[Cache.get\ncurrent_account] --> B{File exists?}
    B -->|No| MISS[Return None]
    B -->|Yes| C{account_id matches?}
    C -->|No| D[Cache.clear\nDelete file]
    D --> MISS
    C -->|Yes| E{TTL expired?}
    E -->|Yes| MISS
    E -->|No| HIT[Return data]

    style HIT fill:#2d5a27
    style MISS fill:#8b4513
```

**File format** (`~/.cache/aws-network-tools/{namespace}.json`):

```json
{
  "data": { ... },
  "cached_at": "2026-04-06T10:30:00+00:00",
  "ttl_seconds": 900,
  "account_id": "123456789012"
}
```

### The `_cached()` Pattern

`AWSNetShell._cached()` is the integration point between L1 and L2. Every handler uses it instead of calling modules directly:

```python
def _cached(self, key: str, fetch_fn, msg: str = "Loading..."):
    if key not in self._cache or self.no_cache:
        self._cache[key] = run_with_spinner(fetch_fn, msg)
    return self._cache[key]
```

The `fetch_fn` lambda wraps the module call. The module itself may internally hit `Cache.get()` for L2. The two levels are independent: L1 stores the processed Python list; L2 stores the raw serialised API response.

**Account safety detail**: `Cache.get()` accepts `current_account`. If the account ID in the file differs from the caller's account, the file is deleted before `None` is returned. This prevents stale cross-account data from surfacing silently after a `set profile` switch.

### Cache Key Reference

| L1 key | L2 namespace | Refresh alias |
|---|---|---|
| `vpcs` | (inline) | `vpc`, `vpcs` |
| `transit_gateways` | (inline) | `tgw`, `transit-gateway` |
| `firewalls` | (inline) | `firewall`, `firewalls` |
| `elbs` | (inline) | `elb`, `elbs` |
| `vpns` | (inline) | `vpn`, `vpns` |
| `enis` | (inline) | `eni`, `enis` |
| `global_networks` | (inline) | `global-network` |
| `core_networks` | (inline) | `core-network` |
| `security_groups` | (inline) | `sg`, `sgs` |
| `ec2_instances` | (inline) | `ec2` |
| `topology` | `topology` | `populate_cache` |
| `cloudwan` | `cloudwan` | `refresh all` |

---

## Deep-Dive: Context Navigation

### The HIERARCHY Dictionary

`HIERARCHY` in `shell/base.py` is the single source of truth for what commands are legal in each context. It maps `context_type` (or `None` for root) to three lists:

- `show`: valid subcommands after `show`
- `set`: valid subcommands after `set`
- `commands`: top-level commands available (shown by `?` and `do_help`)

`AWSNetShellBase.hierarchy` is a property that returns `HIERARCHY[self.ctx_type]`, defaulting to `HIERARCHY[None]` at root. Both `do_show` and `do_set` in `AWSNetShell` call `self.hierarchy.get("show"|"set", [])` before dispatching to handlers, rejecting anything not in the list with a clear error message.

### Context Stack Mechanics

```mermaid
flowchart LR
    subgraph "Before: set vpc 2"
        S1["context_stack = []"]
    end

    subgraph "After: set vpc 2"
        S2["context_stack = [\n  Context(type='vpc',\n    ref='vpc-0abc',\n    name='prod-vpc',\n    data={...},\n    selection_index=2)\n]"]
    end

    subgraph "After: set route-table 1"
        S3["context_stack = [\n  Context('vpc', 'vpc-0abc', ...),\n  Context('route-table', 'rtb-0xyz', ...)\n]"]
    end

    subgraph "After: exit"
        S4["context_stack = [\n  Context('vpc', 'vpc-0abc', ...)\n]"]
    end

    subgraph "After: end"
        S5["context_stack = []"]
    end

    S1 --> S2 --> S3 --> S4 --> S5
```

### Prompt Generation

`_update_prompt()` iterates `context_stack` and renders each level with its theme colour. Two styles are supported, controlled by `config.get_prompt_style()`:

**Short style** (compact, single line):
```
aws-net>gl:1>cn:2>
```

**Long style** (multi-line, with names):
```
aws-net> gl:1:prod-global-network >
  cn:2:prod-core-network >
    rt:1:seg-prod-us-east-1 $
```

Abbreviation mapping: `global-network` → `gl`, `core-network` → `cn`, `transit-gateway` → `tg`, `ec2-instance` → `ec`, all others use first two characters of context type.

### Command Resolution Flow

```mermaid
flowchart TD
    Input([User types command]) --> Precmd[precmd: expand alias]
    Precmd --> Parse[cmd2 parse: verb + args]

    Parse --> Verb{Verb?}

    Verb -->|show| ShowValidate[Validate in hierarchy show list]
    Verb -->|set| SetValidate[Validate in hierarchy set list]
    Verb -->|exit| Exit[Pop context_stack\n_update_prompt]
    Verb -->|end| End[Clear context_stack\n_update_prompt]
    Verb -->|refresh| Refresh[Delete from _cache\nby key alias]
    Verb -->|?| Help[_show_cmds: print hierarchy commands list]
    Verb -->|unknown| Default[default: print Unknown command error]

    ShowValidate -->|invalid| ShowError[Print valid options list]
    ShowValidate -->|valid| ShowDispatch[getattr self _show_{opt}]
    ShowDispatch -->|method exists| ShowRun[Execute handler method]
    ShowDispatch -->|no method| ShowNotImpl[Print not implemented]

    SetValidate -->|invalid| SetError[Print valid options list]
    SetValidate -->|valid| SetDispatch[getattr self _set_{opt}]
    SetDispatch -->|method exists| SetRun[Execute handler method\n→ _enter new context]
    SetDispatch -->|no method| SetNotImpl[Print not implemented]

    style Input fill:#2d5a27
    style ShowRun fill:#4a4a8a
    style SetRun fill:#4a4a8a
```

---

## Adding a New Service Module

### Adding a New AWS Service Module

#### Step 1: Create Module File

`modules/my_service.py`:

```python
from ..core.base import BaseClient, ModuleInterface, BaseDisplay
from ..models.base import AWSResource
from typing import List, Dict

class MyServiceClient(BaseClient):
    """AWS API operations for MyService"""

    def discover(self, regions: List[str] = None) -> List[dict]:
        """Fetch all resources across regions"""
        regions = regions or [self.session.region_name]
        results = []
        for region in regions:
            client = self.client('myservice', region)
            resp = client.describe_resources()
            for item in resp['Resources']:
                results.append({
                    'id': item['ResourceId'],
                    'name': item.get('Tags', {}).get('Name'),
                    'region': region,
                    'state': item['State'],
                })
        return results

    def get_detail(self, resource_id: str, region: str) -> dict:
        """Fetch full resource details"""
        client = self.client('myservice', region)
        resp = client.describe_resource(ResourceId=resource_id)
        return resp['Resource']

class MyServiceDisplay(BaseDisplay):
    """Terminal rendering for MyService"""

    def show_detail(self, data: dict):
        """Render resource detail table"""
        from rich.table import Table
        table = Table(title=f"MyService: {data.get('name')}")
        table.add_column("Field", style="cyan")
        table.add_column("Value")
        for key in ('id', 'state', 'region'):
            if data.get(key):
                table.add_row(key, str(data[key]))
        self.console.print(table)

class MyServiceModule(ModuleInterface):
    """Shell integration"""

    @property
    def name(self) -> str:
        return "myservice"

    @property
    def commands(self) -> Dict[str, str]:
        return {"my-resource": "Enter resource: my-resource <#|id>"}

    @property
    def show_commands(self) -> Dict[str, List[str]]:
        return {
            None: ["my-resources"],
            "my-resource": ["detail", "properties"],
        }

    def execute(self, shell, command: str, args: str):
        if command == "my-resource":
            self._enter_resource(shell, args)
```

#### Step 2: Add Handler Mixin

`shell/handlers/my_service.py`:

```python
from rich.console import Console

console = Console()

class MyServiceHandlersMixin:
    """Handler for MyService contexts"""

    def _show_my_resources(self, _):
        """Show all resources"""
        from ...modules import my_service

        resources = self._cached(
            "my_resources",
            lambda: my_service.MyServiceClient(self.profile).discover(),
            "Fetching resources"
        )

        if not resources:
            console.print("[yellow]No resources found[/]")
            return

        # Render table with index, name, state
        from rich.table import Table
        table = Table(title="My Resources")
        table.add_column("#", style="dim")
        table.add_column("Name")
        table.add_column("State")

        for i, r in enumerate(resources, 1):
            table.add_row(str(i), r['name'], r['state'])

        console.print(table)
        console.print("[dim]Use 'set my-resource <#>' to select[/]")

    def _set_my_resource(self, val):
        """Enter resource context"""
        if not val:
            console.print("[red]Usage: set my-resource <#|id>[/]")
            return

        resources = self._cache.get("my_resources", [])
        if not resources:
            console.print("[yellow]Run 'show my-resources' first[/]")
            return

        resource = self._resolve(resources, val)
        if not resource:
            console.print(f"[red]Not found: {val}[/]")
            return

        from ...modules import my_service
        from ...core import run_with_spinner

        detail = run_with_spinner(
            lambda: my_service.MyServiceClient(self.profile).get_detail(
                resource['id'], resource['region']
            ),
            "Fetching resource details"
        )

        try:
            selection_idx = int(val)
        except ValueError:
            selection_idx = 1

        self._enter("my-resource", resource['id'], resource['name'], detail, selection_idx)
```

#### Step 3: Update Hierarchy

`shell/base.py` - Add to `HIERARCHY`:

```python
HIERARCHY = {
    None: {
        "show": [..., "my-resources"],
        "set": [..., "my-resource"],
        "commands": [...]
    },
    "my-resource": {
        "show": ["detail", "properties"],
        "set": [],
        "commands": ["show", "refresh", "exit", "end"],
    },
}
```

#### Step 4: Register in Main Shell

`shell/main.py`:

```python
from .handlers import (
    ...,
    MyServiceHandlersMixin,
)

class AWSNetShell(
    ...,
    MyServiceHandlersMixin,
    AWSNetShellBase,
):
```

#### Step 5: Add Tests

`tests/test_my_service.py`:

```python
def test_show_my_resources(shell):
    """Test showing resources"""
    # Mock AWS responses
    # Test table rendering
    # Verify caching behavior

def test_set_my_resource(shell):
    """Test entering resource context"""
    # Test context navigation
    # Verify prompt update
```

---

## Module Interactions

### Client → Display → Handler Flow

```mermaid
graph LR
    subgraph "Handler (Shell Command)"
        H1[_show_elbs]
        H2[_set_elb]
    end

    subgraph "Module Layer"
        C[ELBClient]
        D[ELBDisplay]
    end

    subgraph "Core Services"
        BC[BaseClient]
        Cache[Cache]
        Spinner[Spinner]
    end

    subgraph "AWS"
        API[AWS ELB API]
    end

    H1 --> C
    C --> BC
    BC --> API
    API --> C
    C --> Cache
    C --> D
    D --> H1

    H2 --> C
    C --> API
    API --> C
    C --> H2

    H1 -.->|Uses| Spinner
    H2 -.->|Uses| Spinner

    style H1 fill:#6b4c9a
    style H2 fill:#6b4c9a
    style C fill:#1a4a6e
    style D fill:#4a4a8a
    style API fill:#ff9900
```

### Cross-Module Dependencies

```mermaid
graph TB
    subgraph "Shell Layer"
        Shell[AWSNetShell]
        Handlers[Handler Mixins]
    end

    subgraph "Service Modules"
        CloudWAN[cloudwan.py]
        VPC[vpc.py]
        TGW[tgw.py]
        EC2[ec2.py]
        Firewall[anfw.py]
        ENI[eni.py]
    end

    subgraph "Cross-Cutting Modules"
        IPFinder[ip_finder.py<br/>Find IPs across services]
        Traceroute[traceroute.py<br/>Path analysis]
        Security[security.py<br/>SG & NACL utilities]
    end

    subgraph "Core Services"
        BaseClient
        Cache
        Models
    end

    Handlers --> CloudWAN
    Handlers --> VPC
    Handlers --> TGW
    Handlers --> EC2
    Handlers --> Firewall

    IPFinder --> ENI
    IPFinder --> EC2
    IPFinder --> VPC

    Traceroute --> CloudWAN
    Traceroute --> VPC
    Traceroute --> TGW

    Security --> VPC
    Security --> EC2

    CloudWAN --> BaseClient
    VPC --> BaseClient
    TGW --> BaseClient
    EC2 --> BaseClient
    Firewall --> BaseClient
    ENI --> BaseClient

    CloudWAN --> Models
    VPC --> Models
    TGW --> Models

    CloudWAN --> Cache
    VPC --> Cache
    TGW --> Cache

    style IPFinder fill:#8b4513
    style Traceroute fill:#8b4513
    style Security fill:#8b4513
```

---

## Extension Guide

### Adding New Commands to Existing Context

**Example**: Add `show performance` to ELB context

1. **Update Hierarchy** (`shell/base.py`):

```python
"elb": {
    "show": ["detail", "listeners", "targets", "health", "performance"],
    ...
}
```

2. **Add Handler** (`shell/handlers/elb.py`):

```python
def _show_performance(self, _):
    """Show ELB performance metrics"""
    if self.ctx_type != "elb":
        console.print("[red]Must be in ELB context[/]")
        return

    arn = self.ctx.ref
    # Fetch CloudWatch metrics
    # Render performance table
```

3. **Add Test** (`tests/test_elb_handler.py`):

```python
def test_show_performance(shell):
    # Setup ELB context
    # Mock CloudWatch response
    # Verify output
```

### Implementing New Output Format

**Example**: Add CSV export

1. **Add to Base** (`shell/base.py`):

```python
"set": [..., "output-format"],
```

2. **Update Handler** (`shell/main.py`):

```python
def _emit_json_or_table(self, data, render_table_fn):
    if self.output_format == "json":
        # ... existing JSON ...
    elif self.output_format == "csv":
        import csv
        import sys
        writer = csv.DictWriter(sys.stdout, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    else:
        render_table_fn()
```

---

## Interfaces & Contracts

### ModuleInterface (Abstract Base Class)

**Contract**:

```python
class ModuleInterface(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique module identifier"""
        pass

    @property
    def commands(self) -> Dict[str, str]:
        """Root-level commands this module provides"""
        return {}

    @property
    def context_commands(self) -> Dict[str, List[str]]:
        """Commands available in specific contexts"""
        return {}

    @property
    def show_commands(self) -> Dict[str, List[str]]:
        """Show options per context"""
        return {}

    @abstractmethod
    def execute(self, shell, command: str, args: str):
        """Execute module command"""
        pass
```

**Purpose**: Standardizes module behavior for discovery and integration

### BaseClient Interface

**Contract**:

```python
class BaseClient:
    def __init__(self, profile: Optional[str] = None, session: Optional[boto3.Session] = None):
        """Initialize with AWS credentials"""

    def client(self, service: str, region_name: Optional[str] = None):
        """Create configured boto3 client"""
```

**Guarantees**:

- Automatic retry on throttling (10 attempts, exponential backoff)
- 5s connect timeout, 20s read timeout
- User agent tracking for API metrics
- Graceful fallback if config fails

### BaseDisplay Interface

**Contract**:

```python
class BaseDisplay:
    def __init__(self, console: Console):
        """Initialize with Rich console"""

    def show_detail(self, data: dict):
        """Render resource detail view"""
        # Must implement
```

**Purpose**: Separates data fetching from presentation logic

---

## Testing Architecture

```mermaid
graph TB
    subgraph "Test Organization"
        Unit[Unit Tests<br/>tests/unit/]
        Integration[Integration Tests<br/>tests/integration/]
        Fixtures[Test Fixtures<br/>tests/fixtures/]
        Utils[Test Utilities<br/>tests/test_utils/]
    end

    subgraph "Test Categories"
        Shell[Shell Tests<br/>test_shell*.py]
        Handlers[Handler Tests<br/>test_*_handler.py]
        Modules[Module Tests<br/>test_*_module.py]
        Graph[Graph Tests<br/>test_graph*.py]
        Commands[Command Tests<br/>test_*_commands.py]
    end

    subgraph "Test Tools"
        Conftest[conftest.py<br/>Pytest fixtures]
        Mocks[Mock AWS Responses<br/>JSON fixtures]
        CtxMgr[Context Managers<br/>State management]
    end

    Unit --> Handlers
    Unit --> Modules
    Integration --> Shell
    Integration --> Commands

    Shell --> Conftest
    Handlers --> Conftest
    Modules --> Mocks
    Graph --> CtxMgr

    Fixtures --> Mocks
    Utils --> CtxMgr

    style Unit fill:#2d5a27
    style Integration fill:#1a4a6e
    style Fixtures fill:#4a4a8a
```

**Test Coverage** (12/09/2025):

- **Total Tests**: 200+ across 40+ test files
- **Shell Tests**: Context navigation, command validation
- **Handler Tests**: Each service handler validated
- **Module Tests**: AWS API integration with mocking
- **Graph Tests**: Command hierarchy validation

---

## Configuration System

### Config File Structure

**Location**: `~/.aws-network-tools/config.json`

```json
{
  "theme": "catppuccin-mocha",
  "prompt_style": "short",
  "show_indices": true,
  "max_length": 20,
  "cache_ttl_seconds": 900
}
```

### Theme System

**Available Themes**:

- `catppuccin-mocha` (default) - Dark theme with pastel colors
- `catppuccin-latte` - Light theme
- `catppuccin-macchiato` - Mid-tone theme
- `dracula` - Purple-focused dark theme

**Theme Structure**:

```json
{
  "prompt_text": "white",
  "prompt_separator": "bright_black",
  "global-network": "cyan",
  "core-network": "blue",
  "vpc": "green",
  "transit-gateway": "yellow",
  "firewall": "red",
  "ec2-instance": "magenta",
  "elb": "bright_cyan"
}
```

**Customization** (`shell/base.py:236-335`):

- Prompt styles: "short" (compact) vs "long" (multi-line)
- Index display: show/hide selection numbers
- Max length: truncate long names
- Per-context color schemes

---

## Performance Optimizations

### Concurrent API Calls

**Pattern** (`modules/*.py`):

```python
def discover_multi_region(self, regions: List[str]) -> List[dict]:
    from concurrent.futures import ThreadPoolExecutor, as_completed

    results = []
    with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
        futures = {
            executor.submit(self._fetch_region, region): region
            for region in regions
        }
        for future in as_completed(futures):
            results.extend(future.result())
    return results
```

**Used by**: CloudWAN, VPC, TGW, Firewall modules for multi-region discovery

### Smart Caching Strategy

**Level 1 - Memory Cache** (`shell.main._cache`):

- Stores list views (show vpcs, show elbs)
- Cleared by `refresh` command
- Session-scoped only

**Level 2 - File Cache** (`core/cache.py`):

- Stores expensive API results
- TTL-based expiration (15 min default)
- Account-aware (auto-clear on profile switch)
- Survives shell restarts

**Level 3 - Routing Cache** (`shell/utilities.py`):

- Pre-computed route tables across all services
- Used by `find_prefix` at root level
- Database-backed for complex queries

### Lazy Loading

**Pattern**:

```python
def _show_detail(self, _):
    # Fetch full details only when user enters context
    # List view fetches minimal data (id, name, state)
    # Detail view fetches everything (routes, attachments, etc.)
```

**Benefit**: 80% reduction in API calls for typical workflows

---

## Security Considerations

### AWS Credentials

**Priority Order**:

1. `--profile` flag → Use specific AWS profile
2. `AWS_PROFILE` env var
3. Default credentials chain (IAM role, env vars, ~/.AWS/credentials)

**Account Safety**:

- Cache stores `account_id` with each entry
- Automatic cache invalidation on account switch
- Prevents cross-account data leakage

### Sensitive Data Handling

**Not Logged**:

- AWS credentials or temporary tokens
- Resource content (S3 objects, secrets)

**Logged** (debug mode):

- API call parameters (resource IDs, filters)
- Response metadata (status codes, timing)
- Command execution trace

### Input Validation

**Models Layer** (`models/*.py`):

- Pydantic validation on all AWS responses
- CIDR format validation
- Resource ID format checking
- Prevents injection via malformed inputs

---

## Troubleshooting & Debugging

### Debug Mode

**Enable** via runner:

```bash
aws-net-runner --debug "show vpcs" "set vpc 1"
# Logs to: /tmp/aws_net_runner_debug_<timestamp>.log
```

**Log Contents**:

- Command execution timeline
- AWS API calls with parameters
- Cache hits/misses
- Context navigation events
- Error stack traces

### Graph Validation

**Check command hierarchy integrity**:

```bash
aws-net> show graph validate
✓ Graph is valid - all handlers implemented

# Or find missing handlers
✗ Missing handler for 'show xyz' in context 'vpc'
```

### Common Issues

**Issue**: Commands not appearing in context

- **Cause**: Missing in `HIERARCHY` dict
- **Fix**: Add to context's "commands" list

**Issue**: Cache not clearing

- **Cause**: Using wrong cache key name
- **Fix**: Use `refresh all` or check `cache_mappings` in `do_refresh()`

**Issue**: AWS API throttling

- **Cause**: Too many concurrent requests
- **Fix**: Reduce `AWS_NET_MAX_WORKERS` env var (default 10)

---

## Performance Metrics

### Typical Command Latency

| Operation | Cold (No Cache) | Warm (Cached) |
|-----------|----------------|---------------|
| `show vpcs` (5 regions) | 800ms | 5ms |
| `show elbs` (3 regions) | 1.2s | 8ms |
| `set vpc 1` (detail fetch) | 400ms | 15ms |
| `find_prefix` (routing cache) | 50ms | 5ms |
| `show graph` | 10ms | N/A |
| `refresh elb` | 2ms | N/A |

### Memory Usage

| Component | Typical | Max |
|-----------|---------|-----|
| Shell process | 45 MB | 120 MB |
| Memory cache | 2-10 MB | 50 MB |
| File cache | 5-20 MB | 100 MB |

---

## Appendix

### Complete Module List

**AWS Service Modules** (23 total):

1. `cloudwan.py` - Cloud WAN & Global Networks
2. `vpc.py` - VPCs, Subnets, Route Tables
3. `tgw.py` - Transit Gateways, Attachments
4. `ec2.py` - EC2 Instances
5. `anfw.py` - Network Firewall
6. `elb.py` - Load Balancers (ALB/NLB/CLB)
7. `vpn.py` - Site-to-Site VPN
8. `eni.py` - Elastic Network Interfaces
9. `security.py` - Security Groups & NACLs
10. `flowlogs.py` - VPC Flow Logs
11. `route53_resolver.py` - Route 53 Resolver
12. `direct_connect.py` - Direct Connect
13. `client_vpn.py` - Client VPN Endpoints
14. `global_accelerator.py` - Global Accelerator
15. `privatelink.py` - PrivateLink (VPC Endpoints)
16. `peering.py` - VPC Peering Connections
17. `prefix_lists.py` - Managed Prefix Lists
18. `network_alarms.py` - CloudWatch Network Alarms
19. `org.py` - AWS Organizations integration
20. `reachability.py` - Reachability Analyzer
21. `traceroute.py` - Network path tracing
22. `ip_finder.py` - Multi-service IP search

### Command Count by Context

| Context | Show Commands | Set Commands | Actions | Total |
|---------|--------------|--------------|---------|-------|
| Root | 34 | 14 | 10 | 58 |
| global-network | 2 | 1 | 0 | 3 |
| core-network | 11 | 1 | 2 | 14 |
| route-table | 1 | 0 | 2 | 3 |
| vpc | 8 | 1 | 2 | 11 |
| transit-gateway | 3 | 1 | 2 | 6 |
| firewall | 7 | 1 | 0 | 8 |
| rule-group | 1 | 0 | 0 | 1 |
| ec2-instance | 4 | 0 | 0 | 4 |
| elb | 4 | 0 | 0 | 4 |
| vpn | 2 | 0 | 0 | 2 |
| **Total** | **77** | **19** | **18** | **114** |

### Refresh Command Cache Mappings

```python
cache_mappings = {
    "elb": "elb",
    "elbs": "elb",
    "vpc": "vpcs",
    "vpcs": "vpcs",
    "tgw": "transit_gateways",
    "transit-gateway": "transit_gateways",
    "transit-gateways": "transit_gateways",
    "firewall": "firewalls",
    "firewalls": "firewalls",
    "ec2": "ec2_instances",
    "ec2-instance": "ec2_instances",
    "vpn": "vpns",
    "vpns": "vpns",
    "global-network": "global_networks",
    "core-network": "core_networks",
    "eni": "enis",
    "enis": "enis",
}
```

---

## Contributing

### Code Style

- **Python**: PEP 8 compliance with Black formatting
- **Type Hints**: Required for all public methods
- **Docstrings**: Google-style for all classes and functions
- **Imports**: Absolute imports from package root

### Testing Requirements

- **Unit Tests**: All new handlers require tests
- **Mocking**: Use `pytest-mock` for AWS API responses
- **Coverage**: Maintain >80% coverage for new code
- **Integration**: Add to `tests/integration/` for multi-module tests

### Pull Request Checklist

- [ ] Tests added with >80% coverage
- [ ] Documentation updated (README, ARCHITECTURE, command-hierarchy)
- [ ] Graph validation passes (`show graph validate`)
- [ ] No TODO/FIXME comments without linked issues
- [ ] Changelog entry added

---

## Glossary

- **Context**: Current CLI scope (vpc, transit-gateway, etc.)
- **Context Stack**: Navigation history (breadcrumb trail)
- **Handler**: Shell command implementation (do_show,_set_vpc, etc.)
- **Module**: AWS service integration (CloudWANClient, VPCClient)
- **Mixin**: Composable class adding commands to shell
- **Cache Key**: String identifier for cached data ("vpcs", "elb", etc.)
- **TTL**: Time-to-live for cache entries (seconds)
- **Namespace**: Cache isolation boundary (prevents key collisions)

---

**Generated**: 2026-04-06
**Repository**: <https://github.com/[your-org]/aws-network-shell>
**Documentation**: See `docs/` for command hierarchy and testing guides
