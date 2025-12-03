"""CLI for traceroute."""

import asyncio
import sys
import time
from rich.console import Console
from .engine import AWSTraceroute
from .topology import TopologyDiscovery


def main():
    args = sys.argv[1:]

    # Handle cache commands
    if "--clear-cache" in args:
        TopologyDiscovery().clear_cache()
        print("Cache cleared")
        return

    if len(args) < 2 or args[0].startswith("-"):
        print("Usage: aws-trace <src_ip> <dst_ip> [options]")
        print("Options:")
        print("  --profile <name>      AWS profile to use")
        print("  --no-cache            Don't use cached topology")
        print(
            "  --skip-stale-check    Use cache without checking for changes (fastest)"
        )
        print("  --refresh-cache       Force refresh of cached topology")
        print("  --clear-cache         Clear the topology cache and exit")
        sys.exit(1)

    src_ip = args[0]
    dst_ip = args[1]
    profile = None
    no_cache = "--no-cache" in args
    refresh_cache = "--refresh-cache" in args
    skip_stale_check = "--skip-stale-check" in args

    if "--profile" in args:
        idx = args.index("--profile")
        profile = args[idx + 1] if idx + 1 < len(args) else None

    console = Console()
    console.print(f"\n[bold]Tracing {src_ip} → {dst_ip}[/]\n")

    def on_hop(hop):
        style = "green" if hop.type == "destination" else "white"
        if hop.type == "nfg":
            style = "yellow"
        elif hop.type == "firewall":
            style = "red"
        console.print(
            f"[dim]{hop.seq}.[/] [{style}]{hop.type:18}[/] {hop.id} [dim]({hop.name})[/] @ {hop.region}"
        )

    def on_status(msg):
        console.print(f"[dim]  → {msg}[/]")

    tracer = AWSTraceroute(
        profile=profile,
        on_hop=on_hop,
        on_status=on_status,
        no_cache=no_cache,
        refresh_cache=refresh_cache,
        skip_stale_check=skip_stale_check,
    )

    start = time.time()
    result = asyncio.run(tracer.trace(src_ip, dst_ip))
    elapsed = time.time() - start

    console.print()
    if result.reachable:
        console.print(f"[bold green]✅ REACHABLE[/] in {elapsed:.1f}s")
    else:
        console.print(f"[bold red]❌ BLOCKED[/] in {elapsed:.1f}s")
        if result.blocked_reason:
            console.print(f"[red]Reason:[/] {result.blocked_reason}")


if __name__ == "__main__":
    main()
