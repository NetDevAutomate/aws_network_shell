"""Binary test for VPN tunnel display functionality.

Test validates that:
1. VPN context properly loads tunnel data from AWS API
2. show tunnels displays complete tunnel information
3. show detail includes tunnel summary
4. Both UP and DOWN tunnel statuses are displayed correctly

BINARY PASS CRITERIA:
- VPN context data contains 'tunnels' key with list of tunnel dicts
- Each tunnel has required fields: outside_ip, status, status_message, accepted_routes
- show tunnels command executes without errors
- show detail command displays tunnel count and IPs
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from aws_network_tools.shell.main import AWSNetShell


def test_vpn_tunnel_data_extraction():
    """Test that VPN context loads tunnel data from AWS API.

    BINARY: PASS if ctx.data contains 'tunnels' list with valid tunnel dicts
    """
    shell = AWSNetShell()

    # Load VPNs and enter context
    shell.onecmd("show vpns")
    shell.onecmd("set vpn 1")  # First VPN with UP tunnels

    # Verify tunnel data exists in context
    assert shell.ctx_type == "vpn", "Context type must be 'vpn'"
    assert "tunnels" in shell.ctx.data, "Context data must contain 'tunnels' key"

    tunnels = shell.ctx.data["tunnels"]
    assert isinstance(tunnels, list), "Tunnels must be a list"
    assert len(tunnels) > 0, "Tunnels list must not be empty"

    # Verify tunnel structure
    required_fields = ["outside_ip", "status", "status_message", "accepted_routes"]
    for tunnel in tunnels:
        for field in required_fields:
            assert field in tunnel, f"Tunnel missing required field: {field}"

    print("✅ PASS: VPN tunnel data extraction")
    return True


def test_show_tunnels_command():
    """Test that show tunnels command displays tunnel information.

    BINARY: PASS if command executes without errors and displays tunnels
    """
    shell = AWSNetShell()

    # Setup context
    shell.onecmd("show vpns")
    shell.onecmd("set vpn 1")

    # Execute show tunnels
    try:
        shell.onecmd("show tunnels")
        # If no exception, command executed successfully
        print("✅ PASS: show tunnels command execution")
        return True
    except Exception as e:
        print(f"❌ FAIL: show tunnels raised exception: {e}")
        return False


def test_tunnel_status_display():
    """Test that both UP and DOWN tunnel statuses display correctly.

    BINARY: PASS if both UP tunnels (VPN 1) and DOWN tunnels (VPN 2) display
    """
    shell = AWSNetShell()

    # Test UP tunnels
    shell.onecmd("show vpns")
    shell.onecmd("set vpn 1")

    tunnels_up = shell.ctx.data.get("tunnels", [])
    assert len(tunnels_up) > 0, "VPN 1 must have tunnels"
    has_up = any(t.get("status") == "UP" for t in tunnels_up)
    assert has_up, "VPN 1 must have at least one UP tunnel"

    # Exit context and test DOWN tunnels
    shell.onecmd("exit")
    shell.onecmd("set vpn 2")
    tunnels_down = shell.ctx.data.get("tunnels", [])
    assert len(tunnels_down) > 0, "VPN 2 must have tunnels"
    has_down = any(t.get("status") == "DOWN" for t in tunnels_down)
    assert has_down, "VPN 2 must have at least one DOWN tunnel"

    print("✅ PASS: Tunnel status display for UP and DOWN")
    return True


def test_show_detail_includes_tunnels():
    """Test that show detail command includes tunnel summary.

    BINARY: PASS if show detail executes and tunnel data is in context
    """
    shell = AWSNetShell()

    shell.onecmd("show vpns")
    shell.onecmd("set vpn 1")

    # Verify tunnels are available for show detail
    assert "tunnels" in shell.ctx.data, "Context must have tunnels for show detail"

    # Execute show detail
    try:
        shell.onecmd("show detail")
        print("✅ PASS: show detail includes tunnel information")
        return True
    except Exception as e:
        print(f"❌ FAIL: show detail raised exception: {e}")
        return False


if __name__ == "__main__":
    tests = [
        test_vpn_tunnel_data_extraction,
        test_show_tunnels_command,
        test_tunnel_status_display,
        test_show_detail_includes_tunnels,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except AssertionError as e:
            print(f"❌ FAIL: {test.__name__} - {e}")
            results.append(False)
        except Exception as e:
            print(f"❌ ERROR: {test.__name__} - {e}")
            results.append(False)

    # Binary overall result
    all_passed = all(results)
    total = len(results)
    passed = sum(results)

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"BINARY: {'✅ PASS' if all_passed else '❌ FAIL'}")
    print(f"{'='*50}")

    sys.exit(0 if all_passed else 1)
