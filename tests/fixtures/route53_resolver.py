"""Realistic Route53 Resolver mock data fixtures.

Route53 Resolver Architecture:
- Inbound Resolver Endpoints (on-premises DNS queries to AWS)
- Outbound Resolver Endpoints (AWS to on-premises DNS)
- Resolver Rules (forward rules, system rules)
- Query Logging Configurations (CloudWatch Logs, S3)

Use Cases:
- Hybrid DNS resolution between AWS and on-premises
- Cross-VPC DNS resolution
- Centralized DNS management in shared services VPC
- DNS query logging and auditing

Each resolver includes:
- Endpoint configuration (inbound/outbound direction)
- IP addresses across multiple AZs
- Security groups
- Rule associations with VPCs
- Query logging destinations
"""

from typing import Any

# =============================================================================
# ROUTE53 RESOLVER ENDPOINT FIXTURES
# =============================================================================

RESOLVER_ENDPOINT_FIXTURES: dict[str, dict[str, Any]] = {
    # Inbound Resolver Endpoint - Shared Services VPC (for on-premises queries to AWS)
    "rslvr-in-0shared12345": {
        "Id": "rslvr-in-0shared12345",
        "CreatorRequestId": "terraform-20240120-001",
        "Arn": "arn:aws:route53resolver:eu-west-1:123456789012:resolver-endpoint/rslvr-in-0shared12345",
        "Name": "shared-services-inbound-resolver",
        "SecurityGroupIds": [
            "sg-0resolver123456789",
        ],
        "Direction": "INBOUND",
        "IpAddressCount": 2,
        "HostVPCId": "vpc-0shared123456789a",
        "Status": "OPERATIONAL",
        "StatusMessage": "This Resolver Endpoint is operational.",
        "CreationTime": "2024-01-20T10:00:00Z",
        "ModificationTime": "2024-01-20T10:05:00Z",
    },
    # Outbound Resolver Endpoint - Shared Services VPC (for AWS queries to on-premises)
    "rslvr-out-0shared1234": {
        "Id": "rslvr-out-0shared1234",
        "CreatorRequestId": "terraform-20240120-002",
        "Arn": "arn:aws:route53resolver:eu-west-1:123456789012:resolver-endpoint/rslvr-out-0shared1234",
        "Name": "shared-services-outbound-resolver",
        "SecurityGroupIds": [
            "sg-0resolver123456789",
        ],
        "Direction": "OUTBOUND",
        "IpAddressCount": 2,
        "HostVPCId": "vpc-0shared123456789a",
        "Status": "OPERATIONAL",
        "StatusMessage": "This Resolver Endpoint is operational.",
        "CreationTime": "2024-01-20T10:10:00Z",
        "ModificationTime": "2024-01-20T10:15:00Z",
    },
    # Inbound Resolver Endpoint - Production VPC (for centralized DNS)
    "rslvr-in-0prod1234567": {
        "Id": "rslvr-in-0prod1234567",
        "CreatorRequestId": "terraform-20240120-003",
        "Arn": "arn:aws:route53resolver:eu-west-1:123456789012:resolver-endpoint/rslvr-in-0prod1234567",
        "Name": "production-inbound-resolver",
        "SecurityGroupIds": [
            "sg-0resolver123456789",
        ],
        "Direction": "INBOUND",
        "IpAddressCount": 3,
        "HostVPCId": "vpc-0prod1234567890ab",
        "Status": "OPERATIONAL",
        "StatusMessage": "This Resolver Endpoint is operational.",
        "CreationTime": "2024-01-20T11:00:00Z",
        "ModificationTime": "2024-01-20T11:05:00Z",
    },
    # Outbound Resolver Endpoint - Creating status
    "rslvr-out-0stag12345": {
        "Id": "rslvr-out-0stag12345",
        "CreatorRequestId": "terraform-20240322-001",
        "Arn": "arn:aws:route53resolver:us-east-1:123456789012:resolver-endpoint/rslvr-out-0stag12345",
        "Name": "staging-outbound-resolver",
        "SecurityGroupIds": [
            "sg-0stagresolver12345",
        ],
        "Direction": "OUTBOUND",
        "IpAddressCount": 2,
        "HostVPCId": "vpc-0stag1234567890ab",
        "Status": "CREATING",
        "StatusMessage": "This Resolver Endpoint is being created.",
        "CreationTime": "2024-03-22T14:00:00Z",
        "ModificationTime": "2024-03-22T14:00:00Z",
    },
}


