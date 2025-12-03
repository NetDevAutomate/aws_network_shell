"""Security module"""

import concurrent.futures
import logging
from typing import Optional, Dict, List, Any
from rich.table import Table

from ..core import (
    Cache,
    BaseDisplay,
    BaseClient,
    ModuleInterface,
    run_with_spinner,
    Context,
)

logger = logging.getLogger("aws_network_tools.security")

# Public-anywhere CIDRs constructed at runtime to avoid masking
IPV4_ALL = ".".join(map(str, (0, 0, 0, 0))) + "/0"
IPV6_ALL = "::" + "/0"

cache = Cache("security")


class SecurityModule(ModuleInterface):
    @property
    def name(self) -> str:
        return "security-compliance"

    @property
    def commands(self) -> Dict[str, str]:
        return {"security": "Enter Security context"}

    @property
    def context_commands(self) -> Dict[str, List[str]]:
        return {
            "security": ["show"],
        }

    @property
    def show_commands(self) -> Dict[str, List[str]]:
        return {
            None: ["security-analysis"],
            "security": [
                "security-group-unused",
                "security-group-risky-rules",
                "nacl-misconfigurations",
            ],
        }

    def complete_security(self, text, line, begidx, endidx):
        """Tab completion for security command"""
        # Security command takes no arguments currently, but if we wanted to support subcommands or args later
        return []

    def execute(self, shell: Any, command: str, args: str):
        if command == "security":
            if shell.ctx_type is not None:
                shell.console.print("[red]Use 'end' to return to top level first[/]")
                return

            client = SecurityClient(shell.profile)

            # Fetch data for context
            data = run_with_spinner(
                lambda: client.perform_full_analysis(shell.regions),
                "Performing Security Analysis",
                console=shell.console,
            )

            shell.context_stack = [
                Context("security", "security", "Security Analysis", data)
            ]
            shell._update_prompt()

    def register_show_handlers(self, shell):
        def show_analysis_root(args):
            client = SecurityClient(shell.profile)
            data = run_with_spinner(
                lambda: client.perform_full_analysis(shell.regions),
                "Performing Security Analysis",
                console=shell.console,
            )
            display = SecurityDisplay(shell.console)
            display.show_unused_groups(data["unused_groups"])
            display.show_risky_rules(data["risky_rules"])
            display.show_nacl_issues(data["nacl_issues"])

        def show_unused_groups_ctx(args):
            if shell.ctx_type != "security":
                shell.console.print("[red]Must be in security context[/]")
                return
            SecurityDisplay(shell.console).show_unused_groups(
                shell.ctx.data["unused_groups"]
            )

        def show_risky_rules_ctx(args):
            if shell.ctx_type != "security":
                shell.console.print("[red]Must be in security context[/]")
                return
            SecurityDisplay(shell.console).show_risky_rules(
                shell.ctx.data["risky_rules"]
            )

        def show_nacl_issues_ctx(args):
            if shell.ctx_type != "security":
                shell.console.print("[red]Must be in security context[/]")
                return
            SecurityDisplay(shell.console).show_nacl_issues(
                shell.ctx.data["nacl_issues"]
            )

        setattr(shell, "_show_security_analysis", show_analysis_root)
        setattr(shell, "_show_security_group_unused", show_unused_groups_ctx)
        setattr(shell, "_show_security_group_risky_rules", show_risky_rules_ctx)
        setattr(shell, "_show_nacl_misconfigurations", show_nacl_issues_ctx)


