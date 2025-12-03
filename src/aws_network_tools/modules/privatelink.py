"""PrivateLink Services module for endpoint service troubleshooting"""

import concurrent.futures
from typing import Optional, List
import boto3
from rich.table import Table
from rich.text import Text

from ..core import Cache, BaseDisplay, BaseClient

cache = Cache("privatelink")


class PrivateLinkClient(BaseClient):
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
        data = {"region": region, "endpoint_services": [], "vpc_endpoints": []}
        try:
            ec2 = self.session.client("ec2", region_name=region)

            # Get VPC Endpoint Services (services you provide)
            try:
                paginator = ec2.get_paginator(
                    "describe_vpc_endpoint_service_configurations"
                )
                for page in paginator.paginate():
                    for svc in page.get("ServiceConfigurations", []):
                        # Get endpoint connections
                        connections = []
                        try:
                            conn_resp = ec2.describe_vpc_endpoint_connections(
                                Filters=[
                                    {"Name": "service-id", "Values": [svc["ServiceId"]]}
                                ]
                            )
                            for conn in conn_resp.get("VpcEndpointConnections", []):
                                connections.append(
                                    {
                                        "endpoint_id": conn.get("VpcEndpointId"),
                                        "owner": conn.get("VpcEndpointOwner"),
                                        "state": conn.get("VpcEndpointState"),
                                        "creation_time": conn.get("CreationTimestamp"),
                                    }
                                )
                        except Exception:
                            pass

                        # Get name from tags
                        name = svc["ServiceId"]
                        for tag in svc.get("Tags", []):
                            if tag["Key"] == "Name":
                                name = tag["Value"]
                                break

                        data["endpoint_services"].append(
                            {
                                "id": svc["ServiceId"],
                                "name": name,
                                "service_name": svc.get("ServiceName", ""),
                                "service_type": svc.get("ServiceType", [{}])[0].get(
                                    "ServiceType", ""
                                ),
                                "state": svc.get("ServiceState", ""),
                                "acceptance_required": svc.get(
                                    "AcceptanceRequired", False
                                ),
                                "availability_zones": svc.get("AvailabilityZones", []),
                                "network_load_balancers": svc.get(
                                    "NetworkLoadBalancerArns", []
                                ),
                                "gateway_load_balancers": svc.get(
                                    "GatewayLoadBalancerArns", []
                                ),
                                "private_dns_name": svc.get("PrivateDnsName", ""),
                                "private_dns_name_verified": svc.get(
                                    "PrivateDnsNameConfiguration", {}
                                ).get("State")
                                == "verified",
                                "connections": connections,
                            }
                        )
            except Exception:
                pass

            # Get VPC Endpoints (services you consume) - Interface and GatewayLoadBalancer types
            try:
                paginator = ec2.get_paginator("describe_vpc_endpoints")
                for page in paginator.paginate(
                    Filters=[
                        {
                            "Name": "vpc-endpoint-type",
                            "Values": ["Interface", "GatewayLoadBalancer"],
                        }
                    ]
                ):
                    for ep in page.get("VpcEndpoints", []):
                        # Get name from tags
                        name = ep["VpcEndpointId"]
                        for tag in ep.get("Tags", []):
                            if tag["Key"] == "Name":
                                name = tag["Value"]
                                break

                        data["vpc_endpoints"].append(
                            {
                                "id": ep["VpcEndpointId"],
                                "name": name,
                                "service_name": ep.get("ServiceName", ""),
                                "type": ep.get("VpcEndpointType", ""),
                                "state": ep.get("State", ""),
                                "vpc_id": ep.get("VpcId", ""),
                                "subnet_ids": ep.get("SubnetIds", []),
                                "network_interfaces": ep.get("NetworkInterfaceIds", []),
                                "dns_entries": [
                                    d.get("DnsName") for d in ep.get("DnsEntries", [])
                                ],
                                "private_dns_enabled": ep.get(
                                    "PrivateDnsEnabled", False
                                ),
                                "security_groups": [
                                    sg.get("GroupId") for sg in ep.get("Groups", [])
                                ],
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
                if result["endpoint_services"] or result["vpc_endpoints"]:
                    all_data.append(result)
        return sorted(all_data, key=lambda x: x["region"])


class PrivateLinkDisplay(BaseDisplay):
    def show_endpoint_services(self, data: List[dict]):
        """Show VPC Endpoint Services (services you provide)"""
        services = []
        for region_data in data:
            for svc in region_data.get("endpoint_services", []):
                svc["region"] = region_data["region"]
                services.append(svc)

        if not services:
            self.console.print("[yellow]No VPC Endpoint Services found[/]")
            return

        table = Table(
            title="VPC Endpoint Services (Provider)",
            show_header=True,
            header_style="bold",
        )
        table.add_column("#", style="dim", justify="right")
        table.add_column("Region", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Service Name", style="yellow")
        table.add_column("Type", style="white")
        table.add_column("AZs", style="magenta", justify="right")
        table.add_column("Connections", style="blue", justify="right")
        table.add_column("State")

        for i, svc in enumerate(services, 1):
            state = svc["state"]
            state_style = (
                "green"
                if state == "Available"
                else ("yellow" if state == "Pending" else "red")
            )

            table.add_row(
                str(i),
                svc["region"],
                svc["name"][:25],
                svc.get("service_name", "")[-40:],  # Show last part
                svc.get("service_type", ""),
                str(len(svc.get("availability_zones", []))),
                str(len(svc.get("connections", []))),
                Text(state, style=state_style),
            )

        self.console.print(table)
        self.console.print(f"\n[dim]Total: {len(services)} endpoint service(s)[/]")

    def show_vpc_endpoints(self, data: List[dict]):
        """Show VPC Endpoints (services you consume)"""
        endpoints = []
        for region_data in data:
            for ep in region_data.get("vpc_endpoints", []):
                ep["region"] = region_data["region"]
                endpoints.append(ep)

        if not endpoints:
            self.console.print("[yellow]No VPC Endpoints (Interface/GWLB) found[/]")
            return

        table = Table(
            title="VPC Endpoints (Consumer)", show_header=True, header_style="bold"
        )
        table.add_column("#", style="dim", justify="right")
        table.add_column("Region", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Service", style="yellow")
        table.add_column("Type", style="white")
        table.add_column("VPC", style="magenta")
        table.add_column("Subnets", style="blue", justify="right")
        table.add_column("State")

        for i, ep in enumerate(endpoints, 1):
            state = ep["state"]
            state_style = (
                "green"
                if state == "available"
                else ("yellow" if state == "pending" else "red")
            )

            # Shorten service name
            service_name = ep.get("service_name", "")
            if ".amazonaws.com" in service_name:
                service_name = service_name.split(".")[-3]  # Get service name part
            elif service_name.startswith("com.amazonaws.vpce."):
                service_name = "Custom: " + service_name[-15:]

            table.add_row(
                str(i),
                ep["region"],
                ep["name"][:25],
                service_name[:25],
                ep.get("type", ""),
                ep.get("vpc_id", "")[:15],
                str(len(ep.get("subnet_ids", []))),
                Text(state, style=state_style),
            )

        self.console.print(table)
        self.console.print(f"\n[dim]Total: {len(endpoints)} endpoint(s)[/]")

    def show_service_detail(self, service: dict):
        """Show detailed endpoint service info"""
        self.console.print(f"\n[bold]Endpoint Service: {service['name']}[/bold]")
        self.console.print(f"[dim]{service['id']}[/]\n")

        table = Table(show_header=False, box=None)
        table.add_column("Field", style="cyan")
        table.add_column("Value")

        state = service["state"]
        state_style = "green" if state == "Available" else "yellow"

        table.add_row("State", Text(state, style=state_style))
        table.add_row("Region", service.get("region", ""))
        table.add_row("Service Name", service.get("service_name", ""))
        table.add_row("Type", service.get("service_type", ""))
        table.add_row(
            "Acceptance Required", "Yes" if service.get("acceptance_required") else "No"
        )
        table.add_row(
            "Availability Zones", ", ".join(service.get("availability_zones", []))
        )

        if service.get("private_dns_name"):
            dns_status = (
                "✓ Verified"
                if service.get("private_dns_name_verified")
                else "✗ Not Verified"
            )
            table.add_row(
                "Private DNS", f"{service['private_dns_name']} ({dns_status})"
            )

        # Load balancers
        nlbs = service.get("network_load_balancers", [])
        gwlbs = service.get("gateway_load_balancers", [])
        if nlbs:
            table.add_row("NLBs", str(len(nlbs)))
        if gwlbs:
            table.add_row("GWLBs", str(len(gwlbs)))

        self.console.print(table)

        # Connections
        if service.get("connections"):
            self.console.print("\n[bold]Endpoint Connections:[/bold]")
            conn_table = Table(show_header=True, header_style="bold")
            conn_table.add_column("Endpoint ID", style="cyan")
            conn_table.add_column("Owner", style="yellow")
            conn_table.add_column("State")

            for conn in service["connections"]:
                state = conn.get("state", "")
                state_style = (
                    "green"
                    if state == "available"
                    else (
                        "yellow" if state in ["pending", "pendingAcceptance"] else "red"
                    )
                )

                conn_table.add_row(
                    conn.get("endpoint_id", ""),
                    conn.get("owner", ""),
                    Text(state, style=state_style),
                )

            self.console.print(conn_table)

    def show_endpoint_detail(self, endpoint: dict):
        """Show detailed VPC endpoint info"""
        self.console.print(f"\n[bold]VPC Endpoint: {endpoint['name']}[/bold]")
        self.console.print(f"[dim]{endpoint['id']}[/]\n")

        table = Table(show_header=False, box=None)
        table.add_column("Field", style="cyan")
        table.add_column("Value")

        state = endpoint["state"]
        state_style = "green" if state == "available" else "yellow"

        table.add_row("State", Text(state, style=state_style))
        table.add_row("Region", endpoint.get("region", ""))
        table.add_row("Service", endpoint.get("service_name", ""))
        table.add_row("Type", endpoint.get("type", ""))
        table.add_row("VPC", endpoint.get("vpc_id", ""))
        table.add_row(
            "Private DNS",
            "Enabled" if endpoint.get("private_dns_enabled") else "Disabled",
        )

        if endpoint.get("subnet_ids"):
            table.add_row("Subnets", ", ".join(endpoint["subnet_ids"][:5]))

        if endpoint.get("security_groups"):
            table.add_row("Security Groups", ", ".join(endpoint["security_groups"]))

        if endpoint.get("network_interfaces"):
            table.add_row("ENIs", ", ".join(endpoint["network_interfaces"][:3]))

        self.console.print(table)

        # DNS entries
        if endpoint.get("dns_entries"):
            self.console.print("\n[bold]DNS Entries:[/bold]")
            for dns in endpoint["dns_entries"][:5]:
                self.console.print(f"  [cyan]{dns}[/]")

    def show_all(self, data: List[dict]):
        """Show both endpoint services and VPC endpoints"""
        self.show_endpoint_services(data)
        self.console.print()
        self.show_vpc_endpoints(data)
