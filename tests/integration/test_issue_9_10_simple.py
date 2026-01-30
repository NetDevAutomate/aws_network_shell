"""Simple pexpect tests for GitHub Issues #9 and #10 (MVP).

MVP Approach: Hardcoded Python tests without YAML complexity.
Tests spawn REAL aws-net CLI and interact via pexpect.

Run with: uv run pytest tests/integration/test_issue_9_10_simple.py -v
"""

import pytest
import os

# Import pexpect (required dependency)
import pexpect


@pytest.fixture
def shell_process():
    """Spawn real aws-net-shell interactive CLI process.

    Yields process, then ensures cleanup.
    """
    # Check if aws-net-shell command exists
    try:
        import subprocess

        subprocess.run(["which", "aws-net-shell"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        pytest.skip("aws-net-shell CLI not installed - run: pip install -e .")

    # Set AWS profile if provided
    env = os.environ.copy()
    if "AWS_PROFILE" not in env:
        env["AWS_PROFILE"] = "taylaand+net-dev-Admin"  # Default test profile

    # Spawn interactive shell process
    child = pexpect.spawn("aws-net-shell", timeout=15, encoding="utf-8", env=env)

    try:
        # Wait for initial prompt
        child.expect("aws-net>", timeout=5)
        yield child
    finally:
        # Cleanup
        if child.isalive():
            child.sendline("exit")
            try:
                child.expect(pexpect.EOF, timeout=2)
            except (pexpect.TIMEOUT, pexpect.EOF):
                child.terminate(force=True)


@pytest.mark.integration
@pytest.mark.issue_10
class TestIssue10_ELB_NoOutput:
    """GitHub Issue #10: ELB show commands return no data.

    User workflow:
    1. set elb Github-ALB
    2. show detail (works)
    3. show listeners (FAILS - returns "No listeners")
    4. show targets (FAILS - returns "No target groups")
    5. show health (FAILS - returns "No health data")
    """

    def test_elb_show_listeners_has_data(self, shell_process):
        """Binary: show listeners should return listener data."""
        child = shell_process

        # Set ELB context
        child.sendline("set elb Github-ALB")
        child.expect(["aws-net.*>", pexpect.TIMEOUT], timeout=10)

        # Verify we're in ELB context (may show error if ELB doesn't exist)
        _output = child.before  # Not asserted, just ensuring command completes

        # Show listeners - CRITICAL TEST
        child.sendline("show listeners")
        child.expect(["aws-net.*>", pexpect.TIMEOUT], timeout=10)
        listeners_output = child.before

        print(f"\n[Issue #10 Test] Listeners output:\n{listeners_output}")

        # Binary assertion from issue
        assert "No listeners" not in listeners_output, (
            "Issue #10 CONFIRMED: show listeners returned 'No listeners'"
        )

    def test_elb_show_targets_has_data(self, shell_process):
        """Binary: show targets should return target group data."""
        child = shell_process

        child.sendline("set elb Github-ALB")
        child.expect(["aws-net.*>", pexpect.TIMEOUT], timeout=10)

        child.sendline("show targets")
        child.expect(["aws-net.*>", pexpect.TIMEOUT], timeout=10)
        targets_output = child.before

        print(f"\n[Issue #10 Test] Targets output:\n{targets_output}")

        assert "No target groups" not in targets_output, (
            "Issue #10 CONFIRMED: show targets returned 'No target groups'"
        )

    def test_elb_show_health_has_data(self, shell_process):
        """Binary: show health should return health check data."""
        child = shell_process

        child.sendline("set elb Github-ALB")
        child.expect(["aws-net.*>", pexpect.TIMEOUT], timeout=10)

        child.sendline("show health")
        child.expect(["aws-net.*>", pexpect.TIMEOUT], timeout=10)
        health_output = child.before

        print(f"\n[Issue #10 Test] Health output:\n{health_output}")

        assert "No health data" not in health_output, (
            "Issue #10 CONFIRMED: show health returned 'No health data'"
        )


@pytest.mark.integration
@pytest.mark.issue_9
class TestIssue9_EC2_ReturnsAllENIs:
    """GitHub Issue #9: EC2 context returns ALL ENIs, not instance-specific.

    User workflow:
    1. set ec2-instance i-011280e2844a5f00d
    2. show detail (works)
    3. show enis (FAILS - shows 150+ ENIs instead of 1)
    """

    def test_ec2_show_enis_filtered_to_instance(self, shell_process):
        """Binary: show enis should return ONLY instance ENIs."""
        child = shell_process

        # Set EC2 context
        child.sendline("set ec2-instance i-011280e2844a5f00d")
        child.expect(["aws-net.*>", pexpect.TIMEOUT], timeout=10)

        # Show ENIs - CRITICAL TEST
        child.sendline("show enis")
        child.expect(["aws-net.*>", pexpect.TIMEOUT], timeout=15)
        enis_output = child.before

        print(f"\n[Issue #9 Test] ENIs output (first 500 chars):\n{enis_output[:500]}")

        # Count ENIs in output
        eni_count = enis_output.count("eni-")
        print(f"\n[Issue #9 Test] Total ENI count: {eni_count}")

        # Binary assertion: Instance has 1 ENI, should NOT see 50+ ENIs
        assert eni_count <= 5, (
            f"Issue #9 CONFIRMED: show enis returned {eni_count} ENIs. "
            f"Expected 1-2 (instance-specific), got {eni_count} (all account ENIs)"
        )

        # Positive assertion: Should show the instance's actual ENI
        # eni-0989f6e6ce4dfc707 from issue description
        assert "eni-0989f6e6ce4dfc707" in enis_output or eni_count <= 2, (
            "Expected instance-specific ENI not found"
        )


# Note: These tests will FAIL initially, proving the issues exist.
# After fixing Issues #9 and #10 in the codebase, these tests should PASS.
