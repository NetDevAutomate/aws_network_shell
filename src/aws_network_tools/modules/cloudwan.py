"""Cloud WAN module"""

import json
import logging
from typing import Optional, Dict, List, Any
import os
import boto3
from rich.table import Table
from rich.tree import Tree
from rich.panel import Panel
from rich.text import Text
from thefuzz import fuzz

from ..core import Cache, BaseDisplay, BaseClient, ModuleInterface, Context

logger = logging.getLogger("aws_network_tools.cloudwan")

cache = Cache("cloudwan")


class CloudWANModule(ModuleInterface):
    @property
    def name(self) -> str:
        return "cloudwan"

    @property
    def commands(self) -> Dict[str, str]:
        return {"global-network": "Enter global network: global-network <#|name>"}

    @property
    def context_commands(self) -> Dict[str, List[str]]:
        return {
            "global-network": ["core-network"],
            "core-network": ["route-table"],
            "route-table": ["find-prefix", "find-prefix-fuzzy", "find-null-routes"],
        }

    @property
    def show_commands(self) -> Dict[str, List[str]]:
        return {
            None: ["global-networks"],
            "global-network": ["core-networks"],
            "core-network": [
                "policy-documents",
                "live-policy",
                "policy-document",
                "policy-diff",
                "route-tables",
                "routes",
                "blackhole-routes",
                "routing-policy-labels",
            ],
        }

    def execute(self, shell: Any, command: str, args: str):
        if command == "global-network":
            self._enter_global_network(shell, args)
        elif command == "core-network":
            self._enter_core_network(shell, args)

    def _enter_global_network(self, shell, args):
        if shell.ctx_type is not None:
            shell.console.print("[red]Use 'end' to return to top level first[/]")
            return
        ref = args.strip()
        if not ref:
            shell.console.print("[red]Usage: global-network <#|name>[/]")
            return

        # Accessing shell's cached fetch method for global networks
        # We need to expose this data or fetch it here.
        # For now, using the private method if available, or we'd move that logic here.
        gns = shell._get_global_networks()
        target = resolve_network(gns, ref)

        if not target:
            shell.console.print(f"[red]Global network '{ref}' not found[/]")
            return

        shell.context_stack = [
            Context("global-network", ref, target.get("name") or target["id"], target)
        ]
        shell._update_prompt()

    def _enter_core_network(self, shell, args):
        if shell.ctx_type != "global-network":
            shell.console.print("[red]Must be in global-network context[/]")
            return
        ref = args.strip()
        if not ref:
            shell.console.print("[red]Usage: core-network <#|name>[/]")
            return

        cns = shell.ctx.data.get("core_networks", [])
        target = resolve_network(cns, ref)

        if not target:
            shell.console.print(f"[red]Core network '{ref}' not found[/]")
            return

        shell.context_stack.append(
            Context("core-network", ref, target.get("name") or target["id"], target)
        )
        shell._update_prompt()


