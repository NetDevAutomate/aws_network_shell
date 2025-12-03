"""Direct Connect (DX) module"""

import concurrent.futures
from typing import Optional, Dict, List
import boto3
from rich.table import Table
from rich.tree import Tree
from rich.panel import Panel
from rich.text import Text

from ..core import (
    Cache,
    BaseDisplay,
    BaseClient,
    ModuleInterface,
    run_with_spinner,
    Context,
)

cache = Cache("dx")


class DXModule(ModuleInterface):
    @property
    def name(self) -> str:
        return "dx"

    @property
    def commands(self) -> Dict[str, str]:
        return {"dx": "Enter Direct Connect context: dx <#|name|id>"}

    @property
    def context_commands(self) -> Dict[str, List[str]]:
        return {
            "dx": ["virtual-interface"],
        }

    @property
    def show_commands(self) -> Dict[str, List[str]]:
        return {None: ["direct-connect"], "dx": ["detail", "virtual-interfaces"]}

    def complete_dx(self, text, line, begidx, endidx):
        """Tab completion for dx command"""
        # We need access to shell to get cached data
        # But module methods don't get shell passed in completion
        # However, shell.py registers this method as a method of shell instance
        # So 'self' will be the shell instance when called!

        # Wait, in shell.py: setattr(self, complete_method, getattr(mod, complete_method))
        # This binds the method to the shell instance, but the method itself is defined on the module class.
        # If it's an instance method on Module, 'self' is the Module instance.
        # If we want access to shell data, we might need a different approach or rely on cache directly.

        # Actually, looking at shell.py:
        # setattr(self, complete_method, getattr(mod, complete_method))
        # This copies the bound method from mod instance to shell instance.
        # So 'self' inside complete_dx will be the DXModule instance.

        # To get data, we can use the cache directly since it's file-based and shared.
        # Or we can try to access the shell instance if we had a reference, but we don't.
        # Using cache.get() is the safest way to get data without triggering a fetch during completion.

        data = cache.get(ignore_expiry=True)
        if not data:
            return []

        candidates = []
        for item in data:
            candidates.append(item["id"])
            if item.get("name"):
                candidates.append(item["name"])

        return [c for c in candidates if c.startswith(text)]

    def execute(self, shell, command: str, args: str):
        """Enter Direct Connect context"""
        if shell.ctx_type is not None:
            shell.console.print("[red]Use 'end' to return to top level first[/]")
            return

        ref = args.strip()
        if not ref:
            shell.console.print("[red]Usage: dx <#|name|id>[/]")
            return

        # Access shell._get_dx() if available, or fetch directly
        if hasattr(shell, "_get_dx"):
            connections = shell._get_dx()
        else:
            # Fallback if shell method not yet registered/available
            connections = DXClient(shell.profile).discover()

        target = resolve_connection(connections, ref)

        if not target:
            shell.console.print(f"[red]Connection '{ref}' not found[/]")
            return

        client = DXClient(shell.profile)
        detail = run_with_spinner(
            lambda: client.get_connection_detail(target["id"], target["region"]),
            "Fetching Connection details",
            console=shell.console,
        )

        shell.context_stack = [
            Context("dx", ref, target.get("name") or target["id"], detail)
        ]
        shell._update_prompt()


