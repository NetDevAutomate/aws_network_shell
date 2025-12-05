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

    def _show_core_network_policy(self, _):
        """Show current CloudWAN core network policy document."""
        if self.ctx_type != "core-network":
            console.print("[red]Must be in core-network context[/]")
            return
        cn_data = self.ctx.data
        policy = cn_data.get("policy", {})
        if not policy:
            console.print("[yellow]No policy data[/]")
            return
        console.print_json(json.dumps(policy, indent=2, default=str))

    def _show_policy_documents(self, _):
        """Show all policy versions for current core network."""
        if self.ctx_type != "core-network":
            console.print("[red]Must be in core-network context[/]")
            return
        from ...modules import cloudwan

        cn_id = self.ctx_id
        versions = self._cached(
            f"policy-versions:{cn_id}",
            lambda: cloudwan.CloudWANClient(self.profile).list_policy_versions(cn_id),
            "Fetching policy versions",
        )
        if not versions:
            console.print("[yellow]No policy versions found[/]")
            return
        table = Table(title="Policy Versions")
        table.add_column("Version", style="dim")
        table.add_column("Alias")
        table.add_column("Change Set State")
        table.add_column("Created At")
        for v in versions:
            alias_style = "bold green" if v["alias"] == "LIVE" else "white"
            table.add_row(
                str(v["version"]),
                f"[{alias_style}]{v['alias']}[/]" if v["alias"] else "",
                v["change_set_state"],
                v["created_at"],
            )
        console.print(table)
        console.print("[dim]Use 'show live-policy' to view the current LIVE policy[/]")

    def _show_live_policy(self, _):
        """Alias for 'show policy' - shows the current LIVE policy."""
        self._show_core_network_policy(_)

    def _show_core_networks(self, _):
        if self.ctx_type != "global-network":
            return
        from ...modules import cloudwan

        def fetch():
            client = cloudwan.CloudWANClient(self.profile)
            # Get all core networks for this global network with full details
            all_cn = client.discover()
            return [cn for cn in all_cn if cn["global_network_id"] == self.ctx_id]

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

        # Fetch full core network data including policy
        from ...modules import cloudwan

        def fetch_full_cn():
            client = cloudwan.CloudWANClient(self.profile)
            policy = client.get_policy_document(cn["id"])
            full_data = dict(cn)
            full_data["policy"] = policy
            return full_data

        full_cn = self._cached(
            f"cn-detail:{cn['id']}", fetch_full_cn, "Fetching core network details"
        )
        self._enter("core-network", cn["id"], cn["name"], full_cn)

    def do_show(self, args):
        """Override show to handle policy document-diff command."""
        raw = str(args).strip()
        # Check if this is the policy document-diff command
        if raw.startswith("policy document-diff") or raw.startswith("policy diff"):
            parts = raw.split()
            if len(parts) >= 4:
                self._show_policy_document_diff(parts[2], parts[3])
                return
            else:
                console.print(
                    "[red]Usage: show policy document-diff <version1> <version2>[/]"
                )
                console.print("[dim]Use 'show policy-documents' to see available versions[/]")
                return
        # Fall back to default handler
        from ...shell.main import AWSNetShell
        super(CloudWANHandlersMixin, self).do_show(args)

    def _show_policy_document_diff(self, version1: str, version2: str):
        """Show diff between two policy document versions."""
        if self.ctx_type != "core-network":
            console.print("[red]Must be in core-network context[/]")
            return
        from ...modules import cloudwan

        cn_id = self.ctx_id
        try:
            v1 = int(version1)
            v2 = int(version2)
        except ValueError:
            console.print("[red]Version numbers must be integers[/]")
            return

        def fetch_doc(version):
            try:
                resp = (
                    cloudwan.CloudWANClient(self.profile)
                    .nm.get_core_network_policy(
                        CoreNetworkId=cn_id, PolicyVersionId=version
                    )
                )
                return json.loads(resp["CoreNetworkPolicy"]["PolicyDocument"])
            except Exception as e:
                console.print(f"[red]Error fetching version {version}: {e}[/]")
                return None

        doc1 = self._cached(
            f"policy-doc:{cn_id}:{v1}", lambda: fetch_doc(v1), f"Fetching policy v{v1}"
        )
        doc2 = self._cached(
            f"policy-doc:{cn_id}:{v2}", lambda: fetch_doc(v2), f"Fetching policy v{v2}"
        )

        if not doc1 or not doc2:
            console.print("[yellow]Could not fetch one or both policy versions[/]")
            return

        import difflib

        # Convert to JSON strings for diff
        doc1_str = json.dumps(doc1, indent=2, sort_keys=True).splitlines()
        doc2_str = json.dumps(doc2, indent=2, sort_keys=True).splitlines()

        diff = list(
            difflib.unified_diff(
                doc1_str, doc2_str, lineterm="", fromfile=f"Version {v1}", tofile=f"Version {v2}"
            )
        )

        if not diff:
            console.print(f"[green]No differences between version {v1} and {v2}[/]")
            return

        console.print(f"[bold]Differences between version {v1} and {v2}:[/]")
        for line in diff:
            if line.startswith("+") and not line.startswith("+++"):
                console.print(f"[green]{line}[/]")
            elif line.startswith("-") and not line.startswith("---"):
                console.print(f"[red]{line}[/]")
            elif line.startswith("@"):
                console.print(f"[cyan]{line}[/]")
            else:
                console.print(line)

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
            parts = args.strip().split()
            for i, part in enumerate(parts):
                if part.startswith("segment="):
                    segment_filter = part.split("=", 1)[1]
                elif part.startswith("edge="):
                    edge_filter = part.split("=", 1)[1]
                elif i == 0 and "=" not in part:
                    # First positional arg without = is segment name
                    segment_filter = part
                elif i == 1 and "=" not in part:
                    # Second positional arg is edge location
                    edge_filter = part

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
        """Show routes. In route-table context shows that table's routes.
        In core-network context shows all routes across all route tables."""
        if self.ctx_type == "route-table":
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
                # Handle multiple route formats:
                # - VPC normalized: destination, target, state
                # - CloudWAN: prefix, target, state, type
                if "destination" in r:
                    # VPC normalized format
                    prefix = r.get("destination", "")
                    target = r.get("target", "")
                    state = r.get("state", "")
                    route_type = "local" if target == "local" else ""
                else:
                    # CloudWAN route format
                    prefix = r.get("prefix", "")
                    target = r.get("target", "")
                    state = r.get("state", "")
                    route_type = r.get("type", "")
                style = "green" if state.lower() == "active" else "red"
                table.add_row(
                    prefix,
                    target,
                    route_type,
                    f"[{style}]{state}[/]",
                )
            console.print(table)
        elif self.ctx_type == "core-network":
            # Show all routes across all route tables in core-network context
            rts = self.ctx.data.get("route_tables", [])
            if not rts:
                console.print("[yellow]No route tables found[/]")
                return
            total_routes = 0
            for rt in rts:
                routes = rt.get("routes", [])
                if not routes:
                    continue
                total_routes += len(routes)
                title = f"[cyan]{rt.get('region', '')}[/] → [magenta]{rt.get('name', '')}[/]"
                table = Table(title=title)
                table.add_column("Prefix")
                table.add_column("Target")
                table.add_column("Type")
                table.add_column("State")
                for r in routes:
                    style = "green" if r.get("state") == "active" else "red"
                    table.add_row(
                        r.get("prefix", ""),
                        r.get("target", "")[-30:],
                        r.get("type", ""),
                        f"[{style}]{r.get('state', '')}[/]",
                    )
                console.print(table)
                console.print()
            console.print(f"[dim]Total: {total_routes} routes across {len(rts)} route tables[/]")
        else:
            console.print("[red]Must be in core-network or route-table context[/]")

    def _set_route_table(self, val):
        if self.ctx_type == "vpc":
            # Delegate to VPC-specific handler
            self._set_vpc_route_table(val)
            return
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
