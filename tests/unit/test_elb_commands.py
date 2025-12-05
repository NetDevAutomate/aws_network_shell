"""Unit tests for ELB commands (Issue #10).

Tests the 3 missing ELB context commands:
- show listeners
- show targets
- show health

Following TDD: These tests FAIL initially, proving commands don't exist.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from aws_network_tools.shell.handlers.elb import ELBHandlersMixin
from aws_network_tools.modules.elb import ELBClient
from tests.fixtures.elb import ELB_FIXTURES, LISTENER_FIXTURES, TARGET_GROUP_FIXTURES


class TestELBHandlerMethods:
    """Test ELB handler methods exist and work correctly."""

    def test_show_listeners_method_exists(self):
        """Binary: _show_listeners handler method must exist."""
        mixin = ELBHandlersMixin()
        assert hasattr(mixin, '_show_listeners'), "Missing _show_listeners handler"

    def test_show_targets_method_exists(self):
        """Binary: _show_targets handler method must exist."""
        mixin = ELBHandlersMixin()
        assert hasattr(mixin, '_show_targets'), "Missing _show_targets handler"

    def test_show_health_method_exists(self):
        """Binary: _show_health handler method must exist."""
        mixin = ELBHandlersMixin()
        assert hasattr(mixin, '_show_health'), "Missing _show_health handler"


class TestELBClientMethods:
    """Test ELB client methods for fetching listeners/targets/health."""

    def test_get_listeners_method_exists(self):
        """Binary: get_listeners client method must exist."""
        client = ELBClient()
        assert hasattr(client, 'get_listeners'), "Missing get_listeners method"

    def test_get_target_groups_method_exists(self):
        """Binary: get_target_groups client method must exist."""
        client = ELBClient()
        assert hasattr(client, 'get_target_groups'), "Missing get_target_groups method"

    def test_get_target_health_method_exists(self):
        """Binary: get_target_health client method must exist."""
        client = ELBClient()
        assert hasattr(client, 'get_target_health'), "Missing get_target_health method"


class TestELBClientFunctionality:
    """Test ELB client methods return correct data structure."""

    def test_get_listeners_returns_list(self):
        """Binary: get_listeners returns list of listener dicts."""
        elb_arn = list(ELB_FIXTURES.keys())[0]

        with patch('boto3.Session') as mock_session_class:
            mock_session = MagicMock()
            mock_client = MagicMock()
            mock_session.client.return_value = mock_client
            mock_session_class.return_value = mock_session

            # Mock AWS API response
            mock_client.describe_listeners.return_value = {
                'Listeners': list(LISTENER_FIXTURES.values())
            }

            client = ELBClient(session=mock_session)
            result = client.get_listeners(elb_arn, 'us-east-1')

            # Binary assertions
            assert isinstance(result, list), "get_listeners must return list"
            assert len(result) > 0, "Should return listener data"


class TestELBModuleProperty:
    """Test ELB module context_commands property includes new commands."""

    def test_context_commands_includes_elb_commands(self):
        """Binary: context_commands must include listeners, targets, health."""
        from aws_network_tools.modules.elb import ELBModule

        module = ELBModule()
        ctx_commands = module.context_commands

        assert 'elb' in ctx_commands, "Must define elb context commands"

        elb_commands = ctx_commands['elb']
        assert 'listeners' in elb_commands, "Missing 'listeners' command"
        assert 'targets' in elb_commands, "Missing 'targets' command"
        assert 'health' in elb_commands, "Missing 'health' command"
