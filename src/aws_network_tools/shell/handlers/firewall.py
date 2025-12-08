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
        try:
            selection_idx = int(val)
        except ValueError:
            selection_idx = 1
        self._enter("firewall", fw.get("arn", ""), fw.get("name", ""), fw, selection_idx)
        print()  # Add blank line before next prompt

    def _show_firewall(self, _):
        """Show detailed firewall information (renamed from detail)."""
        if self.ctx_type != "firewall":
            return
        from ...modules.anfw import ANFWDisplay
        ANFWDisplay(console).show_firewall_detail(self.ctx.data)

    # Alias for backward compatibility
    def _show_detail(self, _):
        """Alias for show firewall."""
        self._show_firewall(_)

    def _show_firewall_rule_groups(self, _):
        """Show firewall rule groups with index."""
        if self.ctx_type != "firewall":
            return
        rgs = self.ctx.data.get("rule_groups", [])
        if not rgs:
            console.print("[yellow]No rule groups[/]")
            return
        table = Table(title="Firewall Rule Groups")
        table.add_column("#", style="dim", justify="right")
        table.add_column("Name")
        table.add_column("Type")
        table.add_column("Rules", justify="right")
        table.add_column("Capacity", justify="right")
        for i, rg in enumerate(rgs, 1):
            table.add_row(
                str(i),
                rg.get("name", ""),
                rg.get("type", ""),
                str(len(rg.get("rules", []))),
                f"{rg.get('consumed_capacity', 0)}/{rg.get('capacity', 0)}"
            )
        console.print(table)
        console.print("[dim]Use 'set rule-group <#>' to select[/]")

    # Alias for backward compatibility
    def _show_rule_groups(self, arg):
        """Alias for firewall-rule-groups."""
        self._show_firewall_rule_groups(arg)

    def _set_rule_group(self, val):
        """Enter rule group context."""
        if self.ctx_type != "firewall":
            console.print("[red]Must be in firewall context[/]")
            return
        if not val:
            console.print("[red]Usage: set rule-group <#>[/]")
            return
        
        rgs = self.ctx.data.get("rule_groups", [])
        if not rgs:
            console.print("[yellow]No rule groups available[/]")
            return
        
        # Resolve by index or name
        rg = self._resolve(rgs, val)
        if not rg:
            console.print(f"[red]Rule group not found: {val}[/]")
            return
        
        try:
            selection_idx = int(val)
        except ValueError:
            selection_idx = 1
        
        self._enter("rule-group", rg.get("name", ""), rg.get("name", ""), rg, selection_idx)
        print()

    def _show_rule_group(self, _):
        """Show detailed rule group information."""
        if self.ctx_type != "rule-group":
            return
        
        rg = self.ctx.data
        from rich.panel import Panel
        from rich.text import Text
        
        console.print(
            Panel(
                f"[bold]{rg['name']}[/] ({rg['type']})",
                title="Rule Group"
            )
        )
        
        if rg.get("error"):
            console.print(f"[red]Error: {rg['error']}[/]")
            return
        
        cap_info = f"[dim]Capacity: {rg.get('consumed_capacity', 0)}/{rg.get('capacity', 0)}[/]"
        console.print(cap_info)
        console.print()
        
        if rg["type"] == "STATEFUL":
            # Stateful rules (Suricata format, domain lists, or 5-tuple)
            rules = rg.get("rules", [])
            if not rules:
                console.print("[dim]No rules found[/]")
                return
            
            table = Table(show_header=True, header_style="bold")
            table.add_column("#", style="dim", justify="right")
            table.add_column("Rule", style="cyan")
            
            for i, rule in enumerate(rules, 1):
                if "rule" in rule:
                    console.print(f"  [dim]{i}.[/] [cyan]{rule['rule']}[/]")
        else:
            # Stateless rules
            rules = rg.get("rules", [])
            if not rules:
                console.print("[dim]No rules found[/]")
                return
            
            table = Table(show_header=True, header_style="bold")
            table.add_column("#", style="dim", justify="right")
            table.add_column("Priority", style="yellow", justify="right")
            table.add_column("Actions", style="green")
            table.add_column("Sources", style="cyan")
            table.add_column("Destinations", style="magenta")
            table.add_column("Protocols", style="white")
            table.add_column("Source Ports", style="dim")
            table.add_column("Dest Ports", style="dim")
            
            for i, rule in enumerate(rules, 1):
                # Format source/dest ports
                src_ports = rule.get("source_ports", [])
                dst_ports = rule.get("dest_ports", [])
                
                src_port_str = ", ".join(
                    f"{p.get('FromPort', '')}-{p.get('ToPort', '')}" if p.get('FromPort') != p.get('ToPort') 
                    else str(p.get('FromPort', ''))
                    for p in src_ports
                ) if src_ports else "Any"
                
                dst_port_str = ", ".join(
                    f"{p.get('FromPort', '')}-{p.get('ToPort', '')}" if p.get('FromPort') != p.get('ToPort')
                    else str(p.get('FromPort', ''))
                    for p in dst_ports
                ) if dst_ports else "Any"
                
                table.add_row(
                    str(i),
                    str(rule.get("priority", "")),
                    ", ".join(rule.get("actions", [])),
                    ", ".join(rule.get("sources", [])) or "Any",
                    ", ".join(rule.get("destinations", [])) or "Any",
                    ", ".join(str(p) for p in rule.get("protocols", [])) or "Any",
                    src_port_str,
                    dst_port_str
                )
            
            console.print(table)

    def _show_policy(self, _):
        """Show firewall policy with rule groups summary."""
        if self.ctx_type != "firewall":
            return
        
        policy = self.ctx.data.get("policy", {})
        if not policy:
            console.print("[yellow]No policy data available[/]")
            return
        
        from rich.panel import Panel
        
        console.print(Panel(f"[bold]{policy.get('name', 'N/A')}[/]", title="Policy"))
        
        # Show rule groups in table format
        rgs = self.ctx.data.get("rule_groups", [])
        if rgs:
            table = Table(title="Rule Groups", show_header=True, header_style="bold")
            table.add_column("#", style="dim", justify="right")
            table.add_column("Name", style="cyan")
            table.add_column("Type", style="yellow")
            table.add_column("Rules", style="white", justify="right")
            table.add_column("Capacity", style="dim", justify="right")
            for i, rg in enumerate(rgs, 1):
                table.add_row(
                    str(i),
                    rg["name"],
                    rg["type"],
                    str(len(rg.get("rules", []))),
                    f"{rg.get('consumed_capacity', 0)}/{rg.get('capacity', 0)}"
                )
            console.print(table)
