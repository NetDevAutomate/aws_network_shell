"""Realistic Managed Prefix Lists mock data fixtures.

Managed Prefix Lists architecture:
- Customer-managed prefix lists for network policies
- AWS-managed prefix lists (S3, DynamoDB, CloudFront)
- Multi-region prefix list management
- Security group and route table associations

Each prefix list includes:
- CIDR entries with descriptions
- Version tracking
- Entry limits and current usage
- Owner information (customer vs AWS)
- Regional availability
"""

from typing import Any

# =============================================================================
# CUSTOMER-MANAGED PREFIX LIST FIXTURES
# =============================================================================

CUSTOMER_MANAGED_PREFIX_LISTS: dict[str, dict[str, Any]] = {
    # Production On-Premises Networks - eu-west-1
    "pl-0prodremote123456": {
        "PrefixListId": "pl-0prodremote123456",
        "AddressFamily": "IPv4",
        "State": "create-complete",
        "PrefixListArn": "arn:aws:ec2:eu-west-1:123456789012:prefix-list/pl-0prodremote123456",
        "PrefixListName": "prod-on-premises-networks",
        "MaxEntries": 50,
        "Version": 3,
        "Tags": [
            {"Key": "Name", "Value": "prod-on-premises-networks"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "ManagedBy", "Value": "terraform"},
            {"Key": "Purpose", "Value": "on-premises-connectivity"},
        ],
        "OwnerId": "123456789012",
    },
    # Allowed External IPs - eu-west-1
    "pl-0prodallowed123456": {
        "PrefixListId": "pl-0prodallowed123456",
        "AddressFamily": "IPv4",
        "State": "create-complete",
        "PrefixListArn": "arn:aws:ec2:eu-west-1:123456789012:prefix-list/pl-0prodallowed123456",
        "PrefixListName": "prod-allowed-external-ips",
        "MaxEntries": 20,
        "Version": 5,
        "Tags": [
            {"Key": "Name", "Value": "prod-allowed-external-ips"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "ManagedBy", "Value": "terraform"},
            {"Key": "Purpose", "Value": "security-whitelist"},
        ],
        "OwnerId": "123456789012",
    },
    # Blocked IPs - eu-west-1
    "pl-0prodblocked123456": {
        "PrefixListId": "pl-0prodblocked123456",
        "AddressFamily": "IPv4",
        "State": "create-complete",
        "PrefixListArn": "arn:aws:ec2:eu-west-1:123456789012:prefix-list/pl-0prodblocked123456",
        "PrefixListName": "prod-blocked-ips",
        "MaxEntries": 100,
        "Version": 12,
        "Tags": [
            {"Key": "Name", "Value": "prod-blocked-ips"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "ManagedBy", "Value": "security-team"},
            {"Key": "Purpose", "Value": "security-blocklist"},
        ],
        "OwnerId": "123456789012",
    },
    # Partner VPN Networks - us-east-1
    "pl-0stagpartner123456": {
        "PrefixListId": "pl-0stagpartner123456",
        "AddressFamily": "IPv4",
        "State": "create-complete",
        "PrefixListArn": "arn:aws:ec2:us-east-1:123456789012:prefix-list/pl-0stagpartner123456",
        "PrefixListName": "stag-partner-vpn-networks",
        "MaxEntries": 25,
        "Version": 2,
        "Tags": [
            {"Key": "Name", "Value": "stag-partner-vpn-networks"},
            {"Key": "Environment", "Value": "staging"},
            {"Key": "ManagedBy", "Value": "terraform"},
            {"Key": "Purpose", "Value": "partner-connectivity"},
        ],
        "OwnerId": "123456789012",
    },
    # Development Office IPs - ap-southeast-2
    "pl-0devoffice1234567": {
        "PrefixListId": "pl-0devoffice1234567",
        "AddressFamily": "IPv4",
        "State": "create-complete",
        "PrefixListArn": "arn:aws:ec2:ap-southeast-2:123456789012:prefix-list/pl-0devoffice1234567",
        "PrefixListName": "dev-office-ip-ranges",
        "MaxEntries": 10,
        "Version": 1,
        "Tags": [
            {"Key": "Name", "Value": "dev-office-ip-ranges"},
            {"Key": "Environment", "Value": "development"},
            {"Key": "ManagedBy", "Value": "manual"},
        ],
        "OwnerId": "123456789012",
    },
    # IPv6 Partner Networks - eu-west-1
    "pl-0prodv6partner1234": {
        "PrefixListId": "pl-0prodv6partner1234",
        "AddressFamily": "IPv6",
        "State": "create-complete",
        "PrefixListArn": "arn:aws:ec2:eu-west-1:123456789012:prefix-list/pl-0prodv6partner1234",
        "PrefixListName": "prod-ipv6-partner-networks",
        "MaxEntries": 15,
        "Version": 1,
        "Tags": [
            {"Key": "Name", "Value": "prod-ipv6-partner-networks"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "ManagedBy", "Value": "terraform"},
            {"Key": "AddressFamily", "Value": "IPv6"},
        ],
        "OwnerId": "123456789012",
    },
    # Modifying state prefix list
    "pl-0pendmodify123456": {
        "PrefixListId": "pl-0pendmodify123456",
        "AddressFamily": "IPv4",
        "State": "modify-in-progress",
        "PrefixListArn": "arn:aws:ec2:eu-west-1:123456789012:prefix-list/pl-0pendmodify123456",
        "PrefixListName": "pending-modification-list",
        "MaxEntries": 50,
        "Version": 2,
        "Tags": [
            {"Key": "Name", "Value": "pending-modification-list"},
            {"Key": "Environment", "Value": "production"},
        ],
        "OwnerId": "123456789012",
    },
}

