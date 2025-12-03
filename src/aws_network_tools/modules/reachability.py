"""Reachability Analyzer module"""

import time
from typing import Optional, Dict, Any
import boto3
from rich.tree import Tree
from rich.panel import Panel

from ..core import Cache, BaseDisplay, BaseClient, ModuleInterface, run_with_spinner
from ..core.ip_resolver import IpResolver

cache = Cache("reachability")


class ReachabilityModule(ModuleInterface):
    @property
    def name(self) -> str:
        return "reachability-analyzer"

    @property
    def commands(self) -> Dict[str, str]:
        return {
            "reachability-analyzer": "Trace path between resources: reachability-analyzer <source-id|ip> <dest-id|ip> [tcp|udp] [port]",
        }

    def execute(self, shell: Any, command: str, args: str):
        if command == "reachability-analyzer":
            parts = args.split()
            if len(parts) < 2:
                shell.console.print(
                    "[red]Usage: reachability-analyzer <source-id|ip> <dest-id|ip> [tcp|udp] [port][/]"
                )
                return

            source = parts[0]
            dest = parts[1]
            protocol = parts[2] if len(parts) > 2 else "tcp"
            port = int(parts[3]) if len(parts) > 3 else 80

            self._run_trace(shell, source, dest, protocol, port)

    def _resolve_if_ip(self, shell, target: str) -> Optional[str]:
        # Simple heuristic: if it looks like an IP (contains dots), try to resolve
        if "." in target and not target.startswith("eni-"):
            resolver = IpResolver(shell.profile)
            # Use shell regions if set, otherwise default to list including common ones or let resolver handle it
            # The shell.regions might be empty (all regions implied) or specific.
            # IpResolver expects a list of regions.
            regions = (
                shell.regions
                if shell.regions
                else ["us-east-1", "eu-west-1", "eu-west-2", "us-west-2"]
            )

            resolved_id = run_with_spinner(
                lambda: resolver.resolve_ip(target, regions),
                f"Resolving IP {target}",
                console=shell.console,
            )

            if resolved_id:
                shell.console.print(f"[green]Resolved {target} to {resolved_id}[/]")
                return resolved_id
            else:
                shell.console.print(f"[red]Could not resolve IP {target} to an ENI.[/]")
                return None

    def _run_trace(self, shell, source, dest, protocol, port):
        # Resolve IPs if necessary
        source_id = self._resolve_if_ip(shell, source)
        if not source_id:
            return

        dest_id = self._resolve_if_ip(shell, dest)
        if not dest_id:
            return

        client = ReachabilityClient(shell.profile)

        try:
            # 1. Create Path
            path_id = run_with_spinner(
                lambda: client.create_path(source_id, dest_id, protocol, port),
                f"Creating analysis path {source_id} -> {dest_id}",
                console=shell.console,
            )

            # 2. Start Analysis
            analysis_id = run_with_spinner(
                lambda: client.start_analysis(path_id),
                "Starting reachability analysis",
                console=shell.console,
            )

            # 3. Wait for results
            result = run_with_spinner(
                lambda: client.wait_for_analysis(analysis_id),
                "Analyzing network path (this usually takes 30-60s)",
                console=shell.console,
            )

            # 4. Display
            ReachabilityDisplay(shell.console).show_analysis(result)

        except Exception as e:
            shell.console.print(f"[red]Debug: Caught exception type: {type(e)}[/]")
            shell.console.print(f"[red]Trace failed: {str(e)}[/]")
            self._suggest_cloudwan_check(shell)

    def _suggest_cloudwan_check(self, shell):
        shell.console.print(
            "[yellow]Note:[/yellow] AWS Network Insights Path may not fully support paths involving Cloud WAN."
        )
        shell.console.print(
            "[yellow]Consider:[/yellow] Manually verifying Cloud WAN configuration using: [cyan]global-network[/], [cyan]core-network[/] (and sub-commands like [cyan]show policy-documents[/], [cyan]show route-tables[/]) to inspect routing and policies."
        )


