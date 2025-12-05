# AWS Network Shell - Test Implementation Roadmap

**Generated**: 2024-12-04
**Purpose**: Detailed test case specifications and implementation sequence

---

## Test Coverage Summary

**Total Unique Commands**: 111
**Estimated Test Cases**: 214+
**Current Coverage**: ~10 tests (5% coverage)
**Target Coverage**: 90%+ code coverage, 100% command coverage

---

## Phase 1: Foundation Tests (Week 1)

**Goal**: Establish core testing infrastructure and root commands
**Estimated Tests**: 50
**Priority**: P0 (Critical)

### 1.1 Test File: `test_root_show_commands.py`

#### Test Cases (30 tests)

```python
class TestRootShowCommands:
    """Test all root-level show commands."""

    def test_show_version(self, mock_shell):
        """Test show version displays version info."""
        # Execute: show version
        # Assert: Version string displayed, no errors

    def test_show_global_networks(self, mock_shell_with_fixtures):
        """Test show global-networks lists all global networks."""
        # Execute: show global-networks
        # Assert: Table with 2 global networks, proper columns

    def test_show_global_networks_empty(self, mock_shell):
        """Test show global-networks with no data."""
        # Execute: show global-networks (empty cache)
        # Assert: "No global networks" message

    def test_show_vpcs(self, mock_shell_with_fixtures):
        """Test show vpcs lists all VPCs."""
        # Execute: show vpcs
        # Assert: Table with 3 VPCs, proper columns

    def test_show_vpcs_json_format(self, mock_shell_with_fixtures):
        """Test show vpcs in JSON format."""
        # Setup: set output-format json
        # Execute: show vpcs
        # Assert: Valid JSON output

    def test_show_vpcs_yaml_format(self, mock_shell_with_fixtures):
        """Test show vpcs in YAML format."""
        # Setup: set output-format yaml
        # Execute: show vpcs
        # Assert: Valid YAML output

    def test_show_transit_gateways(self, mock_shell_with_fixtures):
        """Test show transit_gateways lists all TGWs."""
        # Execute: show transit_gateways
        # Assert: Table with 2 TGWs

    def test_show_firewalls(self, mock_shell_with_fixtures):
        """Test show firewalls lists all firewalls."""
        # Execute: show firewalls
        # Assert: Table with 2 firewalls

    def test_show_ec2_instances(self, mock_shell_with_fixtures):
        """Test show ec2-instances lists all instances."""
        # Execute: show ec2-instances
        # Assert: Table with 3 instances

    def test_show_elbs(self, mock_shell_with_fixtures):
        """Test show elbs lists all load balancers."""
        # Execute: show elbs
        # Assert: Table with 3 ELBs

    def test_show_vpns(self, mock_shell_with_fixtures):
        """Test show vpns lists all VPN connections."""
        # Execute: show vpns
        # Assert: Table with 2 VPNs

    # ... Additional 19 show commands (enis, security-groups, etc.)
```

### 1.2 Test File: `test_root_set_commands.py`

#### Test Cases (15 tests)

```python
class TestRootSetCommands:
    """Test all root-level set commands."""

    def test_set_profile(self, mock_shell):
        """Test set profile changes AWS profile."""
        # Execute: set profile production
        # Assert: shell.profile == "production"

    def test_set_profile_no_arg(self, mock_shell):
        """Test set profile without argument."""
        # Execute: set profile
        # Assert: Error message displayed

    def test_set_output_format_json(self, mock_shell):
        """Test set output-format json."""
        # Execute: set output-format json
        # Assert: shell.output_format == "json"

    def test_set_output_format_invalid(self, mock_shell):
        """Test set output-format with invalid value."""
        # Execute: set output-format xml
        # Assert: Error message, format unchanged

    def test_set_no_cache(self, mock_shell):
        """Test set no-cache disables caching."""
        # Execute: set no-cache
        # Assert: shell.no_cache == True

    def test_set_watch(self, mock_shell):
        """Test set watch interval."""
        # Execute: set watch 10
        # Assert: shell.watch_interval == 10

    # ... Additional 9 set commands
```

