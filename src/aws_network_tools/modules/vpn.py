"""VPN and BGP module"""

from typing import Optional, Dict, List, Any
import boto3
from rich.table import Table
from rich.text import Text

from ..core import Cache, BaseDisplay, BaseClient, ModuleInterface, run_with_spinner

cache = Cache("vpn")


class VPNModule(ModuleInterface):
    @property
    def name(self) -> str:
        return "vpn"

    @property
    def commands(self) -> Dict[str, str]:
        return {
            "bgp": "Show BGP summary: bgp neighbors",
        }

    @property
    def show_commands(self) -> Dict[str, List[str]]:
        return {
            None: ["bgp-neighbors"],
        }

    def execute(self, shell: Any, command: str, args: str):
        if command == "bgp":
            if args.strip() == "neighbors":
                self._show_bgp_neighbors(shell)
            else:
                shell.console.print("[red]Usage: bgp neighbors[/]")

    def _show_bgp_neighbors(self, shell):
        client = VPNClient(shell.profile)
        neighbors = run_with_spinner(
            lambda: client.get_bgp_neighbors(shell.regions),
            "Discovering BGP sessions",
            console=shell.console,
        )
        VPNDisplay(shell.console).show_bgp_neighbors(neighbors)


class VPNClient(BaseClient):
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
        neighbors = []
        ec2 = self.session.client("ec2", region_name=region)

        try:
            # 1. Site-to-Site VPNs
            vpn_resp = ec2.describe_vpn_connections()
            for vpn in vpn_resp.get("VpnConnections", []):
                name = next(
                    (t["Value"] for t in vpn.get("Tags", []) if t["Key"] == "Name"),
                    vpn["VpnConnectionId"],
                )
                gw_id = vpn.get("TransitGatewayId") or vpn.get("VpnGatewayId")

                # Check tunnel telemetry for BGP status
                # AWS doesn't give deep BGP details for VPNs in API, mostly UP/DOWN
                # But we can infer from telemetry
                for tel in vpn.get("VgwTelemetry", []):
                    status = tel.get("Status", "DOWN")
                    ip = tel.get("OutsideIpAddress")
                    neighbors.append(
                        {
                            "region": region,
                            "type": "VPN",
                            "resource_id": vpn["VpnConnectionId"],
                            "name": name,
                            "neighbor_ip": ip,
                            "asn": "-",  # Customer ASN not always directly in telemetry
                            "status": status,
                            "uptime": tel.get("LastStatusChange", "-"),
                            "routes_received": "-",  # Not available in standard DescribeVpnConnections
                            "attached_to": gw_id,
                        }
                    )

            # 2. TGW Connect Peers (GRE/BGP over TGW attachments)
            # Find Connect attachments first
            atts = ec2.describe_transit_gateway_attachments(
                Filters=[{"Name": "resource-type", "Values": ["connect"]}]
            )
            connect_ids = [
                a["TransitGatewayAttachmentId"]
                for a in atts.get("TransitGatewayAttachments", [])
            ]

            if connect_ids:
                # Describe Connect Peers
                peers = ec2.describe_transit_gateway_connect_peers(
                    Filters=[
                        {"Name": "transit-gateway-attachment-id", "Values": connect_ids}
                    ]
                )
                for peer in peers.get("TransitGatewayConnectPeers", []):
                    peer_id = peer["TransitGatewayConnectPeerId"]
                    name = next(
                        (
                            t["Value"]
                            for t in peer.get("Tags", [])
                            if t["Key"] == "Name"
                        ),
                        peer_id,
                    )

                    config = peer.get("ConnectPeerConfiguration", {})

                    neighbors.append(
                        {
                            "region": region,
                            "type": "TGW-Connect",
                            "resource_id": peer_id,
                            "name": name,
                            "neighbor_ip": config.get("PeerAddress"),
                            "asn": config.get("BgpConfigurations", [{}])[0].get(
                                "PeerAsn", "-"
                            ),
                            "status": peer["State"].upper(),
                            "uptime": "-",
                            "routes_received": "-",
                            "attached_to": peer.get("TransitGatewayAttachmentId"),
                        }
                    )

            # 3. Direct Connect (if we want to add later, requires directconnect client)

        except Exception:
            pass

        return neighbors

    def get_bgp_neighbors(self, regions: Optional[list[str]] = None) -> list[dict]:
        if not regions:
            regions = self.get_regions()

        import concurrent.futures

        all_neighbors = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(self._scan_region, r): r for r in regions}
            for future in concurrent.futures.as_completed(futures):
                all_neighbors.extend(future.result())
        return sorted(
            all_neighbors, key=lambda x: (x["region"], x["type"], x["status"])
        )

    def discover(self, regions: Optional[list[str]] = None) -> list[dict]:
        """Discover all VPN connections."""
        import concurrent.futures

        regions = regions or self.get_regions()
        all_vpns = []

        def scan(region):
            vpns = []
            try:
                ec2 = self.session.client("ec2", region_name=region)
                resp = ec2.describe_vpn_connections()
                for v in resp.get("VpnConnections", []):
                    name = next(
                        (t["Value"] for t in v.get("Tags", []) if t["Key"] == "Name"),
                        None,
                    )
                    vpns.append(
                        {
                            "id": v["VpnConnectionId"],
                            "name": name,
                            "state": v.get("State"),
                            "type": v.get("Type"),
                            "gateway_id": v.get("TransitGatewayId")
                            or v.get("VpnGatewayId"),
                            "customer_gw": v.get("CustomerGatewayId"),
                            "region": region,
                        }
                    )
            except Exception:
                pass
            return vpns

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
            for result in ex.map(scan, regions):
                all_vpns.extend(result)
        return sorted(all_vpns, key=lambda x: (x["region"], x.get("name") or x["id"]))

    def get_vpn_detail(self, vpn_id: str, region: str) -> dict:
        """Get VPN connection details including tunnel status."""
        ec2 = self.session.client("ec2", region_name=region)
        resp = ec2.describe_vpn_connections(VpnConnectionIds=[vpn_id])
        if not resp.get("VpnConnections"):
            return {}
        v = resp["VpnConnections"][0]
        name = next((t["Value"] for t in v.get("Tags", []) if t["Key"] == "Name"), None)

        tunnels = []
        for tel in v.get("VgwTelemetry", []):
            tunnels.append(
                {
                    "outside_ip": tel.get("OutsideIpAddress"),
                    "status": tel.get("Status"),
                    "status_message": tel.get("StatusMessage"),
                    "accepted_routes": tel.get("AcceptedRouteCount", 0),
                    "last_change": str(tel.get("LastStatusChange", "")),
                }
            )

        return {
            "id": vpn_id,
            "name": name,
            "state": v.get("State"),
            "type": v.get("Type"),
            "gateway_id": v.get("TransitGatewayId") or v.get("VpnGatewayId"),
            "customer_gw": v.get("CustomerGatewayId"),
            "region": region,
            "tunnels": tunnels,
            "options": v.get("Options", {}),
        }


class VPNDisplay(BaseDisplay):
    def show_bgp_neighbors(self, neighbors: list[dict]):
        if not neighbors:
            self.console.print("[yellow]No BGP neighbors found (VPN/TGW Connect)[/]")
            return

        table = Table(
            title="BGP Neighbors Summary", show_header=True, header_style="bold"
        )
        table.add_column("Region", style="dim")
        table.add_column("Type", style="cyan")
        table.add_column("Neighbor IP", style="green")
        table.add_column("ASN", style="white")
        table.add_column("State", style="bold")
        table.add_column("Resource", style="blue")
        table.add_column("Uptime", style="dim")

        for n in neighbors:
            status = n["status"]
            style = "green" if status in ["UP", "AVAILABLE"] else "red"

            table.add_row(
                n["region"],
                n["type"],
                n["neighbor_ip"] or "-",
                str(n["asn"]),
                Text(status, style=style),
                n["name"] or n["resource_id"],
                str(n["uptime"]),
            )

        self.console.print(table)
        self.console.print(f"\n[dim]Total: {len(neighbors)} Neighbor(s)[/]")
