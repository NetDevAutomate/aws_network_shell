#!/usr/bin/env python3
"""
Fetch GitHub issues and extract command workflows.

Usage:
    # Fetch all open issues
    uv run python scripts/fetch_issues.py

    # Fetch specific issue
    uv run python scripts/fetch_issues.py --issue 5

    # Output as shell_runner commands
    uv run python scripts/fetch_issues.py --issue 5 --format commands

Requires: GITHUB_TOKEN env var for private repos (optional for public)
"""

import argparse
import json
import os
import re
import sys
from urllib.request import Request, urlopen

REPO = "NetDevAutomate/aws_network_shell"


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

    req = Request(url, headers=headers)
    with urlopen(req) as resp:
        data = json.loads(resp.read().decode())

    return [data] if issue_num else data


def extract_commands(body: str) -> list[str]:
    """Extract shell commands from issue body."""
    commands = []
    lines = body.split("\n")
    
    for line in lines:
        line = line.strip()
        # Match lines that look like shell commands
        # e.g., "aws-net> show vpcs" or "aws-net/tr:xxx> show routes"
        if "aws-net" in line and ">" in line:
            # Extract command after the prompt
            match = re.search(r'[>$]\s*(.+)$', line)
            if match:
                cmd = match.group(1).strip()
                if cmd and not cmd.startswith(("EXCEPTION", "Error", "┏", "┃", "┡", "│", "└")):
                    commands.append(cmd)
    
    return commands


def format_yaml(issues: list[dict]) -> str:
    """Format issues as YAML test definitions."""
    lines = ["# Auto-generated from GitHub issues", "# Review and adjust commands as needed", "", "issues:"]
    
    for issue in issues:
        num = issue["number"]
        title = issue["title"]
        body = issue.get("body", "") or ""
        commands = extract_commands(body)
        
        lines.append(f"  {num}:")
        lines.append(f'    title: "{title}"')
        lines.append("    commands:")
        
        if commands:
            for cmd in commands:
                lines.append(f"      - {cmd}")
        else:
            lines.append("      # No commands extracted - add manually")
            lines.append("      - show global-networks")
        
        lines.append("")
    
    return "\n".join(lines)


def format_commands(issues: list[dict]) -> str:
    """Format as shell_runner.py command line."""
    lines = []
    for issue in issues:
        num = issue["number"]
        title = issue["title"]
        body = issue.get("body", "") or ""
        commands = extract_commands(body)
        
        lines.append(f"# Issue #{num}: {title}")
        if commands:
            cmd_args = " ".join(f'"{c}"' for c in commands)
            lines.append(f"uv run python scripts/shell_runner.py {cmd_args}")
        else:
            lines.append("# No commands extracted")
        lines.append("")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Fetch GitHub issues")
    parser.add_argument("--issue", "-i", type=int, help="Fetch specific issue")
    parser.add_argument("--format", "-f", choices=["yaml", "commands", "json"], 
                        default="yaml", help="Output format")
    args = parser.parse_args()

    try:
        issues = fetch_issues(args.issue)
    except Exception as e:
        print(f"Error fetching issues: {e}", file=sys.stderr)
        sys.exit(1)

    if args.format == "json":
        print(json.dumps(issues, indent=2))
    elif args.format == "commands":
        print(format_commands(issues))
    else:
        print(format_yaml(issues))


if __name__ == "__main__":
    main()
