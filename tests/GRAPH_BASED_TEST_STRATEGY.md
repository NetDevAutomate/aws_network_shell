# Graph-Based Command Testing Strategy

## Problem Statement

Testing `set` subcommands requires output from top-level `show` commands to select valid resource indices. Without proper mocking chain, tests fail.

## Solution: Dependency-Aware Mocking

### Key Insight

The shell uses a **Client.discover()** pattern:
```python
# Handler calls:
vpc.VPCClient(self.profile).discover()  # Returns list
vpc.VPCClient(self.profile).get_vpc_detail(vpc_id, region)  # Returns detail
```

### Mock Chain Required

```
show vpcs → VPCClient.discover() → returns list
set vpc 1 → VPCClient.get_vpc_detail() → returns detail (ALSO NEEDED!)
vpc> show detail → uses cached detail
```

## Implementation

### 1. Fixture Data Generators (`tests/fixtures/command_fixtures.py`)

```python
def _vpcs_list():
    """Generate VPC list in shell's expected format."""
    return [
        {"id": vpc_id, "name": get_tag_value(vpc), "region": "eu-west-1",
         "cidr": vpc["CidrBlock"], "cidrs": [vpc["CidrBlock"]], "state": vpc["State"]}
        for vpc_id, vpc in VPC_FIXTURES.items()
    ]
```

### 2. Context Entry Pattern

```python
@pytest.fixture
def shell_in_vpc(self):
    shell = AWSNetShell()
    vpcs = _vpcs_list()
    vpc_detail = get_vpc_detail(vpcs[0]["id"])
    
    # BOTH mocks required
    p1 = patch("aws_network_tools.modules.vpc.VPCClient.discover", return_value=vpcs)
    p2 = patch("aws_network_tools.modules.vpc.VPCClient.get_vpc_detail", return_value=vpc_detail)
    p1.start()
    p2.start()
    
    shell.onecmd("show vpcs")
    shell.onecmd("set vpc 1")
    
    yield shell
    
    p1.stop()
    p2.stop()
```

### 3. Mock Targets by Resource Type

| Resource | List Mock | Detail Mock |
|----------|-----------|-------------|
| VPC | `vpc.VPCClient.discover` | `vpc.VPCClient.get_vpc_detail` |
| TGW | `tgw.TGWClient.discover` | (uses discover data) |
| Firewall | `anfw.ANFWClient.discover` | (uses discover data) |
| EC2 | `ec2.EC2Client.discover` | `ec2.EC2Client.get_instance_detail` |
| ELB | `elb.ELBClient.discover` | `elb.ELBClient.get_elb_detail` |
| VPN | `vpn.VPNClient.discover` | `vpn.VPNClient.get_vpn_detail` |

## Test Results

Current coverage with graph-based tests:
- **21 tests passing** (root show + context entry + context commands)
- **8 tests failing** (missing mock fields)
- **5 errors** (unmocked API calls)

### Passing Tests
- Root show commands: `show vpcs`, `show transit_gateways`, `show firewalls`, etc.
- Context entry: `set vpc`, `set transit-gateway`, `set firewall`
- TGW context: `show detail`, `show route-tables`, `show attachments`
- VPC context: `show security-groups` (partial)

### Remaining Work

1. **Fix fixture field mismatches**: Ensure mock data has all required fields
2. **Mock additional API calls**: Some handlers make secondary calls
3. **Add action command tests**: `find_prefix`, `find_null_routes`, etc.

## Command Coverage Matrix

| Context | Show | Set | Action | Total | Tested |
|---------|------|-----|--------|-------|--------|
| root | 30 | 15 | 9 | 54 | 6 |
| vpc | 8 | 1 | 2 | 11 | 5 |
| transit-gateway | 3 | 1 | 2 | 6 | 3 |
| firewall | 4 | 0 | 2 | 6 | 3 |
| ec2-instance | 4 | 0 | 2 | 6 | 0 |
| elb | 4 | 0 | 2 | 6 | 3 |
| vpn | 2 | 0 | 2 | 4 | 0 |
| global-network | 2 | 1 | 2 | 5 | 0 |
| core-network | 12 | 1 | 2 | 15 | 0 |
| route-table | 1 | 0 | 2 | 3 | 0 |
| **Total** | **70** | **19** | **25** | **114** | **20** |

## Running Tests

```bash
# Run all graph tests
pytest tests/test_graph_commands.py -v --no-cov

# Run specific context
pytest tests/test_graph_commands.py -k "vpc" -v --no-cov

# Run with coverage
pytest tests/test_graph_commands.py --cov=aws_network_tools
```

## Next Steps

1. **Complete fixture field mapping** - Ensure all mock data matches handler expectations
2. **Add secondary API mocks** - EC2, VPN handlers make additional calls
3. **Test action commands** - `find_prefix`, `find_null_routes`, `trace`
4. **Add global-network/core-network tests** - CloudWAN context chain
5. **Generate coverage report** - Track tested vs untested commands

## Files Created

- `tests/fixtures/command_fixtures.py` - Command-to-fixture mapping
- `tests/test_graph_commands.py` - Graph-based parametrized tests
- `tests/GRAPH_BASED_TEST_STRATEGY.md` - This document
