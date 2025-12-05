"""Realistic AWS Network Firewall mock data fixtures.

Network security architecture:
- Production Network Firewall for egress filtering
- Inspection VPC with firewall endpoints
- Stateless and stateful rule groups
- Domain filtering and IPS rules
- Comprehensive logging configuration

Includes:
- Network Firewalls with endpoints
- Firewall Policies
- Stateless Rule Groups
- Stateful Rule Groups (5-tuple, domain list, Suricata)
- Logging configurations
"""

from typing import Any

# =============================================================================
# NETWORK FIREWALL FIXTURES
# =============================================================================

NETWORK_FIREWALL_FIXTURES: dict[str, dict[str, Any]] = {
    # Production Network Firewall - eu-west-1
    "production-firewall": {
        "FirewallName": "production-firewall",
        "FirewallArn": "arn:aws:network-firewall:eu-west-1:123456789012:firewall/production-firewall",
        "FirewallPolicyArn": "arn:aws:network-firewall:eu-west-1:123456789012:firewall-policy/production-policy",
        "VpcId": "vpc-0firewall1234567",
        "SubnetMappings": [
            {
                "SubnetId": "subnet-0fwtgw1a123456",
                "IPAddressType": "IPV4",
            },
            {
                "SubnetId": "subnet-0fwtgw1b123456",
                "IPAddressType": "IPV4",
            },
        ],
        "DeleteProtection": True,
        "SubnetChangeProtection": True,
        "FirewallPolicyChangeProtection": True,
        "Description": "Production egress and inspection firewall",
        "FirewallId": "fw-0prod12345678901",
        "Tags": [
            {"Key": "Name", "Value": "production-firewall"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "Purpose", "Value": "inspection"},
        ],
        "EncryptionConfiguration": {
            "KeyId": "arn:aws:kms:eu-west-1:123456789012:key/prod-key-123",
            "Type": "CUSTOMER_KMS",
        },
        "FirewallStatus": {
            "Status": "READY",
            "ConfigurationSyncStateSummary": "IN_SYNC",
            "SyncStates": {
                "eu-west-1a": {
                    "Attachment": {
                        "SubnetId": "subnet-0fwtgw1a123456",
                        "EndpointId": "vpce-0fw1a12345678901",
                        "Status": "READY",
                    },
                    "Config": {
                        "sync-status": "IN_SYNC",
                    },
                },
                "eu-west-1b": {
                    "Attachment": {
                        "SubnetId": "subnet-0fwtgw1b123456",
                        "EndpointId": "vpce-0fw1b12345678901",
                        "Status": "READY",
                    },
                    "Config": {
                        "sync-status": "IN_SYNC",
                    },
                },
            },
        },
    },
    # Staging Network Firewall - us-east-1
    "staging-firewall": {
        "FirewallName": "staging-firewall",
        "FirewallArn": "arn:aws:network-firewall:us-east-1:123456789012:firewall/staging-firewall",
        "FirewallPolicyArn": "arn:aws:network-firewall:us-east-1:123456789012:firewall-policy/staging-policy",
        "VpcId": "vpc-0stag1234567890ab",
        "SubnetMappings": [
            {
                "SubnetId": "subnet-0stgfw1a123456",
                "IPAddressType": "IPV4",
            },
        ],
        "DeleteProtection": False,
        "SubnetChangeProtection": False,
        "FirewallPolicyChangeProtection": False,
        "Description": "Staging firewall for testing",
        "FirewallId": "fw-0stag12345678901",
        "Tags": [
            {"Key": "Name", "Value": "staging-firewall"},
            {"Key": "Environment", "Value": "staging"},
        ],
        "EncryptionConfiguration": {
            "Type": "AWS_OWNED_KMS_KEY",
        },
        "FirewallStatus": {
            "Status": "READY",
            "ConfigurationSyncStateSummary": "IN_SYNC",
            "SyncStates": {
                "us-east-1a": {
                    "Attachment": {
                        "SubnetId": "subnet-0stgfw1a123456",
                        "EndpointId": "vpce-0stagfw1a1234567",
                        "Status": "READY",
                    },
                    "Config": {
                        "sync-status": "IN_SYNC",
                    },
                },
            },
        },
    },
}

# =============================================================================
# FIREWALL POLICY FIXTURES
# =============================================================================

