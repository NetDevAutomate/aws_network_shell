"""Cloud WAN context handlers."""

from rich.table import Table
from rich.console import Console
import json

console = Console()


class CloudWANHandlersMixin:
    """Handlers for Cloud WAN contexts (global-network, core-network, route-table)."""

    def _show_segments(self, _):
        """Show segments in current core network."""
        if self.ctx_type != "core-network":
            console.print("[red]Must be in core-network context[/]")
            return
        cn_data = self.ctx.data
        policy = cn_data.get("policy", {})
        segments = policy.get("segments", [])
        if not segments:
            console.print("[yellow]No segments found[/]")
            return
        table = Table(title="Segments")
        table.add_column("Name")
        table.add_column("Edge Locations")
        table.add_column("Isolate Attachments")
        for seg in segments:
            edges = ", ".join(seg.get("edge-locations", [])) or "all"
            table.add_row(
                seg.get("name", ""), edges, str(seg.get("isolate-attachments", False))
            )
        console.print(table)

    def _show_policy(self, _):
        """Show current policy document."""
        if self.ctx_type != "core-network":
            console.print("[red]Must be in core-network context[/]")
            return
        cn_data = self.ctx.data
        policy = cn_data.get("policy", {})
        if not policy:
            console.print("[yellow]No policy data[/]")
            return
        console.print_json(json.dumps(policy, indent=2, default=str))

    def _show_core_networks(self, _):
        if self.ctx_type != "global-network":
            return
        from ...modules import cloudwan

        def fetch():
            client = cloudwan.CloudWANClient(self.profile)
            cns = []
            try:
                for cn in client.nm.list_core_networks().get("CoreNetworks", []):
                    if (
                        cn.get("GlobalNetworkId") != self.ctx_id
                        or cn.get("State") != "AVAILABLE"
                    ):
                        continue
                    cns.append(
                        {
                            "id": cn["CoreNetworkId"],
                            "name": cn.get("Description", cn["CoreNetworkId"]),
                            "state": cn.get("State", ""),
                        }
                    )
            except Exception as e:
                console.print(f"[red]Error: {e}[/]")
            return cns

        cns = self._cached(
            f"core-network:{self.ctx_id}", fetch, "Fetching core networks"
        )
        if not cns:
            console.print("[yellow]No core networks found[/]")
            return
        table = Table(title="Core Networks")
        table.add_column("#", style="dim")
        table.add_column("Name")
        table.add_column("ID")
        for i, cn in enumerate(cns, 1):
            table.add_row(str(i), cn["name"], cn["id"])
        console.print(table)
        console.print("[dim]Use 'set core-network <#>' to select[/]")

    def _set_core_network(self, val):
        if self.ctx_type != "global-network":
            return
        if not val:
            console.print("[red]Usage: set core-network <#>[/]")
            return
        cns = self._cache.get(f"core-network:{self.ctx_id}", [])
        if not cns:
            console.print("[yellow]Run 'show core-networks' first[/]")
            return
        cn = self._resolve(cns, val)
        if not cn:
            console.print(f"[red]Not found: {val}[/]")
            return
        self._enter("core-network", cn["id"], cn["name"], cn)

    def _show_cloudwan_route_tables(self):
        from ...modules import cloudwan

        def fetch():
            client = cloudwan.CloudWANClient(self.profile)
            all_cn = client.discover()
            return next((c for c in all_cn if c["id"] == self.ctx_id), None)

        cn = self._cached(f"cn-full:{self.ctx_id}", fetch, "Fetching routes")
        if not cn:
            console.print("[yellow]No route data[/]")
            return
        rts = cn.get("route_tables", [])
        self._cache[f"route-table:{self.ctx_id}"] = rts
        table = Table(title="Route Tables")
        table.add_column("#", style="dim")
        table.add_column("Name")
        table.add_column("Region")
        table.add_column("Type")
        table.add_column("Routes")
        for i, rt in enumerate(rts, 1):
            table.add_row(
                str(i),
                rt["name"],
                rt["region"],
                rt.get("type", ""),
                str(len(rt.get("routes", []))),
            )
        console.print(table)
        console.print("[dim]Use 'set route-table <#>' to select[/]")

    def _show_policy_change_events(self, _):
        if self.ctx_type != "core-network":
            console.print("[red]Must be in core-network context[/]")
            return
        from ...modules import cloudwan

        cn_id, cn_data = self.ctx_id, self.ctx.data
        events = self._cached(
            f"policy-events:{cn_id}",
            lambda: cloudwan.CloudWANClient(self.profile).get_policy_change_events(
                cn_id
            ),
            "Fetching policy events",
        )
        cloudwan.CloudWANDisplay(console).show_policy_change_events(cn_data, events)

    def _show_connect_attachments(self, _):
        if self.ctx_type != "core-network":
            console.print("[red]Must be in core-network context[/]")
            return
        from ...modules import cloudwan

        cn_id, cn_data = self.ctx_id, self.ctx.data
        attachments = self._cached(
            f"connect-att:{cn_id}",
            lambda: cloudwan.CloudWANClient(self.profile).list_connect_attachments(
                cn_id
            ),
            "Fetching Connect attachments",
        )
        cloudwan.CloudWANDisplay(console).show_connect_attachments(cn_data, attachments)

    def _show_connect_peers(self, _):
        if self.ctx_type != "core-network":
            console.print("[red]Must be in core-network context[/]")
            return
        from ...modules import cloudwan

        cn_id, cn_data = self.ctx_id, self.ctx.data
        peers = self._cached(
            f"connect-peers:{cn_id}",
            lambda: cloudwan.CloudWANClient(self.profile).list_connect_peers(cn_id),
            "Fetching Connect peers",
        )
        cloudwan.CloudWANDisplay(console).show_connect_peers(cn_data, peers)

    def _show_rib(self, args):
        if self.ctx_type != "core-network":
            console.print("[red]Must be in core-network context[/]")
            return
        from ...modules import cloudwan

        cn_id, cn_data = self.ctx_id, self.ctx.data
        segment_filter = edge_filter = None
        if args:
            for part in args.strip().split():
                if part.startswith("segment="):
                    segment_filter = part.split("=", 1)[1]
                elif part.startswith("edge="):
                    edge_filter = part.split("=", 1)[1]

        def fetch():
            client = cloudwan.CloudWANClient(self.profile)
            policy = cn_data.get("policy") or client.get_policy_document(cn_id)
            return client.get_rib_for_core_network(cn_id, policy) if policy else {}

        rib_data = self._cached(f"rib:{cn_id}", fetch, "Fetching RIB")
        cloudwan.CloudWANDisplay(console).show_rib(
            cn_data, rib_data, segment_filter, edge_filter
        )

    def _show_blackhole_routes(self, _):
        """Show blackhole routes across all core-network route tables."""
        if self.ctx_type != "core-network":
            console.print("[red]Must be in core-network context[/]")
            return
        self._cloudwan_find_null_routes()

    def _show_routes(self, _):
        if self.ctx_type != "route-table":
            return
        routes = self.ctx.data.get("routes", [])
        if not routes:
            console.print("[yellow]No routes[/]")
            return
        table = Table(title=f"Routes: {self.ctx.name}")
        table.add_column("Prefix")
        table.add_column("Target")
        table.add_column("Type")
        table.add_column("State")
        for r in routes:
            style = "green" if r.get("state") == "active" else "red"
            table.add_row(
                r["prefix"],
                r["target"],
                r.get("type", ""),
                f"[{style}]{r.get('state', '')}[/]",
            )
        console.print(table)

    def _set_route_table(self, val):
        if self.ctx_type not in ("core-network", "transit-gateway"):
            return
        if not val:
            console.print("[red]Usage: set route-table <#>[/]")
            return
        rts = self._cache.get(f"route-table:{self.ctx_id}", [])
        if not rts:
            console.print("[yellow]Run 'show route-tables' first[/]")
            return
        rt = self._resolve(rts, val)
        if not rt:
            console.print(f"[red]Not found: {val}[/]")
            return
        self._enter("route-table", rt["id"], rt["name"], rt)

    def do_find_prefix(self, args):
        if self.ctx_type != "route-table":
            console.print("[red]Must be in route-table context[/]")
            return
        prefix = str(args).strip()
        if not prefix:
            console.print("[red]Usage: find-prefix <cidr>[/]")
            return
        matches = [r for r in self.ctx.data.get("routes", []) if r["prefix"] == prefix]
        if not matches:
            console.print(f"[yellow]No exact match for {prefix}[/]")
            return
        for r in matches:
            console.print(f"{r['prefix']} -> {r['target']} ({r.get('state', '')})")

    def do_find_null_routes(self, _):
        if self.ctx_type != "route-table":
            console.print("[red]Must be in route-table context[/]")
            return
        nulls = [
            r
            for r in self.ctx.data.get("routes", [])
            if r.get("state", "").upper() == "BLACKHOLE"
        ]
        if not nulls:
            console.print("[green]No blackhole routes[/]")
            return
        for r in nulls:
            console.print(f"[red]{r['prefix']}[/] -> {r['target']}")

    def _cloudwan_find_prefix(self, prefix: str):
        """Find prefix across all core-network route tables."""
        if self.ctx_type != "core-network":
            return

        rts = self.ctx.data.get("route_tables", [])
        matches = []
        for rt in rts:
            for r in rt.get("routes", []):
                dest = r.get("prefix", "")
                if prefix in dest or dest.startswith(prefix.split("/")[0]):
                    matches.append(
                        {
                            "segment": rt.get("segment", ""),
                            "edge": rt.get("edge", ""),
                            "prefix": dest,
                            "target": r.get("target", ""),
                            "state": r.get("state", ""),
                        }
                    )

        if not matches:
            console.print(f"[yellow]No routes matching '{prefix}' in core-network[/]")
            return

        table = Table(title=f"Core Network Routes matching '{prefix}'")
        table.add_column("Segment")
        table.add_column("Edge")
        table.add_column("Prefix")
        table.add_column("Target")
        table.add_column("State")
        for m in matches:
            table.add_row(
                m["segment"], m["edge"], m["prefix"], m["target"][-25:], m["state"]
            )
        console.print(table)

    def _cloudwan_find_null_routes(self):
        """Find blackhole routes across all core-network route tables."""
        if self.ctx_type != "core-network":
            return

        rts = self.ctx.data.get("route_tables", [])
        matches = []
        for rt in rts:
            for r in rt.get("routes", []):
                state = r.get("state", "").upper()
                if state == "BLACKHOLE":
                    matches.append(
                        {
                            "segment": rt.get("segment", ""),
                            "edge": rt.get("edge", ""),
                            "prefix": r.get("prefix", ""),
                            "target": r.get("target", ""),
                            "state": state,
                        }
                    )

        if not matches:
            console.print("[green]No blackhole routes in core-network[/]")
            return

        table = Table(title="Core Network Blackhole Routes")
        table.add_column("Segment")
        table.add_column("Edge")
        table.add_column("Prefix")
        table.add_column("Target")
        for m in matches:
            table.add_row(
                m["segment"], m["edge"], m["prefix"], f"[red]{m['target']}[/]"
            )
        console.print(table)
