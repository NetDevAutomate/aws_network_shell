"""AWS Network Firewall module"""

import concurrent.futures
import logging
from typing import Optional, Dict, List
import boto3
from rich.table import Table
from rich.tree import Tree
from rich.panel import Panel

from ..core import Cache, BaseDisplay, BaseClient, ModuleInterface, Context

logger = logging.getLogger("aws_network_tools.anfw")

cache = Cache("anfw")


class ANFWModule(ModuleInterface):
    @property
    def name(self) -> str:
        return "aws-network-firewall"

    @property
    def commands(self) -> Dict[str, str]:
        return {
            "aws-network-firewall": "Enter firewall context: aws-network-firewall <#|name>"
        }

    @property
    def context_commands(self) -> Dict[str, List[str]]:
        return {
            "aws-network-firewall": ["rule-group"],
        }

    @property
    def show_commands(self) -> Dict[str, List[str]]:
        return {
            None: ["firewalls"],
            "aws-network-firewall": ["firewall", "detail", "firewall-rule-groups", "rule-groups", "firewall-policy", "policy", "firewall-networking"],
            "rule-group": ["rule-group"]
        }

    def execute(self, shell, command: str, args: str):
        """Enter firewall context"""
        if shell.ctx_type is not None:
            shell.console.print("[red]Use 'end' to return to top level first[/]")
            return

        ref = args.strip()
        if not ref:
            shell.console.print("[red]Usage: aws-network-firewall <#|name>[/]")
            return

        fws = shell._get_firewalls()
        # Use existing resolve_firewall helper which checks name and id
        target = resolve_firewall(fws, ref)

        if not target:
            shell.console.print(f"[red]Firewall '{ref}' not found[/]")
            return

        shell.context_stack = [
            Context(
                "aws-network-firewall", ref, target.get("name") or "firewall", target
            )
        ]
        shell._update_prompt()


