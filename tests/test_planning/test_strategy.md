# Comprehensive Test Strategy for aws_network_shell

**Project**: aws_network_shell
**Date**: 2025-12-04
**Models Consulted**: Kimi K2, Nova Premier, Claude Opus 4.5, DeepSeek V3

---

## Executive Summary

This test strategy synthesizes recommendations from 4 foundational models to address the core challenge: **testing CLI commands with context dependencies** where subcommands require output from parent commands (e.g., `vpc vpc-123` → `show subnets`).

### Key Decisions

1. **Architecture**: Session-based CLIContext with output caching (Kimi K2)
2. **Fixtures**: Hierarchical composition with dependency injection (All models)
3. **Assertions**: JSON schema validation for binary pass/fail (Kimi K2, Opus 4.5)
4. **Edge Cases**: AWS-specific limits + auto-generated boundary tests (Nova Premier, Opus 4.5)
5. **Parallelization**: Pytest markers for independent tests (DeepSeek V3)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Test Framework                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐     ┌─────────────────┐     ┌──────────┐ │
│  │  CLIContext  │────▶│  Output Cache   │────▶│ Fixtures │ │
│  │   (Session)  │     │  (Dependencies) │     │ (Setup)  │ │
│  └──────────────┘     └─────────────────┘     └──────────┘ │
│         │                      │                      │      │
│         ▼                      ▼                      ▼      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Command Execution Pipeline                  │  │
│  │  1. Validate Context  2. Execute  3. Cache Output    │  │
│  └──────────────────────────────────────────────────────┘  │
│                             │                               │
│                             ▼                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Schema Validation & Assertions              │  │
│  │  - JSON Schema  - Exit Codes  - Error Messages       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Component: CLIContext Class

**Source**: Kimi K2 (Session-Based Command Graph)

```python
# tests/framework/cli_context.py
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import subprocess
import json

@dataclass
class CLIContext:
    """Session state that accumulates across command executions"""

    # Environment variables
    env: Dict[str, str] = field(default_factory=dict)

    # Output cache for command dependencies
    output_cache: Dict[str, Any] = field(default_factory=dict)

    # Context stack for nested commands (e.g., vpc → subnet → route-table)
    current_context: List[str] = field(default_factory=list)

    # AWS-specific context
    region: str = "us-east-1"
    profile: Optional[str] = None

    def execute(self, cmd: str, expect_json: bool = True) -> tuple[int, str, str]:
        """
        Execute command in current context and cache output.

        Returns: (exit_code, stdout, stderr)
        """
        # Build full command with context prefix
        full_cmd = self._build_command(cmd)

        # Execute
        result = subprocess.run(
            full_cmd,
            capture_output=True,
            text=True,
            env=self._build_env(),
            timeout=30
        )

        # Cache output for downstream dependencies
        cache_key = self._get_cache_key(cmd)
        self.output_cache[cache_key] = {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
            "parsed": self._try_parse_json(result.stdout) if expect_json else None
        }

        return result.returncode, result.stdout, result.stderr

    def enter_context(self, context_segment: str):
        """Enter nested context (e.g., 'vpc vpc-123')"""
        self.current_context.append(context_segment)

    def exit_context(self):
        """Return to parent context"""
        if self.current_context:
            self.current_context.pop()

    def get_cached_output(self, command: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached command output"""
        cache_key = self._get_cache_key(command)
        return self.output_cache.get(cache_key)

    def _build_command(self, cmd: str) -> List[str]:
        """Build command with context prefix"""
        base_cmd = ["aws-network-shell"]

        # Add AWS profile if specified
        if self.profile:
            base_cmd.extend(["--profile", self.profile])

        # Add region
        base_cmd.extend(["--region", self.region])

        # Add context stack (e.g., vpc vpc-123)
        base_cmd.extend(self.current_context)

        # Add actual command
        base_cmd.extend(cmd.split())

        return base_cmd

    def _build_env(self) -> Dict[str, str]:
        """Build environment variables"""
        import os
        env = os.environ.copy()
        env.update(self.env)
        return env

    def _get_cache_key(self, cmd: str) -> str:
        """Generate cache key from context + command"""
        context_str = "_".join(self.current_context)
        cmd_str = cmd.split()[0] if cmd else "unknown"
        return f"{context_str}_{cmd_str}" if context_str else cmd_str

    def _try_parse_json(self, output: str) -> Optional[Any]:
        """Attempt to parse output as JSON"""
        try:
            return json.loads(output)
        except (json.JSONDecodeError, ValueError):
            return None
```

