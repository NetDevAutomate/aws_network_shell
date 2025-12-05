#!/usr/bin/env python3
"""
AWS Network Shell - Test Report Generator
Converts JSON test results into formatted markdown reports.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


def load_results(input_file: str) -> dict:
    """Load test results from JSON file."""
    with open(input_file) as f:
        return json.load(f)


def generate_summary_section(report: dict) -> str:
    """Generate summary section."""
    summary = report.get("summary", {})
    timestamp = report.get("timestamp", datetime.utcnow().isoformat())
    profile = report.get("profile", "unknown")

    return f"""## Summary

| Metric | Value |
|--------|-------|
| **Timestamp** | {timestamp} |
| **Profile** | {profile} |
| **Total Tests** | {summary.get('total', 0)} |
| **Passed** | ✅ {summary.get('passed', 0)} |
| **Failed** | ❌ {summary.get('failed', 0)} |
| **Pass Rate** | {_calc_pass_rate(summary)}% |
"""


def _calc_pass_rate(summary: dict) -> float:
    """Calculate pass rate percentage."""
    total = summary.get("total", 0)
    passed = summary.get("passed", 0)
    if total == 0:
        return 0.0
    return round((passed / total) * 100, 1)


def generate_results_by_phase(results: list[dict]) -> str:
    """Generate results organized by test phase."""
    phases = {
        "ROOT": "Phase 2: Root Level Commands",
        "VPC": "Phase 3: VPC Context",
        "TGW": "Phase 4: Transit Gateway Context",
        "VPN": "Phase 5: VPN Context",
        "FW": "Phase 6: Firewall Context",
        "CWAN": "Phase 7: CloudWAN Context",
        "UTIL": "Phase 8: Utility Commands",
    }

    output = ["## Results by Phase\n"]

    for prefix, phase_name in phases.items():
        phase_results = [r for r in results if r["test_id"].startswith(prefix)]
        if not phase_results:
            continue

        output.append(f"### {phase_name}\n")
        output.append("| Test ID | Command | Result | Details |")
        output.append("|---------|---------|--------|---------|")

        for r in phase_results:
            status = "✅ PASS" if r["passed"] else "❌ FAIL"
            details = "; ".join(r.get("details", [])[:2])  # First 2 details
            details = details[:50] + "..." if len(details) > 50 else details
            command = r["command"][:30] + "..." if len(r["command"]) > 30 else r["command"]
            output.append(f"| {r['test_id']} | `{command}` | {status} | {details} |")

        output.append("")

    return "\n".join(output)


def generate_failures_detail(results: list[dict]) -> str:
    """Generate detailed failure analysis."""
    failures = [r for r in results if not r["passed"]]

    if not failures:
        return """## Failure Details

🎉 **No failures detected!** All tests passed successfully.
"""

    output = ["## Failure Details\n"]

    for r in failures:
        output.append(f"### {r['test_id']}: `{r['command']}`\n")

        if r.get("error"):
            output.append(f"**Error**: {r['error']}\n")

        output.append("**Validation Details**:")
        for detail in r.get("details", []):
            output.append(f"- {detail}")

        output.append("\n---\n")

    return "\n".join(output)


def generate_recommendations(results: list[dict]) -> str:
    """Generate recommendations based on test results."""
    failures = [r for r in results if not r["passed"]]

    if not failures:
        return """## Recommendations

✅ All tests passed. The AWS Network Shell is functioning correctly.

