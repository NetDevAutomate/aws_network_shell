# Command Graph Test Suite

## Overview

Comprehensive test suite for AWS Network Shell command graph testing with binary pass/fail validation.

## Test Structure

```
tests/test_command_graph/
├── README.md (this file)
├── conftest.py (fixtures, mocks, helpers)
├── test_top_level_commands.py (root context commands)
├── test_vpc_context_commands.py (VPC context commands)
├── test_tgw_context_commands.py (Transit Gateway context)
├── test_cloudwan_context_commands.py (CloudWAN/Global Network context)
├── test_ec2_context_commands.py (EC2 instance context)
├── test_elb_context_commands.py (ELB context)
├── test_firewall_context_commands.py (Network Firewall context)
├── test_vpn_context_commands.py (VPN context)
├── test_show_commands.py (all show commands)
├── test_set_commands.py (all set commands)
├── test_context_transitions.py (context navigation)
└── test_coverage_report.py (coverage validation)
```

## Testing Methodology

### TDD Approach

1. Write failing test first
2. Run test and capture failure
3. Implement minimal code to pass
4. Refactor and iterate
5. Move to next test

### Binary Pass/Fail

All tests use binary assertions:

- `assert result.exit_code == 0` for success
- `assert result.exit_code != 0` for expected failures
- `assert "expected_text" in result.output` for data validation

### Mock Strategy

- ALL boto3 calls are mocked
- Use fixture data from `tests/fixtures/`
- No real AWS API calls
- Isolated shell instance per test

## Running Tests

```bash
# Run all command graph tests
pytest tests/test_command_graph/ -v

# Run specific context tests
pytest tests/test_command_graph/test_vpc_context_commands.py -v

# Run with coverage
pytest tests/test_command_graph/ --cov=src/aws_network_tools --cov-report=html

# Run single test
pytest tests/test_command_graph/test_top_level_commands.py::test_show_version -v
```

## Test Coverage Goals

- 100% of HIERARCHY commands tested
- All context transitions validated
- All show/set command combinations
- Error handling for invalid commands
- Output format validation (table, json, yaml)

## Known Limitations

See `test_coverage_report.py` for commands that cannot be tested and justification.