### Usage Example

```python
def test_vpc_to_subnet_workflow(cli_context_factory):
    # Create isolated session
    session = cli_context_factory()

    # Execute parent command
    exit_code, stdout, stderr = session.execute("vpc list")
    assert exit_code == 0

    # Get VPC ID from cached output
    vpcs = session.get_cached_output("vpc list")["parsed"]
    vpc_id = vpcs[0]["VpcId"]

    # Enter VPC context
    session.enter_context(f"vpc {vpc_id}")

    # Execute nested command
    exit_code, stdout, stderr = session.execute("show subnets")
    assert exit_code == 0
    assert "subnet-" in stdout
```

---

## Fixture Architecture

**Source**: All models (consensus approach)

### Base Fixtures (conftest.py)

```python
# tests/conftest.py
import pytest
from tests.framework.cli_context import CLIContext
from tests.framework.boto3_mocks import setup_moto_vpc, setup_moto_tgw

@pytest.fixture
def cli_context_factory():
    """Factory for creating isolated CLI sessions"""
    def _create_context(region="us-east-1", profile=None):
        return CLIContext(region=region, profile=profile)
    return _create_context

@pytest.fixture
def cli_context(cli_context_factory):
    """Single CLI session for simple tests"""
    return cli_context_factory()

@pytest.fixture(scope="session")
def aws_credentials():
    """Mock AWS credentials for boto3"""
    import os
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
```

### Hierarchical Fixtures (fixtures/network.py)

**Source**: Kimi K2 + DeepSeek V3

```python
# tests/fixtures/network.py
import pytest
from moto import mock_ec2, mock_networkmanager
import boto3

@pytest.fixture
def vpc_setup(cli_context_factory, aws_credentials):
    """
    Top-level fixture: Create VPC and return context with cached output.

    Dependencies: None
    Provides: VPC ID, context session
    """
    with mock_ec2():
        # Create VPC using boto3
        ec2 = boto3.client("ec2", region_name="us-east-1")
        vpc_response = ec2.create_vpc(CidrBlock="10.0.0.0/16")
        vpc_id = vpc_response["Vpc"]["VpcId"]

        # Tag for identification
        ec2.create_tags(
            Resources=[vpc_id],
            Tags=[{"Key": "Name", "Value": "test-vpc"}]
        )

        # Create CLI session and cache VPC data
        session = cli_context_factory()
        session.output_cache["vpc_list"] = {
            "parsed": [{"VpcId": vpc_id, "CidrBlock": "10.0.0.0/16"}]
        }

        # Enter VPC context
        session.enter_context(f"vpc {vpc_id}")

        yield session

        # Cleanup
        session.exit_context()

@pytest.fixture
def subnet_setup(vpc_setup):
    """
    Second-level fixture: Create subnets within VPC context.

    Dependencies: vpc_setup
    Provides: Subnet IDs, VPC context session
    """
    session = vpc_setup

    with mock_ec2():
        ec2 = boto3.client("ec2", region_name="us-east-1")

        # Get VPC ID from context
        vpc_id = session.current_context[-1].split()[-1]

        # Create subnets
        subnet_ids = []
        for i, az in enumerate(["us-east-1a", "us-east-1b"]):
            subnet_response = ec2.create_subnet(
                VpcId=vpc_id,
                CidrBlock=f"10.0.{i}.0/24",
                AvailabilityZone=az
            )
            subnet_ids.append(subnet_response["Subnet"]["SubnetId"])

        # Cache subnet data
        session.output_cache["show_subnets"] = {
            "parsed": [{"SubnetId": sid, "VpcId": vpc_id} for sid in subnet_ids]
        }

        yield session

@pytest.fixture
def security_group_setup(vpc_setup):
    """
    Second-level fixture: Create security groups within VPC.

    Dependencies: vpc_setup
    Provides: Security group IDs, VPC context session
    """
    session = vpc_setup

    with mock_ec2():
        ec2 = boto3.client("ec2", region_name="us-east-1")
        vpc_id = session.current_context[-1].split()[-1]

        # Create security group
        sg_response = ec2.create_security_group(
            GroupName="test-sg",
            Description="Test security group",
            VpcId=vpc_id
        )
        sg_id = sg_response["GroupId"]

        # Add ingress rules
        ec2.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[
                {
                    "IpProtocol": "tcp",
                    "FromPort": 22,
                    "ToPort": 22,
                    "IpRanges": [{"CidrIp": "0.0.0.0/0"}]
                }
            ]
        )

        # Cache security group data
        session.output_cache["show_security_groups"] = {
            "parsed": [{"GroupId": sg_id, "VpcId": vpc_id}]
        }

        yield session
```

