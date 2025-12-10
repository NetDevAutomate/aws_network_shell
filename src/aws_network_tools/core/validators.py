"""Input validation utilities for shell commands."""

import re
from typing import Tuple, List, Optional

# AWS region pattern: 2-3 letter region code + '-' + direction + '-' + number
# Examples: us-east-1, eu-west-2, ap-southeast-1, ca-central-1
AWS_REGION_PATTERN = re.compile(
    r"^(us|eu|ap|sa|ca|me|af|il)-(north|south|east|west|central|northeast|southeast|southwest|northwest)-\d+$"
)

# Known AWS regions (as of 2025)
VALID_AWS_REGIONS = {
    # US regions
    "us-east-1", "us-east-2", "us-west-1", "us-west-2",
    # Europe regions
    "eu-west-1", "eu-west-2", "eu-west-3", "eu-central-1",
    "eu-central-2", "eu-north-1", "eu-south-1", "eu-south-2",
    # Asia Pacific
    "ap-south-1", "ap-south-2", "ap-northeast-1", "ap-northeast-2",
    "ap-northeast-3", "ap-southeast-1", "ap-southeast-2",
    "ap-southeast-3", "ap-southeast-4", "ap-east-1",
    # Other regions
    "ca-central-1", "ca-west-1",
    "sa-east-1",
    "me-south-1", "me-central-1",
    "af-south-1",
    "il-central-1",
    # GovCloud
    "us-gov-east-1", "us-gov-west-1",
    # China (special)
    "cn-north-1", "cn-northwest-1",
}


def validate_regions(region_input: str) -> Tuple[bool, Optional[List[str]], Optional[str]]:
    """Validate region input string.

    Args:
        region_input: User input string (comma-separated regions or single region)

    Returns:
        Tuple of (is_valid, parsed_regions, error_message)
        - is_valid: True if input is valid
        - parsed_regions: List of validated region codes (None if invalid)
        - error_message: User-friendly error message (None if valid)
    """
    if not region_input or not region_input.strip():
        return True, [], None

    # Check for space-separated (common mistake)
    if " " in region_input and "," not in region_input:
        return False, None, (
            "Regions must be comma-separated, not space-separated.\n"
            "  ✗ Wrong: eu-west-1 eu-west-2\n"
            "  ✓ Right: eu-west-1,eu-west-2"
        )

    # Parse comma-separated regions
    regions = [r.strip() for r in region_input.split(",") if r.strip()]

    if not regions:
        return True, [], None

    # Validate each region
    invalid_regions = []
    for region in regions:
        if region not in VALID_AWS_REGIONS:
            # Check if it matches pattern but not in known list
            if AWS_REGION_PATTERN.match(region):
                # Might be a new region - allow with warning
                continue
            else:
                invalid_regions.append(region)

    if invalid_regions:
        suggestions = _suggest_regions(invalid_regions)
        error_msg = f"Invalid region codes: {', '.join(invalid_regions)}\n"
        if suggestions:
            error_msg += f"\nDid you mean?\n"
            for invalid, suggested in suggestions.items():
                error_msg += f"  {invalid} → {', '.join(suggested)}\n"
        error_msg += f"\nValid examples: us-east-1, eu-west-1, ap-southeast-1"
        return False, None, error_msg

    return True, regions, None


def _suggest_regions(invalid_regions: List[str]) -> dict:
    """Suggest corrections for invalid region codes.

    Returns:
        Dict mapping invalid region to list of suggestions
    """
    suggestions = {}

    for invalid in invalid_regions:
        matches = []
        invalid_lower = invalid.lower()

        # Try fuzzy matching
        for valid_region in VALID_AWS_REGIONS:
            # Check if invalid is substring of valid
            if invalid_lower in valid_region:
                matches.append(valid_region)
            # Check if they share common prefix (us-, eu-, ap-)
            elif invalid_lower[:3] == valid_region[:3]:
                matches.append(valid_region)

        if matches:
            # Limit to top 3 suggestions
            suggestions[invalid] = sorted(matches)[:3]

    return suggestions


def validate_profile(profile_input: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """Validate AWS profile name.

    Args:
        profile_input: User input profile name

    Returns:
        Tuple of (is_valid, profile_name, error_message)
    """
    if not profile_input or not profile_input.strip():
        return True, None, None

    profile = profile_input.strip()

    # Check for invalid characters (AWS profile names are alphanumeric + _-)
    if not re.match(r"^[a-zA-Z0-9_-]+$", profile):
        return False, None, (
            f"Invalid profile name: '{profile}'\n"
            "Profile names must contain only letters, numbers, hyphens, and underscores"
        )

    return True, profile, None


def validate_output_format(format_input: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """Validate output format.

    Args:
        format_input: User input format string

    Returns:
        Tuple of (is_valid, format, error_message)
    """
    if not format_input or not format_input.strip():
        return False, None, "Output format required"

    fmt = format_input.strip().lower()
    valid_formats = {"table", "json", "yaml"}

    if fmt not in valid_formats:
        return False, None, (
            f"Invalid format: '{fmt}'\n"
            f"Valid formats: {', '.join(sorted(valid_formats))}"
        )

    return True, fmt, None
