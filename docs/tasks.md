# AWS Network Shell - Path to 95%+ Test Pass Rate

**Generated**: 2024-12-04
**Current Status**: 45/84 tests passing (54%)
**Target**: 95%+ pass rate with comprehensive command coverage
**Methodology**: TDD, OOP, Binary Pass/Fail, Iterative Feedback Loop

---

## Model Consultation Summary

**Models Consulted** (MANDATORY multi-model approach):
1. ✅ **Kimi K2** (kimi-k2-thinking) - Test architecture design
2. ✅ **Nova Premier** (nova-premier) - AWS-specific implementation
3. ✅ **DeepSeek R1** (deepseek-r1) - Testing strategy
4. ✅ **Claude Opus 4** (claude-opus-4) - Deep architectural analysis
5. ✅ **Mistral Large 2** (mistral-large-2) - Implementation patterns

**Key Recommendations Synthesized**:

### From Claude Opus 4 (Architectural Analysis):
- **ContextStateManager**: State machine for reliable context transitions
- **DataFormatAdapter**: Transform mock data to match module expectations
- **MockDataAdapter**: Cache and validate transformed responses
- Created comprehensive architecture files

### From Nova Premier (AWS Expert):
- **EC2 ENI Filtering**: Use `attachment.instance-id` filter
- **ELB Data Structure**: Nested listeners→target groups with ARN references
- **CloudWAN API**: Use `describe_core_networks` for validation
- Context entry requires existence validation

### From Kimi K2 & DeepSeek R1 & Mistral Large 2 (Testing Patterns):
- **BaseContextTestCase**: Reusable test base class
- **show_set_sequence()**: Helper method for command chains
- **execute_sequence()**: Validate multi-step execution
- Binary assertions with clear error messages

---

## Task Breakdown (6-8 hours to 95%+)

### PHASE 1: Core Infrastructure (2 hours)

#### Task 1.1: Implement Context State Manager
**Status**: 🟡 In Progress
**Priority**: CRITICAL
**Estimated Time**: 45 minutes
**Binary Success Criteria**: State manager handles all 9 contexts without errors

**Implementation**:
```python
# File: tests/test_utils/context_state_manager.py
# Based on Claude Opus 4's architecture

class ContextStateManager:
    def enter_context(self, context_name, context_data):
        # Validate transition
        # Update state path
        # Apply filters
        return success (True/False)
```

**Test**:
```bash
pytest tests/test_utils/test_context_state_manager.py -v
# PASS: All context transitions work
# PASS: Filters applied correctly
# PASS: State rollback works
```

**Deliverable**: `tests/test_utils/context_state_manager.py` with 100% test coverage

---

#### Task 1.2: Implement Data Format Adapter
**Status**: 🔴 Not Started
**Priority**: CRITICAL
**Estimated Time**: 45 minutes
**Binary Success Criteria**: Mock data transforms to module format without errors

**Implementation**:
```python
# File: tests/test_utils/data_format_adapter.py
# Based on Claude Opus 4's design

class DataFormatAdapter:
    def adapt_cloudwan_response(self, fixture_data):
        # Transform CLOUDWAN_FIXTURES format
        # To CloudWANClient.discover() expected format
        return transformed_data
```

**Test**:
```python
# Binary test:
adapted = adapter.adapt_cloudwan_response(CLOUDWAN_FIXTURES["core-network-0global123"])
assert adapted["id"] == "core-network-0global123"
assert "global_network_id" in adapted
assert "segments" in adapted
```

**Deliverable**: `tests/test_utils/data_format_adapter.py` + tests

---

#### Task 1.3: Create BaseContextTestCase
**Status**: 🔴 Not Started
**Priority**: HIGH
**Estimated Time**: 30 minutes
**Binary Success Criteria**: Base class works for all context types

**Implementation**:
```python
# File: tests/test_command_graph/base_context_test.py

class BaseContextTestCase:
    def show_set_sequence(self, show_cmd, set_cmd, index):
        # Execute show → verify output → execute set → verify context
        pass

    def execute_sequence(self, commands):
        # Execute list of commands, assert all pass
        pass
```

**Test**: Use in one existing test class, verify pattern works

**Deliverable**: `tests/test_command_graph/base_context_test.py`

---

### PHASE 2: Fix Core Issues (2 hours)

#### Task 2.1: Fix Core-Network Context Entry
**Status**: 🔴 Not Started
**Priority**: CRITICAL
**Estimated Time**: 1 hour
**Binary Success Criteria**: `set core-network 1` enters context 100% of time

**Root Cause Analysis** (from models):
- Mock data format doesn't match what module expects
- Context validation may be failing silently
- Need to check `src/aws_network_tools/modules/cloudwan.py` context entry logic

