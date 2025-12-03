"""Transit Gateway module"""

import concurrent.futures
import logging
from typing import Optional, Dict, List
import boto3
from rich.table import Table
from rich.tree import Tree
from rich.text import Text
from thefuzz import fuzz

from ..core import Cache, BaseDisplay, BaseClient, ModuleInterface, Context

logger = logging.getLogger("aws_network_tools.tgw")

cache = Cache("tgw")


class TGWModule(ModuleInterface):
    @property
    def name(self) -> str:
        return "transit-gateway"

    @property
    def commands(self) -> Dict[str, str]:
        return {"transit-gateway": "Enter TGW context: transit-gateway <#|name|id>"}

    @property
    def context_commands(self) -> Dict[str, List[str]]:
        return {
            "transit-gateway": ["route-table"],
        }

    @property
    def show_commands(self) -> Dict[str, List[str]]:
        return {
            None: ["transit-gateways"],
            "transit-gateway": ["detail", "route-tables"],
        }

    def execute(self, shell, command: str, args: str):
        """Enter TGW context"""
        if shell.ctx_type is not None:
            shell.console.print("[red]Use 'end' to return to top level first[/]")
            return

        ref = args.strip()
        if not ref:
            shell.console.print("[red]Usage: transit-gateway <#|name|id>[/]")
            return

        tgws = shell._get_tgws()
        target = resolve_tgw(tgws, ref)
        if not target:
            shell.console.print(f"[red]TGW '{ref}' not found[/]")
            return

        shell.context_stack = [
            Context("transit-gateway", ref, target.get("name") or target["id"], target)
        ]
        shell._update_prompt()


class TGWClient(BaseClient):
    def __init__(
        self, profile: Optional[str] = None, session: Optional[boto3.Session] = None
    ):
        super().__init__(profile, session)

    def get_regions(self) -> list[str]:
        try:
            region = self.session.region_name or "us-east-1"
            ec2 = self.session.client("ec2", region_name=region)
            return [
                r["RegionName"]
                for r in ec2.describe_regions(AllRegions=False)["Regions"]
            ]
        except Exception:
            if self.session.region_name:
                return [self.session.region_name]
            return []

    def _scan_region(self, region: str) -> list[dict]:
        tgws = []
        try:
            ec2 = self.client("ec2", region_name=region)
            resp = ec2.describe_transit_gateways()
            for tgw in resp.get("TransitGateways", []):
                if tgw["State"] != "available":
                    continue
                tgw_id = tgw["TransitGatewayId"]
                name = next(
                    (t["Value"] for t in tgw.get("Tags", []) if t["Key"] == "Name"),
                    None,
                )
                tgw_data = {
                    "id": tgw_id,
                    "name": name,
                    "region": region,
                    "route_tables": [],
                    "attachments": [],
                }

                att_resp = ec2.describe_transit_gateway_attachments(
                    Filters=[{"Name": "transit-gateway-id", "Values": [tgw_id]}]
                )
                for att in att_resp.get("TransitGatewayAttachments", []):
                    if att["State"] in ["available", "pending"]:
                        att_name = next(
                            (
                                t["Value"]
                                for t in att.get("Tags", [])
                                if t["Key"] == "Name"
                            ),
                            None,
                        )
                        tgw_data["attachments"].append(
                            {
                                "id": att["TransitGatewayAttachmentId"],
                                "name": att_name,
                                "type": att["ResourceType"],
                                "resource_id": att.get("ResourceId", "N/A"),
                                "state": att.get("State", ""),
                            }
                        )

                rt_resp = ec2.describe_transit_gateway_route_tables(
                    Filters=[{"Name": "transit-gateway-id", "Values": [tgw_id]}]
                )
                for rt in rt_resp.get("TransitGatewayRouteTables", []):
                    rt_id = rt["TransitGatewayRouteTableId"]
                    rt_name = next(
                        (t["Value"] for t in rt.get("Tags", []) if t["Key"] == "Name"),
                        None,
                    )
                    rt_data = {"id": rt_id, "name": rt_name, "routes": []}

                    routes_resp = ec2.search_transit_gateway_routes(
                        TransitGatewayRouteTableId=rt_id,
                        Filters=[{"Name": "state", "Values": ["active", "blackhole"]}],
                    )
                    for route in routes_resp.get("Routes", []):
                        cidr = route.get("DestinationCidrBlock", "N/A")
                        state = route.get("State", "unknown")
                        route_type = route.get("Type", "unknown")
                        target, target_type = "blackhole", "blackhole"
                        if state != "blackhole" and route.get(
                            "TransitGatewayAttachments"
                        ):
                            att = route["TransitGatewayAttachments"][0]
                            target = att["TransitGatewayAttachmentId"]
                            target_type = att.get("ResourceType", "unknown")
                        rt_data["routes"].append(
                            {
                                "prefix": cidr,
                                "target": target,
                                "target_type": target_type,
                                "state": state,
                                "type": route_type,
                            }
                        )
                    tgw_data["route_tables"].append(rt_data)
                tgws.append(tgw_data)
        except Exception as e:
            logger.warning("Failed to discover TGW in %s: %s", region, e)
        return tgws

    def discover(self, regions: Optional[list[str]] = None) -> list[dict]:
        regions = regions or self.get_regions()
        all_tgws = []
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=getattr(self, "max_workers", 10)
        ) as executor:
            futures = {executor.submit(self._scan_region, r): r for r in regions}
            for future in concurrent.futures.as_completed(futures):
                all_tgws.extend(future.result())
        return sorted(all_tgws, key=lambda t: (t["region"], t["name"] or t["id"]))


