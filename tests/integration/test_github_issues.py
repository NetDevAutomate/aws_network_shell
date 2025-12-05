"""Integration tests replicating exact GitHub issue workflows using pexpect.

Tests ACTUAL CLI behavior by spawning real shell process.
Each test replicates the precise command sequence from a GitHub issue.

REQUIREMENTS:
    - pexpect installed: uv add pexpect
    - aws-net CLI installed: uv pip install -e .
    - Run with: uv run pytest tests/integration/test_github_issues.py -v

Usage:
    # Run all integration tests
    uv run pytest tests/integration/test_github_issues.py -v

    # Run specific issue
    uv run pytest tests/integration/test_github_issues.py -k "issue_10" -v
"""

import pytest
import os

# Try importing pexpect, skip all tests if not available
try:
    import pexpect
    PEXPECT_AVAILABLE = True
except ImportError:
    PEXPECT_AVAILABLE = False
    pytestmark = pytest.mark.skip(reason="pexpect not installed - run: uv add pexpect")


class TestIssue10_ELB_NoOutput:
    """GitHub Issue #10: ELB commands return no output.

    User Workflow:
    1. set elb Github-ALB
    2. show detail (✓ works)
    3. show listeners (✗ returns "No listeners")
    4. show targets (✗ returns "No target groups")
    5. show health (✗ returns "No health data")

    Expected: All commands should return actual ALB data
    """

    @pytest.mark.integration
    @pytest.mark.issue_10
    def test_issue_10_show_listeners(self):
        """Binary: show listeners should return listener data, not 'No listeners'."""
        # Spawn real shell
        child = pexpect.spawn('aws-net', timeout=10)

        try:
            # Wait for prompt
            child.expect('aws-net>')

            # Replicate exact user workflow from issue
            child.sendline('set elb Github-ALB')
            child.expect('aws-net/el:Github-ALB>')

            # Verify detail works (baseline)
            child.sendline('show detail')
            child.expect('aws-net/el:Github-ALB>')
            detail_output = child.before.decode('utf-8')
            assert 'Load Balancer: Github-ALB' in detail_output

            # CRITICAL TEST: show listeners
            child.sendline('show listeners')
            child.expect('aws-net/el:Github-ALB>')
            listeners_output = child.before.decode('utf-8')

            # Binary FAIL condition from issue
            assert 'No listeners' not in listeners_output, (
                f"Issue #10 REPRODUCED: show listeners returned 'No listeners'"
            )

            # Binary PASS condition
            assert ('Listener' in listeners_output or 'Port' in listeners_output), (
                f"Expected listener data in output:\n{listeners_output}"
            )

        finally:
            child.close()


class TestIssue9_EC2_AllENIs:
    """GitHub Issue #9: EC2 context returns ALL ENIs instead of instance-specific.

    User Workflow:
    1. set ec2-instance i-011280e2844a5f00d
    2. show detail (✓ shows instance info)
    3. show enis (✗ shows ALL 150+ ENIs, not just instance ENI)

    Expected: show enis should return ONLY eni-0989f6e6ce4dfc707 (instance's ENI)
    """

    @pytest.mark.integration
    @pytest.mark.issue_9
    def test_issue_9_show_enis_filtered(self):
        """Binary: show enis should return ONLY instance ENI, not all account ENIs."""
        child = pexpect.spawn('aws-net', timeout=10)

        try:
            child.expect('aws-net>')

            # Replicate exact user workflow
            child.sendline('set ec2-instance i-011280e2844a5f00d')
            child.expect('aws-net/ec:AWS-Github>')

            # Verify detail works
            child.sendline('show detail')
            child.expect('aws-net/ec:AWS-Github>')
            detail_output = child.before.decode('utf-8')
            assert 'i-011280e2844a5f00d' in detail_output

            # CRITICAL TEST: show enis should be filtered
            child.sendline('show enis')
            child.expect('aws-net/ec:AWS-Github>')
            enis_output = child.before.decode('utf-8')

            # Binary PASS: Should show instance's ENI
            assert 'eni-0989f6e6ce4dfc707' in enis_output, (
                "Instance ENI not found in output"
            )

            # Binary FAIL: Count ENIs (should be 1, not 150+)
            eni_count = enis_output.count('eni-')

            # From issue, user sees 150+ ENIs when there should be 1
            assert eni_count <= 5, (
                f"Issue #9 REPRODUCED: show enis returned {eni_count} ENIs (expected 1)\n"
                f"This indicates ALL account ENIs are being returned, not filtered to instance"
            )

        finally:
            child.close()


# Execution Summary
if __name__ == "__main__":
    print(__doc__)
    print("\nTo run these tests:")
    print("  pytest tests/integration/test_github_issues.py -v")
    print("\nNote: These tests spawn real 'aws-net' CLI process")
    print("      Install: pip install -e . && pip install pexpect")
