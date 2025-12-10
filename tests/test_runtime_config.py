"""Tests for RuntimeConfig singleton and region filtering."""

import pytest
from aws_network_tools.config import RuntimeConfig
from aws_network_tools.shell.main import AWSNetShell
from io import StringIO
import sys


@pytest.fixture(autouse=True)
def reset_runtime_config():
    """Reset RuntimeConfig before each test."""
    RuntimeConfig.reset()
    yield
    RuntimeConfig.reset()


@pytest.fixture
def shell():
    """Create shell instance."""
    s = AWSNetShell()
    s.profile = "test-profile"
    s._sync_runtime_config()  # Sync the test profile to RuntimeConfig
    return s


class TestRuntimeConfigSingleton:
    """Test RuntimeConfig singleton pattern."""

    def test_singleton_returns_same_instance(self):
        """Test that multiple calls return same instance."""
        config1 = RuntimeConfig()
        config2 = RuntimeConfig()
        assert config1 is config2

    def test_set_and_get_profile(self):
        """Test profile setting and retrieval."""
        RuntimeConfig.set_profile("production")
        assert RuntimeConfig.get_profile() == "production"

    def test_set_and_get_regions(self):
        """Test regions setting and retrieval."""
        regions = ["us-east-1", "eu-west-1"]
        RuntimeConfig.set_regions(regions)
        assert RuntimeConfig.get_regions() == regions

    def test_empty_regions_list(self):
        """Test empty regions list."""
        RuntimeConfig.set_regions([])
        assert RuntimeConfig.get_regions() == []

    def test_set_and_check_no_cache(self):
        """Test no_cache flag."""
        RuntimeConfig.set_no_cache(True)
        assert RuntimeConfig.is_cache_disabled() is True

        RuntimeConfig.set_no_cache(False)
        assert RuntimeConfig.is_cache_disabled() is False

    def test_set_and_get_output_format(self):
        """Test output format setting."""
        RuntimeConfig.set_output_format("json")
        assert RuntimeConfig.get_output_format() == "json"

    def test_invalid_output_format_raises_error(self):
        """Test invalid format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid format"):
            RuntimeConfig.set_output_format("xml")

    def test_reset_clears_all_settings(self):
        """Test reset returns to defaults."""
        RuntimeConfig.set_profile("test")
        RuntimeConfig.set_regions(["us-west-2"])
        RuntimeConfig.set_no_cache(True)
        RuntimeConfig.set_output_format("yaml")

        RuntimeConfig.reset()

        assert RuntimeConfig.get_profile() is None
        assert RuntimeConfig.get_regions() == []
        assert RuntimeConfig.is_cache_disabled() is False
        assert RuntimeConfig.get_output_format() == "table"


class TestShellRuntimeConfigSync:
    """Test shell synchronization with RuntimeConfig."""

    def test_shell_init_syncs_config(self, shell):
        """Test shell initialization sets RuntimeConfig."""
        # Shell fixture explicitly syncs after setting test profile
        assert RuntimeConfig.get_profile() == shell.profile
        assert RuntimeConfig.get_regions() == shell.regions

    def test_set_profile_syncs_to_runtime_config(self, shell):
        """Test setting profile updates RuntimeConfig."""
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        shell.onecmd("set profile production")
        sys.stdout = old_stdout

        assert shell.profile == "production"
        assert RuntimeConfig.get_profile() == "production"

    def test_set_regions_syncs_to_runtime_config(self, shell):
        """Test setting regions updates RuntimeConfig."""
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        shell.onecmd("set regions us-east-1,eu-west-1")
        sys.stdout = old_stdout

        assert shell.regions == ["us-east-1", "eu-west-1"]
        assert RuntimeConfig.get_regions() == ["us-east-1", "eu-west-1"]

    def test_set_no_cache_syncs_to_runtime_config(self, shell):
        """Test setting no-cache updates RuntimeConfig."""
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        shell.onecmd("set no-cache on")
        sys.stdout = old_stdout

        assert shell.no_cache is True
        assert RuntimeConfig.is_cache_disabled() is True

    def test_set_output_format_syncs_to_runtime_config(self, shell):
        """Test setting output format updates RuntimeConfig."""
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        shell.onecmd("set output-format json")
        sys.stdout = old_stdout

        assert shell.output_format == "json"
        assert RuntimeConfig.get_output_format() == "json"


class TestAutoCacheClearOnConfigChange:
    """Test automatic cache clearing when profile or regions change."""

    def test_cache_cleared_when_profile_changes(self, shell):
        """Test cache auto-clears on profile change."""
        # Populate cache
        shell._cache = {
            "transit_gateways": [{"id": "tgw-1"}],
            "vpcs": [{"id": "vpc-1"}],
        }

        old_stdout = sys.stdout
        sys.stdout = StringIO()

        shell.onecmd("set profile production")
        output = sys.stdout.getvalue()

        sys.stdout = old_stdout

        # Cache should be cleared
        assert len(shell._cache) == 0
        assert "Cleared 2 cache entries (profile changed)" in output

    def test_cache_cleared_when_regions_change(self, shell):
        """Test cache auto-clears on regions change."""
        # Populate cache
        shell._cache = {
            "transit_gateways": [{"id": "tgw-1"}],
            "vpcs": [{"id": "vpc-1"}],
            "elbs": [{"id": "elb-1"}],
        }

        old_stdout = sys.stdout
        sys.stdout = StringIO()

        shell.onecmd("set regions eu-west-1")
        output = sys.stdout.getvalue()

        sys.stdout = old_stdout

        # Cache should be cleared
        assert len(shell._cache) == 0
        assert "Cleared 3 cache entries (regions changed)" in output

    def test_no_clear_when_setting_same_profile(self, shell):
        """Test cache not cleared when profile doesn't change."""
        shell.profile = "production"
        shell._cache = {"transit_gateways": [{"id": "tgw-1"}]}

        old_stdout = sys.stdout
        sys.stdout = StringIO()

        shell.onecmd("set profile production")
        output = sys.stdout.getvalue()

        sys.stdout = old_stdout

        # Cache should NOT be cleared
        assert "transit_gateways" in shell._cache
        assert "Cleared" not in output

    def test_no_clear_when_setting_same_regions(self, shell):
        """Test cache not cleared when regions don't change."""
        shell.regions = ["us-east-1"]
        shell._cache = {"transit_gateways": [{"id": "tgw-1"}]}

        old_stdout = sys.stdout
        sys.stdout = StringIO()

        shell.onecmd("set regions us-east-1")
        output = sys.stdout.getvalue()

        sys.stdout = old_stdout

        # Cache should NOT be cleared
        assert "transit_gateways" in shell._cache
        assert "Cleared" not in output

    def test_cache_clear_message_only_when_cache_has_data(self, shell):
        """Test no clear message when cache already empty."""
        shell._cache = {}

        old_stdout = sys.stdout
        sys.stdout = StringIO()

        shell.onecmd("set regions eu-west-1")
        output = sys.stdout.getvalue()

        sys.stdout = old_stdout

        # Should not show "Cleared 0 cache entries"
        assert "Cleared" not in output
        assert "Regions: eu-west-1" in output