class DXClient(BaseClient):
    def __init__(
        self, profile: Optional[str] = None, session: Optional[boto3.Session] = None
    ):
        super().__init__(profile, session)

    def get_regions(self) -> list[str]:
        # Fetch all enabled regions
        try:
            # Try using the session's configured region first
            region = self.session.region_name or "us-east-1"
            ec2 = self.session.client("ec2", region_name=region)
            resp = ec2.describe_regions(AllRegions=False)
            return [r["RegionName"] for r in resp["Regions"]]
        except Exception:
            if self.session.region_name:
                return [self.session.region_name]
            return []

    def _get_name(self, tags: list) -> Optional[str]:
        return next((t["value"] for t in tags if t["key"] == "Name"), None)

    def _scan_region(self, region: str) -> list[dict]:
        connections = []
        try:
            dx = self.session.client("directconnect", region_name=region)
            # Describe connections
            resp = dx.describe_connections()
            for conn in resp.get("connections", []):
                conn_id = conn["connectionId"]
                tags = conn.get("tags", [])
                name = conn[
                    "connectionName"
                ]  # DX connections have a name field, but tags are also used

                # Check for Name tag if connectionName is generic or we prefer tags
                name_tag = self._get_name(tags)
                display_name = name_tag if name_tag else name

                # Get VIFs for this connection
                # Note: describe_virtual_interfaces can filter by connectionId
                vifs = []
                try:
                    vif_resp = dx.describe_virtual_interfaces(connectionId=conn_id)
                    for vif in vif_resp.get("virtualInterfaces", []):
                        vifs.append(
                            {
                                "id": vif["virtualInterfaceId"],
                                "name": vif["virtualInterfaceName"],
                                "type": vif["virtualInterfaceType"],
                                "state": vif["virtualInterfaceState"],
                                "vlan": vif["vlan"],
                                "asn": vif.get("amazonSideAsn"),
                                "customer_asn": vif.get("asn"),
                                "region": region,
                            }
                        )
                except Exception:
                    pass

                connections.append(
                    {
                        "id": conn_id,
                        "name": display_name,
                        "region": region,
                        "state": conn["connectionState"],
                        "location": conn["location"],
                        "bandwidth": conn["bandwidth"],
                        "vifs": vifs,
                        "tags": {
                            t["key"]: t["value"] for t in tags if t["key"] != "Name"
                        },
                    }
                )
        except Exception:
            pass
        return connections

    def discover(self, regions: Optional[list[str]] = None) -> list[dict]:
        regions = regions or self.get_regions()
        all_connections = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(self._scan_region, r): r for r in regions}
            for future in concurrent.futures.as_completed(futures):
                all_connections.extend(future.result())
        return sorted(
            all_connections, key=lambda c: (c["region"], c["name"] or c["id"])
        )

    def get_connection_detail(self, connection_id: str, region: str) -> dict:
        dx = self.session.client("directconnect", region_name=region)

        # Get Connection
        conn_resp = dx.describe_connections(connectionId=connection_id)
        if not conn_resp["connections"]:
            return {}
        conn = conn_resp["connections"][0]

        # tags removed - DX tags are tricky, usually on the resource itself
        # Actually describe_connections returns tags in the response usually
        tags = conn.get("tags", [])
        name_tag = self._get_name(tags)
        display_name = name_tag if name_tag else conn["connectionName"]

        # Get VIFs with BGP details
        vifs = []
        vif_resp = dx.describe_virtual_interfaces(connectionId=connection_id)
        for vif in vif_resp.get("virtualInterfaces", []):
            vif_id = vif["virtualInterfaceId"]

            # Get BGP Peers
            bgp_peers = []
            for peer in vif.get("bgpPeers", []):
                bgp_peers.append(
                    {
                        "asn": peer.get("asn"),
                        "auth_key": peer.get("authKey"),
                        "address_family": peer.get("addressFamily"),
                        "amazon_address": peer.get("amazonAddress"),
                        "customer_address": peer.get("customerAddress"),
                        "state": peer.get("bgpPeerState"),
                        "status": peer.get("bgpStatus"),
                    }
                )

            vifs.append(
                {
                    "id": vif_id,
                    "name": vif["virtualInterfaceName"],
                    "type": vif["virtualInterfaceType"],
                    "state": vif["virtualInterfaceState"],
                    "vlan": vif["vlan"],
                    "asn": vif.get("amazonSideAsn"),
                    "customer_asn": vif.get("asn"),
                    "bgp_peers": bgp_peers,
                    "jumbo_frame_capable": vif.get("jumboFrameCapable"),
                    "mtu": vif.get("mtu"),
                }
            )

        return {
            "id": connection_id,
            "name": display_name,
            "region": region,
            "state": conn["connectionState"],
            "location": conn["location"],
            "bandwidth": conn["bandwidth"],
            "lag_id": conn.get("lagId"),
            "vifs": vifs,
            "tags": {t["key"]: t["value"] for t in tags if t["key"] != "Name"},
        }


