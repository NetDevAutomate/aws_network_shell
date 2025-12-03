"""Client VPN module for remote access troubleshooting"""

import concurrent.futures
from typing import Optional, List
import boto3
from rich.table import Table
from rich.text import Text

from ..core import Cache, BaseDisplay, BaseClient

cache = Cache("client-vpn")


class ClientVPNClient(BaseClient):
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
        data = {"region": region, "endpoints": [], "connections": []}
        try:
            ec2 = self.session.client("ec2", region_name=region)

            # Get Client VPN endpoints
            try:
                paginator = ec2.get_paginator("describe_client_vpn_endpoints")
                for page in paginator.paginate():
                    for ep in page.get("ClientVpnEndpoints", []):
                        # Get target networks
                        target_networks = []
                        try:
                            tn_resp = ec2.describe_client_vpn_target_networks(
                                ClientVpnEndpointId=ep["ClientVpnEndpointId"]
                            )
                            target_networks = [
                                {
                                    "association_id": tn.get("AssociationId"),
                                    "vpc_id": tn.get("VpcId"),
                                    "subnet_id": tn.get("TargetNetworkId"),
                                    "status": tn.get("Status", {}).get("Code"),
                                }
                                for tn in tn_resp.get("ClientVpnTargetNetworks", [])
                            ]
                        except Exception:
                            pass

                        # Get routes
                        routes = []
                        try:
                            rt_resp = ec2.describe_client_vpn_routes(
                                ClientVpnEndpointId=ep["ClientVpnEndpointId"]
                            )
                            routes = [
                                {
                                    "destination": rt.get("DestinationCidr"),
                                    "target_subnet": rt.get("TargetSubnet"),
                                    "type": rt.get("Type"),
                                    "origin": rt.get("Origin"),
                                    "status": rt.get("Status", {}).get("Code"),
                                }
                                for rt in rt_resp.get("Routes", [])
                            ]
                        except Exception:
                            pass

                        # Get auth rules
                        auth_rules = []
                        try:
                            ar_resp = ec2.describe_client_vpn_authorization_rules(
                                ClientVpnEndpointId=ep["ClientVpnEndpointId"]
                            )
                            auth_rules = [
                                {
                                    "destination": ar.get("DestinationCidr"),
                                    "group_id": ar.get("GroupId"),
                                    "access_all": ar.get("AccessAll", False),
                                    "status": ar.get("Status", {}).get("Code"),
                                }
                                for ar in ar_resp.get("AuthorizationRules", [])
                            ]
                        except Exception:
                            pass

                        # Get name from tags
                        name = ep["ClientVpnEndpointId"]
                        for tag in ep.get("Tags", []):
                            if tag["Key"] == "Name":
                                name = tag["Value"]
                                break

                        data["endpoints"].append(
                            {
                                "id": ep["ClientVpnEndpointId"],
                                "name": name,
                                "status": ep.get("Status", {}).get("Code", ""),
                                "client_cidr": ep.get("ClientCidrBlock", ""),
                                "dns_servers": ep.get("DnsServers", []),
                                "split_tunnel": ep.get("SplitTunnel", False),
                                "vpn_protocol": ep.get("VpnProtocol", ""),
                                "transport_protocol": ep.get("TransportProtocol", ""),
                                "vpc_id": ep.get("VpcId"),
                                "security_groups": ep.get("SecurityGroupIds", []),
                                "auth_options": [
                                    a.get("Type")
                                    for a in ep.get("AuthenticationOptions", [])
                                ],
                                "target_networks": target_networks,
                                "routes": routes,
                                "auth_rules": auth_rules,
                                "connection_log": ep.get(
                                    "ConnectionLogOptions", {}
                                ).get("Enabled", False),
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
                if result["endpoints"]:
                    all_data.append(result)
        return sorted(all_data, key=lambda x: x["region"])

    def get_connections(self, region: str, endpoint_id: str) -> List[dict]:
        """Get active connections for a Client VPN endpoint"""
        try:
            ec2 = self.session.client("ec2", region_name=region)
            resp = ec2.describe_client_vpn_connections(ClientVpnEndpointId=endpoint_id)
            return [
                {
                    "connection_id": c.get("ConnectionId"),
                    "username": c.get("Username", ""),
                    "status": c.get("Status", {}).get("Code", ""),
                    "client_ip": c.get("ClientIp", ""),
                    "common_name": c.get("CommonName", ""),
                    "connection_established": c.get("ConnectionEstablishedTime"),
                    "connection_end": c.get("ConnectionEndTime"),
                    "egress_bytes": c.get("EgressBytes", 0),
                    "ingress_bytes": c.get("IngressBytes", 0),
                    "egress_packets": c.get("EgressPackets", 0),
                    "ingress_packets": c.get("IngressPackets", 0),
                }
                for c in resp.get("Connections", [])
            ]
        except Exception:
            return []


class ClientVPNDisplay(BaseDisplay):
    def show_endpoints(self, data: List[dict]):
        endpoints = []
        for region_data in data:
            for ep in region_data.get("endpoints", []):
                ep["region"] = region_data["region"]
                endpoints.append(ep)

        if not endpoints:
            self.console.print("[yellow]No Client VPN endpoints found[/]")
            return

        table = Table(
            title="Client VPN Endpoints", show_header=True, header_style="bold"
        )
        table.add_column("#", style="dim", justify="right")
        table.add_column("Region", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Client CIDR", style="yellow")
        table.add_column("VPC", style="white")
        table.add_column("Networks", style="magenta", justify="right")
        table.add_column("Split", style="blue")
        table.add_column("Status")

        for i, ep in enumerate(endpoints, 1):
            status = ep["status"]
            status_style = (
                "green"
                if status == "available"
                else ("yellow" if status == "pending-associate" else "red")
            )
            split = "Yes" if ep.get("split_tunnel") else "No"

            table.add_row(
                str(i),
                ep["region"],
                ep["name"][:30],
                ep.get("client_cidr", ""),
                ep.get("vpc_id", "")[:20],
                str(len(ep.get("target_networks", []))),
                split,
                Text(status, style=status_style),
            )

        self.console.print(table)
        self.console.print(f"\n[dim]Total: {len(endpoints)} endpoint(s)[/]")

    def show_endpoint_detail(self, endpoint: dict, connections: List[dict] = None):
        """Show detailed endpoint info"""
        self.console.print(f"\n[bold]Client VPN: {endpoint['name']}[/bold]")
        self.console.print(f"[dim]{endpoint['id']}[/]\n")

        table = Table(show_header=False, box=None)
        table.add_column("Field", style="cyan")
        table.add_column("Value")

        status = endpoint["status"]
        status_style = "green" if status == "available" else "yellow"

        table.add_row("Status", Text(status, style=status_style))
        table.add_row("Region", endpoint.get("region", ""))
        table.add_row("Client CIDR", endpoint.get("client_cidr", ""))
        table.add_row("VPC", endpoint.get("vpc_id", ""))
        table.add_row(
            "Protocol",
            f"{endpoint.get('vpn_protocol', '')} / {endpoint.get('transport_protocol', '')}",
        )
        table.add_row(
            "Split Tunnel", "Enabled" if endpoint.get("split_tunnel") else "Disabled"
        )
        table.add_row(
            "Connection Logging",
            "Enabled" if endpoint.get("connection_log") else "Disabled",
        )

        if endpoint.get("dns_servers"):
            table.add_row("DNS Servers", ", ".join(endpoint["dns_servers"]))

        if endpoint.get("auth_options"):
            table.add_row("Auth Types", ", ".join(endpoint["auth_options"]))

        if endpoint.get("security_groups"):
            table.add_row("Security Groups", ", ".join(endpoint["security_groups"][:3]))

        self.console.print(table)

        # Target networks
        if endpoint.get("target_networks"):
            self.console.print("\n[bold]Target Networks:[/bold]")
            tn_table = Table(show_header=True, header_style="bold")
            tn_table.add_column("Subnet", style="cyan")
            tn_table.add_column("VPC", style="yellow")
            tn_table.add_column("Status")

            for tn in endpoint["target_networks"]:
                status_style = "green" if tn.get("status") == "associated" else "yellow"
                tn_table.add_row(
                    tn.get("subnet_id", ""),
                    tn.get("vpc_id", ""),
                    Text(tn.get("status", ""), style=status_style),
                )
            self.console.print(tn_table)

        # Routes
        if endpoint.get("routes"):
            self.console.print("\n[bold]Routes:[/bold]")
            rt_table = Table(show_header=True, header_style="bold")
            rt_table.add_column("Destination", style="cyan")
            rt_table.add_column("Target Subnet", style="yellow")
            rt_table.add_column("Type", style="magenta")
            rt_table.add_column("Status")

            for rt in endpoint["routes"][:10]:
                status_style = "green" if rt.get("status") == "active" else "yellow"
                rt_table.add_row(
                    rt.get("destination", ""),
                    rt.get("target_subnet", ""),
                    rt.get("type", ""),
                    Text(rt.get("status", ""), style=status_style),
                )
            if len(endpoint["routes"]) > 10:
                self.console.print(
                    f"[dim]... and {len(endpoint['routes']) - 10} more routes[/]"
                )
            self.console.print(rt_table)

        # Active connections
        if connections:
            self.console.print("\n[bold]Active Connections:[/bold]")
            self.show_connections(connections)

    def show_connections(self, connections: List[dict]):
        if not connections:
            self.console.print("[yellow]No active connections[/]")
            return

        table = Table(show_header=True, header_style="bold")
        table.add_column("#", style="dim", justify="right")
        table.add_column("Username", style="green")
        table.add_column("Client IP", style="cyan")
        table.add_column("Status")
        table.add_column("Egress", style="yellow", justify="right")
        table.add_column("Ingress", style="magenta", justify="right")
        table.add_column("Connected", style="dim")

        for i, conn in enumerate(connections, 1):
            status = conn.get("status", "")
            status_style = "green" if status == "active" else "yellow"

            # Format bytes
            egress = conn.get("egress_bytes", 0)
            ingress = conn.get("ingress_bytes", 0)
            egress_str = (
                f"{egress / 1024 / 1024:.1f}MB"
                if egress > 1024 * 1024
                else f"{egress / 1024:.1f}KB"
            )
            ingress_str = (
                f"{ingress / 1024 / 1024:.1f}MB"
                if ingress > 1024 * 1024
                else f"{ingress / 1024:.1f}KB"
            )

            connected = conn.get("connection_established")
            if connected:
                connected = (
                    connected.strftime("%m-%d %H:%M")
                    if hasattr(connected, "strftime")
                    else str(connected)[:16]
                )

            table.add_row(
                str(i),
                conn.get("username", conn.get("common_name", ""))[:20],
                conn.get("client_ip", ""),
                Text(status, style=status_style),
                egress_str,
                ingress_str,
                str(connected or ""),
            )

        self.console.print(table)
        self.console.print(f"\n[dim]Total: {len(connections)} connection(s)[/]")