### Multi-Region Fixtures

**Source**: Nova Premier (AWS Expert)

```python
# tests/fixtures/multi_region.py
import pytest
from moto import mock_ec2
import boto3

@pytest.fixture(params=["us-east-1", "eu-west-1", "ap-southeast-2"])
def multi_region_vpc(request, cli_context_factory):
    """
    Parameterized fixture for multi-region testing.

    Creates VPC in each region and yields separate contexts.
    """
    region = request.param

    with mock_ec2():
        ec2 = boto3.client("ec2", region_name=region)
        vpc_response = ec2.create_vpc(CidrBlock="10.0.0.0/16")
        vpc_id = vpc_response["Vpc"]["VpcId"]

        session = cli_context_factory(region=region)
        session.output_cache["vpc_list"] = {
            "parsed": [{"VpcId": vpc_id, "Region": region}]
        }
        session.enter_context(f"vpc {vpc_id}")

        yield session

        session.exit_context()

@pytest.fixture(scope="module")
def cross_region_peering():
    """
    Complex fixture for cross-region VPC peering tests.

    Creates VPCs in two regions and establishes peering.
    """
    with mock_ec2():
        # Region 1: us-east-1
        ec2_us = boto3.client("ec2", region_name="us-east-1")
        vpc_us_response = ec2_us.create_vpc(CidrBlock="10.0.0.0/16")
        vpc_us_id = vpc_us_response["Vpc"]["VpcId"]

        # Region 2: eu-west-1
        ec2_eu = boto3.client("ec2", region_name="eu-west-1")
        vpc_eu_response = ec2_eu.create_vpc(CidrBlock="10.1.0.0/16")
        vpc_eu_id = vpc_eu_response["Vpc"]["VpcId"]

        # Create peering connection
        peering_response = ec2_us.create_vpc_peering_connection(
            VpcId=vpc_us_id,
            PeerVpcId=vpc_eu_id,
            PeerRegion="eu-west-1"
        )
        peering_id = peering_response["VpcPeeringConnection"]["VpcPeeringConnectionId"]

        # Accept peering in eu-west-1
        ec2_eu.accept_vpc_peering_connection(VpcPeeringConnectionId=peering_id)

        yield {
            "us_east_1": {"vpc_id": vpc_us_id, "region": "us-east-1"},
            "eu_west_1": {"vpc_id": vpc_eu_id, "region": "eu-west-1"},
            "peering_id": peering_id
        }
```

---

## Schema Validation & Assertions

**Source**: Kimi K2 (Deterministic Output) + Claude Opus 4.5 (Validators)

### JSON Schema Definitions

