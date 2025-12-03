"""VPC context handlers."""

from rich.table import Table
from rich.console import Console

console = Console()


class VPCHandlersMixin:
    """Handlers for VPC context."""

    def _set_vpc(self, val):
        if not val:
            console.print("[red]Usage: set vpc <#>[/]")
            return
        vpcs = self._cache.get("vpc", [])
        if not vpcs:
            console.print("[yellow]Run 'show vpcs' first[/]")
            return
        v = self._resolve(vpcs, val)
        if not v:
            console.print(f"[red]Not found: {val}[/]")
            return
        from ...modules import vpc
        from ...core import run_with_spinner

        detail = run_with_spinner(
            lambda: vpc.VPCClient(self.profile).get_vpc_detail(
                v["id"], v.get("region")
            ),
            "Fetching VPC details",
            console=console,
        )
        self._enter("vpc", v["id"], v.get("name", v["id"]), detail)

    def _show_vpc_route_tables(self):
        rts = self.ctx.data.get("route_tables", [])
        self._cache["route_table"] = rts
        if not rts:
            console.print("[yellow]No route tables[/]")
            return
        table = Table(title="VPC Route Tables")
        table.add_column("#", style="dim")
        table.add_column("Name")
        table.add_column("ID")
        table.add_column("Routes")
        for i, rt in enumerate(rts, 1):
            table.add_row(
                str(i), rt.get("name", ""), rt["id"], str(len(rt.get("routes", [])))
            )
        console.print(table)
        console.print("[dim]Use 'set route-table <#>' to select[/]")

    def _show_subnets(self, _):
        if self.ctx_type != "vpc":
            return
        subnets = self.ctx.data.get("subnets", [])
        if not subnets:
            console.print("[yellow]No subnets[/]")
            return
        table = Table(title="Subnets")
        table.add_column("#", style="dim", justify="right")
        table.add_column("Name")
        table.add_column("ID")
        table.add_column("CIDR")
        table.add_column("AZ")
        for i, s in enumerate(subnets, 1):
            table.add_row(
                str(i),
                s.get("name", "") or "-",
                s["id"],
                s.get("cidr", ""),
                s.get("az", ""),
            )
        console.print(table)

    def _show_security_groups(self, _):
        if self.ctx_type == "vpc":
            sgs = self.ctx.data.get("security_groups", [])
        elif self.ctx_type == "ec2-instance":
            sgs = self.ctx.data.get("security_groups", [])
        else:
            return
        if not sgs:
            console.print("[yellow]No security groups[/]")
            return
        if self.output_format == "json":
            self._emit_json_or_table(sgs, lambda: None)
            return
        if self.ctx_type == "ec2-instance":
            table = Table(title="Instance Security Groups")
            table.add_column("ID")
            table.add_column("Name")
            table.add_column("Ingress Rules", justify="right")
            table.add_column("Egress Rules", justify="right")
            for sg in sgs:
                table.add_row(
                    sg["id"],
                    sg.get("name", ""),
                    str(len(sg.get("ingress", []))),
                    str(len(sg.get("egress", []))),
                )
        else:
            table = Table(title="Security Groups")
            table.add_column("Name")
            table.add_column("ID")
            table.add_column("Description")
            for sg in sgs:
                table.add_row(
                    sg.get("name", ""), sg["id"], sg.get("description", "")[:40]
                )
        console.print(table)

    def _show_nacls(self, _):
        if self.ctx_type != "vpc":
            return
        nacls = self.ctx.data.get("nacls", [])
        if not nacls:
            console.print("[yellow]No NACLs[/]")
            return
        table = Table(title="Network ACLs")
        table.add_column("Name")
        table.add_column("ID")
        table.add_column("Default")
        for n in nacls:
            table.add_row(
                n.get("name", ""), n["id"], "Yes" if n.get("is_default") else "No"
            )
        console.print(table)

    def _show_internet_gateways(self, _):
        if self.ctx_type != "vpc":
            return
        igws = self.ctx.data.get("igws", [])
        if self.output_format == "json":
            self._emit_json_or_table(igws, lambda: None)
            return
        table = Table(title="Internet Gateways")
        table.add_column("ID")
        table.add_column("Name")
        for i in igws:
            table.add_row(i.get("id", ""), i.get("name", "") or "-")
        console.print(table)

    def _show_nat_gateways(self, _):
        if self.ctx_type != "vpc":
            return
        nats = self.ctx.data.get("nats", [])
        if self.output_format == "json":
            self._emit_json_or_table(nats, lambda: None)
            return
        table = Table(title="NAT Gateways")
        table.add_column("ID")
        table.add_column("Subnet")
        table.add_column("Type")
        for n in nats:
            table.add_row(n.get("id", ""), n.get("subnet", ""), n.get("type", ""))
        console.print(table)

    def _show_endpoints(self, _):
        if self.ctx_type != "vpc":
            return
        eps = self.ctx.data.get("endpoints", [])
        if self.output_format == "json":
            self._emit_json_or_table(eps, lambda: None)
            return
        table = Table(title="VPC Endpoints")
        table.add_column("ID")
        table.add_column("Type")
        table.add_column("Service")
        table.add_column("State")
        for e in eps:
            table.add_row(
                e.get("id", ""),
                e.get("type", ""),
                e.get("service", ""),
                e.get("state", ""),
            )
        console.print(table)

    def _vpc_find_prefix(self, prefix: str):
        """Find prefix across all VPC route tables."""
        if self.ctx_type != "vpc":
            return

        rts = self.ctx.data.get("route_tables", [])
        matches = []
        for rt in rts:
            for r in rt.get("routes", []):
                dest = r.get("DestinationCidrBlock") or r.get(
                    "DestinationPrefixListId", ""
                )
                if prefix in dest or dest.startswith(prefix.split("/")[0]):
                    matches.append(
                        {
                            "route_table": rt.get("name") or rt["id"],
                            "destination": dest,
                            "target": r.get("GatewayId")
                            or r.get("NatGatewayId")
                            or r.get("TransitGatewayId")
                            or r.get("NetworkInterfaceId", ""),
                            "state": r.get("State", ""),
                        }
                    )

        if not matches:
            console.print(f"[yellow]No routes matching '{prefix}' in VPC[/]")
            return

        table = Table(title=f"VPC Routes matching '{prefix}'")
        table.add_column("Route Table")
        table.add_column("Destination")
        table.add_column("Target")
        table.add_column("State")
        for m in matches:
            table.add_row(
                m["route_table"][-20:], m["destination"], m["target"][-25:], m["state"]
            )
        console.print(table)

    def _vpc_find_null_routes(self):
        """Find blackhole routes across all VPC route tables."""
        if self.ctx_type != "vpc":
            return

        rts = self.ctx.data.get("route_tables", [])
        matches = []
        for rt in rts:
            for r in rt.get("routes", []):
                state = r.get("State", "").lower()
                target = (
                    r.get("GatewayId")
                    or r.get("NatGatewayId")
                    or r.get("TransitGatewayId")
                    or r.get("NetworkInterfaceId", "")
                )
                if "blackhole" in state or not target:
                    matches.append(
                        {
                            "route_table": rt.get("name") or rt["id"],
                            "destination": r.get("DestinationCidrBlock")
                            or r.get("DestinationPrefixListId", ""),
                            "state": r.get("State", "") or "no target",
                        }
                    )

        if not matches:
            console.print("[green]No blackhole routes in VPC[/]")
            return

        table = Table(title="VPC Blackhole Routes")
        table.add_column("Route Table")
        table.add_column("Destination")
        table.add_column("State")
        for m in matches:
            table.add_row(
                m["route_table"][-20:], m["destination"], f"[red]{m['state']}[/]"
            )
        console.print(table)

    def _show_vpc(self, sub):
        """Handle 'show vpc <sub>' shortcuts."""
        sub = (sub or "").strip()
        if sub in ("?", "help", ""):
            console.print("[bold]show vpc options:[/]")
            console.print("  show vpc subnets-all")
            return
        if sub == "subnets-all":
            from ...modules import vpc
            from concurrent.futures import ThreadPoolExecutor, as_completed

            vpcs = self._cached(
                "vpc", lambda: vpc.VPCClient(self.profile).discover(), "Fetching VPCs"
            )
            if not vpcs:
                console.print("[yellow]No VPCs found[/]")
                return
            client = vpc.VPCClient(self.profile)
            subs = []

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
                    for s in detail.get("subnets", []):
                        subs.append(
                            {
                                "vpc_id": detail["id"],
                                "vpc_name": detail.get("name") or detail["id"],
                                "region": detail.get("region"),
                                "id": s.get("id"),
                                "name": s.get("name"),
                                "cidr": s.get("cidr"),
                                "az": s.get("az"),
                            }
                        )
            if not subs:
                console.print("[yellow]No subnets found[/]")
                return
            if self.output_format == "json":
                self._emit_json_or_table(subs, lambda: None)
                return
            table = Table(title="VPC Subnets (All)")
            table.add_column("#", style="dim", justify="right")
            table.add_column("VPC", style="cyan")
            table.add_column("Subnet Name", style="yellow")
            table.add_column("Subnet ID", style="green")
            table.add_column("CIDR")
            table.add_column("AZ")
            table.add_column("Region", style="magenta")
            for i, s in enumerate(
                sorted(
                    subs, key=lambda x: (x["region"], x["vpc_name"], x["az"], x["id"])
                ),
                1,
            ):
                table.add_row(
                    str(i),
                    f"{s['vpc_name']} ({s['vpc_id']})",
                    s.get("name") or "-",
                    s["id"],
                    s.get("cidr", ""),
                    s.get("az", ""),
                    s.get("region", ""),
                )
            console.print(table)
            console.print(f"[dim]Total: {len(subs)} Subnet(s)[/]")
            return
        console.print(f"[red]Unknown 'show vpc' option: {sub}[/]")
