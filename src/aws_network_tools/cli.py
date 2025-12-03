"""AWS Network Tools CLI"""

import typer
from typing import Optional
from rich.console import Console
import boto3
import json
import time
import yaml
import logging

from .core import run_with_spinner
from .core.cache import parse_ttl, get_default_ttl, set_default_ttl
from .modules import tgw, anfw, vpc, cloudwan

app = typer.Typer(
    name="aws-net",
    help="AWS networking discovery and analysis tools",
    no_args_is_help=True,
)
console = Console()


class Ctx:
    def __init__(self):
        self.profile: Optional[str] = None
        self.regions: list[str] = []
        self.format: str = "table"
        self.limit: Optional[int] = None
        self.watch: int = 0
        self.debug: bool = False
        self.max_workers: int = 10


# Global context instance
gctx = Ctx()

ALL_CACHES = [
    ("cloudwan", cloudwan.cache),
    ("tgw", tgw.cache),
    ("anfw", anfw.cache),
    ("vpc", vpc.cache),
]

# Optional module caches (loaded lazily)
try:
    from .modules import (
        route53_resolver,
        peering,
        prefix_lists,
        network_alarms,
        client_vpn,
        global_accelerator,
        privatelink,
        eni,
        vpn,
    )

    ALL_CACHES.extend(
        [
            ("route53_resolver", route53_resolver.cache),
            ("peering", peering.cache),
            ("prefix_lists", prefix_lists.cache),
            ("network_alarms", network_alarms.cache),
            ("client_vpn", client_vpn.cache),
            ("global_accelerator", global_accelerator.cache),
            ("privatelink", privatelink.cache),
            ("eni", eni.cache),
            ("vpn", vpn.cache),
        ]
    )
except Exception:
    pass


def _render(data, fmt: str):
    if fmt == "table":
        return False  # caller should render with display
    if fmt == "json":
        console.print_json(json.dumps(data, default=str))
        return True
    if fmt == "yaml":
        console.print(yaml.safe_dump(data, sort_keys=False))
        return True
    console.print(f"[yellow]Unknown format: {fmt}. Defaulting to table.[/]")
    return False


def get_account_id(profile: Optional[str] = None) -> Optional[str]:
    """Get current AWS account ID"""
    try:
        session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        return session.client("sts").get_caller_identity()["Account"]
    except Exception:
        return None


def get_or_fetch(
    cache_obj,
    client_class,
    profile: str,
    no_cache: bool,
    refresh_cache: bool,
    cache_ttl: int,
    msg: str,
):
    account_id = get_account_id(profile)

    if refresh_cache:
        cache_obj.clear()
        console.print("[dim]Cache cleared[/]")
    if not no_cache and not refresh_cache:
        info = cache_obj.get_info()
        if info:
            # Check account mismatch
            if (
                info.get("account_id")
                and account_id
                and info["account_id"] != account_id
            ):
                cache_obj.clear()
                console.print(
                    f"[yellow]Cache was for different account ({info['account_id']}), cleared[/]"
                )
            elif info.get("expired"):
                cache_obj.clear()
                console.print("[dim]Stale cache cleared[/]")
            else:
                cached = cache_obj.get(current_account=account_id)
                if cached:
                    console.print("[dim]Using cached data[/]")
                    return cached

    client = client_class(profile)
    data = run_with_spinner(client.discover, msg, console=console)
    if not no_cache:
        cache_obj.set(data, cache_ttl or get_default_ttl(), account_id)
    return data


def get_cached_or_fetch(
    cache_obj, client_class, profile: str, no_cache: bool, msg: str
):
    """Get from cache or fetch - clears stale/wrong-account cache automatically"""
    account_id = get_account_id(profile)

    if no_cache:
        client = client_class(profile)
        return run_with_spinner(client.discover, msg, console=console)

    info = cache_obj.get_info()
    if info:
        if info.get("account_id") and account_id and info["account_id"] != account_id:
            cache_obj.clear()
            console.print(
                f"[yellow]Cache was for different account ({info['account_id']}), cleared[/]"
            )
        elif info.get("expired"):
            cache_obj.clear()
            console.print("[dim]Stale cache cleared[/]")

    data = cache_obj.get(current_account=account_id)
    if data:
        console.print("[dim]Using cached data[/]")
        return data

    client = client_class(profile)
    data = run_with_spinner(client.discover, msg, console=console)
    cache_obj.set(data, account_id=account_id)
    return data