```python
# tests/framework/schemas.py
from jsonschema import validate, ValidationError

VPC_LIST_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["VpcId", "CidrBlock", "State"],
        "properties": {
            "VpcId": {
                "type": "string",
                "pattern": "^vpc-[a-f0-9]{8,17}$"
            },
            "CidrBlock": {
                "type": "string",
                "pattern": r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}$"
            },
            "State": {
                "type": "string",
                "enum": ["pending", "available"]
            }
        }
    },
    "minItems": 1
}

SUBNET_LIST_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["SubnetId", "VpcId", "CidrBlock", "AvailabilityZone"],
        "properties": {
            "SubnetId": {
                "type": "string",
                "pattern": "^subnet-[a-f0-9]{8,17}$"
            },
            "VpcId": {
                "type": "string",
                "pattern": "^vpc-[a-f0-9]{8,17}$"
            },
            "CidrBlock": {
                "type": "string",
                "pattern": r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}$"
            },
            "AvailabilityZone": {
                "type": "string",
                "pattern": "^[a-z]{2}-[a-z]+-\d[a-z]$"
            }
        }
    }
}

SECURITY_GROUP_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["GroupId", "GroupName", "VpcId"],
        "properties": {
            "GroupId": {
                "type": "string",
                "pattern": "^sg-[a-f0-9]{8,17}$"
            },
            "GroupName": {"type": "string"},
            "VpcId": {"type": "string"},
            "IpPermissions": {"type": "array"},
            "IpPermissionsEgress": {"type": "array"}
        }
    }
}

def validate_vpc_list(output: str) -> bool:
    """Binary validator for VPC list output"""
    try:
        data = json.loads(output)
        validate(instance=data, schema=VPC_LIST_SCHEMA)
        return True
    except (json.JSONDecodeError, ValidationError) as e:
        pytest.fail(f"VPC list validation failed: {e}")
        return False

def validate_subnet_list(output: str) -> bool:
    """Binary validator for subnet list output"""
    try:
        data = json.loads(output)
        validate(instance=data, schema=SUBNET_LIST_SCHEMA)
        return True
    except (json.JSONDecodeError, ValidationError) as e:
        pytest.fail(f"Subnet list validation failed: {e}")
        return False
```

### Assertion Helpers

```python
# tests/framework/assertions.py
import json
from typing import Any, Callable

def assert_command_success(exit_code: int, stderr: str):
    """Binary assertion: command must succeed"""
    assert exit_code == 0, f"Command failed with exit code {exit_code}: {stderr}"

def assert_command_failure(exit_code: int, expected_error: str = None):
    """Binary assertion: command must fail"""
    assert exit_code != 0, "Command should have failed but succeeded"

    if expected_error:
        assert expected_error in stderr, f"Expected error '{expected_error}' not found in: {stderr}"

def assert_json_output(stdout: str, schema: dict = None, validator: Callable = None):
    """Binary assertion: output must be valid JSON matching schema"""
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError as e:
        pytest.fail(f"Output is not valid JSON: {e}")

    if schema:
        validate(instance=data, schema=schema)

    if validator:
        validator(data)

    return data

def assert_contains_resource_id(stdout: str, resource_type: str):
    """Binary assertion: output must contain AWS resource ID"""
    patterns = {
        "vpc": r"vpc-[a-f0-9]{8,17}",
        "subnet": r"subnet-[a-f0-9]{8,17}",
        "sg": r"sg-[a-f0-9]{8,17}",
        "instance": r"i-[a-f0-9]{8,17}",
        "tgw": r"tgw-[a-f0-9]{8,17}"
    }

    import re
    pattern = patterns.get(resource_type)
    assert pattern, f"Unknown resource type: {resource_type}"

    match = re.search(pattern, stdout)
    assert match, f"No {resource_type} ID found in output"

    return match.group(0)
```

---

## Edge Case Testing

**Source**: Nova Premier (AWS Expert) + Claude Opus 4.5 (Auto-Generation)

### AWS-Specific Edge Cases

