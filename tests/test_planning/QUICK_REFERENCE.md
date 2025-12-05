# AWS Network Shell - Testing Quick Reference

**Purpose**: Fast lookup guide for test implementation

---

## Command Counts by Context

| Context | Show | Set | Action | Total |
|---------|------|-----|--------|-------|
| **root** | 30 | 15 | 9 | 59 |
| **global-network** | 2 | 1 | 0 | 3 |
| **core-network** | 12 | 1 | 2 | 15 |
| **route-table** | 1 | 0 | 2 | 3 |
| **vpc** | 8 | 1 | 2 | 11 |
| **transit-gateway** | 3 | 1 | 2 | 6 |
| **firewall** | 4 | 0 | 0 | 4 |
| **ec2-instance** | 4 | 0 | 0 | 4 |
| **elb** | 4 | 0 | 0 | 4 |
| **vpn** | 2 | 0 | 0 | 2 |
| **TOTAL** | **70** | **19** | **19** | **111** |

---

## Context Entry Quick Reference

```python
# From root to any context
"set vpc <ref>"              → vpc context
"set transit-gateway <ref>"  → transit-gateway context
"set global-network <ref>"   → global-network context
"set firewall <ref>"         → firewall context
"set ec2-instance <ref>"     → ec2-instance context
"set elb <ref>"              → elb context
"set vpn <ref>"              → vpn context

# From global-network
"set core-network <ref>"     → core-network context

# From core-network, vpc, or transit-gateway
"set route-table <ref>"      → route-table context

# Navigation
"exit"                       → Back one level
"end"                        → Return to root
```

---

## Most Commonly Used Commands

### Top 10 by Expected Usage
1. `show vpcs` - List all VPCs
2. `set vpc <ref>` - Enter VPC context
3. `show detail` - Show context resource details
4. `show subnets` - List VPC subnets
5. `show route-tables` - List route tables (context-aware)
6. `find_prefix <cidr>` - Find routes for prefix (context-aware)
7. `show transit_gateways` - List all TGWs
8. `set transit-gateway <ref>` - Enter TGW context
9. `trace <src> <dst>` - Network path trace
10. `find_ip <ip>` - Locate IP in ENIs

---

## Context-Aware Commands

These commands behave differently based on context:

### `find_prefix <cidr>`
- **root**: Searches routing cache (all resources)
- **vpc**: Searches VPC route tables only
- **transit-gateway**: Searches TGW route tables only
- **core-network**: Searches CloudWAN route tables only
- **route-table**: Searches specific route table only

### `find_null_routes`
- **root**: All blackhole routes from cache
- **vpc**: VPC blackhole routes only
- **transit-gateway**: TGW blackhole routes only
- **core-network**: CloudWAN blackhole routes only
- **route-table**: Route table blackhole routes only

### `show route-tables`
- **vpc**: VPC route tables
- **transit-gateway**: TGW route tables
- **core-network**: CloudWAN route tables
- **ec2-instance**: Instance-associated route tables

### `show detail`
- **global-network**: Global network metadata
- **core-network**: Core network with policy
- **vpc**: VPC CIDR, subnets, gateways
- **transit-gateway**: TGW config and ASN
- **firewall**: Firewall configuration
- **ec2-instance**: Instance state and networking
- **elb**: Load balancer configuration
- **vpn**: VPN tunnels and status

---

## Test Template

```python
def test_<context>_<command>_<scenario>(self, mock_shell_with_fixtures):
    """Test <command> in <context> for <scenario>."""
    # Setup: Establish preconditions
    # - Enter context if needed
    # - Configure shell settings
    # - Prepare test data

    # Execute: Run the command
    # - Call shell method or onecmd()
    # - Capture output if needed

    # Assert: Verify expected behavior
    # - Check context state
    # - Verify output content
    # - Validate data structure

    # Cleanup: (if needed)
    # - Clear context
    # - Reset shell state
```

---

## Common Test Patterns

