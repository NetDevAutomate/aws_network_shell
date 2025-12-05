# AWS Network Shell - Test Planning Documentation

**Generated**: 2024-12-04
**Purpose**: Central hub for comprehensive test planning and implementation

---

## Quick Navigation

1. **[Command Graph Analysis](./command_graph_analysis.md)** - Complete command structure documentation
2. **[Command Graph (Python)](./command_graph.py)** - Programmatic access to command definitions
3. **[Fixture Requirements](./fixture_requirements.md)** - Test fixture specifications
4. **[Test Roadmap](./test_roadmap.md)** - Implementation plan and test case definitions

---

## Executive Summary

### Current State
- **Total Commands**: 111 unique commands across 10 contexts
- **Current Test Coverage**: ~10 tests (5% coverage)
- **Known Issues**: 2 open issues affecting 5 commands
- **Test Infrastructure**: Basic pytest setup, minimal fixtures

### Target State
- **Test Coverage**: 214+ tests (100% command coverage)
- **Code Coverage**: 90%+ line coverage
- **Issue Coverage**: All known issues have regression tests
- **Fixture Coverage**: 9 comprehensive fixture files

---

## Key Findings

### 1. Command Structure
The shell implements a **hierarchical context system** with:
- **10 contexts**: root + 9 specialized contexts
- **Context nesting**: Up to 4 levels deep (root → global-network → core-network → route-table)
- **Context-aware commands**: find_prefix, find_null_routes, show route-tables, show detail

### 2. Critical Issues

#### Issue #9: EC2 Context Filtering
**Commands Affected**: `show enis`, `show security-groups` in ec2-instance context
**Impact**: Returns all account resources instead of instance-specific data
**Priority**: HIGH

#### Issue #10: ELB Data Retrieval
**Commands Affected**: `show listeners`, `show targets`, `show health` in elb context
**Impact**: Returns "No data" for valid load balancers with data
**Priority**: HIGH

### 3. Test Gaps
Major testing gaps identified:
- Context-specific show commands (40+ untested)
- Context navigation and stack management (untested)
- Action commands (trace, find_ip, etc.) (mostly untested)
- Output format variations (json, yaml) (untested)
- Pipe operators and filtering (untested)
- Watch mode (untested)
- Error handling (minimal coverage)

---

## Command Categories

### By Type
- **Show Commands**: 56 (34 root + 22 context-specific)
- **Set Commands**: 13 (configuration + context entry)
- **Action Commands**: 12 (find, trace, cache, write)
- **Navigation**: 4 (exit, end, clear, ?)
- **Aliases**: 5 (sh, conf, ex, int, no)

### By Context
- **Root**: 59 commands
- **Global-Network**: 3 commands
- **Core-Network**: 15 commands
- **Route-Table**: 3 commands
- **VPC**: 11 commands
- **Transit-Gateway**: 6 commands
- **Firewall**: 4 commands
- **EC2-Instance**: 4 commands
- **ELB**: 4 commands
- **VPN**: 2 commands

---

## Testing Phases

### Phase 1: Foundation (Week 1)
**Tests**: 50
**Focus**: Root commands, context entry, navigation
**Files**: `test_root_show_commands.py`, `test_root_set_commands.py`, `test_navigation_commands.py`, `test_context_entry.py`

### Phase 2: Core Contexts (Week 2)
**Tests**: 30
**Focus**: VPC and Transit Gateway contexts (most used)
**Files**: `test_vpc_context.py`, `test_transit_gateway_context.py`, `test_action_commands.py`

### Phase 3: CloudWAN (Week 3)
**Tests**: 35
**Focus**: Global-network, core-network, route-table contexts
**Files**: `test_global_network_context.py`, `test_core_network_context.py`, `test_route_table_context.py`, `test_context_aware_commands.py`

### Phase 4: Remaining Contexts (Week 4)
**Tests**: 40
**Focus**: Firewall, EC2, ELB, VPN + Issue resolution
**Files**: `test_firewall_context.py`, `test_ec2_context.py`, `test_elb_context.py`, `test_vpn_context.py`, `test_issue_9.py`, `test_issue_10.py`

### Phase 5: Polish & Integration (Week 5)
**Tests**: 59
**Focus**: Output formats, pipe operators, watch mode, edge cases, integration
**Files**: `test_output_formats.py`, `test_pipe_operators.py`, `test_watch_mode.py`, `test_edge_cases.py`, `test_integration_workflows.py`

---

## Fixture Requirements

### Required Fixture Files
1. `global_networks.json` - 2 global networks with core networks
2. `core_networks.json` - 1 core network with policy and segments
3. `vpcs.json` - 3 VPCs (full, empty, default)
4. `transit_gateways.json` - 2 TGWs with route tables
5. `firewalls.json` - 2 firewalls (configured, minimal)
6. `ec2_instances.json` - 3 instances (running, stopped, no-name)
7. `elbs.json` - 3 ELBs (ALB with data, NLB, ALB without data)
8. `vpns.json` - 2 VPNs (mixed status, all up)
9. `routing_cache.json` - Complete routing cache for find commands

