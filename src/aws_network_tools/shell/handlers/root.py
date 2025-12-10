"""Root-level show/set handlers."""

from rich.table import Table
from rich.console import Console
from ...core.logging import get_logger

console = Console()
logger = get_logger("shell.root")


class RootHandlersMixin:
    """Handlers for root-level commands."""

    def _show_version(self, _):
        """Show CLI version and system information."""
        import platform
        import sys

        try:
            from importlib.metadata import version

            cli_version = version("aws-network-tools")
        except Exception:
            cli_version = "dev"
        console.print("[bold]AWS Network Tools CLI[/]")
        console.print(f"  Version: {cli_version}")
        console.print(f"  Python: {sys.version.split()[0]}")
        console.print(f"  Platform: {platform.system()} {platform.release()}")

    def _show_config(self, _):
        console.print(f"[bold]Profile:[/] {self.profile or '(default)'}")
        console.print(
            f"[bold]Regions:[/] {', '.join(self.regions) if self.regions else 'all'}"
        )
        console.print(f"[bold]No-cache:[/] {'on' if self.no_cache else 'off'}")
        console.print(f"[bold]Output-format:[/] {self.output_format}")

    # Alias for Cisco IOS compatibility
    _show_running_config = _show_config

    def _show_cache(self, _):
        from datetime import datetime, timezone

        table = Table(title="Cache Status")
        table.add_column("Cache")
        table.add_column("Entries")
        table.add_column("Status")
        table.add_row("In-memory", str(len(self._cache)), "active")
        try:
            from ...core.cache import Cache

            topo_cache = Cache("topology")
            info = topo_cache.get_info()
            if info:
                age = int(info["age_seconds"])
                status = f"age: {age}s" if not info["expired"] else "stale"
                data = topo_cache.get(ignore_expiry=True)
                entries = len(data.get("eni_index", {})) if data else 0
                table.add_row("Topology", str(entries), status)
            else:
                table.add_row("Topology", "0", "empty")
        except Exception as e:
            table.add_row("Topology", "-", f"error: {e}")
        console.print(table)

    def _show_global_networks(self, _):
        from ...modules import cloudwan
        fetch = lambda: cloudwan.CloudWANClient(self.profile).list_global_networks()
        gns = self._cached("global_networks", fetch, "Fetching global networks")
        if not gns:
            console.print("[yellow]No global networks found[/]")
            return
        if self.output_format == "json":
            self._emit_json_or_table(gns, lambda: None)
            return
        table = Table(title="Global Networks")
        table.add_column("#", style="dim")
        table.add_column("Name")
        table.add_column("ID")
        for i, gn in enumerate(gns, 1):
            table.add_row(str(i), gn["name"], gn["id"])
        console.print(table)
        console.print("[dim]Use 'set global-network <#>' to select[/]")

    def _show_vpcs(self, _):
        from ...modules import vpc

        vpcs = self._cached(
            "vpcs", lambda: vpc.VPCClient(self.profile).discover(self.regions), "Fetching VPCs"
        )
        if not vpcs:
            console.print("[yellow]No VPCs found[/]")
            return
        if self.output_format == "json":
            self._emit_json_or_table(vpcs, lambda: None)
            return
        table = Table(title="VPCs")
        table.add_column("#", style="dim")
        table.add_column("Name")
        table.add_column("ID")
        table.add_column("CIDRs")
        table.add_column("Region")
        for i, v in enumerate(vpcs, 1):
            cidrs = (
                ", ".join(v.get("cidrs", [])) if v.get("cidrs") else v.get("cidr", "")
            )
            table.add_row(
                str(i), v.get("name", ""), v["id"], cidrs, v.get("region", "")
            )
        console.print(table)
        console.print("[dim]Use 'set vpc <#>' to select[/]")

    def _show_transit_gateways(self, _):
        from ...modules import tgw

        tgws = self._cached(
            "transit_gateways",
            lambda: tgw.TGWClient(self.profile).discover(self.regions),
            "Fetching Transit Gateways",
        )
        if not tgws:
            console.print("[yellow]No Transit Gateways found[/]")
            return
        if self.output_format == "json":
            self._emit_json_or_table(tgws, lambda: None)
            return
        table = Table(title="Transit Gateways")
        table.add_column("#", style="dim")
        table.add_column("Name")
        table.add_column("ID")
        table.add_column("Region")
        for i, t in enumerate(tgws, 1):
            table.add_row(str(i), t.get("name", ""), t["id"], t.get("region", ""))
        console.print(table)
        console.print("[dim]Use 'set transit-gateway <#>' to select[/]")

    def _show_firewalls(self, _):
        from ...modules import anfw

        fws = self._cached(
            "firewalls",
            lambda: anfw.ANFWClient(self.profile).discover(self.regions),
            "Fetching firewalls",
        )
        if not fws:
            console.print("[yellow]No firewalls found[/]")
            return
        if self.output_format == "json":
            self._emit_json_or_table(fws, lambda: None)
            return
        table = Table(title="Network Firewalls")
        table.add_column("#", style="dim")
        table.add_column("Name")
        table.add_column("Region")
        for i, fw in enumerate(fws, 1):
            table.add_row(str(i), fw.get("name", ""), fw.get("region", ""))
        console.print(table)
        console.print("[dim]Use 'set firewall <#>' to select[/]")

    def _show_dx_connections(self, _):
        from ...modules import direct_connect

        connections = self._cached(
            "dx_connections",
            lambda: direct_connect.DXClient(self.profile).discover(self.regions),
            "Fetching Direct Connect",
        )
        direct_connect.DXDisplay(console).show_connections_list(connections)

    def _show_enis(self, arg):
        # Issue #9 fix: Delegate to context-specific handler when in EC2 instance context
        # EC2HandlersMixin._show_enis shows instance-specific ENIs from ctx.data
        if self.ctx_type == "ec2-instance":
            from .ec2 import EC2HandlersMixin
            EC2HandlersMixin._show_enis(self, arg)
            return

        from ...modules import eni

        enis_list = self._cached(
            "enis", lambda: eni.ENIClient(self.profile).discover(self.regions), "Fetching ENIs"
        )
        eni.ENIDisplay(console).show_list(enis_list)

    def _show_bgp_neighbors(self, _):
        from ...modules import vpn

        neighbors = self._cached(
            "bgp_neighbors",
            lambda: vpn.VPNClient(self.profile).get_bgp_neighbors(),
            "Fetching BGP neighbors",
        )
        vpn.VPNDisplay(console).show_bgp_neighbors(neighbors)

    def _show_security_groups(self, arg):
        """Show security groups. Use 'unused' to show only unused groups."""
        # Issue #9 fix: Delegate to context-specific handler when in VPC or EC2 context
        # VPCHandlersMixin._show_security_groups shows context-specific SGs from ctx.data
        if self.ctx_type in ("vpc", "ec2-instance"):
            from .vpc import VPCHandlersMixin
            VPCHandlersMixin._show_security_groups(self, arg)
            return

        from ...modules import security

        data = self._cached(
            "security_groups",
            lambda: security.SecurityClient(self.profile).perform_full_analysis(),
            "Performing security analysis",
        )
        display = security.SecurityDisplay(console)
        if arg == "unused":
            display.show_unused_groups(data.get("unused_groups", []))
        else:
            display.show_unused_groups(data.get("unused_groups", []))
            display.show_risky_rules(data.get("risky_rules", []))
            display.show_nacl_issues(data.get("nacl_issues", []))

    def _show_unused_sgs(self, _):
        from ...modules import security

        data = self._cached(
            "security_groups",
            lambda: security.SecurityClient(self.profile).perform_full_analysis(),
            "Analyzing security groups",
        )
        security.SecurityDisplay(console).show_unused_groups(
            data.get("unused_groups", [])
        )

    def _show_resolver_endpoints(self, _):
        from ...modules import route53_resolver

        data = self._cached(
            "route53_resolver",
            lambda: route53_resolver.Route53ResolverClient(self.profile).discover(self.regions),
            "Fetching Route 53 Resolver",
        )
        route53_resolver.Route53ResolverDisplay(console).show_endpoints(data)

    def _show_resolver_rules(self, _):
        from ...modules import route53_resolver

        data = self._cached(
            "route53_resolver",
            lambda: route53_resolver.Route53ResolverClient(self.profile).discover(self.regions),
            "Fetching Route 53 Resolver",
        )
        route53_resolver.Route53ResolverDisplay(console).show_rules(data)

    def _show_query_logs(self, _):
        from ...modules import route53_resolver

        data = self._cached(
            "route53_resolver",
            lambda: route53_resolver.Route53ResolverClient(self.profile).discover(self.regions),
            "Fetching Route 53 Resolver",
        )
        route53_resolver.Route53ResolverDisplay(console).show_query_logs(data)

    def _show_peering_connections(self, _):
        from ...modules import peering

        data = self._cached(
            "peering_connections",
            lambda: peering.PeeringClient(self.profile).discover(self.regions),
            "Fetching VPC peering",
        )
        peering.PeeringDisplay(console).show_list(data)

    def _show_prefix_lists(self, _):
        from ...modules import prefix_lists

        data = self._cached(
            "prefix_lists",
            lambda: prefix_lists.PrefixListClient(self.profile).discover(self.regions),
            "Fetching prefix lists",
        )
        prefix_lists.PrefixListDisplay(console).show_list(data)

    def _show_network_alarms(self, _):
        from ...modules import network_alarms

        data = self._cached(
            "network_alarms",
            lambda: network_alarms.NetworkAlarmsClient(self.profile).discover(self.regions),
            "Fetching network alarms",
        )
        network_alarms.NetworkAlarmsDisplay(console).show_alarms(data)

    def _show_alarms_critical(self, _):
        from ...modules import network_alarms

        data = self._cached(
            "network_alarms",
            lambda: network_alarms.NetworkAlarmsClient(self.profile).discover(self.regions),
            "Fetching network alarms",
        )
        network_alarms.NetworkAlarmsDisplay(console).show_alarms(
            data, state_filter="ALARM"
        )

    def _show_client_vpn_endpoints(self, _):
        from ...modules import client_vpn

        data = self._cached(
            "client_vpn_endpoints",
            lambda: client_vpn.ClientVPNClient(self.profile).discover(self.regions),
            "Fetching Client VPN",
        )
        client_vpn.ClientVPNDisplay(console).show_endpoints(data)

    def _show_global_accelerators(self, _):
        from ...modules import global_accelerator

        data = self._cached(
            "global_accelerators",
            lambda: global_accelerator.GlobalAcceleratorClient(self.profile).discover(self.regions),
            "Fetching Global Accelerators",
        )
        global_accelerator.GlobalAcceleratorDisplay(console).show_accelerators(data)

    def _show_ga_endpoint_health(self, _):
        from ...modules import global_accelerator

        data = self._cached(
            "global_accelerators",
            lambda: global_accelerator.GlobalAcceleratorClient(self.profile).discover(self.regions),
            "Fetching Global Accelerators",
        )
        global_accelerator.GlobalAcceleratorDisplay(console).show_endpoint_health(data)

    def _show_endpoint_services(self, _):
        from ...modules import privatelink

        data = self._cached(
            "vpc_endpoints",
            lambda: privatelink.PrivateLinkClient(self.profile).discover(self.regions),
            "Fetching PrivateLink",
        )
        privatelink.PrivateLinkDisplay(console).show_endpoint_services(data)

    def _show_vpc_endpoints(self, _):
        from ...modules import privatelink

        data = self._cached(
            "vpc_endpoints",
            lambda: privatelink.PrivateLinkClient(self.profile).discover(self.regions),
            "Fetching PrivateLink",
        )
        privatelink.PrivateLinkDisplay(console).show_vpc_endpoints(data)

    # Root set handlers
    def _set_profile(self, val):
        old_profile = self.profile
        self.profile = val if val else None
        console.print(f"[green]Profile: {self.profile or '(default)'}[/]")
        self._sync_runtime_config()
        
        # Auto-clear cache when profile changes
        if old_profile != self.profile:
            count = len(self._cache)
            if count > 0:
                self._cache.clear()
                console.print(f"[dim]Cleared {count} cache entries (profile changed)[/]")

    def _set_regions(self, val):
        old_regions = self.regions.copy()
        self.regions = [r.strip() for r in val.split(",")] if val else []
        console.print(
            f"[green]Regions: {', '.join(self.regions) if self.regions else 'all'}[/]"
        )
        self._sync_runtime_config()
        
        # Auto-clear cache when regions change
        if old_regions != self.regions:
            count = len(self._cache)
            if count > 0:
                self._cache.clear()
                console.print(f"[dim]Cleared {count} cache entries (regions changed)[/]")

    def _set_no_cache(self, val):
        self.no_cache = val and val.lower() in ("on", "true", "1", "yes")
        console.print(f"[green]No-cache: {'on' if self.no_cache else 'off'}[/]")
        self._sync_runtime_config()

    def _set_output_format(self, val):
        fmt = (val or "table").lower()
        if fmt not in ("table", "json", "yaml"):
            console.print("[red]Usage: set output-format <table|json|yaml>[/]")
            return
        self.output_format = fmt
        console.print(f"[green]Output-format: {fmt}[/]")
        self._sync_runtime_config()

    def _set_output_file(self, val):
        self.output_file = val if val else None
        if val:
            console.print(f"[green]Output file: {val}[/]")
        else:
            console.print("[green]Output file cleared[/]")

    def _set_watch(self, val):
        if not val or not val.strip():
            console.print("[red]Usage: set watch <seconds> (0 to disable)[/]")
            return
        try:
            interval = int(val.strip())
            if interval < 0:
                console.print("[red]Watch interval must be >= 0[/]")
                return
            self.watch_interval = interval
            if interval > 0:
                console.print(f"[green]Watch: {interval}s[/]")
            else:
                console.print("[green]Watch disabled[/]")
        except ValueError:
            console.print("[red]Usage: set watch <seconds> (0 to disable)[/]")

    def _set_theme(self, theme_name):
        """Set color theme (dracula, catppuccin, or custom)."""
        if not theme_name:
            console.print(f"[red]Usage: set theme <name>[/]")
            console.print(f"[dim]Available themes: dracula, catppuccin[/]")
            console.print(f"[dim]Custom themes in: {get_theme_dir()}[/]")
            return
        
        from ..themes import load_theme
        
        try:
            self.theme = load_theme(theme_name)
            self.config.set("prompt.theme", theme_name)
            self.config.save()
            console.print(f"[green]Theme set to: {self.theme.name}[/]")
            self._update_prompt()  # Refresh prompt colors
        except Exception as e:
            console.print(f"[red]Error loading theme '{theme_name}': {e}[/]")
            console.print("[dim]Available themes: dracula, catppuccin[/]")

    def _set_prompt(self, style):
        """Set prompt style (short or long)."""
        if not style or style not in ("short", "long"):
            console.print("[red]Usage: set prompt <short|long>[/]")
            console.print(f"[dim]Current: {self.config.get_prompt_style()}[/]")
            console.print("[dim]  short: Compact prompt with indices (gl:1>co:1>)[/]")
            console.print("[dim]  long:  Multi-line with full names[/]")
            return
        
        self.config.set("prompt.style", style)
        self.config.save()
        console.print(f"[green]Prompt style set to: {style}[/]")
        self._update_prompt()

    def _set_global_network(self, val):
        if not val:
            console.print("[red]Usage: set global-network <#>[/]")
            return
        gns = self._cache.get("global_networks", [])
        if not gns:
            console.print("[yellow]Run 'show global-networks' first[/]")
            return
        gn = self._resolve(gns, val)
        if not gn:
            console.print(f"[red]Not found: {val}[/]")
            return
        try:
            selection_idx = int(val)
        except ValueError:
            selection_idx = 1
        self._enter("global-network", gn["id"], gn["name"], gn, selection_idx)
        print()  # Add blank line before next prompt

    # Routing cache commands
    def complete_routing_cache(self, text, line, begidx, endidx):
        """Tab completion for routing-cache arguments."""
        return ['vpc', 'transit-gateway', 'cloud-wan', 'all']

    def _show_routing_cache(self, arg):
        """Show routing cache status or detailed routes.

        Usage:
            show routing-cache              # Summary
            show routing-cache vpc          # All VPC routes
            show routing-cache transit-gateway  # All Transit Gateway routes
            show routing-cache cloud-wan    # All Cloud WAN routes
            show routing-cache all          # All routes (detailed)
        """
        cache = self._cache.get("routing-cache", {})
        if not cache:
            console.print(
                "[yellow]Routing cache empty. Run 'create_routing_cache' to populate.[/]"
            )
            return

        arg = arg.strip().lower() if arg else ""

        # Show detailed routes if argument provided
        if arg in ["vpc", "transit-gateway", "cloud-wan", "all"]:
            self._show_routing_cache_detail(cache, arg)
            return

        # Default: Show summary
        table = Table(title="Routing Cache Summary")
        table.add_column("Source")
        table.add_column("Routes")
        table.add_column("Regions")

        for source, data in cache.items():
            routes = data.get("routes", [])
            regions = set(r.get("region", "?") for r in routes)
            source_display = source.replace("tgw", "Transit Gateway").replace("cloudwan", "Cloud WAN").upper()
            table.add_row(source_display, str(len(routes)), ", ".join(sorted(regions)))

        console.print(table)
        total = sum(len(d.get("routes", [])) for d in cache.values())
        console.print(f"\n[bold]Total routes cached:[/] {total}")
        console.print("\n[dim]Use 'show routing-cache vpc|transit-gateway|cloud-wan|all' for details[/]")

    def _show_routing_cache_detail(self, cache, filter_source):
        """Show detailed routing cache entries."""
        # Map user input to cache keys
        source_map = {
            "vpc": "vpc",
            "transit-gateway": "tgw",
            "transitgateway": "tgw",
            "tgw": "tgw",
            "cloud-wan": "cloudwan",
            "cloudwan": "cloudwan",
        }

        all_routes = []

        for source, data in cache.items():
            # Check if this source matches the filter
            if filter_source != "all":
                target_key = source_map.get(filter_source)
                if source != target_key:
                    continue
            routes = data.get("routes", [])
            all_routes.extend(routes)

        if not all_routes:
            console.print(f"[yellow]No routes found for {filter_source}[/]")
            return

        # Group by source type for organized display
        vpc_routes = [r for r in all_routes if r.get("source") == "vpc"]
        tgw_routes = [r for r in all_routes if r.get("source") == "tgw"]
        cloudwan_routes = [r for r in all_routes if r.get("source") == "cloudwan"]

        if vpc_routes and (filter_source in ["vpc", "all"]):
            self._show_vpc_routes_table(vpc_routes)

        if tgw_routes and (filter_source in ["transit-gateway", "transitgateway", "all"]):
            self._show_transit_gateway_routes_table(tgw_routes)

        if cloudwan_routes and (filter_source in ["cloud-wan", "cloudwan", "all"]):
            self._show_cloud_wan_routes_table(cloudwan_routes)

    def _show_vpc_routes_table(self, routes):
        """Display VPC routes in detailed table."""
        allow_truncate = self.config.get("display.allow_truncate", False)
        use_pager = self.config.get("display.pager", False)

        # Determine how many routes to show
        display_limit = len(routes) if not use_pager else 100

        table = Table(
            title=f"VPC Routes ({len(routes)} total)",
            show_header=True,
            header_style="bold cyan",
            expand=True
        )

        # Balanced column widths (no_wrap + ratio control)
        table.add_column("VPC Name", style="cyan", no_wrap=not allow_truncate, ratio=2)
        table.add_column("VPC ID", style="dim", no_wrap=not allow_truncate, ratio=2)
        table.add_column("Region", style="blue", no_wrap=True, ratio=2)
        table.add_column("Route Table", style="yellow", no_wrap=not allow_truncate, ratio=2)
        table.add_column("Destination", style="green", no_wrap=True, ratio=2)
        table.add_column("Target", style="magenta", no_wrap=not allow_truncate, ratio=3)
        table.add_column("State", style="bold green", no_wrap=True, ratio=1)

        for r in routes[:display_limit]:
            table.add_row(
                r.get("vpc_name") or "",
                r.get("vpc_id") or "",
                r.get("region") or "",
                r.get("route_table") or "",
                r.get("destination") or "",
                r.get("target") or "",
                r.get("state") or ""
            )

        console.print(table)
        if len(routes) > display_limit:
            console.print(f"[dim]Showing first {display_limit} of {len(routes)} routes[/]")
            console.print(f"[dim]Set 'pager: true' in config to enable pagination[/]")

    def _show_transit_gateway_routes_table(self, routes):
        """Display Transit Gateway routes in detailed table."""
        # Check terminal width and config
        allow_truncate = self.config.get("display.allow_truncate", True)

        table = Table(
            title=f"Transit Gateway Routes ({len(routes)} total)",
            show_header=True,
            header_style="bold cyan",
            expand=True  # Use full terminal width
        )

        # Add columns with proper styling and no width limits
        table.add_column("Transit Gateway", style="cyan", no_wrap=not allow_truncate)
        table.add_column("TGW ID", style="dim", no_wrap=not allow_truncate)
        table.add_column("Region", style="blue", no_wrap=True)
        table.add_column("Route Table", style="yellow", no_wrap=not allow_truncate)
        table.add_column("Destination", style="green", no_wrap=True)
        table.add_column("Attachment", style="magenta", no_wrap=not allow_truncate)
        table.add_column("State", style="bold green", no_wrap=True)
        table.add_column("Type", style="white", no_wrap=True)

        for r in routes[:100]:
            table.add_row(
                r.get("tgw_name") or "",
                r.get("tgw_id") or "",
                r.get("region") or "",
                r.get("route_table") or "",
                r.get("destination") or "",
                r.get("target") or "",
                r.get("state") or "",
                r.get("type") or ""
            )

        console.print(table)
        if len(routes) > 100:
            console.print(f"[dim]Showing first 100 of {len(routes)} routes[/]")

    def _show_cloud_wan_routes_table(self, routes):
        """Display Cloud WAN routes in detailed table."""
        allow_truncate = self.config.get("display.allow_truncate", True)

        table = Table(
            title=f"Cloud WAN Routes ({len(routes)} total)",
            show_header=True,
            header_style="bold cyan",
            expand=True
        )

        table.add_column("Core Network", style="cyan", no_wrap=not allow_truncate)
        table.add_column("Core Network ID", style="dim", no_wrap=not allow_truncate)
        table.add_column("Global Network", style="blue", no_wrap=not allow_truncate)
        table.add_column("Segment", style="yellow", no_wrap=True)
        table.add_column("Region", style="white", no_wrap=True)
        table.add_column("Destination", style="green", no_wrap=True)
        table.add_column("Target", style="magenta", no_wrap=not allow_truncate)
        table.add_column("State", style="bold green", no_wrap=True)

        for r in routes[:100]:
            table.add_row(
                r.get("core_network_name") or "",
                r.get("core_network_id") or "",
                r.get("global_network_id") or "",
                r.get("segment") or "",
                r.get("region") or "",
                r.get("destination") or "",
                r.get("target") or "",
                r.get("state") or ""
            )

        console.print(table)
        if len(routes) > 100:
            console.print(f"[dim]Showing first 100 of {len(routes)} routes[/]")

    def do_create_routing_cache(self, _):
        """Cache all routing data for fast global lookups."""
        from ...core.spinner import run_with_spinner

        cache = {}

        # VPC routes
        def fetch_vpc_routes():
            from ...modules import vpc
            from concurrent.futures import ThreadPoolExecutor, as_completed

            client = vpc.VPCClient(self.profile)
            vpcs = client.discover()
            routes = []

            def fetch_detail(v):
                try:
                    return client.get_vpc_detail(v["id"], v.get("region"))
                except Exception:
                    return None

            with ThreadPoolExecutor(max_workers=8) as ex:
                for fut in as_completed([ex.submit(fetch_detail, v) for v in vpcs]):
                    detail = fut.result()
                    if not detail:
                        continue
                    for rt in detail.get("route_tables", []):
                        for r in rt.get("routes", []):
                            routes.append(
                                {
                                    "source": "vpc",
                                    "vpc_id": detail["id"],
                                    "vpc_name": detail.get("name", detail["id"]),
                                    "region": detail.get("region", ""),
                                    "route_table": rt.get("id"),
                                    "destination": r.get("destination", ""),
                                    "target": r.get("target", ""),
                                    "state": r.get("state", ""),
                                }
                            )
            return routes

        # TGW routes
        def fetch_tgw_routes():
            from ...modules import tgw

            tgws = tgw.TGWClient(self.profile).discover()
            routes = []
            for t in tgws:
                tgw_id = t.get("id", "")
                tgw_name = t.get("name") or tgw_id
                tgw_region = t.get("region", "")

                for rt in t.get("route_tables", []):
                    rt_id = rt.get("id", "")

                    for r in rt.get("routes", []):
                        # TGW module uses lowercase keys: prefix, target, state, type
                        # NOT AWS API format: DestinationCidrBlock, TransitGatewayAttachmentId
                        routes.append(
                            {
                                "source": "tgw",
                                "tgw_id": tgw_id,
                                "tgw_name": tgw_name,
                                "region": tgw_region,
                                "route_table": rt_id,
                                "destination": r.get("prefix", ""),  # Lowercase
                                "target": r.get("target", ""),       # Already lowercase
                                "state": r.get("state", ""),         # Already lowercase
                                "type": r.get("type", ""),           # Already lowercase
                            }
                        )
            return routes

        # CloudWAN routes
        def fetch_cloudwan_routes():
            from ...modules import cloudwan

            core_networks = cloudwan.CloudWANClient(self.profile).discover()
            routes = []
            for cn in core_networks:
                for rt in cn.get("route_tables", []):
                    for r in rt.get("routes", []):
                        routes.append(
                            {
                                "source": "cloudwan",
                                "core_network_id": cn["id"],
                                "core_network_name": cn.get("name", cn["id"]),
                                "global_network_id": cn["global_network_id"],
                                "region": rt["region"],
                                "segment": rt["name"],
                                "destination": r.get("prefix", ""),
                                "target": r.get("target", ""),
                                "state": r.get("state", ""),
                                "type": r.get("type", ""),
                            }
                        )
            return routes

        console.print("[bold]Building routing cache...[/]")

        try:
            vpc_routes = run_with_spinner(fetch_vpc_routes, "Fetching VPC routes")
            cache["vpc"] = {"routes": vpc_routes}
            console.print(f"  VPC routes: {len(vpc_routes)}")
        except Exception as e:
            console.print(f"  [red]VPC routes failed: {e}[/]")

        try:
            tgw_routes = run_with_spinner(fetch_tgw_routes, "Fetching TGW routes")
            cache["tgw"] = {"routes": tgw_routes}
            console.print(f"  Transit Gateway routes: {len(tgw_routes)}")
        except Exception as e:
            console.print(f"  [red]TGW routes failed: {e}[/]")

        try:
            cloudwan_routes = run_with_spinner(
                fetch_cloudwan_routes, "Fetching CloudWAN routes"
            )
            cache["cloudwan"] = {"routes": cloudwan_routes}
            console.print(f"  Cloud WAN routes: {len(cloudwan_routes)}")
        except Exception as e:
            console.print(f"  [red]CloudWAN routes failed: {e}[/]")

        self._cache["routing-cache"] = cache

        # Auto-save to local DB if configured
        if self.config.get("cache.use_local_cache", False):
            try:
                from ...core.cache_db import CacheDB
                db = CacheDB()
                saved_count = db.save_routing_cache(cache, self.profile or "default")
                console.print(f"[dim]  → Saved {saved_count} routes to local database[/]")
            except Exception as e:
                console.print(f"[yellow]  → Local DB save failed: {e}[/]")
        total = sum(len(d.get("routes", [])) for d in cache.values())
        console.print(f"\n[green]Routing cache created: {total} routes[/]")

    def do_save_routing_cache(self, _):
        """Save routing cache to local SQLite database."""
        cache = self._cache.get("routing-cache", {})
        if not cache:
            console.print("[yellow]No routing cache to save. Run 'create_routing_cache' first.[/]")
            return

        try:
            from ...core.cache_db import CacheDB
            db = CacheDB()
            saved_count = db.save_routing_cache(cache, self.profile or "default")
            console.print(f"[green]✓ Saved {saved_count} routes to local database[/]")
            console.print(f"[dim]Location: {db.db_path}[/]")
        except Exception as e:
            console.print(f"[red]Failed to save: {e}[/]")

    def do_load_routing_cache(self, _):
        """Load routing cache from local SQLite database."""
        try:
            from ...core.cache_db import CacheDB
            db = CacheDB()
            cache = db.load_routing_cache(self.profile or "default")

            total = sum(len(d.get("routes", [])) for d in cache.values())
            if total == 0:
                console.print("[yellow]No cached routes found in local database.[/]")
                return

            self._cache["routing-cache"] = cache
            console.print(f"[green]✓ Loaded {total} routes from local database[/]")

            # Show breakdown
            for source, data in cache.items():
                route_count = len(data.get("routes", []))
                if route_count > 0:
                    source_display = source.replace("tgw", "Transit Gateway").replace("cloudwan", "Cloud WAN").upper()
                    console.print(f"  {source_display}: {route_count} routes")

        except Exception as e:
            console.print(f"[red]Failed to load: {e}[/]")

    def do_find_prefix(self, args):
        """Find prefix in routing cache globally."""
        if not args or not args.strip():
            console.print("[red]Usage: find-prefix <cidr|prefix>[/]")
            return

        prefix = args.strip()
        cache = self._cache.get("routing-cache", {})

        if not cache:
            console.print(
                "[yellow]Routing cache empty. Run 'create_routing_cache' first.[/]"
            )
            return

        matches = []
        for source, data in cache.items():
            for r in data.get("routes", []):
                dest = r.get("destination", "")
                if prefix in dest or dest.startswith(prefix.split("/")[0]):
                    matches.append(r)

        if not matches:
            console.print(f"[yellow]No routes found matching '{prefix}'[/]")
            return

        table = Table(title=f"Routes matching '{prefix}'")
        table.add_column("Source")
        table.add_column("Region")
        table.add_column("Resource")
        table.add_column("Route Table")
        table.add_column("Destination")
        table.add_column("Target")
        table.add_column("State")

        for r in matches[:50]:  # Limit output
            resource = (
                r.get("vpc_name") or r.get("tgw_name") or r.get("core_network_name", "")
            )
            table.add_row(
                r.get("source", ""),
                r.get("region", ""),
                resource[:20],
                r.get("route_table", "")[-12:],
                r.get("destination", ""),
                r.get("target", "")[-20:],
                r.get("state", ""),
            )

        console.print(table)
        if len(matches) > 50:
            console.print(f"[dim]Showing 50 of {len(matches)} matches[/]")

    def do_find_null_routes(self, _):
        """Find blackhole/null routes in routing cache globally."""
        cache = self._cache.get("routing-cache", {})

        if not cache:
            console.print(
                "[yellow]Routing cache empty. Run 'create_routing_cache' first.[/]"
            )
            return

        matches = []
        for source, data in cache.items():
            for r in data.get("routes", []):
                state = r.get("state", "").lower()
                if "blackhole" in state or "null" in state or not r.get("target"):
                    matches.append(r)

        if not matches:
            console.print("[green]No blackhole/null routes found[/]")
            return

        table = Table(title="Blackhole/Null Routes")
        table.add_column("Source")
        table.add_column("Region")
        table.add_column("Resource")
        table.add_column("Route Table")
        table.add_column("Destination")
        table.add_column("State")

        for r in matches:
            resource = (
                r.get("vpc_name") or r.get("tgw_name") or r.get("core_network_name", "")
            )
            table.add_row(
                r.get("source", ""),
                r.get("region", ""),
                resource[:20],
                r.get("route_table", "")[-12:],
                r.get("destination", ""),
                r.get("state", "") or "[red]no target[/]",
            )

        console.print(table)

    # Graph commands
    def _show_graph(self, arg):
        """Show command hierarchy graph. Options: stats, validate, mermaid, parent <cmd>"""
        from ..graph import build_graph, validate_graph

        graph = build_graph(self.__class__)
        arg = arg or ""

        if arg == "stats":
            stats = graph.stats()
            console.print("[bold]Command Graph Statistics[/]")
            console.print(f"  Total nodes: {stats['total_nodes']}")
            console.print(f"  Total edges: {stats['total_edges']}")
            console.print(f"  Contexts: {stats['contexts']}")
            console.print(f"  Command paths: {stats['paths']}")
            console.print(f"  Implemented: {stats['implemented']}")
            console.print("\n[bold]By type:[/]")
            for t, c in stats["by_type"].items():
                console.print(f"  {t}: {c}")

        elif arg == "validate":
            result = validate_graph(self.__class__)
            if result.valid:
                console.print("[green]✓ Graph is valid - all handlers implemented[/]")
            else:
                console.print("[red]✗ Graph validation failed[/]")
            console.print(str(result))

        elif arg == "mermaid":
            md = graph.to_mermaid()
            console.print(md)

        elif arg.startswith("parent "):
            # Show path to reach a command
            cmd = arg[7:].strip()
            self._show_command_path(graph, cmd)

        else:
            # Default: show tree structure
            self._print_graph_tree(graph.root, 0)

    def _show_command_path(self, graph, command: str):
        """Show the path to reach a specific command."""
        results = graph.find_command_path(command)
        
        if not results:
            console.print(f"[yellow]No command found matching '{command}'[/]")
            return
        
        console.print(f"[bold]Paths to '{command}':[/]\n")
        
        for result in results:
            marker = "✓" if result["implemented"] else "○"
            
            if result["is_global"]:
                console.print(f"{marker} [cyan]{result['command']}[/]")
                console.print("  [green]Global command[/] - available at root level")
            else:
                console.print(f"{marker} [cyan]{result['command']}[/]")
                console.print(f"  Context: [yellow]{result['context']}[/]")
                
                # Build the full navigation path
                path_parts = []
                if result.get("prereq_show"):
                    path_parts.append(result["prereq_show"])
                
                for p in result["path"][:-1]:  # Exclude the command itself
                    path_parts.append(p)
                
                if path_parts:
                    console.print(f"  Path: [blue]{' → '.join(path_parts)} → {result['command']}[/]")
            
            console.print()

    def _print_graph_tree(self, node, depth: int):
        """Print graph as tree with prerequisite show commands for context-entering sets."""
        indent = "  " * depth
        marker = "✓" if node.implemented else "○"
        
        # Map set commands to their prerequisite show commands
        prereq_show_map = {
            "set vpc": "show vpcs",
            "set transit-gateway": "show transit_gateways",
            "set global-network": "show global-networks",
            "set core-network": "show core-networks",
            "set firewall": "show firewalls",
            "set ec2-instance": "show ec2-instances",
            "set elb": "show elbs",
            "set vpn": "show vpns",
            "set route-table": "show route-tables",
        }
        
        if node.enters_context:
            # Show prerequisite show command before set command
            prereq = prereq_show_map.get(node.name)
            if prereq:
                console.print(f"{indent}[dim]({prereq} first)[/]")
            console.print(f"{indent}{marker} {node.name} →")
        else:
            console.print(f"{indent}{marker} {node.name}")
        
        for child in node.children:
            self._print_graph_tree(child, depth + 1)

    def do_validate_graph(self, _):
        """Validate command hierarchy against implemented handlers."""
        from ..graph import validate_graph

        result = validate_graph(self.__class__)

        if result.valid:
            console.print("[green]✓ Command graph is valid[/]")
            console.print("  All HIERARCHY entries have handlers")
        else:
            console.print("[red]✗ Command graph validation failed[/]")

        if result.errors:
            console.print(f"\n[red]Errors ({len(result.errors)}):[/]")
            for issue in result.errors:
                console.print(f"  [{issue.context or 'root'}] {issue.message}")

        if result.warnings:
            console.print(f"\n[yellow]Warnings ({len(result.warnings)}):[/]")
            for issue in result.warnings:
                console.print(f"  {issue.message}")

    def do_export_graph(self, args):
        """Export command graph as Mermaid markdown. Usage: export-graph [filename]"""
        from ..graph import build_graph
        from pathlib import Path

        filename = str(args).strip() or "command_hierarchy.md"

        graph = build_graph(self.__class__)
        md = graph.to_markdown()

        Path(filename).write_text(md)
        console.print(f"[green]Exported to {filename}[/]")
