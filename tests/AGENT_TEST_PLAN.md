# AWS Network Shell - Agent-Executable Test Plan

## Overview

This test plan is designed for autonomous agent execution with real infrastructure validation. Each test:
1. Captures baseline state from AWS CLI
2. Runs shell command
3. Validates output against baseline
4. Extracts context for subsequent commands

## Test Environment

```yaml
profile: taylaand+net-dev-Admin
account: 606289744762
shell_command: source .venv/bin/activate && aws-net-shell
working_dir: /Users/taylaand/code/personal/aws_network_shell
```

## Execution Protocol

### For Each Test:
1. **BASELINE**: Run AWS CLI command to get ground truth
2. **EXECUTE**: Run shell command
3. **CAPTURE**: Store output for validation
4. **VALIDATE**: Compare shell output to baseline
5. **EXTRACT**: Pull IDs/names for next command context
6. **VERDICT**: PASS (data matches) / FAIL (data mismatch or error)

### Pass Criteria:
- Command executes without error
- Output contains expected resource IDs from baseline
- Counts match (e.g., 5 VPCs in baseline = 5 VPCs in shell)
- Data accuracy (CIDRs, names, states match)

---

## Phase 1: Infrastructure Baseline

### 1.1 Capture VPC Baseline
```bash
# BASELINE COMMAND
aws ec2 describe-vpcs --profile taylaand+net-dev-Admin --output json \
  --query 'Vpcs[*].{VpcId:VpcId,CidrBlock:CidrBlock,State:State,Tags:Tags}' > /tmp/baseline_vpcs.json

# EXTRACT
- vpc_count: $(jq length /tmp/baseline_vpcs.json)
- vpc_ids: $(jq -r '.[].VpcId' /tmp/baseline_vpcs.json)
- vpc_cidrs: $(jq -r '.[].CidrBlock' /tmp/baseline_vpcs.json)
```

### 1.2 Capture TGW Baseline
```bash
# BASELINE COMMAND
aws ec2 describe-transit-gateways --profile taylaand+net-dev-Admin --output json \
  --query 'TransitGateways[*].{TgwId:TransitGatewayId,State:State,Tags:Tags}' > /tmp/baseline_tgws.json

# EXTRACT
- tgw_count: $(jq length /tmp/baseline_tgws.json)
- tgw_ids: $(jq -r '.[].TgwId' /tmp/baseline_tgws.json)
```

### 1.3 Capture VPN Baseline
```bash
# BASELINE COMMAND
aws ec2 describe-vpn-connections --profile taylaand+net-dev-Admin --output json \
  --query 'VpnConnections[*].{VpnId:VpnConnectionId,State:State,TunnelStatus:VgwTelemetry}' > /tmp/baseline_vpns.json

# EXTRACT
- vpn_count: $(jq length /tmp/baseline_vpns.json)
- vpn_ids: $(jq -r '.[].VpnId' /tmp/baseline_vpns.json)
- tunnel_states: $(jq -r '.[].TunnelStatus[].Status' /tmp/baseline_vpns.json)
```

### 1.4 Capture Firewall Baseline
```bash
# BASELINE COMMAND
aws network-firewall list-firewalls --profile taylaand+net-dev-Admin --output json > /tmp/baseline_firewalls.json

# EXTRACT
- fw_count: $(jq '.Firewalls | length' /tmp/baseline_firewalls.json)
- fw_names: $(jq -r '.Firewalls[].FirewallName' /tmp/baseline_firewalls.json)
```

### 1.5 Capture CloudWAN Baseline
```bash
# BASELINE COMMAND
aws networkmanager list-core-networks --profile taylaand+net-dev-Admin --output json > /tmp/baseline_corenetworks.json
aws networkmanager describe-global-networks --profile taylaand+net-dev-Admin --output json > /tmp/baseline_globalnetworks.json

# EXTRACT
- gn_count: $(jq '.GlobalNetworks | length' /tmp/baseline_globalnetworks.json)
- cn_count: $(jq '.CoreNetworks | length' /tmp/baseline_corenetworks.json)
- cn_ids: $(jq -r '.CoreNetworks[].CoreNetworkId' /tmp/baseline_corenetworks.json)
```

---

## Phase 2: Root Level Command Tests

### Test 2.1: show vpcs
```yaml
test_id: ROOT_001
command: show vpcs
baseline_file: /tmp/baseline_vpcs.json

validation:
  - row_count_matches: "Number of VPCs in table == vpc_count from baseline"
  - ids_present: "All vpc_ids from baseline appear in output"
  - cidrs_match: "CIDR blocks match baseline values"

extract_for_next:
  - first_vpc_number: "Row number of first VPC (for set vpc command)"
  - first_vpc_id: "VPC ID to validate after context entry"

pass_criteria:
  - No error/exception
  - Count matches baseline
  - All VPC IDs present
  - At least one CIDR matches
```

