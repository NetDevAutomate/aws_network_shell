"""Parametrized tests for all context show commands (Phase 3).

Efficiently tests 40+ context commands using pytest.mark.parametrize.
All tests follow the same pattern: show→set→command→validate.
"""

import pytest
from .base_context_test import BaseContextTestCase
from .test_data_generator import generate_phase3_test_data


class TestContextShowCommands(BaseContextTestCase):
    """Parametrized tests for context show commands."""

    @pytest.mark.parametrize(
        "test_data", generate_phase3_test_data(), ids=lambda t: t["test_id"]
    )
    def test_context_show_command(self, test_data):
        """Test show commands work in each context.

        This single test method runs 40+ times with different data.
        Each iteration tests: show→set→command→validate pattern.
        """
        # Step 1: Enter context using show→set pattern
        self.show_set_sequence(test_data["context"], test_data["index"])

        # Step 2: Verify context entered
        self.assert_context(test_data["context"], has_data=True)

        # Step 3: Execute the show command
        result = self.command_runner.run(test_data["command"])

        # Step 4: Binary validation
        assert result["exit_code"] == 0, (
            f"{test_data['description']} failed: {result.get('output', '')}"
        )

        # Step 5: Validate expected content
        if test_data["min_count"] > 0:
            self.assert_resource_count(
                result["output"], test_data["expected"], test_data["min_count"]
            )
