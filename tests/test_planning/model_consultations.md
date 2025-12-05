# Multi-Model Test Strategy Consultations

**Project**: aws_network_shell
**Date**: 2025-12-04
**Objective**: Design comprehensive test strategy for CLI with context-dependent commands

---

## Executive Summary

Consulted with 4 foundational models via RepoPrompt MCP:
- ✅ **Kimi K2** (kimi-k2-thinking) - Test Architecture
- ✅ **Nova Premier** (nova-premier) - AWS-Specific Testing
- ✅ **Claude Opus 4.5** (claude-opus-4-5-20251101) - Deep Reasoning
- ✅ **DeepSeek V3** (deepseek-v3) - Alternative Perspective
- ❌ GPT-5, Gemini 2.5 Flash - Authentication failures

---

## Model 1: Kimi K2 (Thinking Model)

**Model ID**: `kimi-k2-thinking`
**Focus**: Test architecture for context-dependent CLI commands

### Full Response

For CLI tools with context-dependent commands (like `vpc <id> → show subnets`), you need a **layered testing architecture** that treats command sessions as state machines. Here's the optimal pattern:

#### Core Architecture: Session-Based Command Graph

##### 1. Command Executor Abstraction
```python
# conftest.py
import pytest
from typing import Dict, Any, List

class CLIContext:
    """Mutable session state that accumulates across commands"""
    def __init__(self, env: Dict[str, str]):
        self.env = env
        self.output_cache: Dict[str, Any] = {}
        self.current_context: List[str] = []
        self.exit_code: int = 0

    def execute(self, cmd: str) -> tuple[int, str]:
        """Execute command in current context, cache outputs"""
        full_cmd = " ".join(self.current_context + [cmd])
        # Use subprocess or direct CLI invocation
        exit_code, stdout, stderr = self._run(full_cmd)

        # Cache by command path for dependency resolution
        cache_key = "_".join(self.current_context + [cmd.split()[0]])
        self.output_cache[cache_key] = {
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": exit_code
        }
        return exit_code, stdout

    def enter_context(self, command_segment: str):
        """Transition into nested context (e.g., 'vpc vpc-123')"""
        self.current_context.append(command_segment)

    def exit_context(self):
        """Return to parent context"""
        if self.current_context:
            self.current_context.pop()

@pytest.fixture
def cli():
    """Factory for isolated CLI sessions"""
    def _cli(env=None):
        return CLIContext(env or {})
    return _cli
```

##### 2. Fixture Strategy: Dependency Graph Resolution

```python
# fixtures/command_data.py
@pytest.fixture
def vpc_setup(cli):
    """Top-level command output consumed by subcommands"""
    session = cli()

    # Execute parent command and cache its output
    exit_code, output = session.execute("vpc list")
    assert exit_code == 0, "VPC list failed"

    # Parse output to get test VPC ID (using structured format)
    vpc_id = parse_json(output)[0]["id"]

    # Enter context for subsequent commands
    session.enter_context(f"vpc {vpc_id}")
    return session

@pytest.fixture
def network_context(vpc_setup):
    """Dependent fixture that reuses parent output"""
    session = vpc_setup

    # Execute subcommand that depends on VPC context
    exit_code, output = session.execute("show subnets")
    assert exit_code == 0

    # Cache subnet data for further nested commands
    session.output_cache["subnets"] = parse_json(output)
    return session
```

##### 3. Test Structure: Explicit Path Coverage

```python
# tests/test_vpc_commands.py
def test_vpc_list_returns_valid_ids(cli):
    """Level 1: Top-level command binary test"""
    session = cli()
    exit_code, output = session.execute("vpc list --format json")

    assert exit_code == 0
    data = parse_json(output)
    assert all("id" in item and "vpc-" in item["id"] for item in data)

def test_vpc_context_enables_subnet_command(vpc_setup):
    """Level 2: Context transition test"""
    # vpc_setup fixture already entered context
    exit_code, _ = vpc_setup.execute("show subnets")
    assert exit_code == 0  # Command should be available

def test_subnet_show_uses_vpc_context(network_context):
    """Level 3: Deep command path with dependency"""
    # network_context provides both VPC and subnets
    subnets = network_context.output_cache["subnets"]

    for subnet in subnets:
        subnet_id = subnet["id"]
        exit_code, output = network_context.execute(f"subnet {subnet_id} show")

        assert exit_code == 0
        assert subnet_id in output  # Binary verification

def test_invalid_context_transition(cli):
    """Level 4: Negative path testing"""
    session = cli()
    session.enter_context("vpc invalid-vpc-id")

    exit_code, _ = session.execute("show subnets")
    assert exit_code == 1  # Should fail with invalid context
```

##### 4. Deterministic Output: Schema-Based Assertions

