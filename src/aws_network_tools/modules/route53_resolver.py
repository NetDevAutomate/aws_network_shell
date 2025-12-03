"""Route 53 Resolver module for DNS troubleshooting"""

import concurrent.futures
from typing import Optional, List
import boto3
from rich.table import Table
from rich.text import Text

from ..core import Cache, BaseDisplay, BaseClient

cache = Cache("route53-resolver")


class Route53ResolverClient(BaseClient):
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

    def _scan_region(self, region: str) -> dict:
        data = {"region": region, "endpoints": [], "rules": [], "query_log_configs": []}
        try:
            r53r = self.session.client("route53resolver", region_name=region)

            # Get resolver endpoints
            try:
                paginator = r53r.get_paginator("list_resolver_endpoints")
                for page in paginator.paginate():
                    for ep in page.get("ResolverEndpoints", []):
                        ip_addresses = []
                        try:
                            ip_resp = r53r.list_resolver_endpoint_ip_addresses(
                                ResolverEndpointId=ep["Id"]
                            )
                            ip_addresses = [
                                {
                                    "ip": ip.get("Ip"),
                                    "subnet": ip.get("SubnetId"),
                                    "status": ip.get("Status"),
                                }
                                for ip in ip_resp.get("IpAddresses", [])
                            ]
                        except Exception:
                            pass

                        data["endpoints"].append(
                            {
                                "id": ep["Id"],
                                "name": ep.get("Name", ep["Id"]),
                                "direction": ep["Direction"],
                                "status": ep["Status"],
                                "vpc_id": ep.get("HostVPCId"),
                                "ip_count": ep.get("IpAddressCount", 0),
                                "ip_addresses": ip_addresses,
                            }
                        )
            except Exception:
                pass

            # Get resolver rules
            try:
                paginator = r53r.get_paginator("list_resolver_rules")
                for page in paginator.paginate():
                    for rule in page.get("ResolverRules", []):
                        # Get associated VPCs
                        assoc_vpcs = []
                        try:
                            assoc_resp = r53r.list_resolver_rule_associations(
                                Filters=[
                                    {"Name": "ResolverRuleId", "Values": [rule["Id"]]}
                                ]
                            )
                            assoc_vpcs = [
                                a.get("VPCId")
                                for a in assoc_resp.get("ResolverRuleAssociations", [])
                                if a.get("VPCId")
                            ]
                        except Exception:
                            pass

                        data["rules"].append(
                            {
                                "id": rule["Id"],
                                "name": rule.get("Name", rule["Id"]),
                                "domain": rule.get("DomainName", ""),
                                "rule_type": rule.get("RuleType", ""),
                                "status": rule.get("Status", ""),
                                "endpoint_id": rule.get("ResolverEndpointId"),
                                "target_ips": [
                                    t.get("Ip") for t in rule.get("TargetIps", [])
                                ],
                                "associated_vpcs": assoc_vpcs,
                            }
                        )
            except Exception:
                pass

            # Get query log configs
            try:
                paginator = r53r.get_paginator("list_resolver_query_log_configs")
                for page in paginator.paginate():
                    for cfg in page.get("ResolverQueryLogConfigs", []):
                        data["query_log_configs"].append(
                            {
                                "id": cfg["Id"],
                                "name": cfg.get("Name", cfg["Id"]),
                                "status": cfg.get("Status", ""),
                                "destination": cfg.get("DestinationArn", ""),
                                "association_count": cfg.get("AssociationCount", 0),
                            }
                        )
            except Exception:
                pass

        except Exception:
            pass
        return data

    def discover(self, regions: Optional[list[str]] = None) -> List[dict]:
        regions = regions or self.get_regions()
        all_data = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(self._scan_region, r): r for r in regions}
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if (
                    result["endpoints"]
                    or result["rules"]
                    or result["query_log_configs"]
                ):
                    all_data.append(result)
        return sorted(all_data, key=lambda x: x["region"])


