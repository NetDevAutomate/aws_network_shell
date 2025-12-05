# Test Fixture Requirements for AWS Network Shell

**Generated**: 2024-12-04
**Purpose**: Define comprehensive fixture data requirements for complete test coverage

---

## Overview

Test fixtures must provide realistic AWS resource data that supports:
1. All context entry scenarios (valid/invalid references)
2. Context-specific show commands with proper data structure
3. Context-aware command behavior testing
4. Edge cases (empty data, missing fields, etc.)

---

## 1. Global Networks Fixture

**File**: `tests/fixtures/global_networks.json`

```json
{
  "global_networks": [
    {
      "id": "global-network-01234567890abcdef",
      "name": "production-global-network",
      "state": "AVAILABLE",
      "description": "Production global network for testing",
      "tags": [
        {"Key": "Name", "Value": "production-global-network"},
        {"Key": "Environment", "Value": "production"}
      ],
      "core_networks": [
        {
          "id": "core-network-0a1b2c3d4e5f",
          "name": "prod-core-network",
          "state": "AVAILABLE"
        },
        {
          "id": "core-network-9z8y7x6w5v4u",
          "name": "staging-core-network",
          "state": "AVAILABLE"
        }
      ]
    },
    {
      "id": "global-network-fedcba09876543210",
      "name": "test-global-network",
      "state": "AVAILABLE",
      "description": "Test global network",
      "core_networks": []
    }
  ]
}
```

**Test Scenarios**:
- Valid index selection (1, 2)
- Valid name selection ("production-global-network", "test-global-network")
- Valid ID selection
- Invalid reference (0, 999, "nonexistent")
- Empty core networks list

---

## 2. Core Networks Fixture

**File**: `tests/fixtures/core_networks.json`

```json
{
  "core_networks": [
    {
      "id": "core-network-0a1b2c3d4e5f",
      "name": "prod-core-network",
      "global_network_id": "global-network-01234567890abcdef",
      "state": "AVAILABLE",
      "description": "Production core network",
      "policy": {
        "core-network-configuration": {
          "asn-ranges": ["64512-65534"],
          "edge-locations": [
            {"location": "us-east-1"},
            {"location": "eu-west-1"}
          ]
        },
        "segments": [
          {
            "name": "production",
            "description": "Production segment",
            "require-attachment-acceptance": false
          },
          {
            "name": "staging",
            "description": "Staging segment",
            "require-attachment-acceptance": false
          }
        ],
        "segment-actions": []
      },
      "route_tables": [
        {
          "id": "rt-cloudwan-prod-useast1",
          "segment": "production",
          "edge_location": "us-east-1",
          "routes": [
            {
              "prefix": "10.0.0.0/8",
              "target": "attachment-vpc-01",
              "type": "propagated",
              "state": "ACTIVE"
            },
            {
              "prefix": "192.168.0.0/16",
              "target": "attachment-vpc-02",
              "type": "propagated",
              "state": "BLACKHOLE"
            }
          ]
        },
        {
          "id": "rt-cloudwan-staging-useast1",
          "segment": "staging",
          "edge_location": "us-east-1",
          "routes": [
            {
              "prefix": "172.16.0.0/12",
              "target": "attachment-vpc-03",
              "type": "static",
              "state": "ACTIVE"
            }
          ]
        }
      ],
      "segments": [
        {"name": "production", "edge_locations": ["us-east-1", "eu-west-1"]},
        {"name": "staging", "edge_locations": ["us-east-1"]}
      ]
    }
  ]
}
```

**Test Scenarios**:
- Policy document parsing
- Segment filtering for `show rib`
- Edge location filtering for `show rib`
- Route table enumeration
- Blackhole route detection
- Prefix searching across segments

---

## 3. VPCs Fixture

**File**: `tests/fixtures/vpcs.json`

