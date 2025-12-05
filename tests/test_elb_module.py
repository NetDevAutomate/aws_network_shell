"""TDD Tests for ELB module - Issue #10: ELB commands return no output.

These tests are written FIRST to verify the bug exists and will guide the fix.
Models consulted: Kimi K2 Thinking, Nova Premier, DeepSeek R1, Llama 4 Maverick, Qwen3 235B
"""

import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_elbv2_client():
    """Mock ELBv2 boto3 client with sample ALB data."""
    client = MagicMock()

    # Mock describe_load_balancers response
    client.describe_load_balancers.return_value = {
        "LoadBalancers": [
            {
                "LoadBalancerArn": "arn:aws:elasticloadbalancing:eu-west-1:123456789:loadbalancer/app/test-alb/abc123",
                "LoadBalancerName": "test-alb",
                "DNSName": "test-alb-123456789.eu-west-1.elb.amazonaws.com",
                "Type": "application",
                "Scheme": "internet-facing",
                "VpcId": "vpc-123",
                "State": {"Code": "active"},
                "AvailabilityZones": [{"ZoneName": "eu-west-1a"}, {"ZoneName": "eu-west-1b"}],
            }
        ]
    }

    # Mock describe_listeners response - TWO listeners
    client.describe_listeners.return_value = {
        "Listeners": [
            {
                "ListenerArn": "arn:aws:elasticloadbalancing:eu-west-1:123456789:listener/app/test-alb/abc123/def456",
                "LoadBalancerArn": "arn:aws:elasticloadbalancing:eu-west-1:123456789:loadbalancer/app/test-alb/abc123",
                "Port": 443,
                "Protocol": "HTTPS",
                "Certificates": [{"CertificateArn": "arn:aws:acm:eu-west-1:123456789:certificate/cert123"}],
                "DefaultActions": [
                    {
                        "Type": "forward",
                        "TargetGroupArn": "arn:aws:elasticloadbalancing:eu-west-1:123456789:targetgroup/tg-1/abc123",
                        "Order": 1,
                    }
                ],
            },
            {
                "ListenerArn": "arn:aws:elasticloadbalancing:eu-west-1:123456789:listener/app/test-alb/abc123/ghi789",
                "LoadBalancerArn": "arn:aws:elasticloadbalancing:eu-west-1:123456789:loadbalancer/app/test-alb/abc123",
                "Port": 80,
                "Protocol": "HTTP",
                "Certificates": [],
                "DefaultActions": [
                    {
                        "Type": "redirect",
                        "RedirectConfig": {"Protocol": "HTTPS", "Port": "443", "StatusCode": "HTTP_301"},
                        "Order": 1,
                    }
                ],
            },
        ]
    }

    # Mock describe_target_groups response
    client.describe_target_groups.return_value = {
        "TargetGroups": [
            {
                "TargetGroupArn": "arn:aws:elasticloadbalancing:eu-west-1:123456789:targetgroup/tg-1/abc123",
                "TargetGroupName": "tg-1",
                "Protocol": "HTTP",
                "Port": 8080,
                "VpcId": "vpc-123",
                "HealthCheckProtocol": "HTTP",
                "HealthCheckPort": "traffic-port",
                "HealthCheckPath": "/health",
                "TargetType": "instance",
            }
        ]
    }

    # Mock describe_target_health response
    client.describe_target_health.return_value = {
        "TargetHealthDescriptions": [
            {
                "Target": {"Id": "i-1234567890abcdef0", "Port": 8080},
                "HealthCheckPort": "8080",
                "TargetHealth": {"State": "healthy"},
            },
            {
                "Target": {"Id": "i-0987654321fedcba0", "Port": 8080},
                "HealthCheckPort": "8080",
                "TargetHealth": {"State": "healthy"},
            },
        ]
    }

    # Mock describe_rules response (for ALB)
    client.describe_rules.return_value = {"Rules": []}

    return client


@pytest.fixture
def mock_boto_session(mock_elbv2_client):
    """Mock boto3 session that returns our mocked elbv2 client."""
    session = MagicMock()
    session.client.return_value = mock_elbv2_client
    return session


