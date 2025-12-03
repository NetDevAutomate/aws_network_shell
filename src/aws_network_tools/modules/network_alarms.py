"""CloudWatch Network Alarms module for monitoring network resource health"""

import concurrent.futures
from typing import Optional, List
from datetime import datetime, timedelta
import boto3
from rich.table import Table
from rich.text import Text

from ..core import Cache, BaseDisplay, BaseClient

cache = Cache("network-alarms")

# Network-related alarm namespaces and metrics
NETWORK_METRICS = {
    "AWS/VPN": ["TunnelState", "TunnelDataIn", "TunnelDataOut"],
    "AWS/NATGateway": [
        "ErrorPortAllocation",
        "PacketsDropCount",
        "ConnectionEstablishedCount",
    ],
    "AWS/TransitGateway": [
        "PacketDropCountBlackhole",
        "PacketDropCountNoRoute",
        "BytesIn",
        "BytesOut",
    ],
    "AWS/DX": ["ConnectionState", "ConnectionBpsEgress", "ConnectionBpsIngress"],
    "AWS/NetworkFirewall": ["DroppedPackets", "PassedPackets", "RejectedPackets"],
    "AWS/EC2": ["NetworkIn", "NetworkOut", "NetworkPacketsIn", "NetworkPacketsOut"],
}


class NetworkAlarmsClient(BaseClient):
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

    def _is_network_alarm(self, alarm: dict) -> bool:
        """Check if alarm is related to network resources"""
        namespace = alarm.get("Namespace", "")
        # metric = alarm.get("MetricName", "")  # Not used

        if namespace in NETWORK_METRICS:
            return True

        # Check for custom namespaces with network-related metrics
        network_keywords = [
            "vpn",
            "tunnel",
            "nat",
            "gateway",
            "transit",
            "dx",
            "direct",
            "network",
            "firewall",
        ]
        alarm_name = alarm.get("AlarmName", "").lower()
        return any(kw in alarm_name for kw in network_keywords)

    def _scan_region(self, region: str) -> dict:
        data = {"region": region, "alarms": [], "metric_alarms": []}
        try:
            cw = self.session.client("cloudwatch", region_name=region)

            # Get all alarms and filter for network-related ones
            paginator = cw.get_paginator("describe_alarms")
            for page in paginator.paginate(
                AlarmTypes=["MetricAlarm", "CompositeAlarm"]
            ):
                for alarm in page.get("MetricAlarms", []):
                    if self._is_network_alarm(alarm):
                        data["alarms"].append(
                            {
                                "name": alarm["AlarmName"],
                                "state": alarm["StateValue"],
                                "state_reason": alarm.get("StateReason", "")[:100],
                                "state_updated": alarm.get("StateUpdatedTimestamp"),
                                "namespace": alarm.get("Namespace", ""),
                                "metric": alarm.get("MetricName", ""),
                                "threshold": alarm.get("Threshold"),
                                "comparison": alarm.get("ComparisonOperator", ""),
                                "dimensions": {
                                    d["Name"]: d["Value"]
                                    for d in alarm.get("Dimensions", [])
                                },
                                "actions_enabled": alarm.get("ActionsEnabled", True),
                            }
                        )

                for alarm in page.get("CompositeAlarms", []):
                    alarm_name = alarm.get("AlarmName", "").lower()
                    if any(
                        kw in alarm_name
                        for kw in [
                            "vpn",
                            "tunnel",
                            "nat",
                            "gateway",
                            "transit",
                            "dx",
                            "network",
                        ]
                    ):
                        data["alarms"].append(
                            {
                                "name": alarm["AlarmName"],
                                "state": alarm["StateValue"],
                                "state_reason": alarm.get("StateReason", "")[:100],
                                "state_updated": alarm.get("StateUpdatedTimestamp"),
                                "namespace": "Composite",
                                "metric": "Composite",
                                "threshold": None,
                                "comparison": "",
                                "dimensions": {},
                                "actions_enabled": alarm.get("ActionsEnabled", True),
                            }
                        )
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
                if result["alarms"]:
                    all_data.append(result)
        return sorted(all_data, key=lambda x: x["region"])

    def get_alarm_history(
        self, region: str, alarm_name: str, hours: int = 24
    ) -> List[dict]:
        """Get alarm state history"""
        try:
            cw = self.session.client("cloudwatch", region_name=region)
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=hours)

            resp = cw.describe_alarm_history(
                AlarmName=alarm_name,
                HistoryItemType="StateUpdate",
                StartDate=start_time,
                EndDate=end_time,
                MaxRecords=50,
            )
            return [
                {
                    "timestamp": h.get("Timestamp"),
                    "type": h.get("HistoryItemType"),
                    "summary": h.get("HistorySummary", ""),
                }
                for h in resp.get("AlarmHistoryItems", [])
            ]
        except Exception:
            return []