class TGWDisplay(BaseDisplay):
    def show_list(self, tgws: list[dict]):
        if not tgws:
            self.console.print("[yellow]No Transit Gateways found[/]")
            return
        table = Table(title="Transit Gateways", show_header=True, header_style="bold")
        table.add_column("#", style="dim", justify="right")
        table.add_column("Region", style="cyan")
        table.add_column("TGW ID", style="green")
        table.add_column("Name", style="yellow")
        table.add_column("Route Tables", style="white", justify="right")
        table.add_column("Attachments", style="white", justify="right")
        for i, tgw in enumerate(tgws, 1):
            table.add_row(
                str(i),
                tgw["region"],
                tgw["id"],
                tgw.get("name") or "-",
                str(len(tgw["route_tables"])),
                str(len(tgw["attachments"])),
            )
        self.console.print(table)
        self.console.print(f"\n[dim]Total: {len(tgws)} Transit Gateway(s)[/]")

    def show_discovery(self, tgws: list[dict]):
        self.show_list(tgws)

    def show_tgw_detail(self, tgw: dict):
        if not tgw:
            self.console.print("[red]TGW not found[/]")
            return
        tree = Tree(f"[bold blue]🚀 Transit Gateway: {tgw['name'] or tgw['id']}[/]")
        tree.add(f"[dim]ID: {tgw['id']}[/]")
        tree.add(f"[dim]Region: {tgw['region']}[/]")
        self.console.print(tree)
        self.console.print()

        if tgw["attachments"]:
            att_table = Table(
                title="Attachments", show_header=True, header_style="bold"
            )
            att_table.add_column("#", style="dim", justify="right")
            att_table.add_column("ID", style="cyan")
            att_table.add_column("Name", style="yellow")
            att_table.add_column("Type", style="green")
            att_table.add_column("Resource", style="white")
            for i, att in enumerate(tgw["attachments"], 1):
                att_table.add_row(
                    str(i),
                    att["id"],
                    att.get("name") or "-",
                    att["type"],
                    att["resource_id"],
                )
            self.console.print(att_table)
            self.console.print()

        if tgw["route_tables"]:
            rt_table = Table(
                title="Route Tables", show_header=True, header_style="bold"
            )
            rt_table.add_column("#", style="dim", justify="right")
            rt_table.add_column("ID", style="cyan")
            rt_table.add_column("Name", style="yellow")
            rt_table.add_column("Routes", style="white", justify="right")
            for i, rt in enumerate(tgw["route_tables"], 1):
                rt_table.add_row(
                    str(i), rt["id"], rt.get("name") or "-", str(len(rt["routes"]))
                )
            self.console.print(rt_table)

    def show_prefixes(self, tgws: list[dict]):
        for tgw in tgws:
            for rt in tgw.get("route_tables", []):
                if not rt["routes"]:
                    continue
                title = f"[bold]{tgw['name'] or tgw['id']}[/] → [cyan]{tgw['region']}[/] → [magenta]{rt['name'] or rt['id']}[/]"
                table = Table(title=title, show_header=True, header_style="bold")
                table.add_column("#", style="dim", justify="right")
                table.add_column("Prefix", style="green", no_wrap=True)
                table.add_column("Target", style="cyan")
                table.add_column("Type", style="yellow")
                table.add_column("State", style="white")
                table.add_column("Target Type", style="dim")
                for i, route in enumerate(rt["routes"], 1):
                    state_style = "green" if route["state"] == "active" else "red"
                    table.add_row(
                        str(i),
                        route["prefix"],
                        route["target"],
                        route["type"].upper(),
                        Text(route["state"], style=state_style),
                        route["target_type"],
                    )
                self.console.print(table)
                self.console.print()

    def show_route_tables_list(self, tgw: dict):
        """Show list of route tables for a TGW"""
        rts = tgw.get("route_tables", [])
        if not rts:
            self.console.print("[yellow]No route tables found[/]")
            return
        table = Table(
            title=f"Route Tables for [bold]{tgw['name'] or tgw['id']}[/]",
            show_header=True,
            header_style="bold",
        )
        table.add_column("#", style="dim", justify="right")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Routes", style="yellow", justify="right")
        for i, rt in enumerate(rts, 1):
            table.add_row(
                str(i),
                rt.get("id", ""),
                rt.get("name", ""),
                str(len(rt.get("routes", []))),
            )
        self.console.print(table)

    def show_route_table(self, tgw: dict, rt_ref: str):
        rt = resolve_item(tgw.get("route_tables", []), rt_ref, "name", "id")
        if not rt:
            self.console.print(f"[red]Route table '{rt_ref}' not found[/]")
            return
        title = f"[bold]{tgw['name'] or tgw['id']}[/] → [cyan]{rt.get('name') or rt['id']}[/]"
        table = Table(title=title, show_header=True, header_style="bold")
        table.add_column("#", style="dim", justify="right")
        table.add_column("Prefix", style="green", no_wrap=True)
        table.add_column("Target", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("State", style="white")
        for i, route in enumerate(rt["routes"], 1):
            state_style = "green" if route["state"] == "active" else "red"
            table.add_row(
                str(i),
                route["prefix"],
                route["target"],
                route["type"].upper(),
                Text(route["state"], style=state_style),
            )
        self.console.print(table)

    def show_matches(self, matches: list[dict], query: str):
        if not matches:
            self.console.print(f"[yellow]No matches found for '{query}'[/]")
            return
        table = Table(
            title=f"Search Results for '[cyan]{query}[/]'",
            show_header=True,
            header_style="bold",
        )
        table.add_column("#", style="dim", justify="right")
        table.add_column("Score", style="yellow", justify="right")
        table.add_column("Prefix", style="green", no_wrap=True)
        table.add_column("Route Table", style="blue")
        table.add_column("Target", style="cyan")
        table.add_column("State", style="dim")
        for i, m in enumerate(matches, 1):
            state_style = "green" if m["state"] == "active" else "red"
            table.add_row(
                str(i),
                str(m["score"]),
                m["prefix"],
                m["route_table"],
                m["target"],
                Text(m["state"], style=state_style),
            )
        self.console.print(table)
        self.console.print(f"[dim]Found {len(matches)} matches[/]")


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


def resolve_tgw(tgws: list[dict], ref: str) -> Optional[dict]:
    return resolve_item(tgws, ref, "name", "id")


def search_prefixes(
    tgws: list[dict], query: str, min_score: int = 60, max_results: int = 50
) -> list[dict]:
    matches = []
    for tgw in tgws:
        for rt in tgw.get("route_tables", []):
            for route in rt["routes"]:
                score = fuzz.partial_ratio(query.lower(), route["prefix"].lower())
                if query.lower() in route["prefix"].lower():
                    score = max(score, 90)
                if query.lower() == route["prefix"].lower():
                    score = 100
                if score >= min_score:
                    matches.append(
                        {
                            "prefix": route["prefix"],
                            "target": route["target"],
                            "state": route["state"],
                            "route_table": f"{tgw['name'] or tgw['id']} → {rt['name'] or rt['id']}",
                            "score": score,
                        }
                    )
    matches.sort(key=lambda m: (-m["score"], m["route_table"]))
    return matches[:max_results]