# =============================================================================
# RESOLVER ENDPOINT IP ADDRESS FIXTURES
# =============================================================================

RESOLVER_IP_ADDRESS_FIXTURES: dict[str, list[dict[str, Any]]] = {
    # Inbound Resolver - Shared Services (2 AZs)
    "rslvr-in-0shared12345": [
        {
            "IpId": "rni-0sharedin1a12345",
            "SubnetId": "subnet-0shared1a1234567",
            "Ip": "10.100.10.10",
            "Status": "ATTACHED",
            "StatusMessage": "This IP address is operational.",
            "CreationTime": "2024-01-20T10:02:00Z",
            "ModificationTime": "2024-01-20T10:05:00Z",
        },
        {
            "IpId": "rni-0sharedin1b12345",
            "SubnetId": "subnet-0shared1b1234567",
            "Ip": "10.100.11.10",
            "Status": "ATTACHED",
            "StatusMessage": "This IP address is operational.",
            "CreationTime": "2024-01-20T10:03:00Z",
            "ModificationTime": "2024-01-20T10:05:00Z",
        },
    ],
    # Outbound Resolver - Shared Services (2 AZs)
    "rslvr-out-0shared1234": [
        {
            "IpId": "rni-0sharedout1a1234",
            "SubnetId": "subnet-0shared1a1234567",
            "Ip": "10.100.10.20",
            "Status": "ATTACHED",
            "StatusMessage": "This IP address is operational.",
            "CreationTime": "2024-01-20T10:12:00Z",
            "ModificationTime": "2024-01-20T10:15:00Z",
        },
        {
            "IpId": "rni-0sharedout1b1234",
            "SubnetId": "subnet-0shared1b1234567",
            "Ip": "10.100.11.20",
            "Status": "ATTACHED",
            "StatusMessage": "This IP address is operational.",
            "CreationTime": "2024-01-20T10:13:00Z",
            "ModificationTime": "2024-01-20T10:15:00Z",
        },
    ],
    # Inbound Resolver - Production (3 AZs for HA)
    "rslvr-in-0prod1234567": [
        {
            "IpId": "rni-0prodin1a123456",
            "SubnetId": "subnet-0priv1a123456789",
            "Ip": "10.0.10.53",
            "Status": "ATTACHED",
            "StatusMessage": "This IP address is operational.",
            "CreationTime": "2024-01-20T11:02:00Z",
            "ModificationTime": "2024-01-20T11:05:00Z",
        },
        {
            "IpId": "rni-0prodin1b123456",
            "SubnetId": "subnet-0priv1b123456789",
            "Ip": "10.0.11.53",
            "Status": "ATTACHED",
            "StatusMessage": "This IP address is operational.",
            "CreationTime": "2024-01-20T11:03:00Z",
            "ModificationTime": "2024-01-20T11:05:00Z",
        },
        {
            "IpId": "rni-0prodin1c123456",
            "SubnetId": "subnet-0priv1c123456789",
            "Ip": "10.0.12.53",
            "Status": "ATTACHED",
            "StatusMessage": "This IP address is operational.",
            "CreationTime": "2024-01-20T11:04:00Z",
            "ModificationTime": "2024-01-20T11:05:00Z",
        },
    ],
    # Outbound Resolver - Staging (creating)
    "rslvr-out-0stag12345": [
        {
            "IpId": "rni-0stagout1a12345",
            "SubnetId": "subnet-0stgpriv1a1234567",
            "Ip": "10.1.10.53",
            "Status": "CREATING",
            "StatusMessage": "This IP address is being created.",
            "CreationTime": "2024-03-22T14:01:00Z",
            "ModificationTime": "2024-03-22T14:01:00Z",
        },
        {
            "IpId": "rni-0stagout1b12345",
            "SubnetId": "subnet-0stgpriv1b1234567",
            "Ip": "10.1.11.53",
            "Status": "CREATING",
            "StatusMessage": "This IP address is being created.",
            "CreationTime": "2024-03-22T14:02:00Z",
            "ModificationTime": "2024-03-22T14:02:00Z",
        },
    ],
}