```python
# tests/edge_cases/test_aws_limits.py
import pytest
from tests.framework.assertions import assert_command_failure

class TestAWSQuotaLimits:
    """Test behavior at AWS service quota limits"""

    def test_max_vpcs_per_region(self, cli_context):
        """Test creation of VPCs at quota limit (default: 5)"""
        # Create 5 VPCs
        for i in range(5):
            exit_code, stdout, stderr = cli_context.execute(f"vpc create --cidr 10.{i}.0.0/16")
            assert_command_success(exit_code, stderr)

        # Attempt 6th VPC (should fail)
        exit_code, stdout, stderr = cli_context.execute("vpc create --cidr 10.5.0.0/16")
        assert_command_failure(exit_code, "VpcLimitExceeded")

    def test_overlapping_cidr_blocks(self, cli_context):
        """Test VPC creation with overlapping CIDR blocks"""
        # Create first VPC
        exit_code, _, _ = cli_context.execute("vpc create --cidr 10.0.0.0/16")
        assert exit_code == 0

        # Attempt overlapping CIDR (should succeed - AWS allows this)
        exit_code, _, _ = cli_context.execute("vpc create --cidr 10.0.0.0/24")
        assert exit_code == 0  # AWS allows overlapping CIDRs in different VPCs

    def test_subnet_no_available_ips(self, vpc_setup):
        """Test subnet creation when no IPs are available"""
        session = vpc_setup

        # Create subnet with /28 (14 usable IPs)
        exit_code, _, _ = session.execute("subnet create --cidr 10.0.0.0/28 --az us-east-1a")
        assert exit_code == 0

        # Launch instances to exhaust IPs
        # (AWS reserves 5 IPs: network, gateway, DNS, future, broadcast)
        # So /28 has 16 - 5 = 11 usable IPs
        # This test would verify behavior when launching 12th instance

class TestSecurityGroupLimits:
    """Test security group rule limits"""

    def test_max_rules_per_security_group(self, security_group_setup):
        """Test adding rules at quota limit (default: 60 inbound + 60 outbound)"""
        session = security_group_setup

        sg_id = session.output_cache["show_security_groups"]["parsed"][0]["GroupId"]

        # Add 60 inbound rules (at limit)
        for i in range(60):
            exit_code, _, _ = session.execute(
                f"security-group {sg_id} add-rule --protocol tcp --port {i+1000} --cidr 0.0.0.0/0"
            )
            assert exit_code == 0

        # Attempt 61st rule (should fail)
        exit_code, _, stderr = session.execute(
            f"security-group {sg_id} add-rule --protocol tcp --port 10000 --cidr 0.0.0.0/0"
        )
        assert_command_failure(exit_code, "RulesPerSecurityGroupLimitExceeded")
```

### Auto-Generated Edge Cases

**Source**: Claude Opus 4.5 (Edge Case Generator)

```python
# tests/framework/edge_case_generator.py
from typing import List, Dict, Any
import pytest

class EdgeCaseGenerator:
    """Generate edge case tests automatically for all commands"""

    INVALID_INPUTS = [
        "",                          # Empty string
        " ",                         # Whitespace
        "null",                      # Null string
        "../etc/passwd",             # Path traversal
        "; rm -rf /",                # Command injection
        "' OR '1'='1",               # SQL injection attempt
        "x" * 10000,                 # Very long string
        "🚀",                        # Unicode
        "\x00",                      # Null byte
        "-1",                        # Negative number
        "999999999999999",           # Very large number
        "not-a-valid-id",            # Invalid AWS ID format
        "vpc-zzzzzzzz",              # Invalid characters in ID
    ]

    @staticmethod
    def generate_invalid_input_tests(command: str, arg_name: str) -> List[pytest.param]:
        """Generate test parameters for invalid inputs"""
        test_params = []

        for invalid_input in EdgeCaseGenerator.INVALID_INPUTS:
            test_params.append(
                pytest.param(
                    invalid_input,
                    id=f"invalid_{arg_name}_{repr(invalid_input)[:20]}"
                )
            )

        return test_params

# Usage in tests
@pytest.mark.parametrize(
    "vpc_id",
    EdgeCaseGenerator.generate_invalid_input_tests("vpc", "vpc_id")
)
def test_vpc_show_invalid_inputs(cli_context, vpc_id):
    """Test 'vpc show' with invalid VPC IDs"""
    cli_context.enter_context(f"vpc {vpc_id}")
    exit_code, _, stderr = cli_context.execute("show")

    # Should fail with appropriate error
    assert exit_code != 0
    assert "Invalid" in stderr or "Not Found" in stderr or "Error" in stderr
```

---

## Test Organization

