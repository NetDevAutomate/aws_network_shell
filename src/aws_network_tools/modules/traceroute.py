"""Traceroute module for AWS Network Shell."""

import asyncio
from rich.table import Table

from ..core import ModuleInterface
from ..traceroute import AWSTraceroute, TopologyDiscovery


class TracerouteModule(ModuleInterface):
    """Network path tracing module."""

    name = "traceroute"

    commands = {
        "trace": "Trace path: trace <src_ip> <dst_ip> [--skip-stale-check|--refresh-cache]",
        "refresh-topology": "Refresh the cached network topology",
    }

    context_commands = {}  # No context-specific commands

    show_commands = {
        None: ["topology-cache"],  # Root level show command
    }

    def register_show_handlers(self, shell):
        """Register show handlers on the shell."""
        shell._show_topology_cache = lambda arg=None: self._show_cache_info(shell)

    def execute(self, shell, command: str, args: str):
        if command == "trace":
            self._trace(shell, args)
        elif command == "refresh-topology":
            self._refresh_topology(shell)

    def handle_show(self, shell, option: str, args: str) -> bool:
        if option == "topology-cache":
            self._show_cache_info(shell)
            return True
        return False

    def _trace(self, shell, args: str):
        """Execute traceroute between two IPs."""
        parts = args.strip().split()

        # Parse flags
        skip_stale_check = "--skip-stale-check" in parts
        refresh_cache = "--refresh-cache" in parts

        # Remove flags from parts
        parts = [p for p in parts if not p.startswith("--")]

        if len(parts) < 2:
            shell.console.print(
                "[red]Usage: trace <src_ip> <dst_ip> [--skip-stale-check|--refresh-cache][/]"
            )
            shell.console.print(
                "[dim]  --skip-stale-check  Use cache without checking for changes (fastest)[/]"
            )
            shell.console.print(
                "[dim]  --refresh-cache     Force full topology rebuild[/]"
            )
            return

        src_ip, dst_ip = parts[0], parts[1]
        shell.console.print(f"\n[bold]Tracing {src_ip} → {dst_ip}[/]\n")

        def on_hop(hop):
            style = "green" if hop.type == "destination" else "white"
            if hop.type == "nfg":
                style = "yellow"
            elif hop.type == "firewall":
                style = "red"
            shell.console.print(
                f"[dim]{hop.seq}.[/] [{style}]{hop.type:18}[/] {hop.id} [dim]({hop.name})[/] @ {hop.region}"
            )

        def on_status(msg):
            shell.console.print(f"[dim]  → {msg}[/]")

        tracer = AWSTraceroute(
            profile=shell.profile,
            session=shell.session,
            on_hop=on_hop,
            on_status=on_status,
            no_cache=shell.no_cache,
            skip_stale_check=skip_stale_check,
            refresh_cache=refresh_cache,
        )

        result = asyncio.run(tracer.trace(src_ip, dst_ip))

        shell.console.print()
        if result.reachable:
            shell.console.print("[bold green]✅ REACHABLE[/]")
        else:
            shell.console.print("[bold red]❌ BLOCKED[/]")
            if result.blocked_reason:
                shell.console.print(f"[red]Reason:[/] {result.blocked_reason}")

    def _refresh_topology(self, shell):
        """Force refresh of topology cache."""
        shell.console.print("[dim]Refreshing topology cache...[/]")

        def on_status(msg):
            shell.console.print(f"[dim]  → {msg}[/]")

        discovery = TopologyDiscovery(
            profile=shell.profile, session=shell.session, on_status=on_status
        )
        discovery.clear_cache()
        asyncio.run(discovery.discover())
        shell.console.print("[green]Topology cache refreshed[/]")

    def _show_cache_info(self, shell):
        """Show topology cache status."""
        from ..core.cache import Cache

        cache = Cache("topology")
        info = cache.get_info()

        if not info:
            shell.console.print("[yellow]No topology cache found[/]")
            shell.console.print("Run 'trace' or 'refresh-topology' to build cache")
            return

        table = Table(title="Topology Cache")
        table.add_column("Property")
        table.add_column("Value")

        table.add_row("Cached at", str(info["cached_at"]))
        table.add_row("Age", f"{info['age_seconds']:.0f}s")
        table.add_row("TTL", f"{info['ttl_seconds']}s")
        table.add_row("Expired", "Yes" if info["expired"] else "No")
        table.add_row("Account", info.get("account_id", "unknown"))

        shell.console.print(table)

    def complete_trace(self, text, line, begidx, endidx):
        """Tab completion for trace command."""
        # parts = line.split()  # Not used
        # After 'trace', complete flags if starting with --
        if text.startswith("--"):
            options = ["--skip-stale-check", "--refresh-cache"]
            return [o for o in options if o.startswith(text)]
        return []