# =============================================================================
# RESOLVER RULE FIXTURES
# =============================================================================

RESOLVER_RULE_FIXTURES: dict[str, dict[str, Any]] = {
    # Forward Rule - On-premises corporate domain
    "rslvr-rr-0corp12345678": {
        "Id": "rslvr-rr-0corp12345678",
        "CreatorRequestId": "terraform-20240120-004",
        "Arn": "arn:aws:route53resolver:eu-west-1:123456789012:resolver-rule/rslvr-rr-0corp12345678",
        "DomainName": "corp.example.com",
        "Status": "COMPLETE",
        "StatusMessage": "This Resolver Rule is complete.",
        "RuleType": "FORWARD",
        "Name": "corporate-domain-forward",
        "TargetIps": [
            {
                "Ip": "192.168.1.53",
                "Port": 53,
            },
            {
                "Ip": "192.168.2.53",
                "Port": 53,
            },
        ],
        "ResolverEndpointId": "rslvr-out-0shared1234",
        "OwnerId": "123456789012",
        "ShareStatus": "NOT_SHARED",
        "CreationTime": "2024-01-20T10:20:00Z",
        "ModificationTime": "2024-01-20T10:25:00Z",
    },
    # Forward Rule - On-premises datacenter domain
    "rslvr-rr-0dc123456789": {
        "Id": "rslvr-rr-0dc123456789",
        "CreatorRequestId": "terraform-20240120-005",
        "Arn": "arn:aws:route53resolver:eu-west-1:123456789012:resolver-rule/rslvr-rr-0dc123456789",
        "DomainName": "dc.internal",
        "Status": "COMPLETE",
        "StatusMessage": "This Resolver Rule is complete.",
        "RuleType": "FORWARD",
        "Name": "datacenter-domain-forward",
        "TargetIps": [
            {
                "Ip": "10.255.1.53",
                "Port": 53,
            },
            {
                "Ip": "10.255.2.53",
                "Port": 53,
            },
        ],
        "ResolverEndpointId": "rslvr-out-0shared1234",
        "OwnerId": "123456789012",
        "ShareStatus": "NOT_SHARED",
        "CreationTime": "2024-01-20T10:30:00Z",
        "ModificationTime": "2024-01-20T10:35:00Z",
    },
    # System Rule - Default VPC DNS
    "rslvr-rr-0system12345": {
        "Id": "rslvr-rr-0system12345",
        "CreatorRequestId": "system-generated",
        "Arn": "arn:aws:route53resolver:eu-west-1:123456789012:resolver-rule/rslvr-rr-0system12345",
        "DomainName": ".",
        "Status": "COMPLETE",
        "StatusMessage": "This Resolver Rule is complete.",
        "RuleType": "SYSTEM",
        "Name": "default-internet-resolver",
        "OwnerId": "123456789012",
        "ShareStatus": "NOT_SHARED",
        "CreationTime": "2024-01-20T08:00:00Z",
        "ModificationTime": "2024-01-20T08:00:00Z",
    },
    # Forward Rule - Partner domain (cross-account)
    "rslvr-rr-0partner1234": {
        "Id": "rslvr-rr-0partner1234",
        "CreatorRequestId": "terraform-20240210-001",
        "Arn": "arn:aws:route53resolver:eu-west-1:123456789012:resolver-rule/rslvr-rr-0partner1234",
        "DomainName": "partner.example.net",
        "Status": "COMPLETE",
        "StatusMessage": "This Resolver Rule is complete.",
        "RuleType": "FORWARD",
        "Name": "partner-domain-forward",
        "TargetIps": [
            {
                "Ip": "172.16.100.53",
                "Port": 53,
            },
        ],
        "ResolverEndpointId": "rslvr-out-0shared1234",
        "OwnerId": "123456789012",
        "ShareStatus": "SHARED_WITH_ME",
        "CreationTime": "2024-02-10T12:00:00Z",
        "ModificationTime": "2024-02-10T12:05:00Z",
    },
    # Forward Rule - Conditional forwarding (subdomain)
    "rslvr-rr-0subdomain123": {
        "Id": "rslvr-rr-0subdomain123",
        "CreatorRequestId": "terraform-20240215-001",
        "Arn": "arn:aws:route53resolver:eu-west-1:123456789012:resolver-rule/rslvr-rr-0subdomain123",
        "DomainName": "dev.corp.example.com",
        "Status": "COMPLETE",
        "StatusMessage": "This Resolver Rule is complete.",
        "RuleType": "FORWARD",
        "Name": "dev-subdomain-forward",
        "TargetIps": [
            {
                "Ip": "192.168.10.53",
                "Port": 53,
            },
        ],
        "ResolverEndpointId": "rslvr-out-0shared1234",
        "OwnerId": "123456789012",
        "ShareStatus": "NOT_SHARED",
        "CreationTime": "2024-02-15T09:00:00Z",
        "ModificationTime": "2024-02-15T09:05:00Z",
    },
}


