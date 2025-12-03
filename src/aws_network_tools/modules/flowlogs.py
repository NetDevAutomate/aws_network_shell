"""VPC Flow Logs monitoring module"""

import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import boto3
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from ..core import Cache, BaseDisplay, BaseClient, ModuleInterface, run_with_spinner

cache = Cache("flowlogs")


class FlowLogsModule(ModuleInterface):
    @property
    def name(self) -> str:
        return "monitor"

    @property
    def commands(self) -> Dict[str, str]:
        return {
            "monitor": "Monitor traffic for an interface: monitor interface <eni-id> [minutes] [--analyze]",
        }

    def execute(self, shell: Any, command: str, args: str):
        if command == "monitor":
            parts = args.split()
            analyze = False
            if "--analyze" in parts:
                analyze = True
                parts.remove("--analyze")

            if len(parts) < 2 or parts[0] != "interface":
                shell.console.print(
                    "[red]Usage: monitor interface <eni-id> [minutes] [--analyze][/]"
                )
                return

            eni_id = parts[1]
            minutes = int(parts[2]) if len(parts) > 2 else 15

            if analyze:
                self._analyze_interface(shell, eni_id, minutes)
            else:
                self._monitor_interface(shell, eni_id, minutes)

    def _get_log_group(self, shell, client, eni_id):
        log_group = run_with_spinner(
            lambda: client.find_log_group(eni_id),
            f"Locating Flow Logs for {eni_id}",
            console=shell.console,
        )
        if not log_group:
            shell.console.print(
                f"[red]No CloudWatch Flow Logs found for {eni_id} (or its Subnet/VPC)[/]"
            )
            return None
        return log_group

    def _monitor_interface(self, shell, eni_id, minutes):
        client = FlowLogsClient(shell.profile)

        log_group = self._get_log_group(shell, client, eni_id)
        if not log_group:
            return

        # 2. Query Logs
        results = run_with_spinner(
            lambda: client.query_flow_logs(log_group, eni_id, minutes),
            f"Querying logs from {log_group} (last {minutes}m)",
            console=shell.console,
        )

        if not results:
            shell.console.print("[yellow]No traffic found in the specified window[/]")
            return

        # 3. Display
        FlowLogsDisplay(shell.console).show_logs(results, eni_id)

    def _analyze_interface(self, shell, eni_id, minutes):
        client = FlowLogsClient(shell.profile)

        log_group = self._get_log_group(shell, client, eni_id)
        if not log_group:
            return

        results = run_with_spinner(
            lambda: client.analyze_traffic(log_group, eni_id, minutes),
            f"Analyzing traffic from {log_group} (last {minutes}m)",
            console=shell.console,
        )

        display = FlowLogsDisplay(shell.console)
        display.show_top_talkers(results.get("top_talkers", []))
        display.show_anomalies(results.get("anomalies", []))


