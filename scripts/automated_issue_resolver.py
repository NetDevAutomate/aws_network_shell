#!/usr/bin/env python3
"""Automated Issue Resolution Workflow using issue_investigator.py agent prompts.

This script:
1. Fetches all open GitHub issues
2. For each issue, generates an agent prompt via issue_investigator.py
3. Executes the agent prompt to attempt resolution
4. Creates a test to validate the fix
5. Runs tests iteratively until pass
6. Creates a PR with the fix

Usage:
    # Process all open issues
    uv run python scripts/automated_issue_resolver.py --all

    # Process specific issue
    uv run python scripts/automated_issue_resolver.py --issue 9

    # Dry run (no changes)
    uv run python scripts/automated_issue_resolver.py --issue 9 --dry-run
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Any

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.panel import Panel
except ImportError:
    print("Rich required. Install: pip install rich")
    sys.exit(1)

console = Console()


@dataclass
class IssueResolutionResult:
    """Result of attempting to resolve an issue."""
    issue_number: int
    issue_title: str
    agent_prompt_generated: bool
    fix_attempted: bool
    tests_created: bool
    tests_passed: bool
    pr_created: bool
    error: str | None = None


class AutomatedIssueResolver:
    """Automates issue resolution using agent prompts from issue_investigator.py."""

    def __init__(self, dry_run: bool = False, verbose: bool = False):
        self.dry_run = dry_run
        self.verbose = verbose
        self.scripts_dir = Path(__file__).parent
        self.repo_root = self.scripts_dir.parent

    def resolve_issue(self, issue_number: int) -> IssueResolutionResult:
        """Attempt to resolve a specific issue automatically.

        Workflow:
        1. Generate agent prompt from issue
        2. Execute agent prompt (implement fix)
        3. Create test for the issue
        4. Run tests iteratively
        5. Create PR if successful
        """
        console.print(f"\n[bold blue]Resolving Issue #{issue_number}[/]")

        result = IssueResolutionResult(
            issue_number=issue_number,
            issue_title="",
            agent_prompt_generated=False,
            fix_attempted=False,
            tests_created=False,
            tests_passed=False,
            pr_created=False
        )

        try:
            # Step 1: Generate agent prompt
            console.print("[yellow]Step 1: Generating agent prompt...[/]")
            agent_prompt = self._generate_agent_prompt(issue_number)
            result.agent_prompt_generated = True

            if self.dry_run:
                console.print(f"[dim]Dry run: Would execute agent prompt[/]")
                console.print(Panel(agent_prompt[:500] + "...", title="Agent Prompt Preview"))
                return result

            # Step 2: Execute agent prompt to implement fix
            console.print("[yellow]Step 2: Executing agent prompt to implement fix...[/]")
            fix_applied = self._execute_agent_prompt(agent_prompt, issue_number)
            result.fix_attempted = True

            if not fix_applied:
                result.error = "Failed to apply fix from agent prompt"
                return result

            # Step 3: Create test for the issue
            console.print("[yellow]Step 3: Creating validation test...[/]")
            test_created = self._create_issue_test(issue_number, agent_prompt)
            result.tests_created = test_created

            # Step 4: Run tests iteratively
            console.print("[yellow]Step 4: Running tests iteratively...[/]")
            tests_passed = self._run_tests_iteratively(issue_number)
            result.tests_passed = tests_passed

            # Step 5: Create PR if successful
            if tests_passed:
                console.print("[yellow]Step 5: Creating pull request...[/]")
                pr_created = self._create_pull_request(issue_number)
                result.pr_created = pr_created

            return result

        except Exception as e:
            result.error = str(e)
            if self.verbose:
                console.print(f"[red]Error: {e}[/]")
            return result

    def _generate_agent_prompt(self, issue_number: int) -> str:
        """Generate agent prompt using issue_investigator.py."""
        cmd = [
            "uv", "run", "python",
            str(self.scripts_dir / "issue_investigator.py"),
            "--issue", str(issue_number),
            "--agent-prompt",
            "--format", "xml"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.repo_root)

        if result.returncode != 0:
            raise RuntimeError(f"Failed to generate agent prompt: {result.stderr}")

        return result.stdout

    def _execute_agent_prompt(self, agent_prompt: str, issue_number: int) -> bool:
        """Execute the agent prompt to implement a fix.

        This would integrate with Claude Code or another AI agent system.
        For now, saves the prompt for manual execution.
        """
        # Save prompt to file for agent consumption
        prompt_file = self.repo_root / f"agent_prompts/issue_{issue_number}_prompt.xml"
        prompt_file.parent.mkdir(exist_ok=True)
        prompt_file.write_text(agent_prompt)

        console.print(f"[green]✓[/] Agent prompt saved to: {prompt_file}")
        console.print("[dim]Execute this prompt with your AI agent to implement the fix[/]")

        # TODO: Integrate with Claude Code API or other agent system
        # For now, this is a manual step
        return False

    def _create_issue_test(self, issue_number: int, agent_prompt: str) -> bool:
        """Create a test that validates the issue is fixed."""
        # Extract workflow from agent prompt
        # Create YAML workflow file
        workflow_file = self.repo_root / f"tests/integration/workflows/issue_{issue_number}_automated.yaml"

        # TODO: Parse agent prompt to extract command sequence
        # For now, use issue_tests.yaml if exists

        return False

    def _run_tests_iteratively(self, issue_number: int, max_iterations: int = 3) -> bool:
        """Run tests iteratively, applying fixes on failures."""
        for iteration in range(max_iterations):
            console.print(f"[cyan]Test iteration {iteration + 1}/{max_iterations}[/]")

            # Run test for this specific issue
            cmd = [
                ".venv/bin/python", "-m", "pytest",
                f"tests/integration/test_workflows.py",
                "-k", f"issue_{issue_number}",
                "-v", "--tb=short", "--override-ini=addopts="
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.repo_root)

            if result.returncode == 0:
                console.print(f"[green]✓ Tests passed on iteration {iteration + 1}[/]")
                return True

            console.print(f"[yellow]Tests failed iteration {iteration + 1}[/]")

            # TODO: Parse test output and apply fixes automatically
            # For now, return False requiring manual intervention

        return False

    def _create_pull_request(self, issue_number: int) -> bool:
        """Create a pull request with the fix."""
        branch_name = f"fix/issue-{issue_number}-automated"

        # TODO: Use gh CLI to create PR
        # gh pr create --title "Fix Issue #{issue_number}" --body "Automated fix"

        console.print("[dim]PR creation would happen here[/]")
        return False

    def resolve_all_open_issues(self) -> List[IssueResolutionResult]:
        """Attempt to resolve all open issues."""
        # Fetch open issues
        cmd = ["gh", "issue", "list", "--repo", "NetDevAutomate/aws_network_shell",
               "--state", "open", "--json", "number,title"]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            console.print("[red]Failed to fetch issues[/]")
            return []

        issues = json.loads(result.stdout)

        results = []
        for issue in issues:
            result = self.resolve_issue(issue["number"])
            results.append(result)

        return results


def main():
    parser = argparse.ArgumentParser(
        description="Automated issue resolution using agent prompts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("--issue", type=int, help="Specific issue number to resolve")
    parser.add_argument("--all", action="store_true", help="Resolve all open issues")
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without executing")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--output", "-o", help="Save results to JSON file")

    args = parser.parse_args()

    if not args.issue and not args.all:
        parser.print_help()
        sys.exit(1)

    resolver = AutomatedIssueResolver(dry_run=args.dry_run, verbose=args.verbose)

    if args.all:
        console.print("[bold]Resolving all open issues...[/]")
        results = resolver.resolve_all_open_issues()
    else:
        results = [resolver.resolve_issue(args.issue)]

    # Display summary
    console.print("\n[bold]Resolution Summary:[/]")
    table = Table()
    table.add_column("Issue")
    table.add_column("Prompt")
    table.add_column("Fix")
    table.add_column("Tests")
    table.add_column("PR")

    for r in results:
        table.add_row(
            f"#{r.issue_number}",
            "✓" if r.agent_prompt_generated else "✗",
            "✓" if r.fix_attempted else "✗",
            "✓" if r.tests_passed else "✗",
            "✓" if r.pr_created else "✗"
        )

    console.print(table)

    # Save results if requested
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(json.dumps([asdict(r) for r in results], indent=2))
        console.print(f"\n[green]Results saved to {output_path}[/]")


if __name__ == "__main__":
    main()
