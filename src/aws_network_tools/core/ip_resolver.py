"""IP Resolution Utility"""

import concurrent.futures
from typing import Optional, List
from .base import BaseClient


class IpResolver(BaseClient):
    def __init__(self, profile: Optional[str] = None):
        super().__init__(profile)

    def _check_region(self, ip: str, region: str) -> Optional[str]:
        try:
            ec2 = self.session.client("ec2", region_name=region)

            # Try private IP
            resp = ec2.describe_network_interfaces(
                Filters=[{"Name": "private-ip-address", "Values": [ip]}]
            )
            if resp["NetworkInterfaces"]:
                return resp["NetworkInterfaces"][0]["NetworkInterfaceId"]

            # Try public IP
            resp = ec2.describe_network_interfaces(
                Filters=[{"Name": "association.public-ip", "Values": [ip]}]
            )
            if resp["NetworkInterfaces"]:
                return resp["NetworkInterfaces"][0]["NetworkInterfaceId"]

        except Exception:
            pass
        return None

    def resolve_ip(self, ip: str, regions: List[str]) -> Optional[str]:
        """Resolve an IP address to an ENI ID across multiple regions in parallel"""
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=len(regions)
        ) as executor:
            future_to_region = {
                executor.submit(self._check_region, ip, r): r for r in regions
            }

            for future in concurrent.futures.as_completed(future_to_region):
                result = future.result()
                if result:
                    # Cancel other pending futures as we found it
                    for f in future_to_region:
                        f.cancel()
                    return result
        return None
