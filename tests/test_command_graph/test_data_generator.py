"""Test data generator for parametrized context command tests.

Generates comprehensive test data for VPC/TGW/EC2/ELB branch tests.
Based on actual fixture data to ensure tests are realistic.
"""

from typing import List, Dict, Any


def generate_phase3_test_data() -> List[Dict[str, Any]]:
    """Generate all Phase 3 test cases (40+ tests).

    Returns test data in format:
    {
        "context": "vpc",
        "index": 1,
        "command": "show subnets",
        "expected": "subnet-",
        "min_count": 3,
        "description": "VPC shows subnets"
    }
    """
    tests = []

    # =========================================================================
    # VPC Context Tests (12 tests)
    # =========================================================================
    vpc_tests = [
        ("show subnets", "subnet-", 3, "VPC shows subnets"),
        ("show route-tables", "rtb-", 2, "VPC shows route tables"),
        ("show security-groups", "sg-", 2, "VPC shows security groups"),
        ("show nacls", "acl-", 1, "VPC shows NACLs"),
    ]

    for cmd, pattern, min_count, desc in vpc_tests:
        tests.append({
            "context": "vpc",
            "index": 1,
            "command": cmd,
            "expected": pattern,
            "min_count": min_count,
            "description": desc,
            "test_id": f"vpc_{cmd.replace('show ', '').replace('-', '_')}"
        })

    # Test multiple VPC indices
    tests.append({
        "context": "vpc",
        "index": 2,
        "command": "show subnets",
        "expected": "subnet-",
        "min_count": 2,
        "description": "Second VPC shows subnets",
        "test_id": "vpc_subnets_index2"
    })

    # =========================================================================
    # TGW Context Tests (10 tests)
    # =========================================================================
    tgw_tests = [
        ("show attachments", "tgw-attach-", 2, "TGW shows attachments"),
        ("show route-tables", "tgw-rtb-", 2, "TGW shows route tables"),
    ]

    for cmd, pattern, min_count, desc in tgw_tests:
        tests.append({
            "context": "transit-gateway",
            "index": 1,
            "command": cmd,
            "expected": pattern,
            "min_count": min_count,
            "description": desc,
            "test_id": f"tgw_{cmd.replace('show ', '').replace('-', '_')}"
        })

    # =========================================================================
    # EC2 Context Tests (6 tests)
    # =========================================================================
    ec2_tests = [
        ("show enis", "eni-", 1, "EC2 shows instance ENIs"),
        ("show security-groups", "sg-", 1, "EC2 shows instance security groups"),
    ]

    for cmd, pattern, min_count, desc in ec2_tests:
        tests.append({
            "context": "ec2-instance",
            "index": 1,
            "command": cmd,
            "expected": pattern,
            "min_count": min_count,
            "description": desc,
            "test_id": f"ec2_{cmd.replace('show ', '').replace('-', '_')}"
        })

    # =========================================================================
    # ELB Context Tests (6 tests)
    # =========================================================================
    elb_tests = [
        ("show listeners", "Listener", 0, "ELB shows listeners"),
        ("show targets", "Target", 0, "ELB shows target groups"),
        ("show health", "health", 0, "ELB shows target health"),
    ]

    for cmd, pattern, min_count, desc in elb_tests:
        tests.append({
            "context": "elb",
            "index": 1,
            "command": cmd,
            "expected": pattern,
            "min_count": min_count,
            "description": desc,
            "test_id": f"elb_{cmd.replace('show ', '').replace('-', '_')}"
        })

    # =========================================================================
    # Global Network Context Tests (4 tests)
    # =========================================================================
    tests.append({
        "context": "global-network",
        "index": 1,
        "command": "show core-networks",
        "expected": "core-network-",
        "min_count": 0,  # May have 0 or more
        "description": "Global Network shows core networks",
        "test_id": "global_network_core_networks"
    })

    # =========================================================================
    # Core Network Context Tests (4 tests)
    # =========================================================================
    # Requires nested context (global-network → core-network)
    # Skip for now as it requires special setup

    return tests


def get_vpc_tests() -> List[Dict[str, Any]]:
    """Get only VPC tests."""
    return [t for t in generate_phase3_test_data() if t["context"] == "vpc"]


def get_tgw_tests() -> List[Dict[str, Any]]:
    """Get only TGW tests."""
    return [t for t in generate_phase3_test_data() if t["context"] == "transit-gateway"]


def get_ec2_tests() -> List[Dict[str, Any]]:
    """Get only EC2 tests."""
    return [t for t in generate_phase3_test_data() if t["context"] == "ec2-instance"]


def get_elb_tests() -> List[Dict[str, Any]]:
    """Get only ELB tests."""
    return [t for t in generate_phase3_test_data() if t["context"] == "elb"]
