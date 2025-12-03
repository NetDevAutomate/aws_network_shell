"""ELB module for Application and Network Load Balancers"""

import concurrent.futures
from typing import Optional, Dict, List
import boto3
from rich.table import Table
from rich.tree import Tree

from ..core import (
    Cache,
    BaseDisplay,
    BaseClient,
    ModuleInterface,
    run_with_spinner,
    Context,
)

cache = Cache("elb")


class ELBModule(ModuleInterface):
    @property
    def name(self) -> str:
        return "elb"

    @property
    def commands(self) -> Dict[str, str]:
        return {"elb": "Enter Load Balancer context: elb <#|name|arn>"}

    @property
    def context_commands(self) -> Dict[str, List[str]]:
        return {
            "elb": ["target-group"],
        }

    @property
    def show_commands(self) -> Dict[str, List[str]]:
        return {None: ["elbs"], "elb": ["detail", "listeners", "targets"]}

    def complete_elb(self, text, line, begidx, endidx):
        """Tab completion for elb command"""
        data = cache.get(ignore_expiry=True)
        if not data:
            return []

        candidates = []
        for item in data:
            candidates.append(item["arn"])
            if item.get("name"):
                candidates.append(item["name"])

        return [c for c in candidates if c.startswith(text)]

    def execute(self, shell, command: str, args: str):
        """Enter ELB context"""
        if shell.ctx_type is not None:
            shell.console.print("[red]Use 'end' to return to top level first[/]")
            return

        ref = args.strip()
        if not ref:
            shell.console.print("[red]Usage: elb <#|name|arn>[/]")
            return

        elbs = shell._get_elbs()
        target = resolve_elb(elbs, ref)

        if not target:
            shell.console.print(f"[red]Load Balancer '{ref}' not found[/]")
            return

        client = ELBClient(shell.profile)
        detail = run_with_spinner(
            lambda: client.get_elb_detail(target["arn"], target["region"]),
            "Fetching Load Balancer details",
            console=shell.console,
        )

        shell.context_stack = [
            Context("elb", ref, target.get("name") or target["arn"], detail)
        ]
        shell._update_prompt()