class ANFWClient(BaseClient):
    def __init__(
        self, profile: Optional[str] = None, session: Optional[boto3.Session] = None
    ):
        super().__init__(profile, session)

    def get_regions(self) -> list[str]:
        try:
            region = self.session.region_name or "us-east-1"
            ec2 = self.client("ec2", region_name=region)
            return [
                r["RegionName"]
                for r in ec2.describe_regions(AllRegions=False)["Regions"]
            ]
        except Exception:
            if self.session.region_name:
                return [self.session.region_name]
            return []

    def _get_logging(self, client, fw_name: str) -> dict:
        try:
            resp = client.describe_logging_configuration(FirewallName=fw_name)
            dests = resp.get("LoggingConfiguration", {}).get(
                "LogDestinationConfigs", []
            )
            if not dests:
                return {"enabled": False, "types": [], "destinations": []}
            types, destinations = [], []
            for d in dests:
                types.append(d.get("LogType", "Unknown"))
                dt = d.get("LogDestinationType", "")
                dc = d.get("LogDestination", {})
                if dt == "CloudWatchLogs":
                    destinations.append(f"CW: {dc.get('logGroup', 'N/A')}")
                elif dt == "S3":
                    destinations.append(f"S3: {dc.get('bucketName', 'N/A')}")
                elif dt == "KinesisDataFirehose":
                    destinations.append(f"Firehose: {dc.get('deliveryStream', 'N/A')}")
                else:
                    destinations.append(dt)
            return {"enabled": True, "types": types, "destinations": destinations}
        except Exception:
            return {"enabled": False, "types": [], "destinations": []}

    def _get_policy_details(self, client, policy_arn: str) -> dict:
        try:
            resp = client.describe_firewall_policy(FirewallPolicyArn=policy_arn)
            policy = resp.get("FirewallPolicy", {})
            policy_response = resp.get("FirewallPolicyResponse", {})

            # Get stateless rule groups with type info
            stateless_groups = []
            for rg in policy.get("StatelessRuleGroupReferences", []):
                arn = rg.get("ResourceArn", "")
                name = arn.split("/")[-1] if arn else ""
                stateless_groups.append(
                    {
                        "name": name,
                        "arn": arn,
                        "type": "STATELESS",
                        "priority": rg.get("Priority", 0),
                    }
                )

            # Get stateful rule groups with type info
            stateful_groups = []
            for rg in policy.get("StatefulRuleGroupReferences", []):
                arn = rg.get("ResourceArn", "")
                name = arn.split("/")[-1] if arn else ""
                stateful_groups.append(
                    {
                        "name": name,
                        "arn": arn,
                        "type": "STATEFUL",
                        "priority": rg.get("Priority"),
                    }
                )

            # Get stateful engine options
            stateful_engine = policy.get("StatefulEngineOptions", {})

            return {
                "name": policy_response.get("FirewallPolicyName", "N/A"),
                "arn": policy_arn,
                "rule_group_refs": stateless_groups + stateful_groups,
                "stateless_default_actions": {
                    "full_packets": policy.get("StatelessDefaultActions", []),
                    "fragmented": policy.get("StatelessFragmentDefaultActions", []),
                },
                "stateful_engine_options": {
                    "rule_order": stateful_engine.get("RuleOrder", "N/A"),
                    "stream_exception_policy": stateful_engine.get(
                        "StreamExceptionPolicy", "N/A"
                    ),
                },
            }
        except Exception:
            return {}

    def _get_rule_group(self, client, rg_name: str, rg_type: str) -> dict:
        try:
            resp = client.describe_rule_group(RuleGroupName=rg_name, Type=rg_type)
            rg = resp.get("RuleGroup", {})
            rg_resp = resp.get("RuleGroupResponse", {})
            rules_source = rg.get("RulesSource", {})
            rules = []

            if rg_type == "STATELESS":
                # Stateless rules with full port information
                for sr in rules_source.get("StatelessRulesAndCustomActions", {}).get(
                    "StatelessRules", []
                ):
                    rd = sr.get("RuleDefinition", {})
                    match_attrs = rd.get("MatchAttributes", {})
                    # Format match info
                    sources = [
                        s.get("AddressDefinition", "")
                        for s in match_attrs.get("Sources", [])
                    ]
                    dests = [
                        d.get("AddressDefinition", "")
                        for d in match_attrs.get("Destinations", [])
                    ]
                    protocols = match_attrs.get("Protocols", [])
                    source_ports = match_attrs.get("SourcePorts", [])
                    dest_ports = match_attrs.get("DestinationPorts", [])
                    
                    rules.append(
                        {
                            "priority": sr.get("Priority", 0),
                            "actions": rd.get("Actions", []),
                            "sources": sources,
                            "destinations": dests,
                            "protocols": protocols,
                            "source_ports": source_ports,
                            "dest_ports": dest_ports,
                        }
                    )
            else:
                # Stateful rules - could be Suricata format or domain list
                if rules_source.get("RulesString"):
                    for line in rules_source["RulesString"].split("\n"):
                        line = line.strip()
                        if line and not line.startswith("#"):
                            rules.append({"rule": line})
                # Domain list
                if rules_source.get("RulesSourceList"):
                    rsl = rules_source["RulesSourceList"]
                    for target in rsl.get("Targets", []):
                        rules.append(
                            {
                                "rule": f"{rsl.get('GeneratedRulesType', 'ALLOWLIST')}: {target}",
                                "target_types": rsl.get("TargetTypes", []),
                            }
                        )
                # 5-tuple rules
                for sr in rules_source.get("StatefulRules", []):
                    header = sr.get("Header", {})
                    rules.append(
                        {
                            "rule": f"{sr.get('Action', '')} {header.get('Protocol', '')} {header.get('Source', '')}:{header.get('SourcePort', '')} -> {header.get('Destination', '')}:{header.get('DestinationPort', '')}",
                            "action": sr.get("Action", ""),
                        }
                    )

            return {
                "name": rg_name,
                "type": rg_type,
                "rules": rules,
                "capacity": rg_resp.get("Capacity", 0),
                "consumed_capacity": rg_resp.get("ConsumedCapacity", 0),
            }
        except Exception as e:
            return {"name": rg_name, "type": rg_type, "rules": [], "error": str(e)}

    def _scan_region(self, region: str) -> list[dict]:
        firewalls = []
        try:
            client = self.client("network-firewall", region_name=region)
            paginator = client.get_paginator("list_firewalls")
            for page in paginator.paginate():
                for fw in page.get("Firewalls", []):
                    fw_name = fw.get("FirewallName", "")
                    detail = client.describe_firewall(FirewallName=fw_name)["Firewall"]
                    policy_arn = detail.get("FirewallPolicyArn", "")
                    policy = (
                        self._get_policy_details(client, policy_arn)
                        if policy_arn
                        else {}
                    )

                    # Get rule group details with correct type
                    rule_groups = []
                    for rg_ref in policy.get("rule_group_refs", []):
                        rg = self._get_rule_group(
                            client, rg_ref["name"], rg_ref["type"]
                        )
                        rule_groups.append(rg)

                    firewalls.append(
                        {
                            "region": region,
                            "name": fw_name,
                            "id": detail.get("FirewallId", ""),
                            "policy_arn": policy_arn,
                            "policy": policy,
                            "rule_groups": rule_groups,
                            "vpc_id": detail.get("VpcId", ""),
                            "subnets": [
                                m["SubnetId"] for m in detail.get("SubnetMappings", [])
                            ],
                            "logging": self._get_logging(client, fw_name),
                        }
                    )
        except Exception as e:
            logger.warning("Failed to discover Network Firewall in %s: %s", region, e)
        return firewalls

    def discover(self, regions: Optional[list[str]] = None) -> list[dict]:
        regions = regions or self.get_regions()
        all_fws = []
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=getattr(self, "max_workers", 10)
        ) as executor:
            futures = {executor.submit(self._scan_region, r): r for r in regions}
            for future in concurrent.futures.as_completed(futures):
                all_fws.extend(future.result())
        return sorted(all_fws, key=lambda f: (f["region"], f["name"]))


