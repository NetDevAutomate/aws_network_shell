"""VPC module"""

import concurrent.futures
import logging
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

logger = logging.getLogger("aws_network_tools.vpc")

cache = Cache("vpc")


class VPCModule(ModuleInterface):
    @property
    def name(self) -> str:
        return "vpc"

    @property
    def commands(self) -> Dict[str, str]:
        return {"vpc": "Enter VPC context: vpc <#|name|id>"}

    @property
    def context_commands(self) -> Dict[str, List[str]]:
        return {
            "vpc": ["security-group", "nacl", "route-table"],
        }

    @property
    def show_commands(self) -> Dict[str, List[str]]:
        return {
            None: ["vpcs"],
            "vpc": ["detail", "route-tables", "security-groups", "nacls"],
        }

    def execute(self, shell, command: str, args: str):
        """Enter VPC context"""
        if shell.ctx_type is not None:
            shell.console.print("[red]Use 'end' to return to top level first[/]")
            return

        ref = args.strip()
        if not ref:
            shell.console.print("[red]Usage: vpc <#|name|id>[/]")
            return

        # We need access to shell._get_vpcs which uses cache
        # For now, we'll access shell._get_vpcs directly if available, or fetch
        # This part reveals the tight coupling we are trying to solve.
        # Ideally shell exposes a 'get_data("vpcs")' method.
        # For this refactor, let's assume shell has _get_vpcs or we fetch directly.

        # To avoid circular dependency or breaking shell, let's duplicate the fetch logic safely
        # or call shell._get_vpcs if it exists (duck typing).

        vpcs = shell._get_vpcs()
        target = resolve_vpc(vpcs, ref)

        if not target:
            shell.console.print(f"[red]VPC '{ref}' not found[/]")
            return

        client = VPCClient(shell.profile, shell.session)
        detail = run_with_spinner(
            lambda: client.get_vpc_detail(target["id"], target["region"]),
            "Fetching VPC",
            console=shell.console,
        )

        shell.context_stack = [
            Context("vpc", ref, target.get("name") or target["id"], detail)
        ]
        shell._update_prompt()