### Test 2.2: show transit_gateways
```yaml
test_id: ROOT_002
command: show transit_gateways
baseline_file: /tmp/baseline_tgws.json

validation:
  - row_count_matches: "Number of TGWs == tgw_count"
  - ids_present: "All tgw_ids appear in output"

extract_for_next:
  - first_tgw_number: "Row number for set transit-gateway"
  - first_tgw_id: "TGW ID to validate"

pass_criteria:
  - No error/exception
  - Count matches baseline
  - All TGW IDs present
```

### Test 2.3: show vpns
```yaml
test_id: ROOT_003
command: show vpns
baseline_file: /tmp/baseline_vpns.json

validation:
  - row_count_matches: "Number of VPNs == vpn_count"
  - ids_present: "All vpn_ids appear in output"

extract_for_next:
  - first_vpn_number: "Row number for set vpn"
  - first_vpn_id: "VPN ID to validate"

pass_criteria:
  - No error/exception
  - Count matches baseline
  - All VPN IDs present
```

### Test 2.4: show firewalls
```yaml
test_id: ROOT_004
command: show firewalls
baseline_file: /tmp/baseline_firewalls.json

validation:
  - row_count_matches: "Number of firewalls == fw_count"
  - names_present: "All fw_names appear in output"

extract_for_next:
  - first_fw_number: "Row number for set firewall"
  - first_fw_name: "Firewall name to validate"

pass_criteria:
  - No error/exception
  - Count matches baseline
  - All firewall names present
```

### Test 2.5: show global-networks
```yaml
test_id: ROOT_005
command: show global-networks
baseline_file: /tmp/baseline_globalnetworks.json

validation:
  - row_count_matches: "Number of global networks == gn_count"

extract_for_next:
  - first_gn_number: "Row number for set global-network"

pass_criteria:
  - No error/exception
  - Count matches baseline
```

---

## Phase 3: VPC Context Tests

### Test 3.1: Enter VPC Context
```yaml
test_id: VPC_001
depends_on: ROOT_001
command: set vpc {first_vpc_number}

validation:
  - prompt_changes: "Prompt shows VPC name/ID"
  - no_error: "No error message"

extract_for_next:
  - vpc_context_id: "VPC ID now in context"

pass_criteria:
  - Context entered successfully
  - Prompt reflects VPC context
```

### Test 3.2: show subnets (in VPC context)
```yaml
test_id: VPC_002
depends_on: VPC_001
command: show subnets

baseline_command: |
  aws ec2 describe-subnets --profile taylaand+net-dev-Admin \
    --filters "Name=vpc-id,Values={vpc_context_id}" --output json \
    --query 'Subnets[*].{SubnetId:SubnetId,CidrBlock:CidrBlock,Az:AvailabilityZone}'

validation:
  - row_count_matches: "Subnet count matches baseline"
  - ids_present: "All SubnetIds appear"
  - cidrs_match: "CIDRs match baseline"
  - azs_match: "AZs match baseline"

pass_criteria:
  - Count matches
  - All subnet IDs present
  - CIDRs accurate
```

### Test 3.3: show route-tables (in VPC context)
```yaml
test_id: VPC_003
depends_on: VPC_001
command: show route-tables

baseline_command: |
  aws ec2 describe-route-tables --profile taylaand+net-dev-Admin \
    --filters "Name=vpc-id,Values={vpc_context_id}" --output json

validation:
  - row_count_matches: "Route table count matches"
  - ids_present: "All RouteTableIds appear"

extract_for_next:
  - first_rt_number: "Row number for set route-table"
  - first_rt_id: "Route table ID"

pass_criteria:
  - Count matches baseline
  - All route table IDs present
```

### Test 3.4: show security-groups (in VPC context)
```yaml
test_id: VPC_004
depends_on: VPC_001
command: show security-groups

baseline_command: |
  aws ec2 describe-security-groups --profile taylaand+net-dev-Admin \
    --filters "Name=vpc-id,Values={vpc_context_id}" --output json \
    --query 'SecurityGroups[*].{GroupId:GroupId,GroupName:GroupName}'

validation:
  - row_count_matches: "SG count matches"
  - ids_present: "All GroupIds appear"

pass_criteria:
  - Count matches baseline
  - All security group IDs present
```

