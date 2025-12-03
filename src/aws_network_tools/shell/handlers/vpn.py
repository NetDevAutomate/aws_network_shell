"""VPN context handlers."""

from rich.table import Table
from rich.console import Console

console = Console()


class VPNHandlersMixin:
    """Handlers for VPN context."""

    def _set_vpn(self, val):
        if not val:
            console.print("[red]Usage: set vpn <#>[/]")
            return
        vpns = self._cache.get("vpn", [])
        if not vpns:
            console.print("[yellow]Run 'show vpns' first[/]")
            return
        v = self._resolve(vpns, val)
        if not v:
            console.print(f"[red]Not found: {val}[/]")
            return
        self._enter("vpn", v["id"], v.get("name", v["id"]), v)

    def _show_vpns(self, _):
        """Show Site-to-Site VPN connections."""
        from ...modules import vpn

        vpns = self._cached(
            "vpn", lambda: vpn.VPNClient(self.profile).discover(), "Fetching VPNs"
        )
        if not vpns:
            console.print("[yellow]No VPN connections found[/]")
            return
        if self.output_format == "json":
            self._emit_json_or_table(vpns, lambda: None)
            return
        table = Table(title="Site-to-Site VPN Connections")
        table.add_column("#", style="dim")
        table.add_column("Name")
        table.add_column("ID")
        table.add_column("State")
        table.add_column("Type")
        table.add_column("Region")
        for i, v in enumerate(vpns, 1):
            table.add_row(
                str(i),
                v.get("name", ""),
                v["id"],
                v.get("state", ""),
                v.get("type", ""),
                v.get("region", ""),
            )
        console.print(table)
        console.print("[dim]Use 'set vpn <#>' to select[/]")

    def _show_tunnels(self, _):
        """Show VPN tunnels in current VPN context."""
        if self.ctx_type != "vpn":
            console.print("[red]Must be in vpn context[/]")
            return
        tunnels = self.ctx.data.get("tunnels", [])
        if not tunnels:
            console.print("[yellow]No tunnels[/]")
            return
        table = Table(title=f"VPN Tunnels: {self.ctx.name}")
        table.add_column("Outside IP")
        table.add_column("Status")
        table.add_column("Status Message")
        for t in tunnels:
            status = t.get("status", "")
            style = "green" if status == "UP" else "red"
            table.add_row(
                t.get("outside_ip", ""),
                f"[{style}]{status}[/]",
                t.get("status_message", ""),
            )
        console.print(table)
