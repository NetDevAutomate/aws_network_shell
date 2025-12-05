"""Main shell class composing all handler mixins."""

import yaml
from rich.console import Console

from .base import AWSNetShellBase
from .handlers import (
    RootHandlersMixin,
    CloudWANHandlersMixin,
    VPCHandlersMixin,
    TGWHandlersMixin,
    EC2HandlersMixin,
    FirewallHandlersMixin,
    VPNHandlersMixin,
    ELBHandlersMixin,
    UtilityHandlersMixin,
)

console = Console()


class AWSNetShell(
    RootHandlersMixin,
    CloudWANHandlersMixin,
    VPCHandlersMixin,
    TGWHandlersMixin,
    EC2HandlersMixin,
    FirewallHandlersMixin,
    VPNHandlersMixin,
    ELBHandlersMixin,
    UtilityHandlersMixin,
    AWSNetShellBase,
):
    """Cisco IOS-style hierarchical CLI for AWS networking."""

    def _cached(self, key: str, fetch_fn, msg: str = "Loading..."):
        from ..core import run_with_spinner

        if key not in self._cache or self.no_cache:
            self._cache[key] = run_with_spinner(fetch_fn, msg)
        return self._cache[key]

    def _emit_json_or_table(self, data, render_table_fn):
        if self.output_format == "json":
            try:
                import json

                console.print_json(json.dumps(data, default=str))
            except Exception:
                console.print(data)
        elif self.output_format == "yaml":
            try:
                console.print(yaml.safe_dump(data, sort_keys=False))
            except Exception:
                console.print(data)
        else:
            render_table_fn()

    # ==================== SHOW ====================

    def do_show(self, args):
        raw = str(args).strip()
        # Handle pipe operators: show vpcs | include prod
        pipe_filter = None
        if "|" in raw:
            raw, pipe_filter = raw.split("|", 1)

        parts = raw.strip().split()
        if not parts or parts[0] == "?":
            console.print("[bold]show options:[/]")
            for opt in sorted(self.hierarchy.get("show", [])):
                console.print(f"  show {opt}")
            console.print(
                "\n[dim]Pipe operators: | include <text>, | exclude <text>[/]"
            )
            return

        opt = parts[0]
        watch_n = None
        if "watch" in parts[1:]:
            try:
                idx = parts.index("watch")
                watch_n = int(parts[idx + 1]) if idx + 1 < len(parts) else None
                parts = parts[:idx]
            except Exception:
                watch_n = None
        arg = parts[1] if len(parts) > 1 else None

        # Special nested: 'show vpc <sub>'
        if opt == "vpc":
            sub = parts[1] if len(parts) > 1 else "?"
            if watch_n and watch_n > 0:
                self._watch_loop(lambda: self._show_vpc(sub), watch_n)
            else:
                self._run_with_pipe(lambda: self._show_vpc(sub), pipe_filter)
            return

        valid = self.hierarchy.get("show", [])
        if opt not in valid:
            console.print(f"[red]Invalid: '{opt}'. Valid: {', '.join(valid)}[/]")
            return

        handler = getattr(self, f"_show_{opt.replace('-', '_')}", None)
        if not handler:
            console.print(f"[yellow]Not implemented: show {opt}[/]")
            return

        if watch_n and watch_n > 0:
            self._watch_loop(lambda: handler(arg), watch_n)
        else:
            self._run_with_pipe(lambda: handler(arg), pipe_filter)

    def _run_with_pipe(self, fn, pipe_filter):
        """Run function and apply pipe filter if present."""
        if not pipe_filter:
            fn()
            return
        import io
        from rich.console import Console as RichConsole

        buf = io.StringIO()
        temp_console = RichConsole(file=buf, force_terminal=False, no_color=True)
        # Temporarily swap console
        import aws_network_tools.shell.main as main_mod

        orig = main_mod.console
        main_mod.console = temp_console
        try:
            fn()
        finally:
            main_mod.console = orig
        output = buf.getvalue()
        filtered = self._apply_pipe_filter(output, pipe_filter)
        console.print(filtered)

    def _watch_loop(self, fn, interval):
        import time

        try:
            while True:
                console.clear()
                fn()
                console.print(f"[dim]Watching every {interval}s — Ctrl-C to stop[/]")
                time.sleep(interval)
        except KeyboardInterrupt:
            return

    def complete_show(self, text, line, begidx, endidx):
        parts = line[:begidx].strip().split()
        if len(parts) <= 1:
            return [o for o in self.hierarchy.get("show", []) if o.startswith(text)]
        subcommand = parts[1] if len(parts) > 1 else ""
        if subcommand == "vpc":
            return (
                [o for o in ["subnets-all"] if o.startswith(text)]
                if len(parts) <= 2
                else []
            )
        if subcommand == "rib" and self.ctx_type == "core-network":
            options = []
            cn_data = self.ctx.data if self.ctx else {}
            policy = cn_data.get("policy", {})
            if text.startswith("segment=") or not any(
                p.startswith("segment=") for p in parts[2:]
            ):
                segments = [
                    s.get("name") for s in policy.get("segments", []) if s.get("name")
                ]
                if text.startswith("segment="):
                    prefix = text.split("=", 1)[1]
                    options.extend(
                        [f"segment={s}" for s in segments if s.startswith(prefix)]
                    )
                elif not text:
                    options.append("segment=")
            if text.startswith("edge=") or not any(
                p.startswith("edge=") for p in parts[2:]
            ):
                edges = [
                    e.get("location")
                    for e in policy.get("core-network-configuration", {}).get(
                        "edge-locations", []
                    )
                    if e.get("location")
                ]
                if text.startswith("edge="):
                    prefix = text.split("=", 1)[1]
                    options.extend([f"edge={e}" for e in edges if e.startswith(prefix)])
                elif not text:
                    options.append("edge=")
            return options
        return []

    # ==================== SET ====================

    def do_set(self, args):
        parts = str(args).strip().split(maxsplit=1)
        if not parts or parts[0] == "?":
            console.print("[bold]set options:[/]")
            for opt in sorted(self.hierarchy.get("set", [])):
                console.print(f"  set {opt}")
            return

        opt, val = parts[0], parts[1] if len(parts) > 1 else None
        valid = self.hierarchy.get("set", [])
        if opt not in valid:
            console.print(f"[red]Invalid: '{opt}'. Valid: {', '.join(valid)}[/]")
            return

        handler = getattr(self, f"_set_{opt.replace('-', '_')}", None)
        handler(val) if handler else console.print(
            f"[yellow]Not implemented: set {opt}[/]"
        )

    def complete_set(self, text, line, begidx, endidx):
        parts = line[:begidx].split()
        if len(parts) <= 1:
            return [o for o in self.hierarchy.get("set", []) if o.startswith(text)]
        key = parts[1]
        cache_key = {"transit-gateway": "tgw"}.get(key, key)
        items = self._cache.get(cache_key, [])
        return [str(i) for i, _ in enumerate(items, 1) if str(i).startswith(text)]

    # ==================== Context-aware route tables ====================

    def _show_route_tables(self, _):
        if self.ctx_type == "core-network":
            self._show_cloudwan_route_tables()
        elif self.ctx_type == "transit-gateway":
            self._show_transit_gateway_route_tables()
        elif self.ctx_type == "vpc":
            self._show_vpc_route_tables()
        elif self.ctx_type == "ec2-instance":
            from rich.table import Table

            rts = self.ctx.data.get("route_tables", [])
            if self.output_format == "json":
                self._emit_json_or_table(rts, lambda: None)
                return
            if not rts:
                console.print("[yellow]No route tables[/]")
                return
            table = Table(title="Instance Route Tables")
            table.add_column("ID")
            table.add_column("Routes")
            for rt in rts:
                table.add_row(rt.get("id", ""), str(len(rt.get("routes", []))))
            console.print(table)

    def _show_detail(self, _):
        from rich.table import Table
        from ..modules import tgw, vpc, cloudwan, elb, anfw

        if not self.ctx_type:
            console.print("[red]No context. Use 'set <resource> <#>' first.[/]")
            return
        if self.ctx_type == "transit-gateway":
            tgw.TGWDisplay(console).show_tgw_detail(self.ctx.data)
        elif self.ctx_type == "vpc":
            vpc.VPCDisplay(console).show_detail(self.ctx.data)
        elif self.ctx_type == "global-network":
            # global-network context stores core-network data
            if not self.ctx.data:
                console.print(
                    "[yellow]No data available. Try 'show core-networks' first.[/]"
                )
                return
            # Display global network details
            table = Table(title=f"Global Network: {self.ctx.name}")
            table.add_column("Field", style="cyan")
            table.add_column("Value")
            for k in ("id", "name", "state"):
                if self.ctx.data.get(k):
                    table.add_row(k, str(self.ctx.data.get(k)))
            console.print(table)
        elif self.ctx_type == "core-network":
            cloudwan.CloudWANDisplay(console).show_detail(self.ctx.data)
        elif self.ctx_type == "firewall":
            anfw.ANFWDisplay(console).show_firewall_detail(self.ctx.data)
        elif self.ctx_type == "elb":
            elb.ELBDisplay(console).show_elb_detail(self.ctx.data)
        elif self.ctx_type == "vpn":
            # VPN detail - show tunnel info and configuration
            vpn_data = self.ctx.data or {}
            table = Table(title=f"VPN: {self.ctx.name}")
            table.add_column("Field", style="cyan")
            table.add_column("Value")
            for k in ("id", "state", "type", "category"):
                if vpn_data.get(k):
                    table.add_row(k, str(vpn_data.get(k)))
            console.print(table)
            # Show tunnels if available
            tunnels = vpn_data.get("tunnels", [])
            if tunnels:
                console.print(f"\n[bold]Tunnels ({len(tunnels)}):[/]")
                for t in tunnels:
                    status = t.get("status", "")
                    style = "green" if status == "UP" else "red"
                    console.print(f"  [{style}]{status}[/] {t.get('outside_ip', '')}")
        elif self.ctx_type == "ec2-instance":
            inst = self.ctx.data or {}
            table = Table(title=f"Instance: {inst.get('id', self.ctx.name)}")
            table.add_column("Field", style="cyan")
            table.add_column("Value")
            for k in ("id", "type", "state", "az", "region"):
                if inst.get(k):
                    table.add_row(k, str(inst.get(k)))
            console.print(table)
        else:
            console.print(
                f"[yellow]Detail view not implemented for: {self.ctx_type}[/]"
            )

    # ==================== Context-aware find commands ====================

    def do_find_prefix(self, args):
        """Find prefix - context aware."""
        prefix = str(args).strip()

        # Route-table context (most specific)
        if self.ctx_type == "route-table":
            if not prefix:
                console.print("[red]Usage: find-prefix <cidr>[/]")
                return
            matches = [
                r
                for r in self.ctx.data.get("routes", [])
                if prefix in r.get("prefix", "")
                or r.get("prefix", "").startswith(prefix.split("/")[0])
            ]
            if not matches:
                console.print(f"[yellow]No match for {prefix}[/]")
                return
            for r in matches:
                console.print(f"{r['prefix']} -> {r['target']} ({r.get('state', '')})")
            return

        # Core-network context
        if self.ctx_type == "core-network":
            if not prefix:
                console.print("[red]Usage: find-prefix <cidr>[/]")
                return
            self._cloudwan_find_prefix(prefix)
            return

        # TGW context
        if self.ctx_type == "transit-gateway":
            if not prefix:
                console.print("[red]Usage: find-prefix <cidr>[/]")
                return
            self._tgw_find_prefix(prefix)
            return

        # VPC context
        if self.ctx_type == "vpc":
            if not prefix:
                console.print("[red]Usage: find-prefix <cidr>[/]")
                return
            self._vpc_find_prefix(prefix)
            return

        # Root context - search routing cache
        RootHandlersMixin.do_find_prefix(self, args)

    def do_find_null_routes(self, _):
        """Find blackhole/null routes - context aware."""
        # Route-table context
        if self.ctx_type == "route-table":
            nulls = [
                r
                for r in self.ctx.data.get("routes", [])
                if r.get("state", "").upper() == "BLACKHOLE"
            ]
            if not nulls:
                console.print("[green]No blackhole routes[/]")
                return
            for r in nulls:
                console.print(f"[red]{r['prefix']}[/] -> {r['target']}")
            return

        # Core-network context
        if self.ctx_type == "core-network":
            self._cloudwan_find_null_routes()
            return

        # TGW context
        if self.ctx_type == "transit-gateway":
            self._tgw_find_null_routes()
            return

        # VPC context
        if self.ctx_type == "vpc":
            self._vpc_find_null_routes()
            return

        # Root context - search routing cache
        RootHandlersMixin.do_find_null_routes(self, _)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='AWS Network Tools Interactive Shell')
    parser.add_argument('--profile', '-p', help='AWS profile to use')
    parser.add_argument('--no-cache', action='store_true', help='Disable caching')
    parser.add_argument('--format', choices=['table', 'json', 'yaml'], default='table', help='Output format')

    args, unknown = parser.parse_known_args()

    shell = AWSNetShell()
    if args.profile:
        shell.profile = args.profile
    if args.no_cache:
        shell.no_cache = True
    if args.format:
        shell.output_format = args.format

    shell.cmdloop()


if __name__ == "__main__":
    main()