class TestRegionFilteringWorkflow:
    """Test region filtering workflow scenarios."""

    def test_region_filter_applied_on_fresh_fetch(self, shell):
        """Test regions setting affects next discovery call."""
        # Set region first
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        shell.onecmd("set regions eu-west-1")
        sys.stdout = old_stdout

        # Verify RuntimeConfig has regions
        assert RuntimeConfig.get_regions() == ["eu-west-1"]

    def test_region_change_clears_stale_cache(self, shell):
        """Test changing regions clears cached discovery results."""
        # Simulate cached TGWs from all regions
        shell._cache["transit_gateways"] = [
            {"id": "tgw-1", "region": "us-east-1"},
            {"id": "tgw-2", "region": "eu-west-1"},
        ]

        old_stdout = sys.stdout
        sys.stdout = StringIO()

        # Change regions - should auto-clear cache
        shell.onecmd("set regions eu-west-1")
        output = sys.stdout.getvalue()

        sys.stdout = old_stdout

        # Verify cache was cleared
        assert len(shell._cache) == 0
        assert "Cleared 1 cache entries" in output

    def test_manual_refresh_still_works(self, shell):
        """Test manual refresh command still functions."""
        shell._cache["transit_gateways"] = [{"id": "tgw-1"}]

        old_stdout = sys.stdout
        sys.stdout = StringIO()

        shell.onecmd("refresh transit_gateways")
        output = sys.stdout.getvalue()

        sys.stdout = old_stdout

        assert "transit_gateways" not in shell._cache
        assert "Refreshed" in output
