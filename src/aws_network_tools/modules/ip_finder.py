"""Fast IP address finder - searches all regions in parallel."""

import concurrent.futures
from typing import Optional
import boto3


def find_ip(ip: str, profile: Optional[str] = None) -> Optional[dict]:
    """Find ENI by IP address across all regions."""
    session = boto3.Session(profile_name=profile) if profile else boto3.Session()
    config = boto3.session.Config(
        connect_timeout=5, read_timeout=10, retries={"max_attempts": 2}
    )

    # Get regions
    ec2 = session.client("ec2", region_name="us-east-1", config=config)
    regions = [
        r["RegionName"] for r in ec2.describe_regions(AllRegions=False)["Regions"]
    ]

    result = None

    def search_region(region: str) -> Optional[dict]:
        nonlocal result
        if result:  # Already found
            return None
        try:
            ec2 = session.client("ec2", region_name=region, config=config)
            # Check private IPs
            resp = ec2.describe_network_interfaces(
                Filters=[{"Name": "addresses.private-ip-address", "Values": [ip]}]
            )
            if resp.get("NetworkInterfaces"):
                return _extract_eni(resp["NetworkInterfaces"][0], region, ip, session)

            # Check public/elastic IPs
            resp = ec2.describe_addresses(
                Filters=[{"Name": "public-ip", "Values": [ip]}]
            )
            if resp.get("Addresses"):
                addr = resp["Addresses"][0]
                if addr.get("NetworkInterfaceId"):
                    eni_resp = ec2.describe_network_interfaces(
                        NetworkInterfaceIds=[addr["NetworkInterfaceId"]]
                    )
                    if eni_resp.get("NetworkInterfaces"):
                        return _extract_eni(
                            eni_resp["NetworkInterfaces"][0],
                            region,
                            ip,
                            session,
                            is_eip=True,
                        )
                return {
                    "region": region,
                    "ip": ip,
                    "resource_type": "Elastic IP",
                    "resource_id": addr.get("AllocationId"),
                }
        except Exception:
            pass
        return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as ex:
        futures = {ex.submit(search_region, r): r for r in regions}
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res:
                result = res
                # Cancel remaining
                for f in futures:
                    f.cancel()
                break

    return result


def _extract_eni(
    eni: dict, region: str, ip: str, session, is_eip: bool = False
) -> dict:
    """Extract ENI info and determine resource type."""
    result = {
        "region": region,
        "ip": ip,
        "eni_id": eni["NetworkInterfaceId"],
        "vpc_id": eni.get("VpcId"),
        "subnet_id": eni.get("SubnetId"),
        "extra": {},
    }

    interface_type = eni.get("InterfaceType", "")
    description = eni.get("Description", "")
    attachment = eni.get("Attachment", {})

    # EC2 Instance
    if attachment.get("InstanceId"):
        result["resource_type"] = "EC2 Instance"
        result["resource_id"] = attachment["InstanceId"]
        _add_ec2_details(result, region, attachment["InstanceId"], session)
        return result

    # Lambda
    if "lambda" in description.lower():
        result["resource_type"] = "Lambda"
        result["extra"]["Description"] = description
        return result

    # Load Balancer
    if "ELB" in description or interface_type == "network_load_balancer":
        result["resource_type"] = "Load Balancer"
        result["extra"]["Description"] = description
        return result

    # NAT Gateway
    if interface_type == "nat_gateway":
        result["resource_type"] = "NAT Gateway"
        _add_nat_details(result, region, eni["NetworkInterfaceId"], session)
        return result

    # VPC Endpoint
    if interface_type == "vpc_endpoint" or "vpce" in description.lower():
        result["resource_type"] = "VPC Endpoint"
        _add_vpce_details(result, region, eni["NetworkInterfaceId"], session)
        return result

    # RDS
    if "RDSNetworkInterface" in description:
        result["resource_type"] = "RDS"
        result["extra"]["Description"] = description
        return result

    # Transit Gateway
    if interface_type == "transit_gateway":
        result["resource_type"] = "Transit Gateway"
        return result

    result["resource_type"] = interface_type or "Unknown"
    result["extra"]["Description"] = description
    return result


def _add_ec2_details(result: dict, region: str, instance_id: str, session):
    try:
        ec2 = session.client("ec2", region_name=region)
        resp = ec2.describe_instances(InstanceIds=[instance_id])
        for res in resp.get("Reservations", []):
            for inst in res.get("Instances", []):
                result["extra"]["State"] = inst.get("State", {}).get("Name")
                result["extra"]["Type"] = inst.get("InstanceType")
                for tag in inst.get("Tags", []):
                    if tag["Key"] == "Name":
                        result["resource_name"] = tag["Value"]
    except Exception:
        pass


def _add_nat_details(result: dict, region: str, eni_id: str, session):
    try:
        ec2 = session.client("ec2", region_name=region)
        resp = ec2.describe_nat_gateways(
            Filters=[{"Name": "network-interface-id", "Values": [eni_id]}]
        )
        for nat in resp.get("NatGateways", []):
            result["resource_id"] = nat["NatGatewayId"]
            result["extra"]["State"] = nat.get("State")
            for tag in nat.get("Tags", []):
                if tag["Key"] == "Name":
                    result["resource_name"] = tag["Value"]
    except Exception:
        pass


def _add_vpce_details(result: dict, region: str, eni_id: str, session):
    try:
        ec2 = session.client("ec2", region_name=region)
        resp = ec2.describe_vpc_endpoints(
            Filters=[{"Name": "network-interface-id", "Values": [eni_id]}]
        )
        for vpce in resp.get("VpcEndpoints", []):
            result["resource_id"] = vpce["VpcEndpointId"]
            result["extra"]["Service"] = vpce.get("ServiceName")
            for tag in vpce.get("Tags", []):
                if tag["Key"] == "Name":
                    result["resource_name"] = tag["Value"]
    except Exception:
        pass
