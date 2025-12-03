"""Staleness detection for network topology cache - PoC."""

from dataclasses import dataclass
from typing import Optional
import boto3

from ..core.cache import Cache


@dataclass
class ChangeMarkers:
    """Quick-check markers for cache staleness."""

    cwan_policy_version: Optional[int] = None
    cwan_attachment_count: int = 0
    tgw_count: dict[str, int] = None  # region -> count
    vpc_count: dict[str, int] = None  # region -> count

    def __post_init__(self):
        self.tgw_count = self.tgw_count or {}
        self.vpc_count = self.vpc_count or {}

    def to_dict(self) -> dict:
        return {
            "cwan_policy_version": self.cwan_policy_version,
            "cwan_attachment_count": self.cwan_attachment_count,
            "tgw_count": self.tgw_count,
            "vpc_count": self.vpc_count,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ChangeMarkers":
        return cls(
            cwan_policy_version=d.get("cwan_policy_version"),
            cwan_attachment_count=d.get("cwan_attachment_count", 0),
            tgw_count=d.get("tgw_count", {}),
            vpc_count=d.get("vpc_count", {}),
        )


class StalenessChecker:
    """Check if cached topology is stale without full rebuild."""

    MARKERS_CACHE = "topology_markers"

    def __init__(self, profile: Optional[str] = None):
        self.profile = profile
        self.session = (
            boto3.Session(profile_name=profile) if profile else boto3.Session()
        )
        self._markers_cache = Cache(self.MARKERS_CACHE)

    def _client(self, service: str, region: str = "us-east-1"):
        return self.session.client(service, region_name=region)

    def get_current_markers(self, regions: list[str] = None) -> ChangeMarkers:
        """Get current state markers (fast - few API calls)."""
        markers = ChangeMarkers()

        # 1. Cloud WAN policy version (1 API call)
        try:
            nm = self._client("networkmanager", "us-east-1")
            networks = nm.list_core_networks().get("CoreNetworks", [])
            if networks:
                cn_id = networks[0]["CoreNetworkId"]
                policy = nm.get_core_network_policy(CoreNetworkId=cn_id)
                markers.cwan_policy_version = policy.get("CoreNetworkPolicy", {}).get(
                    "PolicyVersionId"
                )

                # Attachment count (1 more call)
                attachments = nm.list_attachments(CoreNetworkId=cn_id)
                markers.cwan_attachment_count = len(attachments.get("Attachments", []))
        except Exception:
            pass

        # 2. TGW and VPC counts per region (2 calls per region, but fast)
        if regions:
            for region in regions[:5]:  # Limit to 5 regions for speed
                try:
                    ec2 = self._client("ec2", region)
                    tgws = ec2.describe_transit_gateways().get("TransitGateways", [])
                    markers.tgw_count[region] = len(tgws)

                    vpcs = ec2.describe_vpcs().get("Vpcs", [])
                    markers.vpc_count[region] = len(vpcs)
                except Exception:
                    pass

        return markers

    def save_markers(self, markers: ChangeMarkers):
        """Save markers alongside topology cache."""
        self._markers_cache.set(markers.to_dict())

    def get_saved_markers(self) -> Optional[ChangeMarkers]:
        """Get previously saved markers."""
        data = self._markers_cache.get(
            ignore_expiry=True
        )  # Markers don't expire separately
        if data:
            return ChangeMarkers.from_dict(data)
        return None

    def is_stale(self, regions: list[str] = None) -> tuple[bool, str]:
        """
        Quick check if cache is likely stale.
        Returns (is_stale, reason).
        """
        saved = self.get_saved_markers()
        if not saved:
            return True, "No markers saved"

        current = self.get_current_markers(regions)

        # Check Cloud WAN policy version
        if (
            current.cwan_policy_version is not None
            and saved.cwan_policy_version is not None
            and current.cwan_policy_version != saved.cwan_policy_version
        ):
            return (
                True,
                f"Cloud WAN policy changed: {saved.cwan_policy_version} → {current.cwan_policy_version}",
            )

        # Check attachment count (only if both have values)
        if (
            current.cwan_attachment_count > 0
            and saved.cwan_attachment_count > 0
            and current.cwan_attachment_count != saved.cwan_attachment_count
        ):
            return (
                True,
                f"Attachment count changed: {saved.cwan_attachment_count} → {current.cwan_attachment_count}",
            )

        # Check TGW counts (only for regions we checked before)
        for region, count in current.tgw_count.items():
            saved_count = saved.tgw_count.get(region)
            if saved_count is not None and saved_count != count:
                return True, f"TGW count changed in {region}: {saved_count} → {count}"

        # Check VPC counts (only for regions we checked before)
        for region, count in current.vpc_count.items():
            saved_count = saved.vpc_count.get(region)
            if saved_count is not None and saved_count != count:
                return True, f"VPC count changed in {region}: {saved_count} → {count}"

        return False, "No changes detected"


# Quick test
if __name__ == "__main__":
    import sys

    profile = sys.argv[1] if len(sys.argv) > 1 else None

    checker = StalenessChecker(profile=profile)

    print("Getting current markers...")
    markers = checker.get_current_markers(regions=["eu-west-1", "eu-west-2"])
    print(f"  Policy version: {markers.cwan_policy_version}")
    print(f"  Attachments: {markers.cwan_attachment_count}")
    print(f"  TGWs: {markers.tgw_count}")
    print(f"  VPCs: {markers.vpc_count}")

    print("\nChecking staleness...")
    is_stale, reason = checker.is_stale(regions=["eu-west-1", "eu-west-2"])
    print(f"  Stale: {is_stale}")
    print(f"  Reason: {reason}")

    if "--save" in sys.argv:
        print("\nSaving markers...")
        checker.save_markers(markers)
        print("  Done")
