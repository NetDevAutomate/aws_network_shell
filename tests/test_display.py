"""Tests for display modules"""

from aws_network_tools.modules.vpc import VPCDisplay, resolve_vpc, resolve_item
from aws_network_tools.modules.tgw import TGWDisplay, resolve_tgw
from aws_network_tools.modules.cloudwan import CloudWANDisplay, resolve_network
from aws_network_tools.modules.anfw import ANFWDisplay, resolve_firewall


class TestResolveItem:
    def test_resolve_by_index(self):
        items = [{"name": "a", "id": "1"}, {"name": "b", "id": "2"}]
        assert resolve_item(items, "1", "name", "id") == items[0]
        assert resolve_item(items, "2", "name", "id") == items[1]

    def test_resolve_by_name(self):
        items = [{"name": "test-vpc", "id": "vpc-123"}]
        assert resolve_item(items, "test-vpc", "name", "id") == items[0]

    def test_resolve_by_id(self):
        items = [{"name": "test-vpc", "id": "vpc-123"}]
        assert resolve_item(items, "vpc-123", "name", "id") == items[0]

    def test_resolve_not_found(self):
        items = [{"name": "a", "id": "1"}]
        assert resolve_item(items, "nonexistent", "name", "id") is None

    def test_resolve_empty_list(self):
        assert resolve_item([], "1", "name", "id") is None


class TestResolveVPC:
    def test_resolve_vpc(self, sample_vpc_data):
        result = resolve_vpc(sample_vpc_data, "1")
        assert result == sample_vpc_data[0]

    def test_resolve_vpc_by_name(self, sample_vpc_data):
        result = resolve_vpc(sample_vpc_data, "test-vpc")
        assert result == sample_vpc_data[0]


class TestResolveTGW:
    def test_resolve_tgw(self, sample_tgw_data):
        result = resolve_tgw(sample_tgw_data, "1")
        assert result == sample_tgw_data[0]


class TestResolveNetwork:
    def test_resolve_network(self, sample_cloudwan_data):
        result = resolve_network(sample_cloudwan_data, "1")
        assert result == sample_cloudwan_data[0]


class TestResolveFirewall:
    def test_resolve_firewall(self, sample_firewall_data):
        result = resolve_firewall(sample_firewall_data, "1")
        assert result == sample_firewall_data[0]


class TestVPCDisplay:
    def test_show_list(self, mock_console, sample_vpc_data):
        display = VPCDisplay(mock_console)
        display.show_list(sample_vpc_data)
        output = mock_console._output.getvalue()
        assert "test-vpc" in output
        assert "vpc-123" in output

    def test_show_list_empty(self, mock_console):
        display = VPCDisplay(mock_console)
        display.show_list([])
        output = mock_console._output.getvalue()
        assert "No VPCs found" in output

    def test_show_detail(self, mock_console, sample_vpc_detail):
        display = VPCDisplay(mock_console)
        display.show_detail(sample_vpc_detail)
        output = mock_console._output.getvalue()
        assert "test-vpc" in output

    def test_show_route_tables_list(self, mock_console, sample_vpc_detail):
        display = VPCDisplay(mock_console)
        display.show_route_tables_list(sample_vpc_detail)
        output = mock_console._output.getvalue()
        assert "rtb-123" in output

    def test_show_route_table(self, mock_console, sample_vpc_detail):
        display = VPCDisplay(mock_console)
        display.show_route_table(sample_vpc_detail, "1")
        output = mock_console._output.getvalue()
        assert "10.0.0.0/16" in output

    def test_show_security_group(self, mock_console, sample_vpc_detail):
        display = VPCDisplay(mock_console)
        display.show_security_group(sample_vpc_detail, "1")
        output = mock_console._output.getvalue()
        assert "sg-123" in output

    def test_show_nacl(self, mock_console, sample_vpc_detail):
        display = VPCDisplay(mock_console)
        display.show_nacl(sample_vpc_detail, "1")
        output = mock_console._output.getvalue()
        assert "acl-123" in output


