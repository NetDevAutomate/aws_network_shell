"""Base display utilities"""

from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text


class BaseDisplay:
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()

    def print_cache_info(self, cache_info: Optional[dict]):
        if not cache_info:
            self.console.print("[yellow]Cache is empty[/]")
            return
        status = "[green]Valid[/]" if not cache_info["expired"] else "[red]Expired[/]"
        self.console.print(
            Panel(
                f"[bold]Status:[/] {status}\n"
                f"[bold]Cached At:[/] {cache_info['cached_at'].strftime('%Y-%m-%d %H:%M:%S')} UTC\n"
                f"[bold]Age:[/] {cache_info['age_seconds']:.1f}s\n"
                f"[bold]TTL:[/] {cache_info['ttl_seconds']}s",
                title="📦 Cache Information",
            )
        )

    def route_table(
        self, title: str, routes: list[dict], columns: list[tuple[str, str, str]]
    ) -> Table:
        """Create a route table with given columns: (name, style, key)"""
        table = Table(title=title, show_header=True, header_style="bold")
        for name, style, _ in columns:
            table.add_column(name, style=style)
        for route in routes:
            row = []
            for name, style, key in columns:
                val = route.get(key, "")
                if key == "state":
                    row.append(Text(val, style="green" if val == "active" else "red"))
                else:
                    row.append(str(val) if val else "")
            table.add_row(*row)
        return table
