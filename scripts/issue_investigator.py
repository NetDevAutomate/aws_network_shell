#!/usr/bin/env python3
"""
GitHub Issue Investigator for aws-net-shell.

Fetches GitHub issues, allows interactive selection, reproduces the issue
to confirm if it exists, and collects debug information for agent consumption.

Usage:
    # Interactive mode - select from open issues
    uv run python scripts/issue_investigator.py

    # Investigate specific issue
    uv run python scripts/issue_investigator.py --issue 5

    # With AWS profile
    uv run python scripts/issue_investigator.py --profile my-profile --issue 3

    # Output debug info to file
    uv run python scripts/issue_investigator.py --issue 5 --output debug_report.json

    # Generate agent prompt (XML format - default, better for AI agents)
    uv run python scripts/issue_investigator.py --issue 5 --agent-prompt

    # Generate agent prompt in markdown format
    uv run python scripts/issue_investigator.py --issue 5 --agent-prompt --format markdown

    # Verbose mode for more debug output
    uv run python scripts/issue_investigator.py --issue 5 --verbose
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import traceback
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen
from urllib.error import HTTPError

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Prompt
    from rich.syntax import Syntax
    from rich.markdown import Markdown
except ImportError:
    print("Rich library required. Install with: pip install rich")
    sys.exit(1)

from shell_runner import ShellRunner

REPO = "NetDevAutomate/aws_network_shell"
ISSUES_YAML = Path(__file__).parent / "issue_tests.yaml"

console = Console()


@dataclass
class CommandResult:
    """Result of a single command execution."""

    command: str
    output: str
    duration_seconds: float = 0.0
    has_error: bool = False
    error_type: str | None = None
    error_message: str | None = None


@dataclass
class IssueInvestigation:
    """Complete investigation result for an issue."""

    issue_number: int
    issue_title: str
    issue_url: str
    issue_body: str
    investigation_time: str
    reproduced: bool
    status: str  # "confirmed", "not_reproducible", "partial", "error"
    commands_run: list[CommandResult] = field(default_factory=list)
    extracted_commands: list[str] = field(default_factory=list)
    expected_errors: list[str] = field(default_factory=list)
    actual_errors: list[str] = field(default_factory=list)
    debug_info: dict[str, Any] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)
    raw_output: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    def to_agent_prompt(self, fmt: str = "xml") -> str:
        """Generate a structured prompt for an AI agent to work on this issue.

        Args:
            fmt: Output format - "xml" (recommended for agents) or "markdown"
        """
        if fmt == "xml":
            return self._to_xml_prompt()
        return self._to_markdown_prompt()

    def _to_xml_prompt(self) -> str:
        """Generate XML-structured prompt (more efficient for AI agents)."""
        lines = []
        lines.append("<issue_investigation>")

        lines.append(f'  <issue number="{self.issue_number}">')
        lines.append(f"    <title>{self.issue_title}</title>")
        lines.append(f"    <url>{self.issue_url}</url>")
        lines.append(f"    <status>{self.status}</status>")
        lines.append(f"    <reproduced>{self.reproduced}</reproduced>")
        lines.append("  </issue>")

        lines.append("  <description>")
        lines.append(self.issue_body or "No description provided")
        lines.append("  </description>")

        if self.commands_run:
            lines.append("  <commands_executed>")
            for i, result in enumerate(self.commands_run, 1):
                lines.append(f'    <command index="{i}">')
                lines.append(f"      <input>{result.command}</input>")
                if result.has_error:
                    lines.append(
                        f'      <error type="{result.error_type}">{result.error_message}</error>'
                    )
                output = result.output[:1500] + (
                    "..." if len(result.output) > 1500 else ""
                )
                lines.append(f"      <output><![CDATA[{output}]]></output>")
                lines.append(
                    f"      <duration_seconds>{result.duration_seconds:.2f}</duration_seconds>"
                )
                lines.append("    </command>")
            lines.append("  </commands_executed>")

        if self.actual_errors:
            lines.append("  <errors_detected>")
            for error in self.actual_errors:
                lines.append(f"    <error>{error}</error>")
            lines.append("  </errors_detected>")

        if self.debug_info:
            lines.append("  <debug_info>")
            for key, value in self.debug_info.items():
                lines.append(f"    <{key}>{value}</{key}>")
            lines.append("  </debug_info>")

        lines.append("  <task>")
        if self.reproduced:
            lines.append(
                """    <objective>Fix the confirmed issue</objective>
    <steps>
      <step>Analyze the error messages and stack traces in commands_executed</step>
      <step>Search the codebase for relevant code handling these commands</step>
      <step>Identify the root cause of the issue</step>
      <step>Propose and implement a fix</step>
      <step>Add a test case to prevent regression</step>
    </steps>"""
            )
        else:
            lines.append(
                """    <objective>Investigate why issue could not be reproduced</objective>
    <steps>
      <step>Review the commands and output above</step>
      <step>Check if the issue might be environment-specific</step>
      <step>Look for any partial failures or warnings</step>
      <step>Determine if the issue was already fixed or needs different reproduction steps</step>
      <step>Update the issue status accordingly</step>
    </steps>"""
            )
        lines.append("  </task>")

        if self.recommendations:
            lines.append("  <recommendations>")
            for rec in self.recommendations:
                lines.append(f"    <recommendation>{rec}</recommendation>")
            lines.append("  </recommendations>")

        lines.append("</issue_investigation>")
        return "\n".join(lines)

    def _to_markdown_prompt(self) -> str:
        """Generate markdown prompt (better for human readability)."""
        sections = []

        sections.append(f"# GitHub Issue #{self.issue_number}: {self.issue_title}")
        sections.append(f"\n**URL:** {self.issue_url}")
        sections.append(f"**Status:** {self.status.upper()}")
        sections.append(f"**Reproduced:** {'Yes' if self.reproduced else 'No'}")

        sections.append("\n## Original Issue Description")
        sections.append(self.issue_body or "_No description provided_")

        sections.append("\n## Investigation Results")

        if self.commands_run:
            sections.append("\n### Commands Executed")
            for i, result in enumerate(self.commands_run, 1):
                sections.append(f"\n**{i}. `{result.command}`**")
                if result.has_error:
                    sections.append(f"- Error Type: `{result.error_type}`")
                    sections.append(f"- Error Message: `{result.error_message}`")
                sections.append(
                    f"```\n{result.output[:1000]}{'...' if len(result.output) > 1000 else ''}\n```"
                )

        if self.actual_errors:
            sections.append("\n### Errors Detected")
            for error in self.actual_errors:
                sections.append(f"- `{error}`")

        if self.debug_info:
            sections.append("\n### Debug Information")
            for key, value in self.debug_info.items():
                sections.append(f"- **{key}:** {value}")

        sections.append("\n## Task for Agent")
        if self.reproduced:
            sections.append(
                """