class TestTGWDisplay:
    def test_show_list(self, mock_console, sample_tgw_data):
        display = TGWDisplay(mock_console)
        display.show_list(sample_tgw_data)
        output = mock_console._output.getvalue()
        assert "test-tgw" in output

    def test_show_list_empty(self, mock_console):
        display = TGWDisplay(mock_console)
        display.show_list([])
        output = mock_console._output.getvalue()
        assert "No Transit Gateways found" in output

    def test_show_route_tables_list(self, mock_console, sample_tgw_data):
        display = TGWDisplay(mock_console)
        display.show_route_tables_list(sample_tgw_data[0])
        output = mock_console._output.getvalue()
        assert "tgw-rtb-123" in output


class TestCloudWANDisplay:
    def test_show_list(self, mock_console, sample_cloudwan_data):
        display = CloudWANDisplay(mock_console)
        display.show_list(sample_cloudwan_data)
        output = mock_console._output.getvalue()
        assert "test-core-network" in output

    def test_show_list_empty(self, mock_console):
        display = CloudWANDisplay(mock_console)
        display.show_list([])
        output = mock_console._output.getvalue()
        assert "No Cloud WAN" in output

    def test_show_route_tables_list(self, mock_console, sample_cloudwan_data):
        display = CloudWANDisplay(mock_console)
        display.show_route_tables_list(sample_cloudwan_data[0])
        output = mock_console._output.getvalue()
        assert "prod" in output
        assert "eu-west-1" in output

    def test_show_blackhole_routes(self, mock_console, sample_cloudwan_data):
        display = CloudWANDisplay(mock_console)
        display.show_blackhole_routes(sample_cloudwan_data)
        output = mock_console._output.getvalue()
        assert "BLACKHOLE" in output or "blackhole" in output.lower()

    def test_show_policy_versions(
        self, mock_console, sample_cloudwan_data, sample_policy_versions
    ):
        display = CloudWANDisplay(mock_console)
        display.show_policy_versions(sample_cloudwan_data[0], sample_policy_versions)
        output = mock_console._output.getvalue()
        assert "LIVE" in output
        assert "5" in output

    def test_show_live_policy(self, mock_console, sample_cloudwan_data):
        display = CloudWANDisplay(mock_console)
        policy = {"version": "2021.12", "segments": []}
        display.show_live_policy(sample_cloudwan_data[0], policy)
        output = mock_console._output.getvalue()
        assert "2021.12" in output

    def test_show_live_policy_none(self, mock_console, sample_cloudwan_data):
        display = CloudWANDisplay(mock_console)
        display.show_live_policy(sample_cloudwan_data[0], None)
        output = mock_console._output.getvalue()
        assert "No LIVE policy" in output

    def test_show_policy_diff(self, mock_console, sample_cloudwan_data):
        display = CloudWANDisplay(mock_console)
        policy1 = {"version": "1", "segments": ["a"]}
        policy2 = {"version": "2", "segments": ["b"]}
        display.show_policy_diff(sample_cloudwan_data[0], policy1, policy2, "v1", "v2")
        output = mock_console._output.getvalue()
        assert "v1" in output or "v2" in output

    def test_show_policy_diff_no_changes(self, mock_console, sample_cloudwan_data):
        display = CloudWANDisplay(mock_console)
        policy = {"version": "1", "segments": ["a"]}
        display.show_policy_diff(sample_cloudwan_data[0], policy, policy, "v1", "v2")
        output = mock_console._output.getvalue()
        assert "No differences" in output


class TestANFWDisplay:
    def test_show_list(self, mock_console, sample_firewall_data):
        display = ANFWDisplay(mock_console)
        display.show_list(sample_firewall_data)
        output = mock_console._output.getvalue()
        assert "test-firewall" in output

    def test_show_list_empty(self, mock_console):
        display = ANFWDisplay(mock_console)
        display.show_list([])
        output = mock_console._output.getvalue()
        assert "No Network Firewalls found" in output


class TestTGWDisplayDetail:
    def test_show_route_table(self, mock_console, sample_tgw_data):
        display = TGWDisplay(mock_console)
        display.show_route_table(sample_tgw_data[0], "1")
        output = mock_console._output.getvalue()
        assert "10.0.0.0/8" in output


class TestCloudWANDisplayDetail:
    def test_show_route_table(self, mock_console, sample_cloudwan_data):
        display = CloudWANDisplay(mock_console)
        display.show_route_table(sample_cloudwan_data[0], "1")
        output = mock_console._output.getvalue()
        assert "10.0.0.0/16" in output