### Fixture Quality Standards
- Realistic AWS resource IDs and ARNs
- Proper parent-child relationships
- Edge cases included (empty lists, null values)
- Issue reproduction data (especially for #9 and #10)

---

## Implementation Guidelines

### Test Structure
```python
class TestContextName:
    """Test suite for specific context or feature."""

    def test_specific_behavior(self, fixtures):
        """Test description in present tense."""
        # Setup: Establish preconditions
        # Execute: Run command
        # Assert: Verify expected behavior
        # Cleanup: If needed
```

### Naming Conventions
- Test files: `test_<feature_or_context>.py`
- Test classes: `Test<ContextName>` or `Test<Feature>`
- Test methods: `test_<command>_<scenario>`

### Assertion Patterns
```python
# Context management
assert shell.ctx_type == "vpc"
assert len(shell.context_stack) == 1
assert shell.prompt.contains("vpc")

# Output verification
assert output.contains("vpc-0a1b2c3d")
assert table.row_count == 3
assert json.loads(output)["vpcs"][0]["id"] == "vpc-0a1b2c3d"

# Error handling
assert "Error" in output
assert shell.ctx_type is None  # Context not changed
```

---

## Useful Commands

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Phase
```bash
pytest tests/test_root_*.py -v  # Phase 1
pytest tests/test_vpc_context.py tests/test_tgw_context.py -v  # Phase 2
```

### Check Coverage
```bash
pytest tests/ --cov=src/aws_network_tools/shell --cov-report=html
open htmlcov/index.html
```

### Run Issue-Specific Tests
```bash
pytest tests/test_issue_9_ec2_filtering.py -v
pytest tests/test_issue_10_elb_data.py -v
```

### Run with Fixtures
```bash
pytest tests/test_vpc_context.py::TestVPCContext::test_vpc_show_subnets -v -s
```

### Generate Test Report
```bash
pytest tests/ --html=test_report.html --self-contained-html
```

---

## Resources

### Internal Documentation
- [Command Graph Analysis](./command_graph_analysis.md) - Complete command structure
- [Fixture Requirements](./fixture_requirements.md) - Fixture specifications
- [Test Roadmap](./test_roadmap.md) - Detailed test plan

### Code References
- Shell Base: `src/aws_network_tools/shell/base.py`
- Shell Main: `src/aws_network_tools/shell/main.py`
- Handlers: `src/aws_network_tools/shell/handlers/*.py`
- Modules: `src/aws_network_tools/modules/*.py`

### Testing Tools
- Pytest: https://docs.pytest.org/
- Rich Testing: https://rich.readthedocs.io/en/stable/
- Coverage.py: https://coverage.readthedocs.io/

---

## Quick Reference

### Command Categories
| Category | Count | Examples |
|----------|-------|----------|
| Show | 56 | show vpcs, show detail, show routes |
| Set | 13 | set vpc, set profile, set output-format |
| Action | 12 | trace, find_ip, find_prefix |
| Navigation | 4 | exit, end, clear, ? |
| Aliases | 5 | sh, conf, ex, int, no |

### Context Hierarchy
```
root
├── global-network
│   └── core-network
│       └── route-table
├── vpc
│   └── route-table
├── transit-gateway
│   └── route-table
├── firewall
├── ec2-instance
├── elb
└── vpn
```

### Priority Testing Order
1. **P0 (Critical)**: Root commands, context entry, Issues #9 & #10
2. **P1 (High)**: Context show commands, action commands, error handling
3. **P2 (Medium)**: Output formats, pipe operators, watch mode
4. **P3 (Low)**: Aliases, advanced filtering, graph export

---

## Getting Started

### For Test Implementation
1. Read [Command Graph Analysis](./command_graph_analysis.md) to understand structure
2. Review [Fixture Requirements](./fixture_requirements.md) for test data
3. Follow [Test Roadmap](./test_roadmap.md) for specific test cases
4. Use [command_graph.py](./command_graph.py) for programmatic access

### For New Contributors
1. Start with Phase 1 tests (root commands)
2. Pick a single test file to implement
3. Use existing tests as templates
4. Run tests locally before submitting PR
5. Ensure fixtures are properly loaded

---

## Success Criteria

### Complete When
- ✅ All 111 unique commands tested
- ✅ 90%+ code coverage achieved
- ✅ All known issues have regression tests
- ✅ All tests passing in CI/CD
- ✅ Test execution time < 5 minutes
- ✅ Documentation complete and up-to-date

### Quality Metrics
- **Command Coverage**: 100% (111/111 commands)
- **Code Coverage**: 90%+ (shell/ directory)
- **Issue Coverage**: 100% (2/2 known issues)
- **Test Reliability**: 0 flaky tests
- **Performance**: < 5 min full suite execution

---

## Contact & Support

### GitHub Issues
- Issue #9: https://github.com/NetDevAutomate/aws_network_shell/issues/9
- Issue #10: https://github.com/NetDevAutomate/aws_network_shell/issues/10

### Repository
https://github.com/NetDevAutomate/aws_network_shell

---

Last Updated: 2024-12-04
