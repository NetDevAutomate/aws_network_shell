"""Argument registry for commands requiring test arguments.

This module provides a centralized registry of test arguments for commands
that require arguments to execute properly during testing.
"""

from typing import Dict, Optional


class ArgumentRegistry:
    """Registry of test arguments for argument-requiring commands.

    This class provides a single source of truth for test arguments,
    allowing the HierarchicalTester to invoke commands that would
    otherwise be skipped due to requiring arguments.
    """

    # Commands that require arguments and their default test values
    # These are REAL values from the AWS account for valid testing
    REQUIRED_ARGS: Dict[str, str] = {
        "find_prefix": "10.1.0.0/16",  # Real CIDR in eu-west-1
        "trace": "10.1.0.4 10.1.32.4",  # Real IPs for trace (src dst)
        "find_ip": "10.0.0.196",  # Real IP in us-east-1
    }

    # Commands that don't require arguments (return empty string)
    NO_ARG_COMMANDS: set = {
        "find_null_routes",
        "show",
        "set",
        "exit",
        "end",
        "clear",
        "clear_cache",
        "populate_cache",
        "create_routing_cache",
        "validate_graph",
        "export_graph",
    }

    # Context-specific argument overrides (context -> command -> arg)
    CONTEXT_ARGS: Dict[str, Dict[str, str]] = {
        "vpc": {
            "find_prefix": "10.0.0.0/16",
        },
        "transit-gateway": {
            "find_prefix": "10.0.0.0/8",
        },
        "core-network": {
            "find_prefix": "10.0.0.0/8",
        },
        "route-table": {
            "find_prefix": "10.0.0.0/24",
        },
    }

    @classmethod
    def get_test_arg(cls, command: str, context: Optional[str] = None) -> Optional[str]:
        """Get the test argument for a command.

        Args:
            command: The command name (e.g., "find_prefix", "trace")
            context: Optional context type (e.g., "vpc", "transit-gateway")

        Returns:
            The test argument string, empty string if no arg needed,
            or None if command is not in the registry
        """
        # Check if it's a no-arg command
        if command in cls.NO_ARG_COMMANDS:
            return ""

        # Check for context-specific override
        if context and context in cls.CONTEXT_ARGS:
            ctx_args = cls.CONTEXT_ARGS[context]
            if command in ctx_args:
                return ctx_args[command]

        # Return default arg or None if not found
        return cls.REQUIRED_ARGS.get(command)

    @classmethod
    def needs_argument(cls, command: str) -> bool:
        """Check if a command requires an argument.

        Args:
            command: The command name

        Returns:
            True if the command requires an argument, False otherwise
        """
        if command in cls.NO_ARG_COMMANDS:
            return False
        return command in cls.REQUIRED_ARGS

    @classmethod
    def get_command_with_arg(cls, command: str, context: Optional[str] = None) -> str:
        """Get the full command string with argument if needed.

        Args:
            command: The command name
            context: Optional context type

        Returns:
            The command string, with argument appended if needed
        """
        arg = cls.get_test_arg(command, context)
        if arg is None:
            return command
        if arg == "":
            return command
        return f"{command} {arg}"


# Convenience function for backward compatibility
def get_test_arg(command: str, context: Optional[str] = None) -> Optional[str]:
    """Get test argument for a command."""
    return ArgumentRegistry.get_test_arg(command, context)
