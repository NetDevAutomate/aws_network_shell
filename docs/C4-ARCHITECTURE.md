# C4 Architecture: AWS Network Shell

A multi-level architecture document following the C4 model (Context, Containers, Components, Code).

---

## Table of Contents

1. [Level 1: System Context](#level-1-system-context)
2. [Level 2: Container Diagram](#level-2-container-diagram)
3. [Level 3: Component Diagrams](#level-3-component-diagrams)
   - [Shell Components](#31-shell-components)
   - [Core Components](#32-core-components)
   - [Module Components](#33-module-components)
   - [Traceroute Components](#34-traceroute-components)
4. [Level 4: Code-Level Class Diagrams](#level-4-code-level-class-diagrams)
   - [BaseClient Inheritance](#41-baseclient-inheritance-hierarchy)
   - [Shell Composition](#42-shell-composition-via-mixins)
   - [ModuleInterface Hierarchy](#43-moduleinterface-hierarchy)
   - [Pydantic Model Hierarchy](#44-pydantic-model-hierarchy)
5. [Interface Descriptions](#interface-descriptions)

---

## Level 1: System Context

The System Context diagram places AWS Network Shell within its environment, showing who uses it and what external systems it depends on.

**Three distinct user roles interact with the system.** Network Engineers use the interactive shell for live investigation. Automation systems use the runner for scripted workflows. Both invoke the same underlying capabilities. The traceroute engine is available to all three entry points.

The system depends on two external systems: the AWS Cloud (multiple service APIs) and the local filesystem (cache persistence, configuration, output files).

```mermaid
C4Context
    title System Context - AWS Network Shell

    Person(network_eng, "Network Engineer", "Investigates AWS networking topology, routes, firewalls, and connectivity problems interactively")
    Person(devops, "DevOps / Automation", "Runs scripted command sequences against the shell for CI pipelines, auditing, or reporting")
    Person(ops_user, "Operator", "Traces network paths between two IP addresses to diagnose routing and security issues")

    System(aws_net_shell, "AWS Network Shell", "aws-network-tools v0.1.0. Cisco IOS-style hierarchical CLI for AWS networking resources. Provides 100+ commands across VPC, TGW, Cloud WAN, Firewall, EC2, ELB, and VPN contexts.")

    System_Ext(aws_cloud, "AWS Cloud", "EC2, NetworkManager, NetworkFirewall, ELBv2, SSM, STS APIs across multiple regions")
    System_Ext(local_fs, "Local Filesystem", "Cache JSON files, SQLite database, config.json, output files. Located under ~/.cache and ~/.config")

    Rel(network_eng, aws_net_shell, "Uses", "aws-net-shell (interactive terminal)")
    Rel(devops, aws_net_shell, "Automates", "aws-net-runner (pexpect-based runner)")
    Rel(ops_user, aws_net_shell, "Traces paths", "aws-trace <src_ip> <dst_ip>")
    Rel(aws_net_shell, aws_cloud, "Queries", "boto3 / botocore HTTPS")
    Rel(aws_net_shell, local_fs, "Reads / writes", "JSON cache files, SQLite DB, config JSON")
```

---

## Level 2: Container Diagram

The Container diagram zooms into the AWS Network Shell system, showing the deployable units and how they communicate. All containers run as a single installed Python package (`aws-network-tools`).

The three entry-point containers are independent executables defined in `pyproject.toml`. They share the Core Services and Module Layer through direct Python imports. Cache state is shared on the local filesystem, allowing a topology populated by one entry point to be read by another.

```mermaid
C4Container
    title Container Diagram - AWS Network Shell

    Person(user, "User")

    System_Boundary(pkg, "aws-network-tools") {

        Container(interactive_shell, "Interactive Shell", "Python / cmd2", "Cisco IOS-style REPL. Manages context stack (VPC, TGW, Cloud WAN, etc.), prompt rendering, command dispatch, and in-memory session cache. Entry point: aws-net-shell")

        Container(automation_runner, "Automation Runner", "Python / pexpect", "Spawns the interactive shell as a subprocess, sends command sequences, captures output, strips ANSI codes. Entry point: aws-net-runner")

        Container(traceroute_engine, "Traceroute Engine", "Python / asyncio", "Deterministic API-driven path tracer. Resolves source and destination ENIs, walks route tables, TGWs, Cloud WAN segments, and NFGs. Entry point: aws-trace")

        Container(core_services, "Core Services", "Python", "Cross-cutting infrastructure: BaseClient (boto3 wrapper), Cache (TTL JSON files), CacheDB (SQLite), RuntimeConfig (singleton), DisplayRenderer, run_with_spinner")

        Container(module_layer, "AWS Module Layer", "Python / boto3", "22 service-specific clients. Each module follows the Client/Display pattern (e.g., CloudWANClient, VPCClient). Covers CloudWAN, VPC, TGW, EC2, ANFW, ELB, VPN, ENI, security groups, flow logs, and more")

        Container(data_models, "Data Models", "Python / Pydantic v2", "Validated resource representations: AWSResource, VPCModel, TGWModel, CoreNetworkModel. Provide field validation and type-safe dict conversion")
    }

    ContainerDb(file_cache, "File Cache Store", "JSON files on disk", "Per-namespace TTL cache files. Default path: ~/.cache/aws-network-tools/<namespace>.json. Stores AWS API responses with expiry metadata and account ID safety check")

    ContainerDb(sqlite_db, "SQLite Cache DB", "SQLite", "Persistent routing and topology cache. Tables: routing_cache (routes by VPC/TGW/CloudWAN), topology_cache (general key/value). Path: ~/.config/aws_network_shell/cache.db")

    System_Ext(aws_apis, "AWS APIs", "EC2, NetworkManager, NetworkFirewall, ELBv2, SSM, STS")

    Rel(user, interactive_shell, "Types commands", "stdin / stdout (terminal)")
    Rel(user, automation_runner, "Invokes with command list", "CLI args or stdin")
    Rel(user, traceroute_engine, "Invokes with src/dst IPs", "CLI args")

    Rel(automation_runner, interactive_shell, "Spawns and drives", "pexpect subprocess")
    Rel(interactive_shell, core_services, "Uses", "Python import")
    Rel(interactive_shell, module_layer, "Delegates API calls to", "Python import")
    Rel(interactive_shell, data_models, "Validates resources with", "Python import")
    Rel(traceroute_engine, core_services, "Uses Cache and BaseClient via", "Python import")
    Rel(traceroute_engine, aws_apis, "Discovers topology", "boto3 async/threaded")
    Rel(module_layer, core_services, "Inherits BaseClient, uses Cache", "Python import")
    Rel(module_layer, aws_apis, "Queries", "boto3 HTTPS")
    Rel(core_services, file_cache, "Reads / writes", "JSON file I/O")
    Rel(core_services, sqlite_db, "Reads / writes", "sqlite3")
    Rel(traceroute_engine, file_cache, "Caches topology", "via Cache class")
```

---

## Level 3: Component Diagrams

### 3.1 Shell Components

The Shell layer is built around `cmd2.Cmd`. The base class handles all context state and prompt rendering. Nine handler mixin classes each own a specific domain. `AWSNetShell` composes them all through Python's MRO and adds the `do_show` / `do_set` dispatch loop. `CommandGraph` and `CommandDiscovery` provide introspection, validation, and Mermaid export capabilities.

```mermaid
C4Component
    title Component Diagram - Shell Layer (shell/)

    Container_Boundary(shell_pkg, "Interactive Shell") {

        Component(aws_net_shell, "AWSNetShell", "Python class", "Top-level shell class. Composes all 9 handler mixins into a single object via Python MRO. Implements do_show(), do_set(), _cached(), and _emit_json_or_table(). Entry point for cmdloop()")

        Component(aws_net_shell_base, "AWSNetShellBase", "cmd2.Cmd subclass", "Base context management: context_stack (list of Context), _update_prompt(), _enter(), _resolve(), do_exit(), do_end(), do_refresh(). Holds HIERARCHY dict and ALIASES dict. Initialises RuntimeConfig and theme on startup")

        Component(root_mixin, "RootHandlersMixin", "Mixin class", "Handles show/set commands at the root context: show vpcs, show transit-gateways, show global-networks, find_ip, find_prefix, populate_cache, routing cache management")
        Component(cloudwan_mixin, "CloudWANHandlersMixin", "Mixin class", "Handles Cloud WAN context: show core-networks, show segments, show routes, show RIB, set core-network, set route-table, policy document diff")
        Component(vpc_mixin, "VPCHandlersMixin", "Mixin class", "Handles VPC context: show detail, show subnets, show route-tables, show security-groups, show NACLs, set route-table, find-prefix, find-null-routes")
        Component(tgw_mixin, "TGWHandlersMixin", "Mixin class", "Handles Transit Gateway context: show attachments, show route-tables, set route-table, find-prefix, find-null-routes")
        Component(ec2_mixin, "EC2HandlersMixin", "Mixin class", "Handles EC2 instance context: show detail, show security-groups, show ENIs, show routes")
        Component(firewall_mixin, "FirewallHandlersMixin", "Mixin class", "Handles AWS Network Firewall context: show firewall, show policy, show rule-groups, set rule-group")
        Component(vpn_mixin, "VPNHandlersMixin", "Mixin class", "Handles Site-to-Site VPN context: show detail, show tunnels")
        Component(elb_mixin, "ELBHandlersMixin", "Mixin class", "Handles Elastic Load Balancer context: show detail, show listeners, show targets, show health")
        Component(utility_mixin, "UtilityHandlersMixin", "Mixin class", "Cross-cutting utilities: trace, write, export_graph, validate_graph, clear_cache commands")

        Component(command_graph, "CommandGraph", "Python class", "Graph representation of the full command hierarchy. Built from HIERARCHY dict via introspection. Nodes: CommandNode (id, name, NodeType, handler, implemented). Edges: GraphEdge. Methods: build(), validate(), to_mermaid(), find_command_path()")
        Component(command_discovery, "CommandDiscovery", "Python class", "Derives list/set command mappings dynamically from HIERARCHY. Provides PLURAL_MAP and SET_ALIASES. Eliminates hardcoded mappings that can drift from the canonical hierarchy")
        Component(arguments, "arguments.py", "Module", "Argument parser definitions for shell commands")
    }

    Rel(aws_net_shell, aws_net_shell_base, "Inherits (via MRO)")
    Rel(aws_net_shell, root_mixin, "Inherits")
    Rel(aws_net_shell, cloudwan_mixin, "Inherits")
    Rel(aws_net_shell, vpc_mixin, "Inherits")
    Rel(aws_net_shell, tgw_mixin, "Inherits")
    Rel(aws_net_shell, ec2_mixin, "Inherits")
    Rel(aws_net_shell, firewall_mixin, "Inherits")
    Rel(aws_net_shell, vpn_mixin, "Inherits")
    Rel(aws_net_shell, elb_mixin, "Inherits")
    Rel(aws_net_shell, utility_mixin, "Inherits")
    Rel(utility_mixin, command_graph, "Calls build(), validate(), to_mermaid()")
    Rel(aws_net_shell_base, command_discovery, "Uses for completion")
    Rel(aws_net_shell_base, arguments, "Uses for argument parsing")
```

### 3.2 Core Components

Core Services provide infrastructure used by both the Shell layer and the Module layer. `RuntimeConfig` is a thread-safe singleton that propagates shell state (profile, regions, output format) to modules without requiring explicit parameter passing. `BaseClient` reads from `RuntimeConfig` to create correctly configured boto3 sessions.

```mermaid
C4Component
    title Component Diagram - Core Services (core/)

    Container_Boundary(core_pkg, "Core Services") {

        Component(base_client, "BaseClient", "Python class", "boto3 wrapper. Reads profile from RuntimeConfig if not explicitly provided. Creates boto3.Session per instance. Provides client(service, region) factory with DEFAULT_BOTO_CONFIG (retries, timeouts, custom user-agent). get_regions() resolves target regions from RuntimeConfig or session default")

        Component(module_interface, "ModuleInterface", "ABC", "Abstract base for all module classes. Properties: name (str), commands (dict), context_commands (dict), show_commands (dict). Abstract method: execute(shell, command, args). Enforces the module contract")

        Component(cache, "Cache", "Python class", "File-based TTL cache. One instance per namespace (e.g., Cache('cloudwan')). File path: ~/.cache/aws-network-tools/<namespace>.json. Methods: get(ignore_expiry, current_account), set(data, ttl_seconds, account_id), clear(), get_info(). Account ID safety: clears cache on account mismatch. Default TTL: 900s (configurable)")

        Component(cache_db, "CacheDB", "Python class", "SQLite-backed persistent cache. Path: ~/.config/aws_network_shell/cache.db. Two tables: routing_cache (routes with source/resource/destination columns, indexed) and topology_cache (key/value JSON). Methods: save_routing_cache(), load_routing_cache(), save_topology_cache(), load_topology_cache(), clear_all(), get_stats()")

        Component(runtime_config, "RuntimeConfig", "Singleton class", "Thread-safe singleton (double-checked locking). Holds: _profile (str|None), _regions (list[str]), _no_cache (bool), _output_format (str). Class methods: set_profile/get_profile, set_regions/get_regions, set_no_cache/is_cache_disabled, set_output_format/get_output_format, reset(). Shell calls set_* on startup and on each set command; modules call get_*")

        Component(display_renderer, "DisplayRenderer", "Python class", "Unified Rich output renderer. Methods: render(data, fmt, title, columns) for JSON/YAML bypass, table(data, title, columns, show_index, hint) for Rich Table, detail(data, title, fields) for Panel view, routes(routes, title) for route table, status/error/warning/info for styled messages. COLORS dict for resource-type and state coloring")

        Component(base_display, "BaseDisplay", "Python class", "Lightweight display base inherited by module Display classes. Provides: print_cache_info(cache_info), route_table(title, routes, columns). Wraps rich.console.Console")

        Component(spinner, "run_with_spinner", "Function", "Wraps a callable in a Rich Live spinner in a background thread. Detects CI/non-TTY environments and disables the spinner automatically. Enforces a configurable timeout (default 300s). Used by AWSNetShell._cached() and directly by module clients")

        Component(config_cls, "Config", "Python class", "JSON config file manager. Path: ~/.config/aws_network_shell/config.json. Dot-notation get/set. Manages prompt (style, theme, show_indices, max_length), display (output_format, colors, pager), and cache settings")
    }

    Rel(base_client, runtime_config, "Reads profile and regions from")
    Rel(cache_db, cache, "Shares file-based storage layer concept; both write under ~/.config and ~/.cache")
    Rel(display_renderer, base_display, "Supersedes for unified rendering")
    Rel(spinner, base_client, "Called by modules to wrap boto3 calls")
```

### 3.3 Module Components

Each of the 22 modules follows the same structural pattern: a `Client` class (inherits `BaseClient`) handles all API calls; a `Display` class (inherits `BaseDisplay`) handles all Rich rendering; a `Module` class (implements `ModuleInterface`) provides the shell integration contract.

```mermaid
C4Component
    title Component Diagram - AWS Module Layer (modules/)

    Container_Boundary(modules_pkg, "AWS Module Layer") {

        Component(cloudwan_client, "CloudWANClient", "BaseClient subclass", "NetworkManager API: describe_global_networks, list_core_networks, get_core_network, list_attachments, get_core_network_route_table, get_network_routes, get_core_network_policy")
        Component(cloudwan_display, "CloudWANDisplay", "BaseDisplay subclass", "Rich rendering for Cloud WAN resources: global networks table, core network detail panel, route tables, RIB, segments, policy documents, connect peers")
        Component(cloudwan_module, "CloudWANModule", "ModuleInterface impl", "name='cloudwan'. show_commands: global-networks, core-networks, policy-documents, routes, RIB, segments, connect-attachments, connect-peers. Implements execute()")

        Component(vpc_client, "VPCClient", "BaseClient subclass", "EC2 API: describe_vpcs, describe_subnets, describe_route_tables, describe_security_groups, describe_network_acls, describe_internet_gateways, describe_nat_gateways, describe_vpc_endpoints. Multi-region with ThreadPoolExecutor")
        Component(vpc_display, "VPCDisplay", "BaseDisplay subclass", "Rich rendering for VPC resources: VPC list table, subnet tree, route table with state coloring, security group rules, NACL rules")
        Component(vpc_module, "VPCModule", "ModuleInterface impl", "name='vpc'. show_commands: vpcs, detail, route-tables, subnets, security-groups, nacls, internet-gateways, nat-gateways, endpoints")

        Component(tgw_client, "TGWClient", "BaseClient subclass", "EC2 API: describe_transit_gateways, describe_transit_gateway_route_tables, search_transit_gateway_routes, describe_transit_gateway_attachments. Multi-region support")
        Component(tgw_display, "TGWDisplay", "BaseDisplay subclass", "Rich rendering for TGW resources: TGW list, route table detail, attachment list with type coloring")
        Component(tgw_module, "TGWModule", "ModuleInterface impl", "name='tgw'. show_commands: transit-gateways, detail, route-tables, attachments")

        Component(anfw_client, "ANFWClient", "BaseClient subclass", "NetworkFirewall API: list_firewalls, describe_firewall, describe_firewall_policy, list_rule_groups, describe_rule_group")
        Component(anfw_display, "ANFWDisplay", "BaseDisplay subclass", "Rich rendering for firewall resources: firewall list, policy detail, rule group rules")
        Component(anfw_module, "ANFWModule", "ModuleInterface impl", "name='anfw'. show_commands: firewalls, detail, policy, rule-groups, firewall-rule-groups")

        Component(other_modules, "Other Modules (15)", "BaseClient / BaseDisplay / ModuleInterface pattern", "ec2.py: EC2 instances (EC2Client, EC2Display, EC2Module). elb.py: Load balancers (ELBClient, ELBDisplay, ELBModule). vpn.py: Site-to-Site VPN. eni.py: Elastic Network Interfaces. security.py: Security groups. flowlogs.py: VPC Flow Logs. direct_connect.py: DX connections. peering.py: VPC peering. prefix_lists.py: Managed prefix lists. network_alarms.py: CloudWatch alarms. client_vpn.py: Client VPN. global_accelerator.py: Global Accelerator. route53_resolver.py: Route53 Resolver. privatelink.py: PrivateLink endpoints. reachability.py: VPC Reachability Analyzer. ip_finder.py: IP search across regions. org.py: AWS Organizations")
    }

    Rel(cloudwan_client, cloudwan_display, "Provides raw data to")
    Rel(cloudwan_module, cloudwan_client, "Delegates API calls to")
    Rel(cloudwan_module, cloudwan_display, "Delegates rendering to")

    Rel(vpc_client, vpc_display, "Provides raw data to")
    Rel(vpc_module, vpc_client, "Delegates API calls to")
    Rel(vpc_module, vpc_display, "Delegates rendering to")

    Rel(other_modules, anfw_client, "Same Client/Display/Module pattern")
```

### 3.4 Traceroute Components

The Traceroute Engine operates asynchronously. `TopologyDiscovery` runs three parallel coroutines (Cloud WAN, TGWs, VPCs) across all AWS regions. `AWSTraceroute.trace()` is the single public method: it ensures topology is loaded, resolves ENIs, then walks the path hop by hop. `StalenessChecker` performs a lightweight pre-flight comparison (a few API calls) rather than a full rediscovery to decide whether the cached topology is still valid.

```mermaid
C4Component
    title Component Diagram - Traceroute Engine (traceroute/)

    Container_Boundary(trace_pkg, "Traceroute Engine") {

        Component(tracer_cli, "traceroute/cli.py main()", "CLI entry point", "Parses sys.argv. Handles --clear-cache, --profile, --no-cache, --refresh-cache, --skip-stale-check flags. Wires on_hop and on_status callbacks for Rich console output. Calls asyncio.run(tracer.trace(src, dst)). Entry point registered as aws-trace")

        Component(aws_traceroute, "AWSTraceroute", "Python class (async)", "Core path tracing engine. Constructor: profile, on_hop, on_status, no_cache, refresh_cache, skip_stale_check. _topology: NetworkTopology (lazily loaded). _discovery: TopologyDiscovery. Public method: async trace(src_ip, dst_ip) -> TraceResult. Internal: _ensure_topology(), _find_eni_cached(), _find_best_route() (longest prefix match), _trace_via_cloudwan(), _trace_via_tgw(), _get_subnet_route_table(). Uses ThreadPoolExecutor(max_workers=10) for blocking boto3 calls")

        Component(topology_discovery, "TopologyDiscovery", "Python class (async)", "Discovers and caches full network topology. CACHE_NAMESPACE='topology'. Constructor: profile, on_status. Methods: discover(regions) -> NetworkTopology (parallel asyncio.gather for Cloud WAN + TGWs + VPCs), _build_eni_index() (ip -> ENI map), get_cached(check_staleness) -> NetworkTopology|None, clear_cache(). Uses ThreadPoolExecutor(max_workers=20). Writes topology to Cache on completion. Saves staleness markers via StalenessChecker")

        Component(network_topology, "NetworkTopology", "Python dataclass", "In-memory topology snapshot. Fields: account_id, regions, global_networks, core_networks, cwan_attachments, cwan_policy, tgws (region->list), tgw_route_tables (tgw_id->list), vpcs (region->list), route_tables (subnet_id->dict), eni_index (ip->dict). Serialised to JSON by Cache.set() via dataclasses.asdict()")

        Component(staleness_checker, "StalenessChecker", "Python class", "Lightweight cache validity check. MARKERS_CACHE='topology_markers'. get_current_markers(regions) makes ~2+2n API calls (Cloud WAN policy version, attachment count, TGW count per region, VPC count per region). save_markers() / get_saved_markers() use Cache class. is_stale(regions) -> tuple[bool, str]: compares saved vs current markers for policy version, attachment count, and per-region TGW/VPC counts")

        Component(trace_models, "Hop / TraceResult / SecurityCheck", "Python dataclasses", "Hop: seq, type (HopType literal), id, name, region, detail. HopType values: eni, route_table, cloud_wan_segment, nfg, firewall, destination. TraceResult: src_ip, dst_ip, reachable, hops (list[Hop]), security_checks, blocked_at (Hop|None), blocked_reason. SecurityCheck: component, id, verdict (allow/deny/unknown), reason. TraceResult.summary() produces human-readable path output")

        Component(eni_info, "ENIInfo", "Python dataclass", "Resolved ENI: eni_id, ip, vpc_id, subnet_id, region, security_groups. Internal to AWSTraceroute for path walking state")
    }

    Rel(tracer_cli, aws_traceroute, "Instantiates and calls trace()")
    Rel(aws_traceroute, topology_discovery, "Delegates topology loading to (_discovery)")
    Rel(aws_traceroute, network_topology, "Holds reference to (_topology)")
    Rel(aws_traceroute, trace_models, "Builds Hop objects, returns TraceResult")
    Rel(aws_traceroute, eni_info, "Uses internally for resolved ENI state")
    Rel(topology_discovery, network_topology, "Creates and populates")
    Rel(topology_discovery, staleness_checker, "Checks staleness before returning cached; saves markers after discovery")
    Rel(topology_discovery, trace_models, "Indirectly: topology feeds route resolution in AWSTraceroute")
```

---

## Level 4: Code-Level Class Diagrams

### 4.1 BaseClient Inheritance Hierarchy

All 22 module clients inherit from `BaseClient`. They gain a configured `boto3.Session`, the `client(service, region)` factory, and `get_regions()` which reads from `RuntimeConfig`.

```mermaid
classDiagram
    class BaseClient {
        +profile: Optional[str]
        +session: boto3.Session
        +max_workers: int
        +__init__(profile, session, max_workers)
        +client(service, region_name) boto3.client
        +get_regions() list[str]
    }

    class CloudWANClient {
        +get_global_networks() list
        +get_core_networks(global_network_id) list
        +get_core_network_detail(core_network_id) dict
        +get_core_network_policy(core_network_id) dict
        +list_attachments(core_network_id) list
        +get_network_routes(core_network_id, route_table_id, filters) list
    }

    class VPCClient {
        +get_vpcs(regions) list
        +get_vpc_detail(vpc_id, region) dict
        +get_route_tables(vpc_id, region) list
        +get_subnets(vpc_id, region) list
        +get_security_groups(vpc_id, region) list
        +get_nacls(vpc_id, region) list
    }

    class TGWClient {
        +get_transit_gateways(regions) list
        +get_tgw_route_tables(tgw_id, region) list
        +search_routes(route_table_id, region, filters) list
        +get_attachments(tgw_id, region) list
    }

    class ANFWClient {
        +get_firewalls(regions) list
        +get_firewall_detail(firewall_name, region) dict
        +get_firewall_policy(policy_arn) dict
        +list_rule_groups(policy_arn) list
        +get_rule_group(rule_group_arn) dict
    }

    class ELBClient {
        +get_load_balancers(regions) list
        +get_elb_detail(elb_arn, region) dict
        +get_listeners(elb_arn, region) list
        +get_target_groups(elb_arn, region) list
        +get_target_health(target_group_arn, region) list
    }

    class EC2Client {
        +get_instances(regions, filters) list
        +get_instance_detail(instance_id, region) dict
        +get_instance_enis(instance_id, region) list
    }

    class VPNClient {
        +get_vpn_connections(regions) list
        +get_vpn_detail(vpn_id, region) dict
        +get_tunnel_status(vpn_id, region) list
    }

    BaseClient <|-- CloudWANClient
    BaseClient <|-- VPCClient
    BaseClient <|-- TGWClient
    BaseClient <|-- ANFWClient
    BaseClient <|-- ELBClient
    BaseClient <|-- EC2Client
    BaseClient <|-- VPNClient
    BaseClient <|-- "ENIClient\nDirectConnectClient\nSecurityClient\nFlowLogsClient\nPeeringClient\nPrefixListsClient\nNetworkAlarmsClient\nClientVPNClient\nGlobalAcceleratorClient\nRoute53ResolverClient\nPrivateLinkClient\nReachabilityClient\nIPFinderClient\nOrgClient"
```

### 4.2 Shell Composition via Mixins

`AWSNetShell` is assembled through Python's cooperative multiple inheritance (MRO). The order of base classes in the class definition controls which mixin's method wins when names collide. `AWSNetShellBase` always resolves last and provides the `cmd2.Cmd` foundation.

```mermaid
classDiagram
    direction TB

    class `cmd2.Cmd` {
        +cmdloop()
        +onecmd(line)
        +default(stmt)
        +precmd(line)
    }

    class AWSNetShellBase {
        +intro: str
        +profile: Optional[str]
        +regions: list[str]
        +no_cache: bool
        +output_format: str
        +watch_interval: int
        +context_stack: list[Context]
        +_cache: dict
        +config: Config
        +theme: dict
        +ctx: Optional[Context]
        +ctx_type: Optional[str]
        +ctx_id: str
        +hierarchy: dict
        +__init__()
        +_update_prompt()
        +_enter(ctx_type, res_id, name, data, selection_index)
        +_resolve(items, val) Optional[dict]
        +_sync_runtime_config()
        +do_exit(args)
        +do_end(args)
        +do_refresh(args)
        +do_clear(args)
        +do_clear_cache(args)
        +precmd(line) Statement
        +default(stmt)
    }

    class RootHandlersMixin {
        +_show_vpcs(arg)
        +_show_transit_gateways(arg)
        +_show_global_networks(arg)
        +_show_firewalls(arg)
        +_show_ec2_instances(arg)
        +_show_elbs(arg)
        +_show_vpns(arg)
        +_set_vpc(val)
        +_set_transit_gateway(val)
        +_set_global_network(val)
        +do_find_ip(args)
        +do_populate_cache(args)
        +do_create_routing_cache(args)
        +do_save_routing_cache(args)
        +do_load_routing_cache(args)
    }

    class CloudWANHandlersMixin {
        +_show_core_networks(arg)
        +_show_segments(arg)
        +_show_routes(arg)
        +_show_rib(arg)
        +_show_policy_documents(arg)
        +_show_live_policy(arg)
        +_show_connect_attachments(arg)
        +_set_core_network(val)
        +_set_route_table(val)
        +_cloudwan_find_prefix(prefix)
        +_cloudwan_find_null_routes()
    }

    class VPCHandlersMixin {
        +_show_subnets(arg)
        +_show_vpc_route_tables()
        +_show_security_groups(arg)
        +_show_nacls(arg)
        +_show_internet_gateways(arg)
        +_show_nat_gateways(arg)
        +_show_endpoints(arg)
        +_vpc_find_prefix(prefix)
        +_vpc_find_null_routes()
    }

    class TGWHandlersMixin {
        +_show_transit_gateway_route_tables()
        +_show_attachments(arg)
        +_tgw_find_prefix(prefix)
        +_tgw_find_null_routes()
    }

    class EC2HandlersMixin {
        +_show_enis(arg)
        +_show_ec2_routes(arg)
    }

    class FirewallHandlersMixin {
        +_show_firewall(arg)
        +_show_firewall_rule_groups(arg)
        +_show_rule_groups(arg)
        +_show_policy(arg)
        +_set_rule_group(val)
    }

    class VPNHandlersMixin {
        +_show_tunnels(arg)
        +_show_vpn_detail(arg)
    }

    class ELBHandlersMixin {
        +_show_listeners(arg)
        +_show_targets(arg)
        +_show_health(arg)
    }

    class UtilityHandlersMixin {
        +do_trace(args)
        +do_write(args)
        +do_export_graph(args)
        +do_validate_graph(args)
        +do_find_ip(args)
        +do_find_prefix(args)
        +do_find_null_routes(args)
    }

    class AWSNetShell {
        +_cached(key, fetch_fn, msg) Any
        +_emit_json_or_table(data, render_table_fn)
        +do_show(args)
        +do_set(args)
        +complete_show(text, line, begidx, endidx) list
        +complete_set(text, line, begidx, endidx) list
        +_show_detail(arg)
        +_show_route_tables(arg)
        +_run_with_pipe(fn, pipe_filter)
        +_watch_loop(fn, interval)
        +do_find_prefix(args)
        +do_find_null_routes(args)
    }

    `cmd2.Cmd` <|-- AWSNetShellBase
    AWSNetShellBase <|-- AWSNetShell
    RootHandlersMixin <|-- AWSNetShell
    CloudWANHandlersMixin <|-- AWSNetShell
    VPCHandlersMixin <|-- AWSNetShell
    TGWHandlersMixin <|-- AWSNetShell
    EC2HandlersMixin <|-- AWSNetShell
    FirewallHandlersMixin <|-- AWSNetShell
    VPNHandlersMixin <|-- AWSNetShell
    ELBHandlersMixin <|-- AWSNetShell
    UtilityHandlersMixin <|-- AWSNetShell

    note for AWSNetShell "MRO resolution order (left to right, then base):\nRootHandlersMixin -> CloudWANHandlersMixin -> VPCHandlersMixin\n-> TGWHandlersMixin -> EC2HandlersMixin -> FirewallHandlersMixin\n-> VPNHandlersMixin -> ELBHandlersMixin -> UtilityHandlersMixin\n-> AWSNetShellBase -> cmd2.Cmd"
```

### 4.3 ModuleInterface Hierarchy

Each module implements the `ModuleInterface` ABC. The `execute()` method is the single dispatch point: the shell calls it with a command name and args. Display classes inherit `BaseDisplay` for shared Rich rendering utilities.

```mermaid
classDiagram
    class ModuleInterface {
        <<abstract>>
        +name: str
        +commands: Dict[str, str]
        +context_commands: Dict[str, List[str]]
        +show_commands: Dict[str, List[str]]
        +execute(shell, command, args)*
    }

    class BaseDisplay {
        +console: Console
        +__init__(console)
        +print_cache_info(cache_info)
        +route_table(title, routes, columns) Table
    }

    class CloudWANModule {
        +name = "cloudwan"
        +execute(shell, command, args)
    }
    class CloudWANDisplay {
        +show_global_networks(data)
        +show_detail(data)
        +show_route_table(data)
        +show_rib(data)
        +show_segments(data)
        +show_firewall_detail(data)
    }

    class VPCModule {
        +name = "vpc"
        +execute(shell, command, args)
    }
    class VPCDisplay {
        +show_vpcs(data)
        +show_detail(data)
        +show_route_tables(data)
        +show_subnets(data)
        +show_security_groups(data)
    }

    class TGWModule {
        +name = "tgw"
        +execute(shell, command, args)
    }
    class TGWDisplay {
        +show_transit_gateways(data)
        +show_tgw_detail(data)
        +show_route_tables(data)
        +show_attachments(data)
    }

    class ANFWModule {
        +name = "anfw"
        +execute(shell, command, args)
    }
    class ANFWDisplay {
        +show_firewalls(data)
        +show_firewall_detail(data)
        +show_policy(data)
        +show_rule_groups(data)
    }

    class ELBModule {
        +name = "elb"
        +execute(shell, command, args)
    }
    class ELBDisplay {
        +show_load_balancers(data)
        +show_elb_detail(data)
        +show_listeners(data)
        +show_targets(data)
    }

    ModuleInterface <|.. CloudWANModule
    ModuleInterface <|.. VPCModule
    ModuleInterface <|.. TGWModule
    ModuleInterface <|.. ANFWModule
    ModuleInterface <|.. ELBModule
    ModuleInterface <|.. "EC2Module\nVPNModule\nENIModule\nSecurityModule\nFlowLogsModule\nDirectConnectModule\nPeeringModule\nPrefixListsModule\nNetworkAlarmsModule\nClientVPNModule\nGlobalAcceleratorModule\nRoute53ResolverModule\nPrivateLinkModule\nReachabilityModule\nIPFinderModule\nOrgModule"

    BaseDisplay <|-- CloudWANDisplay
    BaseDisplay <|-- VPCDisplay
    BaseDisplay <|-- TGWDisplay
    BaseDisplay <|-- ANFWDisplay
    BaseDisplay <|-- ELBDisplay
```

### 4.4 Pydantic Model Hierarchy

All resource models extend `AWSResource`. The `model_config = ConfigDict(extra="allow")` on the base class means AWS API responses can be captured without enumerating every field, while core fields (`id`, `name`, `region`) are strictly validated.

```mermaid
classDiagram
    class AWSResource {
        <<Pydantic BaseModel>>
        +model_config: ConfigDict(extra="allow")
        +id: str
        +name: Optional[str]
        +region: str
        +validate_id(v) str
        +to_dict() dict
    }

    class CIDRBlock {
        <<Pydantic BaseModel>>
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
        +id: str
        +destination: str
        +target: str
        +state: Literal["active", "blackhole"]
        +type: Optional[str]
        +region: str
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
        +nfgs: list[str]
        +route_tables: list[dict]
        +policy: Optional[dict]
        +validate_cn_id(v) str
    }

    class SegmentModel {
        +id: str
        +edge_locations: list[str]
        +isolate_attachments: bool
        +require_attachment_acceptance: bool
    }

    class CloudWANRouteModel {
        +id: str
        +prefix: str
        +target: str
        +target_type: Optional[str]
        +state: Literal["ACTIVE", "BLACKHOLE", "active", "blackhole"]
        +type: Optional[str]
        +region: str
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

    class TGWRouteModel {
        +id: str
        +prefix: str
        +target: str
        +target_type: Optional[str]
        +state: Literal["active", "blackhole"]
        +type: Optional[str]
        +region: str
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
    AWSResource <|-- TGWRouteModel

    VPCModel "1" *-- "0..*" SubnetModel : contains
    VPCModel "1" *-- "0..*" RouteTableModel : contains
    VPCModel "1" *-- "0..*" SecurityGroupModel : contains
    RouteTableModel "1" *-- "0..*" RouteModel : contains
    TGWModel "1" *-- "0..*" TGWAttachmentModel : contains
    TGWModel "1" *-- "0..*" TGWRouteTableModel : contains
    TGWRouteTableModel "1" *-- "0..*" TGWRouteModel : contains
```

---

## Interface Descriptions

This section documents how the major boundaries in the system communicate.

### Shell -> Core Services

| Interface | Mechanism | Description |
|-----------|-----------|-------------|
| `AWSNetShell._cached(key, fetch_fn, msg)` | Direct call | Wraps any fetch function in `run_with_spinner`. The result is stored in the shell's in-memory `_cache` dict keyed by resource type (e.g. `"vpcs"`, `"tgw"`). On `do_refresh`, the key is deleted from `_cache` to force a fresh fetch on the next command |
| `RuntimeConfig.set_*(...)` | Class method (singleton) | Called by `AWSNetShellBase.__init__()` and `_sync_runtime_config()` whenever the shell's `profile`, `regions`, `no_cache`, or `output_format` changes. Propagates state to all modules without parameter threading |
| `Config.get(key)` | Dot-notation accessor | Read on shell startup to load prompt style, theme name, and display settings |

### Shell -> Module Layer

| Interface | Mechanism | Description |
|-----------|-----------|-------------|
| Handler mixin method calls | Direct Python call | Mixins instantiate module Client and Display classes inline, call client methods to fetch data, then pass results to display methods. Example: `_show_vpcs()` in `RootHandlersMixin` calls `VPCClient(...).get_vpcs(regions)` and `VPCDisplay(console).show_vpcs(data)` |
| `ModuleInterface.execute(shell, command, args)` | Interface dispatch | Used by the legacy module-as-plugin path. The shell can delegate a command to a module by calling its `execute()` method |

### Module Layer -> AWS APIs

| Interface | Mechanism | Description |
|-----------|-----------|-------------|
| `BaseClient.client(service, region)` | boto3 factory | Returns a configured boto3 client with `DEFAULT_BOTO_CONFIG`: 10 retries (standard mode), 5s connect timeout, 20s read timeout, custom user-agent string `aws-network-tools/0.1.0`. Profile is sourced from `RuntimeConfig` |
| `BaseClient.get_regions()` | Region resolver | Returns `RuntimeConfig.get_regions()` if set; otherwise falls back to `boto3.Session.region_name`. Module clients iterate this list with `ThreadPoolExecutor` for multi-region queries |

### Traceroute -> Core Services

| Interface | Mechanism | Description |
|-----------|-----------|-------------|
| `Cache("topology").get/set` | File I/O | `TopologyDiscovery` reads the serialised `NetworkTopology` dataclass from `~/.cache/aws-network-tools/topology.json`. On a miss or stale check failure, it re-discovers and writes the result back |
| `Cache("topology_markers").get/set` | File I/O | `StalenessChecker` reads and writes lightweight `ChangeMarkers` to detect topology changes without a full rebuild |

### Core Services -> Local Filesystem

| Path | Component | Content |
|------|-----------|---------|
| `~/.cache/aws-network-tools/<namespace>.json` | `Cache` | Per-namespace TTL cache. Fields: `data`, `cached_at` (UTC ISO), `ttl_seconds`, `account_id` |
| `~/.config/aws_network_shell/cache.db` | `CacheDB` | SQLite database with `routing_cache` and `topology_cache` tables |
| `~/.config/aws_network_shell/config.json` | `Config` | User preferences (prompt style, theme, output format, cache TTL) |
| `~/.cache/aws-network-tools/config.json` | `Cache` module-level | Stores configurable default TTL (seconds) |

### Automation Runner -> Interactive Shell

| Interface | Mechanism | Description |
|-----------|-----------|-------------|
| `ShellRunner.start()` | `pexpect.spawn("aws-net-shell ...")` | Spawns the interactive shell as a child process with a 250-column terminal to avoid Rich table line-wrapping |
| `ShellRunner.run(command)` | `child.sendline(command)` | Sends a command and waits for a stable prompt (3 consecutive 0.1s reads with no new output). Returns clean output with ANSI codes stripped |
| `ShellRunner.run_sequence(commands)` | Loop over `run()` | Skips blank lines and lines starting with `#` (comment support) |