```json
{
  "vpcs": [
    {
      "id": "vpc-0a1b2c3d4e5f6g7h8",
      "name": "production-vpc",
      "region": "us-east-1",
      "cidr": "10.0.0.0/16",
      "state": "available",
      "is_default": false,
      "tags": [
        {"Key": "Name", "Value": "production-vpc"},
        {"Key": "Environment", "Value": "production"}
      ],
      "route_tables": [
        {
          "id": "rtb-0a1b2c3d4e5f",
          "name": "production-public-rt",
          "routes": [
            {
              "prefix": "10.0.0.0/16",
              "target": "local",
              "state": "active"
            },
            {
              "prefix": "0.0.0.0/0",
              "target": "igw-01234567",
              "state": "active"
            },
            {
              "prefix": "192.168.1.0/24",
              "target": "tgw-01234567",
              "state": "blackhole"
            }
          ]
        },
        {
          "id": "rtb-9z8y7x6w5v4u",
          "name": "production-private-rt",
          "routes": [
            {
              "prefix": "10.0.0.0/16",
              "target": "local",
              "state": "active"
            },
            {
              "prefix": "0.0.0.0/0",
              "target": "nat-01234567",
              "state": "active"
            }
          ]
        }
      ],
      "subnets": [
        {
          "id": "subnet-0a1b2c3d",
          "name": "production-public-1a",
          "cidr": "10.0.1.0/24",
          "az": "us-east-1a",
          "available_ips": 251
        },
        {
          "id": "subnet-9z8y7x6w",
          "name": "production-private-1a",
          "cidr": "10.0.10.0/24",
          "az": "us-east-1a",
          "available_ips": 250
        }
      ],
      "security_groups": [
        {
          "id": "sg-0a1b2c3d4e5f",
          "name": "production-web-sg",
          "description": "Web server security group"
        }
      ],
      "nacls": [
        {
          "id": "acl-0a1b2c3d",
          "name": "production-nacl",
          "default": false
        }
      ],
      "internet_gateways": [
        {
          "id": "igw-01234567",
          "state": "available"
        }
      ],
      "nat_gateways": [
        {
          "id": "nat-01234567",
          "subnet_id": "subnet-0a1b2c3d",
          "state": "available"
        }
      ],
      "endpoints": [
        {
          "id": "vpce-0a1b2c3d",
          "service": "com.amazonaws.us-east-1.s3",
          "type": "Gateway"
        }
      ]
    },
    {
      "id": "vpc-9z8y7x6w5v4u3t2s1",
      "name": "test-vpc",
      "region": "us-west-2",
      "cidr": "172.16.0.0/16",
      "state": "available",
      "is_default": false,
      "route_tables": [],
      "subnets": [],
      "security_groups": [],
      "nacls": [],
      "internet_gateways": [],
      "nat_gateways": [],
      "endpoints": []
    },
    {
      "id": "vpc-default123456789",
      "name": null,
      "region": "us-east-1",
      "cidr": "172.31.0.0/16",
      "state": "available",
      "is_default": true,
      "route_tables": [
        {
          "id": "rtb-default123",
          "name": null,
          "routes": [
            {
              "prefix": "172.31.0.0/16",
              "target": "local",
              "state": "active"
            }
          ]
        }
      ],
      "subnets": [],
      "security_groups": [],
      "nacls": [],
      "internet_gateways": [],
      "nat_gateways": [],
      "endpoints": []
    }
  ]
}
```

**Test Scenarios**:
- VPC with full configuration (production-vpc)
- VPC with empty resources (test-vpc)
- Default VPC with null name
- Route table with blackhole routes
- Subnet enumeration
- Security group listing
- NACL listing
- Gateway listing

---

## 4. Transit Gateways Fixture

**File**: `tests/fixtures/transit_gateways.json`

