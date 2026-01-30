"""Tests for show regions command."""

import pytest
from aws_network_tools.shell.main import AWSNetShell
from aws_network_tools.config import RuntimeConfig
from io import StringIO
import sys


@pytest.fixture(autouse=True)
def reset_config():
    """Reset RuntimeConfig before each test."""
    RuntimeConfig.reset()
    yield
    RuntimeConfig.reset()


@pytest.fixture
def shell():
    """Create shell instance."""
    s = AWSNetShell()
    return s


class TestShowRegions:
    """Test show regions command."""

    def test_show_regions_with_no_filter(self, shell):
        """Test show regions when no regions set (shows 'all')."""
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        shell.onecmd("show regions")
        output = sys.stdout.getvalue()

        sys.stdout = old_stdout

        assert "Current Scope: all regions" in output
        assert "Available AWS Regions:" in output
        assert "US:" in output
        assert "Europe:" in output
        assert "Asia Pacific:" in output
        assert "us-east-1" in output
        assert "eu-west-1" in output
        assert "ap-southeast-1" in output

    def test_show_regions_with_single_region(self, shell):
        """Test show regions after setting single region."""
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        shell.onecmd("set regions us-east-1")
        sys.stdout = StringIO()  # Reset buffer

        shell.onecmd("show regions")
        output = sys.stdout.getvalue()

        sys.stdout = old_stdout

        assert "Current Scope: us-east-1" in output
        assert "limited to 1 region(s)" in output
        assert "Available AWS Regions:" in output

    def test_show_regions_with_multiple_regions(self, shell):
        """Test show regions after setting multiple regions."""
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        shell.onecmd("set regions us-east-1,eu-west-1,ap-southeast-1")
        sys.stdout = StringIO()  # Reset buffer

        shell.onecmd("show regions")
        output = sys.stdout.getvalue()

        sys.stdout = old_stdout

        assert "Current Scope: us-east-1, eu-west-1, ap-southeast-1" in output
        assert "limited to 3 region(s)" in output

    def test_show_regions_displays_usage_hint(self, shell):
        """Test usage hint is always displayed."""
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        shell.onecmd("show regions")
        output = sys.stdout.getvalue()

        sys.stdout = old_stdout

        assert "Usage: set regions" in output

    def test_show_regions_includes_major_regions(self, shell):
        """Test that major AWS regions are displayed."""
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        shell.onecmd("show regions")
        output = sys.stdout.getvalue()

        sys.stdout = old_stdout

        major_regions = [
            "us-east-1",
            "us-west-2",
            "eu-west-1",
            "eu-central-1",
            "ap-southeast-1",
            "ap-northeast-1",
            "ca-central-1",
            "sa-east-1",
        ]

        for region in major_regions:
            assert region in output, f"Region {region} should be in output"

    def test_show_regions_in_hierarchy(self, shell):
        """Test that 'regions' is in show command hierarchy."""
        from aws_network_tools.shell.base import HIERARCHY

        assert "regions" in HIERARCHY[None]["show"]

    def test_show_regions_excludes_china_regions(self, shell):
        """Test that China regions (cn-*) are excluded from display."""
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        shell.onecmd("show regions")
        output = sys.stdout.getvalue()

        sys.stdout = old_stdout

        # China regions should not be in main output
        assert "cn-north-1" not in output
        assert "cn-northwest-1" not in output