class CloudWANClient(BaseClient):
    def __init__(
        self,
        profile: Optional[str] = None,
        session: Optional[boto3.Session] = None,
        nm_region: Optional[str] = None,
    ):
        super().__init__(profile, session)
        self._nm = None
        # Use profile's region, env override, or fallback to us-west-2
        if nm_region:
            self._nm_region = nm_region
        elif os.getenv("AWS_NETWORK_MANAGER_REGION"):
            self._nm_region = os.getenv("AWS_NETWORK_MANAGER_REGION")
        else:
            # Try to get region from session/profile
            self._nm_region = self.session.region_name or "us-west-2"

    @property
    def nm(self):
        if self._nm is None:
            try:
                self._nm = self.client("networkmanager", region_name=self._nm_region)
            except Exception as e:
                logger.warning(
                    "Failed to create networkmanager client (region=%s): %s",
                    self._nm_region,
                    e,
                )
                self._nm = self.session.client(
                    "networkmanager", region_name=self._nm_region
                )
        return self._nm

    def _get_name(self, tags: list) -> Optional[str]:
        return next((t["Value"] for t in tags if t["Key"] == "Name"), None)

    def _get_policy(self, cn_id: str) -> Optional[dict]:
        try:
            versions = self.nm.list_core_network_policy_versions(CoreNetworkId=cn_id)
            live_version = None
            for v in versions.get("CoreNetworkPolicyVersions", []):
                if v.get("Alias") == "LIVE":
                    live_version = v["PolicyVersionId"]
                    break
            if not live_version:
                all_v = versions.get("CoreNetworkPolicyVersions", [])
                if all_v:
                    live_version = max(all_v, key=lambda x: x["PolicyVersionId"])[
                        "PolicyVersionId"
                    ]
            if not live_version:
                return None
            resp = self.nm.get_core_network_policy(
                CoreNetworkId=cn_id, PolicyVersionId=int(live_version)
            )
            return json.loads(resp["CoreNetworkPolicy"]["PolicyDocument"])
        except Exception:
            return None

    def list_policy_versions(self, cn_id: str) -> list[dict]:
        """List all policy versions for a core network"""
        try:
            resp = self.nm.list_core_network_policy_versions(CoreNetworkId=cn_id)
            return [
                {
                    "version": v["PolicyVersionId"],
                    "alias": v.get("Alias", ""),
                    "change_set_state": v.get("ChangeSetState", ""),
                    "created_at": str(v.get("CreatedAt", "")),
                }
                for v in resp.get("CoreNetworkPolicyVersions", [])
            ]
        except Exception:
            return []

    def get_policy_change_events(self, cn_id: str, max_results: int = 50) -> list[dict]:
        """Get policy change events (version changes, executions) for a core network"""
        events = []
        try:
            # Get policy versions with their change details
            resp = self.nm.list_core_network_policy_versions(CoreNetworkId=cn_id)
            versions = resp.get("CoreNetworkPolicyVersions", [])

            for v in versions[:max_results]:
                event = {
                    "version": v["PolicyVersionId"],
                    "alias": v.get("Alias", ""),
                    "change_set_state": v.get("ChangeSetState", ""),
                    "created_at": v.get("CreatedAt"),
                    "event_type": "policy_version",
                }
                events.append(event)

            # Get core network change events
            try:
                change_resp = self.nm.get_core_network_change_set(
                    CoreNetworkId=cn_id,
                    PolicyVersionId=versions[0]["PolicyVersionId"] if versions else 1,
                )
                for change in change_resp.get("CoreNetworkChanges", []):
                    events.append(
                        {
                            "version": versions[0]["PolicyVersionId"]
                            if versions
                            else 0,
                            "event_type": "change",
                            "action": change.get("Action", ""),
                            "identifier": change.get("Identifier", ""),
                            "change_type": change.get("Type", ""),
                            "created_at": None,
                        }
                    )
            except Exception:
                pass  # Change set may not exist for all versions

        except Exception:
            pass

        def _normalize_datetime(val):
            """Convert datetime objects to ISO strings for consistent sorting."""
            if val is None:
                return ""
            if hasattr(val, 'isoformat'):
                return val.isoformat()
            return str(val)

        return sorted(events, key=lambda x: _normalize_datetime(x.get("created_at")), reverse=True)

    def get_policy_document(
        self, cn_id: str, version: Optional[int] = None
    ) -> Optional[dict]:
        """Get a specific policy document (LIVE if version not specified)"""
        try:
            if version is None:
                versions = self.nm.list_core_network_policy_versions(
                    CoreNetworkId=cn_id
                )
                for v in versions.get("CoreNetworkPolicyVersions", []):
                    if v.get("Alias") == "LIVE":
                        version = v["PolicyVersionId"]
                        break
                # If no LIVE, get latest
                if version is None:
                    all_v = versions.get("CoreNetworkPolicyVersions", [])
                    if all_v:
                        version = max(all_v, key=lambda x: x["PolicyVersionId"])[
                            "PolicyVersionId"
                        ]
            if version is None:
                return None
            resp = self.nm.get_core_network_policy(
                CoreNetworkId=cn_id, PolicyVersionId=int(version)
            )
            return json.loads(resp["CoreNetworkPolicy"]["PolicyDocument"])
        except Exception as e:
            print(f"Error getting policy: {e}")
            return None

    def _get_routes(
        self, gn_id: str, cn_id: str, region: str, segment: str
    ) -> list[dict]:
        try:
            route_table_id = {
                "CoreNetworkSegmentEdge": {
                    "CoreNetworkId": cn_id,
                    "EdgeLocation": region,
                    "SegmentName": segment,
                }
            }
            resp = self.nm.get_network_routes(
                GlobalNetworkId=gn_id, RouteTableIdentifier=route_table_id
            )
            routes = []
            for r in resp.get("NetworkRoutes", []):
                prefix = (
                    r.get("DestinationCidrBlock") or r.get("Prefix") or r.get("CIDR")
                )
                if not prefix:
                    continue
                dest = r.get("Destinations", [{}])[0]
                target = (
                    dest.get("CoreNetworkAttachmentId")
                    or dest.get("TransitGatewayAttachmentId")
                    or dest.get("SegmentName")
                    or "unknown"
                )
                target_type = dest.get("ResourceType") or "attachment"
                routes.append(
                    {
                        "prefix": prefix,
                        "target": target,
                        "target_type": target_type,
                        "state": r.get("State", "active"),
                        "type": r.get("Type", "propagated"),
                    }
                )
            return routes
        except Exception:
            return []

    def _get_nfg_routes(
        self, gn_id: str, cn_id: str, region: str, nfg: str
    ) -> list[dict]:
        try:
            route_table_id = {
                "CoreNetworkNetworkFunctionGroup": {
                    "CoreNetworkId": cn_id,
                    "NetworkFunctionGroupName": nfg,
                    "EdgeLocation": region,
                }
            }
            resp = self.nm.get_network_routes(
                GlobalNetworkId=gn_id, RouteTableIdentifier=route_table_id
            )
            routes = []
            for r in resp.get("NetworkRoutes", []):
                prefix = r.get("DestinationCidrBlock") or r.get("Prefix")
                if not prefix:
                    continue
                dest = r.get("Destinations", [{}])[0]
                target = (
                    dest.get("CoreNetworkAttachmentId")
                    or dest.get("SegmentName")
                    or "unknown"
                )
                routes.append(
                    {
                        "prefix": prefix,
                        "target": target,
                        "target_type": dest.get("ResourceType", "attachment"),
                        "state": r.get("State", "active"),
                        "type": r.get("Type", "propagated"),
                    }
                )
            return routes
        except Exception:
            return []

    def list_attachments_with_labels(self, cn_id: str) -> list[dict]:
        """List all attachments for a core network with their routing policy labels"""
        try:
            attachments = []
            paginator = self.nm.get_paginator("list_attachments")

            for page in paginator.paginate(CoreNetworkId=cn_id):
                for att in page.get("Attachments", []):
                    attachment_id = att.get("AttachmentId")
                    attachment_type = att.get("AttachmentType", "Unknown")
                    state = att.get("State", "Unknown")
                    edge_location = att.get("EdgeLocation", "N/A")
                    segment_name = att.get("SegmentName", "N/A")

                    # Get routing policy label if present
                    routing_policy_label = att.get("RoutingPolicyLabel", "")

                    # Get resource ARN/ID for better identification
                    resource_arn = att.get("ResourceArn", "")

                    # Extract a friendly name from tags if available
                    tags = att.get("Tags", [])
                    name = self._get_name(tags) or attachment_id

                    attachments.append(
                        {
                            "id": attachment_id,
                            "name": name,
                            "type": attachment_type,
                            "state": state,
                            "segment": segment_name,
                            "edge_location": edge_location,
                            "routing_policy_label": routing_policy_label,
                            "resource_arn": resource_arn,
                        }
                    )

            return attachments
        except Exception as e:
            print(f"Error listing attachments: {e}")
            return []

    def list_connect_attachments(self, cn_id: str) -> list[dict]:
        """List Connect attachments (used for BGP peering) for a core network"""
        try:
            attachments = []
            paginator = self.nm.get_paginator("list_attachments")

            for page in paginator.paginate(
                CoreNetworkId=cn_id, AttachmentType="CONNECT"
            ):
                for att in page.get("Attachments", []):
                    attachment_id = att.get("AttachmentId")

                    # Get detailed Connect attachment info
                    try:
                        detail = self.nm.get_connect_attachment(
                            AttachmentId=attachment_id
                        )
                        connect_att = detail.get("ConnectAttachment", {})
                        attachment = connect_att.get("Attachment", {})
                        options = connect_att.get("Options", {})

                        tags = attachment.get("Tags", [])
                        name = self._get_name(tags) or attachment_id

                        attachments.append(
                            {
                                "id": attachment_id,
                                "name": name,
                                "state": attachment.get("State", ""),
                                "edge_location": attachment.get("EdgeLocation", ""),
                                "segment": attachment.get("SegmentName", ""),
                                "transport_attachment_id": connect_att.get(
                                    "TransportAttachmentId", ""
                                ),
                                "protocol": options.get("Protocol", "GRE"),
                                "resource_arn": attachment.get("ResourceArn", ""),
                            }
                        )
                    except Exception:
                        # Fallback to basic info
                        tags = att.get("Tags", [])
                        name = self._get_name(tags) or attachment_id
                        attachments.append(
                            {
                                "id": attachment_id,
                                "name": name,
                                "state": att.get("State", ""),
                                "edge_location": att.get("EdgeLocation", ""),
                                "segment": att.get("SegmentName", ""),
                                "transport_attachment_id": "",
                                "protocol": "GRE",
                                "resource_arn": att.get("ResourceArn", ""),
                            }
                        )

            return attachments
        except Exception as e:
            print(f"Error listing connect attachments: {e}")
            return []

    def list_connect_peers(self, cn_id: str) -> list[dict]:
        """List Connect peers (BGP sessions) for a core network"""
        try:
            peers = []
            paginator = self.nm.get_paginator("list_connect_peers")

            for page in paginator.paginate(CoreNetworkId=cn_id):
                for peer_summary in page.get("ConnectPeers", []):
                    peer_id = peer_summary.get("ConnectPeerId")

                    # Get detailed peer info
                    try:
                        detail = self.nm.get_connect_peer(ConnectPeerId=peer_id)
                        peer = detail.get("ConnectPeer", {})
                        config = peer.get("Configuration", {})
                        bgp_configs = config.get("BgpConfigurations", [])

                        tags = peer.get("Tags", [])
                        name = self._get_name(tags) or peer_id

                        # Extract BGP info
                        bgp_info = []
                        for bgp in bgp_configs:
                            bgp_info.append(
                                {
                                    "peer_asn": bgp.get("PeerAsn"),
                                    "peer_address": bgp.get("PeerAddress"),
                                    "core_network_asn": bgp.get("CoreNetworkAsn"),
                                    "core_network_address": bgp.get(
                                        "CoreNetworkAddress"
                                    ),
                                }
                            )

                        peers.append(
                            {
                                "id": peer_id,
                                "name": name,
                                "state": peer.get("State", ""),
                                "connect_attachment_id": peer.get(
                                    "ConnectAttachmentId", ""
                                ),
                                "edge_location": peer.get("EdgeLocation", ""),
                                "protocol": config.get("Protocol", "GRE"),
                                "core_network_address": config.get(
                                    "CoreNetworkAddress", ""
                                ),
                                "peer_address": config.get("PeerAddress", ""),
                                "inside_cidr_blocks": config.get(
                                    "InsideCidrBlocks", []
                                ),
                                "bgp_configurations": bgp_info,
                                "created_at": str(peer.get("CreatedAt", "")),
                            }
                        )
                    except Exception:
                        # Fallback to summary info
                        peers.append(
                            {
                                "id": peer_id,
                                "name": peer_id,
                                "state": peer_summary.get("ConnectPeerState", ""),
                                "connect_attachment_id": peer_summary.get(
                                    "ConnectAttachmentId", ""
                                ),
                                "edge_location": peer_summary.get("EdgeLocation", ""),
                                "protocol": "",
                                "core_network_address": peer_summary.get(
                                    "CoreNetworkAddress", ""
                                ),
                                "peer_address": peer_summary.get("PeerAddress", ""),
                                "inside_cidr_blocks": [],
                                "bgp_configurations": [],
                                "created_at": "",
                            }
                        )

            return peers
        except Exception as e:
            print(f"Error listing connect peers: {e}")
            return []

    def get_routing_information_base(
        self, cn_id: str, segment: str, edge_location: str
    ) -> list[dict]:
        """Get Route Information Base (RIB) for a segment/edge - shows BGP attributes before policy application"""
        try:
            routes = []
            paginator = self.nm.get_paginator("list_core_network_routing_information")

            for page in paginator.paginate(
                CoreNetworkId=cn_id, SegmentName=segment, EdgeLocation=edge_location
            ):
                for route in page.get("CoreNetworkRoutingInformation", []):
                    # Handle NextHop - can be dict or string
                    next_hop_raw = route.get("NextHop", "")
                    if isinstance(next_hop_raw, dict):
                        # Format as "ResourceType:ResourceId" for display
                        next_hop = f"{next_hop_raw.get('ResourceType', '')}:{next_hop_raw.get('ResourceId', '')}"
                    else:
                        next_hop = next_hop_raw
                    routes.append(
                        {
                            "prefix": route.get("DestinationCidrBlock", ""),
                            "next_hop": next_hop,
                            "next_hop_type": route.get("NextHopType", ""),
                            "next_hop_resource": route.get("NextHopResource", ""),
                            "local_preference": route.get("LocalPreference"),
                            "as_path": route.get("AsPath", []),
                            "med": route.get("Med"),
                            "communities": route.get("Communities", []),
                            "origin": route.get("Origin", ""),
                            "origin_type": route.get("OriginType", ""),
                            "edge_location": edge_location,
                            "segment": segment,
                        }
                    )

            return routes
        except Exception as e:
            # API may not be available or segment/edge doesn't exist
            print(f"Error getting RIB: {e}")
            return []

    def get_rib_for_core_network(self, cn_id: str, policy: dict) -> dict:
        """Get RIB for all segments and edge locations in a core network"""
        rib_data = {}

        # Extract regions and segments from policy
        regions = [
            e.get("location")
            for e in policy.get("core-network-configuration", {}).get(
                "edge-locations", []
            )
            if e.get("location")
        ]
        segments = [s.get("name") for s in policy.get("segments", []) if s.get("name")]

        for region in regions:
            for segment in segments:
                key = f"{segment}|{region}"
                routes = self.get_routing_information_base(cn_id, segment, region)
                if routes:
                    rib_data[key] = {
                        "segment": segment,
                        "edge_location": region,
                        "routes": routes,
                    }

        return rib_data

    def discover(self) -> list[dict]:
        core_networks = []
        try:
            gn_resp = self.nm.describe_global_networks()
            for gn in gn_resp.get("GlobalNetworks", []):
                if gn.get("State") != "AVAILABLE":
                    continue
                gn_id = gn["GlobalNetworkId"]
                gn_name = self._get_name(gn.get("Tags", [])) or gn_id

                cn_resp = self.nm.list_core_networks()
                for cn in cn_resp.get("CoreNetworks", []):
                    if (
                        cn.get("State") != "AVAILABLE"
                        or cn.get("GlobalNetworkId") != gn_id
                    ):
                        continue
                    cn_id = cn["CoreNetworkId"]
                    cn_name = cn.get("Description") or cn_id

                    policy = self._get_policy(cn_id)
                    if not policy:
                        continue

                    # Extract regions, segments, NFGs from policy
                    regions = [
                        e.get("location")
                        for e in policy.get("core-network-configuration", {}).get(
                            "edge-locations", []
                        )
                        if e.get("location")
                    ]
                    segments = [
                        s.get("name")
                        for s in policy.get("segments", [])
                        if s.get("name")
                    ]
                    nfgs = [
                        n.get("name")
                        for n in policy.get("network-function-groups", [])
                        if n.get("name")
                    ]

                    # Build route tables
                    route_tables = []
                    for region in regions:
                        for segment in segments:
                            routes = self._get_routes(gn_id, cn_id, region, segment)
                            if routes:
                                route_tables.append(
                                    {
                                        "id": f"{segment}|{region}",
                                        "name": segment,
                                        "region": region,
                                        "type": "segment",
                                        "routes": routes,
                                    }
                                )
                        for nfg in nfgs:
                            routes = self._get_nfg_routes(gn_id, cn_id, region, nfg)
                            if routes:
                                route_tables.append(
                                    {
                                        "id": f"NFG-{nfg}|{region}",
                                        "name": f"NFG-{nfg}",
                                        "region": region,
                                        "type": "nfg",
                                        "routes": routes,
                                    }
                                )

                    core_networks.append(
                        {
                            "id": cn_id,
                            "name": cn_name,
                            "global_network_id": gn_id,
                            "global_network_name": gn_name,
                            "regions": regions,
                            "segments": segments,
                            "nfgs": nfgs,
                            "route_tables": route_tables,
                            "policy": policy,
                        }
                    )
        except Exception:
            pass
        return core_networks


