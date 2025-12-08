# AWS Network Tools - Command Hierarchy (Split Diagrams)

This document shows the command hierarchy using multiple smaller, readable diagrams.

- **Total Contexts**: 9
- **Total Commands**: 103

## 1. Overview: Context Navigation

```mermaid
graph TD
    classDef root fill:#2d5a27,stroke:#1a3518,color:#fff
    classDef context fill:#1a4a6e,stroke:#0d2840,color:#fff

    root["aws-net"]:::root
    root_set_ec2_instance{"set ec2-instance → ec2-instance"}:::context
    root --> root_set_ec2_instance
    root_set_elb{"set elb → elb"}:::context
    root --> root_set_elb
    root_set_firewall{"set firewall → firewall"}:::context
    root --> root_set_firewall
    root_set_global_network{"set global-network → global-network"}:::context
    root --> root_set_global_network
    root_set_transit_gateway{"set transit-gateway → transit-gateway"}:::context
    root --> root_set_transit_gateway
    root_set_vpc{"set vpc → vpc"}:::context
    root --> root_set_vpc
    root_set_vpn{"set vpn → vpn"}:::context
    root --> root_set_vpn
```

## 2. Core-Network Context

**Entry**: `set core-network`

```mermaid
graph LR
    classDef context fill:#1a4a6e,stroke:#0d2840,color:#fff
    classDef show fill:#4a4a8a,stroke:#2d2d5a,color:#fff
    classDef action fill:#8b4513,stroke:#5a2d0a,color:#fff
    classDef set fill:#6b4c9a,stroke:#3d2a5a,color:#fff

    global_network_set_core_network{"set core-network → core-network"}:::context
    core_network_context["core-network context"]:::context
    global_network_set_core_network --> core_network_context
    core_network_show_detail["show detail"]:::show
    core_network_context --> core_network_show_detail
    core_network_show_segments["show segments"]:::show
    core_network_context --> core_network_show_segments
    core_network_show_policy["show policy"]:::show
    core_network_context --> core_network_show_policy
    core_network_show_routes["show routes"]:::show
    core_network_context --> core_network_show_routes
    core_network_show_route_tables["show route-tables"]:::show
    core_network_context --> core_network_show_route_tables
    core_network_show_blackhole_routes["show blackhole-routes"]:::show
    core_network_context --> core_network_show_blackhole_routes
    core_network_show_policy_change_events["show policy-change-events"]:::show
    core_network_context --> core_network_show_policy_change_events
    core_network_show_connect_attachments["show connect-attachments"]:::show
    core_network_context --> core_network_show_connect_attachments
    core_network_show_connect_peers["show connect-peers"]:::show
    core_network_context --> core_network_show_connect_peers
    core_network_show_rib["show rib"]:::show
    core_network_context --> core_network_show_rib
    core_network_do_find_prefix(("find_prefix")):::action
    core_network_context --> core_network_do_find_prefix
    core_network_do_find_null_routes(("find_null_routes")):::action
    core_network_context --> core_network_do_find_null_routes
```

## 3. Ec2-Instance Context

**Entry**: `set ec2-instance`

```mermaid
graph LR
    classDef context fill:#1a4a6e,stroke:#0d2840,color:#fff
    classDef show fill:#4a4a8a,stroke:#2d2d5a,color:#fff
    classDef action fill:#8b4513,stroke:#5a2d0a,color:#fff
    classDef set fill:#6b4c9a,stroke:#3d2a5a,color:#fff

    root_set_ec2_instance{"set ec2-instance → ec2-instance"}:::context
    ec2_instance_context["ec2-instance context"]:::context
    root_set_ec2_instance --> ec2_instance_context
    ec2_instance_show_detail["show detail"]:::show
    ec2_instance_context --> ec2_instance_show_detail
    ec2_instance_show_security_groups["show security-groups"]:::show
    ec2_instance_context --> ec2_instance_show_security_groups
    ec2_instance_show_enis["show enis"]:::show
    ec2_instance_context --> ec2_instance_show_enis
    ec2_instance_show_routes["show routes"]:::show
    ec2_instance_context --> ec2_instance_show_routes
```

