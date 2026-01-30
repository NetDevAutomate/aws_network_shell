# AWS Network Tools - Test Fixtures

High-quality mock data for comprehensive testing without AWS resource deployment.

## 📁 Available Fixtures

### Core Network Resources

- **`vpc.py`** - VPCs, Subnets, Route Tables, Security Groups, NACLs
- **`tgw.py`** - Transit Gateways, Attachments, Route Tables, Peerings
- **`cloudwan.py`** - Core Networks, Segments, Attachments, Policies, Routes
- **`cloudwan_connect.py`** - Connect Peers, BGP Sessions, GRE Tunnels

### Compute & Network Interfaces

- **`ec2.py`** - EC2 Instances, ENIs (including Lambda, RDS, ALB ENIs)
- **`elb.py`** - Application/Network Load Balancers, Target Groups, Listeners, Health Checks

### Hybrid Connectivity

- **`vpn.py`** - Site-to-Site VPN, Customer Gateways, VPN Gateways, Direct Connect
- **`client_vpn.py`** - Client VPN Endpoints, Routes, Authorization Rules

### Gateway Resources

- **`gateways.py`** - Internet Gateways, NAT Gateways, Elastic IPs, Egress-only IGWs

### Security & Filtering

- **`firewall.py`** - Network Firewalls, Policies, Rule Groups (Suricata/5-tuple/Domain)
- **`prefix_lists.py`** - Customer-Managed and AWS-Managed Prefix Lists

### Additional Services

- **`peering.py`** - VPC Peering Connections (intra-region, cross-region, cross-account)
- **`vpc_endpoints.py`** - Interface/Gateway Endpoints, PrivateLink Services
- **`route53_resolver.py`** - Resolver Endpoints, Rules, Query Logging
- **`global_accelerator.py`** - Accelerators, Listeners, Endpoint Groups

## 🚀 Quick Start

```python
# Import fixtures
from tests.fixtures import (
    VPC_FIXTURES,
    TGW_FIXTURES,
    CLOUDWAN_FIXTURES,
    get_vpc_detail,
    get_tgw_detail,
)

# Use in tests
def test_vpc_routing():
    vpc = VPC_FIXTURES["vpc-0prod1234567890ab"]
    assert vpc["State"] == "available"

    # Get comprehensive detail with all associated resources
    detail = get_vpc_detail("vpc-0prod1234567890ab")
    assert len(detail["subnets"]) == 9  # 3 public, 3 private, 2 db, 2 tgw
    assert len(detail["route_tables"]) == 4
```

## 🔧 Adding New Fixtures

### Method 1: Use Fixture Generator Script

```bash
# Generate template file
python tests/fixtures/fixture_generator.py \
    --resource nat-gateway \
    --template-only \
    --output tests/fixtures/new_resource.py

# Fetch from real AWS (requires credentials)
python tests/fixtures/fixture_generator.py \
    --resource nat-gateway \
    --from-api \
    --resource-id nat-01234567890abcdef

# Generate from template
python tests/fixtures/fixture_generator.py \
    --resource nat-gateway \
    --count 3
```

### Method 2: Use AWS MCP Servers

Use Claude with AWS MCP servers to fetch real API responses:

```python
# In Claude Code conversation:
# "Use the AWS Network MCP server to get a real NAT gateway structure"

# Claude will use:
from mcp__awslabs_aws-network-mcp-server import get_vpc_network_details

# Get real structure, then sanitize for fixtures
```

### Method 3: Reference Module Code

```bash
# Find what fields the module expects
grep -A 30 "describe_nat_gateways" src/aws_network_tools/modules/vpc.py

# Read the module to understand data structure
cat src/aws_network_tools/modules/vpc.py
```

### Method 4: Use AWS CLI

```bash
# Get real API response (dry-run if testing)
aws ec2 describe-nat-gateways \
    --region eu-west-1 \
    --output json

# Copy JSON structure into fixture file
```

### Method 5: Read AWS Documentation via MCP

```python
# In Claude Code:
# "Use AWS MCP server to read documentation for NAT Gateway API"

# Claude will use:
from mcp__aws-knowledge-mcp-server import aws___read_documentation

# Gets official API structure from AWS docs
```

## 📝 Fixture File Template