FIREWALL_POLICY_FIXTURES: dict[str, dict[str, Any]] = {
    # Production Firewall Policy
    "arn:aws:network-firewall:eu-west-1:123456789012:firewall-policy/production-policy": {
        "FirewallPolicyName": "production-policy",
        "FirewallPolicyArn": "arn:aws:network-firewall:eu-west-1:123456789012:firewall-policy/production-policy",
        "FirewallPolicyId": "fp-0prod12345678901",
        "Description": "Production firewall policy with IPS and domain filtering",
        "FirewallPolicy": {
            "StatelessDefaultActions": ["aws:forward_to_sfe"],
            "StatelessFragmentDefaultActions": ["aws:forward_to_sfe"],
            "StatelessRuleGroupReferences": [
                {
                    "ResourceArn": "arn:aws:network-firewall:eu-west-1:123456789012:stateless-rulegroup/prod-stateless-rg",
                    "Priority": 10,
                }
            ],
            "StatefulRuleGroupReferences": [
                {
                    "ResourceArn": "arn:aws:network-firewall:eu-west-1:123456789012:stateful-rulegroup/prod-domain-filter",
                    "Priority": 100,
                },
                {
                    "ResourceArn": "arn:aws:network-firewall:eu-west-1:123456789012:stateful-rulegroup/prod-threat-detection",
                    "Priority": 200,
                },
                {
                    "ResourceArn": "arn:aws:network-firewall:eu-west-1:aws-managed:stateful-rulegroup/AbusedLegitMalwareDomainsActionOrder",
                    "Priority": 300,
                },
            ],
            "StatefulDefaultActions": ["aws:drop_strict"],
            "StatefulEngineOptions": {
                "RuleOrder": "STRICT_ORDER",
                "StreamExceptionPolicy": "DROP",
            },
            "TLSInspectionConfigurationArn": None,
        },
        "Tags": [
            {"Key": "Name", "Value": "production-firewall-policy"},
            {"Key": "Environment", "Value": "production"},
        ],
    },
    # Staging Firewall Policy
    "arn:aws:network-firewall:us-east-1:123456789012:firewall-policy/staging-policy": {
        "FirewallPolicyName": "staging-policy",
        "FirewallPolicyArn": "arn:aws:network-firewall:us-east-1:123456789012:firewall-policy/staging-policy",
        "FirewallPolicyId": "fp-0stag12345678901",
        "Description": "Staging firewall policy - permissive for testing",
        "FirewallPolicy": {
            "StatelessDefaultActions": ["aws:forward_to_sfe"],
            "StatelessFragmentDefaultActions": ["aws:forward_to_sfe"],
            "StatelessRuleGroupReferences": [],
            "StatefulRuleGroupReferences": [
                {
                    "ResourceArn": "arn:aws:network-firewall:us-east-1:123456789012:stateful-rulegroup/staging-allow-all",
                    "Priority": 100,
                }
            ],
            "StatefulDefaultActions": ["aws:alert_strict", "aws:pass"],
            "StatefulEngineOptions": {
                "RuleOrder": "DEFAULT_ACTION_ORDER",
            },
        },
        "Tags": [
            {"Key": "Name", "Value": "staging-firewall-policy"},
            {"Key": "Environment", "Value": "staging"},
        ],
    },
}

# =============================================================================
# RULE GROUP FIXTURES
# =============================================================================