## 4. Elb Context

**Entry**: `set elb`

```mermaid
graph LR
    classDef context fill:#1a4a6e,stroke:#0d2840,color:#fff
    classDef show fill:#4a4a8a,stroke:#2d2d5a,color:#fff
    classDef action fill:#8b4513,stroke:#5a2d0a,color:#fff
    classDef set fill:#6b4c9a,stroke:#3d2a5a,color:#fff

    root_set_elb{"set elb → elb"}:::context
    elb_context["elb context"]:::context
    root_set_elb --> elb_context
    elb_show_detail["show detail"]:::show
    elb_context --> elb_show_detail
    elb_show_listeners["show listeners"]:::show
    elb_context --> elb_show_listeners
    elb_show_targets["show targets"]:::show
    elb_context --> elb_show_targets
    elb_show_health["show health"]:::show
    elb_context --> elb_show_health
```

## 5. Firewall Context

**Entry**: `set firewall`

```mermaid
graph LR
    classDef context fill:#1a4a6e,stroke:#0d2840,color:#fff
    classDef show fill:#4a4a8a,stroke:#2d2d5a,color:#fff
    classDef action fill:#8b4513,stroke:#5a2d0a,color:#fff
    classDef set fill:#6b4c9a,stroke:#3d2a5a,color:#fff

    root_set_firewall{"set firewall → firewall"}:::context
    firewall_context["firewall context"]:::context
    root_set_firewall --> firewall_context
    firewall_show_firewall["show firewall"]:::show
    firewall_context --> firewall_show_firewall
    firewall_show_detail["show detail (alias)"]:::show
    firewall_context --> firewall_show_detail
    firewall_show_rule_groups["show firewall-rule-groups"]:::show
    firewall_context --> firewall_show_rule_groups
    firewall_show_rg_alias["show rule-groups (alias)"]:::show
    firewall_context --> firewall_show_rg_alias
    firewall_show_policy["show firewall-policy"]:::show
    firewall_context --> firewall_show_policy
    firewall_show_policy_alias["show policy (alias)"]:::show
    firewall_context --> firewall_show_policy_alias
    firewall_show_networking["show firewall-networking"]:::show
    firewall_context --> firewall_show_networking
    firewall_set_rule_group{"set rule-group → rule-group"}:::set
    firewall_context --> firewall_set_rule_group
    
    rule_group_context["rule-group context"]:::context
    firewall_set_rule_group --> rule_group_context
    rule_group_show_rule_group["show rule-group"]:::show
    rule_group_context --> rule_group_show_rule_group
```

## 6. Global-Network Context

**Entry**: `set global-network`

```mermaid
graph LR
    classDef context fill:#1a4a6e,stroke:#0d2840,color:#fff
    classDef show fill:#4a4a8a,stroke:#2d2d5a,color:#fff
    classDef action fill:#8b4513,stroke:#5a2d0a,color:#fff
    classDef set fill:#6b4c9a,stroke:#3d2a5a,color:#fff

    root_set_global_network{"set global-network → global-network"}:::context
    global_network_context["global-network context"]:::context
    root_set_global_network --> global_network_context
    global_network_show_detail["show detail"]:::show
    global_network_context --> global_network_show_detail
    global_network_show_core_networks["show core-networks"]:::show
    global_network_context --> global_network_show_core_networks
```

## 7. Route-Table Context

**Entry**: `set route-table`

```mermaid
graph LR
    classDef context fill:#1a4a6e,stroke:#0d2840,color:#fff
    classDef show fill:#4a4a8a,stroke:#2d2d5a,color:#fff
    classDef action fill:#8b4513,stroke:#5a2d0a,color:#fff
    classDef set fill:#6b4c9a,stroke:#3d2a5a,color:#fff

    core_network_set_route_table{"set route-table → route-table"}:::context
    route_table_context["route-table context"]:::context
    core_network_set_route_table --> route_table_context
    route_table_show_routes["show routes"]:::show
    route_table_context --> route_table_show_routes
    route_table_do_find_prefix(("find_prefix")):::action
    route_table_context --> route_table_do_find_prefix
    route_table_do_find_null_routes(("find_null_routes")):::action
    route_table_context --> route_table_do_find_null_routes
```

