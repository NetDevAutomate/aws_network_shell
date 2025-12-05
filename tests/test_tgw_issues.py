"""TDD Tests for Transit Gateway Issue #5."""

import sys
from unittest.mock import MagicMock
import pytest

# Mock cmd2 before imports
mock_cmd2 = MagicMock()
mock_cmd2.Cmd = MagicMock
sys.modules['cmd2'] = mock_cmd2


class TestSetRouteTableCacheKey:
    """Issue #5: set route-table stuck in loop due to cache key mismatch."""

    def test_show_route_tables_uses_correct_cache_key(self):
        """Bug: TGW handler cached with 'route_table' but _set_route_table looks for 'route-table:{ctx_id}'."""
        from aws_network_tools.shell.handlers.tgw import TGWHandlersMixin

        mock_self = MagicMock(spec=TGWHandlersMixin)
        mock_self._cache = {}
        mock_self.ctx_id = "tgw-123456"
        mock_self.ctx = MagicMock()  # Explicitly create ctx mock
        mock_self.ctx.data = {
            "route_tables": [
                {"id": "rtb-001", "name": "Production", "routes": []},
                {"id": "rtb-002", "name": "Development", "routes": []},
            ]
        }

        # Call the handler
        TGWHandlersMixin._show_transit_gateway_route_tables(mock_self)

        # After fix: cache key should be f"route-table:{ctx_id}"
        expected_key = f"route-table:{mock_self.ctx_id}"
        assert expected_key in mock_self._cache, (
            f"Cache key should be '{expected_key}' not 'route_table'. "
            f"Found keys: {list(mock_self._cache.keys())}"
        )

        # Verify route tables are cached
        assert len(mock_self._cache[expected_key]) == 2

    def test_cache_key_matches_set_route_table_lookup(self):
        """Verify cache key format matches what _set_route_table expects."""
        from aws_network_tools.shell.handlers.tgw import TGWHandlersMixin

        mock_self = MagicMock(spec=TGWHandlersMixin)
        mock_self._cache = {}
        mock_self.ctx_id = "tgw-abcdef"
        mock_self.ctx = MagicMock()  # Explicitly create ctx mock
        mock_self.ctx.data = {
            "route_tables": [
                {"id": "rtb-test", "name": "TestRT", "routes": [{"dest": "10.0.0.0/8"}]},
            ]
        }

        # Show route tables to populate cache
        TGWHandlersMixin._show_transit_gateway_route_tables(mock_self)

        # Simulate what _set_route_table does - looks up with this key format
        lookup_key = f"route-table:{mock_self.ctx_id}"
        cached_rts = mock_self._cache.get(lookup_key, [])

        # Should find the route tables, not empty list
        assert cached_rts, f"Cache lookup with '{lookup_key}' returned empty - key mismatch!"
        assert cached_rts[0]["id"] == "rtb-test"
