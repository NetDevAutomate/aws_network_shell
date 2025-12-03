"""Network topology discovery and caching."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field, asdict
from typing import Optional
import boto3

from ..core.cache import Cache
from .staleness import StalenessChecker


@dataclass
class NetworkTopology:
    """Cached network topology."""

    account_id: str
    regions: list[str] = field(default_factory=list)

    # Cloud WAN
    global_networks: list[dict] = field(default_factory=list)
    core_networks: list[dict] = field(default_factory=list)
    cwan_attachments: list[dict] = field(default_factory=list)
    cwan_policy: dict = field(default_factory=dict)

    # Transit Gateways by region
    tgws: dict[str, list[dict]] = field(default_factory=dict)
    tgw_route_tables: dict[str, list[dict]] = field(default_factory=dict)

    # VPCs by region
    vpcs: dict[str, list[dict]] = field(default_factory=dict)

    # Route tables: subnet_id -> {id, name, routes}
    route_tables: dict[str, dict] = field(default_factory=dict)

    # ENI index: ip -> {eni_id, vpc_id, subnet_id, region}
    eni_index: dict[str, dict] = field(default_factory=dict)


class TopologyDiscovery:
    """Discover and cache AWS network topology."""

    CACHE_NAMESPACE = "topology"

    def __init__(self, profile: Optional[str] = None, on_status=None):
        self.profile = profile
        self.session = (
            boto3.Session(profile_name=profile) if profile else boto3.Session()
        )
        self._executor = ThreadPoolExecutor(max_workers=20)
        self._cache = Cache(self.CACHE_NAMESPACE)
        self._on_status = on_status
        self._staleness = StalenessChecker(profile=profile)

    def _client(self, service: str, region: str = "us-east-1"):
        return self.session.client(service, region_name=region)

    def _status(self, msg: str):
        if self._on_status:
            self._on_status(msg)

    def get_cached(self, check_staleness: bool = True) -> Optional[NetworkTopology]:
        """Get topology from cache if valid and not stale."""
        account_id = self._get_account_id()
        data = self._cache.get(current_account=account_id)
        if not data:
            return None

        topology = NetworkTopology(**data)

        # Quick staleness check using saved markers (not new regions)
        if check_staleness:
            self._status("Checking for changes...")
            saved_markers = self._staleness.get_saved_markers()
            if saved_markers:
                # Use regions from saved markers, not topology
                check_regions = list(saved_markers.tgw_count.keys())[:5]
                is_stale, reason = self._staleness.is_stale(regions=check_regions)
                if is_stale:
                    self._status(f"Cache stale: {reason}")
                    return None

        return topology

    def clear_cache(self):
        """Clear the topology cache."""
        self._cache.clear()

    def _get_account_id(self) -> str:
        sts = self._client("sts")
        return sts.get_caller_identity()["Account"]

    async def discover(self, regions: list[str] = None) -> NetworkTopology:
        """Discover full network topology."""
        loop = asyncio.get_event_loop()
        account_id = await loop.run_in_executor(self._executor, self._get_account_id)

        # Get regions
        self._status("Getting regions...")
        if not regions:
            ec2 = self._client("ec2", "us-east-1")
            resp = await loop.run_in_executor(
                self._executor, lambda: ec2.describe_regions(AllRegions=False)
            )
            regions = [r["RegionName"] for r in resp["Regions"]]

        topology = NetworkTopology(account_id=account_id, regions=regions)

        # Discover in parallel
        await asyncio.gather(
            self._discover_cloudwan(topology),
            self._discover_tgws(topology, regions),
            self._discover_vpcs(topology, regions),
        )

        # Build ENI index from VPCs
        self._status("Building ENI index...")
        await self._build_eni_index(topology, regions)

        # Cache it
        self._status("Caching topology...")
        self._cache.set(asdict(topology), account_id=account_id)

        # Save staleness markers
        markers = self._staleness.get_current_markers(regions=regions[:5])
        self._staleness.save_markers(markers)

        return topology

    async def _discover_cloudwan(self, topology: NetworkTopology):
        """Discover Cloud WAN resources."""
        loop = asyncio.get_event_loop()
        nm = self._client("networkmanager", "us-east-1")

        def fetch():
            self._status("Discovering Cloud WAN...")
            # Global networks
            gn_resp = nm.describe_global_networks()
            topology.global_networks = gn_resp.get("GlobalNetworks", [])

            # Core networks
            cn_resp = nm.list_core_networks()
            topology.core_networks = cn_resp.get("CoreNetworks", [])

            if topology.core_networks:
                cn_id = topology.core_networks[0]["CoreNetworkId"]

                # Policy
                import json

                policy_resp = nm.get_core_network_policy(CoreNetworkId=cn_id)
                policy_doc = policy_resp.get("CoreNetworkPolicy", {}).get(
                    "PolicyDocument", "{}"
                )
                topology.cwan_policy = (
                    json.loads(policy_doc)
                    if isinstance(policy_doc, str)
                    else policy_doc
                )

                # Attachments
                self._status("Getting Cloud WAN attachments...")
                paginator = nm.get_paginator("list_attachments")
                for page in paginator.paginate(CoreNetworkId=cn_id):
                    topology.cwan_attachments.extend(page.get("Attachments", []))

        await loop.run_in_executor(self._executor, fetch)

    async def _discover_tgws(self, topology: NetworkTopology, regions: list[str]):
        """Discover Transit Gateways in all regions."""
        loop = asyncio.get_event_loop()

        async def fetch_region(region: str):
            def _fetch():
                ec2 = self._client("ec2", region)
                tgw_resp = ec2.describe_transit_gateways()
                tgws = tgw_resp.get("TransitGateways", [])
                if tgws:
                    topology.tgws[region] = tgws
                    # Get route tables for each TGW
                    for tgw in tgws:
                        rt_resp = ec2.describe_transit_gateway_route_tables(
                            Filters=[
                                {
                                    "Name": "transit-gateway-id",
                                    "Values": [tgw["TransitGatewayId"]],
                                }
                            ]
                        )
                        topology.tgw_route_tables[tgw["TransitGatewayId"]] = (
                            rt_resp.get("TransitGatewayRouteTables", [])
                        )

            return await loop.run_in_executor(self._executor, _fetch)

        self._status("Discovering Transit Gateways...")
        await asyncio.gather(*[fetch_region(r) for r in regions])

    async def _discover_vpcs(self, topology: NetworkTopology, regions: list[str]):
        """Discover VPCs and route tables in all regions."""
        loop = asyncio.get_event_loop()

        async def fetch_region(region: str):
            def _fetch():
                ec2 = self._client("ec2", region)
                vpc_resp = ec2.describe_vpcs()
                vpcs = vpc_resp.get("Vpcs", [])
                if vpcs:
                    topology.vpcs[region] = vpcs
                    # Get route tables for this region
                    rt_resp = ec2.describe_route_tables(
                        Filters=[
                            {"Name": "vpc-id", "Values": [v["VpcId"] for v in vpcs]}
                        ]
                    )
                    for rt in rt_resp.get("RouteTables", []):
                        name = next(
                            (
                                t["Value"]
                                for t in rt.get("Tags", [])
                                if t["Key"] == "Name"
                            ),
                            "",
                        )
                        routes = []
                        for r in rt.get("Routes", []):
                            target = (
                                r.get("GatewayId")
                                or r.get("NatGatewayId")
                                or r.get("TransitGatewayId")
                                or r.get("NetworkInterfaceId")
                                or "local"
                            )
                            routes.append(
                                {
                                    "destination": r.get("DestinationCidrBlock", ""),
                                    "target": target if target != "local" else "local",
                                    "core_network_arn": r.get("CoreNetworkArn"),
                                    "state": r.get("State", "active"),
                                }
                            )
                        rt_data = {
                            "id": rt["RouteTableId"],
                            "name": name,
                            "routes": routes,
                            "vpc_id": rt["VpcId"],
                        }
                        # Index by subnet associations
                        for assoc in rt.get("Associations", []):
                            if assoc.get("SubnetId"):
                                topology.route_tables[assoc["SubnetId"]] = rt_data
                            if assoc.get("Main"):
                                # Store main RT under vpc_id for fallback
                                topology.route_tables[f"main:{rt['VpcId']}"] = rt_data

            return await loop.run_in_executor(self._executor, _fetch)

        self._status("Discovering VPCs and route tables...")
        await asyncio.gather(*[fetch_region(r) for r in regions])

    async def _build_eni_index(self, topology: NetworkTopology, regions: list[str]):
        """Build IP -> ENI index for fast lookups."""
        loop = asyncio.get_event_loop()

        async def fetch_region(region: str):
            def _fetch():
                ec2 = self._client("ec2", region)
                paginator = ec2.get_paginator("describe_network_interfaces")
                for page in paginator.paginate():
                    for eni in page.get("NetworkInterfaces", []):
                        for addr in eni.get("PrivateIpAddresses", []):
                            ip = addr.get("PrivateIpAddress")
                            if ip:
                                topology.eni_index[ip] = {
                                    "eni_id": eni["NetworkInterfaceId"],
                                    "vpc_id": eni.get("VpcId"),
                                    "subnet_id": eni.get("SubnetId"),
                                    "region": region,
                                    "security_groups": [
                                        g["GroupId"] for g in eni.get("Groups", [])
                                    ],
                                }

            return await loop.run_in_executor(self._executor, _fetch)

        await asyncio.gather(*[fetch_region(r) for r in regions])