### Pattern 1: Show Command in Root Context
```python
def test_show_vpcs_valid_data(self, mock_shell_with_fixtures):
    """Test show vpcs with valid fixture data."""
    result = mock_shell_with_fixtures.onecmd("show vpcs")
    assert mock_shell_with_fixtures.ctx_type is None
    # Verify output contains fixture VPCs
```

### Pattern 2: Context Entry
```python
def test_set_vpc_by_index(self, mock_shell_with_fixtures):
    """Test entering VPC context by index."""
    mock_shell_with_fixtures.onecmd("set vpc 1")
    assert mock_shell_with_fixtures.ctx_type == "vpc"
    assert len(mock_shell_with_fixtures.context_stack) == 1
    assert mock_shell_with_fixtures.ctx.ref == "1"
```

### Pattern 3: Context Show Command
```python
def test_vpc_show_subnets(self, mock_shell_with_fixtures):
    """Test show subnets in VPC context."""
    mock_shell_with_fixtures.onecmd("set vpc 1")
    result = mock_shell_with_fixtures.onecmd("show subnets")
    assert mock_shell_with_fixtures.ctx_type == "vpc"
    # Verify subnets from fixture displayed
```

### Pattern 4: Context-Aware Command
```python
def test_find_prefix_vpc_context(self, mock_shell_with_fixtures):
    """Test find_prefix searches only VPC routes in VPC context."""
    mock_shell_with_fixtures.onecmd("set vpc 1")
    result = mock_shell_with_fixtures.onecmd("find_prefix 10.0.0.0/16")
    # Verify only VPC routes displayed, not TGW or CloudWAN
```

### Pattern 5: Error Handling
```python
def test_set_vpc_invalid_ref(self, mock_shell_with_fixtures):
    """Test set vpc with invalid reference."""
    mock_shell_with_fixtures.onecmd("set vpc 999")
    assert mock_shell_with_fixtures.ctx_type is None  # Context not changed
    # Verify error message displayed
```

---

## Fixture Access Patterns

### Load All Fixtures
```python
@pytest.fixture
def mock_shell_with_fixtures(all_fixtures):
    """Shell with all fixtures pre-loaded."""
    from aws_network_tools.shell import AWSNetShell
    shell = AWSNetShell()
    shell._cache["vpcs"] = all_fixtures["vpcs"]["vpcs"]
    shell._cache["tgw"] = all_fixtures["transit_gateways"]["transit_gateways"]
    # ... load all fixtures
    return shell
```

### Access Specific Fixture
```python
def test_with_specific_vpc(self, vpcs):
    """Test using specific VPC fixture."""
    production_vpc = vpcs[0]  # First VPC from fixture
    assert production_vpc["name"] == "production-vpc"
```

---

## Known Issues Quick Reference

### Issue #9: EC2 Context Filtering
**Status**: OPEN | **Severity**: HIGH
**Commands**: `ec2-instance> show enis`, `ec2-instance> show security-groups`
**Problem**: Returns ALL account resources instead of instance-specific
**Test**: `tests/test_issue_9_ec2_filtering.py`

### Issue #10: ELB Data Retrieval
**Status**: OPEN | **Severity**: HIGH
**Commands**: `elb> show listeners`, `elb> show targets`, `elb> show health`
**Problem**: Returns "No data" for valid ELBs
**Test**: `tests/test_issue_10_elb_data.py`

---

## Output Format Handling

### Testing Each Format
```python
# Table format (default)
shell.output_format = "table"
shell.onecmd("show vpcs")
# Assert: Rich table rendered

# JSON format
shell.output_format = "json"
shell.onecmd("show vpcs")
# Assert: Valid JSON structure

# YAML format
shell.output_format = "yaml"
shell.onecmd("show vpcs")
# Assert: Valid YAML structure
```

---

## Pipe Operator Testing

### Syntax
```bash
show <command> | include <pattern>
show <command> | exclude <pattern>
show <command> | grep <pattern>
```

### Testing Pattern
```python
def test_pipe_include(self, mock_shell_with_fixtures):
    """Test | include filter."""
    result = mock_shell_with_fixtures.onecmd("show vpcs | include production")
    # Assert: Only rows containing "production" in output
```