class ReachabilityClient(BaseClient):
    def __init__(
        self, profile: Optional[str] = None, session: Optional[boto3.Session] = None
    ):
        super().__init__(profile, session)

    def _get_region(self):
        return self.session.region_name or "us-east-1"

    def create_path(self, source: str, dest: str, protocol: str, port: int) -> str:
        ec2 = self.session.client("ec2")  # Uses default region from profile/config

        try:
            resp = ec2.create_network_insights_path(
                Source=source,
                Destination=dest,
                Protocol=protocol.lower(),
                DestinationPort=port,
                TagSpecifications=[
                    {
                        "ResourceType": "network-insights-path",
                        "Tags": [
                            {"Key": "Name", "Value": f"cli-trace-{source}-{dest}"}
                        ],
                    }
                ],
            )
            return resp["NetworkInsightsPath"]["NetworkInsightsPathId"]
        except Exception as e:
            raise Exception(f"Failed to create path: {e}")

    def start_analysis(self, path_id: str) -> str:
        ec2 = self.session.client("ec2")
        try:
            resp = ec2.start_network_insights_analysis(
                NetworkInsightsPathId=path_id,
                TagSpecifications=[
                    {
                        "ResourceType": "network-insights-analysis",
                        "Tags": [{"Key": "Name", "Value": f"cli-analysis-{path_id}"}],
                    }
                ],
            )
            return resp["NetworkInsightsAnalysis"]["NetworkInsightsAnalysisId"]
        except Exception as e:
            raise Exception(f"Failed to start analysis: {e}")

    def wait_for_analysis(self, analysis_id: str) -> Optional[dict]:
        ec2 = self.session.client("ec2")
        while True:
            resp = ec2.describe_network_insights_analyses(
                NetworkInsightsAnalysisIds=[analysis_id]
            )
            analysis = resp["NetworkInsightsAnalyses"][0]
            status = analysis["Status"]

            if status == "succeeded":
                return analysis
            elif status == "failed":
                return analysis  # Return failed analysis to show why

            time.sleep(2)


class ReachabilityDisplay(BaseDisplay):
    def show_analysis(self, analysis: dict):
        if not analysis:
            self.console.print("[red]No analysis result[/]")
            return

        status = analysis["NetworkInPath"]
        status_color = "green" if status else "red"
        status_text = "REACHABLE" if status else "UNREACHABLE"

        self.console.print(
            Panel(
                f"[bold {status_color}]Result: {status_text}[/]",
                title="Trace Path Result",
                border_style=status_color,
            )
        )

        # Hop-by-hop analysis
        if analysis.get("ForwardPathComponents"):
            tree = Tree("[bold]Forward Path[/]")
            self._build_hop_tree(tree, analysis["ForwardPathComponents"])
            self.console.print(tree)
            self.console.print()

        # Explanations for failure
        if analysis.get("Explanations"):
            self.console.print("[bold red]Issues Found:[/]")
            for expl in analysis["Explanations"]:
                code = expl.get("ExplanationCode", "Unknown")
                # direction = expl.get("Direction", "ingress")  # Not used

                # Get the relevant component
                comp = (
                    expl.get("Acl")
                    or expl.get("SecurityGroup")
                    or expl.get("NetworkInterface")
                    or {}
                )
                comp_id = comp.get("Id", "Unknown")
                comp_name = next(
                    (t["Value"] for t in comp.get("Tags", []) if t["Key"] == "Name"),
                    comp_id,
                )

                msg = f"[red]• {code}[/]: {comp_name} ({comp_id})"
                self.console.print(msg)

    def _build_hop_tree(self, tree, components):
        for comp in components:
            resource = comp.get("Component", {})
            res_id = resource.get("Id", "Unknown")
            res_type = resource.get("Type", "Unknown")
            # Try to get a name if present in tags (not always returned here, might need separate lookup)
            # Simplified for now

            label = f"[{res_type}] [cyan]{res_id}[/]"

            # Additional info
            details = []
            if comp.get("AclRule"):
                rule = comp["AclRule"]
                action = rule.get("RuleAction", "unknown")
                color = "green" if action == "allow" else "red"
                details.append(
                    f"NACL Rule #{rule.get('RuleNumber')}: [{color}]{action.upper()}[/]"
                )

            if comp.get("SecurityGroupRule"):
                # SG info is minimal in response
                details.append("Security Group Rule Match")

            if comp.get("RouteTableRoute"):
                route = comp["RouteTableRoute"]
                details.append(
                    f"Route: {route.get('DestinationCidrBlock')} -> {route.get('GatewayId') or route.get('InstanceId')}"
                )

            if details:
                label += f" ({', '.join(details)})"

            tree.add(label)
