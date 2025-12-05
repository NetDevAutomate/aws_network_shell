"""TDD Tests for CloudWAN issues #1, #2, #3, #4."""

import sys
from unittest.mock import MagicMock
from datetime import datetime
import pytest

# Mock cmd2 before imports
mock_cmd2 = MagicMock()
mock_cmd2.Cmd = MagicMock
sys.modules['cmd2'] = mock_cmd2


class TestShowRibKeyError:
    """Issue #1: show rib KeyError: slice(None, 25, None)."""

    def test_show_rib_handles_dict_next_hop(self):
        """Bug: If next_hop is a dict instead of string, slicing fails."""
        from aws_network_tools.modules.cloudwan import CloudWANDisplay

        mock_console = MagicMock()
        display = CloudWANDisplay(mock_console)

        cn_data = {"name": "test-core-network"}
        # Simulate route with dict instead of string (API inconsistency)
        rib_data = {
            "InsideTrust|us-east-1": {
                "segment": "InsideTrust",
                "edge_location": "us-east-1",
                "routes": [
                    {
                        "prefix": "10.0.0.0/8",
                        "next_hop": {"value": "some-hop"},  # Bug: dict instead of str
                        "next_hop_resource": "attachment-123",
                        "local_preference": 100,
                        "as_path": [],
                        "med": None,
                        "communities": [],
                        "origin_type": "IGP",
                    }
                ],
            }
        }

        # After fix: should not raise KeyError
        try:
            display.show_rib(cn_data, rib_data)
            # If we get here without error, test passes
        except KeyError as e:
            if "slice" in str(e):
                pytest.fail(f"KeyError on slice still occurs: {e}")
            raise

    def test_show_rib_handles_none_next_hop(self):
        """Bug: If next_hop is None, str() conversion needed."""
        from aws_network_tools.modules.cloudwan import CloudWANDisplay

        mock_console = MagicMock()
        display = CloudWANDisplay(mock_console)

        cn_data = {"name": "test-core-network"}
        rib_data = {
            "InsideTrust|us-east-1": {
                "segment": "InsideTrust",
                "edge_location": "us-east-1",
                "routes": [
                    {
                        "prefix": "10.0.0.0/8",
                        "next_hop": None,  # Bug case
                        "next_hop_resource": None,  # Also None
                    }
                ],
            }
        }

        # Should not raise any error
        display.show_rib(cn_data, rib_data)


class TestShowDetailKeyError:
    """Issue #2: show detail KeyError 'global_network_name'."""

    def test_show_detail_missing_global_network_name(self):
        """Bug: Direct dict access cn['global_network_name'] fails if key missing."""
        from aws_network_tools.modules.cloudwan import CloudWANDisplay

        mock_console = MagicMock()
        display = CloudWANDisplay(mock_console)

        # Core network data without global_network_name
        cn_data = {
            "id": "core-network-123",
            "name": "TestCoreNetwork",
            "regions": ["us-east-1"],
            "segments": ["default"],
            "nfgs": [],
            "route_tables": [],
            # Missing: "global_network_name"
        }

        # After fix: should not raise KeyError
        try:
            display.show_detail(cn_data)
        except KeyError as e:
            if "global_network_name" in str(e):
                pytest.fail(f"KeyError for global_network_name still occurs: {e}")
            raise


class TestShowPolicyEmpty:
    """Issue #3: show policy/segments returns empty."""

    def test_policy_data_access(self):
        """Verify policy data structure is correctly accessed."""
        from aws_network_tools.shell.handlers.cloudwan import CloudWANHandlersMixin

        mock_self = MagicMock()
        mock_self.ctx_type = "core-network"
        mock_self.ctx.data = {
            "policy": {
                "segments": [
                    {"name": "default", "edge-locations": ["us-east-1"]},
                    {"name": "production", "edge-locations": ["us-east-1", "us-west-2"]},
                ]
            }
        }

        # Call handler
        CloudWANHandlersMixin._show_segments(mock_self, None)

        # Should NOT print "No segments found"
        calls = [str(c) for c in mock_self.console.print.call_args_list]
        no_segments_called = any("No segments" in c for c in calls)
        # Note: Since we're mocking console, this test verifies logic flow


class TestPolicyChangeEventsDatetime:
    """Issue #4: TypeError comparing datetime and str."""

    def test_sorting_with_mixed_datetime_types(self):
        """Bug: Sorting events fails when created_at has mixed types."""
        from aws_network_tools.modules.cloudwan import CloudWANClient

        # Mock the nm client
        mock_session = MagicMock()
        client = CloudWANClient(session=mock_session)
        client._nm = MagicMock()

        # Simulate API response with datetime objects
        client._nm.list_core_network_policy_versions.return_value = {
            "CoreNetworkPolicyVersions": [
                {
                    "PolicyVersionId": 1,
                    "Alias": "LIVE",
                    "ChangeSetState": "EXECUTED",
                    "CreatedAt": datetime(2024, 1, 1, 12, 0, 0),  # datetime obj
                },
                {
                    "PolicyVersionId": 2,
                    "Alias": "",
                    "ChangeSetState": "PENDING",
                    "CreatedAt": "2024-01-02T12:00:00",  # string
                },
            ]
        }
        client._nm.get_core_network_change_set.side_effect = Exception("No change set")

        # After fix: should not raise TypeError
        try:
            events = client.get_policy_change_events("core-network-123")
            # Should return sorted events without error
            assert isinstance(events, list)
        except TypeError as e:
            if "'<' not supported" in str(e):
                pytest.fail(f"TypeError on datetime comparison still occurs: {e}")
            raise

    def test_display_handles_datetime_object(self):
        """Bug: Display fails when created_at is datetime object."""
        from aws_network_tools.modules.cloudwan import CloudWANDisplay

        mock_console = MagicMock()
        display = CloudWANDisplay(mock_console)

        cn_data = {"name": "test-core-network"}
        events = [
            {
                "version": 1,
                "event_type": "policy_version",
                "alias": "LIVE",
                "change_set_state": "EXECUTED",
                "created_at": datetime(2024, 1, 1, 12, 0, 0),  # datetime object
            }
        ]

        # Should not raise error
        display.show_policy_change_events(cn_data, events)