### 1.3 Test File: `test_navigation_commands.py`

#### Test Cases (12 tests)

```python
class TestNavigationCommands:
    """Test context navigation (exit, end, clear, ?)."""

    def test_exit_from_root(self, mock_shell):
        """Test exit from root context exits shell."""
        # Execute: exit
        # Assert: Shell exits (returns True)

    def test_exit_from_vpc_context(self, mock_shell_with_fixtures):
        """Test exit from VPC context returns to root."""
        # Setup: set vpc 1
        # Execute: exit
        # Assert: context_stack empty, prompt == "aws-net> "

    def test_exit_from_nested_context(self, mock_shell_with_fixtures):
        """Test exit from nested context (core-network > route-table)."""
        # Setup: set global-network 1, set core-network 1, set route-table 1
        # Execute: exit
        # Assert: context_stack has 2 items (global, core-network)

    def test_end_from_nested_context(self, mock_shell_with_fixtures):
        """Test end returns to root from any depth."""
        # Setup: set global-network 1, set core-network 1, set route-table 1
        # Execute: end
        # Assert: context_stack empty

    def test_clear_screen(self, mock_shell):
        """Test clear command clears screen."""
        # Execute: clear
        # Assert: Console.clear() called

    def test_help_at_root(self, mock_shell):
        """Test ? displays root commands."""
        # Execute: ?
        # Assert: List of root commands displayed

    def test_help_in_vpc_context(self, mock_shell_with_fixtures):
        """Test ? displays VPC context commands."""
        # Setup: set vpc 1
        # Execute: ?
        # Assert: List of VPC commands displayed

    # ... Additional 5 navigation tests
```

---

## Phase 2: Context Entry Tests (Week 1-2)

**Goal**: Test all context entry mechanisms
**Estimated Tests**: 32
**Priority**: P0 (Critical)

### 2.1 Test File: `test_context_entry.py`

#### Test Cases (32 tests)

```python
class TestContextEntry:
    """Test entering all context types with valid/invalid references."""

    # VPC Context Entry
    def test_set_vpc_by_index(self, mock_shell_with_fixtures):
        """Test entering VPC context by index."""
        # Execute: set vpc 1
        # Assert: context_stack[0].type == "vpc"
        # Assert: context_stack[0].ref == "1"
        # Assert: prompt contains "vpc"

    def test_set_vpc_by_name(self, mock_shell_with_fixtures):
        """Test entering VPC context by name."""
        # Execute: set vpc production-vpc
        # Assert: context_stack[0].type == "vpc"
        # Assert: context_stack[0].name == "production-vpc"

    def test_set_vpc_by_id(self, mock_shell_with_fixtures):
        """Test entering VPC context by ID."""
        # Execute: set vpc vpc-0a1b2c3d4e5f6g7h8
        # Assert: context_stack[0].type == "vpc"

    def test_set_vpc_invalid_index(self, mock_shell_with_fixtures):
        """Test entering VPC context with invalid index."""
        # Execute: set vpc 999
        # Assert: Error message, context_stack empty

    def test_set_vpc_invalid_name(self, mock_shell_with_fixtures):
        """Test entering VPC context with invalid name."""
        # Execute: set vpc nonexistent-vpc
        # Assert: Error message, context_stack empty

    def test_set_vpc_no_arg(self, mock_shell):
        """Test set vpc without argument."""
        # Execute: set vpc
        # Assert: Usage error message

    # Repeat for all 8 context types:
    # - global-network (4 tests)
    # - transit-gateway (4 tests)
    # - firewall (4 tests)
    # - ec2-instance (4 tests)
    # - elb (4 tests)
    # - vpn (4 tests)
    # Total: 8 contexts × 4 tests = 32 tests
```

---

## Phase 3: Context Show Commands (Week 2-3)

**Goal**: Test all context-specific show commands
**Estimated Tests**: 60
**Priority**: P0-P1

### 3.1 Test File: `test_vpc_context.py`