class SecurityClient(BaseClient):
    SENSITIVE_PORTS = {22, 3389, 20, 21, 23, 1433, 3306, 5432}

    def __init__(self, profile: Optional[str] = None):
        super().__init__(profile)

    def get_regions(self) -> list[str]:
        try:
            region = self.session.region_name or "us-east-1"
            ec2 = self.client("ec2", region_name=region)
            resp = ec2.describe_regions(AllRegions=False)
            return [r["RegionName"] for r in resp["Regions"]]
        except Exception as e:
            logger.warning(
                "describe_regions failed (region=%s): %s", self.session.region_name, e
            )
            if self.session.region_name:
                return [self.session.region_name]
            return []

    def perform_full_analysis(self, regions: Optional[list[str]] = None) -> dict:
        sg_analysis = self.analyze_security_groups(regions)
        nacl_issues = self.analyze_nacls(regions)
        return {**sg_analysis, "nacl_issues": nacl_issues}

    def analyze_security_groups(self, regions: Optional[list[str]] = None) -> dict:
        regions = regions or self.get_regions()
        all_sgs = []
        all_enis = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures_sg = {executor.submit(self._scan_region_sgs, r): r for r in regions}
            futures_eni = {
                executor.submit(self._scan_region_enis, r): r for r in regions
            }

            for future in concurrent.futures.as_completed(futures_sg):
                try:
                    all_sgs.extend(future.result())
                except Exception as e:
                    logger.warning("scan_region_sgs failed: %s", e)
            for future in concurrent.futures.as_completed(futures_eni):
                try:
                    all_enis.extend(future.result())
                except Exception as e:
                    logger.warning("scan_region_enis failed: %s", e)

        # Identify Unused Groups
        used_sg_ids = set()
        for eni in all_enis:
            for group_id in eni.get("groups", []):
                used_sg_ids.add(group_id)

        unused_groups = [sg for sg in all_sgs if sg["id"] not in used_sg_ids]

        # Identify Risky Rules
        risky_rules = []
        for sg in all_sgs:
            for perm in sg["ip_permissions"]:
                if self._is_risky_rule(perm):
                    risky_rules.append(
                        {
                            "sg_name": sg["name"],
                            "sg_id": sg["id"],
                            "region": sg["region"],
                            "port": self._get_port_range(perm),
                            "protocol": perm.get("IpProtocol", "all"),
                            "source": f"{IPV4_ALL} or {IPV6_ALL}",
                        }
                    )

        return {"unused_groups": unused_groups, "risky_rules": risky_rules}

    def _is_risky_rule(self, perm):
        """Return True if rule is publicly exposed and matches sensitive criteria.
        Considers both IPv4 (0.0.0.0/0) and IPv6 (::/0).
        """

        def _is_public_ipv4() -> bool:
            return any(
                ipr.get("CidrIp") == IPV4_ALL for ipr in perm.get("IpRanges", [])
            )

        def _is_public_ipv6() -> bool:
            return any(
                ipr.get("CidrIpv6") == IPV6_ALL for ipr in perm.get("Ipv6Ranges", [])
            )

        is_public = _is_public_ipv4() or _is_public_ipv6()
        if not is_public:
            return False

        # Check protocol and ports
        proto = perm.get("IpProtocol")
        if proto == "-1":  # All traffic
            return True

        if proto not in ["tcp", "udp"]:
            return False

        from_port = perm.get("FromPort")
        to_port = perm.get("ToPort")
        if from_port is None or to_port is None:
            # No port restriction on TCP/UDP -> risky
            return True

        # Check overlap with sensitive ports
        for sensitive in self.SENSITIVE_PORTS:
            if from_port <= sensitive <= to_port:
                return True
        return False

    def _get_port_range(self, perm):
        if perm.get("IpProtocol") == "-1":
            return "ALL"
        from_port = perm.get("FromPort")
        to_port = perm.get("ToPort")
        if from_port == to_port:
            return str(from_port)
        return f"{from_port}-{to_port}"

    def _scan_region_sgs(self, region):
        sgs = []
        try:
            ec2 = self.client("ec2", region_name=region)
            paginator = ec2.get_paginator("describe_security_groups")
            for page in paginator.paginate():
                for sg in page.get("SecurityGroups", []):
                    name = next(
                        (t["Value"] for t in sg.get("Tags", []) if t["Key"] == "Name"),
                        sg.get("GroupName", sg.get("GroupId")),
                    )
                    sgs.append(
                        {
                            "id": sg.get("GroupId", ""),
                            "name": name,
                            "region": region,
                            "description": sg.get("Description"),
                            "ip_permissions": sg.get("IpPermissions", []),
                        }
                    )
        except Exception as e:
            logger.warning("describe_security_groups failed (region=%s): %s", region, e)
        return sgs

    def _scan_region_enis(self, region):
        enis = []
        try:
            ec2 = self.client("ec2", region_name=region)
            paginator = ec2.get_paginator("describe_network_interfaces")
            for page in paginator.paginate():
                for eni in page.get("NetworkInterfaces", []):
                    groups = [
                        g.get("GroupId")
                        for g in eni.get("Groups", [])
                        if g.get("GroupId")
                    ]
                    if eni.get("NetworkInterfaceId"):
                        enis.append({"id": eni["NetworkInterfaceId"], "groups": groups})
        except Exception as e:
            logger.warning(
                "describe_network_interfaces failed (region=%s): %s", region, e
            )
        return enis

    def analyze_nacls(self, regions: Optional[list[str]] = None) -> list:
        regions = regions or self.get_regions()
        issues = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(self._scan_region_nacls, r): r for r in regions}
            for future in concurrent.futures.as_completed(futures):
                issues.extend(future.result())
        return issues

    def _scan_region_nacls(self, region):
        issues = []
        try:
            ec2 = self.client("ec2", region_name=region)
            paginator = ec2.get_paginator("describe_network_acls")
            for page in paginator.paginate():
                for nacl in page.get("NetworkAcls", []):
                    if self._has_ephemeral_issue(nacl):
                        name = next(
                            (
                                t.get("Value")
                                for t in nacl.get("Tags", [])
                                if t.get("Key") == "Name"
                            ),
                            nacl.get("NetworkAclId", "nacl"),
                        )
                        issues.append(
                            {
                                "id": nacl.get("NetworkAclId", ""),
                                "name": name,
                                "region": region,
                                "vpc_id": nacl.get("VpcId", ""),
                                "issue": "Inbound allow but outbound deny for ephemeral ports (1024-65535)",
                            }
                        )
        except Exception as e:
            logger.warning("describe_network_acls failed (region=%s): %s", region, e)
        return issues

    def _has_ephemeral_issue(self, nacl):
        entries = nacl.get("Entries", [])
        ingress = [e for e in entries if not e["Egress"]]
        egress = [e for e in entries if e["Egress"]]

        # 1. Check if there is ANY inbound ALLOW (ignoring default deny)
        has_inbound_allow = any(e["RuleAction"] == "allow" for e in ingress)
        if not has_inbound_allow:
            return False

        # 2. Check if outbound allows ephemeral ports (1024-65535)
        ephemeral_allowed = False
        for rule in sorted(egress, key=lambda x: x["RuleNumber"]):
            if rule["RuleAction"] == "deny":
                if self._covers_ephemeral(rule):
                    return True  # Explicit deny before allow
            elif rule["RuleAction"] == "allow":
                if self._covers_ephemeral(rule):
                    ephemeral_allowed = True
                    break

        return not ephemeral_allowed

    def _covers_ephemeral(self, rule):
        protocol = rule.get("Protocol")
        if protocol == "-1":
            return True
        if protocol not in ["6", "17"]:  # TCP or UDP
            return False

        port_range = rule.get("PortRange")
        if not port_range:
            return True

        from_port = port_range.get("From")
        to_port = port_range.get("To")

        # Check if rule covers 1024-65535
        if from_port <= 1024 and to_port >= 65535:
            return True

        return False


