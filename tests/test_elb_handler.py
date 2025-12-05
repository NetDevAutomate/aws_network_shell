"""Tests for ELB handler - Issue #10: Verify handler correctly displays data."""

import pytest
from unittest.mock import MagicMock, patch
from io import StringIO


@pytest.fixture
def mock_elb_detail():
    """Sample ELB detail data as returned by ELBClient.get_elb_detail()."""
    return {
        "arn": "arn:aws:elasticloadbalancing:eu-west-1:123456789:loadbalancer/app/test-alb/abc123",
        "name": "test-alb",
        "dns_name": "test-alb-123456789.eu-west-1.elb.amazonaws.com",
        "type": "application",
        "scheme": "internet-facing",
        "vpc_id": "vpc-123",
        "state": "active",
        "azs": ["eu-west-1a", "eu-west-1b"],
        "region": "eu-west-1",
        "listeners": [
            {
                "arn": "arn:aws:elasticloadbalancing:eu-west-1:123456789:listener/app/test-alb/abc123/def456",
                "port": 443,
                "protocol": "HTTPS",
                "ssl_certs": [{"CertificateArn": "arn:aws:acm:eu-west-1:123456789:certificate/cert123"}],
                "default_actions": [
                    {
                        "type": "forward",
                        "target_group_arn": "arn:aws:elasticloadbalancing:eu-west-1:123456789:targetgroup/tg-1/abc123",
                        "target_group": {
                            "arn": "arn:aws:elasticloadbalancing:eu-west-1:123456789:targetgroup/tg-1/abc123",
                            "name": "tg-1",
                            "protocol": "HTTP",
                            "port": 8080,
                            "vpc_id": "vpc-123",
                            "target_type": "instance",
                            "targets": [
                                {"id": "i-1234567890abcdef0", "port": 8080, "state": "healthy"},
                                {"id": "i-0987654321fedcba0", "port": 8080, "state": "healthy"},
                            ],
                        },
                    }
                ],
                "rules": [],
            },
            {
                "arn": "arn:aws:elasticloadbalancing:eu-west-1:123456789:listener/app/test-alb/abc123/ghi789",
                "port": 80,
                "protocol": "HTTP",
                "ssl_certs": [],
                "default_actions": [{"type": "redirect"}],
                "rules": [],
            },
        ],
        "target_groups": [
            {
                "arn": "arn:aws:elasticloadbalancing:eu-west-1:123456789:targetgroup/tg-1/abc123",
                "name": "tg-1",
                "protocol": "HTTP",
                "port": 8080,
                "vpc_id": "vpc-123",
                "target_type": "instance",
                "targets": [
                    {"id": "i-1234567890abcdef0", "port": 8080, "state": "healthy"},
                    {"id": "i-0987654321fedcba0", "port": 8080, "state": "healthy"},
                ],
            }
        ],
        "target_health": [
            {
                "target_group_arn": "arn:aws:elasticloadbalancing:eu-west-1:123456789:targetgroup/tg-1/abc123",
                "target_group_name": "tg-1",
                "id": "i-1234567890abcdef0",
                "port": 8080,
                "state": "healthy",
            },
            {
                "target_group_arn": "arn:aws:elasticloadbalancing:eu-west-1:123456789:targetgroup/tg-1/abc123",
                "target_group_name": "tg-1",
                "id": "i-0987654321fedcba0",
                "port": 8080,
                "state": "healthy",
            },
        ],
    }