```python
class TestVPCContext:
    """Test VPC context show commands."""

    def test_vpc_show_detail(self, mock_shell_with_fixtures):
        """Test show detail in VPC context."""
        # Setup: set vpc 1
        # Execute: show detail
        # Assert: VPC details table displayed

    def test_vpc_show_subnets(self, mock_shell_with_fixtures):
        """Test show subnets in VPC context."""
        # Setup: set vpc 1
        # Execute: show subnets
        # Assert: Subnet table with 2 subnets

    def test_vpc_show_subnets_empty(self, mock_shell_with_fixtures):
        """Test show subnets with no subnets."""
        # Setup: set vpc 2 (test-vpc with empty subnets)
        # Execute: show subnets
        # Assert: "No subnets" message

    def test_vpc_show_route_tables(self, mock_shell_with_fixtures):
        """Test show route-tables in VPC context."""
        # Setup: set vpc 1
        # Execute: show route-tables
        # Assert: Route tables displayed

    def test_vpc_show_security_groups(self, mock_shell_with_fixtures):
        """Test show security-groups in VPC context."""
        # Setup: set vpc 1
        # Execute: show security-groups
        # Assert: Security groups table

    def test_vpc_show_nacls(self, mock_shell_with_fixtures):
        """Test show nacls in VPC context."""
        # Setup: set vpc 1
        # Execute: show nacls
        # Assert: NACL table

    def test_vpc_show_internet_gateways(self, mock_shell_with_fixtures):
        """Test show internet-gateways in VPC context."""
        # Setup: set vpc 1
        # Execute: show internet-gateways
        # Assert: IGW table

    def test_vpc_show_nat_gateways(self, mock_shell_with_fixtures):
        """Test show nat-gateways in VPC context."""
        # Setup: set vpc 1
        # Execute: show nat-gateways
        # Assert: NAT gateway table

    def test_vpc_show_endpoints(self, mock_shell_with_fixtures):
        """Test show endpoints in VPC context."""
        # Setup: set vpc 1
        # Execute: show endpoints
        # Assert: VPC endpoints table

    def test_vpc_find_prefix(self, mock_shell_with_fixtures):
        """Test find_prefix in VPC context."""
        # Setup: set vpc 1
        # Execute: find_prefix 10.0.0.0/16
        # Assert: Routes matching prefix displayed

    def test_vpc_find_null_routes(self, mock_shell_with_fixtures):
        """Test find_null_routes in VPC context."""
        # Setup: set vpc 1
        # Execute: find_null_routes
        # Assert: Blackhole routes displayed

    # 11 tests total for VPC context
```

### 3.2 Test Files for Other Contexts

- `test_global_network_context.py` (3 tests)
- `test_core_network_context.py` (15 tests)
- `test_route_table_context.py` (3 tests)
- `test_transit_gateway_context.py` (6 tests)
- `test_firewall_context.py` (4 tests)
- `test_ec2_context.py` (4 tests)
- `test_elb_context.py` (4 tests)
- `test_vpn_context.py` (2 tests)

**Total**: 52 context show command tests

---

## Phase 4: Action Commands (Week 3)

**Goal**: Test all action commands in various contexts
**Estimated Tests**: 30
**Priority**: P1

### 4.1 Test File: `test_action_commands.py`