class FlowLogsClient(BaseClient):
    def __init__(
        self, profile: Optional[str] = None, session: Optional[boto3.Session] = None
    ):
        super().__init__(profile, session)

    def find_log_group(self, eni_id: str) -> Optional[str]:
        # Try to find flow logs attached to ENI, Subnet, or VPC
        ec2 = self.session.client("ec2")
        try:
            # Get ENI details to find Subnet/VPC
            eni = ec2.describe_network_interfaces(NetworkInterfaceIds=[eni_id])[
                "NetworkInterfaces"
            ][0]
            vpc_id = eni["VpcId"]
            subnet_id = eni["SubnetId"]

            # Check for Flow Logs
            # We look for ANY flow log that covers this resource and sends to CloudWatch
            resp = ec2.describe_flow_logs(
                Filters=[
                    {"Name": "resource-id", "Values": [eni_id, subnet_id, vpc_id]},
                    {"Name": "log-destination-type", "Values": ["cloud-watch-logs"]},
                    {"Name": "traffic-type", "Values": ["ALL", "ACCEPT", "REJECT"]},
                ]
            )

            if resp["FlowLogs"]:
                # Return the first one found
                return resp["FlowLogs"][0]["LogGroupName"]

            return None
        except Exception:
            return None

    def _execute_query(self, cw, log_group, query, start_time, end_time):
        start_resp = cw.start_query(
            logGroupName=log_group,
            startTime=start_time,
            endTime=end_time,
            queryString=query,
        )
        query_id = start_resp["queryId"]

        # Wait for results
        while True:
            resp = cw.get_query_results(queryId=query_id)
            status = resp["status"]
            if status in ["Complete", "Failed", "Cancelled"]:
                break
            time.sleep(0.5)

        if status != "Complete":
            return []

        # Parse results
        parsed = []
        for row in resp["results"]:
            item = {field["field"]: field["value"] for field in row}
            parsed.append(item)
        return parsed

    def query_flow_logs(self, log_group: str, eni_id: str, minutes: int) -> list[dict]:
        cw = self.session.client("logs")
        try:
            query = f"""
                fields @timestamp, srcAddr, dstAddr, srcPort, dstPort, protocol, action, bytes
                | filter interfaceId = "{eni_id}"
                | sort @timestamp desc
                | limit 100
            """

            start_time = int((datetime.now() - timedelta(minutes=minutes)).timestamp())
            end_time = int(datetime.now().timestamp())

            return self._execute_query(cw, log_group, query, start_time, end_time)

        except Exception as e:
            print(f"Error querying logs: {e}")
            return []

    def analyze_traffic(
        self, log_group: str, eni_id: str, minutes: int
    ) -> Dict[str, Any]:
        cw = self.session.client("logs")
        start_time = int((datetime.now() - timedelta(minutes=minutes)).timestamp())
        end_time = int(datetime.now().timestamp())

        try:
            # 1. Top Talkers
            query_talkers = f"""
                filter interfaceId = "{eni_id}"
                | stats sum(bytes) as total_bytes by srcAddr, dstAddr
                | sort total_bytes desc
                | limit 10
            """
            top_talkers = self._execute_query(
                cw, log_group, query_talkers, start_time, end_time
            )

            # 2. Rejections
            query_rejections = f"""
                filter interfaceId = "{eni_id}" and action = "REJECT"
                | stats count(*) as rejection_count
            """
            rejections_data = self._execute_query(
                cw, log_group, query_rejections, start_time, end_time
            )
            rejection_count = (
                int(rejections_data[0]["rejection_count"]) if rejections_data else 0
            )

            anomalies = []
            if rejection_count > 100:
                anomalies.append(
                    {
                        "type": "High Rejection Rate",
                        "description": f"Detected {rejection_count} rejected packets in the last {minutes} minutes.",
                        "severity": "HIGH",
                    }
                )

            return {"top_talkers": top_talkers, "anomalies": anomalies}
        except Exception as e:
            print(f"Error analyzing traffic: {e}")
            return {"top_talkers": [], "anomalies": []}


class FlowLogsDisplay(BaseDisplay):
    def show_top_talkers(self, data: list[dict]):
        if not data:
            self.console.print("[yellow]No top talkers found[/]")
            return

        table = Table(
            title="Top Talkers (by Volume)", show_header=True, header_style="bold"
        )
        table.add_column("Source", style="cyan")
        table.add_column("Destination", style="blue")
        table.add_column("Total Bytes", style="green", justify="right")

        for item in data:
            table.add_row(
                item.get("srcAddr", "-"),
                item.get("dstAddr", "-"),
                item.get("total_bytes", "0"),
            )
        self.console.print(table)
        self.console.print()

    def show_anomalies(self, anomalies: list[dict]):
        if not anomalies:
            self.console.print("[green]No anomalies detected.[/]")
            return

        self.console.print(Panel("[bold red]Anomalies Detected![/]", expand=False))
        for anomaly in anomalies:
            self.console.print(f"[red]• {anomaly['description']}[/]")
        self.console.print()

    def show_logs(self, logs: list[dict], eni_id: str):
        if not logs:
            return

        table = Table(
            title=f"Traffic Monitor: {eni_id}", show_header=True, header_style="bold"
        )
        table.add_column("Time", style="dim")
        table.add_column("Source", style="cyan")
        table.add_column("Dest", style="blue")
        table.add_column("Port", style="white")
        table.add_column("Proto", style="white")
        table.add_column("Action", style="bold")
        table.add_column("Bytes", style="dim", justify="right")

        for log in logs:
            action = log.get("action", "UNKNOWN")
            style = "green" if action == "ACCEPT" else "red"

            # Resolve protocol number if possible (simplified)
            proto = log.get("protocol", "")
            if proto == "6":
                proto = "TCP"
            elif proto == "17":
                proto = "UDP"
            elif proto == "1":
                proto = "ICMP"

            port = log.get("dstPort") or log.get("srcPort") or "-"

            table.add_row(
                log.get("@timestamp", "")[11:19],  # Just show time part
                log.get("srcAddr", ""),
                log.get("dstAddr", ""),
                port,
                proto,
                Text(action, style=style),
                log.get("bytes", "0"),
            )

        self.console.print(table)