# =============================================================================
# RESOLVER RULE ASSOCIATION FIXTURES
# =============================================================================

RESOLVER_RULE_ASSOCIATION_FIXTURES: dict[str, list[dict[str, Any]]] = {
    # Corporate domain rule - Associated with Production and Staging VPCs
    "rslvr-rr-0corp12345678": [
        {
            "Id": "rslvr-rrassoc-0prodcorp",
            "ResolverRuleId": "rslvr-rr-0corp12345678",
            "Name": "production-corporate-dns",
            "VPCId": "vpc-0prod1234567890ab",
            "Status": "COMPLETE",
            "StatusMessage": "This association is complete.",
        },
        {
            "Id": "rslvr-rrassoc-0stagcorp",
            "ResolverRuleId": "rslvr-rr-0corp12345678",
            "Name": "staging-corporate-dns",
            "VPCId": "vpc-0stag1234567890ab",
            "Status": "COMPLETE",
            "StatusMessage": "This association is complete.",
        },
        {
            "Id": "rslvr-rrassoc-0sharedcorp",
            "ResolverRuleId": "rslvr-rr-0corp12345678",
            "Name": "shared-services-corporate-dns",
            "VPCId": "vpc-0shared123456789a",
            "Status": "COMPLETE",
            "StatusMessage": "This association is complete.",
        },
    ],
    # Datacenter domain rule - Associated with Production only
    "rslvr-rr-0dc123456789": [
        {
            "Id": "rslvr-rrassoc-0proddc",
            "ResolverRuleId": "rslvr-rr-0dc123456789",
            "Name": "production-datacenter-dns",
            "VPCId": "vpc-0prod1234567890ab",
            "Status": "COMPLETE",
            "StatusMessage": "This association is complete.",
        },
    ],
    # Partner domain rule - Associated with Production VPC
    "rslvr-rr-0partner1234": [
        {
            "Id": "rslvr-rrassoc-0prodpartner",
            "ResolverRuleId": "rslvr-rr-0partner1234",
            "Name": "production-partner-dns",
            "VPCId": "vpc-0prod1234567890ab",
            "Status": "COMPLETE",
            "StatusMessage": "This association is complete.",
        },
    ],
    # Dev subdomain rule - Associated with Development VPC
    "rslvr-rr-0subdomain123": [
        {
            "Id": "rslvr-rrassoc-0devsubdom",
            "ResolverRuleId": "rslvr-rr-0subdomain123",
            "Name": "development-subdomain-dns",
            "VPCId": "vpc-0dev01234567890ab",
            "Status": "COMPLETE",
            "StatusMessage": "This association is complete.",
        },
    ],
}


