"""Global Accelerator module for GA endpoint health monitoring"""

from typing import Optional, List
import boto3
from rich.table import Table
from rich.text import Text

from ..core import Cache, BaseDisplay, BaseClient

cache = Cache("global-accelerator")


class GlobalAcceleratorClient(BaseClient):
    def __init__(
        self, profile: Optional[str] = None, session: Optional[boto3.Session] = None
    ):
        super().__init__(profile, session)

    def discover(self) -> List[dict]:
        """Global Accelerator is a global service, no region iteration needed"""
        accelerators = []
        try:
            # GA API is only available in us-west-2
            ga = self.session.client("globalaccelerator", region_name="us-west-2")

            paginator = ga.get_paginator("list_accelerators")
            for page in paginator.paginate():
                for acc in page.get("Accelerators", []):
                    acc_data = {
                        "arn": acc["AcceleratorArn"],
                        "name": acc.get("Name", ""),
                        "status": acc.get("Status", ""),
                        "enabled": acc.get("Enabled", False),
                        "dns_name": acc.get("DnsName", ""),
                        "ip_address_type": acc.get("IpAddressType", ""),
                        "ip_sets": [],
                        "listeners": [],
                    }

                    # Get IP sets
                    for ip_set in acc.get("IpSets", []):
                        acc_data["ip_sets"].append(
                            {
                                "ip_family": ip_set.get("IpFamily", ""),
                                "ip_addresses": ip_set.get("IpAddresses", []),
                            }
                        )

                    # Get listeners
                    try:
                        listener_resp = ga.list_listeners(
                            AcceleratorArn=acc["AcceleratorArn"]
                        )
                        for listener in listener_resp.get("Listeners", []):
                            listener_data = {
                                "arn": listener["ListenerArn"],
                                "protocol": listener.get("Protocol", ""),
                                "port_ranges": [
                                    f"{pr.get('FromPort')}-{pr.get('ToPort')}"
                                    for pr in listener.get("PortRanges", [])
                                ],
                                "client_affinity": listener.get("ClientAffinity", ""),
                                "endpoint_groups": [],
                            }

                            # Get endpoint groups
                            try:
                                eg_resp = ga.list_endpoint_groups(
                                    ListenerArn=listener["ListenerArn"]
                                )
                                for eg in eg_resp.get("EndpointGroups", []):
                                    eg_data = {
                                        "arn": eg["EndpointGroupArn"],
                                        "region": eg.get("EndpointGroupRegion", ""),
                                        "health_check_path": eg.get(
                                            "HealthCheckPath", ""
                                        ),
                                        "health_check_port": eg.get("HealthCheckPort"),
                                        "health_check_protocol": eg.get(
                                            "HealthCheckProtocol", ""
                                        ),
                                        "health_check_interval": eg.get(
                                            "HealthCheckIntervalSeconds"
                                        ),
                                        "threshold_count": eg.get("ThresholdCount"),
                                        "traffic_dial": eg.get(
                                            "TrafficDialPercentage", 100
                                        ),
                                        "endpoints": [],
                                    }

                                    for ep in eg.get("EndpointDescriptions", []):
                                        eg_data["endpoints"].append(
                                            {
                                                "endpoint_id": ep.get("EndpointId", ""),
                                                "weight": ep.get("Weight", 0),
                                                "health_state": ep.get(
                                                    "HealthState", ""
                                                ),
                                                "health_reason": ep.get(
                                                    "HealthReason", ""
                                                ),
                                                "client_ip_preservation": ep.get(
                                                    "ClientIPPreservationEnabled", False
                                                ),
                                            }
                                        )

                                    listener_data["endpoint_groups"].append(eg_data)
                            except Exception:
                                pass

                            acc_data["listeners"].append(listener_data)
                    except Exception:
                        pass

                    accelerators.append(acc_data)

        except Exception:
            pass

        return accelerators


