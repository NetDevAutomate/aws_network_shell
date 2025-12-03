"""Tests for cache module"""

import time
import pytest

from aws_network_tools.core.cache import (
    Cache,
    get_default_ttl,
    set_default_ttl,
    parse_ttl,
)


class TestParseTTL:
    def test_parse_minutes(self):
        assert parse_ttl("15m") == 900
        assert parse_ttl("1m") == 60

    def test_parse_hours(self):
        assert parse_ttl("1h") == 3600
        assert parse_ttl("2h") == 7200

    def test_parse_days(self):
        assert parse_ttl("1d") == 86400
        assert parse_ttl("2d") == 172800

    def test_parse_plain_number(self):
        # Plain number defaults to minutes
        assert parse_ttl("30") == 1800

    def test_parse_invalid(self):
        with pytest.raises(ValueError):
            parse_ttl("invalid")
        with pytest.raises(ValueError):
            parse_ttl("10x")


class TestDefaultTTL:
    def test_get_set_default_ttl(self):
        original = get_default_ttl()
        set_default_ttl(1800)
        assert get_default_ttl() == 1800
        set_default_ttl(original)  # Restore


class TestCache:
    @pytest.fixture
    def temp_cache(self, tmp_path):
        """Create a cache with temporary directory"""
        cache = Cache("test")
        cache.cache_file = tmp_path / "test.json"
        return cache

    def test_cache_init(self, temp_cache):
        assert temp_cache.namespace == "test"

    def test_cache_set_get(self, temp_cache):
        data = {"key": "value"}
        temp_cache.set(data, account_id="123456789")

        result = temp_cache.get(current_account="123456789")
        assert result == data

    def test_cache_get_empty(self, temp_cache):
        result = temp_cache.get()
        assert result is None

    def test_cache_clear(self, temp_cache):
        temp_cache.set({"key": "value"}, account_id="123")
        temp_cache.clear()
        assert temp_cache.get() is None

    def test_cache_expired(self, temp_cache):
        data = {"key": "value"}
        temp_cache.set(data, account_id="123", ttl_seconds=1)

        # Wait for expiry
        time.sleep(1.1)

        result = temp_cache.get(current_account="123")
        assert result is None

    def test_cache_different_account(self, temp_cache):
        data = {"key": "value"}
        temp_cache.set(data, account_id="123")

        # Different account should return None
        result = temp_cache.get(current_account="456")
        assert result is None

    def test_cache_get_info(self, temp_cache):
        temp_cache.set({"key": "value"}, account_id="123")
        info = temp_cache.get_info()

        assert info is not None
        assert info["account_id"] == "123"
        assert "cached_at" in info
        assert "expired" in info

    def test_cache_get_info_empty(self, temp_cache):
        info = temp_cache.get_info()
        assert info is None

    def test_cache_ignore_expiry(self, temp_cache):
        temp_cache.set({"key": "value"}, account_id="123", ttl_seconds=1)
        time.sleep(1.1)
        # Should return None normally
        assert temp_cache.get(current_account="123") is None
        # But with ignore_expiry, should return data
        assert temp_cache.get(ignore_expiry=True) == {"key": "value"}