# =============================================================================
# QUERY LOGGING CONFIGURATION FIXTURES
# =============================================================================

QUERY_LOG_CONFIG_FIXTURES: dict[str, dict[str, Any]] = {
    # CloudWatch Logs destination - Production VPC
    "rslvr-qlc-0prod12345": {
        "Id": "rslvr-qlc-0prod12345",
        "OwnerId": "123456789012",
        "Status": "CREATED",
        "ShareStatus": "NOT_SHARED",
        "AssociationCount": 1,
        "Arn": "arn:aws:route53resolver:eu-west-1:123456789012:resolver-query-log-config/rslvr-qlc-0prod12345",
        "Name": "production-query-logging",
        "DestinationArn": "arn:aws:logs:eu-west-1:123456789012:log-group:/aws/route53resolver/production",
        "CreatorRequestId": "terraform-20240120-006",
        "CreationTime": "2024-01-20T12:00:00Z",
    },
    # S3 destination - Shared Services VPC
    "rslvr-qlc-0shared123": {
        "Id": "rslvr-qlc-0shared123",
        "OwnerId": "123456789012",
        "Status": "CREATED",
        "ShareStatus": "NOT_SHARED",
        "AssociationCount": 1,
        "Arn": "arn:aws:route53resolver:eu-west-1:123456789012:resolver-query-log-config/rslvr-qlc-0shared123",
        "Name": "shared-services-query-logging-s3",
        "DestinationArn": "arn:aws:s3:::route53-query-logs-shared-services/logs/",
        "CreatorRequestId": "terraform-20240120-007",
        "CreationTime": "2024-01-20T12:10:00Z",
    },
    # CloudWatch Logs - All VPCs (centralized)
    "rslvr-qlc-0central123": {
        "Id": "rslvr-qlc-0central123",
        "OwnerId": "123456789012",
        "Status": "CREATED",
        "ShareStatus": "SHARED_BY_ME",
        "AssociationCount": 3,
        "Arn": "arn:aws:route53resolver:eu-west-1:123456789012:resolver-query-log-config/rslvr-qlc-0central123",
        "Name": "centralized-query-logging",
        "DestinationArn": "arn:aws:logs:eu-west-1:123456789012:log-group:/aws/route53resolver/centralized",
        "CreatorRequestId": "terraform-20240125-001",
        "CreationTime": "2024-01-25T08:00:00Z",
    },
    # Creating status - Staging VPC
    "rslvr-qlc-0stag12345": {
        "Id": "rslvr-qlc-0stag12345",
        "OwnerId": "123456789012",
        "Status": "CREATING",
        "ShareStatus": "NOT_SHARED",
        "AssociationCount": 0,
        "Arn": "arn:aws:route53resolver:us-east-1:123456789012:resolver-query-log-config/rslvr-qlc-0stag12345",
        "Name": "staging-query-logging",
        "DestinationArn": "arn:aws:logs:us-east-1:123456789012:log-group:/aws/route53resolver/staging",
        "CreatorRequestId": "terraform-20240322-002",
        "CreationTime": "2024-03-22T14:10:00Z",
    },
}


# =============================================================================
# QUERY LOG CONFIG ASSOCIATION FIXTURES
# =============================================================================