### Test 3.5: Enter Route Table Context from VPC
```yaml
test_id: VPC_005
depends_on: VPC_003
command: set route-table {first_rt_number}

validation:
  - prompt_changes: "Prompt shows route-table context"
  - no_error: "No error message"

pass_criteria:
  - Context entered successfully
```

### Test 3.6: show routes (in VPC route-table context)
```yaml
test_id: VPC_006
depends_on: VPC_005
command: show routes

baseline_command: |
  aws ec2 describe-route-tables --profile taylaand+net-dev-Admin \
    --route-table-ids {first_rt_id} --output json \
    --query 'RouteTables[0].Routes'

validation:
  - route_count_matches: "Number of routes matches"
  - destinations_present: "All DestinationCidrBlocks appear"
  - targets_present: "Gateway/NAT/TGW targets shown"
  - states_accurate: "Route states (active/blackhole) match"

pass_criteria:
  - Route count matches
  - All destinations present
  - Targets accurate
  - States correct
```

---

## Phase 4: Transit Gateway Context Tests

### Test 4.1: Enter TGW Context
```yaml
test_id: TGW_001
depends_on: ROOT_002
command: set transit-gateway {first_tgw_number}

validation:
  - prompt_changes: "Prompt shows TGW context"

pass_criteria:
  - Context entered successfully
```

### Test 4.2: show route-tables (in TGW context)
```yaml
test_id: TGW_002
depends_on: TGW_001
command: show route-tables

baseline_command: |
  aws ec2 describe-transit-gateway-route-tables --profile taylaand+net-dev-Admin \
    --filters "Name=transit-gateway-id,Values={first_tgw_id}" --output json

validation:
  - row_count_matches: "Route table count matches"
  - ids_present: "All route table IDs appear"

extract_for_next:
  - first_tgw_rt_number: "Row number"
  - first_tgw_rt_id: "Route table ID"

pass_criteria:
  - Count matches baseline
```

### Test 4.3: show routes (in TGW route-table context)
```yaml
test_id: TGW_003
depends_on: TGW_002
command: |
  set route-table {first_tgw_rt_number}
  show routes

baseline_command: |
  aws ec2 search-transit-gateway-routes --profile taylaand+net-dev-Admin \
    --transit-gateway-route-table-id {first_tgw_rt_id} \
    --filters "Name=state,Values=active,blackhole" --output json

validation:
  - route_count_matches: "Route count matches"
  - destinations_present: "All CIDR destinations appear"
  - attachment_ids_present: "Attachment targets shown"
  - states_accurate: "active/blackhole states match"

pass_criteria:
  - Route count matches
  - Destinations accurate
  - States correct
```

---

## Phase 5: VPN Context Tests (REQUIRES ACTIVE TUNNEL)

### Test 5.1: Enter VPN Context
```yaml
test_id: VPN_001
depends_on: ROOT_003
command: set vpn {first_vpn_number}

validation:
  - prompt_changes: "Prompt shows VPN context"

pass_criteria:
  - Context entered successfully
```

### Test 5.2: show detail (in VPN context)
```yaml
test_id: VPN_002
depends_on: VPN_001
command: show detail

baseline_command: |
  aws ec2 describe-vpn-connections --profile taylaand+net-dev-Admin \
    --vpn-connection-ids {first_vpn_id} --output json

validation:
  - vpn_id_matches: "VPN ID shown correctly"
  - state_matches: "Connection state matches (available/pending/etc)"
  - type_matches: "VPN type shown (ipsec.1)"
  - cgw_shown: "Customer Gateway ID present"
  - vgw_or_tgw_shown: "VGW or TGW attachment shown"

pass_criteria:
  - All VPN details accurate
  - State matches baseline
```

### Test 5.3: show tunnels (in VPN context) - CRITICAL
```yaml
test_id: VPN_003
depends_on: VPN_001
command: show tunnels
prerequisite: "At least one IPsec tunnel must be UP"

baseline_command: |
  aws ec2 describe-vpn-connections --profile taylaand+net-dev-Admin \
    --vpn-connection-ids {first_vpn_id} --output json \
    --query 'VpnConnections[0].VgwTelemetry'

validation:
  - tunnel_count: "Shows 2 tunnels (standard AWS VPN)"
  - outside_ips_present: "Outside IP addresses shown"
  - status_matches: "UP/DOWN status matches VgwTelemetry[].Status"
  - status_message: "Status message shown if DOWN"
  - accepted_routes: "AcceptedRouteCount shown"
  - last_status_change: "Timestamp of last change"

pass_criteria:
  - Tunnel count = 2
  - Status matches baseline (at least one UP)
  - Outside IPs accurate
  - Metrics present for UP tunnels
```

