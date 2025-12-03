"""Tests for SecurityModule registration in legacy AWSNetShell (skipped).
The project now uses AWSNetShell with a different registration model.
"""

import pytest
from unittest.mock import patch

pytestmark = pytest.mark.skip(reason="Legacy shell tests superseded by AWSNetShell")


class TestSecurityModule:
    @pytest.fixture
    def shell(self):
        from aws_network_tools.shell.main import AWSNetShell

        with patch("boto3.Session"):
            return AWSNetShell()

    def test_security_module_registered(self, shell):
        """Test that SecurityModule is registered in AWSNetShell"""
        # Check that SecurityModule is in the modules list
        security_modules = [
            mod for mod in shell.modules if mod.__class__.__name__ == "SecurityModule"
        ]
        assert len(security_modules) == 1, (
            "SecurityModule should be registered exactly once"
        )

    def test_security_command_in_context_commands(self, shell):
        """Test that security command is available in context_commands"""
        assert "security" in shell.context_commands[None], (
            "security command should be available at top level"
        )

    def test_security_show_command_registered(self, shell):
        """Test that security show commands are registered"""
        # The security module should register show commands for security context
        assert "security-analysis" in shell.show_commands[None], (
            "security-analysis should be in top level show commands"
        )