---

## Watch Mode Testing

### Syntax
```bash
show <command> watch <interval>
```

### Testing Pattern
```python
def test_watch_mode(self, mock_shell_with_fixtures):
    """Test watch mode execution."""
    import threading

    # Start watch in thread
    def run_watch():
        mock_shell_with_fixtures.onecmd("show vpcs watch 1")

    thread = threading.Thread(target=run_watch)
    thread.start()

    # Wait and interrupt
    import time
    time.sleep(2.5)  # Should execute ~2 times
    thread.join(timeout=1)

    # Assert: Command executed multiple times
```

---

## Test Execution Shortcuts

```bash
# Run single test
pytest tests/test_vpc_context.py::TestVPCContext::test_vpc_show_subnets -v

# Run by marker
pytest -m "root_commands" -v

# Run by keyword
pytest -k "vpc" -v

# Run with coverage
pytest tests/test_vpc_context.py --cov=src/aws_network_tools/shell/handlers/vpc --cov-report=term-missing

# Run fast tests only (skip integration)
pytest -m "not integration" -v

# Run until first failure
pytest tests/ -x

# Run in parallel
pytest tests/ -n auto
```

---

## Common Assertions

### Context State
```python
assert shell.ctx_type == "vpc"
assert shell.ctx_type is None
assert len(shell.context_stack) == 1
assert shell.ctx.ref == "1"
assert shell.ctx.name == "production-vpc"
assert shell.ctx.data["id"] == "vpc-0a1b2c3d"
```

### Output Validation
```python
# Check output contains expected text
assert "vpc-0a1b2c3d" in captured_output
assert "production-vpc" in captured_output

# Check error messages
assert "[red]" in captured_output
assert "Error" in captured_output

# Check table structure (if using Rich table)
assert table.row_count == 3
assert "VPC ID" in table.columns
```

### Cache Validation
```python
assert "vpcs" in shell._cache
assert len(shell._cache["vpcs"]) == 3
assert shell.no_cache == True
```

---

## Test Priority Quick Guide

### P0 (Must Have) - 80 tests
- Root show commands (30)
- Context entry (32)
- Navigation (12)
- Issues #9 & #10 (6)

### P1 (Should Have) - 80 tests
- Context show commands (52)
- Action commands (18)
- Error handling (10)

### P2 (Nice to Have) - 39 tests
- Output formats (24)
- Pipe operators (10)
- Watch mode (5)

### P3 (Future) - 15 tests
- Edge cases (15)

**Total**: 214 tests

---

## Critical Paths for Testing

### Path 1: VPC Investigation Workflow
```bash
show vpcs                    # List VPCs
set vpc 1                    # Enter VPC context
show detail                  # View VPC details
show subnets                 # List subnets
show route-tables            # View routing
find_prefix 10.0.0.0/16      # Find specific routes
find_null_routes             # Check for blackholes
exit                         # Return to root
```

### Path 2: CloudWAN Investigation
```bash
show global-networks         # List global networks
set global-network 1         # Enter global network
show core-networks           # List core networks
set core-network 1           # Enter core network
show segments                # View segments
show route-tables            # View CloudWAN routing
show rib segment=production  # View RIB for segment
find_prefix 10.0.0.0/8       # Search CloudWAN routes
end                          # Return to root
```

### Path 3: Instance Troubleshooting
```bash
show ec2-instances           # List instances
set ec2-instance 1           # Enter instance context
show detail                  # View instance details
show enis                    # View instance ENIs (ISSUE #9)
show security-groups         # View instance SGs (ISSUE #9)
show routes                  # View instance routing
exit                         # Return to root
```

### Path 4: Load Balancer Investigation
```bash
show elbs                    # List load balancers
set elb 1                    # Enter ELB context
show detail                  # View ELB configuration
show listeners               # View listeners (ISSUE #10)
show targets                 # View target groups (ISSUE #10)
show health                  # View health status (ISSUE #10)
exit                         # Return to root
```

---