# =============================================================================
# AWS-MANAGED PREFIX LIST FIXTURES
# =============================================================================

AWS_MANAGED_PREFIX_LISTS: dict[str, dict[str, Any]] = {
    # S3 Prefix List - eu-west-1
    "pl-aws-s3-eu-west-1": {
        "PrefixListId": "pl-6da54004",
        "AddressFamily": "IPv4",
        "State": "create-complete",
        "PrefixListArn": "arn:aws:ec2:eu-west-1:aws:prefix-list/pl-6da54004",
        "PrefixListName": "com.amazonaws.eu-west-1.s3",
        "MaxEntries": 20,
        "Version": 1,
        "Tags": [],
        "OwnerId": "AWS",
    },
    # DynamoDB Prefix List - eu-west-1
    "pl-aws-dynamodb-eu-west-1": {
        "PrefixListId": "pl-6ea54007",
        "AddressFamily": "IPv4",
        "State": "create-complete",
        "PrefixListArn": "arn:aws:ec2:eu-west-1:aws:prefix-list/pl-6ea54007",
        "PrefixListName": "com.amazonaws.eu-west-1.dynamodb",
        "MaxEntries": 10,
        "Version": 1,
        "Tags": [],
        "OwnerId": "AWS",
    },
    # CloudFront Prefix List - Global
    "pl-aws-cloudfront-global": {
        "PrefixListId": "pl-3b927c52",
        "AddressFamily": "IPv4",
        "State": "create-complete",
        "PrefixListArn": "arn:aws:ec2:global:aws:prefix-list/pl-3b927c52",
        "PrefixListName": "com.amazonaws.global.cloudfront.origin-facing",
        "MaxEntries": 100,
        "Version": 1,
        "Tags": [],
        "OwnerId": "AWS",
    },
    # S3 Prefix List - us-east-1
    "pl-aws-s3-us-east-1": {
        "PrefixListId": "pl-63a5400a",
        "AddressFamily": "IPv4",
        "State": "create-complete",
        "PrefixListArn": "arn:aws:ec2:us-east-1:aws:prefix-list/pl-63a5400a",
        "PrefixListName": "com.amazonaws.us-east-1.s3",
        "MaxEntries": 20,
        "Version": 1,
        "Tags": [],
        "OwnerId": "AWS",
    },
    # S3 Prefix List - ap-southeast-2
    "pl-aws-s3-ap-southeast-2": {
        "PrefixListId": "pl-02cd2c6b",
        "AddressFamily": "IPv4",
        "State": "create-complete",
        "PrefixListArn": "arn:aws:ec2:ap-southeast-2:aws:prefix-list/pl-02cd2c6b",
        "PrefixListName": "com.amazonaws.ap-southeast-2.s3",
        "MaxEntries": 20,
        "Version": 1,
        "Tags": [],
        "OwnerId": "AWS",
    },
}

