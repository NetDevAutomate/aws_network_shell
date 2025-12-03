"""TDD tests for cache management commands."""

import pytest
from aws_network_tools.shell import AWSNetShell, HIERARCHY

PROFILE = "taylaand+net-dev-Admin"


class TestCacheHierarchy:
    """Test cache commands are in hierarchy."""

    def test_show_cache_in_root_hierarchy(self):
        """show cache must be available at root level."""
        assert "cache" in HIERARCHY[None]["show"]

    def test_populate_cache_in_root_commands(self):
        """populate_cache must be available at root level."""
        assert "populate_cache" in HIERARCHY[None]["commands"]


class TestShowCache:
    """Test show cache command."""

    def test_show_cache_displays_status(self):
        """show cache must display cache status without error."""
        shell = AWSNetShell()
        shell.profile = PROFILE
        # Should not raise
        shell._show_cache(None)
        # Test passes if no exception


class TestPopulateCache:
    """Test populate-cache command."""

    def test_populate_cache_exists(self):
        """populate-cache command must exist."""
        shell = AWSNetShell()
        assert hasattr(shell, "do_populate_cache")


class TestNoCacheFlag:
    """Test --no-cache flag handling."""

    def test_no_cache_property_default_false(self):
        """no_cache must default to False."""
        shell = AWSNetShell()
        assert shell.no_cache is False

    def test_set_no_cache_on(self):
        """set no-cache on must enable no_cache."""
        shell = AWSNetShell()
        shell.do_set("no-cache on")
        assert shell.no_cache is True

    def test_set_no_cache_off(self):
        """set no-cache off must disable no_cache."""
        shell = AWSNetShell()
        shell.no_cache = True
        shell.do_set("no-cache off")
        assert shell.no_cache is False


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