RULE_GROUP_FIXTURES: dict[str, dict[str, Any]] = {
    # Stateless Rule Group - Quick filtering
    "arn:aws:network-firewall:eu-west-1:123456789012:stateless-rulegroup/prod-stateless-rg": {
        "RuleGroupName": "prod-stateless-rg",
        "RuleGroupArn": "arn:aws:network-firewall:eu-west-1:123456789012:stateless-rulegroup/prod-stateless-rg",
        "RuleGroupId": "rg-0stateless1234567",
        "Type": "STATELESS",
        "Capacity": 50,
        "RuleGroupStatus": "ACTIVE",
        "Description": "Stateless rules for fast path filtering",
        "RuleGroup": {
            "RulesSource": {
                "StatelessRulesAndCustomActions": {
                    "StatelessRules": [
                        {
                            "RuleDefinition": {
                                "MatchAttributes": {
                                    "Sources": [{"AddressDefinition": "10.0.0.0/16"}],
                                    "Destinations": [{"AddressDefinition": "0.0.0.0/0"}],
                                    "SourcePorts": [{"FromPort": 0, "ToPort": 65535}],
                                    "DestinationPorts": [{"FromPort": 443, "ToPort": 443}],
                                    "Protocols": [6],
                                },
                                "Actions": ["aws:pass"],
                            },
                            "Priority": 10,
                        },
                        {
                            "RuleDefinition": {
                                "MatchAttributes": {
                                    "Sources": [{"AddressDefinition": "10.0.0.0/16"}],
                                    "Destinations": [{"AddressDefinition": "0.0.0.0/0"}],
                                    "SourcePorts": [{"FromPort": 0, "ToPort": 65535}],
                                    "DestinationPorts": [{"FromPort": 80, "ToPort": 80}],
                                    "Protocols": [6],
                                },
                                "Actions": ["aws:pass"],
                            },
                            "Priority": 20,
                        },
                    ],
                    "CustomActions": [],
                }
            },
            "RuleVariables": {
                "IPSets": {
                    "INTERNAL_NET": {"Definition": ["10.0.0.0/8", "172.16.0.0/12"]},
                    "EXTERNAL_NET": {"Definition": ["0.0.0.0/0"]},
                }
            },
        },
        "Tags": [
            {"Key": "Name", "Value": "prod-stateless-rg"},
            {"Key": "Type", "Value": "stateless"},
        ],
    },
    # Stateful Rule Group - Domain Filtering
    "arn:aws:network-firewall:eu-west-1:123456789012:stateful-rulegroup/prod-domain-filter": {
        "RuleGroupName": "prod-domain-filter",
        "RuleGroupArn": "arn:aws:network-firewall:eu-west-1:123456789012:stateful-rulegroup/prod-domain-filter",
        "RuleGroupId": "rg-0domain123456789",
        "Type": "STATEFUL",
        "Capacity": 100,
        "RuleGroupStatus": "ACTIVE",
        "Description": "Domain allowlist for egress traffic",
        "RuleGroup": {
            "RulesSource": {
                "RulesSourceList": {
                    "TargetTypes": ["TLS_SNI", "HTTP_HOST"],
                    "Targets": [
                        ".amazonaws.com",
                        ".github.com",
                        ".npmjs.org",
                        ".pypi.org",
                        ".docker.io",
                        ".ubuntu.com",
                        ".debian.org",
                    ],
                    "GeneratedRulesType": "ALLOWLIST",
                }
            },
            "StatefulRuleOptions": {
                "RuleOrder": "STRICT_ORDER",
            },
        },
        "Tags": [
            {"Key": "Name", "Value": "prod-domain-filter"},
            {"Key": "Type", "Value": "domain-filtering"},
        ],
    },
    # Stateful Rule Group - Threat Detection (Suricata)
    "arn:aws:network-firewall:eu-west-1:123456789012:stateful-rulegroup/prod-threat-detection": {
        "RuleGroupName": "prod-threat-detection",
        "RuleGroupArn": "arn:aws:network-firewall:eu-west-1:123456789012:stateful-rulegroup/prod-threat-detection",
        "RuleGroupId": "rg-0threat123456789",
        "Type": "STATEFUL",
        "Capacity": 500,
        "RuleGroupStatus": "ACTIVE",
        "Description": "IPS rules for threat detection",
        "RuleGroup": {
            "RulesSource": {
                "RulesString": """# Block known malware C2 servers
drop ip any any -> [198.51.100.0/24] any (msg:"Block known C2 server"; sid:1000001; rev:1;)

# Detect SQL injection attempts
alert tcp any any -> any [80,443,8080] (msg:"Possible SQL injection detected"; content:"union select"; nocase; sid:1000002; rev:1;)

# Detect command injection
alert tcp any any -> any [80,443] (msg:"Possible command injection"; pcre:"/(%0[ad]|\\n|\\r)/i"; sid:1000003; rev:1;)

# Block crypto mining domains
drop tls any any -> any any (tls.sni; content:"coinhive"; nocase; msg:"Block crypto mining"; sid:1000004; rev:1;)

# Detect data exfiltration
alert tcp $INTERNAL_NET any -> $EXTERNAL_NET any (msg:"Large outbound data transfer"; threshold:type both, track by_src, count 100, seconds 60; sid:1000005; rev:1;)
"""
            },
            "StatefulRuleOptions": {
                "RuleOrder": "STRICT_ORDER",
            },
            "RuleVariables": {
                "IPSets": {
                    "INTERNAL_NET": {"Definition": ["10.0.0.0/8"]},
                    "EXTERNAL_NET": {"Definition": ["0.0.0.0/0"]},
                }
            },
        },
        "Tags": [
            {"Key": "Name", "Value": "prod-threat-detection"},
            {"Key": "Type", "Value": "ips"},
        ],
    },
    # Stateful Rule Group - 5-tuple rules
    "arn:aws:network-firewall:eu-west-1:123456789012:stateful-rulegroup/prod-5tuple-rules": {
        "RuleGroupName": "prod-5tuple-rules",
        "RuleGroupArn": "arn:aws:network-firewall:eu-west-1:123456789012:stateful-rulegroup/prod-5tuple-rules",
        "RuleGroupId": "rg-05tuple123456789",
        "Type": "STATEFUL",
        "Capacity": 50,
        "RuleGroupStatus": "ACTIVE",
        "Description": "5-tuple stateful rules for specific protocols",
        "RuleGroup": {
            "RulesSource": {
                "StatefulRules": [
                    {
                        "Action": "PASS",
                        "Header": {
                            "Protocol": "TCP",
                            "Source": "10.0.0.0/16",
                            "SourcePort": "ANY",
                            "Direction": "FORWARD",
                            "Destination": "0.0.0.0/0",
                            "DestinationPort": "443",
                        },
                        "RuleOptions": [
                            {"Keyword": "sid:2000001"},
                            {"Keyword": "msg:Allow HTTPS egress"},
                        ],
                    },
                    {
                        "Action": "PASS",
                        "Header": {
                            "Protocol": "TCP",
                            "Source": "10.0.0.0/16",
                            "SourcePort": "ANY",
                            "Direction": "FORWARD",
                            "Destination": "0.0.0.0/0",
                            "DestinationPort": "80",
                        },
                        "RuleOptions": [
                            {"Keyword": "sid:2000002"},
                            {"Keyword": "msg:Allow HTTP egress"},
                        ],
                    },
                    {
                        "Action": "DROP",
                        "Header": {
                            "Protocol": "TCP",
                            "Source": "10.0.0.0/16",
                            "SourcePort": "ANY",
                            "Direction": "FORWARD",
                            "Destination": "0.0.0.0/0",
                            "DestinationPort": "23",
                        },
                        "RuleOptions": [
                            {"Keyword": "sid:2000003"},
                            {"Keyword": "msg:Block Telnet"},
                        ],
                    },
                    {
                        "Action": "ALERT",
                        "Header": {
                            "Protocol": "TCP",
                            "Source": "10.0.0.0/16",
                            "SourcePort": "ANY",
                            "Direction": "FORWARD",
                            "Destination": "0.0.0.0/0",
                            "DestinationPort": "3389",
                        },
                        "RuleOptions": [
                            {"Keyword": "sid:2000004"},
                            {"Keyword": "msg:Alert on RDP egress"},
                        ],
                    },
                ]
            },
            "StatefulRuleOptions": {
                "RuleOrder": "STRICT_ORDER",
            },
        },
        "Tags": [
            {"Key": "Name", "Value": "prod-5tuple-rules"},
            {"Key": "Type", "Value": "5-tuple"},
        ],
    },
    # Staging Allow-All Rule Group
    "arn:aws:network-firewall:us-east-1:123456789012:stateful-rulegroup/staging-allow-all": {
        "RuleGroupName": "staging-allow-all",
        "RuleGroupArn": "arn:aws:network-firewall:us-east-1:123456789012:stateful-rulegroup/staging-allow-all",
        "RuleGroupId": "rg-0stagallow123456",
        "Type": "STATEFUL",
        "Capacity": 10,
        "RuleGroupStatus": "ACTIVE",
        "Description": "Permissive rule group for staging",
        "RuleGroup": {
            "RulesSource": {
                "StatefulRules": [
                    {
                        "Action": "PASS",
                        "Header": {
                            "Protocol": "IP",
                            "Source": "ANY",
                            "SourcePort": "ANY",
                            "Direction": "FORWARD",
                            "Destination": "ANY",
                            "DestinationPort": "ANY",
                        },
                        "RuleOptions": [
                            {"Keyword": "sid:3000001"},
                            {"Keyword": "msg:Allow all traffic"},
                        ],
                    },
                ]
            },
            "StatefulRuleOptions": {
                "RuleOrder": "DEFAULT_ACTION_ORDER",
            },
        },
        "Tags": [
            {"Key": "Name", "Value": "staging-allow-all"},
            {"Key": "Type", "Value": "permissive"},
        ],
    },
}

