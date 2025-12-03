"""Network Firewall context handlers."""

from rich.table import Table
from rich.console import Console

console = Console()


class FirewallHandlersMixin:
    """Handlers for Network Firewall context."""

    def _set_firewall(self, val):
        if not val:
            console.print("[red]Usage: set firewall <#>[/]")
            return
        fws = self._cache.get("firewall", [])
        if not fws:
            console.print("[yellow]Run 'show firewalls' first[/]")
            return
        fw = self._resolve(fws, val)
        if not fw:
            console.print(f"[red]Not found: {val}[/]")
            return
        self._enter("firewall", fw.get("arn", ""), fw.get("name", ""), fw)

    def _show_rule_groups(self, _):
        if self.ctx_type != "firewall":
            return
        rgs = self.ctx.data.get("rule_groups", [])
        if not rgs:
            console.print("[yellow]No rule groups[/]")
            return
        table = Table(title="Rule Groups")
        table.add_column("Name")
        table.add_column("Type")
        table.add_column("Priority")
        for rg in rgs:
            table.add_row(
                rg.get("name", ""), rg.get("type", ""), str(rg.get("priority", ""))
            )
        console.print(table)

    def _show_policy(self, _):
        """Show firewall policy details."""
        if self.ctx_type != "firewall":
            return
        policy = self.ctx.data.get("policy", {})
        if not policy:
            console.print("[yellow]No policy data available[/]")
            return

        console.print(f"[bold]Firewall Policy:[/] {policy.get('name', 'N/A')}")
        console.print(f"[bold]ARN:[/] {policy.get('arn', 'N/A')}")

        # Show stateless actions
        stateless = policy.get("stateless_default_actions", {})
        if stateless:
            console.print("\n[bold]Stateless Default Actions:[/]")
            console.print(
                f"  Full packets: {', '.join(stateless.get('full_packets', []))}"
            )
            console.print(f"  Fragmented: {', '.join(stateless.get('fragmented', []))}")

        # Show stateful engine options
        stateful = policy.get("stateful_engine_options", {})
        if stateful:
            console.print("\n[bold]Stateful Engine:[/]")
            console.print(f"  Rule order: {stateful.get('rule_order', 'N/A')}")
            console.print(
                f"  Stream exception: {stateful.get('stream_exception_policy', 'N/A')}"
            )