```python
class TestActionCommands:
    """Test action commands (write, trace, find_ip, etc.)."""

    def test_write_to_file(self, mock_shell_with_fixtures, tmp_path):
        """Test write command saves output to file."""
        # Setup: set output-format json
        # Execute: show vpcs, write output.json
        # Assert: File created with VPC data

    def test_trace_between_ips(self, mock_shell_with_fixtures):
        """Test trace command between two IPs."""
        # Execute: trace 10.0.1.10 172.16.1.10
        # Assert: Path trace displayed

    def test_trace_invalid_ips(self, mock_shell):
        """Test trace with invalid IP addresses."""
        # Execute: trace invalid-ip 10.0.0.1
        # Assert: Error message

    def test_find_ip(self, mock_shell_with_fixtures):
        """Test find_ip locates IP in ENIs."""
        # Execute: find_ip 10.0.1.10
        # Assert: ENI and instance info displayed

    def test_find_ip_not_found(self, mock_shell_with_fixtures):
        """Test find_ip with non-existent IP."""
        # Execute: find_ip 1.2.3.4
        # Assert: "Not found" message

    def test_populate_cache(self, mock_shell):
        """Test populate_cache loads all resources."""
        # Execute: populate_cache
        # Assert: Cache populated with resources

    def test_clear_cache(self, mock_shell_with_fixtures):
        """Test clear_cache empties cache."""
        # Setup: Populate cache
        # Execute: clear_cache
        # Assert: Cache empty

    def test_create_routing_cache(self, mock_shell_with_fixtures):
        """Test create_routing_cache builds routing data."""
        # Execute: create_routing_cache
        # Assert: Routing cache created

    def test_export_graph(self, mock_shell_with_fixtures, tmp_path):
        """Test export_graph saves graph to file."""
        # Execute: export_graph output.dot
        # Assert: Graph file created

    def test_validate_graph(self, mock_shell):
        """Test validate_graph checks command graph."""
        # Execute: validate_graph
        # Assert: Validation results displayed

    # 10 tests for root action commands
```

### 4.2 Test File: `test_context_aware_commands.py`

```python
class TestContextAwareFindPrefix:
    """Test find_prefix behavior in different contexts."""

    def test_find_prefix_root_context(self, mock_shell_with_fixtures):
        """Test find_prefix in root searches routing cache."""
        # Setup: create_routing_cache
        # Execute: find_prefix 10.0.0.0/8
        # Assert: Routes from all resources displayed

    def test_find_prefix_vpc_context(self, mock_shell_with_fixtures):
        """Test find_prefix in VPC context searches VPC routes."""
        # Setup: set vpc 1
        # Execute: find_prefix 10.0.0.0/16
        # Assert: Only VPC routes displayed

    def test_find_prefix_tgw_context(self, mock_shell_with_fixtures):
        """Test find_prefix in TGW context searches TGW routes."""
        # Setup: set transit-gateway 1
        # Execute: find_prefix 10.0.0.0/8
        # Assert: Only TGW routes displayed

    def test_find_prefix_core_network_context(self, mock_shell_with_fixtures):
        """Test find_prefix in core-network searches CloudWAN."""
        # Setup: set global-network 1, set core-network 1
        # Execute: find_prefix 10.0.0.0/8
        # Assert: Only CloudWAN routes displayed

    def test_find_prefix_route_table_context(self, mock_shell_with_fixtures):
        """Test find_prefix in route-table searches specific table."""
        # Setup: set vpc 1, set route-table 1
        # Execute: find_prefix 10.0.0.0/16
        # Assert: Only routes from specific table

    # 5 tests for find_prefix context awareness


class TestContextAwareFindNullRoutes:
    """Test find_null_routes behavior in different contexts."""

    def test_find_null_routes_root(self, mock_shell_with_fixtures):
        """Test find_null_routes in root searches all resources."""
        # Execute: find_null_routes
        # Assert: All blackhole routes from cache

    def test_find_null_routes_vpc(self, mock_shell_with_fixtures):
        """Test find_null_routes in VPC context."""
        # Setup: set vpc 1
        # Execute: find_null_routes
        # Assert: Only VPC blackhole routes

    def test_find_null_routes_tgw(self, mock_shell_with_fixtures):
        """Test find_null_routes in TGW context."""
        # Setup: set transit-gateway 1
        # Execute: find_null_routes
        # Assert: Only TGW blackhole routes

    def test_find_null_routes_core_network(self, mock_shell_with_fixtures):
        """Test find_null_routes in core-network context."""
        # Setup: set global-network 1, set core-network 1
        # Execute: find_null_routes
        # Assert: Only CloudWAN blackhole routes

    def test_find_null_routes_route_table(self, mock_shell_with_fixtures):
        """Test find_null_routes in route-table context."""
        # Setup: set vpc 1, set route-table 1
        # Execute: find_null_routes
        # Assert: Only route table blackhole routes

    # 5 tests for find_null_routes context awareness
```

---

## Phase 5: Output Format Tests (Week 3)