class DXDisplay(BaseDisplay):
    def show_connections_list(self, connections: list[dict]):
        if not connections:
            self.console.print("[yellow]No Direct Connect connections found[/]")
            return
        table = Table(
            title="Direct Connect Connections", show_header=True, header_style="bold"
        )
        table.add_column("#", style="dim", justify="right")
        table.add_column("Region", style="cyan")
        table.add_column("Connection ID", style="green")
        table.add_column("Name", style="yellow")
        table.add_column("Location", style="white")
        table.add_column("Bandwidth", style="magenta")
        table.add_column("State", style="dim")
        table.add_column("# VIFs", style="blue", justify="right")

        for i, conn in enumerate(connections, 1):
            state_style = "green" if conn["state"] == "available" else "red"
            table.add_row(
                str(i),
                conn["region"],
                conn["id"],
                conn.get("name") or "-",
                conn["location"],
                conn["bandwidth"],
                Text(conn["state"], style=state_style),
                str(len(conn.get("vifs", []))),
            )
        self.console.print(table)
        self.console.print(f"\n[dim]Total: {len(connections)} Connection(s)[/]")

    def show_connection_detail(self, connection: dict):
        if not connection:
            self.console.print("[red]Connection not found[/]")
            return

        tree = Tree(
            f"[bold blue]🔌 Connection: {connection.get('name') or connection['id']}[/]"
        )
        tree.add(f"[dim]ID: {connection['id']}[/]")
        tree.add(f"[dim]Region: {connection['region']}[/]")
        tree.add(f"[white]Location: {connection['location']}[/]")
        tree.add(f"[magenta]Bandwidth: {connection['bandwidth']}[/]")

        state_style = "green" if connection["state"] == "available" else "red"
        tree.add(f"[bold]State: [{state_style}]{connection['state']}[/][/]")

        if connection.get("lag_id"):
            tree.add(f"[dim]LAG ID: {connection['lag_id']}[/]")

        if connection.get("tags"):
            tag_branch = tree.add("[dim]🏷️ Tags[/]")
            for k, v in connection["tags"].items():
                tag_branch.add(f"{k}: {v}")

        self.console.print(tree)
        self.console.print()

        # VIFs table
        if connection.get("vifs"):
            vif_table = Table(
                title="Virtual Interfaces", show_header=True, header_style="bold"
            )
            vif_table.add_column("ID", style="cyan")
            vif_table.add_column("Name", style="yellow")
            vif_table.add_column("Type", style="white")
            vif_table.add_column("VLAN", style="magenta", justify="right")
            vif_table.add_column("State", style="dim")
            vif_table.add_column("BGP Status", style="blue")

            for vif in connection["vifs"]:
                state_style = "green" if vif["state"] == "available" else "red"

                bgp_status = "N/A"
                if vif.get("bgp_peers"):
                    # Summarize BGP status
                    statuses = [p.get("state", "unknown") for p in vif["bgp_peers"]]
                    if all(s == "established" for s in statuses):
                        bgp_status = "[green]Established[/]"
                    elif any(s == "established" for s in statuses):
                        bgp_status = "[yellow]Partial[/]"
                    else:
                        bgp_status = f"[red]{statuses[0] if statuses else 'Down'}[/]"

                vif_table.add_row(
                    vif["id"],
                    vif["name"],
                    vif["type"],
                    str(vif["vlan"]),
                    Text(vif["state"], style=state_style),
                    bgp_status,
                )
            self.console.print(vif_table)
            self.console.print()

    def show_vif_detail(self, connection: dict, vif_ref: str):
        vif = resolve_item(connection.get("vifs", []), vif_ref, "name", "id")
        if not vif:
            self.console.print(f"[red]VIF '{vif_ref}' not found[/]")
            return

        self.console.print(
            Panel(f"[bold]{vif['name']}[/] ({vif['id']})", title="Virtual Interface")
        )

        grid = Table.grid(padding=(0, 2))
        grid.add_column(style="bold")
        grid.add_column()

        grid.add_row("Type:", vif["type"])
        grid.add_row(
            "State:",
            Text(vif["state"], style="green" if vif["state"] == "available" else "red"),
        )
        grid.add_row("VLAN:", str(vif["vlan"]))
        grid.add_row("Amazon ASN:", str(vif.get("asn", "N/A")))
        grid.add_row("Customer ASN:", str(vif.get("customer_asn", "N/A")))
        grid.add_row("MTU:", str(vif.get("mtu", "N/A")))
        grid.add_row("Jumbo Frames:", str(vif.get("jumbo_frame_capable", "N/A")))

        self.console.print(grid)
        self.console.print()

        if vif.get("bgp_peers"):
            bgp_table = Table(title="BGP Peers", show_header=True)
            bgp_table.add_column("ASN", style="cyan")
            bgp_table.add_column("Family", style="white")
            bgp_table.add_column("Amazon IP", style="green")
            bgp_table.add_column("Customer IP", style="yellow")
            bgp_table.add_column("State", style="bold")

            for peer in vif["bgp_peers"]:
                state_style = "green" if peer.get("state") == "established" else "red"
                bgp_table.add_row(
                    str(peer.get("asn")),
                    peer.get("address_family"),
                    peer.get("amazon_address"),
                    peer.get("customer_address"),
                    Text(peer.get("state", "unknown"), style=state_style),
                )
            self.console.print(bgp_table)


def resolve_item(
    items: list[dict], ref: str, name_key: str, id_key: str
) -> Optional[dict]:
    """Resolve item by index (1-based), name, or ID"""
    if ref.isdigit():
        idx = int(ref) - 1
        if 0 <= idx < len(items):
            return items[idx]
    for item in items:
        if item.get(id_key) == ref:
            return item
    for item in items:
        if item.get(name_key) and item[name_key].lower() == ref.lower():
            return item
    return None


def resolve_connection(connections: list[dict], ref: str) -> Optional[dict]:
    """Resolve Connection by index (1-based), name, or ID"""
    return resolve_item(connections, ref, "name", "id")
