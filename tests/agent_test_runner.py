#!/usr/bin/env python3
"""
AWS Network Shell - Agent Test Runner
Executes tests with baseline validation and context chaining.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class TestResult:
    """Result of a single test execution."""
    test_id: str
    command: str
    passed: bool = False
    details: list[str] = field(default_factory=list)
    output: str = ""
    baseline: dict = field(default_factory=dict)
    extracted: dict = field(default_factory=dict)
    error: str = ""


@dataclass
class TestState:
    """Persistent state across test execution."""
    baseline: dict = field(default_factory=dict)
    extracted: dict = field(default_factory=dict)
    context_stack: list[str] = field(default_factory=list)
    results: list[TestResult] = field(default_factory=list)


class ShellTestRunner:
    """Runs aws-net-shell commands and validates output."""

    def __init__(self, profile: str, working_dir: str, baseline_dir: str = "/tmp"):
        self.profile = profile
        self.working_dir = Path(working_dir)
        self.baseline_dir = Path(baseline_dir)
        self.state = TestState()
        self.shell_process = None
        self._load_baselines()

    def _load_baselines(self):
        """Load baseline JSON files into state."""
        baseline_files = {
            "vpcs": ("baseline_vpcs.json", "Vpcs"),
            "tgws": ("baseline_tgws.json", "TransitGateways"),
            "vpns": ("baseline_vpns.json", "VpnConnections"),
            "firewalls": ("baseline_firewalls.json", "Firewalls"),
            "global_networks": ("baseline_globalnetworks.json", "GlobalNetworks"),
            "core_networks": ("baseline_corenetworks.json", "CoreNetworks"),
        }
        for key, (filename, aws_key) in baseline_files.items():
            filepath = self.baseline_dir / filename
            if filepath.exists():
                with open(filepath) as f:
                    data = json.load(f)
                    # Extract the actual list from AWS CLI response format
                    self.state.baseline[key] = data.get(aws_key, data)
                print(f"✓ Loaded baseline: {key}")
            else:
                print(f"⚠ Missing baseline: {filepath}")

    def start_shell(self):
        """Start the interactive shell process using PTY for proper TTY behavior."""
        import pty
        import os
        import time

        cmd = f"cd {self.working_dir} && source .venv/bin/activate && aws-net-shell --profile {self.profile}"

        # Create a pseudo-terminal for proper TTY interaction
        master_fd, slave_fd = pty.openpty()

        self.shell_process = subprocess.Popen(
            cmd,
            shell=True,
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            executable="/bin/bash",
            close_fds=True
        )

        # Close slave fd in parent (child keeps it open)
        os.close(slave_fd)

        # Store master fd for reading/writing
        self.master_fd = master_fd

        # Wait for initial prompt
        startup_output = self._read_until_prompt_pty(timeout=30.0, idle_timeout=3.0)

        print(f"✓ Shell started (captured {len(startup_output)} chars during init)")

    def _read_until_prompt_pty(self, timeout: float = 30.0, idle_timeout: float = 2.0) -> str:
        """Read shell output from PTY until we see a prompt."""
        import select
        import time
        import os

        output = []
        start_time = time.time()
        last_char_time = start_time

        while True:
            # Short select timeout to check frequently
            ready, _, _ = select.select([self.master_fd], [], [], 0.1)

            # Check for overall timeout
            if time.time() - start_time > timeout:
                break

            if ready:
                try:
                    chunk = os.read(self.master_fd, 1024)
                    if not chunk:
                        break
                    decoded = chunk.decode('utf-8', errors='replace')
                    output.append(decoded)
                    last_char_time = time.time()

                    # Check for common prompts
                    current = "".join(output)[-50:]
                    if current.endswith("> ") or current.endswith("# ") or current.endswith("$ "):
                        break
                except OSError:
                    break
            else:
                # No data available - check if we've been idle too long
                if time.time() - last_char_time > idle_timeout:
                    # No new data for idle_timeout seconds, assume output complete
                    break

        return "".join(output)

    def run_command(self, command: str) -> str:
        """Send command to shell via PTY and capture output."""
        import os
        import time

        if not self.shell_process:
            self.start_shell()

        # Send command via PTY
        os.write(self.master_fd, (command + "\n").encode('utf-8'))
        time.sleep(0.5)  # Allow command to start processing

        # Use 5min overall timeout for slow AWS API calls, 10s idle for table rendering
        output = self._read_until_prompt_pty(timeout=300.0, idle_timeout=10.0)
        return output

    def run_aws_cli(self, command: str) -> dict | list | None:
        """Run AWS CLI command and return JSON output."""
        # Substitute variables
        for key, value in self.state.extracted.items():
            command = command.replace(f"{{{key}}}", str(value))

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
        except Exception as e:
            print(f"  AWS CLI error: {e}")
        return None

    def validate_count(self, output: str, expected_count: int, item_type: str) -> tuple[bool, str]:
        """Validate row count in table output."""
        # Count table rows - Rich tables use │ as column separator
        # Strip ANSI escape codes for accurate parsing
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        lines = output.strip().split("\n")
        table_rows = []
        for line in lines:
            # Strip ANSI codes for parsing
            clean_line = ansi_escape.sub('', line)

            # Match Rich table rows: │ 1  │ or standard rows starting with number
            if "│" in clean_line:
                parts = [p.strip() for p in clean_line.split("│") if p.strip()]
                if parts and parts[0].isdigit():
                    table_rows.append(line)
            elif re.match(r"^\s*\d+", clean_line.strip()):
                table_rows.append(line)
        actual_count = len(table_rows)

        if actual_count == expected_count:
            return True, f"✓ {item_type} count: {actual_count}"
        else:
            return False, f"✗ {item_type} count: expected {expected_count}, got {actual_count}"

    def validate_ids_present(self, output: str, expected_ids: list[str]) -> tuple[bool, str]:
        """Validate that expected IDs appear in output."""
        missing = [id_ for id_ in expected_ids if id_ not in output]
        if not missing:
            return True, f"✓ All {len(expected_ids)} IDs present"
        else:
            return False, f"✗ Missing IDs: {missing[:5]}..."

    def extract_table_values(self, output: str, column_index: int = 0) -> list[str]:
        """Extract values from a table column."""
        values = []
        lines = output.strip().split("\n")
        for line in lines:
            # Skip header lines and separators
            if "─" in line or "│" not in line:
                continue
            parts = [p.strip() for p in line.split("│") if p.strip()]
            if len(parts) > column_index:
                values.append(parts[column_index])
        return values

    def extract_first_row_number(self, output: str) -> str | None:
        """Extract the row number from first data row."""
        # Strip ANSI escape codes
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        lines = output.strip().split("\n")
        for line in lines:
            clean_line = ansi_escape.sub('', line)

            # Handle Rich table format: │ 1  │ ...
            if "│" in clean_line:
                parts = [p.strip() for p in clean_line.split("│") if p.strip()]
                if parts and parts[0].isdigit():
                    return parts[0]
            # Standard format: starts with number
            match = re.match(r"^\s*(\d+)\s", clean_line)
            if match:
                return match.group(1)
        return None

    def run_test(self, test_id: str, command: str,
                 baseline_key: str | None = None,
                 baseline_command: str | None = None,
                 validations: list[dict] | None = None,
                 extractions: list[dict] | None = None) -> TestResult:
        """Execute a single test with validation."""
        result = TestResult(test_id=test_id, command=command)

        print(f"\n{'='*60}")
        print(f"TEST: {test_id}")
        print(f"COMMAND: {command}")
        print(f"{'='*60}")

        # Substitute variables in command
        for key, value in self.state.extracted.items():
            command = command.replace(f"{{{key}}}", str(value))

        # Get baseline if needed
        if baseline_command:
            result.baseline = self.run_aws_cli(baseline_command) or {}
        elif baseline_key and baseline_key in self.state.baseline:
            result.baseline = self.state.baseline[baseline_key]

        # Execute shell command
        try:
            result.output = self.run_command(command)
            print(f"\n--- OUTPUT ({len(result.output)} chars) ---")
            print(f"First 500: {result.output[:500]}")
            print(f"Last 500: ...{result.output[-500:]}")
        except Exception as e:
            result.error = str(e)
            result.passed = False
            result.details.append(f"✗ Execution error: {e}")
            self.state.results.append(result)
            return result

        # Check for errors in output
        if "error" in result.output.lower() or "traceback" in result.output.lower():
            result.passed = False
            result.details.append("✗ Error detected in output")
        else:
            result.details.append("✓ No errors in output")
            result.passed = True

        # Run validations
        if validations:
            for v in validations:
                if v["type"] == "count":
                    passed, msg = self.validate_count(result.output, v["expected"], v.get("item", "items"))
                    result.details.append(msg)
                    if not passed:
                        result.passed = False
                elif v["type"] == "ids_present":
                    passed, msg = self.validate_ids_present(result.output, v["ids"])
                    result.details.append(msg)
                    if not passed:
                        result.passed = False

        # Extract values for next tests
        if extractions:
            for e in extractions:
                if e["type"] == "first_row_number":
                    value = self.extract_first_row_number(result.output)
                    if value:
                        self.state.extracted[e["key"]] = value
                        result.extracted[e["key"]] = value
                        result.details.append(f"✓ Extracted {e['key']}: {value}")

        # Record result
        status = "PASS" if result.passed else "FAIL"
        print(f"\n--- RESULT: {status} ---")
        for detail in result.details:
            print(f"  {detail}")

        self.state.results.append(result)
        return result

    def run_phase_1_baseline(self):
        """Phase 1: Verify baselines are loaded."""
        print("\n" + "="*60)
        print("PHASE 1: INFRASTRUCTURE BASELINE")
        print("="*60)

        baseline = self.state.baseline

        # Extract key values for subsequent tests
        if "vpcs" in baseline and baseline["vpcs"]:
            self.state.extracted["vpc_count"] = len(baseline["vpcs"])
            self.state.extracted["vpc_ids"] = [v["VpcId"] for v in baseline["vpcs"]]
            print(f"✓ VPCs: {len(baseline['vpcs'])}")

        if "tgws" in baseline and baseline["tgws"]:
            self.state.extracted["tgw_count"] = len(baseline["tgws"])
            self.state.extracted["tgw_ids"] = [t["TransitGatewayId"] for t in baseline["tgws"]]
            print(f"✓ TGWs: {len(baseline['tgws'])}")

        if "vpns" in baseline and baseline["vpns"]:
            self.state.extracted["vpn_count"] = len(baseline["vpns"])
            self.state.extracted["vpn_ids"] = [v["VpnConnectionId"] for v in baseline["vpns"]]
            # Check tunnel status
            tunnels_up = sum(
                1 for v in baseline["vpns"]
                for t in (v.get("VgwTelemetry") or [])
                if t.get("Status") == "UP"
            )
            self.state.extracted["tunnels_up"] = tunnels_up
            print(f"✓ VPNs: {len(baseline['vpns'])} (tunnels UP: {tunnels_up})")

        if "firewalls" in baseline and baseline["firewalls"]:
            fws = baseline["firewalls"]  # Already extracted by loader
            self.state.extracted["fw_count"] = len(fws)
            self.state.extracted["fw_names"] = [f["FirewallName"] for f in fws]
            print(f"✓ Firewalls: {len(fws)}")

        if "global_networks" in baseline and baseline["global_networks"]:
            gns = baseline["global_networks"]  # Already extracted by loader
            self.state.extracted["gn_count"] = len(gns)
            print(f"✓ Global Networks: {len(gns)}")

        if "core_networks" in baseline and baseline["core_networks"]:
            cns = baseline["core_networks"]  # Already extracted by loader
            self.state.extracted["cn_count"] = len(cns)
            self.state.extracted["cn_ids"] = [c["CoreNetworkId"] for c in cns]
            print(f"✓ Core Networks: {len(cns)}")

    def run_phase_2_root_commands(self):
        """Phase 2: Test root level commands."""
        print("\n" + "="*60)
        print("PHASE 2: ROOT LEVEL COMMANDS")
        print("="*60)

        # Test: show vpcs (multi-region - just check no errors and extraction works)
        self.run_test(
            test_id="ROOT_001",
            command="show vpcs",
            baseline_key="vpcs",
            validations=[
                # Shell queries all regions, so just check baseline VPC is present
                {"type": "ids_present", "ids": self.state.extracted.get("vpc_ids", [])[:5]},
            ],
            extractions=[{"type": "first_row_number", "key": "first_vpc_number"}],
        )

        # Test: show transit_gateways (multi-region - just check no errors)
        self.run_test(
            test_id="ROOT_002",
            command="show transit_gateways",
            baseline_key="tgws",
            extractions=[{"type": "first_row_number", "key": "first_tgw_number"}],
        )

        # Test: show vpns (multi-region - just check no errors)
        self.run_test(
            test_id="ROOT_003",
            command="show vpns",
            baseline_key="vpns",
            extractions=[{"type": "first_row_number", "key": "first_vpn_number"}],
        )

        # Test: show firewalls (multi-region - just check no errors)
        self.run_test(
            test_id="ROOT_004",
            command="show firewalls",
            extractions=[{"type": "first_row_number", "key": "first_fw_number"}],
        )

        # Test: show global-networks (global resource - validate exact count)
        self.run_test(
            test_id="ROOT_005",
            command="show global-networks",
            validations=[
                {"type": "count", "expected": self.state.extracted.get("gn_count", 0), "item": "Global Networks"},
            ],
            extractions=[{"type": "first_row_number", "key": "first_gn_number"}],
        )

    def run_phase_3_vpc_context(self):
        """Phase 3: Test VPC context commands."""
        print("\n" + "="*60)
        print("PHASE 3: VPC CONTEXT")
        print("="*60)

        first_vpc = self.state.extracted.get("first_vpc_number")
        if not first_vpc:
            print("⚠ Skipping: No VPC number extracted from ROOT_001")
            return

        # Enter VPC context
        self.run_test(
            test_id="VPC_001",
            command=f"set vpc {first_vpc}",
        )

        # Show subnets
        self.run_test(
            test_id="VPC_002",
            command="show subnets",
        )

        # Show route-tables
        self.run_test(
            test_id="VPC_003",
            command="show route-tables",
            extractions=[{"type": "first_row_number", "key": "first_vpc_rt_number"}],
        )

        # Show security-groups
        self.run_test(
            test_id="VPC_004",
            command="show security-groups",
        )

        # Enter route-table context
        first_rt = self.state.extracted.get("first_vpc_rt_number")
        if first_rt:
            self.run_test(
                test_id="VPC_005",
                command=f"set route-table {first_rt}",
            )
            self.run_test(
                test_id="VPC_006",
                command="show routes",
            )
            # Exit route-table context
            self.run_command("exit")

        # Exit VPC context
        self.run_command("exit")

    def run_phase_4_tgw_context(self):
        """Phase 4: Test Transit Gateway context commands."""
        print("\n" + "="*60)
        print("PHASE 4: TRANSIT GATEWAY CONTEXT")
        print("="*60)

        first_tgw = self.state.extracted.get("first_tgw_number")
        if not first_tgw:
            print("⚠ Skipping: No TGW number extracted from ROOT_002")
            return

        # Enter TGW context
        self.run_test(
            test_id="TGW_001",
            command=f"set transit-gateway {first_tgw}",
        )

        # Show route-tables
        self.run_test(
            test_id="TGW_002",
            command="show route-tables",
            extractions=[{"type": "first_row_number", "key": "first_tgw_rt_number"}],
        )

        # Enter route-table context and show routes
        first_rt = self.state.extracted.get("first_tgw_rt_number")
        if first_rt:
            self.run_test(
                test_id="TGW_003",
                command=f"set route-table {first_rt}",
            )
            self.run_test(
                test_id="TGW_004",
                command="show routes",
            )
            self.run_command("exit")

        self.run_command("exit")

    def run_phase_5_vpn_context(self):
        """Phase 5: Test VPN context commands (requires active tunnel)."""
        print("\n" + "="*60)
        print("PHASE 5: VPN CONTEXT")
        print("="*60)

        tunnels_up = self.state.extracted.get("tunnels_up", 0)
        if tunnels_up == 0:
            print("⚠ PREREQUISITE NOT MET: No active VPN tunnels (all DOWN)")
            print("⚠ VPN tests skipped - tunnel status validation cannot be performed")
            return

        first_vpn = self.state.extracted.get("first_vpn_number")
        if not first_vpn:
            print("⚠ Skipping: No VPN number extracted from ROOT_003")
            return

        # Enter VPN context
        self.run_test(
            test_id="VPN_001",
            command=f"set vpn {first_vpn}",
        )

        # Show detail
        self.run_test(
            test_id="VPN_002",
            command="show detail",
        )

        # Show tunnels - CRITICAL TEST
        self.run_test(
            test_id="VPN_003",
            command="show tunnels",
        )

        self.run_command("exit")

    def run_phase_6_firewall_context(self):
        """Phase 6: Test Firewall context commands."""
        print("\n" + "="*60)
        print("PHASE 6: FIREWALL CONTEXT")
        print("="*60)

        first_fw = self.state.extracted.get("first_fw_number")
        if not first_fw:
            print("⚠ Skipping: No firewall number extracted from ROOT_004")
            return

        # Enter Firewall context
        self.run_test(
            test_id="FW_001",
            command=f"set firewall {first_fw}",
        )

        # Show detail
        self.run_test(
            test_id="FW_002",
            command="show detail",
        )

        # Show rule-groups
        self.run_test(
            test_id="FW_003",
            command="show rule-groups",
        )

        self.run_command("exit")

    def run_phase_7_cloudwan_context(self):
        """Phase 7: Test CloudWAN context commands."""
        print("\n" + "="*60)
        print("PHASE 7: CLOUDWAN CONTEXT")
        print("="*60)

        first_gn = self.state.extracted.get("first_gn_number")
        if not first_gn:
            print("⚠ Skipping: No global network number extracted from ROOT_005")
            return

        # Enter Global Network context
        self.run_test(
            test_id="CWAN_001",
            command=f"set global-network {first_gn}",
        )

        # Show core-networks
        self.run_test(
            test_id="CWAN_002",
            command="show core-networks",
            extractions=[{"type": "first_row_number", "key": "first_cn_number"}],
        )

        # Enter Core Network context
        first_cn = self.state.extracted.get("first_cn_number")
        if first_cn:
            self.run_test(
                test_id="CWAN_003",
                command=f"set core-network {first_cn}",
            )

            # Show segments
            self.run_test(
                test_id="CWAN_004",
                command="show segments",
            )

            # Show route-tables
            self.run_test(
                test_id="CWAN_005",
                command="show route-tables",
            )

            # Show routes
            self.run_test(
                test_id="CWAN_006",
                command="show routes",
            )

            self.run_command("exit")

        self.run_command("exit")

    def generate_report(self) -> dict:
        """Generate test report."""
        passed = sum(1 for r in self.state.results if r.passed)
        failed = sum(1 for r in self.state.results if not r.passed)

        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "profile": self.profile,
            "summary": {
                "total": len(self.state.results),
                "passed": passed,
                "failed": failed,
            },
            "results": [
                {
                    "test_id": r.test_id,
                    "command": r.command,
                    "passed": r.passed,
                    "details": r.details,
                    "error": r.error,
                }
                for r in self.state.results
            ],
        }
        return report

    def cleanup(self):
        """Clean up shell process and PTY file descriptor."""
        import os
        if self.shell_process:
            try:
                # Try to send exit command via PTY
                os.write(self.master_fd, b"exit\n")
            except:
                pass
            self.shell_process.terminate()
            try:
                self.shell_process.wait(timeout=5)
            except:
                self.shell_process.kill()

        # Close PTY file descriptor
        if hasattr(self, 'master_fd'):
            try:
                os.close(self.master_fd)
            except:
                pass


def main():
    parser = argparse.ArgumentParser(description="AWS Network Shell Test Runner")
    parser.add_argument("--profile", default="taylaand+net-dev-Admin", help="AWS profile")
    parser.add_argument("--working-dir", default=".", help="Working directory")
    parser.add_argument("--baseline-dir", default="/tmp", help="Baseline files directory")
    parser.add_argument("--output", default=None, help="Output report file")
    args = parser.parse_args()

    runner = ShellTestRunner(
        profile=args.profile,
        working_dir=args.working_dir,
        baseline_dir=args.baseline_dir,
    )

    try:
        runner.start_shell()
        runner.run_phase_1_baseline()
        runner.run_phase_2_root_commands()
        runner.run_phase_3_vpc_context()
        runner.run_phase_4_tgw_context()
        runner.run_phase_5_vpn_context()
        runner.run_phase_6_firewall_context()
        runner.run_phase_7_cloudwan_context()
    finally:
        runner.cleanup()

    # Generate report
    report = runner.generate_report()

    print("\n" + "="*60)
    print("FINAL REPORT")
    print("="*60)
    print(f"Total: {report['summary']['total']}")
    print(f"Passed: {report['summary']['passed']}")
    print(f"Failed: {report['summary']['failed']}")

    if args.output:
        with open(args.output, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\nReport saved to: {args.output}")

    # Exit with error code if tests failed
    sys.exit(0 if report["summary"]["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