**Goal**: Test all output format variations
**Estimated Tests**: 24
**Priority**: P1

### 5.1 Test File: `test_output_formats.py`

```python
class TestOutputFormats:
    """Test table, JSON, and YAML output formats."""

    def test_table_output_default(self, mock_shell_with_fixtures):
        """Test default table output format."""
        # Execute: show vpcs
        # Assert: Rich table rendered

    def test_json_output_show_vpcs(self, mock_shell_with_fixtures):
        """Test JSON output for show vpcs."""
        # Setup: set output-format json
        # Execute: show vpcs
        # Assert: Valid JSON structure

    def test_yaml_output_show_vpcs(self, mock_shell_with_fixtures):
        """Test YAML output for show vpcs."""
        # Setup: set output-format yaml
        # Execute: show vpcs
        # Assert: Valid YAML structure

    def test_json_output_vpc_context(self, mock_shell_with_fixtures):
        """Test JSON output in VPC context."""
        # Setup: set output-format json, set vpc 1
        # Execute: show detail
        # Assert: Valid JSON with VPC detail

    def test_output_format_persistence(self, mock_shell_with_fixtures):
        """Test output format persists across commands."""
        # Setup: set output-format json
        # Execute: show vpcs, show transit_gateways
        # Assert: Both commands use JSON format

    def test_output_file_redirection(self, mock_shell_with_fixtures, tmp_path):
        """Test output-file redirection."""
        # Setup: set output-file /tmp/output.json
        # Execute: show vpcs
        # Assert: File created with VPC data

    # 8 format tests × 3 output types = 24 tests
```

---

## Phase 6: Pipe Operators & Filtering (Week 4)

**Goal**: Test pipe operators and filtering
**Estimated Tests**: 15
**Priority**: P2

### 6.1 Test File: `test_pipe_operators.py`

```python
class TestPipeOperators:
    """Test pipe operators (include, exclude, grep)."""

    def test_include_filter(self, mock_shell_with_fixtures):
        """Test | include <pattern> filters output."""
        # Execute: show vpcs | include production
        # Assert: Only "production-vpc" row displayed

    def test_exclude_filter(self, mock_shell_with_fixtures):
        """Test | exclude <pattern> filters output."""
        # Execute: show vpcs | exclude test
        # Assert: "test-vpc" not in output

    def test_grep_filter(self, mock_shell_with_fixtures):
        """Test | grep <pattern> filters output."""
        # Execute: show vpcs | grep 10.0
        # Assert: Only VPCs with 10.0 CIDR displayed

    def test_multiple_pipe_operators(self, mock_shell_with_fixtures):
        """Test chaining pipe operators."""
        # Execute: show vpcs | include production | exclude test
        # Assert: Filtered correctly

    def test_pipe_case_insensitive(self, mock_shell_with_fixtures):
        """Test pipe operators are case-insensitive."""
        # Execute: show vpcs | include PRODUCTION
        # Assert: Matches "production-vpc"

    # 5 pipe operator tests
```

---

## Phase 7: Watch Mode (Week 4)

**Goal**: Test watch mode functionality
**Estimated Tests**: 10
**Priority**: P2

### 7.1 Test File: `test_watch_mode.py`

```python
class TestWatchMode:
    """Test watch mode for continuous monitoring."""

    def test_watch_show_vpcs(self, mock_shell_with_fixtures):
        """Test watch mode refreshes show vpcs."""
        # Execute: show vpcs watch 1
        # Assert: Command executes multiple times
        # Assert: Ctrl-C interrupts watch

    def test_watch_invalid_interval(self, mock_shell_with_fixtures):
        """Test watch with invalid interval."""
        # Execute: show vpcs watch invalid
        # Assert: Error or ignored

    def test_watch_in_vpc_context(self, mock_shell_with_fixtures):
        """Test watch mode in VPC context."""
        # Setup: set vpc 1
        # Execute: show subnets watch 2
        # Assert: Subnets refresh every 2 seconds

    # 5 watch mode tests
```

---

## Phase 8: Issue Resolution Tests (Week 4)