class VPCClient(BaseClient):
    def __init__(
        self, profile: Optional[str] = None, session: Optional[boto3.Session] = None
    ):
        super().__init__(profile, session)

    def get_regions(self) -> list[str]:
        # Fetch all enabled regions
        try:
            # Try using the session's configured region first
            region = self.session.region_name or "us-east-1"
            ec2 = self.client("ec2", region_name=region)
            resp = ec2.describe_regions(AllRegions=False)
            return [r["RegionName"] for r in resp["Regions"]]
        except Exception as e:
            logger.warning(
                "describe_regions failed (region=%s): %s", self.session.region_name, e
            )
            # If we can't list regions, we can't discover globally.
            # Return current session region as the only known region if available.
            if self.session.region_name:
                return [self.session.region_name]
            return []

    def _get_name(self, tags: list) -> Optional[str]:
        return next((t["Value"] for t in tags if t["Key"] == "Name"), None)

    def _scan_region(self, region: str) -> list[dict]:
        vpcs = []
        try:
            ec2 = self.client("ec2", region_name=region)
            resp = ec2.describe_vpcs()
            for vpc in resp.get("Vpcs", []):
                vpc_id = vpc["VpcId"]
                tags = vpc.get("Tags", [])
                name = self._get_name(tags)
                cidrs = [vpc["CidrBlock"]]
                for assoc in vpc.get("CidrBlockAssociationSet", []):
                    if (
                        assoc["CidrBlockState"]["State"] == "associated"
                        and assoc["CidrBlock"] != vpc["CidrBlock"]
                    ):
                        cidrs.append(assoc["CidrBlock"])
                vpcs.append(
                    {
                        "id": vpc_id,
                        "name": name,
                        "region": region,
                        "cidrs": cidrs,
                        "tags": {
                            t["Key"]: t["Value"] for t in tags if t["Key"] != "Name"
                        },
                        "is_default": vpc.get("IsDefault", False),
                    }
                )
        except Exception as e:
            logger.warning("describe_vpcs failed (region=%s): %s", region, e)
        return vpcs

    def discover(self, regions: Optional[list[str]] = None) -> list[dict]:
        regions = regions or self.get_regions()
        all_vpcs = []
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=getattr(self, "max_workers", 10)
        ) as executor:
            futures = {executor.submit(self._scan_region, r): r for r in regions}
            for future in concurrent.futures.as_completed(futures):
                all_vpcs.extend(future.result())
        return sorted(all_vpcs, key=lambda v: (v["region"], v["name"] or v["id"]))

    def get_vpc_detail(self, vpc_id: str, region: str) -> dict:
        ec2 = self.client("ec2", region_name=region)
        vpc_resp = ec2.describe_vpcs(VpcIds=[vpc_id])
        if not vpc_resp["Vpcs"]:
            return {}
        vpc = vpc_resp["Vpcs"][0]
        tags = vpc.get("Tags", [])
        name = self._get_name(tags)

        cidrs = [vpc["CidrBlock"]]
        for assoc in vpc.get("CidrBlockAssociationSet", []):
            if (
                assoc["CidrBlockState"]["State"] == "associated"
                and assoc["CidrBlock"] != vpc["CidrBlock"]
            ):
                cidrs.append(assoc["CidrBlock"])

        subnets_resp = ec2.describe_subnets(
            Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
        )
        subnets, azs = [], set()
        for s in subnets_resp.get("Subnets", []):
            azs.add(s["AvailabilityZone"])
            subnets.append(
                {
                    "id": s["SubnetId"],
                    "name": self._get_name(s.get("Tags", [])),
                    "az": s["AvailabilityZone"],
                    "cidr": s["CidrBlock"],
                }
            )

        igw_resp = ec2.describe_internet_gateways(
            Filters=[{"Name": "attachment.vpc-id", "Values": [vpc_id]}]
        )
        igws = [
            {"id": i["InternetGatewayId"], "name": self._get_name(i.get("Tags", []))}
            for i in igw_resp.get("InternetGateways", [])
        ]

        nat_resp = ec2.describe_nat_gateways(
            Filters=[
                {"Name": "vpc-id", "Values": [vpc_id]},
                {"Name": "state", "Values": ["available"]},
            ]
        )
        nats = [
            {
                "id": n["NatGatewayId"],
                "subnet": n["SubnetId"],
                "type": n.get("ConnectivityType", "public"),
            }
            for n in nat_resp.get("NatGateways", [])
        ]

        rt_resp = ec2.describe_route_tables(
            Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
        )
        route_tables = []
        for rt in rt_resp.get("RouteTables", []):
            rt_name = self._get_name(rt.get("Tags", []))
            assocs = [
                a.get("SubnetId")
                for a in rt.get("Associations", [])
                if a.get("SubnetId")
            ]
            is_main = any(a.get("Main", False) for a in rt.get("Associations", []))
            routes = []
            for r in rt.get("Routes", []):
                dest = (
                    r.get("DestinationCidrBlock")
                    or r.get("DestinationIpv6CidrBlock")
                    or r.get("DestinationPrefixListId")
                    or "N/A"
                )
                target = (
                    r.get("GatewayId")
                    or r.get("NatGatewayId")
                    or r.get("TransitGatewayId")
                    or r.get("VpcPeeringConnectionId")
                    or r.get("NetworkInterfaceId")
                    or r.get("CoreNetworkArn", "").split("/")[-1]
                    or "local"
                )
                routes.append(
                    {
                        "destination": dest,
                        "target": target,
                        "state": r.get("State", "active"),
                    }
                )
            route_tables.append(
                {
                    "id": rt["RouteTableId"],
                    "name": rt_name,
                    "is_main": is_main,
                    "subnets": assocs,
                    "routes": routes,
                }
            )

        sg_resp = ec2.describe_security_groups(
            Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
        )
        sgs = []
        for sg in sg_resp.get("SecurityGroups", []):
            ingress, egress = [], []
            for r in sg.get("IpPermissions", []):
                proto = r.get("IpProtocol", "all")
                ports = (
                    f"{r.get('FromPort', 'all')}-{r.get('ToPort', 'all')}"
                    if r.get("FromPort")
                    else "all"
                )
                for ip in r.get("IpRanges", []):
                    ingress.append(
                        {
                            "protocol": proto,
                            "ports": ports,
                            "source": ip.get("CidrIp", "N/A"),
                        }
                    )
                for grp in r.get("UserIdGroupPairs", []):
                    ingress.append(
                        {
                            "protocol": proto,
                            "ports": ports,
                            "source": grp.get("GroupId", "N/A"),
                        }
                    )
                if not r.get("IpRanges") and not r.get("UserIdGroupPairs"):
                    ingress.append({"protocol": proto, "ports": ports, "source": "N/A"})
                for r in sg.get("IpPermissionsEgress", []):
                    proto = r.get("IpProtocol", "all")
                    ports = (
                        f"{r.get('FromPort', 'all')}-{r.get('ToPort', 'all')}"
                        if r.get("FromPort")
                        else "all"
                    )
                    for ip in r.get("IpRanges", []):
                        egress.append(
                            {
                                "protocol": proto,
                                "ports": ports,
                                "dest": ip.get("CidrIp")
                                or (".".join(map(str, (0, 0, 0, 0))) + "/0"),
                            }
                        )
                    # IPv6 ranges
                    for ip6 in r.get("Ipv6Ranges", []):
                        egress.append(
                            {
                                "protocol": proto,
                                "ports": ports,
                                "dest": ip6.get("CidrIpv6") or ("::" + "/0"),
                            }
                        )
                    if not r.get("IpRanges") and not r.get("Ipv6Ranges"):
                        egress.append(
                            {
                                "protocol": proto,
                                "ports": ports,
                                "dest": (".".join(map(str, (0, 0, 0, 0))) + "/0")
                                + ", "
                                + ("::" + "/0"),
                            }
                        )
            sgs.append(
                {
                    "id": sg["GroupId"],
                    "name": sg["GroupName"],
                    "ingress": ingress,
                    "egress": egress,
                }
            )

        nacl_resp = ec2.describe_network_acls(
            Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
        )
        nacls = []
        for nacl in nacl_resp.get("NetworkAcls", []):
            entries = [
                {
                    "rule": e["RuleNumber"],
                    "protocol": e.get("Protocol", "all"),
                    "action": e["RuleAction"],
                    "cidr": e.get("CidrBlock", "N/A"),
                    "egress": e["Egress"],
                }
                for e in nacl.get("Entries", [])
                if e["RuleNumber"] != 32767
            ]
            nacls.append(
                {
                    "id": nacl["NetworkAclId"],
                    "name": self._get_name(nacl.get("Tags", [])),
                    "is_default": nacl.get("IsDefault", False),
                    "entries": entries,
                }
            )

        attachments = []
        try:
            tgw_att_resp = ec2.describe_transit_gateway_vpc_attachments(
                Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
            )
            for att in tgw_att_resp.get("TransitGatewayVpcAttachments", []):
                if att["State"] in ["available", "pending"]:
                    attachments.append(
                        {
                            "type": "transit-gateway",
                            "id": att["TransitGatewayAttachmentId"],
                            "resource": att["TransitGatewayId"],
                        }
                    )
        except Exception as e:
            logger.warning(
                "describe_transit_gateway_vpc_attachments failed (region=%s): %s",
                region,
                e,
            )

        endpoints = []
        try:
            vpce_resp = ec2.describe_vpc_endpoints(
                Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
            )
            for vpce in vpce_resp.get("VpcEndpoints", []):
                endpoints.append(
                    {
                        "id": vpce["VpcEndpointId"],
                        "type": vpce["VpcEndpointType"],
                        "service": vpce["ServiceName"],
                        "state": vpce["State"],
                    }
                )
        except Exception as e:
            logger.warning("describe_vpc_endpoints failed (region=%s): %s", region, e)

        encrypted = any(t.get("Key") == "encrypted-vpc" for t in tags)
        no_ingress = any(t.get("Key") == "no-ingress" for t in tags)

        return {
            "id": vpc_id,
            "name": name,
            "region": region,
            "cidrs": cidrs,
            "azs": sorted(azs),
            "subnets": subnets,
            "igws": igws,
            "nats": nats,
            "route_tables": route_tables,
            "security_groups": sgs,
            "nacls": nacls,
            "attachments": attachments,
            "endpoints": endpoints,
            "encrypted": encrypted,
            "no_ingress": no_ingress,
            "tags": {t["Key"]: t["Value"] for t in tags if t["Key"] != "Name"},
        }


