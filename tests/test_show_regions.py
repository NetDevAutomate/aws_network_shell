"""Tests for show regions command."""

import pytest
from botocore.exceptions import NoCredentialsError
from unittest.mock import MagicMock, patch
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


@pytest.fixture(autouse=True)
def no_aws_account():
    """Default: the enabled-regions lookup fails, so the static list is shown.

    `show regions` calls ec2.describe_regions on the current account. Without
    this the tests depend on local credentials and on which regions that
    account has opted into.
    """
    with patch("boto3.Session", side_effect=NoCredentialsError()):
        yield


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
        assert "Available Regions:" in output
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
        assert "Available Regions:" in output

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

    def test_show_regions_uses_account_enabled_regions(self, shell):
        """When describe_regions succeeds, only the account's regions are shown."""
        ec2 = MagicMock()
        ec2.describe_regions.return_value = {
            "Regions": [{"RegionName": "us-east-1"}, {"RegionName": "eu-west-1"}]
        }
        session = MagicMock()
        session.client.return_value = ec2

        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            with patch("boto3.Session", return_value=session):
                shell.onecmd("show regions")
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout

        ec2.describe_regions.assert_called_once_with(AllRegions=False)
        assert "Showing only regions enabled in your AWS account" in output
        assert "us-east-1" in output
        assert "eu-west-1" in output
        assert "ap-southeast-1" not in output

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