**Goal**: Regression tests for known issues
**Estimated Tests**: 10
**Priority**: P0

### 8.1 Test File: `test_issue_9_ec2_filtering.py`

```python
class TestIssue9EC2Filtering:
    """Regression tests for Issue #9: EC2 context filtering."""

    def test_ec2_show_enis_filters_to_instance(self, mock_shell_with_fixtures):
        """Test show enis returns only instance ENIs."""
        # Setup: set ec2-instance 1 (production-web-01 with 1 ENI)
        # Execute: show enis
        # Assert: Only 1 ENI displayed (eni-0a1b2c3d4e5f)
        # Assert: ENI belongs to instance i-0a1b2c3d4e5f6g7h8

    def test_ec2_show_security_groups_filters_to_instance(self, mock_shell_with_fixtures):
        """Test show security-groups returns only instance SGs."""
        # Setup: set ec2-instance 1 (production-web-01 with 2 SGs)
        # Execute: show security-groups
        # Assert: Only 2 SGs displayed
        # Assert: SGs are sg-0a1b2c3d4e5f and sg-9z8y7x6w5v4u

    def test_ec2_show_enis_multiple_enis(self, mock_shell_with_fixtures):
        """Test show enis with multi-ENI instance."""
        # Create fixture with instance having 3 ENIs
        # Setup: set ec2-instance <multi-eni-instance>
        # Execute: show enis
        # Assert: All 3 instance ENIs displayed

    def test_ec2_show_security_groups_no_sgs(self, mock_shell_with_fixtures):
        """Test show security-groups with no SGs."""
        # Setup: set ec2-instance 2 (test-instance with no SGs)
        # Execute: show security-groups
        # Assert: "No security groups" message

    def test_ec2_filtering_does_not_affect_root_commands(self, mock_shell_with_fixtures):
        """Test root show commands unaffected by context."""
        # Setup: set ec2-instance 1
        # Execute: end, show enis
        # Assert: ALL account ENIs displayed (144 items in issue #9)

    # 5 tests for Issue #9
```

### 8.2 Test File: `test_issue_10_elb_data.py`

```python
class TestIssue10ELBData:
    """Regression tests for Issue #10: ELB data retrieval."""

    def test_elb_show_listeners_with_data(self, mock_shell_with_fixtures):
        """Test show listeners displays listener data."""
        # Setup: set elb 1 (production-alb with 2 listeners)
        # Execute: show listeners
        # Assert: 2 listeners displayed
        # Assert: Ports 443 and 80 shown

    def test_elb_show_targets_with_data(self, mock_shell_with_fixtures):
        """Test show targets displays target groups."""
        # Setup: set elb 1 (production-alb with 1 target group)
        # Execute: show targets
        # Assert: 1 target group displayed
        # Assert: Targets shown

    def test_elb_show_health_with_data(self, mock_shell_with_fixtures):
        """Test show health displays health status."""
        # Setup: set elb 1 (production-alb with healthy/unhealthy targets)
        # Execute: show health
        # Assert: Health status for each target
        # Assert: Healthy and unhealthy states shown

    def test_elb_show_listeners_no_data(self, mock_shell_with_fixtures):
        """Test show listeners with no listeners (Github-ALB)."""
        # Setup: set elb 3 (Github-ALB with no listeners)
        # Execute: show listeners
        # Assert: "No listeners" message (not error)

    def test_elb_show_targets_no_data(self, mock_shell_with_fixtures):
        """Test show targets with no target groups."""
        # Setup: set elb 3 (Github-ALB with no targets)
        # Execute: show targets
        # Assert: "No target groups" message (not error)

    # 5 tests for Issue #10
```

---

## Phase 9: Edge Cases & Error Handling (Week 5)

**Goal**: Test error handling and edge cases
**Estimated Tests**: 30
**Priority**: P1-P2

### 9.1 Test File: `test_error_handling.py`