The issue has been **confirmed reproducible**. Please:
1. Analyze the error messages and stack traces above
2. Search the codebase for relevant code handling these commands
3. Identify the root cause of the issue
4. Propose and implement a fix
5. Add a test case to prevent regression
"""
            )
        else:
            sections.append(
                """
The issue could **not be reproduced**. Please:
1. Review the commands and output above
2. Check if the issue might be environment-specific
3. Look for any partial failures or warnings
4. Determine if the issue was already fixed or needs different reproduction steps
5. Update the issue status accordingly
"""
            )

        if self.recommendations:
            sections.append("\n### Recommendations")
            for rec in self.recommendations:
                sections.append(f"- {rec}")

        return "\n".join(sections)


def fetch_issues(issue_num: int | None = None) -> list[dict]:
    """Fetch issues from GitHub API."""
    token = os.environ.get("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    if issue_num:
        url = f"https://api.github.com/repos/{REPO}/issues/{issue_num}"
    else:
        url = f"https://api.github.com/repos/{REPO}/issues?state=open"

    try:
        req = Request(url, headers=headers)
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
        return [data] if issue_num else data
    except HTTPError as e:
        if e.code == 404:
            console.print(f"[red]Issue #{issue_num} not found[/red]")
        else:
            console.print(f"[red]GitHub API error: {e.code} {e.reason}[/red]")
        raise


def extract_commands_from_body(body: str) -> list[str]:
    """Extract shell commands from issue body."""
    if not body:
        return []

    commands = []
    lines = body.split("\n")

    for line in lines:
        line = line.strip()
        # Match lines that look like shell commands
        # e.g., "aws-net> show vpcs" or "aws-net/tr:xxx> show routes"
        if "aws-net" in line and ">" in line:
            match = re.search(r"[>$]\s*(.+)$", line)
            if match:
                cmd = match.group(1).strip()
                if cmd and not cmd.startswith(
                    ("EXCEPTION", "Error", "┏", "┃", "┡", "│", "└", "No ", "Use ")
                ):
                    commands.append(cmd)

    return commands


def extract_errors_from_body(body: str) -> list[str]:
    """Extract expected error patterns from issue body."""
    if not body:
        return []

    errors = []

    # Look for EXCEPTION patterns
    exception_matches = re.findall(
        r"EXCEPTION of type '(\w+)' occurred with message: (.+?)(?:\n|$)", body
    )
    for exc_type, message in exception_matches:
        errors.append(f"{exc_type}: {message.strip()}")

    # Look for KeyError, TypeError, etc.
    error_patterns = re.findall(
        r"(KeyError|TypeError|ValueError|AttributeError)[:\s]+['\"]?([^'\"]+)['\"]?",
        body,
    )
    for error_type, detail in error_patterns:
        errors.append(f"{error_type}: {detail.strip()}")

    # Look for common error messages
    if "No data returned" in body or "No policy data" in body:
        errors.append("No data returned")
    if "Run 'show" in body:
        match = re.search(r"Run '(show [^']+)' first", body)
        if match:
            errors.append(f"Context error: {match.group(0)}")

    return list(set(errors))


def detect_errors_in_output(output: str) -> tuple[bool, str | None, str | None]:
    """Detect if output contains an error."""
    output_lower = output.lower()

    # Check for EXCEPTION
    exc_match = re.search(
        r"EXCEPTION of type '(\w+)' occurred with message: (.+?)(?:\n|$)", output
    )
    if exc_match:
        return True, exc_match.group(1), exc_match.group(2).strip()

    # Check for common Python exceptions in output
    for exc_type in [
        "KeyError",
        "TypeError",
        "ValueError",
        "AttributeError",
        "IndexError",
    ]:
        if exc_type in output:
            match = re.search(rf"{exc_type}[:\s]+['\"]?([^'\"]+)['\"]?", output)
            if match:
                return True, exc_type, match.group(1).strip()
            return True, exc_type, "Unknown details"

    # Check for "Invalid:" messages
    if "Invalid:" in output:
        return (
            True,
            "InvalidCommand",
            output.split("Invalid:")[1].split("\n")[0].strip(),
        )

    # Check for traceback
    if "traceback" in output_lower:
        return True, "Traceback", "Python traceback detected"

    return False, None, None


def display_issues_table(issues: list[dict]) -> None:
    """Display issues in a formatted table."""
    table = Table(
        title="Open GitHub Issues", show_header=True, header_style="bold cyan"
    )
    table.add_column("#", style="dim", width=4)
    table.add_column("Title", style="white", max_width=50)
    table.add_column("Created", style="dim", width=12)
    table.add_column("Commands", width=8, justify="center")

    for issue in issues:
        body = issue.get("body", "") or ""
        commands = extract_commands_from_body(body)
        created = issue["created_at"][:10]

        table.add_row(
            str(issue["number"]),
            issue["title"][:50],
            created,
            str(len(commands)) if commands else "-",
        )

    console.print(table)


def select_issue_interactive(issues: list[dict]) -> dict | None:
    """Interactively select an issue from the list."""
    display_issues_table(issues)

    console.print("\n[dim]Enter issue number to investigate, or 'q' to quit[/dim]")

    issue_nums = [i["number"] for i in issues]
    while True:
        choice = Prompt.ask("Select issue", default="q")
        if choice.lower() == "q":
            return None
        try:
            num = int(choice)
            if num in issue_nums:
                return next(i for i in issues if i["number"] == num)
            console.print(
                f"[yellow]Issue #{num} not in list. Valid: {issue_nums}[/yellow]"
            )
        except ValueError:
            console.print("[yellow]Please enter a number or 'q'[/yellow]")


def investigate_issue(
    issue: dict, profile: str | None = None, timeout: int = 60, verbose: bool = False
) -> IssueInvestigation:
    """Investigate a single issue by attempting to reproduce it."""

    issue_num = issue["number"]
    body = issue.get("body", "") or ""

    investigation = IssueInvestigation(
        issue_number=issue_num,
        issue_title=issue["title"],
        issue_url=issue["html_url"],
        issue_body=body,
        investigation_time=datetime.now().isoformat(),
        reproduced=False,
        status="pending",
    )

    # Extract commands and expected errors from issue body
    investigation.extracted_commands = extract_commands_from_body(body)
    investigation.expected_errors = extract_errors_from_body(body)

    if not investigation.extracted_commands:
        console.print(
            f"[yellow]⚠️  No commands found in issue #{issue_num} body[/yellow]"
        )
        investigation.status = "no_commands"
        investigation.recommendations.append(
            "Manually review issue and add test commands to issue_tests.yaml"
        )
        return investigation

    console.print(
        Panel(
            f"[bold]Issue #{issue_num}:[/bold] {issue['title']}\n\n"
            f"[dim]Commands to run: {len(investigation.extracted_commands)}[/dim]\n"
            f"[dim]Expected errors: {len(investigation.expected_errors)}[/dim]",
            title="🔍 Investigation Starting",
        )
    )

    if verbose:
        console.print("\n[dim]Extracted commands:[/dim]")
        for cmd in investigation.extracted_commands:
            console.print(f"  [cyan]{cmd}[/cyan]")

    # Run the commands
    runner = ShellRunner(profile=profile, timeout=timeout)
    all_output = ""

    try:
        runner.start()

        for cmd in investigation.extracted_commands:
            import time

            start_time = time.time()

            try:
                output = runner.run(cmd)
                duration = time.time() - start_time
            except Exception as e:
                output = f"RUNNER ERROR: {e}\n{traceback.format_exc()}"
                duration = time.time() - start_time

            all_output += f"\n> {cmd}\n{output}\n"

            # Check for errors in output
            has_error, error_type, error_msg = detect_errors_in_output(output)

            result = CommandResult(
                command=cmd,
                output=output,
                duration_seconds=duration,
                has_error=has_error,
                error_type=error_type,
                error_message=error_msg,
            )
            investigation.commands_run.append(result)

            if has_error and error_type:
                investigation.actual_errors.append(f"{error_type}: {error_msg}")

    except Exception as e:
        investigation.debug_info["runner_error"] = str(e)
        investigation.debug_info["runner_traceback"] = traceback.format_exc()
        investigation.status = "error"
    finally:
        runner.close()

    investigation.raw_output = all_output

    # Analyze results
    _analyze_investigation(investigation)

    return investigation


def _analyze_investigation(investigation: IssueInvestigation) -> None:
    """Analyze the investigation results and set status."""

    # Check if any expected errors were found
    errors_found = len(investigation.actual_errors) > 0
    expected_matched = False

    for expected in investigation.expected_errors:
        for actual in investigation.actual_errors:
            # Fuzzy match - check if key parts match
            expected_lower = expected.lower()
            actual_lower = actual.lower()
            if any(part in actual_lower for part in expected_lower.split(":")):
                expected_matched = True
                break

    # Determine status
    if investigation.status == "error":
        investigation.recommendations.append(
            "Investigation encountered an error - check runner configuration"
        )
    elif expected_matched:
        investigation.reproduced = True
        investigation.status = "confirmed"
        investigation.recommendations.append(
            "Issue is confirmed - analyze the error and fix the root cause"
        )
    elif errors_found:
        investigation.reproduced = True
        investigation.status = "confirmed"
        investigation.recommendations.append(
            "Errors detected (different from expected) - issue likely exists but symptoms may have changed"
        )
    elif investigation.expected_errors:
        investigation.status = "not_reproducible"
        investigation.recommendations.append(
            "Expected errors not found - issue may be fixed or environment-specific"
        )
    else:
        investigation.status = "partial"
        investigation.recommendations.append(
            "No explicit errors expected or found - manual review of output recommended"
        )

    # Add recommendations based on error types
    for error in investigation.actual_errors:
        if "KeyError" in error:
            investigation.recommendations.append(
                "KeyError suggests missing dictionary key - check API response structure"
            )
        elif "TypeError" in error:
            investigation.recommendations.append(
                "TypeError suggests type mismatch - check data types in comparison/operations"
            )
        elif "AttributeError" in error:
            investigation.recommendations.append(
                "AttributeError suggests accessing missing attribute - check object structure"
            )
        elif "InvalidCommand" in error:
            investigation.recommendations.append(
                "Invalid command - check command registration and available commands"
            )


def display_investigation_results(
    investigation: IssueInvestigation, verbose: bool = False
) -> None:
    """Display investigation results in a formatted way."""

    status_styles = {
        "confirmed": "[red]❌ CONFIRMED - Issue exists[/red]",
        "not_reproducible": "[green]✅ NOT REPRODUCIBLE - May be fixed[/green]",
        "partial": "[yellow]⚠️  PARTIAL - Manual review needed[/yellow]",
        "error": "[red]💥 ERROR - Investigation failed[/red]",
        "no_commands": "[yellow]📝 NO COMMANDS - Cannot auto-investigate[/yellow]",
    }

    console.print("\n")
    console.print(
        Panel(
            f"[bold]Issue #{investigation.issue_number}:[/bold] {investigation.issue_title}\n\n"
            f"Status: {status_styles.get(investigation.status, investigation.status)}",
            title="📊 Investigation Results",
        )
    )

    if investigation.actual_errors:
        console.print("\n[bold red]Errors Detected:[/bold red]")
        for error in investigation.actual_errors:
            console.print(f"  • {error}")

    if investigation.recommendations:
        console.print("\n[bold cyan]Recommendations:[/bold cyan]")
        for rec in investigation.recommendations:
            console.print(f"  → {rec}")

    if verbose and investigation.raw_output:
        console.print("\n[bold]Raw Output:[/bold]")
        console.print(Panel(investigation.raw_output[:2000], title="Shell Output"))


def save_investigation(
    investigation: IssueInvestigation, output_path: Path, fmt: str = "xml"
) -> None:
    """Save investigation results to a file."""
    data = {
        "investigation": investigation.to_dict(),
        "agent_prompt_xml": investigation.to_agent_prompt(fmt="xml"),
        "agent_prompt_markdown": investigation.to_agent_prompt(fmt="markdown"),
    }

    with open(output_path, "w") as f:
        json.dump(data, f, indent=2, default=str)

    console.print(f"\n[green]✓ Investigation saved to: {output_path}[/green]")


def main():
    parser = argparse.ArgumentParser(
        description="Investigate GitHub issues for aws-net-shell",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--issue", "-i", type=int, help="Specific issue number to investigate"
    )
    parser.add_argument("--profile", "-p", help="AWS profile to use")
    parser.add_argument(
        "--timeout", "-t", type=int, default=60, help="Command timeout (default: 60s)"
    )
    parser.add_argument(
        "--output", "-o", type=Path, help="Save investigation to JSON file"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--agent-prompt",
        "-a",
        action="store_true",
        help="Print agent-ready prompt to stdout",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["xml", "markdown"],
        default="xml",
        help="Agent prompt format: xml (default, better for agents) or markdown",
    )
    parser.add_argument(
        "--list", "-l", action="store_true", help="Just list open issues"
    )
    args = parser.parse_args()

    try:
        # Fetch issues
        if args.issue:
            issues = fetch_issues(args.issue)
            issue = issues[0]
        else:
            issues = fetch_issues()

            if args.list:
                display_issues_table(issues)
                sys.exit(0)

            issue = select_issue_interactive(issues)
            if not issue:
                console.print("[dim]Cancelled[/dim]")
                sys.exit(0)

        # Investigate the issue
        investigation = investigate_issue(
            issue=issue,
            profile=args.profile,
            timeout=args.timeout,
            verbose=args.verbose,
        )

        # Display results
        display_investigation_results(investigation, verbose=args.verbose)

        # Save to file if requested
        if args.output:
            save_investigation(investigation, args.output)

        # Print agent prompt if requested
        if args.agent_prompt:
            console.print("\n" + "=" * 60)
            console.print(f"[bold]AGENT PROMPT ({args.format.upper()})[/bold]")
            console.print("=" * 60 + "\n")
            prompt = investigation.to_agent_prompt(fmt=args.format)
            if args.format == "markdown":
                console.print(Markdown(prompt))
            else:
                console.print(Syntax(prompt, "xml", theme="monokai"))

        # Exit code based on status
        if investigation.reproduced:
            sys.exit(1)  # Issue exists
        sys.exit(0)

    except KeyboardInterrupt:
        console.print("\n[dim]Interrupted[/dim]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if args.verbose:
            console.print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