@app.callback()
def _global(
    profile: Optional[str] = typer.Option(None, "--profile", "-p"),
    regions: Optional[str] = typer.Option(
        None, "--regions", help="CSV list of regions"
    ),
    output_format: str = typer.Option("table", "--format", help="table|json|yaml"),
    limit: Optional[int] = typer.Option(
        None, "--limit", help="Limit rows in list outputs"
    ),
    watch: int = typer.Option(
        0, "--watch", help="Refresh every N seconds (list outputs)"
    ),
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging"),
    max_workers: int = typer.Option(
        10, "--max-workers", help="Thread pool size for discovery"
    ),
):
    gctx.profile = profile
    gctx.regions = [r.strip() for r in regions.split(",")] if regions else []
    gctx.format = output_format
    gctx.limit = limit
    gctx.watch = watch
    gctx.debug = debug
    gctx.max_workers = max_workers
    if debug:
        logging.basicConfig(level=logging.DEBUG)


# ============ Top-level Commands ============
@app.command("clear-cache")
def clear_all_cache():
    """Clear all module caches"""
    for name, cache_obj in ALL_CACHES:
        try:
            cache_obj.clear()
            console.print(f"[green]Cleared {name} cache[/]")
        except Exception as e:
            console.print(f"[yellow]Skip {name} cache: {e}[/]")

    # Clear traceroute topology and staleness markers
    try:
        from .traceroute.topology import TopologyDiscovery
        from .traceroute.staleness import StalenessChecker

        TopologyDiscovery().clear_cache()
        StalenessChecker()._markers_cache.clear()
        console.print("[green]Cleared traceroute topology & markers[/]")
    except Exception as e:
        console.print(f"[yellow]Skip traceroute caches: {e}[/]")

    console.print("[bold green]All caches cleared[/]")


@app.command("cache-timeout")
def set_cache_timeout(
    timeout: str = typer.Argument(
        ...,
        help="Timeout value: number with optional m(inutes)/h(ours)/d(ays) suffix. e.g. 15m, 1h, 2d",
    ),
):
    """Set default cache timeout (e.g. 15m, 1h, 2d)"""
    try:
        seconds = parse_ttl(timeout)
        set_default_ttl(seconds)

        # Format for display
        if seconds >= 86400:
            display = f"{seconds // 86400}d"
        elif seconds >= 3600:
            display = f"{seconds // 3600}h"
        else:
            display = f"{seconds // 60}m"

        console.print(f"[green]Cache timeout set to {display} ({seconds} seconds)[/]")
    except ValueError as e:
        console.print(f"[red]{e}[/]")
        raise typer.Exit(1)


@app.command("show-config")
def show_config():
    """Show current configuration"""
    ttl = get_default_ttl()
    if ttl >= 86400:
        display = f"{ttl // 86400}d"
    elif ttl >= 3600:
        display = f"{ttl // 3600}h"
    else:
        display = f"{ttl // 60}m"
    console.print(f"[bold]Cache timeout:[/] {display} ({ttl} seconds)")


# ============ Cloud WAN Commands ============
cwan_app = typer.Typer(
    help="Cloud WAN: cloudwan <ref> [route-table <n>]", invoke_without_command=True
)
app.add_typer(cwan_app, name="cloudwan")


