"""EC2 instance context handlers."""

from rich.table import Table
from rich.console import Console

console = Console()


class EC2HandlersMixin:
    """Handlers for EC2 instance context."""

    def _show_ec2_instances(self, _):
        key = f"ec2-instance:{','.join(self.regions) if self.regions else 'all'}"
        if key not in self._cache or self.no_cache:
            from ...modules.ec2 import EC2Client
            from ...core import run_with_spinner

            self._cache[key] = run_with_spinner(
                lambda: EC2Client(self.profile).discover(self.regions or None),
                "Fetching EC2 instances",
            )
        instances = self._cache.get(key, [])
        if self.output_format == "json":
            self._emit_json_or_table(instances, lambda: None)
            return
        table = Table(title="EC2 Instances")
        table.add_column("#", style="dim")
        table.add_column("Name")
        table.add_column("ID")
        table.add_column("Type")
        table.add_column("State")
        table.add_column("AZ")
        table.add_column("Region")
        for i, inst in enumerate(instances, 1):
            table.add_row(
                str(i),
                inst.get("name") or "-",
                inst["id"],
                inst.get("type", ""),
                inst.get("state", ""),
                inst.get("az", ""),
                inst.get("region", ""),
            )
        console.print(table)
        console.print("[dim]Use 'set ec2-instance <#>' to select[/]")

    def _set_ec2_instance(self, val):
        if not val:
            console.print("[red]Usage: set ec2-instance <#>[/]")
            return
        key = f"ec2-instance:{','.join(self.regions) if self.regions else 'all'}"
        items = self._cache.get(key, [])
        if not items:
            console.print("[yellow]Run 'show ec2-instances' first[/]")
            return
        target = self._resolve(items, val)
        if not target:
            console.print(f"[red]Not found: {val}[/]")
            return
        from ...modules.ec2 import EC2Client
        from ...core import run_with_spinner

        detail = run_with_spinner(
            lambda: EC2Client(self.profile).get_instance_detail(
                target["id"], target["region"]
            ),
            "Fetching instance",
            console=console,
        )
        self._enter(
            "ec2-instance", target["id"], target.get("name") or target["id"], detail
        )

    def _show_enis(self, _):
        if self.ctx_type != "ec2-instance":
            return
        enis = self.ctx.data.get("enis", [])
        if self.output_format == "json":
            self._emit_json_or_table(enis, lambda: None)
            return
        if not enis:
            console.print("[yellow]No ENIs[/]")
            return
        table = Table(title="Instance ENIs")
        table.add_column("ID")
        table.add_column("Private IP")
        table.add_column("Public IP")
        table.add_column("Subnet")
        for e in enis:
            table.add_row(
                e.get("id", ""),
                e.get("private_ip", ""),
                e.get("public_ip", "") or "-",
                e.get("subnet_id", ""),
            )
        console.print(table)
