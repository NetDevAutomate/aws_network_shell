"""Utility command handlers (trace, find_ip, run, cache, write)."""

from rich.console import Console
import boto3

console = Console()


class UtilityHandlersMixin:
    """Handlers for utility commands."""

    def do_write(self, args):
        """write <filename> - Save last output to file in current format."""
        filename = str(args).strip()
        if not filename:
            console.print("[red]Usage: write <filename>[/]")
            console.print(
                "[dim]Saves cached data in current output-format (table/json/yaml)[/]"
            )
            return
        # Get last cached data
        if not self._cache:
            console.print("[yellow]No cached data to save[/]")
            return
        # Save all cache or specific key
        data = dict(self._cache)
        self._save_output(data, filename)

    def do_populate_cache(self, _):
        """Pre-fetch all topology data."""
        if self.ctx_type is not None:
            console.print("[red]populate-cache only at root level[/]")
            return
        try:
            from ...traceroute.topology import TopologyDiscovery
            import asyncio
            import concurrent.futures

            def on_status(msg):
                console.print(f"[dim]  → {msg}[/]")

            discovery = TopologyDiscovery(profile=self.profile, on_status=on_status)
            console.print("[bold]Populating topology cache...[/]")
            try:
                # loop = asyncio.get_running_loop()  # Not used
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    pool.submit(asyncio.run, discovery.discover()).result()
            except RuntimeError:
                asyncio.run(discovery.discover())
            console.print("[green]Cache populated[/]")
        except ImportError as e:
            console.print(f"[yellow]Topology module not available: {e}[/]")

    def do_find_ip(self, args):
        """find_ip <IP> - Resolve IP to ENI and attached resource."""
        ip = str(args).strip()
        if not ip:
            console.print("[red]Usage: find_ip <ip>[/]")
            return
        from ...core.ip_resolver import IpResolver

        resolver = IpResolver(profile=self.profile)
        regions = self.regions or resolver.session.get_available_regions("ec2")
        eni_id = resolver.resolve_ip(ip, regions)
        if not eni_id:
            console.print(f"[yellow]No ENI found for {ip}[/]")
            return
        for region in regions:
            try:
                ec2 = boto3.Session(profile_name=self.profile).client(
                    "ec2", region_name=region
                )
                resp = ec2.describe_network_interfaces(NetworkInterfaceIds=[eni_id])
                if resp.get("NetworkInterfaces"):
                    eni = resp["NetworkInterfaces"][0]
                    console.print(
                        {
                            "eni_id": eni_id,
                            "region": region,
                            "vpc_id": eni.get("VpcId"),
                            "subnet_id": eni.get("SubnetId"),
                            "private_ip": eni.get("PrivateIpAddress"),
                            "public_ip": eni.get("Association", {}).get("PublicIp"),
                            "attachment": eni.get("Attachment", {}).get("InstanceId")
                            or eni.get("InterfaceType"),
                        }
                    )
                    return
            except Exception:
                continue
        console.print(f"[yellow]Found ENI {eni_id} but could not fetch details[/]")

    def do_run(self, args):
        """run <instance-id|ip> <command> - Run a shell command via SSM."""
        parts = str(args).strip().split(maxsplit=1)
        if len(parts) < 2:
            console.print("[red]Usage: run <instance-id|ip> <command>[/]")
            return
        target, cmd = parts[0], parts[1]
        session = boto3.Session(profile_name=self.profile)
        instance_id = inst_region = None
        regions = self.regions or session.get_available_regions("ec2")

        if target.startswith("i-"):
            for r in regions:
                try:
                    ec2 = session.client("ec2", region_name=r)
                    if ec2.describe_instances(InstanceIds=[target]).get("Reservations"):
                        instance_id, inst_region = target, r
                        break
                except Exception:
                    continue
        else:
            for r in regions:
                try:
                    ec2 = session.client("ec2", region_name=r)
                    for filt in [
                        {"Name": "private-ip-address", "Values": [target]},
                        {"Name": "ip-address", "Values": [target]},
                    ]:
                        resp = ec2.describe_instances(Filters=[filt])
                        for res in resp.get("Reservations", []):
                            for inst in res.get("Instances", []):
                                instance_id, inst_region = inst["InstanceId"], r
                                break
                        if instance_id:
                            break
                    if instance_id:
                        break
                except Exception:
                    continue

        if not instance_id:
            console.print(f"[red]Could not resolve target '{target}' to an instance[/]")
            return

        ssm = session.client("ssm", region_name=inst_region)
        try:
            resp = ssm.send_command(
                InstanceIds=[instance_id],
                DocumentName="AWS-RunShellScript",
                Parameters={"commands": [cmd]},
            )
            cmd_id = resp["Command"]["CommandId"]
            console.print(f"[dim]Sent, command-id:[/] {cmd_id}")
            import time

            end = time.time() + 120
            while time.time() < end:
                inv = ssm.get_command_invocation(
                    CommandId=cmd_id, InstanceId=instance_id
                )
                if inv.get("Status") in (
                    "Success",
                    "Cancelled",
                    "Failed",
                    "TimedOut",
                    "Undeliverable",
                    "Terminated",
                ):
                    break
                time.sleep(2)
            console.print(
                {
                    "Status": inv.get("Status"),
                    "StdOut": inv.get("StandardOutputContent", "").strip(),
                    "StdErr": inv.get("StandardErrorContent", "").strip(),
                }
            )
        except Exception as e:
            console.print(f"[red]SSM error:[/] {e}")

    def do_trace(self, args):
        if self.ctx_type is not None:
            console.print("[red]trace only at root level[/]")
            return
        parts = str(args).strip().split()
        flags = [p for p in parts if p.startswith("--")]
        ips = [p for p in parts if not p.startswith("--")]
        if len(ips) < 2:
            console.print("[red]Usage: trace <src_ip> <dst_ip> [--no-cache][/]")
            return
        try:
            from ..traceroute import AWSTraceroute
            import asyncio
            import concurrent.futures

            def on_hop(hop):
                style = {
                    "destination": "green",
                    "nfg": "yellow",
                    "firewall": "red",
                }.get(hop.type, "white")
                console.print(
                    f"[dim]{hop.seq}.[/] [{style}]{hop.type:18}[/] {hop.id} @ {hop.region}"
                )

            def on_status(msg):
                console.print(f"[dim]  → {msg}[/]")

            no_cache = self.no_cache or "--no-cache" in flags
            tracer = AWSTraceroute(
                profile=self.profile,
                on_hop=on_hop,
                on_status=on_status,
                no_cache=no_cache,
            )
            console.print(f"\n[bold]Tracing {ips[0]} → {ips[1]}[/]\n")
            try:
                # loop = asyncio.get_running_loop()  # Not used
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    result = pool.submit(
                        asyncio.run, tracer.trace(ips[0], ips[1])
                    ).result()
            except RuntimeError:
                result = asyncio.run(tracer.trace(ips[0], ips[1]))
            if result.reachable:
                console.print("\n[bold green]✅ REACHABLE[/]")
            else:
                console.print(
                    f"\n[bold red]❌ BLOCKED[/] {result.blocked_reason or ''}"
                )
        except ImportError as e:
            console.print(f"[yellow]Traceroute module not available: {e}[/]")

    # reachability command removed - duplicate of trace command
