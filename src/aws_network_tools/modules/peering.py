"""VPC Peering module"""

import concurrent.futures
from typing import Optional, List
import boto3
from rich.table import Table
from rich.text import Text

from ..core import Cache, BaseDisplay, BaseClient

cache = Cache("peering")


class PeeringClient(BaseClient):
    def __init__(
        self, profile: Optional[str] = None, session: Optional[boto3.Session] = None
    ):
        super().__init__(profile, session)

    def get_regions(self) -> list[str]:
        try:
            region = self.session.region_name or "us-east-1"
            ec2 = self.session.client("ec2", region_name=region)
            resp = ec2.describe_regions(AllRegions=False)
            return [r["RegionName"] for r in resp["Regions"]]
        except Exception:
            return [self.session.region_name] if self.session.region_name else []

    def _get_name(self, tags: list) -> Optional[str]:
        return next((t["Value"] for t in tags if t["Key"] == "Name"), None)

    def _scan_region(self, region: str) -> List[dict]:
        peerings = []
        try:
            ec2 = self.session.client("ec2", region_name=region)
            paginator = ec2.get_paginator("describe_vpc_peering_connections")

            for page in paginator.paginate():
                for pcx in page.get("VpcPeeringConnections", []):
                    status = pcx.get("Status", {})
                    requester = pcx.get("RequesterVpcInfo", {})
                    accepter = pcx.get("AccepterVpcInfo", {})

                    peerings.append(
                        {
                            "id": pcx["VpcPeeringConnectionId"],
                            "name": self._get_name(pcx.get("Tags", [])),
                            "region": region,
                            "status": status.get("Code", "unknown"),
                            "status_message": status.get("Message", ""),
                            "requester_vpc": requester.get("VpcId", ""),
                            "requester_cidr": requester.get("CidrBlock", ""),
                            "requester_owner": requester.get("OwnerId", ""),
                            "requester_region": requester.get("Region", ""),
                            "accepter_vpc": accepter.get("VpcId", ""),
                            "accepter_cidr": accepter.get("CidrBlock", ""),
                            "accepter_owner": accepter.get("OwnerId", ""),
                            "accepter_region": accepter.get("Region", ""),
                        }
                    )
        except Exception:
            pass
        return peerings

    def discover(self, regions: Optional[list[str]] = None) -> List[dict]:
        regions = regions or self.get_regions()
        all_peerings = []
        seen_ids = set()

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(self._scan_region, r): r for r in regions}
            for future in concurrent.futures.as_completed(futures):
                for pcx in future.result():
                    # Avoid duplicates (peering shows in both regions)
                    if pcx["id"] not in seen_ids:
                        seen_ids.add(pcx["id"])
                        all_peerings.append(pcx)

        return sorted(
            all_peerings,
            key=lambda x: (
                x["status"] != "active",
                x["region"],
                x.get("name") or x["id"],
            ),
        )


class PeeringDisplay(BaseDisplay):
    def show_list(self, peerings: List[dict]):
        if not peerings:
            self.console.print("[yellow]No VPC Peering connections found[/]")
            return

        table = Table(
            title="VPC Peering Connections", show_header=True, header_style="bold"
        )
        table.add_column("#", style="dim", justify="right")
        table.add_column("Name", style="green")
        table.add_column("ID", style="cyan")
        table.add_column("Requester VPC", style="yellow")
        table.add_column("Requester CIDR", style="white")
        table.add_column("Accepter VPC", style="yellow")
        table.add_column("Accepter CIDR", style="white")
        table.add_column("Status")

        for i, pcx in enumerate(peerings, 1):
            status = pcx["status"]
            if status == "active":
                status_style = "green"
            elif status in ["pending-acceptance", "provisioning"]:
                status_style = "yellow"
            else:
                status_style = "red"

            table.add_row(
                str(i),
                pcx.get("name") or "-",
                pcx["id"],
                pcx["requester_vpc"],
                pcx["requester_cidr"],
                pcx["accepter_vpc"],
                pcx["accepter_cidr"],
                Text(status, style=status_style),
            )

        self.console.print(table)

        # Summary
        active = sum(1 for p in peerings if p["status"] == "active")
        pending = sum(1 for p in peerings if p["status"] == "pending-acceptance")
        self.console.print(
            f"\n[dim]Total: {len(peerings)} | Active: [green]{active}[/] | Pending: [yellow]{pending}[/][/]"
        )

    def show_detail(self, pcx: dict):
        if not pcx:
            self.console.print("[red]Peering connection not found[/]")
            return

        from rich.panel import Panel
        from rich.columns import Columns

        status = pcx["status"]
        status_style = (
            "green"
            if status == "active"
            else "yellow"
            if status == "pending-acceptance"
            else "red"
        )

        self.console.print(
            Panel(
                f"[bold]{pcx.get('name') or pcx['id']}[/]\n"
                f"Status: [{status_style}]{status}[/]\n"
                f"{pcx.get('status_message', '')}",
                title="VPC Peering Connection",
            )
        )

        req_table = Table(title="Requester", show_header=False)
        req_table.add_column("Property", style="cyan")
        req_table.add_column("Value")
        req_table.add_row("VPC", pcx["requester_vpc"])
        req_table.add_row("CIDR", pcx["requester_cidr"])
        req_table.add_row("Owner", pcx["requester_owner"])
        req_table.add_row("Region", pcx["requester_region"])

        acc_table = Table(title="Accepter", show_header=False)
        acc_table.add_column("Property", style="cyan")
        acc_table.add_column("Value")
        acc_table.add_row("VPC", pcx["accepter_vpc"])
        acc_table.add_row("CIDR", pcx["accepter_cidr"])
        acc_table.add_row("Owner", pcx["accepter_owner"])
        acc_table.add_row("Region", pcx["accepter_region"])

        self.console.print(Columns([req_table, acc_table]))