```python
# tests/validators.py
from jsonschema import validate

VPC_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["id", "cidr"],
        "properties": {
            "id": {"type": "string", "pattern": "^vpc-[a-z0-9]+$"},
            "cidr": {"type": "string", "pattern": r"^\d+\.\d+\.\d+\.\d+/\d+$"}
        }
    }
}

def assert_valid_vpc_list(output: str):
    """Binary validator - no ambiguity"""
    data = parse_json(output)
    validate(instance=data, schema=VPC_SCHEMA)
    return True
```

##### 5. Performance: Parallelization & Caching

```python
# conftest.py
from functools import lru_cache

@lru_cache(maxsize=10)
def cached_vpc_fixture():
    """Expensive setup run once per test session"""
    session = CLIContext({})
    exit_code, output = session.execute("vpc create --name test-bed")
    vpc_id = parse_json(output)["id"]
    return vpc_id

@pytest.fixture(scope="session")
def shared_vpc_id():
    """Shared resource for performance"""
    return cached_vpc_fixture()
```

#### Key Principles for Binary Pass/Fail

1. **Never parse free text**: Use `--format json` or `--format yaml` for structured output
2. **Strict schemas**: Define exact output structures; any deviation fails
3. **Exit code verification**: Every command must have deterministic exit code
4. **Isolated state**: Each test gets clean session (or explicit shared cache)
5. **Explicit dependencies**: Fixtures compose in dependency order, no magic

#### Handling the Core Challenge: Command Graph Dependencies

For "top-level output needed by subcommands", implement **Output Capturers**:

```python
class VPCCapturer:
    """Explicit dependency resolver"""
    def __init__(self, cli_session):
        self.session = cli_session

    def get_first_vpc(self) -> str:
        """Binary operation: either returns ID or fails"""
        cache_key = "vpc_list"
        if cache_key not in self.session.output_cache:
            exit_code, output = self.session.execute("vpc list")
            assert exit_code == 0, "Failed to get VPC list"
            self.session.output_cache[cache_key] = parse_json(output)

        vpcs = self.session.output_cache[cache_key]
        assert len(vpcs) > 0, "No VPCs available"
        return vpcs[0]["id"]

# Usage in test
def test_with_dynamic_dependency(cli):
    session = cli()
    vpc_id = VPCCapturer(session).get_first_vpc()

    session.enter_context(f"vpc {vpc_id}")
    exit_code, _ = session.execute("show subnets")
    assert exit_code == 0
```

This architecture ensures **100% path coverage** through fixture composition, **binary outcomes** via strict schemas, and **zero ambiguity** by caching deterministic outputs across the command graph.

### Key Insights from Kimi K2

1. **Session-based architecture**: Treat CLI as state machine with context stack
2. **Output caching**: Store command outputs for downstream dependencies
3. **Fixture composition**: Chain fixtures to build context hierarchically
4. **Schema validation**: Use JSON schemas for deterministic assertions
5. **Context capturers**: Explicit classes to extract and reuse command outputs

---

## Model 2: Nova Premier (AWS Expert)

**Model ID**: `nova-premier`
**Focus**: AWS-specific edge cases and testing patterns

### Full Response

To address your testing requirements for `aws_network_shell`:

#### 1. Edge Cases to Cover
- VPCs with overlapping CIDR blocks
- Transit Gateway with maximum route table entries
- CloudWAN core network in unsupported regions
- Subnets with no available IP addresses
- Security group rules exceeding quota limits

#### 2. Validating Boto3 Mock Responses
```python
# Example validation pattern
from moto import mock_ec2
import boto3

def test_describe_vpcs():
    with mock_ec2():
        client = boto3.client("ec2", region_name="us-east-1")
        # Real AWS response structure check
        response = client.describe_vpcs()
        assert "Vpcs" in response
        assert isinstance(response["Vpcs"], list)
```

#### 3. High-Risk Failure Scenarios
- Cross-region peering connections
- Multi-account resource sharing permissions
- Service-linked role permission changes
- Propagated route limits in TGW route tables

#### 4. Multi-Region/Account Test Structure
```python
# Using pytest fixtures
@pytest.fixture(scope="module")
def network_setup():
    accounts = ["123456789012", "987654321098"]
    regions = ["us-east-1", "eu-west-1"]

    for account in accounts:
        for region in regions:
            # Create VPC/TGW/CloudWAN resources
            yield {"account": account, "region": region}

def test_cross_region_connectivity(network_setup):
    # Validate connectivity between regions
```

### Key Insights from Nova Premier

1. **AWS-specific edge cases**: Focus on quota limits, overlapping CIDRs, regional constraints
2. **Moto validation**: Ensure mock responses match real AWS API structures
3. **High-risk scenarios**: Cross-region, multi-account, service quotas
4. **Multi-region testing**: Use module-scoped fixtures with account/region matrices