# =============================================================================
# LOGGING CONFIGURATION FIXTURES
# =============================================================================

FIREWALL_LOGGING_CONFIG: dict[str, dict[str, Any]] = {
    # Production Firewall Logging
    "production-firewall": {
        "FirewallArn": "arn:aws:network-firewall:eu-west-1:123456789012:firewall/production-firewall",
        "LoggingConfiguration": {
            "LogDestinationConfigs": [
                {
                    "LogType": "ALERT",
                    "LogDestinationType": "CloudWatchLogs",
                    "LogDestination": {
                        "logGroup": "/aws/networkfirewall/production/alert",
                    },
                },
                {
                    "LogType": "FLOW",
                    "LogDestinationType": "CloudWatchLogs",
                    "LogDestination": {
                        "logGroup": "/aws/networkfirewall/production/flow",
                    },
                },
                {
                    "LogType": "FLOW",
                    "LogDestinationType": "S3",
                    "LogDestination": {
                        "bucketName": "production-firewall-logs",
                        "prefix": "flow-logs/",
                    },
                },
            ]
        },
    },
    # Staging Firewall Logging
    "staging-firewall": {
        "FirewallArn": "arn:aws:network-firewall:us-east-1:123456789012:firewall/staging-firewall",
        "LoggingConfiguration": {
            "LogDestinationConfigs": [
                {
                    "LogType": "ALERT",
                    "LogDestinationType": "CloudWatchLogs",
                    "LogDestination": {
                        "logGroup": "/aws/networkfirewall/staging/alert",
                    },
                },
            ]
        },
    },
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_firewall_by_name(firewall_name: str) -> dict[str, Any] | None:
    """Get Network Firewall fixture by name."""
    return NETWORK_FIREWALL_FIXTURES.get(firewall_name)


def get_firewall_detail(firewall_name: str) -> dict[str, Any] | None:
    """Get comprehensive firewall detail with policy and rule groups."""
    firewall = NETWORK_FIREWALL_FIXTURES.get(firewall_name)
    if not firewall:
        return None

    # Get associated policy
    policy_arn = firewall.get("FirewallPolicyArn")
    policy = FIREWALL_POLICY_FIXTURES.get(policy_arn) if policy_arn else None

    # Get rule groups if policy exists
    rule_groups = []
    if policy:
        stateless_refs = policy.get("FirewallPolicy", {}).get(
            "StatelessRuleGroupReferences", []
        )
        stateful_refs = policy.get("FirewallPolicy", {}).get(
            "StatefulRuleGroupReferences", []
        )

        for ref in stateless_refs + stateful_refs:
            rg_arn = ref.get("ResourceArn")
            if rg_arn and rg_arn in RULE_GROUP_FIXTURES:
                rule_groups.append(RULE_GROUP_FIXTURES[rg_arn])

    # Get logging configuration
    logging_config = FIREWALL_LOGGING_CONFIG.get(firewall_name)

    return {
        "firewall": firewall,
        "policy": policy,
        "rule_groups": rule_groups,
        "logging_config": logging_config,
    }


def get_policy_by_arn(policy_arn: str) -> dict[str, Any] | None:
    """Get firewall policy by ARN."""
    return FIREWALL_POLICY_FIXTURES.get(policy_arn)


def get_rule_group_by_arn(rule_group_arn: str) -> dict[str, Any] | None:
    """Get rule group by ARN."""
    return RULE_GROUP_FIXTURES.get(rule_group_arn)


def get_firewalls_by_vpc(vpc_id: str) -> list[dict[str, Any]]:
    """Get all firewalls in a VPC."""
    return [
        fw for fw in NETWORK_FIREWALL_FIXTURES.values() if fw["VpcId"] == vpc_id
    ]