## Test Data Shortcuts

### Fixture References
```python
# VPC IDs
production_vpc = "vpc-0a1b2c3d4e5f6g7h8"
test_vpc = "vpc-9z8y7x6w5v4u3t2s1"
default_vpc = "vpc-default123456789"

# TGW IDs
production_tgw = "tgw-0a1b2c3d4e5f6g7h8"
test_tgw = "tgw-9z8y7x6w5v4u3t2s1"

# Core Network IDs
prod_core = "core-network-0a1b2c3d4e5f"
staging_core = "core-network-9z8y7x6w5v4u"

# Instance IDs
prod_web = "i-0a1b2c3d4e5f6g7h8"
test_instance = "i-9z8y7x6w5v4u3t2s1"
unnamed_instance = "i-fedcba0987654321"

# ELB ARNs
production_alb = "arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/production-alb/50dc6c495c0c9188"
github_alb = "arn:aws:elasticloadbalancing:us-east-1:545009866561:loadbalancer/app/Github-ALB/02d64eddbcd409ff"
```

### CIDRs for Testing
```python
# Valid prefixes in fixtures
"10.0.0.0/16"      # production-vpc CIDR
"172.16.0.0/16"    # test-vpc CIDR
"192.168.0.0/16"   # Appears in TGW routes
"10.0.0.0/8"       # Broad prefix for aggregation

# Blackhole routes
"192.168.0.0/16"   # In TGW route table (blackhole)
"192.168.1.0/24"   # In VPC route table (blackhole)
```

---

## Testing Checklist

### Before Writing Tests
- [ ] Read command_graph_analysis.md for command structure
- [ ] Review fixture_requirements.md for test data
- [ ] Check test_roadmap.md for specific test cases
- [ ] Verify fixtures are created and valid

### When Writing Tests
- [ ] Use descriptive test names
- [ ] Include docstrings explaining what's tested
- [ ] Follow Setup → Execute → Assert pattern
- [ ] Test both success and failure cases
- [ ] Add tests for edge cases (empty data, null values)

### After Writing Tests
- [ ] Run tests locally: `pytest tests/test_<file>.py -v`
- [ ] Check coverage: `pytest --cov`
- [ ] Verify no test pollution (tests pass in isolation)
- [ ] Update test count in documentation
- [ ] Submit PR with tests and fixture updates

---

## Command Testing Matrix

### Test Each Command For:
- ✅ Valid execution with data
- ✅ Valid execution with empty data
- ✅ Invalid arguments
- ✅ Missing required arguments
- ✅ Wrong context execution
- ✅ Output format variations (table/json/yaml)
- ✅ Pipe operator compatibility
- ✅ Watch mode compatibility (show commands only)

### Example: Testing `show vpcs`
```python
class TestShowVPCs:
    def test_show_vpcs_with_data(self, fixtures): pass         # Valid data
    def test_show_vpcs_empty(self, mock_shell): pass           # Empty cache
    def test_show_vpcs_json(self, fixtures): pass              # JSON format
    def test_show_vpcs_yaml(self, fixtures): pass              # YAML format
    def test_show_vpcs_pipe_include(self, fixtures): pass      # Pipe filter
    def test_show_vpcs_watch_mode(self, fixtures): pass        # Watch mode
    # 6 tests per show command
```

---

## Fixture Validation

### Required Fields Check
```python
def validate_vpc_fixture(vpc):
    """Validate VPC fixture has required fields."""
    required = ["id", "name", "region", "cidr", "state"]
    for field in required:
        assert field in vpc, f"Missing required field: {field}"

    # Validate nested structures
    assert "route_tables" in vpc
    assert isinstance(vpc["route_tables"], list)
```

### Relationship Validation
```python
def validate_ec2_instance_fixture(instance, vpcs):
    """Validate EC2 instance references valid VPC."""
    vpc_id = instance["vpc_id"]
    vpc_ids = [v["id"] for v in vpcs]
    assert vpc_id in vpc_ids, f"Instance references invalid VPC: {vpc_id}"
```

---