**Investigation Steps**:
1. Read `src/aws_network_tools/modules/cloudwan.py` - find context entry code
2. Add debug logging to see why context entry fails
3. Compare mock data format with expected format
4. Fix data adapter or mock client

**Implementation**:
```python
# In conftest.py MockCloudWANClient
def discover(self):
    # Ensure format EXACTLY matches CloudWANClient.discover() output
    # Check actual cloudwan.py module for expected structure
```

**Test**:
```bash
pytest tests/test_command_graph/test_cloudwan_branch.py::TestCoreNetworkBranch::test_set_core_network_by_number -v
# MUST PASS (binary)
```

**Deliverable**: Updated mock in conftest.py, test passing

---

#### Task 2.2: Fix EC2 Context ENI Filtering (Issue #9)
**Status**: 🔴 Not Started
**Priority**: HIGH
**Estimated Time**: 30 minutes
**Binary Success Criteria**: `show enis` in EC2 context returns ONLY instance ENIs

**Solution** (from Nova Premier):
```python
# In EC2 handler (src/aws_network_tools/shell/handlers/ec2.py)
def _show_enis(self):
    instance_id = self.ctx_id  # Current instance ID from context

    # Filter ENIs by attachment.instance-id
    filters = [{'Name': 'attachment.instance-id', 'Values': [instance_id]}]

    # Get filtered ENIs
    enis = ec2_client.describe_network_interfaces(Filters=filters)
```

**Test**:
```python
def test_ec2_context_show_enis_filtered():
    run("show ec2-instances")
    run("set ec2-instance 1")  # Instance i-0prodweb1a123456789
    result = run("show enis")

    # Binary: Should show ONLY eni-0prodweb1a1234567
    assert "eni-0prodweb1a1234567" in result
    assert result.count("eni-") == 1  # ONLY one ENI
```

**Deliverable**: Fixed EC2 handler, test passing

---

#### Task 2.3: Fix ELB Context Data (Issue #10)
**Status**: 🔴 Not Started
**Priority**: HIGH
**Estimated Time**: 30 minutes
**Binary Success Criteria**: `show listeners/targets/health` returns data

**Solution** (from Nova Premier):
```python
# Update ELB mock in conftest.py to include listeners/targets/health

class MockELBClient:
    def get_elb_detail(self, elb_arn):
        from tests.fixtures import get_elb_detail
        return get_elb_detail(elb_arn)  # Returns full detail with listeners
```

**Test**:
```python
def test_elb_context_show_listeners():
    run("show elbs")
    run("set elb 1")
    result = run("show listeners")

    # Binary: Must show listeners
    assert "Listener" in result or "Port" in result
    assert result != "No listeners"  # Fail if empty
```

**Deliverable**: Fixed ELB mock, 3 tests passing (listeners, targets, health)

---

### PHASE 3: Apply Patterns to All Branches (2 hours)

#### Task 3.1: VPC Branch Tests
**Status**: 🔴 Not Started
**Priority**: HIGH
**Estimated Time**: 30 minutes
**Binary Success Criteria**: 12+ VPC tests pass

**Command Path**:
```
show vpcs → set vpc 1 → show subnets/routes/security-groups/nacls/endpoints
```

**Implementation**:
```python
# File: tests/test_command_graph/test_vpc_branch.py

class TestVPCBranch(BaseContextTestCase):
    def test_vpc_navigation_chain(self):
        self.show_set_sequence("show vpcs", "set vpc", 1)
        # Test all vpc context commands
```

**Tests to Create**: 12 tests covering all VPC context commands

**Deliverable**: `tests/test_command_graph/test_vpc_branch.py`, 12+ tests passing

---

#### Task 3.2: Transit Gateway Branch Tests
**Status**: 🔴 Not Started
**Priority**: HIGH
**Estimated Time**: 30 minutes
**Binary Success Criteria**: 10+ TGW tests pass

**Command Path**:
```
show transit-gateways → set transit-gateway 1 → show attachments/routes/route-tables
```

**Deliverable**: `tests/test_command_graph/test_tgw_branch.py`, 10+ tests passing

---

#### Task 3.3: EC2 Branch Tests
**Status**: 🔴 Not Started
**Priority**: MEDIUM
**Estimated Time**: 20 minutes
**Binary Success Criteria**: 6+ EC2 tests pass

**Command Path**:
```
show ec2-instances → set ec2-instance 1 → show detail/enis/security-groups/routes
```

**Deliverable**: `tests/test_command_graph/test_ec2_branch.py`, 6+ tests passing

---