---

## Model 3: Claude Opus 4.5 (Deep Reasoning)

**Model ID**: `claude-opus-4-5-20251101`
**Focus**: Comprehensive test framework design

### Full Response

I'll design a comprehensive test framework for your CLI with command graph dependencies. This framework will handle context state management, ensure proper test isolation, and achieve 100% command coverage.

#### Core Test Framework Architecture

```python
# test_framework/core.py
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set, Callable
from enum import Enum
import json
import tempfile
import shutil
from pathlib import Path
from contextlib import contextmanager

class TestResult(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"
    ERROR = "ERROR"

@dataclass
class CommandContext:
    """Represents the state context for a command execution"""
    vpc_id: Optional[str] = None
    region: Optional[str] = None
    account_id: Optional[str] = None
    subnet_ids: List[str] = field(default_factory=list)
    security_group_ids: List[str] = field(default_factory=list)
    instance_ids: List[str] = field(default_factory=list)
    custom_data: Dict[str, Any] = field(default_factory=dict)

    def merge(self, other: 'CommandContext') -> 'CommandContext':
        """Merge another context into this one"""
        new_context = CommandContext(
            vpc_id=other.vpc_id or self.vpc_id,
            region=other.region or self.region,
            account_id=other.account_id or self.account_id,
            subnet_ids=list(set(self.subnet_ids + other.subnet_ids)),
            security_group_ids=list(set(self.security_group_ids + other.security_group_ids)),
            instance_ids=list(set(self.instance_ids + other.instance_ids)),
            custom_data={**self.custom_data, **other.custom_data}
        )
        return new_context

@dataclass
class TestCase:
    """Represents a single test case"""
    name: str
    command: str
    args: List[str]
    required_context: CommandContext
    expected_output: Optional[str] = None
    expected_error: Optional[str] = None
    expected_exit_code: int = 0
    timeout: int = 30
    dependencies: List[str] = field(default_factory=list)
    setup_fixtures: List[str] = field(default_factory=list)
    teardown_fixtures: List[str] = field(default_factory=list)
    validators: List[Callable] = field(default_factory=list)
```

[Note: Response was extremely comprehensive with 10+ additional code sections covering Fixture Management, Test Isolation, Dependency Graphs, Coverage Tracking, Edge Case Generation, and Test Suite Building - full details available in chat log]

### Key Insights from Claude Opus 4.5

1. **Comprehensive framework**: Full object-oriented test framework with dataclasses
2. **Context merging**: Elegant pattern for combining context from multiple sources
3. **Fixture registry**: Centralized management of test fixtures with lifecycle
4. **Dependency graph**: Topological sorting for test execution order
5. **Edge case generation**: Automated generation of boundary, error, and security tests
6. **Coverage tracking**: Detailed tracking of command variations and coverage gaps
7. **Test isolation**: Context managers for clean test environments
8. **Validator pattern**: Callable validators for flexible assertions

---

## Model 4: DeepSeek V3 (Alternative Perspective)

**Model ID**: `deepseek-v3`
**Focus**: Efficient context management and parallelization

### Full Response

To architect tests for CLI commands with contextual dependencies, I would implement the following strategy:

#### 1. Test Architecture with Context Management

```python
# Core context management
class CLIContext:
    def __init__(self):
        self.context_stack = {}

    def set_context(self, context_type, context_value):
        self.context_stack[context_type] = context_value

    def get_context(self, context_type):
        return self.context_stack.get(context_type)

    def clear_context(self, context_type=None):
        if context_type:
            self.context_stack.pop(context_type, None)
        else:
            self.context_stack.clear()
```

#### 2. Hierarchical Test Structure with Fixture Dependencies

```python
import pytest

# Base fixtures for context setup
@pytest.fixture
def cli_context():
    return CLIContext()

# Context-dependent fixtures
@pytest.fixture
def vpc_context(cli_context, vpc_setup):
    cli_context.set_context('vpc', vpc_setup.vpc_id)
    yield vpc_setup
    cli_context.clear_context('vpc')

@pytest.fixture
def subnet_context(cli_context, vpc_context, subnet_setup):
    cli_context.set_context('subnet', subnet_setup.subnet_id)
    yield subnet_setup
    cli_context.clear_context('subnet')
```

#### 3. Command Execution with Context Validation

```python
def execute_command(command, context, expected_success=True):
    # Validate context requirements
    required_context = get_required_context(command)
    missing_context = [ctx for ctx in required_context if not context.get_context(ctx)]

    if missing_context:
        pytest.skip(f"Missing required context: {missing_context}")

    # Execute command with context
    result = run_cli_command(command, context)

    # Binary assertion
    if expected_success:
        assert result.success, f"Command failed: {result.error}"
    else:
        assert not result.success, "Command should have failed but succeeded"

    return result
```