class ANFWDisplay(BaseDisplay):
    def show_list(self, firewalls: list[dict]):
        if not firewalls:
            self.console.print("[yellow]No Network Firewalls found[/]")
            return
        table = Table(title="Network Firewalls", show_header=True, header_style="bold")
        table.add_column("#", style="dim", justify="right")
        table.add_column("Region", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("VPC", style="yellow")
        table.add_column("Policy", style="white")
        table.add_column("Logging", style="dim")
        for i, fw in enumerate(firewalls, 1):
            log_status = "Yes" if fw.get("logging", {}).get("enabled") else "No"
            table.add_row(
                str(i),
                fw["region"],
                fw["name"],
                fw["vpc_id"],
                fw.get("policy", {}).get("name", "-"),
                log_status,
            )
        self.console.print(table)
        self.console.print(f"\n[dim]Total: {len(firewalls)} Network Firewall(s)[/]")

    def show_discovery(self, firewalls: list[dict]):
        self.show_list(firewalls)

    def show_firewall_detail(self, fw: dict):
        if not fw:
            self.console.print("[red]Firewall not found[/]")
            return
        tree = Tree(f"[bold blue]🔥 Network Firewall: {fw['name']}[/]")
        tree.add(f"[dim]ID: {fw['id']}[/]")
        tree.add(f"[dim]Region: {fw['region']}[/]")
        tree.add(f"[dim]VPC: {fw['vpc_id']}[/]")
        tree.add(f"[dim]Subnets: {', '.join(fw['subnets'])}[/]")

        log = fw.get("logging", {})
        if log.get("enabled"):
            log_branch = tree.add("[green]📝 Logging: Enabled[/]")
            log_branch.add(f"Types: {', '.join(log['types'])}")
            for dest in log["destinations"]:
                log_branch.add(f"[dim]{dest}[/]")
        else:
            tree.add("[red]📝 Logging: Disabled[/]")
        self.console.print(tree)
        self.console.print()

        if fw.get("policy"):
            self.console.print(
                Panel(f"[bold]{fw['policy'].get('name', 'N/A')}[/]", title="Policy")
            )
            if fw.get("rule_groups"):
                rg_table = Table(
                    title="Rule Groups", show_header=True, header_style="bold"
                )
                rg_table.add_column("#", style="dim", justify="right")
                rg_table.add_column("Name", style="cyan")
                rg_table.add_column("Type", style="yellow")
                rg_table.add_column("Rules", style="white", justify="right")
                rg_table.add_column("Capacity", style="dim", justify="right")
                for i, rg in enumerate(fw["rule_groups"], 1):
                    rg_table.add_row(
                        str(i),
                        rg["name"],
                        rg["type"],
                        str(len(rg.get("rules", []))),
                        f"{rg.get('consumed_capacity', 0)}/{rg.get('capacity', 0)}",
                    )
                self.console.print(rg_table)

    def show_policies(self, firewalls: list[dict]):
        for fw in firewalls:
            if not fw.get("policy"):
                continue
            title = f"[bold]{fw['name']}[/] → [cyan]{fw['region']}[/] → [magenta]{fw['policy'].get('name', 'N/A')}[/]"
            table = Table(title=title, show_header=True, header_style="bold")
            table.add_column("#", style="dim", justify="right")
            table.add_column("Type", style="yellow")
            table.add_column("Rule Group", style="cyan")
            table.add_column("Rules", style="white", justify="right")
            table.add_column("Capacity", style="dim", justify="right")
            for i, rg in enumerate(fw.get("rule_groups", []), 1):
                table.add_row(
                    str(i),
                    rg["type"],
                    rg["name"],
                    str(len(rg.get("rules", []))),
                    f"{rg.get('consumed_capacity', 0)}/{rg.get('capacity', 0)}",
                )
            stateless_defaults = fw["policy"].get("stateless_default_actions", {})
            if stateless_defaults:
                # Handle both old (list) and new (dict) formats for backwards compatibility
                if isinstance(stateless_defaults, dict):
                    full_packets = stateless_defaults.get("full_packets", [])
                    actions_str = ", ".join(full_packets) if full_packets else "N/A"
                else:
                    # Legacy list format
                    actions_str = ", ".join(stateless_defaults)
                table.add_row(
                    "-",
                    "DEFAULT",
                    "Stateless Default",
                    actions_str,
                    "",
                )
            self.console.print(table)
            self.console.print()

    def show_rule_group(self, firewalls: list[dict], group_ref: str):
        for fw in firewalls:
            rg = resolve_item(fw.get("rule_groups", []), group_ref, "name", "name")
            if rg:
                self.console.print(
                    Panel(
                        f"[bold]{rg['name']}[/] ({rg['type']})",
                        title=f"Rule Group - {fw['name']}",
                    )
                )

                if rg.get("error"):
                    self.console.print(f"[red]Error: {rg['error']}[/]")
                    return

                cap_info = f"[dim]Capacity: {rg.get('consumed_capacity', 0)}/{rg.get('capacity', 0)}[/]"
                self.console.print(cap_info)
                self.console.print()

                if rg["type"] == "STATEFUL":
                    for i, rule in enumerate(rg.get("rules", []), 1):
                        if "rule" in rule:
                            self.console.print(
                                f"  [dim]{i}.[/] [cyan]{rule['rule']}[/]"
                            )
                else:
                    # Stateless rules
                    table = Table(show_header=True, header_style="bold")
                    table.add_column("#", style="dim", justify="right")
                    table.add_column("Priority", style="yellow", justify="right")
                    table.add_column("Actions", style="green")
                    table.add_column("Sources", style="cyan")
                    table.add_column("Destinations", style="magenta")
                    table.add_column("Protocols", style="white")
                    for i, rule in enumerate(rg.get("rules", []), 1):
                        table.add_row(
                            str(i),
                            str(rule.get("priority", "")),
                            ", ".join(rule.get("actions", [])),
                            ", ".join(rule.get("sources", [])) or "Any",
                            ", ".join(rule.get("destinations", [])) or "Any",
                            ", ".join(str(p) for p in rule.get("protocols", []))
                            or "Any",
                        )
                    self.console.print(table)

                if not rg.get("rules"):
                    self.console.print("[dim]No rules found[/]")
                return
        self.console.print(f"[yellow]Rule group '{group_ref}' not found[/]")


def resolve_item(
    items: list[dict], ref: str, name_key: str, id_key: str
) -> Optional[dict]:
    """Resolve item by index (1-based), name, or ID"""
    if ref.isdigit():
        idx = int(ref) - 1
        if 0 <= idx < len(items):
            return items[idx]
    for item in items:
        if item.get(id_key) == ref:
            return item
    for item in items:
        if item.get(name_key) and item[name_key].lower() == ref.lower():
            return item
    return None


def resolve_firewall(firewalls: list[dict], ref: str) -> Optional[dict]:
    return resolve_item(firewalls, ref, "name", "id")