@cwan_app.callback(invoke_without_command=True)
def cwan_main(
    ctx: typer.Context,
    ref: Optional[str] = typer.Argument(
        None, help="Core Network index/name/ID, or command"
    ),
    subcommand: Optional[str] = typer.Argument(None, help="Subcommand: route-table"),
    item_ref: Optional[str] = typer.Argument(None, help="Item index/name/ID"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Don't use cache"),
    refresh_cache: bool = typer.Option(
        False, "--refresh-cache", help="Force refresh cache"
    ),
    cache_ttl: Optional[int] = typer.Option(
        None, "--cache-ttl", help="Cache TTL in seconds"
    ),
):
    """Cloud WAN commands"""
    if ref is None:
        console.print(ctx.get_help())
        return

    if ref == "discover":
        data = get_or_fetch(
            cloudwan.cache,
            cloudwan.CloudWANClient,
            profile,
            no_cache,
            refresh_cache,
            cache_ttl,
            "Discovering Cloud WAN",
        )
        if _render(data if not gctx.limit else data[: gctx.limit], gctx.format):
            if gctx.watch > 0:
                try:
                    while True:
                        time.sleep(gctx.watch)
                        data = get_or_fetch(
                            cloudwan.cache,
                            cloudwan.CloudWANClient,
                            profile,
                            no_cache,
                            refresh_cache,
                            cache_ttl,
                            "Discovering Cloud WAN",
                        )
                        _render(
                            data if not gctx.limit else data[: gctx.limit], gctx.format
                        )
                except KeyboardInterrupt:
                    pass
            return
        # table mode
        to_show = data if not gctx.limit else data[: gctx.limit]
        cloudwan.CloudWANDisplay(console).show_list(to_show)
        if gctx.watch > 0:
            try:
                while True:
                    time.sleep(gctx.watch)
                    data = get_or_fetch(
                        cloudwan.cache,
                        cloudwan.CloudWANClient,
                        profile,
                        no_cache,
                        refresh_cache,
                        cache_ttl,
                        "Discovering Cloud WAN",
                    )
                    console.clear()
                    cloudwan.CloudWANDisplay(console).show_list(
                        data if not gctx.limit else data[: gctx.limit]
                    )
            except KeyboardInterrupt:
                pass
        return
    if ref == "get-prefixes":
        data = get_or_fetch(
            cloudwan.cache,
            cloudwan.CloudWANClient,
            profile,
            no_cache,
            refresh_cache,
            cache_ttl,
            "Fetching Cloud WAN prefixes",
        )
        cloudwan.CloudWANDisplay(console).show_prefixes(data)
        return
    if ref == "find-prefix":
        if not subcommand:
            console.print("[red]Usage: cloudwan find-prefix <query>[/]")
            raise typer.Exit(1)
        data = get_cached_or_fetch(
            cloudwan.cache,
            cloudwan.CloudWANClient,
            profile,
            no_cache,
            "Fetching Cloud WAN data",
        )
        matches = cloudwan.search_prefixes(data, subcommand, 60, 50)
        cloudwan.CloudWANDisplay(console).show_matches(matches, subcommand)
        return
    if ref == "show-cache":
        cloudwan.CloudWANDisplay(console).print_cache_info(cloudwan.cache.get_info())
        return
    if ref == "clear-cache":
        cloudwan.cache.clear()
        console.print("[green]Cache cleared[/]")
        return

    data = get_cached_or_fetch(
        cloudwan.cache,
        cloudwan.CloudWANClient,
        profile,
        no_cache,
        "Discovering Cloud WAN",
    )
    target = cloudwan.resolve_network(data, ref)
    if not target:
        console.print(f"[red]Core Network '{ref}' not found[/]")
        raise typer.Exit(1)

    if subcommand is None:
        cloudwan.CloudWANDisplay(console).show_detail(target)
    elif subcommand == "route-table":
        if not item_ref:
            console.print("[red]Usage: cloudwan <ref> route-table <rt-ref>[/]")
            raise typer.Exit(1)
        cloudwan.CloudWANDisplay(console).show_route_table(target, item_ref)
    else:
        console.print(f"[red]Unknown subcommand: {subcommand}[/]")
        raise typer.Exit(1)


# ============ TGW Commands ============
tgw_app = typer.Typer(
    help="Transit Gateway: transit_gateway <ref> [route-table <n>]",
    invoke_without_command=True,
)
app.add_typer(tgw_app, name="transit_gateway")


@tgw_app.callback(invoke_without_command=True)
def tgw_main(
    ctx: typer.Context,
    ref: Optional[str] = typer.Argument(None, help="TGW index/name/ID, or command"),
    subcommand: Optional[str] = typer.Argument(None, help="Subcommand: route-table"),
    item_ref: Optional[str] = typer.Argument(None, help="Item index/name/ID"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Don't use cache"),
    refresh_cache: bool = typer.Option(
        False, "--refresh-cache", help="Force refresh cache"
    ),
    cache_ttl: Optional[int] = typer.Option(
        None, "--cache-ttl", help="Cache TTL in seconds"
    ),
):
    """Transit Gateway commands"""
    if ref is None:
        console.print(ctx.get_help())
        return

    if ref == "discover":
        data = get_or_fetch(
            tgw.cache,
            tgw.TGWClient,
            profile,
            no_cache,
            refresh_cache,
            cache_ttl,
            "Discovering Transit Gateways",
        )
        if _render(data if not gctx.limit else data[: gctx.limit], gctx.format):
            return
        tgw.TGWDisplay(console).show_list(
            data if not gctx.limit else data[: gctx.limit]
        )
        return
    if ref == "get-prefixes":
        data = get_or_fetch(
            tgw.cache,
            tgw.TGWClient,
            profile,
            no_cache,
            refresh_cache,
            cache_ttl,
            "Fetching TGW prefixes",
        )
        tgw.TGWDisplay(console).show_prefixes(data)
        return
    if ref == "find-prefix":
        if not subcommand:
            console.print("[red]Usage: transit_gateway find-prefix <query>[/]")
            raise typer.Exit(1)
        data = get_cached_or_fetch(
            tgw.cache, tgw.TGWClient, profile, no_cache, "Fetching TGW data"
        )
        matches = tgw.search_prefixes(data, subcommand, 60, 50)
        tgw.TGWDisplay(console).show_matches(matches, subcommand)
        return
    if ref == "show-cache":
        tgw.TGWDisplay(console).print_cache_info(tgw.cache.get_info())
        return
    if ref == "clear-cache":
        tgw.cache.clear()
        console.print("[green]Cache cleared[/]")
        return

    data = get_cached_or_fetch(
        tgw.cache, tgw.TGWClient, profile, no_cache, "Discovering Transit Gateways"
    )
    target = tgw.resolve_tgw(data, ref)
    if not target:
        console.print(f"[red]Transit Gateway '{ref}' not found[/]")
        raise typer.Exit(1)

    if subcommand is None:
        tgw.TGWDisplay(console).show_tgw_detail(target)
    elif subcommand == "route-table":
        if not item_ref:
            console.print("[red]Usage: transit_gateway <ref> route-table <rt-ref>[/]")
            raise typer.Exit(1)
        tgw.TGWDisplay(console).show_route_table(target, item_ref)
    else:
        console.print(f"[red]Unknown subcommand: {subcommand}[/]")
        raise typer.Exit(1)


# ============ ANFW Commands ============
anfw_app = typer.Typer(
    help="Network Firewall: aws_network_firewall <ref> [rule-group <n>]",
    invoke_without_command=True,
)
app.add_typer(anfw_app, name="aws_network_firewall")


@anfw_app.callback(invoke_without_command=True)
def anfw_main(
    ctx: typer.Context,
    ref: Optional[str] = typer.Argument(
        None, help="Firewall index/name/ID, or command"
    ),
    subcommand: Optional[str] = typer.Argument(None, help="Subcommand: rule-group"),
    item_ref: Optional[str] = typer.Argument(None, help="Item index/name"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Don't use cache"),
    refresh_cache: bool = typer.Option(
        False, "--refresh-cache", help="Force refresh cache"
    ),
    cache_ttl: Optional[int] = typer.Option(
        None, "--cache-ttl", help="Cache TTL in seconds"
    ),
):
    """Network Firewall commands"""
    if ref is None:
        console.print(ctx.get_help())
        return

    if ref == "discover":
        data = get_or_fetch(
            anfw.cache,
            anfw.ANFWClient,
            profile,
            no_cache,
            refresh_cache,
            cache_ttl,
            "Discovering Network Firewalls",
        )
        if _render(data if not gctx.limit else data[: gctx.limit], gctx.format):
            return
        anfw.ANFWDisplay(console).show_list(
            data if not gctx.limit else data[: gctx.limit]
        )
        return
    if ref == "get-policies":
        data = get_or_fetch(
            anfw.cache,
            anfw.ANFWClient,
            profile,
            no_cache,
            refresh_cache,
            cache_ttl,
            "Fetching firewall policies",
        )
        anfw.ANFWDisplay(console).show_policies(data)
        return
    if ref == "show-cache":
        anfw.ANFWDisplay(console).print_cache_info(anfw.cache.get_info())
        return
    if ref == "clear-cache":
        anfw.cache.clear()
        console.print("[green]Cache cleared[/]")
        return

    data = get_cached_or_fetch(
        anfw.cache, anfw.ANFWClient, profile, no_cache, "Discovering firewalls"
    )
    target = anfw.resolve_firewall(data, ref)
    if not target:
        console.print(f"[red]Firewall '{ref}' not found[/]")
        raise typer.Exit(1)

    if subcommand is None:
        anfw.ANFWDisplay(console).show_firewall_detail(target)
    elif subcommand == "rule-group":
        if not item_ref:
            console.print(
                "[red]Usage: aws_network_firewall <ref> rule-group <rg-ref>[/]"
            )
            raise typer.Exit(1)
        anfw.ANFWDisplay(console).show_rule_group([target], item_ref)
    else:
        console.print(f"[red]Unknown subcommand: {subcommand}[/]")
        raise typer.Exit(1)


# ============ VPC Commands ============
vpc_app = typer.Typer(
    help="VPC: vpc <ref> [route-table|security-group|nacl <n>]",
    invoke_without_command=True,
)
app.add_typer(vpc_app, name="vpc")


@vpc_app.callback(invoke_without_command=True)
def vpc_main(
    ctx: typer.Context,
    ref: Optional[str] = typer.Argument(None, help="VPC index/name/ID, or command"),
    subcommand: Optional[str] = typer.Argument(
        None, help="Subcommand: route-table, security-group, nacl"
    ),
    item_ref: Optional[str] = typer.Argument(None, help="Item index/name/ID"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Don't use cache"),
    refresh_cache: bool = typer.Option(
        False, "--refresh-cache", help="Force refresh cache"
    ),
    cache_ttl: Optional[int] = typer.Option(
        None, "--cache-ttl", help="Cache TTL in seconds"
    ),
):
    """VPC commands"""
    if ref is None:
        console.print(ctx.get_help())
        return

    if ref in ("list", "discover"):
        data = get_or_fetch(
            vpc.cache,
            vpc.VPCClient,
            profile,
            no_cache,
            refresh_cache,
            cache_ttl,
            "Discovering VPCs",
        )
        if _render(data if not gctx.limit else data[: gctx.limit], gctx.format):
            return
        vpc.VPCDisplay(console).show_list(
            data if not gctx.limit else data[: gctx.limit]
        )
        return
    if ref == "show-cache":
        vpc.VPCDisplay(console).print_cache_info(vpc.cache.get_info())
        return
    if ref == "clear-cache":
        vpc.cache.clear()
        console.print("[green]Cache cleared[/]")
        return

    vpcs = get_cached_or_fetch(
        vpc.cache, vpc.VPCClient, profile, no_cache, "Discovering VPCs"
    )
    target = vpc.resolve_vpc(vpcs, ref)
    if not target:
        console.print(
            f"[red]VPC '{ref}' not found. Use 'vpc list' to see available VPCs.[/]"
        )
        raise typer.Exit(1)

    client = vpc.VPCClient(profile)
    detail = run_with_spinner(
        lambda: client.get_vpc_detail(target["id"], target["region"]),
        "Fetching VPC details",
        console=console,
    )

    if subcommand is None:
        vpc.VPCDisplay(console).show_detail(detail)
    elif subcommand == "route-table":
        if not item_ref:
            console.print("[red]Usage: vpc <ref> route-table <rt-ref>[/]")
            raise typer.Exit(1)
        vpc.VPCDisplay(console).show_route_table(detail, item_ref)
    elif subcommand == "security-group":
        if not item_ref:
            console.print("[red]Usage: vpc <ref> security-group <sg-ref>[/]")
            raise typer.Exit(1)
        vpc.VPCDisplay(console).show_security_group(detail, item_ref)
    elif subcommand == "nacl":
        if not item_ref:
            console.print("[red]Usage: vpc <ref> nacl <nacl-ref>[/]")
            raise typer.Exit(1)
        vpc.VPCDisplay(console).show_nacl(detail, item_ref)
    else:
        console.print(f"[red]Unknown subcommand: {subcommand}[/]")
        raise typer.Exit(1)


@app.command("find-ip")
def find_ip_cmd(ip: str = typer.Argument(..., help="IPv4 or IPv6 address")):
    """Resolve an IP to its ENI and attached resource across regions."""
    from .core.ip_resolver import IpResolver

    resolver = IpResolver(profile=gctx.profile)
    regions = gctx.regions or resolver.session.get_available_regions("ec2")
    eni_id = resolver.resolve_ip(ip, regions)
    if not eni_id:
        console.print(f"[yellow]No ENI found for {ip}[/]")
        raise typer.Exit(1)
    # Get details of the ENI
    for region in regions:
        ec2 = boto3.Session(profile_name=gctx.profile).client("ec2", region_name=region)
        try:
            resp = ec2.describe_network_interfaces(NetworkInterfaceIds=[eni_id])
            if resp.get("NetworkInterfaces"):
                eni = resp["NetworkInterfaces"][0]
                out = {
                    "eni_id": eni_id,
                    "region": region,
                    "vpc_id": eni.get("VpcId"),
                    "subnet_id": eni.get("SubnetId"),
                    "private_ip": eni.get("PrivateIpAddress"),
                    "public_ip": eni.get("Association", {}).get("PublicIp"),
                    "attachment": eni.get("Attachment", {}).get("InstanceId")
                    or eni.get("InterfaceType"),
                }
                if _render(out, gctx.format):
                    return
                console.print(out)
                return
        except Exception:
            continue
    console.print(f"[yellow]Found ENI {eni_id} but could not fetch details[/]")


@app.command("run")
def run_cmd(
    target: str = typer.Argument(..., help="Instance ID (i-...) or IP address"),
    command: str = typer.Argument(..., help="Shell command to run on the instance"),
    document: str = typer.Option(
        "AWS-RunShellScript", "--document", help="SSM document name"
    ),
    region: Optional[str] = typer.Option(
        None, "--region", help="AWS region; defaults to context or instance's region"
    ),
    timeout: int = typer.Option(
        120, "--timeout", help="Seconds to wait for command output"
    ),
    no_wait: bool = typer.Option(
        False, "--no-wait", help="Do not wait for command to finish"
    ),
):
    """Run a shell command on an EC2 instance via SSM."""
    session = boto3.Session(profile_name=gctx.profile)

    def resolve_instance(inp: str) -> tuple[Optional[str], Optional[str]]:
        if inp.startswith("i-"):
            # Try provided region or search context regions
            regions = (
                [region]
                if region
                else (gctx.regions or session.get_available_regions("ec2"))
            )
            for r in regions:
                ec2 = session.client("ec2", region_name=r)
                try:
                    resp = ec2.describe_instances(InstanceIds=[inp])
                    if resp.get("Reservations"):
                        return inp, r
                except Exception:
                    continue
            return inp, None
        # Assume IP
        regions = (
            [region]
            if region
            else (gctx.regions or session.get_available_regions("ec2"))
        )
        for r in regions:
            ec2 = session.client("ec2", region_name=r)
            try:
                resp = ec2.describe_instances(
                    Filters=[
                        {"Name": "private-ip-address", "Values": [inp]},
                    ]
                )
                for res in resp.get("Reservations", []):
                    for inst in res.get("Instances", []):
                        return inst["InstanceId"], r
                # Try public IP
                resp = ec2.describe_instances(
                    Filters=[
                        {"Name": "ip-address", "Values": [inp]},
                    ]
                )
                for res in resp.get("Reservations", []):
                    for inst in res.get("Instances", []):
                        return inst["InstanceId"], r
            except Exception:
                continue
        return None, None

    instance_id, inst_region = resolve_instance(target)
    if not instance_id:
        console.print(f"[red]Could not resolve target '{target}' to an instance[/]")
        raise typer.Exit(1)
    inst_region = inst_region or region or (gctx.regions[0] if gctx.regions else None)
    if not inst_region:
        console.print("[red]Region could not be determined; specify --region[/]")
        raise typer.Exit(1)

    ssm = session.client("ssm", region_name=inst_region)
    params = {"commands": [command]}
    try:
        resp = ssm.send_command(
            InstanceIds=[instance_id],
            DocumentName=document,
            Parameters=params,
        )
        cmd_id = resp["Command"]["CommandId"]
        console.print(f"[dim]Sent, command-id:[/] {cmd_id}")
        if no_wait:
            return
        # poll for result
        import time as _time

        end = _time.time() + timeout
        while _time.time() < end:
            inv = ssm.get_command_invocation(CommandId=cmd_id, InstanceId=instance_id)
            status = inv.get("Status")
            if status in (
                "Success",
                "Cancelled",
                "Failed",
                "TimedOut",
                "Undeliverable",
                "Terminated",
            ):
                break
            _time.sleep(2)
        # Print output
        out = {
            "Status": inv.get("Status"),
            "StdOut": inv.get("StandardOutputContent", "").strip(),
            "StdErr": inv.get("StandardErrorContent", "").strip(),
        }
        if _render(out, gctx.format):
            return
        console.print(out)
    except Exception as e:
        console.print(f"[red]SSM error:[/] {e}")
        raise typer.Exit(1)


def main():
    app()


if __name__ == "__main__":
    main()