class CloudWANDisplay(BaseDisplay):
    def show_list(self, networks: list[dict]):
        if not networks:
            self.console.print("[yellow]No Cloud WAN Core Networks found[/]")
            return
        table = Table(
            title="Cloud WAN Core Networks", show_header=True, header_style="bold"
        )
        table.add_column("#", style="dim", justify="right")
        table.add_column("Name", style="green")
        table.add_column("ID", style="cyan")
        table.add_column("Global Network", style="yellow")
        table.add_column("Regions", style="white", justify="right")
        table.add_column("Segments", style="white", justify="right")
        table.add_column("Route Tables", style="white", justify="right")
        for i, cn in enumerate(networks, 1):
            table.add_row(
                str(i),
                cn["name"],
                cn["id"],
                cn.get("global_network_name", "N/A"),
                str(len(cn["regions"])),
                str(len(cn["segments"])),
                str(len(cn["route_tables"])),
            )
        self.console.print(table)
        self.console.print(f"\n[dim]Total: {len(networks)} Core Network(s)[/]")

    def show_detail(self, cn: dict):
        if not cn:
            self.console.print("[red]Core Network not found[/]")
            return
        tree = Tree(f"[bold blue]🌐 Core Network: {cn.get('name', cn.get('id', 'N/A'))}[/]")
        tree.add(f"[dim]ID: {cn.get('id', 'N/A')}[/]")
        tree.add(f"[dim]Global Network: {cn.get('global_network_name', 'N/A')}[/]")

        regions = cn.get("regions", [])
        if regions:
            reg_branch = tree.add("[yellow]Regions[/]")
            for r in regions:
                reg_branch.add(f"[green]{r}[/]")

        segments = cn.get("segments", [])
        if segments:
            seg_branch = tree.add("[magenta]Segments[/]")
            for s in segments:
                seg_branch.add(f"[white]{s}[/]")

        nfgs = cn.get("nfgs", [])
        if nfgs:
            nfg_branch = tree.add("[red]Network Function Groups[/]")
            for n in nfgs:
                nfg_branch.add(f"[white]{n}[/]")

        self.console.print(tree)
        self.console.print()

        route_tables = cn.get("route_tables", [])
        if route_tables:
            rt_table = Table(
                title="Route Tables", show_header=True, header_style="bold"
            )
            rt_table.add_column("#", style="dim", justify="right")
            rt_table.add_column("Segment/NFG", style="cyan")
            rt_table.add_column("Region", style="yellow")
            rt_table.add_column("Type", style="magenta")
            rt_table.add_column("Routes", style="white", justify="right")
            for i, rt in enumerate(route_tables, 1):
                rt_table.add_row(
                    str(i),
                    rt.get("name", ""),
                    rt.get("region", ""),
                    rt.get("type", ""),
                    str(len(rt.get("routes", []))),
                )
            self.console.print(rt_table)

    def show_prefixes(self, networks: list[dict]):
        for cn in networks:
            for rt in cn.get("route_tables", []):
                if not rt["routes"]:
                    continue
                title = f"[bold]{cn['name']}[/] → [cyan]{rt['region']}[/] → [magenta]{rt['name']}[/]"
                table = Table(title=title, show_header=True, header_style="bold")
                table.add_column("#", style="dim", justify="right")
                table.add_column("Prefix", style="green", no_wrap=True)
                table.add_column("Target", style="cyan")
                table.add_column("Type", style="yellow")
                table.add_column("State", style="white")
                table.add_column("Target Type", style="dim")
                for i, route in enumerate(rt["routes"], 1):
                    state_style = "green" if route["state"] == "active" else "red"
                    table.add_row(
                        str(i),
                        route["prefix"],
                        route["target"],
                        route["type"].upper(),
                        Text(route["state"], style=state_style),
                        route["target_type"],
                    )
                self.console.print(table)
                self.console.print()
        total = sum(
            len(rt["routes"]) for cn in networks for rt in cn.get("route_tables", [])
        )
        self.console.print(
            Panel(f"[bold green]Total Routes: {total}[/]", title="Summary")
        )

    def show_route_tables_list(self, cn: dict):
        """Show list of route tables for a core network"""
        rts = cn.get("route_tables", [])
        if not rts:
            self.console.print("[yellow]No route tables found[/]")
            return
        table = Table(
            title=f"Route Tables for [bold]{cn['name']}[/]",
            show_header=True,
            header_style="bold",
        )
        table.add_column("#", style="dim", justify="right")
        table.add_column("Region", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Routes", style="yellow", justify="right")
        for i, rt in enumerate(rts, 1):
            table.add_row(
                str(i),
                rt.get("region", ""),
                rt.get("name", ""),
                str(len(rt.get("routes", []))),
            )
        self.console.print(table)

    def show_policy_versions(self, cn: dict, versions: list[dict]):
        """Show list of policy versions"""
        if not versions:
            self.console.print("[yellow]No policy versions found[/]")
            return
        table = Table(
            title=f"Policy Versions for [bold]{cn['name']}[/]",
            show_header=True,
            header_style="bold",
        )
        table.add_column("#", style="dim", justify="right")
        table.add_column("Version", style="cyan", justify="right")
        table.add_column("Alias", style="green")
        table.add_column("State", style="yellow")
        table.add_column("Created", style="dim")
        for i, v in enumerate(versions, 1):
            alias_style = "bold green" if v["alias"] == "LIVE" else "dim"
            table.add_row(
                str(i),
                str(v["version"]),
                Text(v["alias"] or "-", style=alias_style),
                v["change_set_state"],
                v["created_at"][:19] if v["created_at"] else "",
            )
        self.console.print(table)

    def show_live_policy(self, cn: dict, policy: dict):
        """Show the LIVE policy document"""
        if not policy:
            self.console.print("[yellow]No LIVE policy document found[/]")
            return
        from rich.syntax import Syntax

        self.console.print(
            Panel(
                f"[bold]{cn['name']}[/] LIVE Policy Document", title="Cloud WAN Policy"
            )
        )
        self.console.print(
            Syntax(
                json.dumps(policy, indent=2), "json", theme="monokai", line_numbers=True
            )
        )

    def show_policy(self, cn: dict, policy: dict, version: str):
        """Show a specific policy document"""
        if not policy:
            self.console.print(f"[yellow]Policy version '{version}' not found[/]")
            return
        from rich.syntax import Syntax

        self.console.print(
            Panel(
                f"[bold]{cn['name']}[/] Policy Version {version}",
                title="Cloud WAN Policy",
            )
        )
        self.console.print(
            Syntax(
                json.dumps(policy, indent=2), "json", theme="monokai", line_numbers=True
            )
        )

    def show_policy_diff(
        self, cn: dict, policy1: dict, policy2: dict, label1: str, label2: str
    ):
        """Show side-by-side diff of two policy documents"""
        import difflib
        from rich.text import Text

        if not policy1 or not policy2:
            self.console.print("[red]Could not load one or both policies[/]")
            return

        # Convert to formatted JSON lines
        json1 = json.dumps(policy1, indent=2, sort_keys=True).splitlines()
        json2 = json.dumps(policy2, indent=2, sort_keys=True).splitlines()

        # Generate unified diff
        diff = list(
            difflib.unified_diff(
                json1, json2, fromfile=label1, tofile=label2, lineterm=""
            )
        )

        if not diff:
            self.console.print(
                f"[green]No differences between {label1} and {label2}[/]"
            )
            return

        self.console.print(
            Panel(
                f"[bold]{cn['name']}[/] Policy Diff: [cyan]{label1}[/] vs [magenta]{label2}[/]",
                title="Policy Comparison",
            )
        )

        # Build colored diff output
        diff_text = Text()
        for line in diff:
            if line.startswith("+++"):
                diff_text.append(line + "\n", style="bold magenta")
            elif line.startswith("---"):
                diff_text.append(line + "\n", style="bold cyan")
            elif line.startswith("@@"):
                diff_text.append(line + "\n", style="bold yellow")
            elif line.startswith("+"):
                diff_text.append(line + "\n", style="green")
            elif line.startswith("-"):
                diff_text.append(line + "\n", style="red")
            else:
                diff_text.append(line + "\n", style="dim")

        self.console.print(diff_text)

        # Summary
        added = sum(
            1 for line in diff if line.startswith("+") and not line.startswith("+++")
        )
        removed = sum(
            1 for line in diff if line.startswith("-") and not line.startswith("---")
        )
        self.console.print(
            f"\n[green]+{added} additions[/]  [red]-{removed} deletions[/]"
        )

    def show_routing_policy_labels(self, cn: dict, attachments: list[dict]):
        """Show all attachments with their routing policy labels"""
        if not attachments:
            self.console.print("[yellow]No attachments found[/]")
            return

        # Count attachments with labels
        with_labels = sum(1 for a in attachments if a.get("routing_policy_label"))

        table = Table(
            title=f"[bold]Routing Policy Labels for {cn['name']}[/]",
            show_header=True,
            header_style="bold",
        )
        table.add_column("#", style="dim", justify="right")
        table.add_column("Attachment Name", style="cyan")
        table.add_column("Attachment ID", style="white")
        table.add_column("Type", style="yellow")
        table.add_column("Segment", style="green")
        table.add_column("Edge Location", style="magenta")
        table.add_column("Routing Policy Label", style="bold blue")
        table.add_column("State", style="dim")

        for i, att in enumerate(attachments, 1):
            label = att.get("routing_policy_label", "")
            label_text = Text(
                label if label else "-", style="bold blue" if label else "dim"
            )
            state_style = "green" if att["state"] == "AVAILABLE" else "yellow"

            table.add_row(
                str(i),
                att["name"][:30],
                att["id"],
                att["type"],
                att["segment"],
                att["edge_location"],
                label_text,
                Text(att["state"], style=state_style),
            )

        self.console.print(table)
        self.console.print(
            f"\n[dim]Total: {len(attachments)} attachment(s) | "
            f"[bold blue]{with_labels}[/] with routing policy labels[/]"
        )

    def show_policy_change_events(self, cn: dict, events: list[dict]):
        """Show policy change events for a core network"""
        if not events:
            self.console.print("[yellow]No policy change events found[/]")
            return

        table = Table(
            title=f"[bold]Policy Change Events for {cn['name']}[/]",
            show_header=True,
            header_style="bold",
        )
        table.add_column("#", style="dim", justify="right")
        table.add_column("Version", style="cyan", justify="right")
        table.add_column("Type", style="yellow")
        table.add_column("Alias", style="green")
        table.add_column("State/Action", style="magenta")
        table.add_column("Details", style="white")
        table.add_column("Created", style="dim")

        for i, event in enumerate(events, 1):
            created = event.get("created_at")
            if created:
                created = (
                    created.strftime("%Y-%m-%d %H:%M")
                    if hasattr(created, "strftime")
                    else str(created)[:16]
                )

            if event.get("event_type") == "policy_version":
                alias_style = "bold green" if event.get("alias") == "LIVE" else "dim"
                table.add_row(
                    str(i),
                    str(event.get("version", "")),
                    "Policy Version",
                    Text(event.get("alias", "-") or "-", style=alias_style),
                    event.get("change_set_state", ""),
                    "",
                    created or "",
                )
            else:
                table.add_row(
                    str(i),
                    str(event.get("version", "")),
                    event.get("change_type", "Change"),
                    "-",
                    event.get("action", ""),
                    event.get("identifier", "")[:30],
                    created or "",
                )

        self.console.print(table)
        self.console.print(f"\n[dim]Total: {len(events)} event(s)[/]")

    def show_connect_attachments(self, cn: dict, attachments: list[dict]):
        """Show Connect attachments for BGP peering"""
        if not attachments:
            self.console.print("[yellow]No Connect attachments found[/]")
            return

        table = Table(
            title=f"[bold]Connect Attachments for {cn.get('name', 'Core Network')}[/]",
            show_header=True,
            header_style="bold",
        )
        table.add_column("#", style="dim", justify="right")
        table.add_column("Name", style="cyan")
        table.add_column("Attachment ID", style="white")
        table.add_column("Edge Location", style="yellow")
        table.add_column("Segment", style="green")
        table.add_column("Protocol", style="magenta")
        table.add_column("Transport Attachment", style="dim")
        table.add_column("State")

        for i, att in enumerate(attachments, 1):
            state = att.get("state", "")
            state_style = (
                "green"
                if state == "AVAILABLE"
                else ("yellow" if state in ["CREATING", "PENDING"] else "red")
            )

            table.add_row(
                str(i),
                att.get("name", "")[:25],
                att.get("id", ""),
                att.get("edge_location", ""),
                att.get("segment", ""),
                att.get("protocol", "GRE"),
                att.get("transport_attachment_id", "")[:20] or "-",
                Text(state, style=state_style),
            )

        self.console.print(table)
        self.console.print(f"\n[dim]Total: {len(attachments)} Connect attachment(s)[/]")

    def show_connect_peers(self, cn: dict, peers: list[dict]):
        """Show Connect peers (BGP sessions)"""
        if not peers:
            self.console.print("[yellow]No Connect peers found[/]")
            return

        table = Table(
            title=f"[bold]Connect Peers (BGP) for {cn.get('name', 'Core Network')}[/]",
            show_header=True,
            header_style="bold",
        )
        table.add_column("#", style="dim", justify="right")
        table.add_column("Name", style="cyan")
        table.add_column("Edge", style="yellow")
        table.add_column("Peer ASN", style="green", justify="right")
        table.add_column("Peer Address", style="white")
        table.add_column("Core Network Address", style="magenta")
        table.add_column("Inside CIDRs", style="dim")
        table.add_column("State")

        for i, peer in enumerate(peers, 1):
            state = peer.get("state", "")
            state_style = (
                "green"
                if state == "AVAILABLE"
                else ("yellow" if state in ["CREATING", "PENDING"] else "red")
            )

            # Get BGP ASN from configurations
            bgp_configs = peer.get("bgp_configurations", [])
            peer_asn = str(bgp_configs[0].get("peer_asn", "")) if bgp_configs else "-"

            inside_cidrs = ", ".join(peer.get("inside_cidr_blocks", [])[:2])
            if len(peer.get("inside_cidr_blocks", [])) > 2:
                inside_cidrs += "..."

            table.add_row(
                str(i),
                peer.get("name", "")[:20],
                peer.get("edge_location", ""),
                peer_asn,
                peer.get("peer_address", ""),
                peer.get("core_network_address", ""),
                inside_cidrs or "-",
                Text(state, style=state_style),
            )

        self.console.print(table)
        self.console.print(f"\n[dim]Total: {len(peers)} Connect peer(s)[/]")

        # Show detailed BGP info if available
        peers_with_bgp = [p for p in peers if p.get("bgp_configurations")]
        if peers_with_bgp:
            self.console.print("\n[bold]BGP Configuration Details:[/bold]")
            for peer in peers_with_bgp:
                self.console.print(f"\n  [cyan]{peer.get('name', peer.get('id'))}[/]:")
                for bgp in peer.get("bgp_configurations", []):
                    self.console.print(
                        f"    Peer ASN: [green]{bgp.get('peer_asn')}[/] → Core ASN: [magenta]{bgp.get('core_network_asn')}[/]"
                    )
                    self.console.print(
                        f"    Peer: {bgp.get('peer_address')} ↔ Core: {bgp.get('core_network_address')}"
                    )

    def show_rib(
        self,
        cn: dict,
        rib_data: dict,
        segment_filter: str = None,
        edge_filter: str = None,
    ):
        """Show Route Information Base (RIB) with BGP attributes"""
        if not rib_data:
            self.console.print(
                "[yellow]No RIB data found (requires policy version 2025.11+)[/]"
            )
            return

        total_routes = 0
        for key, data in sorted(rib_data.items()):
            segment = data["segment"]
            edge = data["edge_location"]
            routes = data["routes"]

            # Apply filters if specified
            if segment_filter and segment.lower() != segment_filter.lower():
                continue
            if edge_filter and edge.lower() != edge_filter.lower():
                continue

            if not routes:
                continue

            title = f"[bold]RIB: {cn.get('name', 'Core Network')}[/] → [cyan]{edge}[/] → [magenta]{segment}[/]"
            table = Table(title=title, show_header=True, header_style="bold")
            table.add_column("#", style="dim", justify="right")
            table.add_column("Prefix", style="green", no_wrap=True)
            table.add_column("Next Hop", style="cyan")
            table.add_column("LP", style="yellow", justify="right")
            table.add_column("AS Path", style="white")
            table.add_column("MED", style="magenta", justify="right")
            table.add_column("Communities", style="dim")
            table.add_column("Origin", style="blue")

            for i, route in enumerate(routes, 1):
                # Format AS path
                as_path = route.get("as_path", [])
                as_path_str = " ".join(str(asn) for asn in as_path[:5])
                if len(as_path) > 5:
                    as_path_str += "..."

                # Format communities
                communities = route.get("communities", [])
                comm_str = ",".join(communities[:2])
                if len(communities) > 2:
                    comm_str += "..."

                # Local preference
                lp = route.get("local_preference")
                lp_str = str(lp) if lp is not None else "-"

                # MED
                med = route.get("med")
                med_str = str(med) if med is not None else "-"

                table.add_row(
                    str(i),
                    route.get("prefix", ""),
                    str(route.get("next_hop", "") or route.get("next_hop_resource", "") or "")[:25],
                    lp_str,
                    as_path_str or "-",
                    med_str,
                    comm_str or "-",
                    route.get("origin_type", route.get("origin", ""))[:10],
                )

            self.console.print(table)
            self.console.print()
            total_routes += len(routes)

        self.console.print(f"[dim]Total: {total_routes} route(s) in RIB[/]")
        self.console.print(
            "[dim]Note: RIB shows routes BEFORE routing policies are applied[/]"
        )

    def show_blackhole_routes(self, networks: list[dict]):
        """Show all routes with BLACKHOLE or NULL state"""
        matches = []
        for cn in networks:
            for rt in cn.get("route_tables", []):
                for r in rt["routes"]:
                    state = r.get("state", "").upper()
                    target = r.get("target", "").lower()
                    if state == "BLACKHOLE" or target in [
                        "blackhole",
                        "null",
                        "unknown",
                    ]:
                        matches.append(
                            {
                                "prefix": r["prefix"],
                                "target": r["target"],
                                "state": r["state"],
                                "core_network": cn["name"],
                                "global_network": cn.get("global_network_name", ""),
                                "region": rt["region"],
                                "segment": rt["name"],
                            }
                        )
        if not matches:
            self.console.print("[green]No blackhole/null routes found[/]")
            return
        table = Table(
            title="[red]Blackhole/Null Routes[/]", show_header=True, header_style="bold"
        )
        table.add_column("#", style="dim", justify="right")
        table.add_column("Core Network", style="cyan")
        table.add_column("Region", style="yellow")
        table.add_column("Segment", style="green")
        table.add_column("Prefix", style="white", no_wrap=True)
        table.add_column("Target", style="dim")
        table.add_column("State", style="red")
        for i, m in enumerate(matches, 1):
            table.add_row(
                str(i),
                m["core_network"],
                m["region"],
                m["segment"],
                m["prefix"],
                m["target"],
                m["state"],
            )
        self.console.print(table)
        self.console.print(f"[red]Found {len(matches)} blackhole/null route(s)[/]")

    def show_route_table(self, cn: dict, rt_ref: str):
        rt = resolve_item(cn.get("route_tables", []), rt_ref, "name", "id")
        if not rt:
            self.console.print(f"[red]Route table '{rt_ref}' not found[/]")
            return
        title = f"[bold]{cn['name']}[/] → [cyan]{rt['region']}[/] → [magenta]{rt['name']}[/]"
        table = Table(title=title, show_header=True, header_style="bold")
        table.add_column("#", style="dim", justify="right")
        table.add_column("Prefix", style="green", no_wrap=True)
        table.add_column("Target", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("State", style="white")
        for i, route in enumerate(rt["routes"], 1):
            state_style = "green" if route["state"] == "active" else "red"
            table.add_row(
                str(i),
                route["prefix"],
                route["target"],
                route["type"].upper(),
                Text(route["state"], style=state_style),
            )
        self.console.print(table)

    def show_matches(self, matches: list[dict], query: str):
        if not matches:
            self.console.print(f"[yellow]No matches found for '{query}'[/]")
            return
        table = Table(
            title=f"Search Results for '[cyan]{query}[/]'",
            show_header=True,
            header_style="bold",
        )
        table.add_column("#", style="dim", justify="right")
        table.add_column("Score", style="yellow", justify="right")
        table.add_column("Prefix", style="green", no_wrap=True)
        table.add_column("Route Table", style="blue")
        table.add_column("Target", style="cyan")
        table.add_column("State", style="dim")
        for i, m in enumerate(matches, 1):
            state_style = "green" if m["state"] == "active" else "red"
            table.add_row(
                str(i),
                str(m["score"]),
                m["prefix"],
                m["route_table"],
                m["target"],
                Text(m["state"], style=state_style),
            )
        self.console.print(table)
        self.console.print(f"[dim]Found {len(matches)} matches[/]")


def resolve_item(
    items: list[dict], ref: str, name_key: str, id_key: str
) -> Optional[dict]:
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


def resolve_network(networks: list[dict], ref: str) -> Optional[dict]:
    return resolve_item(networks, ref, "name", "id")


def search_prefixes(
    networks: list[dict], query: str, min_score: int = 60, max_results: int = 50
) -> list[dict]:
    matches = []
    for cn in networks:
        for rt in cn.get("route_tables", []):
            for route in rt["routes"]:
                score = fuzz.partial_ratio(query.lower(), route["prefix"].lower())
                if query.lower() in route["prefix"].lower():
                    score = max(score, 90)
                if query.lower() == route["prefix"].lower():
                    score = 100
                if score >= min_score:
                    matches.append(
                        {
                            "prefix": route["prefix"],
                            "target": route["target"],
                            "state": route["state"],
                            "route_table": f"{cn['name']} → {rt['region']} → {rt['name']}",
                            "score": score,
                        }
                    )
    matches.sort(key=lambda m: (-m["score"], m["route_table"]))
    return matches[:max_results]
