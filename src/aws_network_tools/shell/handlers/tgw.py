"""Transit Gateway context handlers."""

from rich.table import Table
from rich.console import Console

console = Console()


class TGWHandlersMixin:
    """Handlers for Transit Gateway context."""

    def _set_transit_gateway(self, val):
        if not val:
            console.print("[red]Usage: set transit-gateway <#>[/]")
            return
        tgws = self._cache.get("tgw", [])
        if not tgws:
            console.print("[yellow]Run 'show transit_gateways' first[/]")
            return
        t = self._resolve(tgws, val)
        if not t:
            console.print(f"[red]Not found: {val}[/]")
            return
        self._enter("transit-gateway", t["id"], t.get("name", t["id"]), t)

    def _show_transit_gateway_route_tables(self):
        t = self.ctx.data
        rts = t.get("route_tables", [])
        # Issue #5 fix: Use correct cache key format to match _set_route_table expectations
        cache_key = f"route-table:{self.ctx_id}"
        self._cache[cache_key] = rts
        if not rts:
            console.print("[yellow]No route tables[/]")
            return
        table = Table(title="TGW Route Tables")
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

    def _show_attachments(self, _):
        if self.ctx_type != "transit-gateway":
            return
        atts = self.ctx.data.get("attachments", [])
        if not atts:
            console.print("[yellow]No attachments[/]")
            return
        table = Table(title="Transit Gateway Attachments")
        table.add_column("#", style="dim", justify="right")
        table.add_column("Name")
        table.add_column("ID")
        table.add_column("Type")
        table.add_column("State")
        for i, a in enumerate(atts, 1):
            table.add_row(
                str(i),
                a.get("name", ""),
                a["id"],
                a.get("type", ""),
                a.get("state", ""),
            )
        console.print(table)

    def _tgw_find_prefix(self, prefix: str):
        """Find prefix across all TGW route tables."""
        if self.ctx_type != "transit-gateway":
            return

        rts = self.ctx.data.get("route_tables", [])
        matches = []
        for rt in rts:
            for r in rt.get("routes", []):
                dest = r.get("DestinationCidrBlock", "")
                if prefix in dest or dest.startswith(prefix.split("/")[0]):
                    matches.append(
                        {
                            "route_table": rt.get("name") or rt["id"],
                            "destination": dest,
                            "attachment": r.get("TransitGatewayAttachmentId", ""),
                            "type": r.get("Type", ""),
                            "state": r.get("State", ""),
                        }
                    )

        if not matches:
            console.print(f"[yellow]No routes matching '{prefix}' in TGW[/]")
            return

        table = Table(title=f"TGW Routes matching '{prefix}'")
        table.add_column("Route Table")
        table.add_column("Destination")
        table.add_column("Attachment")
        table.add_column("Type")
        table.add_column("State")
        for m in matches:
            table.add_row(
                m["route_table"][-20:],
                m["destination"],
                m["attachment"][-20:],
                m["type"],
                m["state"],
            )
        console.print(table)

    def _tgw_find_null_routes(self):
        """Find blackhole routes across all TGW route tables."""
        if self.ctx_type != "transit-gateway":
            return

        rts = self.ctx.data.get("route_tables", [])
        matches = []
        for rt in rts:
            for r in rt.get("routes", []):
                state = r.get("State", "").lower()
                if "blackhole" in state:
                    matches.append(
                        {
                            "route_table": rt.get("name") or rt["id"],
                            "destination": r.get("DestinationCidrBlock", ""),
                            "type": r.get("Type", ""),
                            "state": r.get("State", ""),
                        }
                    )

        if not matches:
            console.print("[green]No blackhole routes in TGW[/]")
            return

        table = Table(title="TGW Blackhole Routes")
        table.add_column("Route Table")
        table.add_column("Destination")
        table.add_column("Type")
        table.add_column("State")
        for m in matches:
            table.add_row(
                m["route_table"][-20:],
                m["destination"],
                m["type"],
                f"[red]{m['state']}[/]",
            )
        console.print(table)
