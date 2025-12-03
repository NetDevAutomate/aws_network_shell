"""Managed Prefix Lists module"""

import concurrent.futures
from typing import Optional, List
import boto3
from rich.table import Table
from rich.text import Text

from ..core import Cache, BaseDisplay, BaseClient

cache = Cache("prefix-lists")


class PrefixListClient(BaseClient):
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

    def _scan_region(self, region: str) -> List[dict]:
        prefix_lists = []
        try:
            ec2 = self.session.client("ec2", region_name=region)
            paginator = ec2.get_paginator("describe_managed_prefix_lists")

            for page in paginator.paginate():
                for pl in page.get("PrefixLists", []):
                    pl_id = pl["PrefixListId"]

                    # Get entries for this prefix list
                    entries = []
                    try:
                        entry_paginator = ec2.get_paginator(
                            "get_managed_prefix_list_entries"
                        )
                        for entry_page in entry_paginator.paginate(PrefixListId=pl_id):
                            for entry in entry_page.get("Entries", []):
                                entries.append(
                                    {
                                        "cidr": entry.get("Cidr", ""),
                                        "description": entry.get("Description", ""),
                                    }
                                )
                    except Exception:
                        pass

                    prefix_lists.append(
                        {
                            "id": pl_id,
                            "name": pl.get("PrefixListName", pl_id),
                            "region": region,
                            "state": pl.get("State", ""),
                            "version": pl.get("Version", 0),
                            "max_entries": pl.get("MaxEntries", 0),
                            "current_entries": len(entries),
                            "owner_id": pl.get("OwnerId", ""),
                            "address_family": pl.get("AddressFamily", ""),
                            "entries": entries,
                            "is_aws_managed": pl.get("OwnerId", "") == "AWS",
                        }
                    )
        except Exception:
            pass
        return prefix_lists

    def discover(
        self, regions: Optional[list[str]] = None, include_aws_managed: bool = False
    ) -> List[dict]:
        regions = regions or self.get_regions()
        all_lists = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(self._scan_region, r): r for r in regions}
            for future in concurrent.futures.as_completed(futures):
                for pl in future.result():
                    if include_aws_managed or not pl["is_aws_managed"]:
                        all_lists.append(pl)

        return sorted(all_lists, key=lambda x: (x["region"], x.get("name") or x["id"]))


class PrefixListDisplay(BaseDisplay):
    def show_list(self, prefix_lists: List[dict]):
        if not prefix_lists:
            self.console.print("[yellow]No managed prefix lists found[/]")
            return

        table = Table(
            title="Managed Prefix Lists", show_header=True, header_style="bold"
        )
        table.add_column("#", style="dim", justify="right")
        table.add_column("Region", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("ID", style="white")
        table.add_column("Family", style="yellow")
        table.add_column("Entries", style="magenta", justify="right")
        table.add_column("Max", style="dim", justify="right")
        table.add_column("Version", style="dim", justify="right")
        table.add_column("State")

        for i, pl in enumerate(prefix_lists, 1):
            state = pl["state"]
            state_style = (
                "green"
                if state == "create-complete"
                else "yellow"
                if "pending" in state
                else "red"
            )

            # Show utilization
            usage = f"{pl['current_entries']}"
            if pl["current_entries"] >= pl["max_entries"] * 0.9:
                usage = f"[red]{usage}[/]"
            elif pl["current_entries"] >= pl["max_entries"] * 0.7:
                usage = f"[yellow]{usage}[/]"

            table.add_row(
                str(i),
                pl["region"],
                pl["name"][:30],
                pl["id"],
                pl["address_family"],
                usage,
                str(pl["max_entries"]),
                str(pl["version"]),
                Text(state.replace("create-", ""), style=state_style),
            )

        self.console.print(table)
        self.console.print(f"\n[dim]Total: {len(prefix_lists)} prefix list(s)[/]")

    def show_entries(self, pl: dict):
        if not pl:
            self.console.print("[red]Prefix list not found[/]")
            return

        entries = pl.get("entries", [])

        self.console.print(f"\n[bold]{pl['name']}[/] ({pl['id']})")
        self.console.print(
            f"[dim]Region: {pl['region']} | Family: {pl['address_family']} | Version: {pl['version']}[/]\n"
        )

        if not entries:
            self.console.print("[yellow]No entries in this prefix list[/]")
            return

        table = Table(
            title=f"Entries ({len(entries)}/{pl['max_entries']})",
            show_header=True,
            header_style="bold",
        )
        table.add_column("#", style="dim", justify="right")
        table.add_column("CIDR", style="green")
        table.add_column("Description", style="dim")

        for i, entry in enumerate(entries, 1):
            table.add_row(
                str(i),
                entry["cidr"],
                entry.get("description", "")[:50],
            )

        self.console.print(table)