## 8. Transit-Gateway Context

**Entry**: `set transit-gateway`

```mermaid
graph LR
    classDef context fill:#1a4a6e,stroke:#0d2840,color:#fff
    classDef show fill:#4a4a8a,stroke:#2d2d5a,color:#fff
    classDef action fill:#8b4513,stroke:#5a2d0a,color:#fff
    classDef set fill:#6b4c9a,stroke:#3d2a5a,color:#fff

    root_set_transit_gateway{"set transit-gateway → transit-gateway"}:::context
    transit_gateway_context["transit-gateway context"]:::context
    root_set_transit_gateway --> transit_gateway_context
    transit_gateway_show_detail["show detail"]:::show
    transit_gateway_context --> transit_gateway_show_detail
    transit_gateway_show_route_tables["show route-tables"]:::show
    transit_gateway_context --> transit_gateway_show_route_tables
    transit_gateway_show_attachments["show attachments"]:::show
    transit_gateway_context --> transit_gateway_show_attachments
    transit_gateway_do_find_prefix(("find_prefix")):::action
    transit_gateway_context --> transit_gateway_do_find_prefix
    transit_gateway_do_find_null_routes(("find_null_routes")):::action
    transit_gateway_context --> transit_gateway_do_find_null_routes
```

## 9. Vpc Context

**Entry**: `set vpc`

```mermaid
graph LR
    classDef context fill:#1a4a6e,stroke:#0d2840,color:#fff
    classDef show fill:#4a4a8a,stroke:#2d2d5a,color:#fff
    classDef action fill:#8b4513,stroke:#5a2d0a,color:#fff
    classDef set fill:#6b4c9a,stroke:#3d2a5a,color:#fff

    root_set_vpc{"set vpc → vpc"}:::context
    vpc_context["vpc context"]:::context
    root_set_vpc --> vpc_context
    vpc_show_detail["show detail"]:::show
    vpc_context --> vpc_show_detail
    vpc_show_route_tables["show route-tables"]:::show
    vpc_context --> vpc_show_route_tables
    vpc_show_subnets["show subnets"]:::show
    vpc_context --> vpc_show_subnets
    vpc_show_security_groups["show security-groups"]:::show
    vpc_context --> vpc_show_security_groups
    vpc_show_nacls["show nacls"]:::show
    vpc_context --> vpc_show_nacls
    vpc_show_internet_gateways["show internet-gateways"]:::show
    vpc_context --> vpc_show_internet_gateways
    vpc_show_nat_gateways["show nat-gateways"]:::show
    vpc_context --> vpc_show_nat_gateways
    vpc_show_endpoints["show endpoints"]:::show
    vpc_context --> vpc_show_endpoints
    vpc_do_find_prefix(("find_prefix")):::action
    vpc_context --> vpc_do_find_prefix
    vpc_do_find_null_routes(("find_null_routes")):::action
    vpc_context --> vpc_do_find_null_routes
```

## 10. Vpn Context

**Entry**: `set vpn`

```mermaid
graph LR
    classDef context fill:#1a4a6e,stroke:#0d2840,color:#fff
    classDef show fill:#4a4a8a,stroke:#2d2d5a,color:#fff
    classDef action fill:#8b4513,stroke:#5a2d0a,color:#fff
    classDef set fill:#6b4c9a,stroke:#3d2a5a,color:#fff

    root_set_vpn{"set vpn → vpn"}:::context
    vpn_context["vpn context"]:::context
    root_set_vpn --> vpn_context
    vpn_show_detail["show detail"]:::show
    vpn_context --> vpn_show_detail
    vpn_show_tunnels["show tunnels"]:::show
    vpn_context --> vpn_show_tunnels
```
