"""Data Format Adapter - transforms fixture data to module expected format.

Design (per Kimi K2 + Nova Premier):
- Simple format registry with transformation functions
- AWS validation (ARN format, region consistency, ID patterns)
- Extensible for all AWS resource types

Purpose:
Mock fixture data structure != Module expected format
This adapter bridges the gap transparently.
"""

import re
from typing import Any, Callable


class DataFormatAdapter:
    """Transform AWS fixture data to module-expected formats.

    Usage:
        adapter = DataFormatAdapter()
        transformed_vpc = adapter.transform('vpc', VPC_FIXTURES['vpc-123'])
        assert transformed_vpc['id'] == 'vpc-123'
    """

    def __init__(self):
        """Initialize adapter with format registry."""
        self.FORMAT_REGISTRY: dict[str, Callable] = {
            'vpc': self._transform_vpc,
            'tgw': self._transform_tgw,
            'cloudwan': self._transform_cloudwan,
            'ec2': self._transform_ec2,
            'elb': self._transform_elb,
        }

    def transform(self, resource_type: str, fixture_data: dict[str, Any]) -> dict[str, Any]:
        """Transform fixture data to module format.

        Args:
            resource_type: Type of AWS resource (vpc, tgw, cloudwan, etc.)
            fixture_data: Raw fixture data from fixtures module

        Returns:
            Transformed data matching module expectations

        Raises:
            ValueError: If resource_type not in registry
        """
        if resource_type not in self.FORMAT_REGISTRY:
            raise ValueError(f"No transformer for resource type: {resource_type}")

        transformer = self.FORMAT_REGISTRY[resource_type]
        return transformer(fixture_data)

    def transform_batch(self, resource_type: str, fixtures: list[dict]) -> list[dict]:
        """Transform multiple fixtures at once.

        Args:
            resource_type: Type of AWS resource
            fixtures: List of fixture data dicts

        Returns:
            List of transformed dicts
        """
        return [self.transform(resource_type, fixture) for fixture in fixtures]

    # =========================================================================
    # Transformation Functions
    # =========================================================================

    def _transform_vpc(self, fixture: dict[str, Any]) -> dict[str, Any]:
        """Transform VPC fixture to module format.

        Module expects: {id, name, cidr, cidrs, region, state}
        Fixture has: {VpcId, CidrBlock, CidrBlockAssociationSet, Tags, State}
        """
        return {
            'id': fixture['VpcId'],
            'name': self._get_tag_value(fixture, 'Name', default=fixture['VpcId']),
            'cidr': fixture['CidrBlock'],
            'cidrs': [
                assoc['CidrBlock']
                for assoc in fixture.get('CidrBlockAssociationSet', [])
            ],
            'region': self._derive_region_from_id(fixture['VpcId']),
            'state': fixture['State'],
        }

    def _transform_tgw(self, fixture: dict[str, Any]) -> dict[str, Any]:
        """Transform Transit Gateway fixture to module format."""
        return {
            'id': fixture['TransitGatewayId'],
            'name': self._get_tag_value(fixture, 'Name', default=fixture['TransitGatewayId']),
            'region': self._derive_region_from_id(fixture['TransitGatewayId']),
            'state': fixture['State'],
            'route_tables': [],
            'attachments': [],
        }

    def _transform_cloudwan(self, fixture: dict[str, Any]) -> dict[str, Any]:
        """Transform CloudWAN Core Network fixture to module format.

        Module expects: {id, name, arn, global_network_id, state, regions, segments}
        """
        return {
            'id': fixture['CoreNetworkId'],
            'name': self._get_tag_value(fixture, 'Name', default=fixture['CoreNetworkId']),
            'arn': fixture['CoreNetworkArn'],
            'global_network_id': fixture['GlobalNetworkId'],
            'state': fixture['State'],
            'regions': [edge['EdgeLocation'] for edge in fixture.get('Edges', [])],
            'segments': fixture.get('Segments', []),
            'route_tables': [],
            'policy': None,
            'core_networks': [],
        }

    def _transform_ec2(self, fixture: dict[str, Any]) -> dict[str, Any]:
        """Transform EC2 instance fixture to module format."""
        return {
            'id': fixture['InstanceId'],
            'name': self._get_tag_value(fixture, 'Name', default=fixture['InstanceId']),
            'type': fixture['InstanceType'],
            'state': fixture['State']['Name'],
            'az': fixture['Placement']['AvailabilityZone'],
            'region': fixture['Placement']['AvailabilityZone'][:-1],  # Remove AZ letter
            'vpc_id': fixture['VpcId'],
            'subnet_id': fixture['SubnetId'],
            'private_ip': fixture['PrivateIpAddress'],
        }

    def _transform_elb(self, fixture: dict[str, Any]) -> dict[str, Any]:
        """Transform ELB fixture to module format (per Nova Premier)."""
        return {
            'arn': fixture['LoadBalancerArn'],
            'name': fixture['LoadBalancerName'],
            'type': fixture['Type'],
            'scheme': fixture['Scheme'],
            'state': fixture['State']['Code'],
            'vpc_id': fixture['VpcId'],
            'dns_name': fixture['DNSName'],
            'region': self._extract_region_from_arn(fixture['LoadBalancerArn']),
        }

    # =========================================================================
    # Helper Functions
    # =========================================================================

    def _get_tag_value(
        self, resource: dict, key: str, default: str = ''
    ) -> str:
        """Extract tag value from AWS Tags list."""
        tags = resource.get('Tags', [])
        for tag in tags:
            if tag.get('Key') == key:
                return tag.get('Value', default)
        return default

    def _derive_region_from_id(self, resource_id: str) -> str:
        """Derive region from resource ID pattern.

        FIXTURE COMPATIBILITY ONLY: Real AWS IDs are random hex.
        Uses naming convention: *prod* → eu-west-1, *stag* → us-east-1, *dev* → ap-southeast-2

        NOTE (Nova Premier feedback): Phase 2 should use explicit region field in fixtures
        instead of this pattern matching approach.
        """
        if 'prod' in resource_id:
            return 'eu-west-1'
        elif 'stag' in resource_id:
            return 'us-east-1'
        elif 'dev' in resource_id:
            return 'ap-southeast-2'
        return 'us-east-1'  # Default

    def _extract_region_from_arn(self, arn: str) -> str:
        """Extract region from AWS ARN.

        ARN format: arn:aws:service:region:account:resource
        """
        parts = arn.split(':')
        return parts[3] if len(parts) > 3 else 'us-east-1'

    # =========================================================================
    # Validation Functions (per Nova Premier)
    # =========================================================================

    def validate_vpc_id(self, vpc_id: str) -> bool:
        """Validate VPC ID format: vpc-[0-9a-f]{17}."""
        return bool(re.match(r'^vpc-[0-9a-f]{17}$', vpc_id))

    def validate_arn(self, arn: str) -> bool:
        """Validate AWS ARN format (supports standard, GovCloud, China).

        Per Nova Premier: Comprehensive ARN validation including all partitions.
        """
        return bool(re.match(
            r'^arn:(aws|aws-us-gov|aws-cn):[a-zA-Z0-9-]+:[a-zA-Z0-9-]*:\d{12}:[a-zA-Z0-9-_/:.]+$',
            arn
        ))

    def validate_region(self, region: str) -> bool:
        """Validate region is valid AWS region."""
        AWS_REGIONS = [
            'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
            'eu-west-1', 'eu-west-2', 'eu-central-1',
            'ap-southeast-1', 'ap-southeast-2', 'ap-northeast-1',
        ]
        return region in AWS_REGIONS