class GlobalAcceleratorDisplay(BaseDisplay):
    def show_accelerators(self, data: List[dict]):
        if not data:
            self.console.print("[yellow]No Global Accelerators found[/]")
            return

        table = Table(
            title="Global Accelerators", show_header=True, header_style="bold"
        )
        table.add_column("#", style="dim", justify="right")
        table.add_column("Name", style="green")
        table.add_column("DNS Name", style="cyan")
        table.add_column("IPs", style="yellow")
        table.add_column("Listeners", style="magenta", justify="right")
        table.add_column("Endpoints", style="blue", justify="right")
        table.add_column("Enabled", style="white")
        table.add_column("Status")

        for i, acc in enumerate(data, 1):
            status = acc["status"]
            status_style = (
                "green"
                if status == "DEPLOYED"
                else ("yellow" if status == "IN_PROGRESS" else "red")
            )

            # Get all IPs
            ips = []
            for ip_set in acc.get("ip_sets", []):
                ips.extend(ip_set.get("ip_addresses", []))

            # Count total endpoints
            total_endpoints = sum(
                len(eg.get("endpoints", []))
                for listener in acc.get("listeners", [])
                for eg in listener.get("endpoint_groups", [])
            )

            enabled = "Yes" if acc.get("enabled") else "No"

            table.add_row(
                str(i),
                acc["name"][:25],
                acc.get("dns_name", "")[:35],
                ", ".join(ips[:2]) + ("..." if len(ips) > 2 else ""),
                str(len(acc.get("listeners", []))),
                str(total_endpoints),
                enabled,
                Text(status, style=status_style),
            )

        self.console.print(table)
        self.console.print(f"\n[dim]Total: {len(data)} accelerator(s)[/]")

    def show_accelerator_detail(self, acc: dict):
        """Show detailed accelerator info"""
        self.console.print(f"\n[bold]Global Accelerator: {acc['name']}[/bold]\n")

        table = Table(show_header=False, box=None)
        table.add_column("Field", style="cyan")
        table.add_column("Value")

        status = acc["status"]
        status_style = "green" if status == "DEPLOYED" else "yellow"

        table.add_row("Status", Text(status, style=status_style))
        table.add_row("Enabled", "Yes" if acc.get("enabled") else "No")
        table.add_row("DNS Name", acc.get("dns_name", ""))
        table.add_row("IP Address Type", acc.get("ip_address_type", ""))

        # IP addresses
        for ip_set in acc.get("ip_sets", []):
            ips = ", ".join(ip_set.get("ip_addresses", []))
            table.add_row(f"IPs ({ip_set.get('ip_family', '')})", ips)

        self.console.print(table)

        # Listeners and endpoint groups
        for listener in acc.get("listeners", []):
            ports = ", ".join(listener.get("port_ranges", []))
            self.console.print(
                f"\n[bold]Listener:[/bold] {listener.get('protocol', '')} {ports}"
            )
            self.console.print(
                f"[dim]Client Affinity: {listener.get('client_affinity', 'NONE')}[/]"
            )

            for eg in listener.get("endpoint_groups", []):
                self.console.print(
                    f"\n  [bold]Endpoint Group:[/bold] {eg.get('region', '')}"
                )
                self.console.print(
                    f"  [dim]Traffic Dial: {eg.get('traffic_dial', 100)}% | Health Check: {eg.get('health_check_protocol', '')} {eg.get('health_check_path', '')}[/]"
                )

                if eg.get("endpoints"):
                    ep_table = Table(
                        show_header=True, header_style="bold", padding=(0, 1)
                    )
                    ep_table.add_column("Endpoint ID", style="cyan")
                    ep_table.add_column("Weight", style="yellow", justify="right")
                    ep_table.add_column("Health")
                    ep_table.add_column("Reason", style="dim")

                    for ep in eg["endpoints"]:
                        health = ep.get("health_state", "")
                        health_style = (
                            "green"
                            if health == "HEALTHY"
                            else ("yellow" if health == "INITIAL" else "red")
                        )

                        ep_table.add_row(
                            ep.get("endpoint_id", "")[:40],
                            str(ep.get("weight", 0)),
                            Text(health, style=health_style),
                            ep.get("health_reason", "")[:30],
                        )

                    self.console.print(ep_table)

    def show_endpoint_health(self, data: List[dict]):
        """Show health status of all endpoints across all accelerators"""
        endpoints = []
        for acc in data:
            for listener in acc.get("listeners", []):
                for eg in listener.get("endpoint_groups", []):
                    for ep in eg.get("endpoints", []):
                        endpoints.append(
                            {
                                "accelerator": acc["name"],
                                "region": eg.get("region", ""),
                                "endpoint_id": ep.get("endpoint_id", ""),
                                "health_state": ep.get("health_state", ""),
                                "health_reason": ep.get("health_reason", ""),
                                "weight": ep.get("weight", 0),
                            }
                        )

        if not endpoints:
            self.console.print("[yellow]No endpoints found[/]")
            return

        # Sort by health state (unhealthy first)
        health_order = {"UNHEALTHY": 0, "INITIAL": 1, "HEALTHY": 2}
        endpoints.sort(key=lambda x: health_order.get(x["health_state"], 3))

        table = Table(
            title="Global Accelerator Endpoint Health",
            show_header=True,
            header_style="bold",
        )
        table.add_column("#", style="dim", justify="right")
        table.add_column("Accelerator", style="green")
        table.add_column("Region", style="cyan")
        table.add_column("Endpoint ID", style="yellow")
        table.add_column("Weight", style="magenta", justify="right")
        table.add_column("Health")
        table.add_column("Reason", style="dim")

        for i, ep in enumerate(endpoints, 1):
            health = ep["health_state"]
            health_style = (
                "green"
                if health == "HEALTHY"
                else ("yellow" if health == "INITIAL" else "red")
            )

            table.add_row(
                str(i),
                ep["accelerator"][:20],
                ep["region"],
                ep["endpoint_id"][:35],
                str(ep["weight"]),
                Text(health, style=health_style),
                ep.get("health_reason", "")[:25],
            )

        self.console.print(table)

        # Summary
        healthy = sum(1 for ep in endpoints if ep["health_state"] == "HEALTHY")
        unhealthy = sum(1 for ep in endpoints if ep["health_state"] == "UNHEALTHY")
        initial = sum(1 for ep in endpoints if ep["health_state"] == "INITIAL")

        summary = f"\n[dim]Total: {len(endpoints)} endpoint(s) - "
        summary += f"[green]HEALTHY: {healthy}[/green], "
        summary += f"[red]UNHEALTHY: {unhealthy}[/red], "
        summary += f"[yellow]INITIAL: {initial}[/yellow][/]"
        self.console.print(summary)