```python
class TestErrorHandling:
    """Test error handling for invalid commands and arguments."""

    def test_unknown_command(self, mock_shell):
        """Test unknown command displays error."""
        # Execute: invalid_command
        # Assert: "Unknown command" error

    def test_show_invalid_option(self, mock_shell):
        """Test show with invalid option."""
        # Execute: show invalid_option
        # Assert: "Invalid option" error with valid options listed

    def test_set_invalid_option(self, mock_shell):
        """Test set with invalid option."""
        # Execute: set invalid_option value
        # Assert: "Invalid option" error

    def test_command_missing_required_arg(self, mock_shell):
        """Test command requiring argument called without one."""
        # Execute: trace
        # Assert: "Usage: trace <src> <dst>" error

    def test_command_in_wrong_context(self, mock_shell_with_fixtures):
        """Test context-specific command in wrong context."""
        # Execute: show segments (without core-network context)
        # Assert: "Invalid option" or context error

    def test_set_context_from_nested_context(self, mock_shell_with_fixtures):
        """Test set vpc from within another context."""
        # Setup: set transit-gateway 1
        # Execute: set vpc 1
        # Assert: Error - must use 'end' first

    # 15 error handling tests
```

### 9.2 Test File: `test_edge_cases.py`

```python
class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_cache_show_command(self, mock_shell):
        """Test show command with empty cache."""
        # Execute: show vpcs (no cache)
        # Assert: Loading spinner, empty result message

    def test_large_dataset_rendering(self, mock_shell):
        """Test rendering very large tables."""
        # Setup: Mock 1000 VPCs
        # Execute: show vpcs
        # Assert: Table renders without error

    def test_special_characters_in_names(self, mock_shell_with_fixtures):
        """Test resources with special characters in names."""
        # Setup: VPC with name "test-vpc_v2.0"
        # Execute: set vpc test-vpc_v2.0
        # Assert: Context entered successfully

    def test_null_name_handling(self, mock_shell_with_fixtures):
        """Test resources with null names."""
        # Setup: set vpc 3 (default VPC with null name)
        # Execute: show detail
        # Assert: ID displayed instead of name

    def test_concurrent_command_execution(self, mock_shell_with_fixtures):
        """Test rapid command execution."""
        # Execute: Multiple commands in quick succession
        # Assert: All execute correctly without interference

    # 15 edge case tests
```

---

## Phase 10: Integration Tests (Week 5)

**Goal**: Test complex workflows and command sequences
**Estimated Tests**: 20
**Priority**: P1

### 10.1 Test File: `test_integration_workflows.py`

```python
class TestIntegrationWorkflows:
    """Test complex command sequences and workflows."""

    def test_deep_context_navigation(self, mock_shell_with_fixtures):
        """Test navigating to deepest context level."""
        # Execute: set global-network 1
        # Execute: set core-network 1
        # Execute: set route-table 1
        # Execute: show routes
        # Assert: Routes displayed
        # Execute: exit, exit, exit
        # Assert: Back at root

    def test_find_prefix_across_contexts(self, mock_shell_with_fixtures):
        """Test find_prefix returns different results per context."""
        # Execute: find_prefix 10.0.0.0/8 (root)
        # Execute: set vpc 1, find_prefix 10.0.0.0/8 (vpc)
        # Execute: end, set transit-gateway 1, find_prefix 10.0.0.0/8 (tgw)
        # Assert: Different results in each context

    def test_output_format_changes_during_session(self, mock_shell_with_fixtures):
        """Test changing output format multiple times."""
        # Execute: show vpcs (table)
        # Execute: set output-format json, show vpcs (json)
        # Execute: set output-format yaml, show vpcs (yaml)
        # Execute: set output-format table, show vpcs (table)
        # Assert: Each format correct

    def test_cache_behavior_across_contexts(self, mock_shell_with_fixtures):
        """Test cache usage across context changes."""
        # Execute: show vpcs (caches data)
        # Execute: set vpc 1 (uses cached data)
        # Execute: clear_cache
        # Execute: show vpcs (re-fetches)
        # Assert: Cache behavior correct

    def test_watch_mode_with_context_change(self, mock_shell_with_fixtures):
        """Test watch mode interrupted by context change."""
        # Execute: show vpcs watch 1 (start watch)
        # Interrupt with Ctrl-C
        # Execute: set vpc 1
        # Assert: Context change successful

    # 10 integration workflow tests
```