class Route53ResolverDisplay(BaseDisplay):
    def show_endpoints(self, data: List[dict]):
        endpoints = []
        for region_data in data:
            for ep in region_data.get("endpoints", []):
                ep["region"] = region_data["region"]
                endpoints.append(ep)

        if not endpoints:
            self.console.print("[yellow]No Route 53 Resolver endpoints found[/]")
            return

        table = Table(
            title="Route 53 Resolver Endpoints", show_header=True, header_style="bold"
        )
        table.add_column("#", style="dim", justify="right")
        table.add_column("Region", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Direction", style="yellow")
        table.add_column("VPC", style="white")
        table.add_column("IPs", style="magenta", justify="right")
        table.add_column("Status")

        for i, ep in enumerate(endpoints, 1):
            status_style = "green" if ep["status"] == "OPERATIONAL" else "red"
            table.add_row(
                str(i),
                ep["region"],
                ep["name"],
                ep["direction"],
                ep.get("vpc_id", ""),
                str(ep["ip_count"]),
                Text(ep["status"], style=status_style),
            )
        self.console.print(table)
        self.console.print(f"\n[dim]Total: {len(endpoints)} endpoint(s)[/]")

    def show_rules(self, data: List[dict]):
        rules = []
        for region_data in data:
            for rule in region_data.get("rules", []):
                rule["region"] = region_data["region"]
                rules.append(rule)

        if not rules:
            self.console.print("[yellow]No Route 53 Resolver rules found[/]")
            return

        table = Table(
            title="Route 53 Resolver Rules", show_header=True, header_style="bold"
        )
        table.add_column("#", style="dim", justify="right")
        table.add_column("Region", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Domain", style="yellow")
        table.add_column("Type", style="white")
        table.add_column("Target IPs", style="magenta")
        table.add_column("VPCs", style="blue", justify="right")
        table.add_column("Status")

        for i, rule in enumerate(rules, 1):
            status_style = "green" if rule["status"] == "COMPLETE" else "yellow"
            target_ips = ", ".join(rule.get("target_ips", [])[:2])
            if len(rule.get("target_ips", [])) > 2:
                target_ips += "..."
            table.add_row(
                str(i),
                rule["region"],
                rule["name"][:25],
                rule["domain"][:30],
                rule["rule_type"],
                target_ips,
                str(len(rule.get("associated_vpcs", []))),
                Text(rule["status"], style=status_style),
            )
        self.console.print(table)
        self.console.print(f"\n[dim]Total: {len(rules)} rule(s)[/]")

    def show_query_logs(self, data: List[dict]):
        configs = []
        for region_data in data:
            for cfg in region_data.get("query_log_configs", []):
                cfg["region"] = region_data["region"]
                configs.append(cfg)

        if not configs:
            self.console.print(
                "[yellow]No Route 53 Resolver query log configs found[/]"
            )
            return

        table = Table(
            title="Route 53 Resolver Query Log Configs",
            show_header=True,
            header_style="bold",
        )
        table.add_column("#", style="dim", justify="right")
        table.add_column("Region", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Destination", style="yellow")
        table.add_column("Associations", style="magenta", justify="right")
        table.add_column("Status")

        for i, cfg in enumerate(configs, 1):
            status_style = "green" if cfg["status"] == "CREATED" else "yellow"
            # Shorten destination ARN
            dest = cfg.get("destination", "")
            if ":log-group:" in dest:
                dest = "CW: " + dest.split(":log-group:")[-1][:30]
            elif ":bucket/" in dest:
                dest = "S3: " + dest.split(":bucket/")[-1][:30]
            table.add_row(
                str(i),
                cfg["region"],
                cfg["name"],
                dest,
                str(cfg.get("association_count", 0)),
                Text(cfg["status"], style=status_style),
            )
        self.console.print(table)
        self.console.print(f"\n[dim]Total: {len(configs)} config(s)[/]")

    def show_all(self, data: List[dict]):
        self.show_endpoints(data)
        self.console.print()
        self.show_rules(data)
        self.console.print()
        self.show_query_logs(data)
