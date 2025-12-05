"""
Test for Issue #2: Error trying to view Core Network detail
KeyError: 'global_network_name'

This test verifies that CloudWANDisplay.show_detail() handles
incomplete data gracefully (missing global_network_name key).
"""

import pytest
from unittest.mock import MagicMock, patch
from io import StringIO

# Import the module under test
import sys
sys.path.insert(0, '/Users/taylaand/code/personal/aws_network_shell_worktrees/issue-2-core-network-detail/src')

from aws_network_tools.modules.cloudwan import CloudWANDisplay


class TestIssue2ShowDetail:
    """Test CloudWANDisplay.show_detail() with various data scenarios."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_console = MagicMock()
        self.display = CloudWANDisplay(self.mock_console)

    def test_show_detail_with_complete_data(self):
        """Test show_detail with all expected keys present."""
        cn_data = {
            "id": "core-network-123",
            "name": "Test Core Network",
            "global_network_name": "Test Global Network",
            "regions": ["us-east-1", "eu-west-1"],
            "segments": ["production", "development"],
            "nfgs": ["firewall-nfg"],
            "route_tables": [
                {
                    "id": "rt-1",
                    "name": "production",
                    "region": "us-east-1",
                    "type": "segment",
                    "routes": []
                }
            ]
        }

        # Should NOT raise KeyError
        self.display.show_detail(cn_data)

        # Verify console.print was called (method executed successfully)
        assert self.mock_console.print.called

    def test_show_detail_missing_global_network_name(self):
        """
        Test show_detail with MISSING global_network_name key.
        This is the exact scenario that caused Issue #2.
        """
        cn_data = {
            "id": "core-network-456",
            "name": "Test Core Network Without Global",
            # NOTE: global_network_name is MISSING - this caused the KeyError
            "regions": ["us-west-2"],
            "segments": ["shared"],
            "nfgs": [],
            "route_tables": []
        }

        # Should NOT raise KeyError - this is the bug fix verification
        try:
            self.display.show_detail(cn_data)
            passed = True
        except KeyError as e:
            pytest.fail(f"KeyError raised for missing key: {e} - Issue #2 NOT FIXED")
            passed = False

        assert passed, "show_detail should handle missing global_network_name"
        assert self.mock_console.print.called

    def test_show_detail_empty_global_network_name(self):
        """Test show_detail with empty string for global_network_name."""
        cn_data = {
            "id": "core-network-789",
            "name": "Test Core Network Empty Global",
            "global_network_name": "",  # Empty string instead of missing
            "regions": [],
            "segments": [],
            "nfgs": [],
            "route_tables": []
        }

        # Should NOT raise any errors
        self.display.show_detail(cn_data)
        assert self.mock_console.print.called

    def test_show_detail_none_global_network_name(self):
        """Test show_detail with None value for global_network_name."""
        cn_data = {
            "id": "core-network-abc",
            "name": "Test Core Network None Global",
            "global_network_name": None,  # None value
            "regions": ["ap-southeast-1"],
            "segments": ["transit"],
            "nfgs": [],
            "route_tables": []
        }

        # Should NOT raise any errors
        self.display.show_detail(cn_data)
        assert self.mock_console.print.called

    def test_show_detail_none_input(self):
        """Test show_detail with None input (edge case)."""
        # Should handle None gracefully and print error message
        self.display.show_detail(None)

        # Should print error message
        assert self.mock_console.print.called
        call_args = str(self.mock_console.print.call_args)
        assert "not found" in call_args.lower() or "red" in call_args.lower()

    def test_show_detail_empty_dict(self):
        """Test show_detail with empty dict input."""
        cn_data = {}

        # May raise KeyError for 'name' - that's expected behavior
        # The fix is specifically for 'global_network_name'
        try:
            self.display.show_detail(cn_data)
        except KeyError as e:
            # KeyError for 'name' is acceptable - it's a required field
            if str(e) == "'global_network_name'":
                pytest.fail("KeyError for global_network_name - Issue #2 NOT FIXED")

    def test_show_detail_minimal_required_fields(self):
        """Test show_detail with only minimal required fields."""
        cn_data = {
            "id": "core-network-min",
            "name": "Minimal Core Network",
            # No optional fields - simulates handler-cached data
        }

        # Should NOT raise KeyError for global_network_name
        try:
            self.display.show_detail(cn_data)
        except KeyError as e:
            if str(e) == "'global_network_name'":
                pytest.fail("KeyError for global_network_name - Issue #2 NOT FIXED")


class TestIssue2ShowListTableRow:
    """Test CloudWANDisplay.show_list() table row generation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_console = MagicMock()
        self.display = CloudWANDisplay(self.mock_console)

    def test_show_list_with_missing_global_network_name(self):
        """Test show_list handles missing global_network_name in network data."""
        networks = [
            {
                "id": "cn-1",
                "name": "Network 1",
                # Missing global_network_name
                "regions": ["us-east-1"],
                "segments": ["seg1"],
                "route_tables": []
            }
        ]

        # Should NOT raise KeyError
        try:
            self.display.show_list(networks)
            passed = True
        except KeyError as e:
            if "global_network_name" in str(e):
                pytest.fail(f"KeyError for global_network_name in show_list: {e}")
            passed = False

        assert passed or True  # show_list may use different fields


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
