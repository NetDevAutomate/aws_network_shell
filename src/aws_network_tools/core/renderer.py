"""Unified display renderer for consistent Rich output."""

from typing import Any, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import json
import yaml


class DisplayRenderer:
    """Unified renderer for all CLI output with consistent styling."""

    # Color scheme for resource types
    COLORS = {
        "vpc": "blue",
        "subnet": "cyan",
        "tgw": "yellow",
        "firewall": "red",
        "ec2": "green",
        "eni": "magenta",
        "route": "white",
        "cloudwan": "bright_blue",
        "active": "green",
        "blackhole": "red",
        "available": "green",
        "pending": "yellow",
        "error": "red",
    }

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()

    def render(
        self,
        data: Any,
        fmt: str = "table",
        title: Optional[str] = None,
        columns: Optional[list[dict]] = None,
    ) -> bool:
        """Render data in specified format.

        Args:
            data: Data to render (list of dicts or single dict)
            fmt: Output format (table, json, yaml)
            title: Optional title for table
            columns: Column definitions for table [{name, key, style}]

        Returns:
            True if rendered as non-table format, False if table
        """
        if fmt == "json":
            self.console.print_json(json.dumps(data, default=str))
            return True
        if fmt == "yaml":
            self.console.print(yaml.safe_dump(data, sort_keys=False))
            return True
        return False

    def table(
        self,
        data: list[dict],
        title: str,
        columns: list[dict],
        show_index: bool = True,
        hint: Optional[str] = None,
    ) -> None:
        """Render data as a Rich table.

        Args:
            data: List of dicts to display
            title: Table title
            columns: List of {name, key, style?, width?}
            show_index: Whether to show row numbers
            hint: Optional hint text below table
        """
        if not data:
            self.console.print(f"[yellow]No {title.lower()} found[/]")
            return

        table = Table(title=title, show_header=True, header_style="bold")

        if show_index:
            table.add_column("#", style="dim", justify="right", width=4)

        for col in columns:
            table.add_column(
                col["name"],
                style=col.get("style", ""),
                width=col.get("width"),
                justify=col.get("justify", "left"),
            )

        for i, row in enumerate(data, 1):
            values = []
            if show_index:
                values.append(str(i))
            for col in columns:
                val = row.get(col["key"], "")
                if val is None:
                    val = "-"
                elif isinstance(val, list):
                    val = ", ".join(str(v) for v in val[:3])
                    if len(row.get(col["key"], [])) > 3:
                        val += "..."
                else:
                    val = str(val)
                # Apply state-based coloring
                if col["key"] == "state":
                    color = self.COLORS.get(val.lower(), "white")
                    val = f"[{color}]{val}[/]"
                values.append(val)
            table.add_row(*values)

        self.console.print(table)
        if hint:
            self.console.print(f"[dim]{hint}[/]")

    def detail(self, data: dict, title: str, fields: list[tuple[str, str]]) -> None:
        """Render detail view as a panel.

        Args:
            data: Dict with resource details
            title: Panel title
            fields: List of (label, key) tuples
        """
        lines = []
        for label, key in fields:
            val = data.get(key, "-")
            if isinstance(val, list):
                val = ", ".join(str(v) for v in val)
            lines.append(f"[bold]{label}:[/] {val}")

        self.console.print(Panel("\n".join(lines), title=title))

    def routes(self, routes: list[dict], title: str) -> None:
        """Render route table with state coloring."""
        columns = [
            {"name": "Prefix", "key": "prefix", "style": "cyan"},
            {"name": "Target", "key": "target"},
            {"name": "Type", "key": "type"},
            {"name": "State", "key": "state"},
        ]
        self.table(routes, title, columns, show_index=False)

    def status(self, message: str, style: str = "green") -> None:
        """Print a status message."""
        self.console.print(f"[{style}]{message}[/]")

    def error(self, message: str) -> None:
        """Print an error message."""
        self.console.print(f"[red]{message}[/]")

    def warning(self, message: str) -> None:
        """Print a warning message."""
        self.console.print(f"[yellow]{message}[/]")

    def info(self, message: str) -> None:
        """Print an info message."""
        self.console.print(f"[dim]{message}[/]")