## Mock Shell Setup

### Basic Mock Shell
```python
@pytest.fixture
def mock_shell():
    """Basic shell without fixtures."""
    from aws_network_tools.shell import AWSNetShell
    return AWSNetShell()
```

### Shell with Fixtures
```python
@pytest.fixture
def mock_shell_with_fixtures(all_fixtures):
    """Shell with pre-loaded fixtures."""
    from aws_network_tools.shell import AWSNetShell
    shell = AWSNetShell()

    # Pre-populate cache
    shell._cache["vpcs"] = all_fixtures["vpcs"]["vpcs"]
    shell._cache["tgw"] = all_fixtures["transit_gateways"]["transit_gateways"]
    shell._cache["global-networks"] = all_fixtures["global_networks"]["global_networks"]
    shell._cache["ec2-instances"] = all_fixtures["ec2_instances"]["ec2_instances"]
    shell._cache["elbs"] = all_fixtures["elbs"]["elbs"]
    shell._cache["firewalls"] = all_fixtures["firewalls"]["firewalls"]
    shell._cache["vpns"] = all_fixtures["vpns"]["vpns"]
    shell._cache["routing_cache"] = all_fixtures["routing_cache"]["routing_cache"]

    return shell
```

---

## Progress Tracking

### Test Count by File
```python
# tests/test_root_show_commands.py          → 30 tests ⏳
# tests/test_root_set_commands.py           → 15 tests ⏳
# tests/test_navigation_commands.py         → 12 tests ⏳
# tests/test_context_entry.py               → 32 tests ⏳
# tests/test_vpc_context.py                 → 11 tests ⏳
# tests/test_transit_gateway_context.py     → 6 tests ⏳
# tests/test_global_network_context.py      → 3 tests ⏳
# tests/test_core_network_context.py        → 15 tests ⏳
# tests/test_route_table_context.py         → 3 tests ⏳
# tests/test_firewall_context.py            → 4 tests ⏳
# tests/test_ec2_context.py                 → 4 tests ⏳
# tests/test_elb_context.py                 → 4 tests ⏳
# tests/test_vpn_context.py                 → 2 tests ⏳
# tests/test_action_commands.py             → 10 tests ⏳
# tests/test_context_aware_commands.py      → 10 tests ⏳
# tests/test_output_formats.py              → 24 tests ⏳
# tests/test_pipe_operators.py              → 10 tests ⏳
# tests/test_watch_mode.py                  → 5 tests ⏳
# tests/test_error_handling.py              → 15 tests ⏳
# tests/test_edge_cases.py                  → 15 tests ⏳
# tests/test_integration_workflows.py       → 10 tests ⏳
# tests/test_issue_9_ec2_filtering.py       → 5 tests ⏳
# tests/test_issue_10_elb_data.py           → 5 tests ⏳
# ============================================
# TOTAL:                                      240 tests
```

### Current Status (2024-12-04)
- **Implemented**: ~10 tests (4%)
- **Remaining**: ~230 tests (96%)
- **Target**: 240 tests (100% command coverage)

---

## Next Steps

1. **Create Fixtures**: Implement all 9 fixture JSON files
2. **Implement Phase 1**: Root commands + context entry (50 tests)
3. **Run & Validate**: Ensure fixtures work correctly
4. **Continue Phases**: Follow 5-week roadmap
5. **Issue Resolution**: Fix #9 and #10 with tests

---

## Quick Command Reference

```python
# Import for test development
from tests.test_planning.command_graph import (
    ALL_COMMANDS,
    get_commands_for_context,
    get_show_commands,
    get_context_entry_commands,
    CONTEXT_HIERARCHY,
    KNOWN_ISSUES,
)

# Get all VPC commands
vpc_commands = get_commands_for_context("vpc")

# Get all context entry commands
entry_commands = get_context_entry_commands()

# Check context hierarchy
parent_contexts = CONTEXT_HIERARCHY["route-table"]["parent"]  # ["vpc", "transit-gateway", "core-network"]
```

---

Last Updated: 2024-12-04