class NetworkAlarmsDisplay(BaseDisplay):
    def show_alarms(self, data: List[dict], state_filter: Optional[str] = None):
        alarms = []
        for region_data in data:
            for alarm in region_data.get("alarms", []):
                alarm["region"] = region_data["region"]
                if state_filter is None or alarm["state"] == state_filter:
                    alarms.append(alarm)

        if not alarms:
            msg = "No network alarms found"
            if state_filter:
                msg += f" in {state_filter} state"
            self.console.print(f"[yellow]{msg}[/]")
            return

        # Sort by state (ALARM first, then INSUFFICIENT_DATA, then OK)
        state_order = {"ALARM": 0, "INSUFFICIENT_DATA": 1, "OK": 2}
        alarms.sort(
            key=lambda x: (state_order.get(x["state"], 3), x["region"], x["name"])
        )

        table = Table(title="Network Alarms", show_header=True, header_style="bold")
        table.add_column("#", style="dim", justify="right")
        table.add_column("Region", style="cyan")
        table.add_column("Alarm Name", style="green")
        table.add_column("Namespace", style="white")
        table.add_column("Metric", style="yellow")
        table.add_column("Resource", style="magenta")
        table.add_column("State")
        table.add_column("Actions", style="dim")

        for i, alarm in enumerate(alarms, 1):
            state = alarm["state"]
            if state == "ALARM":
                state_style = "bold red"
            elif state == "INSUFFICIENT_DATA":
                state_style = "yellow"
            else:
                state_style = "green"

            # Extract resource ID from dimensions
            dims = alarm.get("dimensions", {})
            resource = ""
            for key in [
                "VpnId",
                "TunnelIpAddress",
                "NatGatewayId",
                "TransitGateway",
                "ConnectionId",
                "FirewallName",
            ]:
                if key in dims:
                    resource = dims[key][:20]
                    break
            if not resource and dims:
                resource = list(dims.values())[0][:20]

            actions = "✓" if alarm.get("actions_enabled") else "✗"

            table.add_row(
                str(i),
                alarm["region"],
                alarm["name"][:35],
                alarm.get("namespace", "")[:15],
                alarm.get("metric", "")[:20],
                resource,
                Text(state, style=state_style),
                actions,
            )

        self.console.print(table)

        # Summary by state
        alarm_count = sum(1 for a in alarms if a["state"] == "ALARM")
        insuff_count = sum(1 for a in alarms if a["state"] == "INSUFFICIENT_DATA")
        ok_count = sum(1 for a in alarms if a["state"] == "OK")

        summary = f"\n[dim]Total: {len(alarms)} alarm(s) - "
        summary += f"[red]ALARM: {alarm_count}[/red], "
        summary += f"[yellow]INSUFFICIENT_DATA: {insuff_count}[/yellow], "
        summary += f"[green]OK: {ok_count}[/green][/]"
        self.console.print(summary)

    def show_alarm_detail(self, alarm: dict, history: List[dict]):
        """Show detailed alarm info with history"""
        self.console.print(f"\n[bold]Alarm: {alarm['name']}[/bold]\n")

        table = Table(show_header=False, box=None)
        table.add_column("Field", style="cyan")
        table.add_column("Value")

        state = alarm["state"]
        state_style = (
            "bold red"
            if state == "ALARM"
            else ("yellow" if state == "INSUFFICIENT_DATA" else "green")
        )

        table.add_row("State", Text(state, style=state_style))
        table.add_row("Region", alarm.get("region", ""))
        table.add_row("Namespace", alarm.get("namespace", ""))
        table.add_row("Metric", alarm.get("metric", ""))

        if alarm.get("threshold") is not None:
            table.add_row(
                "Threshold", f"{alarm.get('comparison', '')} {alarm.get('threshold')}"
            )

        if alarm.get("dimensions"):
            dims = ", ".join(f"{k}={v}" for k, v in alarm["dimensions"].items())
            table.add_row("Dimensions", dims)

        table.add_row(
            "Actions Enabled", "Yes" if alarm.get("actions_enabled") else "No"
        )

        if alarm.get("state_reason"):
            table.add_row("State Reason", alarm["state_reason"])

        self.console.print(table)

        if history:
            self.console.print("\n[bold]Recent State Changes (24h):[/bold]")
            hist_table = Table(show_header=True, header_style="bold")
            hist_table.add_column("Time", style="cyan")
            hist_table.add_column("Summary")

            for h in history[:10]:
                ts = h.get("timestamp")
                if ts:
                    ts = (
                        ts.strftime("%Y-%m-%d %H:%M:%S")
                        if hasattr(ts, "strftime")
                        else str(ts)[:19]
                    )
                hist_table.add_row(ts, h.get("summary", "")[:80])

            self.console.print(hist_table)
