#!/usr/bin/env python3
"""
Run GitHub issue reproduction tests against aws-net-shell.

Usage:
    # Run all issue tests
    uv run python scripts/run_issue_tests.py

    # Run specific issue
    uv run python scripts/run_issue_tests.py --issue 5

    # Just print commands for an issue (for shell_runner.py)
    uv run python scripts/run_issue_tests.py --issue 5 --print-commands

    # With AWS profile
    uv run python scripts/run_issue_tests.py --profile my-profile --issue 3
"""

import argparse
import sys
from pathlib import Path

import yaml

from shell_runner import ShellRunner


def load_issues(yaml_path: Path) -> dict:
    """Load issue test definitions from YAML."""
    with open(yaml_path) as f:
        data = yaml.safe_load(f)
    return data.get("issues", {})


def print_commands(issue: dict):
    """Print commands for use with shell_runner.py."""
    for cmd in issue.get("commands", []):
        # Strip comments
        cmd = cmd.split("#")[0].strip()
        if cmd:
            print(f'"{cmd}"', end=" ")
    print()


def run_issue_test(runner: ShellRunner, issue_num: int, issue: dict) -> bool:
    """Run a single issue test and check results."""
    print(f"\n{'=' * 60}")
    print(f"ISSUE #{issue_num}: {issue.get('title', 'Untitled')}")
    print(f"{'=' * 60}")

    outputs = []
    all_output = ""

    for cmd in issue.get("commands", []):
        # Strip comments
        cmd = cmd.split("#")[0].strip()
        if cmd:
            output = runner.run(cmd)
            outputs.append(output)
            all_output += output + "\n"

    # Check expectations
    passed = True

    # Check for expected error
    if "expect_error" in issue:
        if issue["expect_error"] not in all_output:
            print(f"\n⚠️  Expected error not found: {issue['expect_error']}")
        else:
            print(
                f"\n❌ CONFIRMED: Error '{issue['expect_error']}' present (issue exists)"
            )
            passed = False

    # Check for strings that should be present (indicating bug)
    if "expect_contains" in issue:
        for expected in issue["expect_contains"]:
            if expected in all_output:
                print(f"\n❌ CONFIRMED: Found '{expected}' (issue exists)")
                passed = False

    # Check for strings that should NOT be present
    if "expect_not_contains" in issue:
        for unexpected in issue["expect_not_contains"]:
            if unexpected in all_output:
                print(f"\n❌ CONFIRMED: Found '{unexpected}' (issue exists)")
                passed = False

    if passed:
        print(f"\n✅ Issue #{issue_num} appears FIXED or not reproducible")

    return passed


def main():
    parser = argparse.ArgumentParser(description="Run GitHub issue reproduction tests")
    parser.add_argument("--issue", "-i", type=int, help="Run specific issue number")
    parser.add_argument("--profile", "-p", help="AWS profile to use")
    parser.add_argument("--timeout", "-t", type=int, default=60, help="Command timeout")
    parser.add_argument(
        "--print-commands",
        action="store_true",
        help="Just print commands for shell_runner.py",
    )
    parser.add_argument(
        "--yaml",
        default=Path(__file__).parent / "issue_tests.yaml",
        help="Path to issue tests YAML file",
    )
    args = parser.parse_args()

    issues = load_issues(Path(args.yaml))

    if not issues:
        print("No issues found in YAML file")
        sys.exit(1)

    # Filter to specific issue if requested
    if args.issue:
        if args.issue not in issues:
            print(f"Issue #{args.issue} not found in YAML")
            sys.exit(1)
        issues = {args.issue: issues[args.issue]}

    # Just print commands mode
    if args.print_commands:
        for issue_num, issue in issues.items():
            print(f"# Issue #{issue_num}: {issue.get('title', '')}")
            print("uv run python scripts/shell_runner.py ", end="")
            print_commands(issue)
            print()
        sys.exit(0)

    # Run tests
    runner = ShellRunner(profile=args.profile, timeout=args.timeout)
    results = {}

    try:
        runner.start()
        for issue_num, issue in issues.items():
            results[issue_num] = run_issue_test(runner, issue_num, issue)
    finally:
        runner.close()

    # Summary
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")

    passed = sum(1 for v in results.values() if v)
    failed = sum(1 for v in results.values() if not v)

    for issue_num, result in results.items():
        status = "✅ FIXED" if result else "❌ EXISTS"
        print(f"  Issue #{issue_num}: {status}")

    print(f"\nTotal: {passed} fixed, {failed} still exist")
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
