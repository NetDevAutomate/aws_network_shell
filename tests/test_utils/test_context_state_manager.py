"""Tests for ContextStateManager - validates context transitions and state.

Following TDD methodology: Define expected state tracking before implementation.

Key Requirements (from Kimi K2):
- Track expected context stack for validation
- Simple state tracking (not full state machine yet)
- Integration with shell.context_stack
"""

import pytest
from tests.test_utils.context_state_manager import ContextStateManager
from aws_network_tools.shell.main import AWSNetShell


class TestContextStateManagerInit:
    """Test ContextStateManager initialization."""

    def test_manager_initialization(self):
        """Binary: Manager initializes with shell reference."""
        shell = AWSNetShell()
        manager = ContextStateManager(shell)

        assert manager is not None
        assert manager.shell == shell

    def test_expected_stack_empty(self):
        """Binary: Expected stack starts empty."""
        shell = AWSNetShell()
        manager = ContextStateManager(shell)

        assert len(manager.expected_stack) == 0


class TestPushContext:
    """Test push_context() method."""

    @pytest.fixture
    def manager(self):
        shell = AWSNetShell()
        return ContextStateManager(shell)

    def test_push_single_context(self, manager):
        """Binary: Push single context to expected stack."""
        manager.push_context('vpc', {'vpc_id': 'vpc-123'})

        assert len(manager.expected_stack) == 1
        assert manager.expected_stack[0][0] == 'vpc'

    def test_push_multiple_contexts(self, manager):
        """Binary: Push multiple contexts maintains order."""
        manager.push_context('global-network', {'gn_id': 'gn-123'})
        manager.push_context('core-network', {'cn_id': 'cn-456'})

        assert len(manager.expected_stack) == 2
        assert manager.expected_stack[0][0] == 'global-network'
        assert manager.expected_stack[1][0] == 'core-network'


class TestValidateCurrentState:
    """Test validate_current_state() method."""

    @pytest.fixture
    def manager(self):
        shell = AWSNetShell()
        shell.no_cache = True
        return ContextStateManager(shell)

    def test_validate_empty_state(self, manager):
        """Binary: Empty shell stack matches empty expected stack."""
        # Both should be empty
        manager.validate_current_state()  # Should not raise

    def test_validate_single_context_match(self, manager):
        """Binary: Single context validates successfully."""
        # Manually set shell context
        from aws_network_tools.core import Context
        manager.shell.context_stack = [
            Context(type='vpc', ref='1', name='production-vpc', data={})
        ]

        # Set expected
        manager.push_context('vpc', {})

        # Validate
        manager.validate_current_state()  # Should not raise

    def test_validate_depth_mismatch(self, manager):
        """Binary: Depth mismatch raises AssertionError."""
        # Shell has context, expected is empty
        from aws_network_tools.core import Context
        manager.shell.context_stack = [
            Context(type='vpc', ref='1', name='test', data={})
        ]

        with pytest.raises(AssertionError, match="stack depth"):
            manager.validate_current_state()

    def test_validate_type_mismatch(self, manager):
        """Binary: Context type mismatch raises AssertionError."""
        from aws_network_tools.core import Context
        manager.shell.context_stack = [
            Context(type='vpc', ref='1', name='test', data={})
        ]
        manager.push_context('tgw', {})  # Expected tgw, got vpc

        with pytest.raises(AssertionError, match="[Cc]ontext type"):
            manager.validate_current_state()


class TestPopContext:
    """Test pop_context() method."""

    @pytest.fixture
    def manager(self):
        shell = AWSNetShell()
        return ContextStateManager(shell)

    def test_pop_single_context(self, manager):
        """Binary: Pop removes last context from expected stack."""
        manager.push_context('vpc', {})
        manager.push_context('subnet', {})

        manager.pop_context()
        assert len(manager.expected_stack) == 1
        assert manager.expected_stack[0][0] == 'vpc'

    def test_pop_empty_stack_raises(self, manager):
        """Binary: Pop on empty stack raises error."""
        with pytest.raises(IndexError):
            manager.pop_context()


class TestResetState:
    """Test reset() method."""

    @pytest.fixture
    def manager(self):
        shell = AWSNetShell()
        return ContextStateManager(shell)

    def test_reset_clears_expected_stack(self, manager):
        """Binary: Reset clears expected stack."""
        manager.push_context('vpc', {})
        manager.push_context('subnet', {})

        manager.reset()
        assert len(manager.expected_stack) == 0


class TestGetCurrentContextType:
    """Test get_current_context_type() helper."""

    @pytest.fixture
    def manager(self):
        shell = AWSNetShell()
        return ContextStateManager(shell)

    def test_get_empty_context_type(self, manager):
        """Binary: Empty stack returns None."""
        assert manager.get_current_context_type() is None

    def test_get_current_context_type(self, manager):
        """Binary: Returns top of expected stack."""
        manager.push_context('vpc', {})
        assert manager.get_current_context_type() == 'vpc'

        manager.push_context('subnet', {})
        assert manager.get_current_context_type() == 'subnet'
