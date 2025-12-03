"""Deterministic AWS Network Traceroute Engine."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from ipaddress import ip_network, ip_address
from typing import Optional
import boto3

from .models import Hop, TraceResult
from .topology import TopologyDiscovery, NetworkTopology


@dataclass
class ENIInfo:
    """Resolved ENI information."""

    eni_id: str
    ip: str
    vpc_id: str
    subnet_id: str
    region: str
    security_groups: list[str]


class AWSTraceroute:
    """Deterministic AWS network path tracer."""

    def __init__(
        self,
        profile: Optional[str] = None,
        on_hop=None,
        on_status=None,
        no_cache=False,
        refresh_cache=False,
        skip_stale_check=False,
    ):
        self.profile = profile
        self.session = (
            boto3.Session(profile_name=profile) if profile else boto3.Session()
        )
        self._executor = ThreadPoolExecutor(max_workers=10)
        self._on_hop = on_hop
        self._on_status = on_status
        self._no_cache = no_cache
        self._refresh_cache = refresh_cache
        self._skip_stale_check = skip_stale_check
        self._topology: Optional[NetworkTopology] = None
        self._discovery = TopologyDiscovery(profile=profile, on_status=on_status)

    def _emit(self, hop: Hop):
        if self._on_hop:
            self._on_hop(hop)

    def _status(self, msg: str):
        if self._on_status:
            self._on_status(msg)

    def _client(self, service: str, region: str):
        return self.session.client(service, region_name=region)

    async def _ensure_topology(self):
        """Load or discover topology."""
        if self._topology:
            return

        if self._refresh_cache:
            self._discovery.clear_cache()

        if not self._no_cache:
            check_staleness = not self._skip_stale_check
            self._topology = self._discovery.get_cached(check_staleness=check_staleness)
            if self._topology:
                self._status("Using cached topology")
                return

        self._status("Discovering network topology (this may take a minute)...")
        self._topology = await self._discovery.discover()

    async def trace(self, src_ip: str, dst_ip: str) -> TraceResult:
        """Trace network path between two IPs."""
        result = TraceResult(src_ip=src_ip, dst_ip=dst_ip, reachable=False)
        hop_seq = 0

        # Load topology
        await self._ensure_topology()

        # Step 1: Find source and destination ENIs from index
        src_eni = self._find_eni_cached(src_ip)
        dst_eni = self._find_eni_cached(dst_ip)

        if not src_eni:
            result.blocked_reason = f"Source IP {src_ip} not found in topology"
            return result
        if not dst_eni:
            result.blocked_reason = f"Destination IP {dst_ip} not found in topology"
            return result

        # Add source hop
        hop_seq += 1
        hop = Hop(
            hop_seq,
            "eni",
            src_eni.eni_id,
            f"src:{src_ip}",
            src_eni.region,
            {"vpc_id": src_eni.vpc_id, "subnet_id": src_eni.subnet_id},
        )
        result.hops.append(hop)
        self._emit(hop)

        # Step 2: Get source route table (from cache or API)
        src_rt = self._get_route_table_cached(src_eni.subnet_id, src_eni.vpc_id)
        if not src_rt:
            src_rt = await self._get_subnet_route_table(
                src_eni.region, src_eni.vpc_id, src_eni.subnet_id
            )
        hop_seq += 1
        hop = Hop(
            hop_seq, "route_table", src_rt["id"], src_rt.get("name", ""), src_eni.region
        )
        result.hops.append(hop)
        self._emit(hop)

        # Step 3: Find matching route
        route = self._find_best_route(src_rt["routes"], dst_ip)
        if not route:
            result.blocked_reason = (
                f"No route to {dst_ip} in route table {src_rt['id']}"
            )
            result.blocked_at = result.hops[-1]
            return result

        # Step 4: Determine next hop type
        target = route.get("target")

        # Same VPC - direct routing
        if target == "local" and src_eni.vpc_id == dst_eni.vpc_id:
            hop_seq += 1
            hop = Hop(
                hop_seq, "destination", dst_eni.eni_id, f"dst:{dst_ip}", dst_eni.region
            )
            result.hops.append(hop)
            self._emit(hop)
            result.reachable = True
            return result

        # Cloud WAN route
        if route.get("core_network_arn"):
            result = await self._trace_via_cloudwan(result, hop_seq, src_eni, dst_eni)
            return result

        # TGW route
        if target and target.startswith("tgw-"):
            result = await self._trace_via_tgw(
                result, hop_seq, src_eni, dst_eni, target
            )
            return result

        result.blocked_reason = f"Unsupported route target: {target}"
        return result

    def _find_eni_cached(self, ip: str) -> Optional[ENIInfo]:
        """Find ENI from cached topology, fallback to API if not found."""
        if self._topology:
            eni_data = self._topology.eni_index.get(ip)
            if eni_data:
                return ENIInfo(
                    eni_id=eni_data["eni_id"],
                    ip=ip,
                    vpc_id=eni_data["vpc_id"],
                    subnet_id=eni_data["subnet_id"],
                    region=eni_data["region"],
                    security_groups=eni_data.get("security_groups", []),
                )

        # Fallback: search via API (IP might be new)
        self._status(f"IP {ip} not in cache, searching...")
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor() as pool:
            return pool.submit(asyncio.run, self._find_eni_api(ip)).result()

    async def _find_eni_api(self, ip: str) -> Optional[ENIInfo]:
        """Find ENI via API calls (fallback for uncached IPs)."""
        loop = asyncio.get_event_loop()

        # Try cached regions first
        regions = self._topology.regions if self._topology else []
        if not regions:
            ec2 = self._client("ec2", "us-east-1")
            resp = await loop.run_in_executor(
                self._executor, lambda: ec2.describe_regions(AllRegions=False)
            )
            regions = [r["RegionName"] for r in resp["Regions"]]

        # Priority regions first
        priority = ["eu-west-1", "eu-west-2", "us-east-1", "us-west-2"]
        ordered = [r for r in priority if r in regions] + [
            r for r in regions if r not in priority
        ]

        for region in ordered:
            result = await loop.run_in_executor(
                self._executor, self._find_eni_in_region, ip, region
            )
            if result:
                # Add to cache for next time
                if self._topology:
                    self._topology.eni_index[ip] = {
                        "eni_id": result.eni_id,
                        "vpc_id": result.vpc_id,
                        "subnet_id": result.subnet_id,
                        "region": result.region,
                        "security_groups": result.security_groups,
                    }
                return result
        return None

    def _find_eni_in_region(self, ip: str, region: str) -> Optional[ENIInfo]:
        """Check if IP exists in a specific region."""
        try:
            ec2 = self._client("ec2", region)
            resp = ec2.describe_network_interfaces(
                Filters=[{"Name": "addresses.private-ip-address", "Values": [ip]}]
            )
            if resp.get("NetworkInterfaces"):
                eni = resp["NetworkInterfaces"][0]
                return ENIInfo(
                    eni_id=eni["NetworkInterfaceId"],
                    ip=ip,
                    vpc_id=eni["VpcId"],
                    subnet_id=eni["SubnetId"],
                    region=region,
                    security_groups=[g["GroupId"] for g in eni.get("Groups", [])],
                )
        except Exception:
            pass
        return None

    def _get_route_table_cached(self, subnet_id: str, vpc_id: str) -> Optional[dict]:
        """Get route table from cached topology."""
        if not self._topology:
            return None
        # Try subnet-specific first, then main RT for VPC
        return self._topology.route_tables.get(
            subnet_id
        ) or self._topology.route_tables.get(f"main:{vpc_id}")

    def _get_segment_for_vpc(self, vpc_id: str, region: str) -> Optional[str]:
        """Find segment name for a VPC from cached attachments."""
        for att in self._topology.cwan_attachments:
            if (
                att.get("ResourceArn", "").endswith(vpc_id)
                and att.get("EdgeLocation") == region
            ):
                return att.get("SegmentName")
        return None

    def _get_nfg_for_vpc(self, vpc_id: str, region: str) -> Optional[str]:
        """Find NFG name for a VPC from cached attachments."""
        for att in self._topology.cwan_attachments:
            if (
                att.get("ResourceArn", "").endswith(vpc_id)
                and att.get("EdgeLocation") == region
            ):
                return att.get("NetworkFunctionGroupName")
        return None

    def _get_send_via_nfg(self, src_segment: str, dst_segment: str) -> Optional[str]:
        """Check if traffic between segments goes via an NFG."""
        for action in self._topology.cwan_policy.get("segment-actions", []):
            if (
                action.get("action") == "send-via"
                and action.get("segment") == src_segment
            ):
                when_sent_to = action.get("when-sent-to", {}).get("segments", [])
                if when_sent_to == "*" or dst_segment in when_sent_to:
                    nfgs = action.get("via", {}).get("network-function-groups", [])
                    return nfgs[0] if nfgs else None
        return None

    async def _trace_via_cloudwan(
        self, result: TraceResult, hop_seq: int, src_eni: ENIInfo, dst_eni: ENIInfo
    ) -> TraceResult:
        """Trace path through Cloud WAN."""
        src_segment = self._get_segment_for_vpc(src_eni.vpc_id, src_eni.region)
        dst_segment = self._get_segment_for_vpc(dst_eni.vpc_id, dst_eni.region)

        if not src_segment:
            result.blocked_reason = (
                f"Source VPC {src_eni.vpc_id} not attached to Cloud WAN"
            )
            return result

        hop_seq += 1
        hop = Hop(
            hop_seq,
            "cloud_wan_segment",
            src_segment,
            f"segment:{src_segment}",
            src_eni.region,
        )
        result.hops.append(hop)
        self._emit(hop)

        # Check for send-via NFG
        nfg = self._get_send_via_nfg(src_segment, dst_segment)
        if nfg:
            hop_seq += 1
            hop = Hop(hop_seq, "nfg", nfg, f"inspection:{nfg}", src_eni.region)
            result.hops.append(hop)
            self._emit(hop)

            # Find the firewall attachment for this NFG
            for att in self._topology.cwan_attachments:
                if (
                    att.get("NetworkFunctionGroupName") == nfg
                    and att.get("EdgeLocation") == src_eni.region
                ):
                    hop_seq += 1
                    fw_name = next(
                        (t["Value"] for t in att.get("Tags", []) if t["Key"] == "Name"),
                        "firewall",
                    )
                    fw_vpc = att.get("ResourceArn", "").split("/")[-1]
                    hop = Hop(
                        hop_seq,
                        "firewall",
                        fw_vpc,
                        fw_name,
                        att.get("EdgeLocation", ""),
                        {"attachment_id": att["AttachmentId"]},
                    )
                    result.hops.append(hop)
                    self._emit(hop)

        # Cross-region?
        if src_eni.region != dst_eni.region:
            hop_seq += 1
            hop = Hop(
                hop_seq,
                "cloud_wan_segment",
                dst_segment or "unknown",
                f"segment:{dst_segment}@{dst_eni.region}",
                dst_eni.region,
            )
            result.hops.append(hop)
            self._emit(hop)

        # Destination
        hop_seq += 1
        hop = Hop(
            hop_seq,
            "destination",
            dst_eni.eni_id,
            f"dst:{result.dst_ip}",
            dst_eni.region,
            {"vpc_id": dst_eni.vpc_id, "segment": dst_segment},
        )
        result.hops.append(hop)
        self._emit(hop)

        result.reachable = True
        return result

    async def _trace_via_tgw(
        self,
        result: TraceResult,
        hop_seq: int,
        src_eni: ENIInfo,
        dst_eni: ENIInfo,
        tgw_id: str,
    ) -> TraceResult:
        """Trace path through Transit Gateway."""
        hop_seq += 1
        hop = Hop(hop_seq, "tgw", tgw_id, "transit-gateway", src_eni.region)
        result.hops.append(hop)
        self._emit(hop)

        hop_seq += 1
        hop = Hop(
            hop_seq,
            "destination",
            dst_eni.eni_id,
            f"dst:{result.dst_ip}",
            dst_eni.region,
        )
        result.hops.append(hop)
        self._emit(hop)
        result.reachable = True
        return result

    async def _get_subnet_route_table(
        self, region: str, vpc_id: str, subnet_id: str
    ) -> dict:
        """Get route table for a subnet."""
        loop = asyncio.get_event_loop()
        ec2 = self._client("ec2", region)

        def fetch():
            resp = ec2.describe_route_tables(
                Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
            )
            main_rt = None
            for rt in resp["RouteTables"]:
                for assoc in rt.get("Associations", []):
                    if assoc.get("SubnetId") == subnet_id:
                        return self._parse_route_table(rt)
                    if assoc.get("Main"):
                        main_rt = rt
            return (
                self._parse_route_table(main_rt)
                if main_rt
                else {"id": "unknown", "routes": []}
            )

        return await loop.run_in_executor(self._executor, fetch)

    def _parse_route_table(self, rt: dict) -> dict:
        """Parse route table into simplified format."""
        name = next((t["Value"] for t in rt.get("Tags", []) if t["Key"] == "Name"), "")
        routes = []
        for r in rt.get("Routes", []):
            target = (
                r.get("GatewayId")
                or r.get("NatGatewayId")
                or r.get("TransitGatewayId")
                or r.get("NetworkInterfaceId")
                or "local"
            )
            dest = (
                r.get("DestinationCidrBlock") or r.get("DestinationIpv6CidrBlock") or ""
            )
            routes.append(
                {
                    "destination": dest,
                    "target": target if target != "local" else "local",
                    "core_network_arn": r.get("CoreNetworkArn"),
                    "state": r.get("State", "active"),
                }
            )
        return {"id": rt["RouteTableId"], "name": name, "routes": routes}

    def _find_best_route(self, routes: list[dict], dst_ip: str) -> Optional[dict]:
        """Find most specific matching route (longest prefix match)."""
        dst = ip_address(dst_ip)
        best_match = None
        best_prefix_len = -1

        for route in routes:
            dest = route.get("destination", "")
            if not dest or route.get("state") == "blackhole":
                continue
            try:
                network = ip_network(dest, strict=False)
                if dst in network and network.prefixlen > best_prefix_len:
                    best_match = route
                    best_prefix_len = network.prefixlen
            except ValueError:
                continue
        return best_match
