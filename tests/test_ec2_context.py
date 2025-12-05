"""TDD Tests for EC2 context - Issue #9: show enis/security-groups returns all account data.

These tests are written FIRST to verify the bug exists and will guide the fix.
Root Cause: MRO places RootHandlersMixin._show_enis before EC2HandlersMixin._show_enis.
The fix: Root handlers should check ctx_type and skip when in specific context.
"""

import sys
import pytest
from unittest.mock import MagicMock, patch
from dataclasses import dataclass

# Mock cmd2 BEFORE importing shell modules
mock_cmd2 = MagicMock()
mock_cmd2.Cmd = MagicMock
sys.modules['cmd2'] = mock_cmd2


@dataclass
class MockContext:
    """Mock Context object for testing."""
    ctx_type: str
    ref: str
    label: str
    data: dict


class TestRootHandlerContextAwareness:
    """Test that root handlers are context-aware after the fix."""

    def test_root_show_enis_skips_when_in_ec2_context(self):
        """Bug: _show_enis in root.py should skip when ctx_type == 'ec2-instance'.

        The root handler fetches ALL ENIs. When in EC2 instance context,
        it should NOT run - let the EC2 handler show instance-specific ENIs.
        """
        from aws_network_tools.shell.handlers.root import RootHandlersMixin

        # Create a mock shell object with EC2 instance context
        mock_self = MagicMock()
        mock_self.ctx_type = "ec2-instance"
        mock_self.ctx = MockContext(
            ctx_type="ec2-instance",
            ref="i-1234567890abcdef0",
            label="my-instance",
            data={
                "enis": [
                    {"id": "eni-instance-001", "private_ip": "10.0.1.100"},
                ],
            }
        )

        # Track if discover() gets called
        with patch('aws_network_tools.modules.eni.ENIClient') as mock_eni:
            mock_eni.return_value.discover.return_value = [
                {"id": "eni-all-001"},
                {"id": "eni-all-002"},
            ]

            # Call the root handler's _show_enis
            # After the fix, it should return early and NOT call discover()
            RootHandlersMixin._show_enis(mock_self, None)

            # The fix: discover() should NOT be called when in ec2-instance context
            # Before fix: This assertion fails (discover IS called via _cached)
            # After fix: This assertion passes (returns early)
            assert not mock_self._cached.called, \
                "Root _show_enis should NOT call _cached() when in ec2-instance context"

    def test_root_show_enis_runs_when_at_root_level(self):
        """Root _show_enis should run normally when at root level (no context)."""
        from aws_network_tools.shell.handlers.root import RootHandlersMixin

        mock_self = MagicMock()
        mock_self.ctx_type = None  # Root level
        mock_self.ctx = None
        mock_self._cached = MagicMock(return_value=[
            {"id": "eni-001"},
            {"id": "eni-002"},
        ])

        with patch('aws_network_tools.modules.eni.ENIDisplay'):
            # At root level, the handler should run and use _cached
            RootHandlersMixin._show_enis(mock_self, None)

            # Should call _cached to fetch ENIs at root level
            assert mock_self._cached.called, \
                "Root _show_enis should call _cached() at root level"

    def test_root_show_security_groups_skips_when_in_ec2_context(self):
        """Bug: _show_security_groups in root.py should skip when ctx_type == 'ec2-instance'."""
        from aws_network_tools.shell.handlers.root import RootHandlersMixin

        mock_self = MagicMock()
        mock_self.ctx_type = "ec2-instance"
        mock_self.ctx = MockContext(
            ctx_type="ec2-instance",
            ref="i-1234567890abcdef0",
            label="my-instance",
            data={
                "security_groups": [{"id": "sg-instance-001"}],
            }
        )

        # The fix: _cached should NOT be called in ec2-instance context
        RootHandlersMixin._show_security_groups(mock_self, None)

        assert not mock_self._cached.called, \
            "Root _show_security_groups should NOT call _cached() in ec2-instance context"

    def test_root_show_security_groups_skips_when_in_vpc_context(self):
        """_show_security_groups should also skip when ctx_type == 'vpc'."""
        from aws_network_tools.shell.handlers.root import RootHandlersMixin

        mock_self = MagicMock()
        mock_self.ctx_type = "vpc"
        mock_self.ctx = MockContext(
            ctx_type="vpc",
            ref="vpc-123",
            label="my-vpc",
            data={
                "security_groups": [{"id": "sg-vpc-001"}],
            }
        )

        RootHandlersMixin._show_security_groups(mock_self, None)

        assert not mock_self._cached.called, \
            "Root _show_security_groups should NOT call _cached() in vpc context"

    def test_root_show_security_groups_runs_when_at_root_level(self):
        """Root _show_security_groups should run normally at root level."""
        from aws_network_tools.shell.handlers.root import RootHandlersMixin

        mock_self = MagicMock()
        mock_self.ctx_type = None  # Root level
        mock_self.ctx = None
        mock_self._cached = MagicMock(return_value={
            "unused_groups": [],
            "risky_rules": [],
            "nacl_issues": [],
        })

        with patch('aws_network_tools.modules.security.SecurityDisplay'):
            RootHandlersMixin._show_security_groups(mock_self, None)

            # Should call _cached at root level
            assert mock_self._cached.called, \
                "Root _show_security_groups should call _cached() at root level"


class TestMRODocumentation:
    """Document the MRO issue for future reference."""

    def test_document_mro_conflict(self):
        """Document that both RootHandlersMixin and EC2HandlersMixin define _show_enis."""
        from aws_network_tools.shell.handlers.root import RootHandlersMixin
        from aws_network_tools.shell.handlers.ec2 import EC2HandlersMixin

        # Both define _show_enis - this is the source of the conflict
        assert hasattr(RootHandlersMixin, '_show_enis'), "Root has _show_enis"
        assert hasattr(EC2HandlersMixin, '_show_enis'), "EC2 has _show_enis"

        # The fix makes root handler context-aware, so MRO conflict is resolved