class ELBClient(BaseClient):
    def __init__(
        self, profile: Optional[str] = None, session: Optional[boto3.Session] = None
    ):
        super().__init__(profile, session)

    def get_regions(self) -> list[str]:
        try:
            region = self.session.region_name or "us-east-1"
            ec2 = self.session.client("ec2", region_name=region)
            resp = ec2.describe_regions(AllRegions=False)
            return [r["RegionName"] for r in resp["Regions"]]
        except Exception:
            if self.session.region_name:
                return [self.session.region_name]
            return []

    def _scan_region(self, region: str) -> list[dict]:
        elbs = []
        try:
            client = self.session.client("elbv2", region_name=region)
            paginator = client.get_paginator("describe_load_balancers")
            for page in paginator.paginate():
                for lb in page["LoadBalancers"]:
                    elbs.append(
                        {
                            "arn": lb["LoadBalancerArn"],
                            "name": lb["LoadBalancerName"],
                            "dns_name": lb["DNSName"],
                            "type": lb["Type"],
                            "scheme": lb["Scheme"],
                            "vpc_id": lb.get("VpcId"),
                            "state": lb["State"]["Code"],
                            "azs": [
                                az["ZoneName"] for az in lb.get("AvailabilityZones", [])
                            ],
                            "region": region,
                        }
                    )
        except Exception:
            pass
        return elbs

    def discover(self, regions: Optional[list[str]] = None) -> list[dict]:
        regions = regions or self.get_regions()
        all_elbs = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(self._scan_region, r): r for r in regions}
            for future in concurrent.futures.as_completed(futures):
                all_elbs.extend(future.result())
        return sorted(all_elbs, key=lambda x: (x["region"], x["name"]))

    def get_elb_detail(self, elb_arn: str, region: str) -> dict:
        client = self.session.client("elbv2", region_name=region)

        # Get basic info
        resp = client.describe_load_balancers(LoadBalancerArns=[elb_arn])
        if not resp["LoadBalancers"]:
            return {}
        lb = resp["LoadBalancers"][0]

        detail = {
            "arn": lb["LoadBalancerArn"],
            "name": lb["LoadBalancerName"],
            "dns_name": lb["DNSName"],
            "type": lb["Type"],
            "scheme": lb["Scheme"],
            "vpc_id": lb.get("VpcId"),
            "state": lb["State"]["Code"],
            "azs": [az["ZoneName"] for az in lb.get("AvailabilityZones", [])],
            "region": region,
            "listeners": [],
        }

        # Get Listeners
        try:
            listeners_resp = client.describe_listeners(LoadBalancerArn=elb_arn)
            for listener in listeners_resp.get("Listeners", []):
                listener = {
                    "arn": listener["ListenerArn"],
                    "port": listener["Port"],
                    "protocol": listener["Protocol"],
                    "ssl_certs": listener.get("Certificates", []),
                    "default_actions": [],
                    "rules": [],  # Only for ALB
                }

                # Process default actions
                for action in listener.get("DefaultActions", []):
                    act = {
                        "type": action["Type"],
                        "target_group_arn": action.get("TargetGroupArn"),
                    }
                    if act["target_group_arn"]:
                        act["target_group"] = self._get_target_group_detail(
                            client, act["target_group_arn"]
                        )
                    listener["default_actions"].append(act)

                # If ALB, get rules (optional but good for completeness if we want full path)
                if lb["Type"] == "application":
                    rules_resp = client.describe_rules(
                        ListenerArn=listener["ListenerArn"]
                    )
                    for r in rules_resp.get("Rules", []):
                        if r["IsDefault"]:
                            continue  # Skip default rule as it's covered in DefaultActions usually
                        rule = {
                            "arn": r["RuleArn"],
                            "priority": r["Priority"],
                            "conditions": r.get("Conditions", []),
                            "actions": [],
                        }
                        for action in r.get("Actions", []):
                            act = {
                                "type": action["Type"],
                                "target_group_arn": action.get("TargetGroupArn"),
                            }
                            if act["target_group_arn"]:
                                act["target_group"] = self._get_target_group_detail(
                                    client, act["target_group_arn"]
                                )
                            rule["actions"].append(act)
                        listener["rules"].append(rule)

                detail["listeners"].append(listener)
        except Exception:
            # Log or handle error
            pass

        return detail

    def _get_target_group_detail(self, client, tg_arn: str) -> dict:
        # Get TG info
        try:
            tg_resp = client.describe_target_groups(TargetGroupArns=[tg_arn])
            if not tg_resp["TargetGroups"]:
                return {"arn": tg_arn, "error": "Not found"}
            tg = tg_resp["TargetGroups"][0]

            result = {
                "arn": tg["TargetGroupArn"],
                "name": tg["TargetGroupName"],
                "protocol": tg.get("Protocol"),
                "port": tg.get("Port"),
                "vpc_id": tg.get("VpcId"),
                "target_type": tg["TargetType"],
                "targets": [],
            }

            # Get Target Health
            health_resp = client.describe_target_health(TargetGroupArn=tg_arn)
            for th in health_resp.get("TargetHealthDescriptions", []):
                target = th["Target"]
                health = th["TargetHealth"]
                result["targets"].append(
                    {
                        "id": target["Id"],
                        "port": target.get("Port"),
                        "az": target.get("AvailabilityZone"),
                        "state": health["State"],
                        "reason": health.get("Reason"),
                        "description": health.get("Description"),
                    }
                )
            return result
        except Exception:
            return {"arn": tg_arn, "error": "Error fetching details"}