QUERY_LOG_ASSOCIATION_FIXTURES: dict[str, list[dict[str, Any]]] = {
    # Production query logging - Associated with Production VPC
    "rslvr-qlc-0prod12345": [
        {
            "Id": "rslvr-qlcassoc-0prod1",
            "ResolverQueryLogConfigId": "rslvr-qlc-0prod12345",
            "ResourceId": "vpc-0prod1234567890ab",
            "Status": "ACTIVE",
            "Error": None,
            "ErrorMessage": None,
            "CreationTime": "2024-01-20T12:05:00Z",
        },
    ],
    # Shared services query logging - Associated with Shared Services VPC
    "rslvr-qlc-0shared123": [
        {
            "Id": "rslvr-qlcassoc-0shared1",
            "ResolverQueryLogConfigId": "rslvr-qlc-0shared123",
            "ResourceId": "vpc-0shared123456789a",
            "Status": "ACTIVE",
            "Error": None,
            "ErrorMessage": None,
            "CreationTime": "2024-01-20T12:15:00Z",
        },
    ],
    # Centralized query logging - Associated with multiple VPCs
    "rslvr-qlc-0central123": [
        {
            "Id": "rslvr-qlcassoc-0centralprod",
            "ResolverQueryLogConfigId": "rslvr-qlc-0central123",
            "ResourceId": "vpc-0prod1234567890ab",
            "Status": "ACTIVE",
            "Error": None,
            "ErrorMessage": None,
            "CreationTime": "2024-01-25T08:05:00Z",
        },
        {
            "Id": "rslvr-qlcassoc-0centralstag",
            "ResolverQueryLogConfigId": "rslvr-qlc-0central123",
            "ResourceId": "vpc-0stag1234567890ab",
            "Status": "ACTIVE",
            "Error": None,
            "ErrorMessage": None,
            "CreationTime": "2024-01-25T08:10:00Z",
        },
        {
            "Id": "rslvr-qlcassoc-0centraldev",
            "ResolverQueryLogConfigId": "rslvr-qlc-0central123",
            "ResourceId": "vpc-0dev01234567890ab",
            "Status": "ACTIVE",
            "Error": None,
            "ErrorMessage": None,
            "CreationTime": "2024-01-25T08:15:00Z",
        },
    ],
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_resolver_endpoint_by_id(endpoint_id: str) -> dict[str, Any] | None:
    """Get resolver endpoint fixture by ID."""
    return RESOLVER_ENDPOINT_FIXTURES.get(endpoint_id)


def get_resolver_endpoints_by_vpc(vpc_id: str) -> list[dict[str, Any]]:
    """Get all resolver endpoints for a specific VPC."""
    return [
        ep for ep in RESOLVER_ENDPOINT_FIXTURES.values() if ep["HostVPCId"] == vpc_id
    ]


def get_resolver_endpoints_by_direction(direction: str) -> list[dict[str, Any]]:
    """Get resolver endpoints by direction (INBOUND or OUTBOUND)."""
    return [
        ep for ep in RESOLVER_ENDPOINT_FIXTURES.values() if ep["Direction"] == direction
    ]


def get_operational_endpoints() -> list[dict[str, Any]]:
    """Get all operational resolver endpoints."""
    return [
        ep
        for ep in RESOLVER_ENDPOINT_FIXTURES.values()
        if ep["Status"] == "OPERATIONAL"
    ]


def get_endpoint_ip_addresses(endpoint_id: str) -> list[dict[str, Any]]:
    """Get IP addresses for a resolver endpoint."""
    return RESOLVER_IP_ADDRESS_FIXTURES.get(endpoint_id, [])


def get_resolver_rule_by_id(rule_id: str) -> dict[str, Any] | None:
    """Get resolver rule fixture by ID."""
    return RESOLVER_RULE_FIXTURES.get(rule_id)


def get_resolver_rules_by_type(rule_type: str) -> list[dict[str, Any]]:
    """Get resolver rules by type (FORWARD, SYSTEM, RECURSIVE)."""
    return [
        rule
        for rule in RESOLVER_RULE_FIXTURES.values()
        if rule["RuleType"] == rule_type
    ]


def get_forward_rules() -> list[dict[str, Any]]:
    """Get all forward resolver rules."""
    return get_resolver_rules_by_type("FORWARD")


def get_resolver_rules_by_endpoint(endpoint_id: str) -> list[dict[str, Any]]:
    """Get all resolver rules associated with an endpoint."""
    return [
        rule
        for rule in RESOLVER_RULE_FIXTURES.values()
        if rule.get("ResolverEndpointId") == endpoint_id
    ]


def get_rule_associations(rule_id: str) -> list[dict[str, Any]]:
    """Get VPC associations for a resolver rule."""
    return RESOLVER_RULE_ASSOCIATION_FIXTURES.get(rule_id, [])


def get_rules_associated_with_vpc(vpc_id: str) -> list[dict[str, Any]]:
    """Get all resolver rules associated with a specific VPC."""
    associated_rules = []
    for rule_id, associations in RESOLVER_RULE_ASSOCIATION_FIXTURES.items():
        for assoc in associations:
            if assoc["VPCId"] == vpc_id:
                rule = get_resolver_rule_by_id(rule_id)
                if rule:
                    associated_rules.append(rule)
                break
    return associated_rules


def get_query_log_config_by_id(config_id: str) -> dict[str, Any] | None:
    """Get query logging configuration fixture by ID."""
    return QUERY_LOG_CONFIG_FIXTURES.get(config_id)


def get_query_log_configs_by_status(status: str) -> list[dict[str, Any]]:
    """Get query logging configurations by status (CREATED, CREATING, DELETING)."""
    return [
        config
        for config in QUERY_LOG_CONFIG_FIXTURES.values()
        if config["Status"] == status
    ]


def get_query_log_associations(config_id: str) -> list[dict[str, Any]]:
    """Get VPC associations for a query logging configuration."""
    return QUERY_LOG_ASSOCIATION_FIXTURES.get(config_id, [])


def get_query_log_configs_for_vpc(vpc_id: str) -> list[dict[str, Any]]:
    """Get all query logging configurations associated with a VPC."""
    configs = []
    for config_id, associations in QUERY_LOG_ASSOCIATION_FIXTURES.items():
        for assoc in associations:
            if assoc["ResourceId"] == vpc_id:
                config = get_query_log_config_by_id(config_id)
                if config:
                    configs.append(config)
                break
    return configs


def format_endpoint_for_display(endpoint: dict[str, Any]) -> dict[str, Any]:
    """Format resolver endpoint data for display/testing.

    Returns simplified structure matching module output format.
    """
    ip_addresses = get_endpoint_ip_addresses(endpoint["Id"])

    return {
        "id": endpoint["Id"],
        "name": endpoint.get("Name", endpoint["Id"]),
        "direction": endpoint["Direction"],
        "status": endpoint["Status"],
        "vpc_id": endpoint.get("HostVPCId"),
        "ip_count": endpoint.get("IpAddressCount", 0),
        "ip_addresses": [
            {
                "ip": ip.get("Ip"),
                "subnet": ip.get("SubnetId"),
                "status": ip.get("Status"),
            }
            for ip in ip_addresses
        ],
    }


def format_rule_for_display(rule: dict[str, Any]) -> dict[str, Any]:
    """Format resolver rule data for display/testing.

    Returns simplified structure matching module output format.
    """
    associations = get_rule_associations(rule["Id"])

    return {
        "id": rule["Id"],
        "name": rule.get("Name", rule["Id"]),
        "domain": rule.get("DomainName", ""),
        "rule_type": rule.get("RuleType", ""),
        "status": rule.get("Status", ""),
        "endpoint_id": rule.get("ResolverEndpointId"),
        "target_ips": [t.get("Ip") for t in rule.get("TargetIps", [])],
        "associated_vpcs": [a.get("VPCId") for a in associations],
    }


def get_complete_resolver_config_for_vpc(vpc_id: str) -> dict[str, Any]:
    """Get complete Route53 Resolver configuration for a VPC.

    Returns endpoints, rules, and query logging configurations.
    """
    return {
        "vpc_id": vpc_id,
        "endpoints": get_resolver_endpoints_by_vpc(vpc_id),
        "rules": get_rules_associated_with_vpc(vpc_id),
        "query_log_configs": get_query_log_configs_for_vpc(vpc_id),
    }
