"""Tests for spinner module"""

import pytest
from unittest.mock import MagicMock
from aws_network_tools.core.spinner import run_with_spinner


class TestRunWithSpinner:
    def test_run_with_spinner_returns_result(self, mock_console):
        def test_func():
            return {"result": "success"}

        result = run_with_spinner(test_func, "Testing...", console=mock_console)
        assert result == {"result": "success"}

    def test_run_with_spinner_calls_function(self, mock_console):
        mock_func = MagicMock(return_value="done")
        run_with_spinner(mock_func, "Testing...", console=mock_console)
        mock_func.assert_called_once()

    def test_run_with_spinner_handles_exception(self, mock_console):
        def failing_func():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            run_with_spinner(failing_func, "Testing...", console=mock_console)
