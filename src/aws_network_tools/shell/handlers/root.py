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
        from datetime import datetime

        table = Table(title="Cache Status")
        table.add_column("Cache")
        table.add_column("Entries")
        table.add_column("Status")
        table.add_row("In-memory", str(len(self._cache)), "active")
        try:
            from ...traceroute.topology import TopologyDiscovery

            discovery = TopologyDiscovery(profile=self.profile)
            topo = discovery._load_cache()
            if topo:
                age = (datetime.now() - topo.cached_at).total_seconds()
                table.add_row(
                    "Topology",
                    str(len(topo.enis)),
                    f"age: {int(age)}s" if age < 900 else "stale",
                )
            else:
                table.add_row("Topology", "0", "empty")
        except Exception:
            table.add_row("Topology", "-", "unavailable")
        console.print(table)

    def _show_global_networks(self, _):
        from ...modules import cloudwan

        def fetch():
            client = cloudwan.CloudWANClient(self.profile)
            gns = []
            try:
                for gn in client.nm.describe_global_networks().get(
                    "GlobalNetworks", []
                ):
                    if gn.get("State") != "AVAILABLE":
                        continue
                    gn_id = gn["GlobalNetworkId"]
                    name = next(
                        (t["Value"] for t in gn.get("Tags", []) if t["Key"] == "Name"),
                        gn_id,
                    )
                    gns.append(
                        {"id": gn_id, "name": name, "state": gn.get("State", "")}
                    )
            except Exception as e:
                logger.exception("Failed to fetch global networks")
                console.print(f"[red]Error: {e}[/]")
            return gns

        gns = self._cached("global-network", fetch, "Fetching global networks")
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
            "vpc", lambda: vpc.VPCClient(self.profile).discover(), "Fetching VPCs"
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
            "tgw",
            lambda: tgw.TGWClient(self.profile).discover(),
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
            "firewall",
            lambda: anfw.ANFWClient(self.profile).discover(),
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
            "dx",
            lambda: direct_connect.DXClient(self.profile).discover(),
            "Fetching Direct Connect",
        )
        direct_connect.DXDisplay(console).show_connections_list(connections)

    def _show_enis(self, _):
        from ...modules import eni

        enis_list = self._cached(
            "eni", lambda: eni.ENIClient(self.profile).discover(), "Fetching ENIs"
        )
        eni.ENIDisplay(console).show_list(enis_list)

    def _show_bgp_neighbors(self, _):
        from ...modules import vpn

        neighbors = self._cached(
            "bgp-neighbors",
            lambda: vpn.VPNClient(self.profile).get_bgp_neighbors(),
            "Fetching BGP neighbors",
        )
        vpn.VPNDisplay(console).show_bgp_neighbors(neighbors)

    def _show_security_groups(self, arg):
        """Show security groups. Use 'unused' to show only unused groups."""
        from ...modules import security

        data = self._cached(
            "security",
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
            "security",
            lambda: security.SecurityClient(self.profile).perform_full_analysis(),
            "Analyzing security groups",
        )
        security.SecurityDisplay(console).show_unused_groups(
            data.get("unused_groups", [])
        )

    def _show_resolver_endpoints(self, _):
        from ...modules import route53_resolver

        data = self._cached(
            "r53-resolver",
            lambda: route53_resolver.Route53ResolverClient(self.profile).discover(),
            "Fetching Route 53 Resolver",
        )
        route53_resolver.Route53ResolverDisplay(console).show_endpoints(data)

    def _show_resolver_rules(self, _):
        from ...modules import route53_resolver

        data = self._cached(
            "r53-resolver",
            lambda: route53_resolver.Route53ResolverClient(self.profile).discover(),
            "Fetching Route 53 Resolver",
        )
        route53_resolver.Route53ResolverDisplay(console).show_rules(data)

    def _show_query_logs(self, _):
        from ...modules import route53_resolver

        data = self._cached(
            "r53-resolver",
            lambda: route53_resolver.Route53ResolverClient(self.profile).discover(),
            "Fetching Route 53 Resolver",
        )
        route53_resolver.Route53ResolverDisplay(console).show_query_logs(data)

    def _show_peering_connections(self, _):
        from ...modules import peering

        data = self._cached(
            "peering",
            lambda: peering.PeeringClient(self.profile).discover(),
            "Fetching VPC peering",
        )
        peering.PeeringDisplay(console).show_list(data)

    def _show_prefix_lists(self, _):
        from ...modules import prefix_lists

        data = self._cached(
            "prefix-lists",
            lambda: prefix_lists.PrefixListClient(self.profile).discover(),
            "Fetching prefix lists",
        )
        prefix_lists.PrefixListDisplay(console).show_list(data)

    def _show_network_alarms(self, _):
        from ...modules import network_alarms

        data = self._cached(
            "network-alarms",
            lambda: network_alarms.NetworkAlarmsClient(self.profile).discover(),
            "Fetching network alarms",
        )
        network_alarms.NetworkAlarmsDisplay(console).show_alarms(data)

    def _show_alarms_critical(self, _):
        from ...modules import network_alarms

        data = self._cached(
            "network-alarms",
            lambda: network_alarms.NetworkAlarmsClient(self.profile).discover(),
            "Fetching network alarms",
        )
        network_alarms.NetworkAlarmsDisplay(console).show_alarms(
            data, state_filter="ALARM"
        )

    def _show_client_vpn_endpoints(self, _):
        from ...modules import client_vpn

        data = self._cached(
            "client-vpn",
            lambda: client_vpn.ClientVPNClient(self.profile).discover(),
            "Fetching Client VPN",
        )
        client_vpn.ClientVPNDisplay(console).show_endpoints(data)

    def _show_global_accelerators(self, _):
        from ...modules import global_accelerator

        data = self._cached(
            "global-accelerator",
            lambda: global_accelerator.GlobalAcceleratorClient(self.profile).discover(),
            "Fetching Global Accelerators",
        )
        global_accelerator.GlobalAcceleratorDisplay(console).show_accelerators(data)

    def _show_ga_endpoint_health(self, _):
        from ...modules import global_accelerator

        data = self._cached(
            "global-accelerator",
            lambda: global_accelerator.GlobalAcceleratorClient(self.profile).discover(),
            "Fetching Global Accelerators",
        )
        global_accelerator.GlobalAcceleratorDisplay(console).show_endpoint_health(data)

    def _show_endpoint_services(self, _):
        from ...modules import privatelink

        data = self._cached(
            "privatelink",
            lambda: privatelink.PrivateLinkClient(self.profile).discover(),
            "Fetching PrivateLink",
        )
        privatelink.PrivateLinkDisplay(console).show_endpoint_services(data)

    def _show_vpc_endpoints(self, _):
        from ...modules import privatelink

        data = self._cached(
            "privatelink",
            lambda: privatelink.PrivateLinkClient(self.profile).discover(),
            "Fetching PrivateLink",
        )
        privatelink.PrivateLinkDisplay(console).show_vpc_endpoints(data)

    # Root set handlers
    def _set_profile(self, val):
        self.profile = val if val else None
        console.print(f"[green]Profile: {self.profile or '(default)'}[/]")

    def _set_regions(self, val):
        self.regions = [r.strip() for r in val.split(",")] if val else []
        console.print(
            f"[green]Regions: {', '.join(self.regions) if self.regions else 'all'}[/]"
        )

    def _set_no_cache(self, val):
        self.no_cache = val and val.lower() in ("on", "true", "1", "yes")
        console.print(f"[green]No-cache: {'on' if self.no_cache else 'off'}[/]")

    def _set_output_format(self, val):
        fmt = (val or "table").lower()
        if fmt not in ("table", "json", "yaml"):
            console.print("[red]Usage: set output-format <table|json|yaml>[/]")
            return
        self.output_format = fmt
        console.print(f"[green]Output-format: {fmt}[/]")

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

    def _set_global_network(self, val):
        if not val:
            console.print("[red]Usage: set global-network <#>[/]")
            return
        gns = self._cache.get("global-network", [])
        if not gns:
            console.print("[yellow]Run 'show global-networks' first[/]")
            return
        gn = self._resolve(gns, val)
        if not gn:
            console.print(f"[red]Not found: {val}[/]")
            return
        self._enter("global-network", gn["id"], gn["name"], gn)

    # Routing cache commands
    def _show_routing_cache(self, _):
        """Show routing cache status."""
        cache = self._cache.get("routing-cache", {})
        if not cache:
            console.print(
                "[yellow]Routing cache empty. Run 'create-routing-cache' to populate.[/]"
            )
            return

        table = Table(title="Routing Cache")
        table.add_column("Source")
        table.add_column("Routes")
        table.add_column("Regions")

        for source, data in cache.items():
            routes = data.get("routes", [])
            regions = set(r.get("region", "?") for r in routes)
            table.add_row(source, str(len(routes)), ", ".join(sorted(regions)))

        console.print(table)
        total = sum(len(d.get("routes", [])) for d in cache.values())
        console.print(f"\n[bold]Total routes cached:[/] {total}")

    def do_create_routing_cache(self, _):
        """Cache all routing data for fast global lookups."""
        from ...core.spinner import run_with_spinner

        cache = {}

        # VPC routes
        def fetch_vpc_routes():
            from ...modules import vpc

            vpcs = vpc.VPCClient(self.profile).discover()
            routes = []
            for v in vpcs:
                for rt in v.get("route_tables", []):
                    for r in rt.get("routes", []):
                        routes.append(
                            {
                                "source": "vpc",
                                "vpc_id": v["id"],
                                "vpc_name": v.get("name", v["id"]),
                                "region": v["region"],
                                "route_table": rt.get("id"),
                                "destination": r.get("DestinationCidrBlock")
                                or r.get("DestinationPrefixListId", ""),
                                "target": r.get("GatewayId")
                                or r.get("NatGatewayId")
                                or r.get("TransitGatewayId")
                                or r.get("NetworkInterfaceId", ""),
                                "state": r.get("State", ""),
                            }
                        )
            return routes

        # TGW routes
        def fetch_tgw_routes():
            from ...modules import tgw

            tgws = tgw.TGWClient(self.profile).discover()
            routes = []
            for t in tgws:
                for rt in t.get("route_tables", []):
                    for r in rt.get("routes", []):
                        routes.append(
                            {
                                "source": "tgw",
                                "tgw_id": t["id"],
                                "tgw_name": t.get("name", t["id"]),
                                "region": t["region"],
                                "route_table": rt.get("id"),
                                "destination": r.get("DestinationCidrBlock", ""),
                                "target": r.get("TransitGatewayAttachmentId", ""),
                                "state": r.get("State", ""),
                                "type": r.get("Type", ""),
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
            console.print(f"  TGW routes: {len(tgw_routes)}")
        except Exception as e:
            console.print(f"  [red]TGW routes failed: {e}[/]")

        self._cache["routing-cache"] = cache
        total = sum(len(d.get("routes", [])) for d in cache.values())
        console.print(f"\n[green]Routing cache created: {total} routes[/]")

    def do_find_prefix(self, args):
        """Find prefix in routing cache globally."""
        if not args or not args.strip():
            console.print("[red]Usage: find-prefix <cidr|prefix>[/]")
            return

        prefix = args.strip()
        cache = self._cache.get("routing-cache", {})

        if not cache:
            console.print(
                "[yellow]Routing cache empty. Run 'create-routing-cache' first.[/]"
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
                "[yellow]Routing cache empty. Run 'create-routing-cache' first.[/]"
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
        """Show command hierarchy graph. Options: stats, validate, mermaid"""
        from ..graph import build_graph, validate_graph

        graph = build_graph(self.__class__)

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

        else:
            # Default: show tree structure
            self._print_graph_tree(graph.root, 0)

    def _print_graph_tree(self, node, depth: int):
        """Print graph as tree."""
        indent = "  " * depth
        marker = "✓" if node.implemented else "○"
        if node.enters_context:
            console.print(f"{indent}{marker} {node.name} → [{node.enters_context}]")
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