```json
{
  "transit_gateways": [
    {
      "id": "tgw-0a1b2c3d4e5f6g7h8",
      "name": "production-tgw",
      "region": "us-east-1",
      "state": "available",
      "amazon_side_asn": 64512,
      "route_tables": [
        {
          "id": "tgw-rtb-0a1b2c3d",
          "name": "production-rt",
          "default": false,
          "routes": [
            {
              "prefix": "10.0.0.0/8",
              "target": "tgw-attach-vpc-01",
              "type": "propagated",
              "state": "active"
            },
            {
              "prefix": "192.168.0.0/16",
              "target": "tgw-attach-vpc-02",
              "type": "static",
              "state": "blackhole"
            }
          ]
        },
        {
          "id": "tgw-rtb-9z8y7x6w",
          "name": "staging-rt",
          "default": false,
          "routes": []
        }
      ],
      "attachments": [
        {
          "id": "tgw-attach-vpc-01",
          "type": "vpc",
          "resource_id": "vpc-0a1b2c3d4e5f6g7h8",
          "state": "available"
        },
        {
          "id": "tgw-attach-vpn-01",
          "type": "vpn",
          "resource_id": "vpn-01234567",
          "state": "available"
        }
      ]
    },
    {
      "id": "tgw-9z8y7x6w5v4u3t2s1",
      "name": "test-tgw",
      "region": "us-west-2",
      "state": "available",
      "amazon_side_asn": 64513,
      "route_tables": [],
      "attachments": []
    }
  ]
}
```

**Test Scenarios**:
- TGW with route tables and attachments
- TGW with empty configuration
- Route table selection
- Attachment enumeration
- Blackhole route detection
- Prefix searching

---

## 5. Firewalls Fixture

**File**: `tests/fixtures/firewalls.json`

```json
{
  "firewalls": [
    {
      "id": "firewall-0a1b2c3d4e5f",
      "name": "production-anfw",
      "region": "us-east-1",
      "arn": "arn:aws:network-firewall:us-east-1:123456789012:firewall/production-anfw",
      "vpc_id": "vpc-0a1b2c3d4e5f6g7h8",
      "subnet_mappings": [
        {"subnet_id": "subnet-0a1b2c3d", "az": "us-east-1a"}
      ],
      "rule_groups": [
        {
          "id": "rg-0a1b2c3d",
          "name": "allow-https",
          "type": "STATEFUL",
          "priority": 100
        }
      ],
      "policy": {
        "id": "policy-0a1b2c3d",
        "name": "production-policy",
        "stateless_default_actions": ["aws:forward_to_sfe"],
        "stateful_default_actions": ["aws:drop_strict"]
      }
    },
    {
      "id": "firewall-9z8y7x6w5v4u",
      "name": "test-anfw",
      "region": "us-west-2",
      "arn": "arn:aws:network-firewall:us-west-2:123456789012:firewall/test-anfw",
      "vpc_id": "vpc-9z8y7x6w5v4u3t2s1",
      "subnet_mappings": [],
      "rule_groups": [],
      "policy": null
    }
  ]
}
```

**Test Scenarios**:
- Firewall with complete configuration
- Firewall with minimal data
- Rule group enumeration
- Policy display

---

## 6. EC2 Instances Fixture

**File**: `tests/fixtures/ec2_instances.json`

```json
{
  "ec2_instances": [
    {
      "id": "i-0a1b2c3d4e5f6g7h8",
      "name": "production-web-01",
      "type": "t3.medium",
      "state": "running",
      "az": "us-east-1a",
      "region": "us-east-1",
      "private_ip": "10.0.1.10",
      "public_ip": "54.123.45.67",
      "vpc_id": "vpc-0a1b2c3d4e5f6g7h8",
      "subnet_id": "subnet-0a1b2c3d",
      "enis": [
        {
          "id": "eni-0a1b2c3d4e5f",
          "subnet_id": "subnet-0a1b2c3d",
          "private_ip": "10.0.1.10",
          "public_ip": "54.123.45.67",
          "sg_ids": ["sg-0a1b2c3d4e5f", "sg-9z8y7x6w5v4u"]
        }
      ],
      "security_groups": [
        {
          "id": "sg-0a1b2c3d4e5f",
          "name": "production-web-sg",
          "description": "Web server security group",
          "rules": []
        },
        {
          "id": "sg-9z8y7x6w5v4u",
          "name": "production-ssh-sg",
          "description": "SSH access security group",
          "rules": []
        }
      ],
      "route_tables": [
        {
          "id": "rtb-0a1b2c3d4e5f",
          "routes": [
            {"prefix": "10.0.0.0/16", "target": "local", "state": "active"},
            {"prefix": "0.0.0.0/0", "target": "igw-01234567", "state": "active"}
          ]
        }
      ]
    },
    {
      "id": "i-9z8y7x6w5v4u3t2s1",
      "name": "test-instance",
      "type": "t2.micro",
      "state": "stopped",
      "az": "us-west-2a",
      "region": "us-west-2",
      "private_ip": "172.16.1.10",
      "public_ip": null,
      "vpc_id": "vpc-9z8y7x6w5v4u3t2s1",
      "subnet_id": "subnet-9z8y7x6w",
      "enis": [],
      "security_groups": [],
      "route_tables": []
    },
    {
      "id": "i-fedcba0987654321",
      "name": null,
      "type": "t3.small",
      "state": "running",
      "az": "us-east-1b",
      "region": "us-east-1",
      "private_ip": "10.0.2.20",
      "public_ip": null,
      "vpc_id": "vpc-0a1b2c3d4e5f6g7h8",
      "subnet_id": "subnet-9z8y7x6w",
      "enis": [
        {
          "id": "eni-fedcba098765",
          "subnet_id": "subnet-9z8y7x6w",
          "private_ip": "10.0.2.20",
          "public_ip": null,
          "sg_ids": ["sg-0a1b2c3d4e5f"]
        }
      ],
      "security_groups": [
        {
          "id": "sg-0a1b2c3d4e5f",
          "name": "production-web-sg",
          "description": "Web server security group",
          "rules": []
        }
      ],
      "route_tables": []
    }
  ]
}
```