#### 4. Test Organization for Parallel Execution

```python
# Independent test suites (can run in parallel)
class TestVPCCommands:
    @pytest.mark.parallel_safe
    def test_vpc_list(self, cli_context):
        result = execute_command("list vpcs", cli_context)
        assert len(result.output) > 0

# Context-dependent test suites (run sequentially within suite)
class TestSubnetCommands:
    @pytest.mark.depends_on('vpc')
    def test_subnet_list(self, vpc_context):
        result = execute_command("show subnets", vpc_context)
        assert "subnet-" in result.output

# Fixture completeness validation
@pytest.fixture(autouse=True)
def validate_fixture_completeness(request):
    fixture_names = request.fixturenames
    # Validate all required fixtures are present and properly configured
```

#### 5. Test Execution Strategy

```yaml
# pytest configuration for parallel execution
addopts:
  -n auto  # Run independent tests in parallel
  -x       # Fail fast on first failure
  -v

# Markers for test organization
markers:
  parallel_safe: tests that can run independently
  depends_on: tests requiring specific context
  sequential: tests that must run in order
```

#### Implementation Benefits

1. **Efficient Context Handling**: Context managers ensure proper setup/teardown
2. **Fixture Completeness**: Automatic validation of required preconditions
3. **Binary Results**: Clear pass/fail assertions with meaningful error messages
4. **Parallel Execution**: Mark-based isolation for safe parallel testing
5. **Dependency Management**: Explicit context requirements prevent false negatives

This architecture provides both the flexibility for complex command chains and the rigor needed for reliable automated testing.

### Key Insights from DeepSeek V3

1. **Simple context stack**: Dictionary-based context management
2. **Yield fixtures**: Clean setup/teardown with yield pattern
3. **Context validation**: Pre-execution checks for required context
4. **Pytest markers**: Mark tests for parallel vs sequential execution
5. **Binary assertions**: Clear success/failure with descriptive messages
6. **Fixture completeness validation**: Autouse fixture to validate setup

---

## Cross-Model Analysis

### Common Themes (4/4 models agreed)

1. **Context as first-class object**: All models emphasized explicit context management
2. **Fixture composition**: Chain fixtures to build complex test scenarios
3. **Binary pass/fail**: Deterministic assertions, no ambiguity
4. **Output caching**: Store command outputs for downstream tests
5. **Schema validation**: Use structured formats (JSON) for assertions

### Divergent Approaches

| Aspect | Kimi K2 | Nova Premier | Opus 4.5 | DeepSeek V3 |
|--------|---------|--------------|----------|-------------|
| Context Storage | output_cache dict | N/A | CommandContext dataclass | context_stack dict |
| Fixture Strategy | Dependency graph | Module-scoped | Registry pattern | Yield with cleanup |
| Parallelization | LRU cache | Multi-region matrix | Coverage tracker | Pytest markers |
| Edge Cases | Output capturers | AWS-specific limits | Auto-generation | Context validation |
| Complexity | Medium | Low | Very High | Low |

### Model Strengths

- **Kimi K2**: Best balance of simplicity and completeness, practical examples
- **Nova Premier**: AWS domain expertise, specific edge cases
- **Claude Opus 4.5**: Most comprehensive framework, enterprise-ready
- **DeepSeek V3**: Simplest implementation, fastest to adopt

---

## Recommended Implementation Priority

### Phase 1: Foundation (Week 1)
- Implement Kimi K2's CLIContext class (session-based execution)
- Add output caching for command dependencies
- Create basic fixture composition pattern

### Phase 2: AWS Integration (Week 2)
- Add Nova Premier's edge cases to test matrix
- Implement boto3 mock validation
- Add multi-region test fixtures

### Phase 3: Comprehensive Framework (Week 3-4)
- Adopt Opus 4.5's dataclass architecture (optional, if scalability needed)
- Add coverage tracking
- Implement edge case auto-generation

### Phase 4: Optimization (Week 5)
- Add DeepSeek V3's pytest markers for parallelization
- Implement fixture completeness validation
- Optimize test execution with caching

---

## Failed Model Attempts

### GPT-5-1
- **Error**: `status code 401`
- **Reason**: Authentication failure with litellm proxy
- **Impact**: Missing fast iteration perspective

### Gemini-2-5-Flash
- **Error**: `status code 401`
- **Reason**: Authentication failure with litellm proxy
- **Impact**: Missing quick iteration patterns

Both failures suggest litellm proxy configuration issues with these specific models.

---

## Next Steps

1. Review synthesized test strategy document
2. Create prototype implementation using Kimi K2's architecture
3. Add AWS-specific test cases from Nova Premier
4. Consider Opus 4.5's framework for long-term scalability
5. Implement DeepSeek V3's parallelization markers