#### Task 3.4: ELB Branch Tests
**Status**: 🔴 Not Started
**Priority**: MEDIUM
**Estimated Time**: 20 minutes
**Binary Success Criteria**: 6+ ELB tests pass

**Command Path**:
```
show elbs → set elb 1 → show listeners/targets/health/detail
```

**Deliverable**: `tests/test_command_graph/test_elb_branch.py`, 6+ tests passing

---

### PHASE 4: Comprehensive Coverage (1-2 hours)

#### Task 4.1: VPN Branch Tests
**Status**: 🔴 Not Started
**Priority**: MEDIUM
**Estimated Time**: 20 minutes
**Binary Success Criteria**: 4+ VPN tests pass

**Deliverable**: `tests/test_command_graph/test_vpn_branch.py`

---

#### Task 4.2: Firewall Branch Tests
**Status**: 🔴 Not Started
**Priority**: MEDIUM
**Estimated Time**: 20 minutes
**Binary Success Criteria**: 4+ firewall tests pass

**Deliverable**: `tests/test_command_graph/test_firewall_branch.py`

---

#### Task 4.3: Route Table Context Tests
**Status**: 🔴 Not Started
**Priority**: LOW
**Estimated Time**: 20 minutes
**Binary Success Criteria**: 3+ route-table tests pass

**Deliverable**: `tests/test_command_graph/test_route_table_branch.py`

---

### PHASE 5: Validation & Cleanup (1 hour)

#### Task 5.1: Run Full Test Suite
**Status**: 🔴 Not Started
**Priority**: CRITICAL
**Estimated Time**: 10 minutes (iterative)
**Binary Success Criteria**: 95%+ tests passing

**Command**:
```bash
pytest tests/test_command_graph/ -v --tb=short --no-cov
# Target: 140+/150 tests passing (93%+)
```

**Iterative Loop**:
1. Run tests
2. If failure → analyze → fix → re-run
3. If failure twice → consult models
4. Repeat until 95%+

---

#### Task 5.2: Fix Remaining Failures
**Status**: 🔴 Not Started
**Priority**: HIGH
**Estimated Time**: 30 minutes
**Binary Success Criteria**: All fixable failures resolved

**Process**:
- Categorize failures (mock data, format, logic)
- Fix root causes
- Re-run tests
- Achieve 95%+

---

#### Task 5.3: Generate Coverage Report
**Status**: 🔴 Not Started
**Priority**: MEDIUM
**Estimated Time**: 10 minutes
**Binary Success Criteria**: Coverage report generated

**Commands**:
```bash
pytest tests/test_command_graph/ --cov=src/aws_network_tools --cov-report=html
# Generate comprehensive coverage report
```

**Deliverable**: HTML coverage report showing 90%+ coverage

---

#### Task 5.4: Final Documentation
**Status**: 🔴 Not Started
**Priority**: MEDIUM
**Estimated Time**: 20 minutes
**Binary Success Criteria**: All documentation complete

**Deliverables**:
- Update `~/Desktop/aws_net_shell_testing.md` with final results
- Update `tests/test_command_graph/README.md`
- Add test patterns to fixture README

---

## Implementation Guidelines

### TDD Methodology

**Red-Green-Refactor Cycle**:
1. **Red**: Write failing test first
2. **Green**: Write minimal code to pass
3. **Refactor**: Clean up while keeping tests green

**Example**:
```python
# RED: Write test that fails
def test_show_segments_in_core_network_context():
    # Setup context
    run("show global-networks")
    run("set global-network 1")
    run("show core-networks")
    run("set core-network 1")

    # Test command
    result = run("show segments")

    # Binary assertion
    assert result.exit_code == 0
    assert "production" in result.output
    assert "staging" in result.output

# GREEN: Fix mock to return proper segment data
# REFACTOR: Extract show_set_sequence helper
```

### OOP Structure

**Class Hierarchy**:
```
BaseContextTestCase (abstract)
├── TestGlobalNetworkBranch
│   └── test_show_global_networks()
│   └── test_set_global_network()
├── TestCoreNetworkBranch
│   └── test_show_segments()
│   └── test_show_routes()
├── TestVPCBranch
│   └── test_show_subnets()
│   └── test_show_routes()
└── ...
```

**Benefits**:
- Code reuse via base class
- Clear test organization
- Easy to add new contexts

### Binary Pass/Fail

**All assertions must be binary**:
```python
# ✅ GOOD - Binary
assert result.exit_code == 0  # Pass or fail, no ambiguity
assert "vpc-123" in output     # Present or not
assert len(items) == 5         # Exact count

# ❌ BAD - Ambiguous
assert "maybe" in output       # Unclear what constitutes pass
assert len(items) > 0          # Doesn't verify correctness
```