# =============================================================================
# PREFIX LIST ENTRIES
# =============================================================================

PREFIX_LIST_ENTRIES: dict[str, list[dict[str, Any]]] = {
    # Production On-Premises Networks entries
    "pl-0prodremote123456": [
        {"Cidr": "192.168.0.0/16", "Description": "HQ datacenter network"},
        {"Cidr": "172.20.0.0/16", "Description": "Branch office network"},
        {"Cidr": "10.100.0.0/16", "Description": "DR site network"},
        {"Cidr": "10.200.0.0/16", "Description": "Remote office 1"},
        {"Cidr": "10.201.0.0/16", "Description": "Remote office 2"},
    ],
    # Allowed External IPs entries
    "pl-0prodallowed123456": [
        {"Cidr": "203.0.113.0/24", "Description": "Partner API gateway"},
        {"Cidr": "198.51.100.0/24", "Description": "Vendor management system"},
        {"Cidr": "192.0.2.10/32", "Description": "Third-party monitoring service"},
        {"Cidr": "192.0.2.20/32", "Description": "Security scanning service"},
        {"Cidr": "192.0.2.30/32", "Description": "CI/CD pipeline webhook"},
    ],
    # Blocked IPs entries
    "pl-0prodblocked123456": [
        {"Cidr": "185.220.100.0/24", "Description": "Known malicious network"},
        {"Cidr": "185.220.101.0/24", "Description": "Spam source network"},
        {"Cidr": "45.142.120.0/24", "Description": "DDoS attack source"},
        {"Cidr": "91.219.236.0/24", "Description": "Scanning activity source"},
        {"Cidr": "194.26.192.0/24", "Description": "Brute force attempts"},
    ],
    # Partner VPN Networks entries
    "pl-0stagpartner123456": [
        {"Cidr": "10.50.0.0/16", "Description": "Partner A VPN network"},
        {"Cidr": "10.51.0.0/16", "Description": "Partner B VPN network"},
        {"Cidr": "172.25.0.0/16", "Description": "Partner C VPN network"},
    ],
    # Development Office IPs entries
    "pl-0devoffice1234567": [
        {"Cidr": "203.0.113.100/32", "Description": "Sydney office"},
        {"Cidr": "203.0.113.101/32", "Description": "Melbourne office"},
        {"Cidr": "203.0.113.102/32", "Description": "Brisbane office"},
    ],
    # IPv6 Partner Networks entries
    "pl-0prodv6partner1234": [
        {"Cidr": "2001:db8:1::/48", "Description": "Partner A IPv6 network"},
        {"Cidr": "2001:db8:2::/48", "Description": "Partner B IPv6 network"},
    ],
    # Pending modification list entries
    "pl-0pendmodify123456": [
        {"Cidr": "10.250.0.0/16", "Description": "Existing entry 1"},
        {"Cidr": "10.251.0.0/16", "Description": "Existing entry 2"},
    ],
    # S3 Prefix List - eu-west-1 entries
    "pl-6da54004": [
        {"Cidr": "52.218.0.0/17", "Description": ""},
        {"Cidr": "54.231.0.0/16", "Description": ""},
        {"Cidr": "52.92.16.0/20", "Description": ""},
    ],
    # DynamoDB Prefix List - eu-west-1 entries
    "pl-6ea54007": [
        {"Cidr": "52.94.0.0/22", "Description": ""},
        {"Cidr": "52.119.0.0/22", "Description": ""},
    ],
    # CloudFront Prefix List entries
    "pl-3b927c52": [
        {"Cidr": "13.32.0.0/15", "Description": ""},
        {"Cidr": "52.84.0.0/15", "Description": ""},
        {"Cidr": "54.182.0.0/16", "Description": ""},
        {"Cidr": "54.192.0.0/16", "Description": ""},
        {"Cidr": "54.230.0.0/16", "Description": ""},
    ],
    # S3 Prefix List - us-east-1 entries
    "pl-63a5400a": [
        {"Cidr": "52.216.0.0/15", "Description": ""},
        {"Cidr": "54.231.0.0/16", "Description": ""},
        {"Cidr": "52.92.16.0/20", "Description": ""},
    ],
    # S3 Prefix List - ap-southeast-2 entries
    "pl-02cd2c6b": [
        {"Cidr": "52.95.128.0/21", "Description": ""},
        {"Cidr": "54.231.248.0/22", "Description": ""},
    ],
}

