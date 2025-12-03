"""EC2 Instances module."""

import concurrent.futures
import logging
from typing import Optional
import boto3

from ..core import BaseClient

logger = logging.getLogger("aws_network_tools.ec2")


class EC2Client(BaseClient):
    def __init__(
        self, profile: Optional[str] = None, session: Optional[boto3.Session] = None
    ):
        super().__init__(profile, session)

    def get_regions(self) -> list[str]:
        try:
            ec2 = self.client(
                "ec2", region_name=self.session.region_name or "us-east-1"
            )
            return [
                r["RegionName"]
                for r in ec2.describe_regions(AllRegions=False)["Regions"]
            ]
        except Exception as e:
            logger.warning(
                "describe_regions failed (region=%s): %s", self.session.region_name, e
            )
            return [self.session.region_name] if self.session.region_name else []

    def _get_name(self, tags: list) -> Optional[str]:
        return next((t["Value"] for t in tags if t["Key"] == "Name"), None)

    def _scan_region(self, region: str) -> list[dict]:
        instances = []
        try:
            ec2 = self.client("ec2", region_name=region)
            paginator = ec2.get_paginator("describe_instances")
            for page in paginator.paginate():
                for res in page.get("Reservations", []):
                    for i in res.get("Instances", []):
                        tags = i.get("Tags", [])
                        instances.append(
                            {
                                "id": i["InstanceId"],
                                "name": self._get_name(tags),
                                "type": i.get("InstanceType", ""),
                                "state": i.get("State", {}).get("Name", ""),
                                "az": i.get("Placement", {}).get(
                                    "AvailabilityZone", ""
                                ),
                                "region": region,
                                "private_ip": i.get("PrivateIpAddress", ""),
                                "public_ip": i.get("PublicIpAddress", ""),
                                "vpc_id": i.get("VpcId", ""),
                                "subnet_id": i.get("SubnetId", ""),
                            }
                        )
        except Exception as e:
            logger.warning("describe_instances failed (region=%s): %s", region, e)
        return instances

    def discover(self, regions: Optional[list[str]] = None) -> list[dict]:
        regions = regions or self.get_regions()
        all_instances = []
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=getattr(self, "max_workers", 10)
        ) as ex:
            for result in ex.map(self._scan_region, regions):
                all_instances.extend(result)
        return sorted(all_instances, key=lambda x: (x["region"], x["name"] or x["id"]))

    def get_instance_detail(self, instance_id: str, region: str) -> dict:
        ec2 = self.client("ec2", region_name=region)
        resp = ec2.describe_instances(InstanceIds=[instance_id])
        if not resp.get("Reservations") or not resp["Reservations"][0].get("Instances"):
            return {}

        i = resp["Reservations"][0]["Instances"][0]
        tags = i.get("Tags", [])

        # Get ENIs
        # ENI IDs processed below
        enis = []
        subnet_ids = set()
        for eni in i.get("NetworkInterfaces", []):
            subnet_ids.add(eni.get("SubnetId"))
            enis.append(
                {
                    "id": eni["NetworkInterfaceId"],
                    "subnet_id": eni.get("SubnetId", ""),
                    "private_ip": eni.get("PrivateIpAddress", ""),
                    "public_ip": eni.get("Association", {}).get("PublicIp", ""),
                    "sg_ids": [g["GroupId"] for g in eni.get("Groups", [])],
                }
            )

        # Get security groups with rules
        sg_ids = list({sg["GroupId"] for sg in i.get("SecurityGroups", [])})
        security_groups = []
        if sg_ids:
            sg_resp = ec2.describe_security_groups(GroupIds=sg_ids)
            for sg in sg_resp.get("SecurityGroups", []):
                ingress = []
                for r in sg.get("IpPermissions", []):
                    proto = r.get("IpProtocol", "all")
                    ports = (
                        f"{r.get('FromPort', 'all')}-{r.get('ToPort', 'all')}"
                        if r.get("FromPort")
                        else "all"
                    )
                    for ip in r.get("IpRanges", []):
                        ingress.append(
                            {
                                "proto": proto,
                                "ports": ports,
                                "source": ip.get("CidrIp", ""),
                            }
                        )
                    for grp in r.get("UserIdGroupPairs", []):
                        ingress.append(
                            {
                                "proto": proto,
                                "ports": ports,
                                "source": grp.get("GroupId", ""),
                            }
                        )
                    for pl in r.get("PrefixListIds", []):
                        ingress.append(
                            {
                                "proto": proto,
                                "ports": ports,
                                "source": pl.get("PrefixListId", ""),
                            }
                        )
                egress = []
                for r in sg.get("IpPermissionsEgress", []):
                    proto = r.get("IpProtocol", "all")
                    ports = (
                        f"{r.get('FromPort', 'all')}-{r.get('ToPort', 'all')}"
                        if r.get("FromPort")
                        else "all"
                    )
                    for ip in r.get("IpRanges", []):
                        egress.append(
                            {
                                "proto": proto,
                                "ports": ports,
                                "dest": ip.get("CidrIp", ""),
                            }
                        )
                    for grp in r.get("UserIdGroupPairs", []):
                        egress.append(
                            {
                                "proto": proto,
                                "ports": ports,
                                "dest": grp.get("GroupId", ""),
                            }
                        )
                    for pl in r.get("PrefixListIds", []):
                        egress.append(
                            {
                                "proto": proto,
                                "ports": ports,
                                "dest": pl.get("PrefixListId", ""),
                            }
                        )
                security_groups.append(
                    {
                        "id": sg["GroupId"],
                        "name": sg["GroupName"],
                        "ingress": ingress,
                        "egress": egress,
                    }
                )

        # Get route tables for subnets
        route_tables = []
        if subnet_ids:
            rt_resp = ec2.describe_route_tables(
                Filters=[{"Name": "association.subnet-id", "Values": list(subnet_ids)}]
            )
            # Also get main route table for VPC
            if i.get("VpcId"):
                main_rt = ec2.describe_route_tables(
                    Filters=[
                        {"Name": "vpc-id", "Values": [i["VpcId"]]},
                        {"Name": "association.main", "Values": ["true"]},
                    ]
                )
                rt_resp["RouteTables"].extend(main_rt.get("RouteTables", []))

            seen = set()
            for rt in rt_resp.get("RouteTables", []):
                if rt["RouteTableId"] in seen:
                    continue
                seen.add(rt["RouteTableId"])
                routes = [
                    {
                        "dest": r.get("DestinationCidrBlock")
                        or r.get("DestinationPrefixListId", ""),
                        "target": r.get("GatewayId")
                        or r.get("NatGatewayId")
                        or r.get("TransitGatewayId")
                        or r.get("NetworkInterfaceId")
                        or "local",
                        "state": r.get("State", "active"),
                    }
                    for r in rt.get("Routes", [])
                ]
                route_tables.append(
                    {
                        "id": rt["RouteTableId"],
                        "name": self._get_name(rt.get("Tags", [])),
                        "routes": routes,
                    }
                )

        # Get subnet details
        subnets = []
        if subnet_ids:
            sub_resp = ec2.describe_subnets(SubnetIds=list(subnet_ids))
            for s in sub_resp.get("Subnets", []):
                subnets.append(
                    {
                        "id": s["SubnetId"],
                        "name": self._get_name(s.get("Tags", [])),
                        "cidr": s.get("CidrBlock", ""),
                        "az": s.get("AvailabilityZone", ""),
                    }
                )

        return {
            "id": instance_id,
            "name": self._get_name(tags),
            "region": region,
            "type": i.get("InstanceType", ""),
            "state": i.get("State", {}).get("Name", ""),
            "az": i.get("Placement", {}).get("AvailabilityZone", ""),
            "private_ip": i.get("PrivateIpAddress", ""),
            "public_ip": i.get("PublicIpAddress", ""),
            "vpc_id": i.get("VpcId", ""),
            "key_name": i.get("KeyName", ""),
            "launch_time": str(i.get("LaunchTime", "")),
            "ami_id": i.get("ImageId", ""),
            "enis": enis,
            "security_groups": security_groups,
            "subnets": subnets,
            "route_tables": route_tables,
            "tags": {t["Key"]: t["Value"] for t in tags if t["Key"] != "Name"},
        }