**Next Steps**:
1. Run tests periodically to catch regressions
2. Add new tests for additional commands
3. Consider integration with CI/CD pipeline
"""

    recommendations = ["## Recommendations\n"]

    # Analyze failure patterns
    error_types = {
        "count_mismatch": [],
        "missing_ids": [],
        "execution_error": [],
        "output_error": [],
    }

    for r in failures:
        for detail in r.get("details", []):
            if "count" in detail.lower() and "expected" in detail.lower():
                error_types["count_mismatch"].append(r["test_id"])
            elif "missing" in detail.lower():
                error_types["missing_ids"].append(r["test_id"])
            elif "error" in detail.lower():
                if r.get("error"):
                    error_types["execution_error"].append(r["test_id"])
                else:
                    error_types["output_error"].append(r["test_id"])

    if error_types["count_mismatch"]:
        recommendations.append("### Count Mismatches")
        recommendations.append("The following tests showed count discrepancies:")
        for tid in error_types["count_mismatch"]:
            recommendations.append(f"- {tid}")
        recommendations.append("\n**Fix**: Check if shell is filtering resources differently than AWS CLI.\n")

    if error_types["missing_ids"]:
        recommendations.append("### Missing Resource IDs")
        recommendations.append("The following tests had missing resource IDs:")
        for tid in error_types["missing_ids"]:
            recommendations.append(f"- {tid}")
        recommendations.append("\n**Fix**: Verify shell is querying all regions/resources.\n")

    if error_types["execution_error"]:
        recommendations.append("### Execution Errors")
        recommendations.append("The following tests had execution errors:")
        for tid in error_types["execution_error"]:
            recommendations.append(f"- {tid}")
        recommendations.append("\n**Fix**: Check command syntax and handler implementation.\n")

    if error_types["output_error"]:
        recommendations.append("### Output Errors")
        recommendations.append("The following tests had errors in output:")
        for tid in error_types["output_error"]:
            recommendations.append(f"- {tid}")
        recommendations.append("\n**Fix**: Review handler error handling and edge cases.\n")

    return "\n".join(recommendations)


def generate_test_coverage(results: list[dict]) -> str:
    """Generate test coverage summary."""
    phases = {
        "ROOT": {"name": "Root Commands", "expected": 5},
        "VPC": {"name": "VPC Context", "expected": 6},
        "TGW": {"name": "TGW Context", "expected": 4},
        "VPN": {"name": "VPN Context", "expected": 4},
        "FW": {"name": "Firewall Context", "expected": 3},
        "CWAN": {"name": "CloudWAN Context", "expected": 6},
        "UTIL": {"name": "Utility Commands", "expected": 3},
    }

    output = ["## Test Coverage\n"]
    output.append("| Phase | Tests Run | Expected | Coverage |")
    output.append("|-------|-----------|----------|----------|")

    for prefix, info in phases.items():
        count = len([r for r in results if r["test_id"].startswith(prefix)])
        expected = info["expected"]
        coverage = f"{int((count / expected) * 100)}%" if expected > 0 else "N/A"
        output.append(f"| {info['name']} | {count} | {expected} | {coverage} |")

    output.append("")
    return "\n".join(output)


def generate_markdown_report(report: dict) -> str:
    """Generate full markdown report."""
    results = report.get("results", [])

    sections = [
        "# AWS Network Shell Test Report\n",
        generate_summary_section(report),
        generate_test_coverage(results),
        generate_results_by_phase(results),
        generate_failures_detail(results),
        generate_recommendations(results),
        f"\n---\n*Report generated: {datetime.utcnow().isoformat()}*\n",
    ]

    return "\n".join(sections)


def main():
    parser = argparse.ArgumentParser(description="Generate test report from JSON results")
    parser.add_argument(
        "--input",
        default="/tmp/test_results.json",
        help="Input JSON file from test runner",
    )
    parser.add_argument(
        "--output",
        default="test_report.md",
        help="Output markdown file",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json", "summary"],
        default="markdown",
        help="Output format",
    )
    args = parser.parse_args()

    # Load results
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {args.input}")
        print("Run agent_test_runner.py first to generate test results.")
        sys.exit(1)

    report = load_results(args.input)

    # Generate output
    if args.format == "markdown":
        output = generate_markdown_report(report)
        Path(args.output).write_text(output)
        print(f"Report saved to: {args.output}")

    elif args.format == "json":
        # Just pretty-print the JSON
        Path(args.output).write_text(json.dumps(report, indent=2))
        print(f"JSON report saved to: {args.output}")

    elif args.format == "summary":
        # Print summary to console
        summary = report.get("summary", {})
        print("=" * 50)
        print("AWS Network Shell Test Summary")
        print("=" * 50)
        print(f"Total:  {summary.get('total', 0)}")
        print(f"Passed: {summary.get('passed', 0)}")
        print(f"Failed: {summary.get('failed', 0)}")
        print(f"Rate:   {_calc_pass_rate(summary)}%")

        failures = [r for r in report.get("results", []) if not r["passed"]]
        if failures:
            print("\nFailed Tests:")
            for r in failures:
                print(f"  - {r['test_id']}: {r['command']}")


if __name__ == "__main__":
    main()