# =============================================================================
# PREFIX LIST ASSOCIATIONS (Security Groups and Route Tables)
# =============================================================================

PREFIX_LIST_ASSOCIATIONS: dict[str, list[dict[str, Any]]] = {
    # Production On-Premises Networks associations
    "pl-0prodremote123456": [
        {
            "ResourceId": "sg-0prodweb123456789",
            "ResourceType": "security-group",
            "ResourceName": "production-web-sg",
            "Region": "eu-west-1",
        },
        {
            "ResourceId": "sg-0prodapp123456789",
            "ResourceType": "security-group",
            "ResourceName": "production-app-sg",
            "Region": "eu-west-1",
        },
        {
            "ResourceId": "rtb-0prodpriv1234567",
            "ResourceType": "route-table",
            "ResourceName": "production-private-rtb",
            "Region": "eu-west-1",
        },
    ],
    # Allowed External IPs associations
    "pl-0prodallowed123456": [
        {
            "ResourceId": "sg-0prodapi123456789",
            "ResourceType": "security-group",
            "ResourceName": "production-api-sg",
            "Region": "eu-west-1",
        },
        {
            "ResourceId": "sg-0prodlb1234567890",
            "ResourceType": "security-group",
            "ResourceName": "production-alb-sg",
            "Region": "eu-west-1",
        },
    ],
    # Blocked IPs associations
    "pl-0prodblocked123456": [
        {
            "ResourceId": "sg-0prodfirewall12345",
            "ResourceType": "security-group",
            "ResourceName": "production-firewall-sg",
            "Region": "eu-west-1",
        },
        {
            "ResourceId": "nacl-0prod123456789ab",
            "ResourceType": "network-acl",
            "ResourceName": "production-public-nacl",
            "Region": "eu-west-1",
        },
    ],
    # Partner VPN Networks associations
    "pl-0stagpartner123456": [
        {
            "ResourceId": "sg-0stagvpn123456789",
            "ResourceType": "security-group",
            "ResourceName": "staging-vpn-sg",
            "Region": "us-east-1",
        },
    ],
    # Development Office IPs associations
    "pl-0devoffice1234567": [
        {
            "ResourceId": "sg-0devssh1234567890",
            "ResourceType": "security-group",
            "ResourceName": "development-ssh-sg",
            "Region": "ap-southeast-2",
        },
    ],
    # IPv6 Partner Networks associations
    "pl-0prodv6partner1234": [
        {
            "ResourceId": "sg-0prodipv612345678",
            "ResourceType": "security-group",
            "ResourceName": "production-ipv6-sg",
            "Region": "eu-west-1",
        },
    ],
    # S3 Prefix List associations
    "pl-6da54004": [
        {
            "ResourceId": "rtb-0prods3route12345",
            "ResourceType": "route-table",
            "ResourceName": "production-s3-endpoint-rtb",
            "Region": "eu-west-1",
        },
        {
            "ResourceId": "sg-0prods3endpoint123",
            "ResourceType": "security-group",
            "ResourceName": "production-s3-endpoint-sg",
            "Region": "eu-west-1",
        },
    ],
    # DynamoDB Prefix List associations
    "pl-6ea54007": [
        {
            "ResourceId": "rtb-0proddynamo12345",
            "ResourceType": "route-table",
            "ResourceName": "production-dynamodb-endpoint-rtb",
            "Region": "eu-west-1",
        },
    ],
    # CloudFront Prefix List associations
    "pl-3b927c52": [
        {
            "ResourceId": "sg-0prodcf123456789",
            "ResourceType": "security-group",
            "ResourceName": "production-cloudfront-sg",
            "Region": "eu-west-1",
        },
    ],
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_prefix_list_by_id(prefix_list_id: str) -> dict[str, Any] | None:
    """Get prefix list by ID.

    Args:
        prefix_list_id: Prefix list ID

    Returns:
        Prefix list data or None if not found
    """
    # Check customer-managed first
    if prefix_list_id in CUSTOMER_MANAGED_PREFIX_LISTS:
        return CUSTOMER_MANAGED_PREFIX_LISTS[prefix_list_id]
    # Then check AWS-managed
    return AWS_MANAGED_PREFIX_LISTS.get(prefix_list_id)


def get_prefix_list_by_name(name: str) -> dict[str, Any] | None:
    """Get prefix list by name.

    Args:
        name: Prefix list name

    Returns:
        Prefix list data or None if not found
    """
    # Check customer-managed
    for pl in CUSTOMER_MANAGED_PREFIX_LISTS.values():
        if pl.get("PrefixListName") == name:
            return pl
    # Check AWS-managed
    for pl in AWS_MANAGED_PREFIX_LISTS.values():
        if pl.get("PrefixListName") == name:
            return pl
    return None


def get_customer_managed_prefix_lists() -> list[dict[str, Any]]:
    """Get all customer-managed prefix lists.

    Returns:
        List of customer-managed prefix lists
    """
    return list(CUSTOMER_MANAGED_PREFIX_LISTS.values())


def get_aws_managed_prefix_lists() -> list[dict[str, Any]]:
    """Get all AWS-managed prefix lists.

    Returns:
        List of AWS-managed prefix lists
    """
    return list(AWS_MANAGED_PREFIX_LISTS.values())


def get_all_prefix_lists(include_aws_managed: bool = True) -> list[dict[str, Any]]:
    """Get all prefix lists.

    Args:
        include_aws_managed: Include AWS-managed prefix lists

    Returns:
        List of all prefix lists
    """
    lists = list(CUSTOMER_MANAGED_PREFIX_LISTS.values())
    if include_aws_managed:
        lists.extend(AWS_MANAGED_PREFIX_LISTS.values())
    return lists


def get_prefix_list_entries(prefix_list_id: str) -> list[dict[str, Any]]:
    """Get entries for a prefix list.

    Args:
        prefix_list_id: Prefix list ID

    Returns:
        List of prefix list entries
    """
    return PREFIX_LIST_ENTRIES.get(prefix_list_id, [])


def get_prefix_list_associations(prefix_list_id: str) -> list[dict[str, Any]]:
    """Get associations for a prefix list.

    Args:
        prefix_list_id: Prefix list ID

    Returns:
        List of associations
    """
    return PREFIX_LIST_ASSOCIATIONS.get(prefix_list_id, [])


def get_prefix_lists_by_state(state: str) -> list[dict[str, Any]]:
    """Get prefix lists by state.

    Args:
        state: State (create-complete, modify-in-progress, etc.)

    Returns:
        List of prefix lists with matching state
    """
    return [
        pl
        for pl in get_all_prefix_lists(include_aws_managed=True)
        if pl.get("State") == state
    ]


def get_prefix_lists_by_address_family(address_family: str) -> list[dict[str, Any]]:
    """Get prefix lists by address family.

    Args:
        address_family: Address family (IPv4, IPv6)

    Returns:
        List of prefix lists with matching address family
    """
    return [
        pl
        for pl in get_all_prefix_lists(include_aws_managed=True)
        if pl.get("AddressFamily") == address_family
    ]


def get_prefix_lists_by_tag(key: str, value: str) -> list[dict[str, Any]]:
    """Get customer-managed prefix lists by tag.

    Args:
        key: Tag key
        value: Tag value

    Returns:
        List of prefix lists with matching tag
    """
    matching = []
    for pl in CUSTOMER_MANAGED_PREFIX_LISTS.values():
        for tag in pl.get("Tags", []):
            if tag.get("Key") == key and tag.get("Value") == value:
                matching.append(pl)
                break
    return matching


def get_prefix_lists_near_capacity(threshold: float = 0.8) -> list[dict[str, Any]]:
    """Get prefix lists nearing capacity.

    Args:
        threshold: Capacity threshold (0.0-1.0, default 0.8 = 80%)

    Returns:
        List of prefix lists above threshold
    """
    near_capacity = []
    for pl_id, pl in {
        **CUSTOMER_MANAGED_PREFIX_LISTS,
        **AWS_MANAGED_PREFIX_LISTS,
    }.items():
        max_entries = pl.get("MaxEntries", 0)
        current_entries = len(PREFIX_LIST_ENTRIES.get(pl_id, []))
        if max_entries > 0 and current_entries / max_entries >= threshold:
            near_capacity.append(
                {
                    **pl,
                    "current_entries": current_entries,
                    "capacity_percentage": (current_entries / max_entries) * 100,
                }
            )
    return near_capacity


def get_security_group_associations() -> dict[str, list[str]]:
    """Get all security group associations with prefix lists.

    Returns:
        Dictionary mapping security group IDs to prefix list IDs
    """
    sg_associations: dict[str, list[str]] = {}
    for pl_id, associations in PREFIX_LIST_ASSOCIATIONS.items():
        for assoc in associations:
            if assoc.get("ResourceType") == "security-group":
                sg_id = assoc["ResourceId"]
                if sg_id not in sg_associations:
                    sg_associations[sg_id] = []
                sg_associations[sg_id].append(pl_id)
    return sg_associations


def get_route_table_associations() -> dict[str, list[str]]:
    """Get all route table associations with prefix lists.

    Returns:
        Dictionary mapping route table IDs to prefix list IDs
    """
    rtb_associations: dict[str, list[str]] = {}
    for pl_id, associations in PREFIX_LIST_ASSOCIATIONS.items():
        for assoc in associations:
            if assoc.get("ResourceType") == "route-table":
                rtb_id = assoc["ResourceId"]
                if rtb_id not in rtb_associations:
                    rtb_associations[rtb_id] = []
                rtb_associations[rtb_id].append(pl_id)
    return rtb_associations


def count_entries_by_prefix_list() -> dict[str, int]:
    """Count entries for each prefix list.

    Returns:
        Dictionary mapping prefix list IDs to entry counts
    """
    return {pl_id: len(entries) for pl_id, entries in PREFIX_LIST_ENTRIES.items()}


def get_ipv6_prefix_lists() -> list[dict[str, Any]]:
    """Get all IPv6 prefix lists.

    Returns:
        List of IPv6 prefix lists
    """
    return get_prefix_lists_by_address_family("IPv6")