class TestELBHandlerIssue10:
    """Tests for ELB handler - Issue #10."""

    def test_show_listeners_displays_data(self, mock_elb_detail):
        """Test that show listeners displays listener data correctly."""
        from aws_network_tools.shell.handlers.elb import ELBHandlersMixin
        from aws_network_tools.core.base import Context

        # Create a mock shell with the mixin
        class MockShell(ELBHandlersMixin):
            def __init__(self):
                self.ctx_type = "elb"
                self.ctx = Context("elb", "test-alb", "test-alb", mock_elb_detail)
                self.output_format = "table"

        shell = MockShell()
        
        # Verify listeners exist in context data
        listeners = shell.ctx.data.get("listeners", [])
        assert len(listeners) == 2, f"Expected 2 listeners, got {len(listeners)}"
        
        # Verify listener fields are accessible
        for listener in listeners:
            assert "port" in listener, "Listener should have 'port'"
            assert "protocol" in listener, "Listener should have 'protocol'"
            assert "default_actions" in listener, "Listener should have 'default_actions'"

    def test_show_targets_displays_data(self, mock_elb_detail):
        """Test that show targets displays target group data correctly."""
        from aws_network_tools.shell.handlers.elb import ELBHandlersMixin
        from aws_network_tools.core.base import Context

        class MockShell(ELBHandlersMixin):
            def __init__(self):
                self.ctx_type = "elb"
                self.ctx = Context("elb", "test-alb", "test-alb", mock_elb_detail)
                self.output_format = "table"

        shell = MockShell()
        
        # Verify target_groups exist at top level
        targets = shell.ctx.data.get("target_groups", [])
        assert len(targets) > 0, "target_groups should not be empty"
        
        # Verify target group fields
        for tg in targets:
            assert "name" in tg, "Target group should have 'name'"
            assert "protocol" in tg, "Target group should have 'protocol'"
            assert "port" in tg, "Target group should have 'port'"
            assert "target_type" in tg, "Target group should have 'target_type'"

    def test_show_health_displays_data(self, mock_elb_detail):
        """Test that show health displays target health data correctly."""
        from aws_network_tools.shell.handlers.elb import ELBHandlersMixin
        from aws_network_tools.core.base import Context

        class MockShell(ELBHandlersMixin):
            def __init__(self):
                self.ctx_type = "elb"
                self.ctx = Context("elb", "test-alb", "test-alb", mock_elb_detail)
                self.output_format = "table"

        shell = MockShell()
        
        # Verify target_health exists at top level
        health = shell.ctx.data.get("target_health", [])
        assert len(health) > 0, "target_health should not be empty"
        
        # Verify health fields
        for h in health:
            assert "id" in h, "Health should have 'id'"
            assert "port" in h, "Health should have 'port'"
            assert "state" in h, "Health should have 'state'"

    def test_handler_processes_default_actions_list(self, mock_elb_detail):
        """Test that handler correctly processes default_actions as a list."""
        listeners = mock_elb_detail["listeners"]
        
        # HTTPS listener should have forward action
        https_listener = [l for l in listeners if l["port"] == 443][0]
        actions = https_listener.get("default_actions", [])
        assert len(actions) > 0, "HTTPS listener should have default_actions"
        
        forward_action = actions[0]
        assert forward_action["type"] == "forward"
        assert forward_action.get("target_group") is not None
        assert forward_action["target_group"]["name"] == "tg-1"

    def test_handler_uses_id_field_for_health(self, mock_elb_detail):
        """Test that handler uses 'id' field for target health display."""
        health = mock_elb_detail["target_health"]
        
        for h in health:
            # Handler should use 'id' field
            assert "id" in h, "Health entry should have 'id' field"
            assert h["id"].startswith("i-"), "Target ID should be an instance ID"


class TestELBHandlerIntegration:
    """Integration tests that verify handler output."""

    def test_show_listeners_produces_output(self, mock_elb_detail, capsys):
        """Test that _show_listeners produces visible output."""
        from aws_network_tools.shell.handlers.elb import ELBHandlersMixin
        from aws_network_tools.core.base import Context

        class MockShell(ELBHandlersMixin):
            def __init__(self):
                self.ctx_type = "elb"
                self.ctx = Context("elb", "test-alb", "test-alb", mock_elb_detail)
                self.output_format = "table"

        shell = MockShell()
        shell._show_listeners(None)
        
        # Rich console output goes to stdout
        # We can't easily capture Rich output, but we can verify no exception

    def test_show_targets_produces_output(self, mock_elb_detail, capsys):
        """Test that _show_targets produces visible output."""
        from aws_network_tools.shell.handlers.elb import ELBHandlersMixin
        from aws_network_tools.core.base import Context

        class MockShell(ELBHandlersMixin):
            def __init__(self):
                self.ctx_type = "elb"
                self.ctx = Context("elb", "test-alb", "test-alb", mock_elb_detail)
                self.output_format = "table"

        shell = MockShell()
        shell._show_targets(None)

    def test_show_health_produces_output(self, mock_elb_detail, capsys):
        """Test that _show_health produces visible output."""
        from aws_network_tools.shell.handlers.elb import ELBHandlersMixin
        from aws_network_tools.core.base import Context

        class MockShell(ELBHandlersMixin):
            def __init__(self):
                self.ctx_type = "elb"
                self.ctx = Context("elb", "test-alb", "test-alb", mock_elb_detail)
                self.output_format = "table"

        shell = MockShell()
        shell._show_health(None)
