"""Shared pytest fixtures"""

import pytest
from unittest.mock import MagicMock, patch
from rich.console import Console
from io import StringIO


@pytest.fixture
def mock_console():
    """Create a mock console that captures output"""
    output = StringIO()
    console = Console(file=output, force_terminal=True, width=120)
    console._output = output
    return console


@pytest.fixture
def mock_boto_session():
    """Mock boto3 session"""
    with patch("boto3.Session") as mock:
        session = MagicMock()
        mock.return_value = session
        yield session


@pytest.fixture
def sample_vpc_data():
    """Sample VPC data for testing"""
    return [
        {
            "id": "vpc-123",
            "name": "test-vpc",
            "region": "eu-west-1",
            "cidr": "10.0.0.0/16",
            "cidrs": ["10.0.0.0/16"],
            "state": "available",
        }
    ]


@pytest.fixture
def sample_vpc_detail():
    """Sample VPC detail data"""
    return {
        "id": "vpc-123",
        "name": "test-vpc",
        "region": "eu-west-1",
        "cidr": "10.0.0.0/16",
        "cidrs": ["10.0.0.0/16"],
        "route_tables": [
            {
                "id": "rtb-123",
                "name": "main",
                "is_main": True,
                "subnets": ["subnet-1"],
                "routes": [
                    {
                        "destination": "10.0.0.0/16",
                        "target": "local",
                        "state": "active",
                    },
                    {
                        "destination": "0.0.0.0/0",
                        "target": "igw-123",
                        "state": "active",
                    },
                ],
            }
        ],
        "security_groups": [
            {
                "id": "sg-123",
                "name": "default",
                "description": "Default SG",
                "ingress": [{"protocol": "tcp", "ports": "443", "source": "0.0.0.0/0"}],
                "egress": [{"protocol": "-1", "ports": "All", "dest": "0.0.0.0/0"}],
            }
        ],
        "nacls": [
            {
                "id": "acl-123",
                "name": "acl-123",
                "is_default": True,
                "entries": [
                    {
                        "rule_number": 100,
                        "protocol": "-1",
                        "action": "allow",
                        "cidr": "0.0.0.0/0",
                        "egress": False,
                        "rule": "100 ALLOW -1 0.0.0.0/0",
                    }
                ],
            }
        ],
    }


@pytest.fixture
def sample_tgw_data():
    """Sample TGW data"""
    return [
        {
            "id": "tgw-123",
            "name": "test-tgw",
            "region": "eu-west-1",
            "state": "available",
            "attachments": [],
            "route_tables": [
                {
                    "id": "tgw-rtb-123",
                    "name": "main",
                    "routes": [
                        {
                            "prefix": "10.0.0.0/8",
                            "target": "tgw-attach-123",
                            "state": "active",
                            "type": "propagated",
                            "target_type": "vpc",
                        },
                    ],
                }
            ],
        }
    ]


@pytest.fixture
def sample_cloudwan_data():
    """Sample Cloud WAN data"""
    return [
        {
            "id": "core-network-123",
            "name": "test-core-network",
            "global_network_id": "global-network-123",
            "global_network_name": "test-global-network",
            "regions": ["eu-west-1", "eu-west-2"],
            "segments": ["prod", "dev"],
            "nfgs": [],
            "route_tables": [
                {
                    "id": "prod|eu-west-1",
                    "name": "prod",
                    "region": "eu-west-1",
                    "type": "segment",
                    "routes": [
                        {
                            "prefix": "10.0.0.0/16",
                            "target": "attachment-123",
                            "target_type": "vpc",
                            "state": "ACTIVE",
                            "type": "propagated",
                        },
                        {
                            "prefix": "0.0.0.0/0",
                            "target": "unknown",
                            "target_type": "unknown",
                            "state": "BLACKHOLE",
                            "type": "static",
                        },
                    ],
                }
            ],
            "policy": {"version": "2021.12", "segments": []},
        }
    ]


@pytest.fixture
def sample_firewall_data():
    """Sample Network Firewall data"""
    return [
        {
            "name": "test-firewall",
            "arn": "arn:aws:network-firewall:eu-west-1:123456789:firewall/test-firewall",
            "region": "eu-west-1",
            "vpc_id": "vpc-123",
            "policy_arn": "arn:aws:network-firewall:eu-west-1:123456789:firewall-policy/test-policy",
            "rule_groups": [
                {
                    "name": "test-rule-group",
                    "arn": "arn:aws:network-firewall:eu-west-1:123456789:stateful-rulegroup/test",
                    "type": "STATEFUL",
                    "priority": 1,
                    "rules": [],
                }
            ],
        }
    ]


@pytest.fixture
def sample_policy_versions():
    """Sample policy versions"""
    return [
        {
            "version": 5,
            "alias": "LIVE",
            "change_set_state": "EXECUTED",
            "created_at": "2024-01-15 10:30:00",
        },
        {
            "version": 4,
            "alias": "",
            "change_set_state": "EXECUTED",
            "created_at": "2024-01-10 14:20:00",
        },
        {
            "version": 3,
            "alias": "",
            "change_set_state": "EXECUTED",
            "created_at": "2024-01-05 09:15:00",
        },
    ]


@pytest.fixture
def isolated_shell():
    """Provide isolated shell instance per test with no caching."""
    from aws_network_tools.shell import AWSNetShell

    shell = AWSNetShell()
    shell.no_cache = True
    yield shell
    # Cleanup
    shell._cache.clear()
    shell.context_stack.clear()
