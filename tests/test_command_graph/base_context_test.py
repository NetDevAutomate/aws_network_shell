"""Base test case class for command graph testing.

Provides reusable helpers for testing CLI command sequences, context transitions,
and resource validation. Uses composition pattern with command_runner fixture.

Design Philosophy (per Kimi K2):
- Simple foundation for immediate needs
- Extensible for future state machine integration
- Focus on show→set pattern and context validation
"""

import pytest


class BaseContextTestCase:
    """Base class for all command graph context tests.

    Provides:
    - Isolated shell instance per test
    - Command execution helpers (execute_sequence, show_set_sequence)
    - Context validation helpers (assert_context, assert_context_depth)
    - Resource counting helpers (assert_resource_count)

    Usage:
        class TestVPCContext(BaseContextTestCase):
            def test_vpc_navigation(self):
                self.show_set_sequence('vpc', 1)
                self.assert_context('vpc')
    """

    @pytest.fixture(autouse=True)
    def _setup_base_context(self, isolated_shell, command_runner):
        """Auto-inject shell and command runner for every test.

        Args:
            isolated_shell: Fresh shell instance from conftest.py
            command_runner: Command execution helper from conftest.py
        """
        self.shell = isolated_shell
        self.command_runner = command_runner

    def execute_sequence(self, commands: list[str]) -> list[dict] | dict:
        """Execute command sequence and return results.

        Stops on first failure to prevent cascading errors.

        Args:
            commands: List of command strings to execute sequentially

        Returns:
            If single command: dict with exit_code, output, success
            If multiple commands: list of result dicts

        Example:
            results = self.execute_sequence(['show vpcs', 'set vpc 1'])
            assert all(r['exit_code'] == 0 for r in results)
        """
        if len(commands) == 1:
            return self.command_runner.run(commands[0])

        return self.command_runner.run_chain(commands)

    def show_set_sequence(self, resource_type: str, index: int = 1) -> dict:
        """Execute standard show→set command pattern.

        This is the CRITICAL pattern for context entry:
        1. show command displays indexed table
        2. set command uses index to enter context

        Args:
            resource_type: Resource type (vpc, transit-gateway, global-network, etc.)
            index: 1-based index from show command output (default: 1)

        Returns:
            Result dict from set command

        Raises:
            AssertionError: If show or set command fails

        Example:
            self.show_set_sequence('vpc', 1)
            assert self.shell.ctx_type == 'vpc'
        """
        # Determine correct show/set command forms
        show_cmd = self._get_show_command(resource_type)
        set_cmd = self._get_set_command(resource_type)

        # Execute show→set sequence
        results = self.execute_sequence([show_cmd, f'{set_cmd} {index}'])

        # Validate both commands succeeded
        assert results[0]['exit_code'] == 0, f"show command failed: {results[0].get('output', '')}"
        assert results[1]['exit_code'] == 0, f"set command failed: {results[1].get('output', '')}"

        return results[1]

    def _get_show_command(self, resource_type: str) -> str:
        """Get correct show command for resource type.

        Handles pluralization and command name mapping.
        """
        # Special cases with underscore commands
        if resource_type == 'transit-gateway':
            return 'show transit_gateways'  # Underscore, not hyphen
        elif resource_type == 'global-network':
            return 'show global-networks'
        elif resource_type == 'core-network':
            return 'show core-networks'

        # Default: add 's' for plural
        return f'show {resource_type}s'

    def _get_set_command(self, resource_type: str) -> str:
        """Get correct set command for resource type."""
        return f'set {resource_type}'

    def assert_context(self, expected_type: str, has_data: bool = False):
        """Assert shell is in expected context type.

        Args:
            expected_type: Expected context type (vpc, transit-gateway, etc.)
            has_data: If True, also validate context has resource data

        Raises:
            AssertionError: If context doesn't match or data missing

        Example:
            self.assert_context('vpc')
            self.assert_context('vpc', has_data=True)
        """
        actual_type = self.shell.ctx_type
        assert actual_type == expected_type, (
            f"Expected context '{expected_type}', got '{actual_type}'"
        )

        if has_data:
            assert self.shell.ctx_id is not None, "Context has no resource ID"

    def assert_context_depth(self, expected_depth: int):
        """Assert context stack has expected depth.

        Args:
            expected_depth: Expected number of contexts in stack

        Raises:
            AssertionError: If depth doesn't match

        Example:
            self.assert_context_depth(1)  # Single context
            self.assert_context_depth(2)  # Nested context
        """
        actual_depth = len(self.shell.context_stack)
        assert actual_depth == expected_depth, (
            f"Expected context depth {expected_depth}, got {actual_depth}"
        )

    def assert_resource_count(self, output: str, resource_name: str, min_count: int = 1):
        """Assert output contains minimum resource count.

        Args:
            output: Command output text
            resource_name: Resource identifier to count (e.g., 'vpc-', 'subnet-')
            min_count: Minimum expected occurrences

        Raises:
            AssertionError: If count below minimum

        Example:
            result = self.command_runner.run('show vpcs')
            self.assert_resource_count(result['output'], 'vpc-', min_count=3)
        """
        count = output.count(resource_name)
        assert count >= min_count, (
            f"Expected at least {min_count} '{resource_name}' in output, found {count}"
        )