class ELBDisplay(BaseDisplay):
    def show_elbs_list(self, elbs: list[dict]):
        if not elbs:
            self.console.print("[yellow]No Load Balancers found[/]")
            return
        table = Table(title="Load Balancers", show_header=True, header_style="bold")
        table.add_column("#", style="dim", justify="right")
        table.add_column("Region", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Scheme", style="white")
        table.add_column("VPC", style="blue")
        table.add_column("State", style="magenta")
        table.add_column("DNS Name", style="dim")

        for i, lb in enumerate(elbs, 1):
            table.add_row(
                str(i),
                lb["region"],
                lb["name"],
                lb["type"],
                lb["scheme"],
                lb.get("vpc_id") or "-",
                lb["state"],
                lb["dns_name"],
            )
        self.console.print(table)
        self.console.print(f"\n[dim]Total: {len(elbs)} Load Balancer(s)[/]")

    def show_elb_detail(self, elb: dict):
        if not elb:
            self.console.print("[red]Load Balancer not found[/]")
            return

        tree = Tree(f"[bold blue]⚖️  Load Balancer: {elb['name']}[/]")

        # Attributes
        attrs = tree.add("[dim]Attributes[/]")
        attrs.add(f"ARN: {elb['arn']}")
        attrs.add(f"DNS: {elb['dns_name']}")
        attrs.add(f"Type: {elb['type']}")
        attrs.add(f"Scheme: {elb['scheme']}")
        attrs.add(f"VPC: {elb.get('vpc_id')}")
        attrs.add(f"State: {elb['state']}")
        attrs.add(f"AZs: {', '.join(elb.get('azs', []))}")

        # Listeners
        listeners_node = tree.add("[yellow]👂 Listeners[/]")
        for listener in elb.get("listeners", []):
            l_node = listeners_node.add(
                f"[bold]{listener['protocol']}:{listener['port']}[/] ({listener['arn'].split('/')[-1]})"
            )

            # Default Actions
            if listener.get("default_actions"):
                da_node = l_node.add("Default Actions")
                for action in listener["default_actions"]:
                    self._add_action_node(da_node, action)

            # Rules (for ALB)
            if listener.get("rules"):
                rules_node = l_node.add("Rules")
                for r in listener["rules"]:
                    # Format conditions
                    conds = []
                    for c in r.get("conditions", []):
                        field = c.get("Field")
                        values = c.get("Values", [])
                        if not values and "HostHeaderConfig" in c:
                            values = c["HostHeaderConfig"].get("Values", [])
                        elif not values and "PathPatternConfig" in c:
                            values = c["PathPatternConfig"].get("Values", [])
                        conds.append(f"{field}={values}")

                    r_node = rules_node.add(
                        f"Priority {r['priority']}: {', '.join(conds)}"
                    )
                    for action in r.get("actions", []):
                        self._add_action_node(r_node, action)

        self.console.print(tree)

    def _add_action_node(self, parent, action):
        if action["type"] == "forward" and action.get("target_group"):
            tg = action["target_group"]
            if tg.get("error"):
                parent.add(f"[red]Error fetching target group: {tg['error']}[/]")
                return

            tg_node = parent.add(
                f"[cyan]➡️  Forward to {tg['name']}[/] ({tg['protocol']}:{tg['port']})"
            )

            # Targets
            if tg.get("targets"):
                for t in tg["targets"]:
                    color = "green" if t["state"] == "healthy" else "red"
                    icon = "✅" if t["state"] == "healthy" else "❌"
                    if t["state"] == "draining":
                        color = "yellow"
                        icon = "⚠️"

                    t_text = (
                        f"{icon} [{color}]{t['id']}:{t.get('port')}[/] ({t['state']})"
                    )
                    if t.get("reason"):
                        t_text += f" - {t['reason']}"
                    tg_node.add(t_text)
            else:
                tg_node.add("[dim]No targets registered[/]")
        else:
            parent.add(f"[dim]Action: {action['type']}[/]")

    def show_listeners(self, elb: dict):
        if not elb or not elb.get("listeners"):
            self.console.print("[yellow]No listeners found[/]")
            return

        table = Table(
            title=f"Listeners for {elb['name']}", show_header=True, header_style="bold"
        )
        table.add_column("Protocol", style="cyan")
        table.add_column("Port", style="green")
        table.add_column("SSL Certs", style="yellow")
        table.add_column("Default Action", style="white")

        for listener in elb["listeners"]:
            certs = len(listener.get("ssl_certs", []))
            actions = []
            for a in listener.get("default_actions", []):
                if a["type"] == "forward" and a.get("target_group"):
                    actions.append(f"Forward to {a['target_group']['name']}")
                else:
                    actions.append(a["type"])

            table.add_row(
                listener["protocol"],
                str(listener["port"]),
                str(certs) if certs else "-",
                ", ".join(actions),
            )
        self.console.print(table)

    def show_targets(self, elb: dict):
        if not elb:
            return

        tree = Tree(f"[bold blue]🎯 Targets for {elb['name']}[/]")

        for listener in elb.get("listeners", []):
            # Check default actions
            for a in listener.get("default_actions", []):
                if a["type"] == "forward" and a.get("target_group"):
                    self._add_target_group_node(tree, a["target_group"])

            # Check rules
            for r in listener.get("rules", []):
                for a in r.get("actions", []):
                    if a["type"] == "forward" and a.get("target_group"):
                        self._add_target_group_node(tree, a["target_group"])

        self.console.print(tree)

    def _add_target_group_node(self, parent, tg):
        if tg.get("error"):
            parent.add(f"[red]Error fetching target group: {tg['error']}[/]")
            return

        tg_node = parent.add(f"[cyan]{tg['name']}[/] ({tg['protocol']}:{tg['port']})")

        if tg.get("targets"):
            for t in tg["targets"]:
                color = "green" if t["state"] == "healthy" else "red"
                icon = "✅" if t["state"] == "healthy" else "❌"
                if t["state"] == "draining":
                    color = "yellow"
                    icon = "⚠️"

                t_text = f"{icon} [{color}]{t['id']}:{t.get('port')}[/] ({t['state']})"
                if t.get("reason"):
                    t_text += f" - {t['reason']}"
                tg_node.add(t_text)
        else:
            tg_node.add("[dim]No targets registered[/]")


def resolve_elb(elbs: list[dict], ref: str) -> Optional[dict]:
    """Resolve ELB by index (1-based), name, or ARN"""
    if ref.isdigit():
        idx = int(ref) - 1
        if 0 <= idx < len(elbs):
            return elbs[idx]
    for elb in elbs:
        if elb["arn"] == ref:
            return elb
    for elb in elbs:
        if elb["name"].lower() == ref.lower():
            return elb
    return None
