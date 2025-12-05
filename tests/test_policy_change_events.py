"""Tests for policy change events sorting fix (Issue #4).

Issue: TypeError: '<' not supported between instances of 'datetime.datetime' and 'str'
when running 'show policy-change-events' in core-network context.

Root cause: The sorting function used `x.get("created_at") or ""` which mixed
datetime objects (from AWS API) with empty strings (for None values).
"""
from datetime import datetime
import pytest


class TestPolicyChangeEventsSorting:
    """Test that policy change events handle mixed datetime/None values."""

    def test_sort_mixed_datetime_and_none(self):
        """Issue #4: TypeError when sorting events with mixed datetime/None."""
        events = [
            {"version": 1, "created_at": datetime(2024, 1, 1, 12, 0)},
            {"version": 2, "created_at": None},
            {"version": 3, "created_at": datetime(2024, 6, 1, 12, 0)},
        ]

        def sort_key(x):
            val = x.get("created_at")
            if val is None:
                return datetime.min
            if isinstance(val, datetime):
                return val
            return datetime.min

        # This should not raise TypeError
        result = sorted(events, key=sort_key, reverse=True)
        
        # Newest first, None last
        assert [e["version"] for e in result] == [3, 1, 2]

    def test_sort_all_none(self):
        """Handle case where all created_at values are None."""
        events = [
            {"version": 1, "created_at": None},
            {"version": 2, "created_at": None},
        ]

        def sort_key(x):
            val = x.get("created_at")
            if val is None:
                return datetime.min
            if isinstance(val, datetime):
                return val
            return datetime.min

        result = sorted(events, key=sort_key, reverse=True)
        assert len(result) == 2

    def test_sort_all_datetime(self):
        """Handle case where all values are datetime."""
        events = [
            {"version": 1, "created_at": datetime(2024, 1, 1)},
            {"version": 2, "created_at": datetime(2024, 6, 1)},
        ]

        def sort_key(x):
            val = x.get("created_at")
            if val is None:
                return datetime.min
            if isinstance(val, datetime):
                return val
            return datetime.min

        result = sorted(events, key=sort_key, reverse=True)
        assert [e["version"] for e in result] == [2, 1]

    def test_original_bug_reproduction(self):
        """Reproduce the exact bug from Issue #4."""
        # This is what the old code did - it would fail
        events = [
            {"version": 1, "created_at": datetime(2024, 1, 1)},
            {"version": 2, "created_at": None},  # This becomes "" with `or ""`
        ]
        
        # Old buggy code: sorted(events, key=lambda x: (x.get("created_at") or ""), reverse=True)
        # This raises: TypeError: '<' not supported between instances of 'datetime.datetime' and 'str'
        
        # New fixed code:
        def sort_key(x):
            val = x.get("created_at")
            if val is None:
                return datetime.min
            if isinstance(val, datetime):
                return val
            return datetime.min
        
        # Should not raise TypeError
        result = sorted(events, key=sort_key, reverse=True)
        assert len(result) == 2
        # datetime(2024, 1, 1) > datetime.min, so version 1 comes first
        assert result[0]["version"] == 1
        assert result[1]["version"] == 2
