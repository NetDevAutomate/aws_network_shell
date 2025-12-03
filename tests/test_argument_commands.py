"""Binary pass/fail tests for argument-required commands.

These tests validate that commands requiring arguments can be properly
invoked with test arguments in the HierarchicalTester.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestArgumentRegistry:
    """Binary tests for argument command registry."""

    def test_registry_exists(self):
        """BINARY: ArgumentRegistry class must exist."""
        from aws_network_tools.shell.arguments import ArgumentRegistry

        assert ArgumentRegistry is not None

    def test_find_prefix_has_default_arg(self):
        """BINARY: find_prefix must have a default test argument."""
        from aws_network_tools.shell.arguments import ArgumentRegistry

        arg = ArgumentRegistry.get_test_arg("find_prefix")
        assert arg is not None
        assert "/" in arg  # Must be a CIDR

    def test_find_null_routes_no_arg_needed(self):
        """BINARY: find_null_routes should return empty string (no arg needed)."""
        from aws_network_tools.shell.arguments import ArgumentRegistry

        arg = ArgumentRegistry.get_test_arg("find_null_routes")
        assert arg == ""  # No argument needed

    def test_trace_has_default_arg(self):
        """BINARY: trace must have a default test argument."""
        from aws_network_tools.shell.arguments import ArgumentRegistry

        arg = ArgumentRegistry.get_test_arg("trace")
        assert arg is not None

    def test_find_ip_has_default_arg(self):
        """BINARY: find_ip must have a default test argument."""
        from aws_network_tools.shell.arguments import ArgumentRegistry

        arg = ArgumentRegistry.get_test_arg("find_ip")
        assert arg is not None
        assert "." in arg  # Must be an IP address

    def test_reachability_has_default_arg(self):
        """BINARY: reachability must have a default test argument."""
        from aws_network_tools.shell.arguments import ArgumentRegistry

        arg = ArgumentRegistry.get_test_arg("reachability")
        assert arg is not None

    def test_unknown_command_returns_none(self):
        """BINARY: Unknown commands return None."""
        from aws_network_tools.shell.arguments import ArgumentRegistry

        arg = ArgumentRegistry.get_test_arg("nonexistent_cmd")
        assert arg is None

    def test_show_commands_no_arg(self):
        """BINARY: show commands don't need args (return empty string)."""
        from aws_network_tools.shell.arguments import ArgumentRegistry

        arg = ArgumentRegistry.get_test_arg("show")
        assert arg == ""  # Empty string means no arg needed, None means not in registry


class TestArgumentNeedsCheck:
    """Binary tests for needs_argument method."""

    def test_find_prefix_needs_arg(self):
        """BINARY: find_prefix needs an argument."""
        from aws_network_tools.shell.arguments import ArgumentRegistry

        assert ArgumentRegistry.needs_argument("find_prefix") is True

    def test_find_null_routes_no_arg_needed(self):
        """BINARY: find_null_routes doesn't need argument."""
        from aws_network_tools.shell.arguments import ArgumentRegistry

        assert ArgumentRegistry.needs_argument("find_null_routes") is False

    def test_trace_needs_arg(self):
        """BINARY: trace needs an argument."""
        from aws_network_tools.shell.arguments import ArgumentRegistry

        assert ArgumentRegistry.needs_argument("trace") is True

    def test_show_command_no_arg(self):
        """BINARY: show doesn't need argument."""
        from aws_network_tools.shell.arguments import ArgumentRegistry

        assert ArgumentRegistry.needs_argument("show") is False

    def test_exit_command_no_arg(self):
        """BINARY: exit doesn't need argument."""
        from aws_network_tools.shell.arguments import ArgumentRegistry

        assert ArgumentRegistry.needs_argument("exit") is False


class TestContextSpecificArgs:
    """Binary tests for context-specific argument resolution."""

    def test_find_prefix_in_vpc_context(self):
        """BINARY: find_prefix in vpc context uses appropriate arg."""
        from aws_network_tools.shell.arguments import ArgumentRegistry

        arg = ArgumentRegistry.get_test_arg("find_prefix", context="vpc")
        assert arg is not None
        assert "/" in arg

    def test_find_prefix_in_tgw_context(self):
        """BINARY: find_prefix in transit-gateway context uses appropriate arg."""
        from aws_network_tools.shell.arguments import ArgumentRegistry

        arg = ArgumentRegistry.get_test_arg("find_prefix", context="transit-gateway")
        assert arg is not None
        assert "/" in arg

    def test_find_prefix_in_root_context(self):
        """BINARY: find_prefix in root context uses appropriate arg."""
        from aws_network_tools.shell.arguments import ArgumentRegistry

        arg = ArgumentRegistry.get_test_arg("find_prefix", context=None)
        assert arg is not None
        assert "/" in arg


class TestAllArgumentCommands:
    """Binary tests for comprehensive argument command list."""

    def test_all_arg_commands_covered(self):
        """BINARY: All argument-required commands have test args defined."""
        from aws_network_tools.shell.arguments import ArgumentRegistry

        required_commands = ["find_prefix", "trace", "find_ip", "reachability"]
        for cmd in required_commands:
            arg = ArgumentRegistry.get_test_arg(cmd)
            assert arg is not None, f"Missing test arg for {cmd}"

    def test_no_arg_commands_return_empty_or_none(self):
        """BINARY: Commands not needing args return empty string or None."""
        from aws_network_tools.shell.arguments import ArgumentRegistry

        no_arg_commands = ["find_null_routes", "show", "exit", "end", "clear"]
        for cmd in no_arg_commands:
            needs = ArgumentRegistry.needs_argument(cmd)
            assert needs is False, f"{cmd} should not need argument"


def run_binary_tests():
    """Run all tests and return binary pass/fail."""
    import subprocess

    result = subprocess.run(
        ["python", "-m", "pytest", __file__, "-v", "--tb=short"],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
    return result.returncode == 0


if __name__ == "__main__":
    success = run_binary_tests()
    sys.exit(0 if success else 1)