**Source**: DeepSeek V3 (Parallel Execution)

### Directory Structure

```
tests/
├── conftest.py                 # Base fixtures
├── framework/                  # Test framework components
│   ├── __init__.py
│   ├── cli_context.py         # CLIContext class
│   ├── schemas.py             # JSON schemas
│   ├── assertions.py          # Assertion helpers
│   ├── edge_case_generator.py # Edge case auto-generation
│   └── boto3_mocks.py         # Boto3 mock helpers
├── fixtures/                   # Fixture definitions
│   ├── __init__.py
│   ├── network.py             # VPC, subnet, SG fixtures
│   ├── transit_gateway.py     # TGW fixtures
│   ├── cloudwan.py            # CloudWAN fixtures
│   └── multi_region.py        # Cross-region fixtures
├── unit/                       # Unit tests (fast, parallel-safe)
│   ├── test_vpc_commands.py
│   ├── test_subnet_commands.py
│   ├── test_sg_commands.py
│   └── test_route_commands.py
├── integration/                # Integration tests (sequential)
│   ├── test_vpc_to_subnet_workflow.py
│   ├── test_tgw_routing.py
│   └── test_cloudwan_peering.py
├── edge_cases/                 # Edge case tests
│   ├── test_aws_limits.py
│   ├── test_invalid_inputs.py
│   └── test_error_handling.py
└── test_planning/              # Documentation
    ├── model_consultations.md
    └── test_strategy.md
```

### Pytest Configuration

```ini
# pytest.ini
[pytest]
minversion = 7.0
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Markers
markers =
    parallel_safe: Tests that can run independently in parallel
    requires_vpc: Tests that require VPC context
    requires_tgw: Tests that require Transit Gateway
    requires_cloudwan: Tests that require CloudWAN
    slow: Tests that take >5 seconds
    aws_integration: Tests that interact with AWS APIs

# Parallel execution
addopts =
    -v
    --strict-markers
    --tb=short
    --disable-warnings

# Coverage
[coverage:run]
source = aws_network_shell
omit =
    */tests/*
    */test_*

[coverage:report]
precision = 2
show_missing = True
skip_covered = False
```

### Pytest Markers for Parallelization

```python
# tests/unit/test_vpc_commands.py
import pytest
from tests.framework.cli_context import CLIContext
from tests.framework.schemas import validate_vpc_list

@pytest.mark.parallel_safe
class TestVPCListCommand:
    """Unit tests for 'vpc list' command - can run in parallel"""

    def test_vpc_list_json_format(self, cli_context):
        """Test vpc list returns valid JSON"""
        exit_code, stdout, stderr = cli_context.execute("vpc list")

        assert exit_code == 0
        assert validate_vpc_list(stdout)

    @pytest.mark.parametrize("region", ["us-east-1", "eu-west-1", "ap-southeast-2"])
    def test_vpc_list_multi_region(self, cli_context_factory, region):
        """Test vpc list in different regions"""
        session = cli_context_factory(region=region)
        exit_code, stdout, stderr = session.execute("vpc list")

        assert exit_code == 0
        assert validate_vpc_list(stdout)

@pytest.mark.requires_vpc
class TestVPCShowCommand:
    """Unit tests for 'vpc show' command - requires VPC context"""

    def test_vpc_show_displays_details(self, vpc_setup):
        """Test vpc show displays VPC details"""
        session = vpc_setup
        exit_code, stdout, stderr = session.execute("show")

        assert exit_code == 0
        assert "VpcId" in stdout
        assert "CidrBlock" in stdout
```

### Running Tests

```bash
# Run all tests in parallel (parallel-safe tests only)
pytest -n auto -m parallel_safe

# Run all tests sequentially
pytest

# Run specific test category
pytest tests/unit/                    # Unit tests only
pytest tests/integration/             # Integration tests only
pytest tests/edge_cases/              # Edge case tests only

# Run tests with coverage
pytest --cov=aws_network_shell --cov-report=html

# Run tests matching pattern
pytest -k "vpc"                       # All VPC-related tests
pytest -k "test_invalid"              # All invalid input tests

# Run with verbose output and timing
pytest -v --durations=10

# Run specific test with context
pytest tests/unit/test_vpc_commands.py::TestVPCListCommand::test_vpc_list_json_format -v
```

