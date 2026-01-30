"""Fixture Generator - Helper script for creating new AWS resource fixtures.

This script helps generate new fixtures by:
1. Fetching real AWS API responses (if credentials available)
2. Providing templates based on existing fixtures
3. Validating fixture structure against module expectations

Usage:
    python tests/fixtures/fixture_generator.py --resource nat-gateway --count 3
    python tests/fixtures/fixture_generator.py --from-api vpc --vpc-id vpc-xxx
    python tests/fixtures/fixture_generator.py --template ec2-instance
"""

import json
import sys
from typing import Any, Optional
from pathlib import Path

# Template registry for common resource types
FIXTURE_TEMPLATES = {
    "vpc": {
        "VpcId": "vpc-0example1234567890",
        "CidrBlock": "10.0.0.0/16",
        "CidrBlockAssociationSet": [
            {
                "AssociationId": "vpc-cidr-assoc-example",
                "CidrBlock": "10.0.0.0/16",
                "CidrBlockState": {"State": "associated"},
            }
        ],
        "State": "available",
        "IsDefault": False,
        "DhcpOptionsId": "dopt-example12345",
        "InstanceTenancy": "default",
        "OwnerId": "123456789012",
        "Tags": [
            {"Key": "Name", "Value": "example-vpc"},
            {"Key": "Environment", "Value": "production"},
        ],
        "EnableDnsHostnames": True,
        "EnableDnsSupport": True,
    },
    "subnet": {
        "SubnetId": "subnet-0example123456789",
        "VpcId": "vpc-0example1234567890",
        "CidrBlock": "10.0.1.0/24",
        "AvailabilityZone": "us-east-1a",
        "AvailabilityZoneId": "use1-az1",
        "State": "available",
        "MapPublicIpOnLaunch": False,
        "DefaultForAz": False,
        "AvailableIpAddressCount": 251,
        "Tags": [{"Key": "Name", "Value": "example-subnet"}],
    },
    "security-group": {
        "GroupId": "sg-0example123456789",
        "GroupName": "example-sg",
        "Description": "Example security group",
        "VpcId": "vpc-0example1234567890",
        "IpPermissions": [
            {
                "IpProtocol": "tcp",
                "FromPort": 443,
                "ToPort": 443,
                "IpRanges": [{"CidrIp": "0.0.0.0/0", "Description": "HTTPS"}],
            }
        ],
        "IpPermissionsEgress": [
            {
                "IpProtocol": "-1",
                "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
            }
        ],
        "Tags": [{"Key": "Name", "Value": "example-sg"}],
    },
    "nat-gateway": {
        "NatGatewayId": "nat-0example12345678",
        "State": "available",
        "SubnetId": "subnet-0example123456789",
        "VpcId": "vpc-0example1234567890",
        "CreateTime": "2024-01-20T10:00:00+00:00",
        "ConnectivityType": "public",
        "NatGatewayAddresses": [
            {
                "AllocationId": "eipalloc-0example1234",
                "NetworkInterfaceId": "eni-0example123456789",
                "PrivateIp": "10.0.1.100",
                "PublicIp": "52.31.200.10",
                "AssociationId": "eipassoc-0example123",
                "IsPrimary": True,
                "Status": "succeeded",
            }
        ],
        "Tags": [{"Key": "Name", "Value": "example-nat"}],
    },
    "internet-gateway": {
        "InternetGatewayId": "igw-0example123456789",
        "Attachments": [{"VpcId": "vpc-0example1234567890", "State": "available"}],
        "OwnerId": "123456789012",
        "Tags": [{"Key": "Name", "Value": "example-igw"}],
    },
    "elastic-ip": {
        "AllocationId": "eipalloc-0example1234",
        "PublicIp": "52.31.200.10",
        "Domain": "vpc",
        "NetworkInterfaceId": "eni-0example123456789",
        "PrivateIpAddress": "10.0.1.100",
        "AssociationId": "eipassoc-0example123",
        "NetworkInterfaceOwnerId": "123456789012",
        "Tags": [{"Key": "Name", "Value": "example-eip"}],
    },
}