---

## Test Execution Strategy

### Week 1: Foundation
```bash
pytest tests/test_root_show_commands.py -v
pytest tests/test_root_set_commands.py -v
pytest tests/test_navigation_commands.py -v
pytest tests/test_context_entry.py -v
```

### Week 2: VPC & TGW (Most Used)
```bash
pytest tests/test_vpc_context.py -v
pytest tests/test_transit_gateway_context.py -v
pytest tests/test_action_commands.py -v
```

### Week 3: CloudWAN (Most Complex)
```bash
pytest tests/test_global_network_context.py -v
pytest tests/test_core_network_context.py -v
pytest tests/test_route_table_context.py -v
pytest tests/test_context_aware_commands.py -v
```

### Week 4: Remaining Contexts & Issues
```bash
pytest tests/test_firewall_context.py -v
pytest tests/test_ec2_context.py -v
pytest tests/test_elb_context.py -v
pytest tests/test_vpn_context.py -v
pytest tests/test_issue_9_ec2_filtering.py -v
pytest tests/test_issue_10_elb_data.py -v
```

### Week 5: Polish & Integration
```bash
pytest tests/test_output_formats.py -v
pytest tests/test_pipe_operators.py -v
pytest tests/test_watch_mode.py -v
pytest tests/test_edge_cases.py -v
pytest tests/test_integration_workflows.py -v
```

---

## Code Coverage Goals

### Target Coverage by Component

```
src/aws_network_tools/shell/
├── base.py                    → 95% (context management)
├── main.py                    → 90% (command dispatch)
├── handlers/
│   ├── root.py               → 90% (root commands)
│   ├── cloudwan.py           → 85% (complex CloudWAN logic)
│   ├── vpc.py                → 90% (VPC commands)
│   ├── tgw.py                → 90% (TGW commands)
│   ├── ec2.py                → 90% (EC2 commands + Issue #9)
│   ├── elb.py                → 90% (ELB commands + Issue #10)
│   ├── firewall.py           → 85% (firewall commands)
│   ├── vpn.py                → 90% (VPN commands)
│   └── utilities.py          → 80% (utility commands)
```

**Overall Target**: 90%+ code coverage

---

## Test Naming Conventions

### Pattern
```
test_<context>_<command>_<scenario>
```

### Examples
- `test_root_show_vpcs_valid_data`
- `test_vpc_context_show_subnets_empty`
- `test_core_network_find_prefix_exact_match`
- `test_issue_9_ec2_show_enis_filters_to_instance`
- `test_elb_show_listeners_json_format`

---

## Continuous Testing Strategy

### Pre-commit Hooks
```bash
# Run fast tests before commit
pytest tests/ -k "not integration" --maxfail=1

# Check coverage
pytest tests/ --cov=src/aws_network_tools/shell --cov-report=term-missing
```

### CI/CD Pipeline
```yaml
# .github/workflows/test.yml
test:
  - Run unit tests
  - Run integration tests
  - Generate coverage report
  - Fail if coverage < 90%
```

---

## Success Metrics

### Definition of Done
- ✅ All 111 unique commands have at least 1 test
- ✅ All known issues (9, 10) have regression tests
- ✅ Code coverage ≥ 90%
- ✅ All tests passing in CI/CD
- ✅ Fixture validation passing
- ✅ No manual testing required for regression validation

### Quality Gates
1. **Command Coverage**: 100% of commands tested
2. **Branch Coverage**: 90%+ code branches covered
3. **Issue Coverage**: All GitHub issues have tests
4. **Performance**: All tests execute in < 5 minutes
5. **Maintenance**: Clear test names and documentation

---

## Summary

This roadmap provides a structured 5-week plan to achieve comprehensive test coverage for all 111 unique commands across 10 contexts. The phased approach prioritizes critical functionality (root commands, context entry) before moving to complex features (CloudWAN, watch mode) and issue resolution. With proper fixture data and systematic execution, we can achieve 90%+ code coverage and prevent regression for all identified issues.