---

## Implementation Phases

### Phase 1: Foundation (Week 1) - 40 hours

**Deliverables**:
1. CLIContext class implementation (8 hours)
   - Session management
   - Output caching
   - Context stack
   - Command execution

2. Base fixtures (8 hours)
   - cli_context_factory
   - cli_context
   - aws_credentials
   - Basic VPC fixture

3. Schema validation (8 hours)
   - JSON schemas for all commands
   - Validation functions
   - Assertion helpers

4. Test structure (8 hours)
   - Directory organization
   - pytest.ini configuration
   - Initial unit tests for 5 core commands

5. Documentation (8 hours)
   - Testing guide
   - Fixture usage examples
   - Running tests guide

**Success Criteria**:
- ✅ 20+ tests passing
- ✅ CLIContext handles context transitions
- ✅ Fixtures support VPC → Subnet → SG hierarchy
- ✅ All tests have binary pass/fail assertions

### Phase 2: AWS Integration (Week 2) - 40 hours

**Deliverables**:
1. boto3 mock fixtures (12 hours)
   - VPC/Subnet/SG mocks
   - Transit Gateway mocks
   - CloudWAN mocks
   - ENI/Route Table mocks

2. AWS edge cases (12 hours)
   - Quota limit tests
   - Overlapping CIDR tests
   - Cross-region tests
   - Multi-account tests

3. Multi-region fixtures (8 hours)
   - Parameterized region fixtures
   - Cross-region peering
   - Regional resource tests

4. Integration tests (8 hours)
   - End-to-end workflows
   - Context transition chains
   - Multi-resource interactions

**Success Criteria**:
- ✅ 50+ tests passing
- ✅ All AWS services mocked correctly
- ✅ Edge cases cover quota limits
- ✅ Multi-region tests pass

### Phase 3: Comprehensive Coverage (Week 3) - 40 hours

**Deliverables**:
1. Edge case auto-generation (10 hours)
   - Invalid input generator
   - Boundary value generator
   - Error condition generator

2. Complete command coverage (15 hours)
   - Tests for ALL CLI commands
   - All context transitions
   - All command variations

3. Coverage tracking (5 hours)
   - Coverage reporting
   - Gap analysis
   - Missing test identification

4. Documentation (10 hours)
   - Test coverage report
   - Command test matrix
   - Known limitations

**Success Criteria**:
- ✅ 100+ tests passing
- ✅ 90%+ command coverage
- ✅ All edge cases generated
- ✅ Coverage gaps documented

### Phase 4: Optimization (Week 4) - 20 hours

**Deliverables**:
1. Parallelization (8 hours)
   - Pytest markers for parallel tests
   - Parallel execution configuration
   - Performance optimization

2. CI/CD Integration (6 hours)
   - GitHub Actions workflow
   - Automated test runs
   - Coverage reporting

3. Performance tuning (6 hours)
   - Fixture caching
   - Test execution speed
   - Resource cleanup

**Success Criteria**:
- ✅ Tests run <5 minutes total
- ✅ 50%+ tests run in parallel
- ✅ CI/CD pipeline automated
- ✅ Coverage reports generated

---

## Success Metrics

### Coverage Targets

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Command Coverage | 100% | 0% | ❌ Not Started |
| Line Coverage | 80% | 0% | ❌ Not Started |
| Branch Coverage | 70% | 0% | ❌ Not Started |
| Edge Case Coverage | 90% | 0% | ❌ Not Started |
| Integration Tests | 20+ | 0 | ❌ Not Started |
| Unit Tests | 100+ | 0 | ❌ Not Started |

### Quality Gates

- ✅ All tests have binary pass/fail (no ambiguous assertions)
- ✅ All command paths tested (top-level + all context transitions)
- ✅ All fixtures support dependency resolution
- ✅ Schema validation for all JSON outputs
- ✅ Edge cases cover AWS-specific scenarios
- ✅ Tests run in <5 minutes
- ✅ 50%+ tests run in parallel
- ✅ CI/CD integration complete

