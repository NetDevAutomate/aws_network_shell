"""Load Balancer context handlers."""

from rich.table import Table
from rich.console import Console

console = Console()


class ELBHandlersMixin:
    """Handlers for ELB context."""

    def _set_elb(self, val):
        if not val:
            console.print("[red]Usage: set elb <#>[/]")
            return
        elbs = self._cache.get("elb", [])
        if not elbs:
            console.print("[yellow]Run 'show elbs' first[/]")
            return
        e = self._resolve(elbs, val)
        if not e:
            console.print(f"[red]Not found: {val}[/]")
            return
        # Fetch detail
        from ...modules import elb
        from ...core import run_with_spinner

        detail = run_with_spinner(
            lambda: elb.ELBClient(self.profile).get_elb_detail(
                e["arn"], e.get("region")
            ),
            "Fetching ELB details",
            console=console,
        )
        self._enter("elb", e["arn"], e.get("name", e["arn"]), detail)

    def _show_elbs(self, _):
        """Show load balancers."""
        from ...modules import elb

        elbs = self._cached(
            "elb",
            lambda: elb.ELBClient(self.profile).discover(),
            "Fetching Load Balancers",
        )
        if not elbs:
            console.print("[yellow]No load balancers found[/]")
            return
        if self.output_format == "json":
            self._emit_json_or_table(elbs, lambda: None)
            return
        table = Table(title="Load Balancers")
        table.add_column("#", style="dim")
        table.add_column("Name")
        table.add_column("Type")
        table.add_column("Scheme")
        table.add_column("State")
        table.add_column("Region")
        for i, e in enumerate(elbs, 1):
            table.add_row(
                str(i),
                e.get("name", ""),
                e.get("type", ""),
                e.get("scheme", ""),
                e.get("state", ""),
                e.get("region", ""),
            )
        console.print(table)
        console.print("[dim]Use 'set elb <#>' to select[/]")

    def _show_listeners(self, _):
        """Show ELB listeners."""
        if self.ctx_type != "elb":
            console.print("[red]Must be in elb context[/]")
            return
        listeners = self.ctx.data.get("listeners", [])
        if not listeners:
            console.print("[yellow]No listeners[/]")
            return
        table = Table(title=f"Listeners: {self.ctx.name}")
        table.add_column("Port")
        table.add_column("Protocol")
        table.add_column("Default Action")
        for listener in listeners:
            table.add_row(
                str(listener.get("port", "")),
                listener.get("protocol", ""),
                listener.get("default_action", ""),
            )
        console.print(table)

    def _show_targets(self, _):
        """Show ELB target groups."""
        if self.ctx_type != "elb":
            console.print("[red]Must be in elb context[/]")
            return
        targets = self.ctx.data.get("target_groups", [])
        if not targets:
            console.print("[yellow]No target groups[/]")
            return
        table = Table(title=f"Target Groups: {self.ctx.name}")
        table.add_column("Name")
        table.add_column("Protocol")
        table.add_column("Port")
        table.add_column("Target Type")
        for t in targets:
            table.add_row(
                t.get("name", ""),
                t.get("protocol", ""),
                str(t.get("port", "")),
                t.get("target_type", ""),
            )
        console.print(table)

    def _show_health(self, _):
        """Show ELB target health."""
        if self.ctx_type != "elb":
            console.print("[red]Must be in elb context[/]")
            return
        health = self.ctx.data.get("target_health", [])
        if not health:
            console.print("[yellow]No health data[/]")
            return
        table = Table(title=f"Target Health: {self.ctx.name}")
        table.add_column("Target")
        table.add_column("Port")
        table.add_column("Health")
        table.add_column("Reason")
        for h in health:
            state = h.get("state", "")
            style = (
                "green"
                if state == "healthy"
                else "red"
                if state == "unhealthy"
                else "yellow"
            )
            table.add_row(
                h.get("target", ""),
                str(h.get("port", "")),
                f"[{style}]{state}[/]",
                h.get("reason", ""),
            )
        console.print(table)
