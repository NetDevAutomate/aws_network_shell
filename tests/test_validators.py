"""Tests for input validators."""

import pytest
from aws_network_tools.core.validators import (
    validate_regions,
    validate_profile,
    validate_output_format,
)


class TestRegionValidation:
    """Test region input validation."""

    def test_valid_single_region(self):
        """Test single valid region."""
        is_valid, regions, error = validate_regions("us-east-1")
        assert is_valid
        assert regions == ["us-east-1"]
        assert error is None

    def test_valid_multiple_regions_comma_separated(self):
        """Test multiple regions with comma separation."""
        is_valid, regions, error = validate_regions("us-east-1,eu-west-1,ap-southeast-1")
        assert is_valid
        assert regions == ["us-east-1", "eu-west-1", "ap-southeast-1"]
        assert error is None

    def test_valid_regions_with_spaces_after_commas(self):
        """Test regions with spaces after commas (should be trimmed)."""
        is_valid, regions, error = validate_regions("us-east-1, eu-west-1, ap-southeast-1")
        assert is_valid
        assert regions == ["us-east-1", "eu-west-1", "ap-southeast-1"]
        assert error is None

    def test_invalid_space_separated_regions(self):
        """Test space-separated regions (common mistake)."""
        is_valid, regions, error = validate_regions("us-east-1 eu-west-1")
        assert not is_valid
        assert regions is None
        assert "comma-separated" in error
        assert "✗ Wrong" in error
        assert "✓ Right" in error

    def test_invalid_region_code(self):
        """Test invalid region code."""
        is_valid, regions, error = validate_regions("invalid-region")
        assert not is_valid
        assert regions is None
        assert "Invalid region codes" in error
        assert "invalid-region" in error

    def test_invalid_mixed_with_valid(self):
        """Test mix of valid and invalid regions."""
        is_valid, regions, error = validate_regions("us-east-1,bad-region,eu-west-1")
        assert not is_valid
        assert regions is None
        assert "Invalid region codes" in error
        assert "bad-region" in error

    def test_empty_string_returns_empty_list(self):
        """Test empty string returns valid with empty list."""
        is_valid, regions, error = validate_regions("")
        assert is_valid
        assert regions == []
        assert error is None

    def test_whitespace_only_returns_empty_list(self):
        """Test whitespace-only returns valid with empty list."""
        is_valid, regions, error = validate_regions("   ")
        assert is_valid
        assert regions == []
        assert error is None

    def test_suggestions_for_typos(self):
        """Test that suggestions are provided for typos."""
        is_valid, regions, error = validate_regions("us-east")
        assert not is_valid
        assert "Did you mean?" in error
        assert "us-east-1" in error or "us-east-2" in error

    def test_all_major_regions_valid(self):
        """Test all major AWS regions are recognized."""
        major_regions = [
            "us-east-1", "us-west-2", "eu-west-1", "eu-central-1",
            "ap-southeast-1", "ap-northeast-1", "ca-central-1", "sa-east-1"
        ]
        for region in major_regions:
            is_valid, regions, error = validate_regions(region)
            assert is_valid, f"Region {region} should be valid"
            assert regions == [region]

    def test_new_region_pattern_allowed(self):
        """Test that unknown regions matching AWS pattern are allowed."""
        # Hypothetical new region following AWS naming pattern
        is_valid, regions, error = validate_regions("eu-north-5")
        # Should be valid (matches pattern even if not in known list yet)
        assert is_valid or regions == ["eu-north-5"]


class TestProfileValidation:
    """Test profile input validation."""

    def test_valid_alphanumeric_profile(self):
        """Test valid alphanumeric profile name."""
        is_valid, profile, error = validate_profile("production")
        assert is_valid
        assert profile == "production"
        assert error is None

    def test_valid_profile_with_hyphens(self):
        """Test profile with hyphens."""
        is_valid, profile, error = validate_profile("prod-account-1")
        assert is_valid
        assert profile == "prod-account-1"
        assert error is None

    def test_valid_profile_with_underscores(self):
        """Test profile with underscores."""
        is_valid, profile, error = validate_profile("prod_account_1")
        assert is_valid
        assert profile == "prod_account_1"
        assert error is None

    def test_invalid_profile_with_spaces(self):
        """Test invalid profile with spaces."""
        is_valid, profile, error = validate_profile("my profile")
        assert not is_valid
        assert profile is None
        assert "Invalid profile name" in error

    def test_invalid_profile_with_special_chars(self):
        """Test invalid profile with special characters."""
        is_valid, profile, error = validate_profile("prod@account")
        assert not is_valid
        assert profile is None
        assert "Invalid profile name" in error

    def test_empty_profile_returns_none(self):
        """Test empty profile returns valid with None."""
        is_valid, profile, error = validate_profile("")
        assert is_valid
        assert profile is None
        assert error is None

    def test_whitespace_profile_returns_none(self):
        """Test whitespace-only profile returns valid with None."""
        is_valid, profile, error = validate_profile("   ")
        assert is_valid
        assert profile is None
        assert error is None


class TestOutputFormatValidation:
    """Test output format validation."""

    def test_valid_table_format(self):
        """Test valid table format."""
        is_valid, fmt, error = validate_output_format("table")
        assert is_valid
        assert fmt == "table"
        assert error is None

    def test_valid_json_format(self):
        """Test valid JSON format."""
        is_valid, fmt, error = validate_output_format("json")
        assert is_valid
        assert fmt == "json"
        assert error is None

    def test_valid_yaml_format(self):
        """Test valid YAML format."""
        is_valid, fmt, error = validate_output_format("yaml")
        assert is_valid
        assert fmt == "yaml"
        assert error is None

    def test_case_insensitive_format(self):
        """Test format validation is case-insensitive."""
        is_valid, fmt, error = validate_output_format("JSON")
        assert is_valid
        assert fmt == "json"

    def test_invalid_format(self):
        """Test invalid output format."""
        is_valid, fmt, error = validate_output_format("xml")
        assert not is_valid
        assert fmt is None
        assert "Invalid format" in error
        assert "xml" in error
        assert "table" in error  # Shows valid options

    def test_empty_format_returns_error(self):
        """Test empty format returns error."""
        is_valid, fmt, error = validate_output_format("")
        assert not is_valid
        assert fmt is None
        assert "required" in error

    def test_whitespace_format_returns_error(self):
        """Test whitespace-only format returns error."""
        is_valid, fmt, error = validate_output_format("   ")
        assert not is_valid
        assert fmt is None
        assert "required" in error