class TestELBModuleIssue10:
    """Tests for Issue #10: ELB commands return no output."""

    def test_listener_loop_processes_all_items(self, mock_boto_session, mock_elbv2_client):
        """Bug: Variable shadowing causes loop to lose original listener data.

        The loop variable 'listener' is reassigned inside the loop (line 163),
        preventing access to AWS response fields like 'DefaultActions'.
        """
        from aws_network_tools.modules.elb import ELBClient

        elb_client = ELBClient(session=mock_boto_session)
        result = elb_client.get_elb_detail(
            "arn:aws:elasticloadbalancing:eu-west-1:123456789:loadbalancer/app/test-alb/abc123",
            "eu-west-1"
        )

        # Should have processed BOTH listeners (port 443 and 80)
        assert "listeners" in result, "Result should contain 'listeners' key"
        assert len(result["listeners"]) == 2, f"Expected 2 listeners, got {len(result.get('listeners', []))}"

        # Verify listener data was extracted correctly (not shadowed)
        ports = [l.get("port") for l in result["listeners"]]
        assert 443 in ports, "Port 443 listener should be present"
        assert 80 in ports, "Port 80 listener should be present"

    def test_target_groups_at_top_level(self, mock_boto_session, mock_elbv2_client):
        """Bug: Handler expects target_groups at top level but module nests it.

        The handler calls: self.ctx.data.get("target_groups", [])
        But the module doesn't provide target_groups at the root level.
        """
        from aws_network_tools.modules.elb import ELBClient

        elb_client = ELBClient(session=mock_boto_session)
        result = elb_client.get_elb_detail(
            "arn:aws:elasticloadbalancing:eu-west-1:123456789:loadbalancer/app/test-alb/abc123",
            "eu-west-1"
        )

        # target_groups MUST be at top level
        assert "target_groups" in result, "Result must have 'target_groups' at top level"
        assert isinstance(result["target_groups"], list), "target_groups must be a list"
        assert len(result["target_groups"]) > 0, "target_groups should not be empty for ALB with target groups"

    def test_target_health_at_top_level(self, mock_boto_session, mock_elbv2_client):
        """Bug: Handler expects target_health at top level but module doesn't provide it.

        The handler calls: self.ctx.data.get("target_health", [])
        But the module doesn't provide target_health at the root level.
        """
        from aws_network_tools.modules.elb import ELBClient

        elb_client = ELBClient(session=mock_boto_session)
        result = elb_client.get_elb_detail(
            "arn:aws:elasticloadbalancing:eu-west-1:123456789:loadbalancer/app/test-alb/abc123",
            "eu-west-1"
        )

        # target_health MUST be at top level
        assert "target_health" in result, "Result must have 'target_health' at top level"
        assert isinstance(result["target_health"], list), "target_health must be a list"

    def test_empty_listeners_returns_empty_structures(self, mock_boto_session, mock_elbv2_client):
        """Edge case: ELB with no listeners should return empty lists, not None."""
        from aws_network_tools.modules.elb import ELBClient

        # Mock empty listeners
        mock_elbv2_client.describe_listeners.return_value = {"Listeners": []}

        elb_client = ELBClient(session=mock_boto_session)
        result = elb_client.get_elb_detail(
            "arn:aws:elasticloadbalancing:eu-west-1:123456789:loadbalancer/app/test-alb/abc123",
            "eu-west-1"
        )

        # Should return empty lists, not None or missing keys
        assert result.get("listeners") == [], "Empty listeners should return []"
        assert result.get("target_groups") == [], "No listeners means no target_groups, should return []"
        assert result.get("target_health") == [], "No listeners means no target_health, should return []"

    def test_listener_with_forward_action_extracts_target_group(self, mock_boto_session, mock_elbv2_client):
        """Test that forward actions properly extract target group ARNs."""
        from aws_network_tools.modules.elb import ELBClient

        elb_client = ELBClient(session=mock_boto_session)
        result = elb_client.get_elb_detail(
            "arn:aws:elasticloadbalancing:eu-west-1:123456789:loadbalancer/app/test-alb/abc123",
            "eu-west-1"
        )

        # Find the HTTPS listener (port 443) which has a forward action
        https_listeners = [l for l in result.get("listeners", []) if l.get("port") == 443]
        assert len(https_listeners) == 1, "Should have one HTTPS listener"

        https_listener = https_listeners[0]
        # Check that default_actions contains the forward action with target group
        actions = https_listener.get("default_actions", [])
        forward_actions = [a for a in actions if a.get("type") == "forward"]
        assert len(forward_actions) > 0, "HTTPS listener should have forward action"
        assert forward_actions[0].get("target_group_arn") is not None, "Forward action should have target_group_arn"
