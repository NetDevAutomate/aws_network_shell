"""TDD tests for shell decorators - Binary pass/fail."""

from unittest.mock import patch

from aws_network_tools.core.decorators import requires_context, requires_root


class MockShell:
    """Mock shell for testing decorators."""

    def __init__(self, ctx_type=None):
        self.ctx_type = ctx_type
        self.called = False
        self.call_args = None

    @requires_context("vpc")
    def vpc_only_command(self, args):
        self.called = True
        self.call_args = args
        return "vpc_result"

    @requires_context("vpc", "transit-gateway")
    def multi_context_command(self, args):
        self.called = True
        return "multi_result"

    @requires_root
    def root_only_command(self, args):
        self.called = True
        return "root_result"


class TestRequiresContext:
    """Binary tests for requires_context decorator."""

    def test_correct_context_executes(self):
        """BINARY: Command in correct context must execute."""
        shell = MockShell(ctx_type="vpc")
        result = shell.vpc_only_command("test_args")
        assert shell.called is True
        assert result == "vpc_result"

    def test_wrong_context_blocks(self):
        """BINARY: Command in wrong context must be blocked."""
        shell = MockShell(ctx_type="transit-gateway")
        from unittest.mock import patch

        with patch("aws_network_tools.core.decorators.console") as mock_console:
            result = shell.vpc_only_command("test_args")
        assert shell.called is False
        assert result is None
        mock_console.print.assert_called_once()

    def test_no_context_blocks(self):
        """BINARY: Command with no context must be blocked."""
        shell = MockShell(ctx_type=None)
        with patch("aws_network_tools.core.decorators.console"):
            result = shell.vpc_only_command("test_args")
        assert shell.called is False
        assert result is None

    def test_multi_context_first_valid(self):
        """BINARY: Multi-context decorator accepts first valid context."""
        shell = MockShell(ctx_type="vpc")
        result = shell.multi_context_command("args")
        assert shell.called is True
        assert result == "multi_result"

    def test_multi_context_second_valid(self):
        """BINARY: Multi-context decorator accepts second valid context."""
        shell = MockShell(ctx_type="transit-gateway")
        result = shell.multi_context_command("args")
        assert shell.called is True
        assert result == "multi_result"

    def test_multi_context_invalid(self):
        """BINARY: Multi-context decorator blocks invalid context."""
        shell = MockShell(ctx_type="firewall")
        from unittest.mock import patch

        with patch("aws_network_tools.core.decorators.console"):
            result = shell.multi_context_command("args")
        assert shell.called is False
        assert result is None


class TestRequiresRoot:
    """Binary tests for requires_root decorator."""

    def test_root_level_executes(self):
        """BINARY: Command at root level must execute."""
        shell = MockShell(ctx_type=None)
        result = shell.root_only_command("args")
        assert shell.called is True
        assert result == "root_result"

    def test_in_context_blocks(self):
        """BINARY: Command in any context must be blocked."""
        shell = MockShell(ctx_type="vpc")
        from unittest.mock import patch

        with patch("aws_network_tools.core.decorators.console") as mock_console:
            result = shell.root_only_command("args")
        assert shell.called is False
        assert result is None
        mock_console.print.assert_called_once()


class TestDecoratorPreservesMetadata:
    """Ensure decorators preserve function metadata."""

    def test_requires_context_preserves_name(self):
        """BINARY: Decorator must preserve function name."""
        shell = MockShell()
        assert shell.vpc_only_command.__name__ == "vpc_only_command"

    def test_requires_root_preserves_name(self):
        """BINARY: Decorator must preserve function name."""
        shell = MockShell()
        assert shell.root_only_command.__name__ == "root_only_command"
