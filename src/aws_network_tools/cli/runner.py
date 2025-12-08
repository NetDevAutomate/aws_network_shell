#!/usr/bin/env python3
"""
Generic AWS Network Shell command runner using pexpect.

Usage:
    # Pass commands as arguments (use quotes for multi-word commands)
    uv run python scripts/shell_runner.py "show global-networks" "set global-network 3" "show core-networks"

    # Or pipe commands from a file
    echo -e "show global-networks\nset global-network 2\nshow core-networks" | uv run python scripts/shell_runner.py

    # With AWS profile
    uv run python scripts/shell_runner.py --profile my-profile "show vpcs" "set vpc 1" "show subnets"
"""

import argparse
import sys
import re

import pexpect


class ShellRunner:
    """Run commands against aws-net-shell interactively."""

    def __init__(self, profile: str | None = None, timeout: int = 60):
        self.profile = profile
        self.timeout = timeout
        self.child: pexpect.spawn | None = None
        # Match prompt at end of line: "aws-net> " or "context $"
        self.prompt_pattern = r'\n(?:aws-net>|.*\$)\s*$'

    def start(self):
        """Start the interactive shell."""
        cmd = 'aws-net-shell'
        if self.profile:
            cmd += f' --profile {self.profile}'

        self.child = pexpect.spawn(cmd, timeout=self.timeout, encoding='utf-8')
        # Wait for initial prompt
        self._wait_for_prompt()
        print(f"✓ Shell started\n{'='*60}")

    def _wait_for_prompt(self):
        """Wait for shell prompt, handling spinners and partial output."""
        import time
        
        # Collect output until we see a stable prompt
        buffer = ""
        last_size = 0
        stable_count = 0
        
        while stable_count < 3:  # Need 3 stable checks (~0.3s of no new output)
            try:
                # Non-blocking read with short timeout
                self.child.expect(r'.+', timeout=0.1)
                buffer += self.child.after
            except pexpect.TIMEOUT:
                pass
            
            # Check if buffer size is stable (no new output)
            if len(buffer) == last_size:
                stable_count += 1
            else:
                stable_count = 0
                last_size = len(buffer)
            
            # Check for prompt indicators
            clean = self._strip_ansi(buffer)
            if clean.rstrip().endswith(('aws-net>', '$')) and stable_count >= 2:
                break
                
            time.sleep(0.1)
        
        return buffer

    def run(self, command: str) -> str:
        """Run a command and return output."""
        if not self.child:
            self.start()

        print(f"\n> {command}")
        print("-" * 60)

        self.child.sendline(command)
        
        # Wait for complete output
        import time
        time.sleep(0.2)  # Let command start
        output = self._wait_for_prompt()

        # Clean ANSI codes for display but keep structure
        clean_output = self._strip_ansi(output)
        
        # Remove the echoed command from output
        lines = clean_output.split('\n')
        if lines and command in lines[0]:
            lines = lines[1:]
        
        result = '\n'.join(lines).strip()
        print(result)
        return result

    def run_sequence(self, commands: list[str]):
        """Run a sequence of commands."""
        for cmd in commands:
            cmd = cmd.strip()
            if cmd and not cmd.startswith('#'):
                self.run(cmd)

    def close(self):
        """Close the shell."""
        if self.child and self.child.isalive():
            self.child.sendline('exit')
            try:
                self.child.expect(pexpect.EOF, timeout=5)
            except:
                self.child.terminate(force=True)
        print(f"\n{'='*60}\n✓ Shell closed")

    @staticmethod
    def _strip_ansi(text: str) -> str:
        """Remove ANSI escape codes."""
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)


def main():
    parser = argparse.ArgumentParser(
        description='Run commands against aws-net-shell interactively',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('commands', nargs='*', help='Commands to run')
    parser.add_argument('--profile', '-p', help='AWS profile to use')
    parser.add_argument('--timeout', '-t', type=int, default=30, help='Command timeout (default: 30s)')
    args = parser.parse_args()

    # Get commands from args or stdin
    commands = args.commands
    if not commands and not sys.stdin.isatty():
        commands = sys.stdin.read().strip().split('\n')

    if not commands:
        parser.print_help()
        sys.exit(1)

    runner = ShellRunner(profile=args.profile, timeout=args.timeout)
    try:
        runner.start()
        runner.run_sequence(commands)
    finally:
        runner.close()


if __name__ == '__main__':
    main()