class VPCDisplay(BaseDisplay):
    def show_list(self, vpcs: list[dict]):
        if not vpcs:
            self.console.print("[yellow]No VPCs found[/]")
            return
        table = Table(title="VPCs", show_header=True, header_style="bold")
        table.add_column("#", style="dim", justify="right")
        table.add_column("Region", style="cyan")
        table.add_column("VPC ID", style="green")
        table.add_column("Name", style="yellow")
        table.add_column("CIDRs", style="white")
        table.add_column("Default", style="dim")
        for i, vpc in enumerate(vpcs, 1):
            table.add_row(
                str(i),
                vpc["region"],
                vpc["id"],
                vpc.get("name") or "-",
                ", ".join(vpc["cidrs"]),
                "Yes" if vpc.get("is_default") else "",
            )
        self.console.print(table)
        self.console.print(f"\n[dim]Total: {len(vpcs)} VPC(s)[/]")

    def show_detail(self, vpc: dict):
        if not vpc:
            self.console.print("[red]VPC not found[/]")
            return

        tree = Tree(f"[bold blue]🌐 VPC: {vpc.get('name') or vpc['id']}[/]")
        tree.add(f"[dim]ID: {vpc['id']}[/]")
        tree.add(f"[dim]Region: {vpc['region']}[/]")
        tree.add(f"[cyan]CIDRs: {', '.join(vpc['cidrs'])}[/]")
        tree.add(f"[dim]AZs: {', '.join(vpc.get('azs', []))}[/]")
        if vpc.get("encrypted"):
            tree.add("[green]🔒 Encrypted VPC[/]")
        if vpc.get("no_ingress"):
            tree.add("[yellow]🚫 No Ingress[/]")
        if vpc.get("igws"):
            igw_branch = tree.add("[yellow]🌍 Internet Gateways[/]")
            for igw in vpc["igws"]:
                igw_branch.add(f"{igw.get('name') or igw['id']}")
        if vpc.get("nats"):
            nat_branch = tree.add("[magenta]🔄 NAT Gateways[/]")
            for nat in vpc["nats"]:
                nat_branch.add(f"{nat['id']} ({nat['type']}) in {nat['subnet']}")
        if vpc.get("attachments"):
            att_branch = tree.add("[cyan]📎 Attachments[/]")
            for att in vpc["attachments"]:
                att_branch.add(f"{att['type']}: {att['resource']} ({att['id']})")
        if vpc.get("endpoints"):
            vpce_branch = tree.add("[blue]🔌 VPC Endpoints[/]")
            for vpce in vpc["endpoints"]:
                vpce_type = "Interface" if vpce["type"] == "Interface" else "Gateway"
                vpce_branch.add(
                    f"[blue]{vpce['id']}[/] ([cyan]{vpce_type}[/]) - {vpce['service']}"
                )
        if vpc.get("tags"):
            tag_branch = tree.add("[dim]🏷️ Tags[/]")
            for k, v in vpc["tags"].items():
                tag_branch.add(f"{k}: {v}")
        self.console.print(tree)
        self.console.print()

        # Route tables with index
        if vpc.get("route_tables"):
            rt_table = Table(
                title="Route Tables", show_header=True, header_style="bold"
            )
            rt_table.add_column("#", style="dim", justify="right")
            rt_table.add_column("Name/ID", style="cyan")
            rt_table.add_column("Main", style="yellow")
            rt_table.add_column("Subnets", style="white")
            rt_table.add_column("Routes", style="dim", justify="right")
            for i, rt in enumerate(vpc["route_tables"], 1):
                rt_table.add_row(
                    str(i),
                    rt.get("name") or rt["id"],
                    "Yes" if rt["is_main"] else "",
                    ", ".join(rt.get("subnets", [])) or "-",
                    str(len(rt["routes"])),
                )
            self.console.print(rt_table)
            self.console.print()

        # Security groups with index
        if vpc.get("security_groups"):
            sg_table = Table(
                title="Security Groups", show_header=True, header_style="bold"
            )
            sg_table.add_column("#", style="dim", justify="right")
            sg_table.add_column("ID", style="cyan")
            sg_table.add_column("Name", style="yellow")
            sg_table.add_column("Ingress", style="green", justify="right")
            sg_table.add_column("Egress", style="red", justify="right")
            for i, sg in enumerate(vpc["security_groups"], 1):
                sg_table.add_row(
                    str(i),
                    sg["id"],
                    sg["name"],
                    str(len(sg["ingress"])),
                    str(len(sg["egress"])),
                )
            self.console.print(sg_table)
            self.console.print()

        # NACLs with index
        if vpc.get("nacls"):
            nacl_table = Table(
                title="Network ACLs", show_header=True, header_style="bold"
            )
            nacl_table.add_column("#", style="dim", justify="right")
            nacl_table.add_column("ID", style="cyan")
            nacl_table.add_column("Name", style="yellow")
            nacl_table.add_column("Default", style="dim")
            nacl_table.add_column("Rules", style="white", justify="right")
            for i, nacl in enumerate(vpc["nacls"], 1):
                nacl_table.add_row(
                    str(i),
                    nacl["id"],
                    nacl.get("name") or "-",
                    "Yes" if nacl["is_default"] else "",
                    str(len(nacl["entries"])),
                )
            self.console.print(nacl_table)

    def show_route_tables_list(self, vpc: dict):
        """Show list of route tables for a VPC"""
        rts = vpc.get("route_tables", [])
        if not rts:
            self.console.print("[yellow]No route tables found[/]")
            return
        table = Table(
            title=f"Route Tables for [bold]{vpc.get('name') or vpc['id']}[/]",
            show_header=True,
            header_style="bold",
        )
        table.add_column("#", style="dim", justify="right")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Main", style="yellow")
        table.add_column("Subnets", style="dim")
        table.add_column("Routes", style="white", justify="right")
        for i, rt in enumerate(rts, 1):
            table.add_row(
                str(i),
                rt.get("id", ""),
                rt.get("name") or "-",
                "Yes" if rt.get("is_main") else "",
                str(len(rt.get("subnets", []))),
                str(len(rt.get("routes", []))),
            )
        self.console.print(table)

    def show_route_table(self, vpc: dict, rt_ref: str):
        rt = resolve_item(vpc.get("route_tables", []), rt_ref, "name", "id")
        if not rt:
            self.console.print(f"[red]Route table '{rt_ref}' not found[/]")
            return
        title = f"[bold]{vpc.get('name') or vpc['id']}[/] → [cyan]{rt.get('name') or rt['id']}[/]"
        table = Table(title=title, show_header=True, header_style="bold")
        table.add_column("Destination", style="green", no_wrap=True)
        table.add_column("Target", style="cyan")
        table.add_column("State", style="white")
        for route in rt["routes"]:
            state_style = "green" if route["state"] == "active" else "red"
            table.add_row(
                route["destination"],
                route["target"],
                Text(route["state"], style=state_style),
            )
        self.console.print(table)
        if rt.get("subnets"):
            self.console.print(
                f"[dim]Associated subnets: {', '.join(rt['subnets'])}[/]"
            )

    def show_security_group(self, vpc: dict, sg_ref: str):
        sg = resolve_item(vpc.get("security_groups", []), sg_ref, "name", "id")
        if not sg:
            self.console.print(f"[red]Security group '{sg_ref}' not found[/]")
            return
        self.console.print(
            Panel(f"[bold]{sg['name']}[/] ({sg['id']})", title="Security Group")
        )
        if sg["ingress"]:
            in_table = Table(
                title="Ingress Rules", show_header=True, header_style="bold"
            )
            in_table.add_column("#", style="dim", justify="right")
            in_table.add_column("Protocol", style="yellow")
            in_table.add_column("Ports", style="cyan")
            in_table.add_column("Source", style="green")
            for i, r in enumerate(sg["ingress"], 1):
                in_table.add_row(str(i), r["protocol"], r["ports"], r["source"])
            self.console.print(in_table)
        if sg["egress"]:
            out_table = Table(
                title="Egress Rules", show_header=True, header_style="bold"
            )
            out_table.add_column("#", style="dim", justify="right")
            out_table.add_column("Protocol", style="yellow")
            out_table.add_column("Ports", style="cyan")
            out_table.add_column("Destination", style="red")
            for i, r in enumerate(sg["egress"], 1):
                out_table.add_row(str(i), r["protocol"], r["ports"], r["dest"])
            self.console.print(out_table)

    def show_nacl(self, vpc: dict, nacl_ref: str):
        nacl = resolve_item(vpc.get("nacls", []), nacl_ref, "name", "id")
        if not nacl:
            self.console.print(f"[red]NACL '{nacl_ref}' not found[/]")
            return
        self.console.print(
            Panel(f"[bold]{nacl.get('name') or nacl['id']}[/]", title="Network ACL")
        )

        ingress = [e for e in nacl["entries"] if not e["egress"]]
        egress = [e for e in nacl["entries"] if e["egress"]]

        if ingress:
            in_table = Table(
                title="Ingress Rules", show_header=True, header_style="bold"
            )
            in_table.add_column("Rule #", style="dim", justify="right")
            in_table.add_column("Protocol", style="yellow")
            in_table.add_column("CIDR", style="cyan")
            in_table.add_column("Action", style="white")
            for e in sorted(ingress, key=lambda x: x["rule"]):
                action_style = "green" if e["action"] == "allow" else "red"
                in_table.add_row(
                    str(e["rule"]),
                    e["protocol"],
                    e["cidr"],
                    Text(e["action"], style=action_style),
                )
            self.console.print(in_table)

        if egress:
            out_table = Table(
                title="Egress Rules", show_header=True, header_style="bold"
            )
            out_table.add_column("Rule #", style="dim", justify="right")
            out_table.add_column("Protocol", style="yellow")
            out_table.add_column("CIDR", style="cyan")
            out_table.add_column("Action", style="white")
            for e in sorted(egress, key=lambda x: x["rule"]):
                action_style = "green" if e["action"] == "allow" else "red"
                out_table.add_row(
                    str(e["rule"]),
                    e["protocol"],
                    e["cidr"],
                    Text(e["action"], style=action_style),
                )
            self.console.print(out_table)


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


def resolve_vpc(vpcs: list[dict], ref: str) -> Optional[dict]:
    """Resolve VPC by index (1-based), name, or ID"""
    return resolve_item(vpcs, ref, "name", "id")
