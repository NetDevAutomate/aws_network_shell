"""Context State Manager - track and validate context transitions.

Design (per Kimi K2):
- Simple state tracking for Phase 1
- Can evolve to full state machine in Phase 2
- Focuses on validation, not enforcement

Purpose:
Tests need to validate that shell entered expected context.
This manager tracks expected state and validates against actual shell state.
"""

from typing import Any, Optional


class ContextStateManager:
    """Track expected context state and validate against shell.

    Usage:
        shell = AWSNetShell()
        manager = ContextStateManager(shell)

        # Execute command that enters VPC context
        shell.onecmd('set vpc 1')

        # Track and validate
        manager.push_context('vpc', {'vpc_id': 'vpc-123'})
        manager.validate_current_state()  # Raises if mismatch
    """

    def __init__(self, shell):
        """Initialize manager with shell reference.

        Args:
            shell: AWSNetShell instance to track
        """
        self.shell = shell
        self.expected_stack: list[tuple[str, dict[str, Any]]] = []

    def push_context(self, context_type: str, context_data: dict[str, Any]):
        """Push expected context to stack.

        Args:
            context_type: Expected context type (vpc, tgw, etc.)
            context_data: Optional metadata about expected context
        """
        self.expected_stack.append((context_type, context_data))

    def pop_context(self) -> tuple[str, dict[str, Any]]:
        """Remove and return last expected context.

        Returns:
            Tuple of (context_type, context_data)

        Raises:
            IndexError: If stack is empty
        """
        return self.expected_stack.pop()

    def validate_current_state(self):
        """Validate shell's actual context matches expected.

        Checks:
        1. Stack depth matches
        2. Context types match at each level

        Raises:
            AssertionError: If validation fails
        """
        actual_depth = len(self.shell.context_stack)
        expected_depth = len(self.expected_stack)

        assert actual_depth == expected_depth, (
            f"Context stack depth mismatch: expected {expected_depth}, got {actual_depth}"
        )

        # Validate each level
        for i, (expected_type, _) in enumerate(self.expected_stack):
            actual_context = self.shell.context_stack[i]
            actual_type = actual_context.type  # Context dataclass field is 'type', not 'ctx_type'

            assert actual_type == expected_type, (
                f"Context type mismatch at level {i}: expected '{expected_type}', got '{actual_type}'"
            )

    def get_current_context_type(self) -> Optional[str]:
        """Get current expected context type (top of stack).

        Returns:
            Context type string or None if stack empty
        """
        if not self.expected_stack:
            return None
        return self.expected_stack[-1][0]

    def reset(self):
        """Clear expected stack."""
        self.expected_stack.clear()

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"ContextStateManager(expected={[ctx[0] for ctx in self.expected_stack]})"
