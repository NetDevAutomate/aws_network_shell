"""Test for issue #8: Error trying to set VPC with VPC ID.

Issue: When using 'set vpc vpc-019dd8e2dee602c9c' (VPC ID directly),
the shell throws: AttributeError: 'NoneType' object has no attribute 'lower'

Root cause: VPCs without a Name tag have name=None in the dict.
The _resolve method used item.get("name", "").lower() which returns None
when the key exists but has value None, causing .lower() to fail.

Fix: Changed to (item.get("name") or "").lower() to handle None values.
"""

import pytest
from aws_network_tools.shell.base import AWSNetShellBase


class TestIssue8VpcSet:
    """Test cases for issue #8 - VPC set error with VPC ID."""

    def test_resolve_with_none_name_by_id(self):
        """Test _resolve handles items where name is None when searching by ID.
        
        This is the exact scenario from issue #8:
        - VPC has no Name tag, so name=None
        - User tries to set vpc by VPC ID
        - Previously failed with: AttributeError: 'NoneType' object has no attribute 'lower'
        """
        shell = AWSNetShellBase()
        
        # Simulate VPCs where some have name=None (no Name tag)
        items = [
            {"id": "vpc-0ed63bf689aae45cf", "name": None, "region": "ap-northeast-1"},
            {"id": "vpc-019dd8e2dee602c9c", "name": "DC-AB2-vpc", "region": "us-east-2"},
            {"id": "vpc-0f0e196d10a1854c8", "name": None, "region": "us-east-1"},
        ]
        
        # This was the failing case - resolving by VPC ID when name is None
        result = shell._resolve(items, "vpc-0ed63bf689aae45cf")
        assert result is not None, "Should resolve VPC by ID even when name is None"
        assert result["id"] == "vpc-0ed63bf689aae45cf"
        
    def test_resolve_with_none_name_by_name_search(self):
        """Test _resolve doesn't crash when searching by name with None names in list."""
        shell = AWSNetShellBase()
        
        items = [
            {"id": "vpc-0ed63bf689aae45cf", "name": None, "region": "ap-northeast-1"},
            {"id": "vpc-019dd8e2dee602c9c", "name": "DC-AB2-vpc", "region": "us-east-2"},
        ]
        
        # Search by name - should not crash even with None names in list
        result = shell._resolve(items, "DC-AB2-vpc")
        assert result is not None
        assert result["id"] == "vpc-019dd8e2dee602c9c"
        
    def test_resolve_by_id(self):
        """Test _resolve can find item by ID."""
        shell = AWSNetShellBase()
        items = [
            {"id": "vpc-abc123", "name": "test-vpc"},
            {"id": "vpc-def456", "name": "other-vpc"},
        ]
        
        result = shell._resolve(items, "vpc-def456")
        assert result is not None
        assert result["id"] == "vpc-def456"
        
    def test_resolve_by_name_case_insensitive(self):
        """Test _resolve can find item by name (case-insensitive)."""
        shell = AWSNetShellBase()
        items = [
            {"id": "vpc-abc123", "name": "Test-VPC"},
            {"id": "vpc-def456", "name": "Other-VPC"},
        ]
        
        result = shell._resolve(items, "test-vpc")
        assert result is not None
        assert result["id"] == "vpc-abc123"
        
    def test_resolve_by_index(self):
        """Test _resolve can find item by index."""
        shell = AWSNetShellBase()
        items = [
            {"id": "vpc-abc123", "name": "test-vpc"},
            {"id": "vpc-def456", "name": "other-vpc"},
        ]
        
        result = shell._resolve(items, "2")
        assert result is not None
        assert result["id"] == "vpc-def456"
        
    def test_resolve_not_found(self):
        """Test _resolve returns None when not found."""
        shell = AWSNetShellBase()
        items = [
            {"id": "vpc-abc123", "name": "test-vpc"},
        ]
        
        result = shell._resolve(items, "vpc-nonexistent")
        assert result is None
        
    def test_resolve_with_empty_string_name(self):
        """Test _resolve handles items where name is empty string."""
        shell = AWSNetShellBase()
        items = [
            {"id": "vpc-abc123", "name": ""},
            {"id": "vpc-def456", "name": "other-vpc"},
        ]
        
        result = shell._resolve(items, "vpc-abc123")
        assert result is not None
        assert result["id"] == "vpc-abc123"
        
    def test_resolve_all_none_names(self):
        """Test _resolve works when ALL items have name=None."""
        shell = AWSNetShellBase()
        items = [
            {"id": "vpc-abc123", "name": None},
            {"id": "vpc-def456", "name": None},
            {"id": "vpc-ghi789", "name": None},
        ]
        
        # Should still find by ID
        result = shell._resolve(items, "vpc-def456")
        assert result is not None
        assert result["id"] == "vpc-def456"
        
        # Should still find by index
        result = shell._resolve(items, "3")
        assert result is not None
        assert result["id"] == "vpc-ghi789"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