class FixtureGenerator:
    """Helper class for generating AWS resource fixtures."""

    def __init__(self):
        self.fixtures_dir = Path(__file__).parent
        self.existing_fixtures = self._load_existing_fixtures()

    def _load_existing_fixtures(self) -> dict[str, Any]:
        """Load existing fixtures to extract IDs for cross-references."""
        fixtures = {}
        try:
            from . import (
                VPC_FIXTURES,
                SUBNET_FIXTURES,
                SECURITY_GROUP_FIXTURES,
                TGW_FIXTURES,
                CLOUDWAN_FIXTURES,
            )

            fixtures["vpcs"] = list(VPC_FIXTURES.keys())
            fixtures["subnets"] = list(SUBNET_FIXTURES.keys())
            fixtures["security_groups"] = list(SECURITY_GROUP_FIXTURES.keys())
            fixtures["tgws"] = list(TGW_FIXTURES.keys())
            fixtures["core_networks"] = list(CLOUDWAN_FIXTURES.keys())
        except ImportError:
            pass
        return fixtures

    def generate_from_template(
        self, resource_type: str, count: int = 1, **kwargs
    ) -> list[dict[str, Any]]:
        """Generate fixtures from template.

        Args:
            resource_type: Type of resource (vpc, subnet, nat-gateway, etc.)
            count: Number of fixtures to generate
            **kwargs: Override values (vpc_id, cidr, name, etc.)

        Returns:
            List of fixture dictionaries
        """
        template = FIXTURE_TEMPLATES.get(resource_type)
        if not template:
            print(f"❌ No template for resource type: {resource_type}")
            print(f"Available templates: {', '.join(FIXTURE_TEMPLATES.keys())}")
            return []

        fixtures = []
        for i in range(count):
            fixture = json.loads(json.dumps(template))  # Deep copy
            # TODO: Customize IDs, increment counters, apply kwargs
            fixtures.append(fixture)

        return fixtures

    def fetch_from_aws(self, resource_type: str, resource_id: str) -> Optional[dict]:
        """Fetch real AWS resource and convert to fixture format.

        Args:
            resource_type: AWS resource type (vpc, subnet, nat-gateway, etc.)
            resource_id: AWS resource ID

        Returns:
            Fixture dictionary or None if fetch fails
        """
        try:
            import boto3

            session = boto3.Session()
            region = session.region_name or "us-east-1"
            ec2 = session.client("ec2", region_name=region)

            # Map resource types to AWS API calls
            api_calls = {
                "vpc": lambda: ec2.describe_vpcs(VpcIds=[resource_id])["Vpcs"][0],
                "subnet": lambda: ec2.describe_subnets(SubnetIds=[resource_id])[
                    "Subnets"
                ][0],
                "nat-gateway": lambda: ec2.describe_nat_gateways(
                    NatGatewayIds=[resource_id]
                )["NatGateways"][0],
                "internet-gateway": lambda: ec2.describe_internet_gateways(
                    InternetGatewayIds=[resource_id]
                )["InternetGateways"][0],
                "security-group": lambda: ec2.describe_security_groups(
                    GroupIds=[resource_id]
                )["SecurityGroups"][0],
            }

            fetch_func = api_calls.get(resource_type)
            if not fetch_func:
                print(f"❌ No API mapping for: {resource_type}")
                return None

            return fetch_func()

        except ImportError:
            print("❌ boto3 not available. Install with: pip install boto3")
            return None
        except Exception as e:
            print(f"❌ Error fetching from AWS: {e}")
            return None

    def sanitize_fixture(self, raw_data: dict) -> dict:
        """Sanitize AWS API response for use as fixture.

        Removes sensitive data, converts datetime to ISO strings, etc.
        """
        # Convert datetime objects to ISO strings
        sanitized = json.loads(
            json.dumps(raw_data, default=str, indent=2)
        )  # Handles datetime

        # Remove or mask sensitive fields
        sensitive_fields = [
            "CustomerGatewayConfiguration",
            "PreSharedKey",
            "AuthKey",
            "Password",
        ]
        for field in sensitive_fields:
            if field in sanitized:
                sanitized[field] = "**hidden**"

        return sanitized

    def validate_fixture(self, fixture: dict, resource_type: str) -> list[str]:
        """Validate fixture has required fields.

        Returns:
            List of validation errors (empty if valid)
        """
        required_fields = {
            "vpc": ["VpcId", "CidrBlock", "State"],
            "subnet": ["SubnetId", "VpcId", "CidrBlock", "AvailabilityZone"],
            "nat-gateway": ["NatGatewayId", "State", "SubnetId", "VpcId"],
            "internet-gateway": ["InternetGatewayId"],
            "security-group": ["GroupId", "GroupName", "VpcId"],
        }

        errors = []
        required = required_fields.get(resource_type, [])
        for field in required:
            if field not in fixture:
                errors.append(f"Missing required field: {field}")

        return errors

    def generate_helper_functions(self, resource_type: str, id_field: str) -> str:
        """Generate helper function code for a fixture file.

        Args:
            resource_type: Type of resource (nat_gateway, prefix_list, etc.)
            id_field: Primary ID field name (NatGatewayId, PrefixListId, etc.)

        Returns:
            Python code string for helper functions
        """
        fixture_name = f"{resource_type.upper()}_FIXTURES"
        get_by_id_func = f"get_{resource_type}_by_id"

        code = f'''
# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def {get_by_id_func}({resource_type}_id: str) -> dict[str, Any] | None:
    """Get {resource_type} fixture by ID."""
    return {fixture_name}.get({resource_type}_id)


def get_{resource_type}s_by_vpc(vpc_id: str) -> list[dict[str, Any]]:
    """Get all {resource_type}s in a VPC."""
    return [
        resource for resource in {fixture_name}.values()
        if resource.get("VpcId") == vpc_id
    ]


def get_{resource_type}s_by_state(state: str) -> list[dict[str, Any]]:
    """Get all {resource_type}s with specific state."""
    return [
        resource for resource in {fixture_name}.values()
        if resource.get("State") == state
    ]
'''
        return code

    def create_fixture_file_template(
        self, resource_type: str, resource_name: str
    ) -> str:
        """Generate complete fixture file template.

        Args:
            resource_type: Technical type (nat_gateway, prefix_list, etc.)
            resource_name: Display name (NAT Gateway, Managed Prefix List)

        Returns:
            Complete Python file content as string
        """
        fixture_name = f"{resource_type.upper()}_FIXTURES"

        template = f'''"""Realistic {resource_name} mock data fixtures.

Architecture description:
- [Describe the architecture and scenarios]
- [List environments: Production, Staging, Development]
- [List regions: eu-west-1, us-east-1, ap-southeast-2]

Each fixture includes:
- [Key attributes]
- [Relationships to other resources]
- [Realistic configurations]
"""

from typing import Any

# =============================================================================
# {resource_name.upper()} FIXTURES
# =============================================================================

{fixture_name}: dict[str, dict[str, Any]] = {{
    # Production {resource_name} - eu-west-1
    "resource-id-prod": {{
        # Add fixture data here
        "Tags": [
            {{"Key": "Name", "Value": "production-resource"}},
            {{"Key": "Environment", "Value": "production"}},
        ],
    }},
    # Staging {resource_name} - us-east-1
    "resource-id-stag": {{
        # Add fixture data here
        "Tags": [
            {{"Key": "Name", "Value": "staging-resource"}},
            {{"Key": "Environment", "Value": "staging"}},
        ],
    }},
}}

{self.generate_helper_functions(resource_type, "ResourceId")}
'''
        return template


