"""TDD tests for EC2 instance support (AWSNetShell)."""

import pytest
from aws_network_tools.shell import AWSNetShell, HIERARCHY

PROFILE = "taylaand+net-dev-Admin"


class TestEC2Hierarchy:
    """Test EC2 in hierarchy."""

    def test_ec2_instances_in_root_show(self):
        assert "ec2-instances" in HIERARCHY[None]["show"]

    def test_ec2_instance_in_root_set(self):
        assert "ec2-instance" in HIERARCHY[None]["set"]

    def test_ec2_instance_context_exists(self):
        assert "ec2-instance" in HIERARCHY

    def test_ec2_instance_show_options(self):
        opts = HIERARCHY["ec2-instance"]["show"]
        assert "detail" in opts
        assert "security-groups" in opts
        assert "enis" in opts
        assert "routes" in opts


class TestEC2Handlers:
    """Test EC2 handlers exist."""

    def test_show_ec2_instances_handler(self):
        shell = AWSNetShell()
        assert hasattr(shell, "_show_ec2_instances")

    def test_set_ec2_instance_handler(self):
        shell = AWSNetShell()
        assert hasattr(shell, "_set_ec2_instance")

    def test_show_enis_handler(self):
        shell = AWSNetShell()
        assert hasattr(shell, "_show_enis")


@pytest.mark.integration
class TestEC2Integration:
    """Integration tests against live AWS."""

    @pytest.fixture
    def shell(self):
        s = AWSNetShell()
        s.profile = PROFILE
        return s

    def test_show_ec2_instances_no_error(self, shell):
        shell._show_ec2_instances(None)
        cache_key = (
            f"ec2-instance:{','.join(shell.regions) if shell.regions else 'all'}"
        )
        assert cache_key in shell._cache

    def test_show_ec2_instances_with_region(self, shell):
        shell.regions = ["eu-west-1"]
        shell._show_ec2_instances(None)
        assert "ec2-instance:eu-west-1" in shell._cache

    def test_set_ec2_instance_enters_context(self, shell):
        shell._show_ec2_instances(None)
        cache_key = (
            f"ec2-instance:{','.join(shell.regions) if shell.regions else 'all'}"
        )
        instances = shell._cache.get(cache_key, [])
        if instances:
            shell._set_ec2_instance("1")
            assert shell.ctx_type == "ec2-instance"

    def test_show_detail_in_ec2_context(self, shell):
        shell._show_ec2_instances(None)
        cache_key = (
            f"ec2-instance:{','.join(shell.regions) if shell.regions else 'all'}"
        )
        instances = shell._cache.get(cache_key, [])
        if instances:
            shell._set_ec2_instance("1")
            shell._show_detail(None)  # Should not raise

    def test_show_security_groups_in_ec2_context(self, shell):
        shell._show_ec2_instances(None)
        cache_key = (
            f"ec2-instance:{','.join(shell.regions) if shell.regions else 'all'}"
        )
        instances = shell._cache.get(cache_key, [])
        if instances:
            shell._set_ec2_instance("1")
            shell._show_security_groups(None)  # Should not raise

    def test_show_enis_in_ec2_context(self, shell):
        shell._show_ec2_instances(None)
        cache_key = (
            f"ec2-instance:{','.join(shell.regions) if shell.regions else 'all'}"
        )
        instances = shell._cache.get(cache_key, [])
        if instances:
            shell._set_ec2_instance("1")
            shell._show_enis(None)  # Should not raise

    def test_show_routes_in_ec2_context(self, shell):
        shell._show_ec2_instances(None)
        cache_key = (
            f"ec2-instance:{','.join(shell.regions) if shell.regions else 'all'}"
        )
        instances = shell._cache.get(cache_key, [])
        if instances:
            shell._set_ec2_instance("1")
            shell._show_ec2_routes(None)  # Should not raise


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