```python
"""Realistic [Resource Name] mock data fixtures.

Architecture description:
- Multi-region setup (eu-west-1, us-east-1, ap-southeast-2)
- Multi-environment (Production, Staging, Development)
- [Describe key scenarios]

Each fixture includes:
- [Key attributes]
- [Relationships]
- [Realistic configurations]
"""

from typing import Any

# =============================================================================
# [RESOURCE NAME] FIXTURES
# =============================================================================

RESOURCE_FIXTURES: dict[str, dict[str, Any]] = {
    "resource-id-1": {
        "ResourceId": "resource-id-1",
        "State": "available",
        # ... complete AWS API structure
        "Tags": [
            {"Key": "Name", "Value": "resource-name"},
            {"Key": "Environment", "Value": "production"},
        ],
    },
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_resource_by_id(resource_id: str) -> dict[str, Any] | None:
    """Get resource fixture by ID."""
    return RESOURCE_FIXTURES.get(resource_id)

def get_resources_by_vpc(vpc_id: str) -> list[dict[str, Any]]:
    """Get all resources in a VPC."""
    return [r for r in RESOURCE_FIXTURES.values() if r.get("VpcId") == vpc_id]

def get_resource_detail(resource_id: str) -> dict[str, Any] | None:
    """Get comprehensive resource detail with all associations."""
    resource = RESOURCE_FIXTURES.get(resource_id)
    if not resource:
        return None

    # Gather related resources from other fixture modules
    # Return complete detail dictionary
    return {"resource": resource, "related": []}
```

## 🏗️ Fixture Architecture

### Resource Relationships

```
VPC
├── Subnets
│   ├── Route Tables
│   ├── NACLs
│   └── ENIs
│       └── Security Groups
├── Internet Gateway
├── NAT Gateways (per subnet)
│   └── Elastic IPs
├── VPC Endpoints
│   └── ENIs (for Interface endpoints)
└── VPC Peering

Transit Gateway
├── VPC Attachments → VPCs
├── VPN Attachments → VPN Connections
├── Peering Attachments → Other TGWs
├── Route Tables
│   ├── Routes
│   ├── Associations
│   └── Propagations
└── Connect Attachments → CloudWAN

CloudWAN Core Network
├── Segments
├── VPC Attachments → VPCs
├── Connect Attachments
│   └── Connect Peers (BGP)
├── VPN Attachments → VPN Connections
├── TGW Peering Attachments → TGWs
└── Route Tables (per segment/region)

Load Balancer
├── Listeners
│   └── Rules
└── Target Groups
    ├── Targets
    └── Target Health

Network Firewall
├── Firewall Policy
│   ├── Stateless Rule Groups
│   └── Stateful Rule Groups
└── Endpoints (ENIs)
```

## 🎯 Best Practices

### 1. **Consistent ID Patterns**

```python
# Follow AWS ID patterns
vpc_id = "vpc-0prod1234567890ab"      # 17 hex chars after prefix
subnet_id = "subnet-0pub1a1234567890"  # 17 hex chars after prefix
tgw_id = "tgw-0prod12345678901"        # 17 hex chars after prefix
```

### 2. **Multi-Region Coverage**

```python
# Always include 3 regions minimum
regions = ["eu-west-1", "us-east-1", "ap-southeast-2"]
environments = ["production", "staging", "development"]
```

### 3. **Cross-References**

```python
# Reference existing fixture IDs
nat_gateway = {
    "VpcId": "vpc-0prod1234567890ab",  # From VPC_FIXTURES
    "SubnetId": "subnet-0pub1a1234567890",  # From SUBNET_FIXTURES
    "NatGatewayAddresses": [{
        "NetworkInterfaceId": "eni-0nat1a12345678901",  # From ENI_FIXTURES
    }]
}
```

### 4. **Include All States**

```python
# Cover operational and transitional states
states = ["available", "pending", "deleting", "deleted", "failed"]

# Include error cases
nat_failed = {
    "State": "failed",
    "FailureCode": "InsufficientFreeAddressesInSubnet",
    "FailureMessage": "Not enough free IP addresses in subnet",
}
```

### 5. **Helper Functions**

Every fixture file should include:

- `get_*_by_id()` - Primary ID lookup
- `get_*s_by_vpc()` - VPC-scoped queries
- `get_*s_by_state()` - State filtering
- `get_*_detail()` - Comprehensive detail with associations
- Custom queries specific to resource type

### 6. **Docstrings**

```python
"""Get comprehensive [resource] detail with all associated resources.

Args:
    resource_id: The [resource] ID

Returns:
    Dictionary containing:
    - resource: The main resource
    - related_resources: Associated resources
    - relationships: Cross-references

    Returns None if resource not found.
"""
```

## 🧪 Testing with Fixtures