**Test Scenarios**:
- Instance with complete networking (production-web-01)
- Instance with minimal data (test-instance)
- Instance without name (null handling)
- Instance-specific ENI filtering (ISSUE #9)
- Instance-specific security group filtering (ISSUE #9)
- Multi-ENI instances
- Stopped vs running instances

---

## 7. ELBs Fixture

**File**: `tests/fixtures/elbs.json`

```json
{
  "elbs": [
    {
      "arn": "arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/production-alb/50dc6c495c0c9188",
      "name": "production-alb",
      "type": "application",
      "scheme": "internet-facing",
      "vpc_id": "vpc-0a1b2c3d4e5f6g7h8",
      "state": "active",
      "region": "us-east-1",
      "dns_name": "production-alb-1234567890.us-east-1.elb.amazonaws.com",
      "availability_zones": ["us-east-1a", "us-east-1b"],
      "listeners": [
        {
          "listener_arn": "arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/production-alb/50dc6c495c0c9188/f2f7dc8efc522ab2",
          "port": 443,
          "protocol": "HTTPS",
          "default_actions": [
            {
              "type": "forward",
              "target_group_arn": "arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/production-tg/50dc6c495c0c9188"
            }
          ]
        },
        {
          "listener_arn": "arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/production-alb/50dc6c495c0c9188/a1b2c3d4e5f6",
          "port": 80,
          "protocol": "HTTP",
          "default_actions": [
            {
              "type": "redirect",
              "redirect_config": {
                "protocol": "HTTPS",
                "port": "443",
                "status_code": "HTTP_301"
              }
            }
          ]
        }
      ],
      "target_groups": [
        {
          "arn": "arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/production-tg/50dc6c495c0c9188",
          "name": "production-tg",
          "protocol": "HTTPS",
          "port": 443,
          "vpc_id": "vpc-0a1b2c3d4e5f6g7h8",
          "health_check": {
            "protocol": "HTTPS",
            "port": "443",
            "path": "/health",
            "interval": 30,
            "timeout": 5,
            "healthy_threshold": 2,
            "unhealthy_threshold": 2
          },
          "targets": [
            {
              "id": "i-0a1b2c3d4e5f6g7h8",
              "port": 443,
              "health": {
                "state": "healthy",
                "reason": "Target.ResponseCodeMismatch",
                "description": "Health checks successful"
              }
            },
            {
              "id": "i-fedcba0987654321",
              "port": 443,
              "health": {
                "state": "unhealthy",
                "reason": "Target.Timeout",
                "description": "Request timeout"
              }
            }
          ]
        }
      ]
    },
    {
      "arn": "arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/net/production-nlb/6789012345abcdef",
      "name": "production-nlb",
      "type": "network",
      "scheme": "internal",
      "vpc_id": "vpc-0a1b2c3d4e5f6g7h8",
      "state": "active",
      "region": "us-east-1",
      "dns_name": "production-nlb-6789012345abcdef.elb.us-east-1.amazonaws.com",
      "availability_zones": ["us-east-1a"],
      "listeners": [
        {
          "listener_arn": "arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/net/production-nlb/6789012345abcdef/abc123def456",
          "port": 443,
          "protocol": "TCP",
          "default_actions": [
            {
              "type": "forward",
              "target_group_arn": "arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/production-nlb-tg/6789012345abcdef"
            }
          ]
        }
      ],
      "target_groups": [
        {
          "arn": "arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/production-nlb-tg/6789012345abcdef",
          "name": "production-nlb-tg",
          "protocol": "TCP",
          "port": 443,
          "vpc_id": "vpc-0a1b2c3d4e5f6g7h8",
          "health_check": {
            "protocol": "TCP",
            "port": "traffic-port",
            "interval": 30,
            "timeout": 10,
            "healthy_threshold": 3,
            "unhealthy_threshold": 3
          },
          "targets": [
            {
              "id": "i-0a1b2c3d4e5f6g7h8",
              "port": 443,
              "health": {
                "state": "healthy",
                "reason": "",
                "description": "Target is healthy"
              }
            }
          ]
        }
      ]
    },
    {
      "arn": "arn:aws:elasticloadbalancing:us-east-1:545009866561:loadbalancer/app/Github-ALB/02d64eddbcd409ff",
      "name": "Github-ALB",
      "type": "application",
      "scheme": "internal",
      "vpc_id": "vpc-0a7f437f503cfacf8",
      "state": "active",
      "region": "us-east-1",
      "dns_name": "internal-Github-ALB-1424514326.us-east-1.elb.amazonaws.com",
      "availability_zones": ["us-east-1a", "us-east-1b", "us-east-1c"],
      "listeners": [],
      "target_groups": []
    }
  ]
}
```

**Test Scenarios**:
- ALB with listeners and targets (production-alb)
- NLB with TCP listeners (production-nlb)
- ELB without listeners/targets (Github-ALB) - ISSUE #10
- Listener enumeration
- Target group health status
- Mixed healthy/unhealthy targets

---

## 8. VPNs Fixture

**File**: `tests/fixtures/vpns.json`

```json
{
  "vpns": [
    {
      "id": "vpn-0a1b2c3d4e5f6g7h8",
      "name": "production-vpn",
      "state": "available",
      "type": "ipsec.1",
      "category": "VPN",
      "region": "us-east-1",
      "customer_gateway_id": "cgw-01234567",
      "vpn_gateway_id": "vgw-01234567",
      "transit_gateway_id": null,
      "tunnels": [
        {
          "outside_ip": "54.123.45.67",
          "status": "UP",
          "status_message": "Tunnel is up and passing traffic",
          "last_status_change": "2024-12-01T10:00:00Z"
        },
        {
          "outside_ip": "52.98.76.54",
          "status": "DOWN",
          "status_message": "Tunnel is down",
          "last_status_change": "2024-12-01T12:00:00Z"
        }
      ]
    },
    {
      "id": "vpn-9z8y7x6w5v4u3t2s1",
      "name": "test-vpn",
      "state": "available",
      "type": "ipsec.1",
      "category": "VPN",
      "region": "us-west-2",
      "customer_gateway_id": "cgw-98765432",
      "vpn_gateway_id": null,
      "transit_gateway_id": "tgw-9z8y7x6w5v4u3t2s1",
      "tunnels": [
        {
          "outside_ip": "34.98.76.54",
          "status": "UP",
          "status_message": "Tunnel is up",
          "last_status_change": "2024-12-02T08:00:00Z"
        },
        {
          "outside_ip": "35.87.65.43",
          "status": "UP",
          "status_message": "Tunnel is up",
          "last_status_change": "2024-12-02T08:00:00Z"
        }
      ]
    }
  ]
}
```

**Test Scenarios**:
- VPN with mixed tunnel status (UP/DOWN)
- VPN with all tunnels UP
- VGW-attached VPN
- TGW-attached VPN
- Tunnel status display

---

## 9. Routing Cache Fixture

**File**: `tests/fixtures/routing_cache.json`

```json
{
  "routing_cache": {
    "vpcs": {
      "vpc-0a1b2c3d4e5f6g7h8": [
        {"prefix": "10.0.0.0/16", "target": "local", "type": "vpc_local"},
        {"prefix": "0.0.0.0/0", "target": "igw-01234567", "type": "igw"},
        {"prefix": "192.168.0.0/16", "target": "tgw-0a1b2c3d4e5f6g7h8", "type": "tgw"}
      ]
    },
    "transit_gateways": {
      "tgw-0a1b2c3d4e5f6g7h8": [
        {"prefix": "10.0.0.0/8", "target": "tgw-attach-vpc-01", "type": "propagated"},
        {"prefix": "192.168.0.0/16", "target": "tgw-attach-vpc-02", "type": "static", "state": "blackhole"}
      ]
    },
    "core_networks": {
      "core-network-0a1b2c3d4e5f": [
        {"prefix": "10.0.0.0/8", "target": "attachment-vpc-01", "segment": "production"},
        {"prefix": "192.168.0.0/16", "target": "attachment-vpc-02", "segment": "staging", "state": "blackhole"}
      ]
    }
  }
}
```

**Test Scenarios**:
- Root context find_prefix searches routing cache
- Root context find_null_routes searches routing cache
- Cache population
- Cache clearing
- Empty cache handling

---

## 10. Fixture Loading Strategy

### 10.1 Fixture Loader Implementation

```python
# tests/fixtures/loader.py
import json
from pathlib import Path
from typing import Dict, Any

FIXTURES_DIR = Path(__file__).parent

def load_fixture(name: str) -> Dict[str, Any]:
    """Load a fixture file by name."""
    fixture_path = FIXTURES_DIR / f"{name}.json"
    with open(fixture_path, 'r') as f:
        return json.load(f)

def load_all_fixtures() -> Dict[str, Dict[str, Any]]:
    """Load all fixture files."""
    return {
        "global_networks": load_fixture("global_networks"),
        "core_networks": load_fixture("core_networks"),
        "vpcs": load_fixture("vpcs"),
        "transit_gateways": load_fixture("transit_gateways"),
        "firewalls": load_fixture("firewalls"),
        "ec2_instances": load_fixture("ec2_instances"),
        "elbs": load_fixture("elbs"),
        "vpns": load_fixture("vpns"),
        "routing_cache": load_fixture("routing_cache"),
    }
```

### 10.2 Pytest Fixtures

```python
# tests/conftest.py additions
import pytest
from tests.fixtures.loader import load_all_fixtures

@pytest.fixture
def all_fixtures():
    """Load all fixture data."""
    return load_all_fixtures()

@pytest.fixture
def global_networks(all_fixtures):
    """Global networks fixture."""
    return all_fixtures["global_networks"]["global_networks"]

@pytest.fixture
def core_networks(all_fixtures):
    """Core networks fixture."""
    return all_fixtures["core_networks"]["core_networks"]

@pytest.fixture
def vpcs(all_fixtures):
    """VPCs fixture."""
    return all_fixtures["vpcs"]["vpcs"]

@pytest.fixture
def transit_gateways(all_fixtures):
    """Transit gateways fixture."""
    return all_fixtures["transit_gateways"]["transit_gateways"]

@pytest.fixture
def firewalls(all_fixtures):
    """Firewalls fixture."""
    return all_fixtures["firewalls"]["firewalls"]

@pytest.fixture
def ec2_instances(all_fixtures):
    """EC2 instances fixture."""
    return all_fixtures["ec2_instances"]["ec2_instances"]

@pytest.fixture
def elbs(all_fixtures):
    """ELBs fixture."""
    return all_fixtures["elbs"]["elbs"]

@pytest.fixture
def vpns(all_fixtures):
    """VPNs fixture."""
    return all_fixtures["vpns"]["vpns"]

@pytest.fixture
def routing_cache(all_fixtures):
    """Routing cache fixture."""
    return all_fixtures["routing_cache"]["routing_cache"]

@pytest.fixture
def mock_shell_with_fixtures(all_fixtures):
    """Create shell instance with all fixtures pre-loaded."""
    from aws_network_tools.shell import AWSNetShell
    shell = AWSNetShell()

    # Pre-populate cache with fixture data
    shell._cache["global-networks"] = all_fixtures["global_networks"]["global_networks"]
    shell._cache["vpcs"] = all_fixtures["vpcs"]["vpcs"]
    shell._cache["tgw"] = all_fixtures["transit_gateways"]["transit_gateways"]
    shell._cache["firewalls"] = all_fixtures["firewalls"]["firewalls"]
    shell._cache["ec2-instances"] = all_fixtures["ec2_instances"]["ec2_instances"]
    shell._cache["elbs"] = all_fixtures["elbs"]["elbs"]
    shell._cache["vpns"] = all_fixtures["vpns"]["vpns"]
    shell._cache["routing_cache"] = all_fixtures["routing_cache"]["routing_cache"]

    return shell
```

---

## 11. Fixture Validation Requirements

Each fixture must pass validation checks:

### 11.1 Required Fields Validation
```python
REQUIRED_FIELDS = {
    "global_network": ["id", "name", "state", "core_networks"],
    "core_network": ["id", "name", "policy", "segments", "route_tables"],
    "vpc": ["id", "region", "cidr", "state", "route_tables", "subnets"],
    "transit_gateway": ["id", "name", "region", "state", "route_tables", "attachments"],
    "firewall": ["id", "name", "region", "arn", "vpc_id"],
    "ec2_instance": ["id", "type", "state", "az", "region", "vpc_id"],
    "elb": ["arn", "name", "type", "scheme", "vpc_id", "state", "region"],
    "vpn": ["id", "state", "type", "category", "region", "tunnels"],
}
```

### 11.2 Relationship Validation
- Core networks must reference valid global network IDs
- Route tables must reference valid parent resources
- EC2 instances must reference valid VPCs and subnets
- ELB target groups must reference valid VPCs
- Attachments must reference valid resources

### 11.3 Edge Case Coverage
Each fixture type must include:
1. Valid complete data example
2. Minimal data example (empty lists, null optional fields)
3. Invalid state examples (for error testing)
4. Large data set example (for performance testing)

---

## 12. Test Data Generation Script

```python
# tests/fixtures/generate.py
"""Generate realistic test fixture data."""

def generate_vpc_fixture(count: int = 3) -> dict:
    """Generate VPC fixture data."""
    # Implementation to create varied VPC data
    pass

def generate_elb_fixture(count: int = 3) -> dict:
    """Generate ELB fixture data with listeners and targets."""
    # Ensures ISSUE #10 can be properly tested
    pass

def validate_fixture_relationships(fixtures: dict) -> List[str]:
    """Validate that fixture relationships are consistent."""
    errors = []
    # Check VPC IDs referenced by instances exist
    # Check subnet IDs referenced by ENIs exist
    # etc.
    return errors

def generate_all_fixtures():
    """Generate all fixture files."""
    fixtures = {
        "global_networks": generate_global_network_fixture(),
        "vpcs": generate_vpc_fixture(),
        "elbs": generate_elb_fixture(),
        # ... etc
    }

    # Validate relationships
    errors = validate_fixture_relationships(fixtures)
    if errors:
        raise ValueError(f"Fixture validation failed: {errors}")

    # Write to files
    for name, data in fixtures.items():
        with open(f"tests/fixtures/{name}.json", "w") as f:
            json.dump(data, f, indent=2)
```

---

## Summary

This document defines the complete fixture requirements for testing all 150+ commands in AWS Network Shell. Key requirements:

1. **9 fixture files** covering all resource types
2. **Realistic AWS data** with proper ID formats and relationships
3. **Edge case coverage** including empty data, null values, and error conditions
4. **Issue reproduction data** specifically for Issues #9 and #10
5. **Validation framework** to ensure fixture consistency

Next steps:
1. Create fixture JSON files based on these specifications
2. Implement fixture loader and pytest fixtures
3. Validate fixture relationships
4. Begin test implementation using fixtures
