"""Elastic Network Interface (ENI) module"""

from typing import Optional, Dict, List, Any
import boto3
from rich.table import Table
from rich.text import Text

from ..core import Cache, BaseDisplay, BaseClient, ModuleInterface, run_with_spinner

cache = Cache("eni")


class ENIModule(ModuleInterface):
    @property
    def name(self) -> str:
        return "interface"

    @property
    def commands(self) -> Dict[str, str]:
        return {
            "interfaces": "Show interface inventory: interfaces [brief]",
        }

    @property
    def show_commands(self) -> Dict[str, List[str]]:
        return {
            None: ["interfaces"],
        }

    def execute(self, shell: Any, command: str, args: str):
        if command == "interfaces":
            self._show_interfaces(shell, args)

    def _show_interfaces(self, shell, args):
        client = ENIClient(shell.profile)
        enis = run_with_spinner(
            lambda: client.discover(shell.regions),
            "Discovering Interfaces",
            console=shell.console,
        )
        ENIDisplay(shell.console).show_list(enis)


class ENIClient(BaseClient):
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
        enis = []
        try:
            ec2 = self.session.client("ec2", region_name=region)
            paginator = ec2.get_paginator("describe_network_interfaces")
            for page in paginator.paginate():
                for eni in page["NetworkInterfaces"]:
                    # Determine what it's attached to
                    attachment = eni.get("Attachment", {})
                    attached_to = "Available"
                    if eni["Status"] == "in-use":
                        if attachment.get("InstanceId"):
                            attached_to = f"Instance: {attachment['InstanceId']}"
                        elif eni.get("Description", "").startswith("ELB"):
                            attached_to = "Load Balancer"
                        elif "NAT Gateway" in eni.get("Description", ""):
                            attached_to = "NAT Gateway"
                        elif eni.get("InterfaceType") == "transit_gateway":
                            attached_to = "Transit Gateway"
                        elif eni.get("InterfaceType") == "vpc_endpoint":
                            attached_to = "VPC Endpoint"
                        else:
                            attached_to = eni.get("Description", "Unknown")[:30]

                    name = next(
                        (
                            t["Value"]
                            for t in eni.get("TagSet", [])
                            if t["Key"] == "Name"
                        ),
                        None,
                    )

                    enis.append(
                        {
                            "id": eni["NetworkInterfaceId"],
                            "name": name,
                            "region": region,
                            "status": eni["Status"],
                            "type": eni["InterfaceType"],
                            "private_ip": eni.get("PrivateIpAddress"),
                            "public_ip": eni.get("Association", {}).get("PublicIp"),
                            "mac": eni.get("MacAddress"),
                            "subnet_id": eni["SubnetId"],
                            "vpc_id": eni["VpcId"],
                            "attached_to": attached_to,
                            "security_groups": [
                                sg["GroupId"] for sg in eni.get("Groups", [])
                            ],
                        }
                    )
        except Exception:
            pass
        return enis

    def discover(self, regions: Optional[list[str]] = None) -> list[dict]:
        if not regions:
            regions = self.get_regions()

        import concurrent.futures

        all_enis = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(self._scan_region, r): r for r in regions}
            for future in concurrent.futures.as_completed(futures):
                all_enis.extend(future.result())
        return sorted(all_enis, key=lambda x: (x["region"], x["attached_to"]))


class ENIDisplay(BaseDisplay):
    def show_list(self, enis: list[dict]):
        if not enis:
            self.console.print("[yellow]No interfaces found[/]")
            return

        table = Table(
            title="Interface Inventory", show_header=True, header_style="bold"
        )
        table.add_column("#", style="dim", justify="right")
        table.add_column("Region", style="cyan")
        table.add_column("Interface ID", style="green")
        table.add_column("Name", style="blue")
        table.add_column("Status", style="white")
        table.add_column("Type", style="dim")
        table.add_column("Private IP", style="yellow")
        table.add_column("Public IP", style="red")
        table.add_column("Attached To", style="magenta")

        for i, eni in enumerate(enis, 1):
            status_style = "green" if eni["status"] == "in-use" else "yellow"
            table.add_row(
                str(i),
                eni["region"],
                eni["id"],
                eni["name"] or "-",
                Text(eni["status"], style=status_style),
                eni["type"],
                eni["private_ip"] or "-",
                eni["public_ip"] or "-",
                eni["attached_to"],
            )
        self.console.print(table)
        self.console.print(f"\n[dim]Total: {len(enis)} Interface(s)[/]")