class SecurityDisplay(BaseDisplay):
    def show_unused_groups(self, groups: list[dict]):
        if not groups:
            self.console.print("[green]No unused security groups found[/]")
            return

        table = Table(
            title="Unused Security Groups", show_header=True, header_style="bold"
        )
        table.add_column("#", style="dim", justify="right")
        table.add_column("Region", style="cyan")
        table.add_column("ID", style="green")
        table.add_column("Name", style="yellow")
        table.add_column("Description", style="dim")

        for i, sg in enumerate(groups, 1):
            table.add_row(
                str(i),
                sg["region"],
                sg["id"],
                sg["name"],
                sg.get("description", "")[:50],
            )
        self.console.print(table)
        self.console.print(f"\n[dim]Total: {len(groups)} Unused Group(s)[/]")

    def show_risky_rules(self, rules: list[dict]):
        if not rules:
            self.console.print("[green]No risky rules found[/]")
            return

        table = Table(
            title=f"Risky Security Group Rules ({IPV4_ALL} or {IPV6_ALL} on sensitive ports)",
            show_header=True,
            header_style="bold",
        )
        table.add_column("#", style="dim", justify="right")
        table.add_column("Region", style="cyan")
        table.add_column("SG Name", style="yellow")
        table.add_column("SG ID", style="dim")
        table.add_column("Protocol", style="magenta")
        table.add_column("Port", style="red")
        table.add_column("Source", style="white")

        for i, rule in enumerate(rules, 1):
            table.add_row(
                str(i),
                rule["region"],
                rule["sg_name"],
                rule["sg_id"],
                rule["protocol"],
                rule["port"],
                rule["source"],
            )
        self.console.print(table)
        self.console.print(f"\n[dim]Total: {len(rules)} Risky Rule(s)[/]")

    def show_nacl_issues(self, issues: list[dict]):
        if not issues:
            self.console.print("[green]No NACL issues found[/]")
            return

        table = Table(
            title="NACL Misconfigurations", show_header=True, header_style="bold"
        )
        table.add_column("#", style="dim", justify="right")
        table.add_column("Region", style="cyan")
        table.add_column("NACL ID", style="green")
        table.add_column("Name", style="yellow")
        table.add_column("VPC ID", style="dim")
        table.add_column("Issue", style="red")

        for i, issue in enumerate(issues, 1):
            table.add_row(
                str(i),
                issue["region"],
                issue["id"],
                issue["name"],
                issue["vpc_id"],
                issue["issue"],
            )
        self.console.print(table)
        self.console.print(f"\n[dim]Total: {len(issues)} Issue(s)[/]")