def main():
    """CLI interface for fixture generator."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate AWS resource fixtures")
    parser.add_argument(
        "--resource", required=True, help="Resource type (vpc, nat-gateway, etc.)"
    )
    parser.add_argument("--count", type=int, default=1, help="Number of fixtures")
    parser.add_argument("--from-api", action="store_true", help="Fetch from AWS API")
    parser.add_argument("--resource-id", help="AWS resource ID (for --from-api)")
    parser.add_argument(
        "--template-only", action="store_true", help="Generate file template only"
    )
    parser.add_argument("--output", help="Output file path")

    args = parser.parse_args()

    generator = FixtureGenerator()

    # Generate template file
    if args.template_only:
        template = generator.create_fixture_file_template(
            args.resource, args.resource.replace("-", " ").title()
        )
        if args.output:
            with open(args.output, "w") as f:
                f.write(template)
            print(f"✅ Template written to: {args.output}")
        else:
            print(template)
        return

    # Fetch from AWS API
    if args.from_api:
        if not args.resource_id:
            print("❌ --resource-id required when using --from-api")
            sys.exit(1)

        print(f"🔍 Fetching {args.resource} {args.resource_id} from AWS...")
        fixture = generator.fetch_from_aws(args.resource, args.resource_id)
        if fixture:
            sanitized = generator.sanitize_fixture(fixture)
            print("\n📋 Sanitized fixture:")
            print(json.dumps(sanitized, indent=2))

            # Validate
            errors = generator.validate_fixture(sanitized, args.resource)
            if errors:
                print("\n⚠️  Validation warnings:")
                for error in errors:
                    print(f"  - {error}")
            else:
                print("\n✅ Fixture is valid")
        return

    # Generate from template
    print(f"📝 Generating {args.count} {args.resource} fixture(s) from template...")
    fixtures = generator.generate_from_template(args.resource, args.count)
    if fixtures:
        print(json.dumps(fixtures, indent=2))


if __name__ == "__main__":
    main()