### Test Reliability

- **Flaky Tests**: 0% tolerance
- **False Positives**: 0% tolerance
- **False Negatives**: 0% tolerance
- **Test Isolation**: 100% (no shared state between tests)
- **Deterministic Output**: 100% (schema validation ensures consistency)

---

## Maintenance & Evolution

### Adding New Commands

1. Create test file: `tests/unit/test_<command>_commands.py`
2. Define JSON schema: `tests/framework/schemas.py`
3. Create fixture if needed: `tests/fixtures/<resource>.py`
4. Add edge cases: Use `EdgeCaseGenerator` to auto-generate
5. Update coverage report: Run `pytest --cov`

### Handling Breaking Changes

1. Update CLIContext if command structure changes
2. Update schemas if output format changes
3. Update fixtures if AWS API changes
4. Run full test suite: `pytest -v`
5. Review failures and update tests accordingly

### Continuous Improvement

1. **Weekly**: Review test execution time, optimize slow tests
2. **Monthly**: Review coverage reports, add missing tests
3. **Quarterly**: Review edge cases, add new AWS-specific scenarios
4. **Annually**: Major refactoring if needed, framework updates

---

## References

### Model Consultations

- **Full transcripts**: `tests/test_planning/model_consultations.md`
- **Kimi K2**: Session-based architecture, output caching
- **Nova Premier**: AWS edge cases, multi-region testing
- **Claude Opus 4.5**: Comprehensive framework, coverage tracking
- **DeepSeek V3**: Parallelization, pytest markers

### Related Documentation

- **Pytest**: https://docs.pytest.org/
- **moto**: https://github.com/getmoto/moto (AWS mocking)
- **JSON Schema**: https://json-schema.org/
- **AWS Service Quotas**: https://docs.aws.amazon.com/general/latest/gr/aws_service_limits.html

---

## Appendix A: Quick Start Guide

### Setup

```bash
# Install dependencies
pip install -r requirements-dev.txt

# Install test dependencies
pip install pytest pytest-cov pytest-xdist moto jsonschema

# Run initial tests
pytest tests/unit/ -v
```

### Creating Your First Test

```python
# tests/unit/test_my_command.py
import pytest
from tests.framework.cli_context import CLIContext
from tests.framework.assertions import assert_command_success

@pytest.mark.parallel_safe
def test_my_command(cli_context):
    """Test my new command"""
    exit_code, stdout, stderr = cli_context.execute("my-command --arg value")

    assert_command_success(exit_code, stderr)
    assert "expected output" in stdout
```

### Running Your Test

```bash
pytest tests/unit/test_my_command.py -v
```

---

## Appendix B: Troubleshooting

### Common Issues

**Issue**: Test hangs during execution
- **Cause**: Missing timeout in subprocess execution
- **Fix**: Add `timeout=30` to `subprocess.run()`

**Issue**: Fixture not found
- **Cause**: Missing conftest.py or incorrect import
- **Fix**: Ensure conftest.py exists and fixture is defined

**Issue**: Schema validation fails
- **Cause**: Output format doesn't match schema
- **Fix**: Update schema or fix CLI output format

**Issue**: Tests fail intermittently
- **Cause**: Shared state between tests
- **Fix**: Ensure proper fixture cleanup, use isolated contexts

**Issue**: Moto mocks not working
- **Cause**: Missing mock decorator or incorrect region
- **Fix**: Add `@mock_ec2` decorator, verify region matches

---

## Conclusion

This comprehensive test strategy provides a robust foundation for testing aws_network_shell with context-dependent commands. By combining insights from multiple foundational models, we've created an architecture that:

1. **Handles command dependencies** through session-based context and output caching
2. **Ensures binary pass/fail** through JSON schema validation
3. **Covers AWS-specific edge cases** through targeted testing
4. **Enables parallel execution** through pytest markers
5. **Provides comprehensive coverage** through auto-generated edge cases

The implementation phases provide a clear roadmap from foundation to optimization, with measurable success criteria at each stage.
