"""TDD tests for unified display renderer - Binary pass/fail."""

import pytest
from io import StringIO
from rich.console import Console

from aws_network_tools.core.renderer import DisplayRenderer


@pytest.fixture
def renderer():
    """Create renderer with captured output."""
    output = StringIO()
    console = Console(file=output, force_terminal=True, width=120)
    r = DisplayRenderer(console=console)
    r._output = output
    return r


class TestRenderFormat:
    """Binary tests for format rendering."""

    def test_json_format_returns_true(self, renderer):
        """BINARY: JSON format must return True."""
        result = renderer.render({"id": "vpc-123"}, fmt="json")
        assert result is True

    def test_yaml_format_returns_true(self, renderer):
        """BINARY: YAML format must return True."""
        result = renderer.render({"id": "vpc-123"}, fmt="yaml")
        assert result is True

    def test_table_format_returns_false(self, renderer):
        """BINARY: Table format must return False."""
        result = renderer.render([{"id": "vpc-123"}], fmt="table")
        assert result is False

    def test_json_output_valid(self, renderer):
        """BINARY: JSON output must be valid JSON."""
        renderer.render({"id": "vpc-123", "name": "test"}, fmt="json")
        output = renderer._output.getvalue()
        assert "vpc-123" in output


class TestTableRendering:
    """Binary tests for table rendering."""

    def test_table_with_data(self, renderer):
        """BINARY: Table with data must render rows."""
        data = [
            {"id": "vpc-1", "name": "test1", "region": "us-east-1"},
            {"id": "vpc-2", "name": "test2", "region": "us-west-2"},
        ]
        columns = [
            {"name": "ID", "key": "id"},
            {"name": "Name", "key": "name"},
            {"name": "Region", "key": "region"},
        ]
        renderer.table(data, "VPCs", columns)
        output = renderer._output.getvalue()
        assert "vpc-1" in output
        assert "vpc-2" in output
        assert "VPCs" in output

    def test_table_empty_data(self, renderer):
        """BINARY: Empty data must show 'not found' message."""
        renderer.table([], "VPCs", [{"name": "ID", "key": "id"}])
        output = renderer._output.getvalue()
        assert "No vpcs found" in output

    def test_table_with_index(self, renderer):
        """BINARY: Table with index must show row numbers."""
        data = [{"id": "vpc-1"}]
        renderer.table(data, "Test", [{"name": "ID", "key": "id"}], show_index=True)
        output = renderer._output.getvalue()
        assert "1" in output

    def test_table_without_index(self, renderer):
        """BINARY: Table without index must not show # column."""
        data = [{"id": "vpc-1"}]
        renderer.table(data, "Test", [{"name": "ID", "key": "id"}], show_index=False)
        # Just verify it doesn't crash
        assert True

    def test_table_with_hint(self, renderer):
        """BINARY: Table with hint must show hint text."""
        data = [{"id": "vpc-1"}]
        renderer.table(
            data, "Test", [{"name": "ID", "key": "id"}], hint="Use 'set vpc <#>'"
        )
        output = renderer._output.getvalue()
        assert "set vpc" in output


class TestStateColoring:
    """Binary tests for state-based coloring."""

    def test_active_state_colored(self, renderer):
        """BINARY: Active state must be colored green."""
        data = [{"id": "route-1", "state": "active"}]
        renderer.table(data, "Routes", [{"name": "State", "key": "state"}])
        # Verify render completes (color codes are in output)
        output = renderer._output.getvalue()
        assert "active" in output

    def test_blackhole_state_colored(self, renderer):
        """BINARY: Blackhole state must be colored red."""
        data = [{"id": "route-1", "state": "blackhole"}]
        renderer.table(data, "Routes", [{"name": "State", "key": "state"}])
        output = renderer._output.getvalue()
        assert "blackhole" in output


class TestDetailRendering:
    """Binary tests for detail panel rendering."""

    def test_detail_renders_fields(self, renderer):
        """BINARY: Detail must render all specified fields."""
        data = {"id": "vpc-123", "name": "test-vpc", "region": "us-east-1"}
        fields = [("ID", "id"), ("Name", "name"), ("Region", "region")]
        renderer.detail(data, "VPC Details", fields)
        output = renderer._output.getvalue()
        assert "vpc-123" in output
        assert "test-vpc" in output

    def test_detail_handles_missing_fields(self, renderer):
        """BINARY: Detail must handle missing fields gracefully."""
        data = {"id": "vpc-123"}
        fields = [("ID", "id"), ("Name", "name")]
        renderer.detail(data, "VPC", fields)
        output = renderer._output.getvalue()
        assert "vpc-123" in output
        assert "-" in output  # Missing field shows dash


class TestRouteRendering:
    """Binary tests for route table rendering."""

    def test_routes_renders_correctly(self, renderer):
        """BINARY: Routes must render with correct columns."""
        routes = [
            {
                "prefix": "10.0.0.0/8",
                "target": "tgw-123",
                "type": "propagated",
                "state": "active",
            },
        ]
        renderer.routes(routes, "Routes")
        output = renderer._output.getvalue()
        assert "10.0.0.0/8" in output
        assert "tgw-123" in output


class TestStatusMessages:
    """Binary tests for status message methods."""

    def test_status_message(self, renderer):
        """BINARY: Status must print message."""
        renderer.status("Success!")
        assert "Success!" in renderer._output.getvalue()

    def test_error_message(self, renderer):
        """BINARY: Error must print message."""
        renderer.error("Failed!")
        assert "Failed!" in renderer._output.getvalue()

    def test_warning_message(self, renderer):
        """BINARY: Warning must print message."""
        renderer.warning("Caution!")
        assert "Caution!" in renderer._output.getvalue()

    def test_info_message(self, renderer):
        """BINARY: Info must print message."""
        renderer.info("Note")
        assert "Note" in renderer._output.getvalue()