### Test 5.4: show bgp (in VPN context) - IF BGP ENABLED
```yaml
test_id: VPN_004
depends_on: VPN_001
command: show bgp
prerequisite: "VPN must use BGP routing (not static)"

baseline_command: |
  aws ec2 describe-vpn-connections --profile taylaand+net-dev-Admin \
    --vpn-connection-ids {first_vpn_id} --output json \
    --query 'VpnConnections[0].Options'

validation:
  - bgp_asn_shown: "Local and remote BGP ASN displayed"
  - tunnel_inside_ips: "Inside tunnel IPs shown"
  - bgp_status: "BGP session state (if available)"

pass_criteria:
  - BGP configuration accurate
  - ASNs match baseline
```

---

## Phase 6: Firewall Context Tests

### Test 6.1: Enter Firewall Context
```yaml
test_id: FW_001
depends_on: ROOT_004
command: set firewall {first_fw_number}

validation:
  - prompt_changes: "Prompt shows firewall context"

pass_criteria:
  - Context entered successfully
```

### Test 6.2: show detail (in Firewall context)
```yaml
test_id: FW_002
depends_on: FW_001
command: show detail

baseline_command: |
  aws network-firewall describe-firewall --profile taylaand+net-dev-Admin \
    --firewall-name {first_fw_name} --output json

validation:
  - name_matches: "Firewall name correct"
  - arn_shown: "Firewall ARN displayed"
  - vpc_id_shown: "VPC ID where deployed"
  - subnet_mappings: "Subnet mappings shown"
  - policy_arn: "Firewall policy ARN shown"
  - status_matches: "FirewallStatus matches"

pass_criteria:
  - All details accurate
  - Status matches baseline
```

### Test 6.3: show rule-groups (in Firewall context)
```yaml
test_id: FW_003
depends_on: FW_001
command: show rule-groups

baseline_command: |
  # Get policy ARN first, then describe policy
  POLICY_ARN=$(aws network-firewall describe-firewall --profile taylaand+net-dev-Admin \
    --firewall-name {first_fw_name} --query 'Firewall.FirewallPolicyArn' --output text)
  aws network-firewall describe-firewall-policy --profile taylaand+net-dev-Admin \
    --firewall-policy-arn $POLICY_ARN --output json

validation:
  - stateless_groups_shown: "Stateless rule group references"
  - stateful_groups_shown: "Stateful rule group references"
  - priorities_shown: "Rule group priorities displayed"

pass_criteria:
  - Rule groups match policy
  - Priorities accurate
```

---

## Phase 7: CloudWAN Context Tests

### Test 7.1: Enter Global Network Context
```yaml
test_id: CWAN_001
depends_on: ROOT_005
command: set global-network {first_gn_number}

validation:
  - prompt_changes: "Prompt shows global-network context"

pass_criteria:
  - Context entered successfully
```

### Test 7.2: show core-networks (in Global Network context)
```yaml
test_id: CWAN_002
depends_on: CWAN_001
command: show core-networks

baseline_file: /tmp/baseline_corenetworks.json

validation:
  - row_count_matches: "Core network count matches"
  - ids_present: "All CoreNetworkIds appear"

extract_for_next:
  - first_cn_number: "Row number"
  - first_cn_id: "Core network ID"

pass_criteria:
  - Count matches baseline
```

### Test 7.3: Enter Core Network Context
```yaml
test_id: CWAN_003
depends_on: CWAN_002
command: set core-network {first_cn_number}

validation:
  - prompt_changes: "Prompt shows core-network context"

pass_criteria:
  - Context entered successfully
```

### Test 7.4: show segments (in Core Network context)
```yaml
test_id: CWAN_004
depends_on: CWAN_003
command: show segments

baseline_command: |
  aws networkmanager get-core-network-policy --profile taylaand+net-dev-Admin \
    --core-network-id {first_cn_id} --output json \
    --query 'CoreNetworkPolicy.Segments'

validation:
  - segment_names_match: "All segment names present"
  - edge_locations_shown: "Edge locations per segment"

pass_criteria:
  - All segments from policy shown
```

### Test 7.5: show route-tables (in Core Network context)
```yaml
test_id: CWAN_005
depends_on: CWAN_003
command: show route-tables

baseline_command: |
  aws networkmanager get-core-network --profile taylaand+net-dev-Admin \
    --core-network-id {first_cn_id} --output json

validation:
  - route_tables_by_segment: "Route tables shown per segment"
  - route_tables_by_edge: "Route tables shown per edge location"
  - route_counts_shown: "Number of routes per table"

extract_for_next:
  - first_cwan_rt_number: "Row number"

pass_criteria:
  - Route tables enumerate correctly
```