```python
import pytest
from tests.fixtures import get_vpc_detail, get_tgw_detail

def test_vpc_has_internet_gateway():
    """Test that production VPC has IGW route."""
    vpc_detail = get_vpc_detail("vpc-0prod1234567890ab")

    # Check public route table has IGW route
    public_rt = next(
        rt for rt in vpc_detail["route_tables"]
        if "public" in rt.get("Tags", [{}])[0].get("Value", "").lower()
    )

    igw_route = next(
        r for r in public_rt["Routes"]
        if r["DestinationCidrBlock"] == "0.0.0.0/0"
    )

    assert igw_route["GatewayId"].startswith("igw-")

def test_nat_gateway_has_eip():
    """Test NAT Gateway has allocated Elastic IP."""
    from tests.fixtures import get_nat_by_id, get_eip_by_allocation_id

    nat = get_nat_by_id("nat-0prod1a12345678")
    alloc_id = nat["NatGatewayAddresses"][0]["AllocationId"]

    eip = get_eip_by_allocation_id(alloc_id)
    assert eip is not None
    assert eip["PublicIp"] == nat["NatGatewayAddresses"][0]["PublicIp"]
```

## 📚 Resources for Creating Fixtures

### AWS Documentation

Use AWS MCP server to read official docs:

```python
# In Claude Code:
# "Read AWS documentation for [resource] API using MCP server"
```

### Boto3 Documentation

- <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html>
- <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/networkmanager.html>

### Module Source Code

Your modules are the **best reference** for expected data structure:

- `src/aws_network_tools/modules/[resource].py`
- Look for `describe_*` boto3 API calls
- Check what fields are accessed in display/processing code

## 🔍 Finding Missing Fixtures

```bash
# Search for resource IDs referenced but not defined
cd /Users/taylaand/code/personal/aws_network_shell
grep -r "igw-" tests/fixtures/*.py | grep -v "def " | grep -v "#"

# Find modules without fixtures
ls src/aws_network_tools/modules/*.py | while read module; do
    basename=$(basename "$module" .py)
    if [ ! -f "tests/fixtures/${basename}.py" ]; then
        echo "Missing fixture: ${basename}.py"
    fi
done
```

## 📊 Fixture Statistics

- **Total Fixture Files**: 16
- **Total Resources**: 200+
- **Helper Functions**: 150+
- **Regions Covered**: 3 (eu-west-1, us-east-1, ap-southeast-2)
- **Environments**: 4 (production, staging, development, shared)
- **Lines of Code**: ~8,000

## 🎓 Learning Resources

### Understanding AWS API Responses

1. **AWS CLI with --debug**: See raw API responses
2. **AWS MCP Server**: Fetch real resource details
3. **boto3 documentation**: Official API reference
4. **Module code**: Your own code shows expected structure

### Creating Realistic Test Data

1. **Use realistic CIDR blocks**: RFC1918 private ranges
2. **Follow naming conventions**: Environment-tier-region-az pattern
3. **Include tags**: Name, Environment, ManagedBy, Purpose
4. **Multi-AZ for production**: High availability patterns
5. **Include failure cases**: Test error handling paths

### Cross-Reference Validation

Run this check to ensure fixture integrity:

```python
from tests.fixtures import get_all_gateways_by_vpc, VPC_FIXTURES

# Verify all route table gateway IDs exist
for vpc_id in VPC_FIXTURES:
    gateways = get_all_gateways_by_vpc(vpc_id)
    print(f"{vpc_id}: {len(gateways['nat_gateways'])} NATs, "
          f"{len(gateways['internet_gateways'])} IGWs")
```

## 🤝 Contributing New Fixtures

1. **Identify the resource type** and check if module exists
2. **Use fixture_generator.py** to create template or fetch from AWS
3. **Follow existing patterns** from similar fixture files
4. **Include helper functions** for common query patterns
5. **Add comprehensive docstrings** with architecture description
6. **Cross-reference existing fixtures** (VPC IDs, subnet IDs, etc.)
7. **Update `__init__.py`** to export new fixtures
8. **Include multiple states** (available, pending, failed)
9. **Cover multiple regions** and environments
10. **Test fixture integrity** with helper functions

## 💡 Pro Tips

- **Start with templates**: Use `fixture_generator.py --template-only`
- **Fetch real data once**: Use `--from-api` to get correct structure
- **Reference existing fixtures**: Maintain relationship integrity
- **Include edge cases**: Pending, deleting, failed states
- **Add helper functions**: Make fixtures easy to query in tests
- **Document architecture**: Explain the scenario in docstring
- **Use realistic values**: Makes debugging easier
- **Test your fixtures**: Write simple tests to validate structure

## 📞 Need Help?

1. **Check existing fixtures**: Similar resources may already have patterns
2. **Read module code**: Shows exactly what fields are expected
3. **Use MCP servers**: AWS MCP and AWS Knowledge MCP for real data
4. **Run fixture_generator.py**: Automated template creation
5. **Ask Claude**: I can help create new fixtures using AWS MCP servers!

---

**Last Updated**: 2024-12-04
**Total Fixture Coverage**: 16 resource types, 200+ resources, production-ready quality