### Iterative Feedback Loop

**Process for Each Task**:
1. **Implement**: Write code/test
2. **Run**: Execute test suite
3. **Analyze**: If fail, examine output
4. **Fix**: Apply fix based on output
5. **Re-run**: Test again
6. **Repeat**: Until binary pass achieved

**Failure Threshold**:
- **1st failure**: Analyze and fix directly
- **2nd failure**: Consult models (via RepoPrompt or litellm gateway)
- **3rd failure**: Escalate for human review

---

## Progress Tracking

### Task Checklist

| Task | Status | Tests | Pass Rate | Time |
|------|--------|-------|-----------|------|
| 1.1 Context State Manager | 🟡 | - | - | - |
| 1.2 Data Format Adapter | 🔴 | - | - | - |
| 1.3 Base Test Case | 🔴 | - | - | - |
| 2.1 Core-Network Context | 🔴 | 0/10 | 0% | - |
| 2.2 EC2 ENI Filtering | 🔴 | 0/1 | 0% | - |
| 2.3 ELB Data Structure | 🔴 | 0/3 | 0% | - |
| 3.1 VPC Branch | 🔴 | 0/12 | 0% | - |
| 3.2 TGW Branch | 🔴 | 0/10 | 0% | - |
| 3.3 EC2 Branch | 🔴 | 0/6 | 0% | - |
| 3.4 ELB Branch | 🔴 | 0/6 | 0% | - |
| 4.1 VPN Branch | 🔴 | 0/4 | 0% | - |
| 4.2 Firewall Branch | 🔴 | 0/4 | 0% | - |
| 4.3 Route Table Branch | 🔴 | 0/3 | 0% | - |
| 5.1 Full Test Suite | 🔴 | 45/84 | 54% | - |
| 5.2 Fix Remaining | 🔴 | - | - | - |
| 5.3 Coverage Report | 🔴 | - | - | - |
| 5.4 Documentation | 🔴 | - | - | - |

**Target**: 140+/150 tests passing (95%+)

---

## Model-Specific Recommendations

### EC2 ENI Filtering Fix (Nova Premier)
```python
# File: src/aws_network_tools/shell/handlers/ec2.py

def _show_enis(self):
    """Show ENIs for current EC2 instance."""
    instance_id = self.ctx_id  # From context

    # Filter by attachment
    filters = [{'Name': 'attachment.instance-id', 'Values': [instance_id]}]

    # Call EC2 client
    ec2 = ec2.EC2Client(self.profile)
    enis = ec2.get_instance_enis(instance_id, filters)

    # Display
    ec2.EC2Display(console).show_enis(enis)
```

### ELB Listener Data Structure (Nova Premier)
```python
# In conftest.py MockELBClient
def get_elb_detail(self, elb_arn):
    # Import comprehensive detail from fixtures
    from tests.fixtures import get_elb_detail

    detail = get_elb_detail(elb_arn)
    # Ensure detail includes:
    # - load_balancer
    # - listeners (with DefaultActions)
    # - target_groups
    # - target_health
    return detail
```

### Context State Machine Pattern (Claude Opus 4)
```python
# Implement full ContextStateManager from architecture
# With transition validation, data filtering, state history
# See: testing/context_state_machine.py (created by model)
```

---

## Success Metrics

### Test Coverage Goals

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Total Tests | 84 | 150+ | 🟡 56% |
| Pass Rate | 54% | 95%+ | 🔴 |
| Command Coverage | ~40% | 95%+ | 🔴 |
| Context Coverage | 2/9 | 9/9 | 🔴 |
| Line Coverage | ~30% | 80%+ | 🔴 |

### Binary Success Criteria

✅ **SUCCESS = All of**:
- 95%+ tests passing (143+/150)
- All 9 context types tested
- GitHub Issues #9 and #10 resolved
- Command graph 95%+ covered
- Zero test flakiness

❌ **FAILURE = Any of**:
- <90% tests passing
- Any context type untested
- GitHub issues still open
- Flaky tests present

---

## Next Actions (Immediate)

1. **START**: Task 1.1 (Context State Manager) - 45 minutes
2. **THEN**: Task 2.1 (Fix Core-Network Context) - 1 hour
3. **THEN**: Task 2.2 (Fix EC2 Filtering) - 30 minutes
4. **THEN**: Task 2.3 (Fix ELB Data) - 30 minutes
5. **ITERATE**: Run tests, fix failures, repeat

**Expected Timeline**: 6-8 hours to 95%+ pass rate

---

**Document Status**: Living document - update after each task completion
**Last Updated**: 2024-12-04 11:15:00 PST