### Test 7.6: show routes (in Core Network context - all tables)
```yaml
test_id: CWAN_006
depends_on: CWAN_003
command: show routes

validation:
  - routes_grouped_by_table: "Routes grouped by segment/edge"
  - prefixes_shown: "CIDR prefixes displayed"
  - targets_shown: "Attachment targets shown"
  - states_shown: "active/blackhole states"

pass_criteria:
  - Routes display without error
  - Grouping logical
```

---

## Phase 8: Utility Command Tests

### Test 8.1: find_ip (known IP)
```yaml
test_id: UTIL_001
command: find_ip {known_private_ip}

baseline_command: |
  aws ec2 describe-network-interfaces --profile taylaand+net-dev-Admin \
    --filters "Name=addresses.private-ip-address,Values={known_private_ip}" --output json

validation:
  - eni_found: "ENI ID returned"
  - vpc_shown: "VPC ID where ENI exists"
  - subnet_shown: "Subnet ID shown"
  - az_shown: "Availability zone shown"

pass_criteria:
  - ENI found matches baseline
  - All associated data accurate
```

### Test 8.2: create-routing-cache
```yaml
test_id: UTIL_002
command: create-routing-cache

validation:
  - vpc_routes_nonzero: "VPC routes > 0"
  - tgw_routes_shown: "TGW routes counted"
  - cloudwan_routes_shown: "CloudWAN routes counted"
  - total_calculated: "Total matches sum of parts"

pass_criteria:
  - All route sources populated
  - No errors during cache build
```

### Test 8.3: find-prefix (after cache)
```yaml
test_id: UTIL_003
depends_on: UTIL_002
command: find-prefix 10.0

validation:
  - matches_found: "Routes matching 10.0.x.x returned"
  - source_shown: "Source (vpc/tgw/cloudwan) indicated"
  - region_shown: "Region per route"
  - route_table_shown: "Route table ID"

pass_criteria:
  - Matching routes returned
  - Data accurate per source
```

---

## Execution Agent Instructions

### Setup
```python
# Agent should maintain state between commands
state = {
    "baseline": {},      # Baseline data from AWS CLI
    "extracted": {},     # Values extracted from shell output
    "context_stack": [], # Current shell context path
    "results": []        # Test results
}
```

### Per-Test Execution
```python
def execute_test(test):
    # 1. Run baseline command if specified
    if test.baseline_command:
        baseline = run_aws_cli(test.baseline_command)
        state["baseline"][test.test_id] = baseline

    # 2. Substitute variables from previous extractions
    command = substitute_variables(test.command, state["extracted"])

    # 3. Execute shell command
    output = run_shell_command(command)

    # 4. Validate output against baseline
    validation_result = validate(output, baseline, test.validation)

    # 5. Extract values for next test
    if test.extract_for_next:
        extracted = extract_values(output, test.extract_for_next)
        state["extracted"].update(extracted)

    # 6. Record result
    state["results"].append({
        "test_id": test.test_id,
        "passed": validation_result.passed,
        "details": validation_result.details,
        "output": output
    })

    return validation_result.passed
```

### Failure Handling
```yaml
on_failure:
  - capture_full_output: true
  - capture_traceback: true
  - continue_independent_tests: true
  - halt_dependent_tests: true
  - generate_bug_report: true
```

---

## Test Report Template

```markdown
# AWS Network Shell Test Report
**Date**: {timestamp}
**Profile**: {profile}
**Account**: {account_id}

## Summary
- Total Tests: {total}
- Passed: {passed}
- Failed: {failed}
- Skipped: {skipped}

## Results by Phase

### Phase 1: Baseline
{baseline_capture_status}

### Phase 2: Root Commands
| Test ID | Command | Result | Details |
|---------|---------|--------|---------|
| ROOT_001 | show vpcs | {result} | {details} |
...

### Phase 3: VPC Context
...

## Failures Detail
{for each failure}
### {test_id}: {command}
**Expected**: {expected}
**Actual**: {actual}
**Baseline**: {baseline_data}
**Shell Output**:
```
{raw_output}
```
{end for}

## Recommendations
{auto_generated_fix_suggestions}
```

---

## Quick Start for Agent

```bash
# 1. Activate environment
cd /Users/taylaand/code/personal/aws_network_shell
source .venv/bin/activate

# 2. Capture all baselines
./tests/capture_baselines.sh

# 3. Run test suite
python tests/agent_test_runner.py --profile taylaand+net-dev-Admin

# 4. Generate report
python tests/generate_report.py --output ~/Desktop/aws_net_shell_test_report.md
```
