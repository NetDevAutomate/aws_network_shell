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
    
    # With debug logging
    uv run python scripts/shell_runner.py --debug "show vpcs" "set vpc 1" "show subnets"
"""

import argparse
import sys
import re
import logging
from datetime import datetime
from pathlib import Path

import pexpect


class ShellRunner:
    """Run commands against aws-net-shell interactively."""

    def __init__(self, profile: str | None = None, timeout: int = 60, debug: bool = False):
        self.profile = profile
        self.timeout = timeout
        self.debug = debug
        self.child: pexpect.spawn | None = None
        # Match prompt at end of line: "aws-net> " or "context $"
        self.prompt_pattern = r'\n(?:aws-net>|.*\$)\s*$'
        self.logger = None
        
        if debug:
            self._setup_debug_logging()

    def _setup_debug_logging(self):
        """Initialize debug logging to timestamped file in /tmp/."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = Path(f"/tmp/aws_net_runner_debug_{timestamp}.log")
        
        # Create logger
        self.logger = logging.getLogger("shell_runner")
        self.logger.setLevel(logging.DEBUG)
        
        # File handler with detailed formatting
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Log session start
        self.logger.info("="*80)
        self.logger.info("AWS Network Shell Runner - Debug Session Started")
        self.logger.info(f"Log file: {log_file}")
        self.logger.info(f"Profile: {self.profile or 'default'}")
        self.logger.info(f"Timeout: {self.timeout}s")
        self.logger.info("="*80)
        
        print(f"[DEBUG] Logging to: {log_file}")

    def _debug(self, message: str):
        """Log debug message if debug mode enabled."""
        if self.logger:
            self.logger.debug(message)

    def _info(self, message: str):
        """Log info message if debug mode enabled."""
        if self.logger:
            self.logger.info(message)

    def _error(self, message: str):
        """Log error message if debug mode enabled."""
        if self.logger:
            self.logger.error(message)

    def start(self):
        """Start the interactive shell."""
        cmd = 'aws-net-shell'
        if self.profile:
            cmd += f' --profile {self.profile}'

        self._info(f"Starting shell: {cmd}")
        
        try:
            self.child = pexpect.spawn(cmd, timeout=self.timeout, encoding='utf-8')
            self._debug(f"Shell process spawned (PID: {self.child.pid})")
            
            # Wait for initial prompt
            self._wait_for_prompt()
            print(f"✓ Shell started\n{'='*60}")
            self._info("Shell startup complete")
        except Exception as e:
            self._error(f"Shell startup failed: {e}")
            raise

    def _wait_for_prompt(self):
        """Wait for shell prompt, handling spinners and partial output."""
        import time
        
        self._debug("Waiting for prompt...")
        start_time = time.time()
        
        # Collect output until we see a stable prompt
        buffer = ""
        last_size = 0
        stable_count = 0
        iterations = 0
        
        while stable_count < 3:  # Need 3 stable checks (~0.3s of no new output)
            iterations += 1
            try:
                # Non-blocking read with short timeout
                self.child.expect(r'.+', timeout=0.1)
                buffer += self.child.after
                self._debug(f"[iter {iterations}] Read {len(self.child.after)} chars, buffer size: {len(buffer)}")
            except pexpect.TIMEOUT:
                self._debug(f"[iter {iterations}] Read timeout (no new data)")
                pass
            
            # Check if buffer size is stable (no new output)
            if len(buffer) == last_size:
                stable_count += 1
                self._debug(f"[iter {iterations}] Stable count: {stable_count}/3")
            else:
                stable_count = 0
                last_size = len(buffer)
                self._debug(f"[iter {iterations}] Buffer growing, reset stable count")
            
            # Check for prompt indicators
            clean = self._strip_ansi(buffer)
            if clean.rstrip().endswith(('aws-net>', '$')) and stable_count >= 2:
                self._debug(f"[iter {iterations}] Prompt detected: '{clean[-50:]}'")
                break
                
            time.sleep(0.1)
        
        elapsed = time.time() - start_time
        self._info(f"Prompt received after {elapsed:.2f}s ({iterations} iterations)")
        self._debug(f"Final buffer size: {len(buffer)} chars")
        
        return buffer

    def run(self, command: str) -> str:
        """Run a command and return output."""
        if not self.child:
            self.start()

        print(f"\n> {command}")
        print("-" * 60)
        
        self._info(f"Executing command: '{command}'")
        cmd_start = datetime.now()

        self.child.sendline(command)
        self._debug(f"Command sent to shell")
        
        # Wait for complete output
        import time
        time.sleep(0.2)  # Let command start
        self._debug("Waiting for command output...")
        
        try:
            output = self._wait_for_prompt()
            cmd_elapsed = (datetime.now() - cmd_start).total_seconds()
            self._info(f"Command completed in {cmd_elapsed:.2f}s")
            
            # Log raw output with ANSI codes
            self._debug(f"Raw output ({len(output)} chars):\n{output}")
        except Exception as e:
            self._error(f"Command execution failed: {e}")
            raise

        # Clean ANSI codes for display but keep structure
        clean_output = self._strip_ansi(output)
        self._debug(f"Cleaned output ({len(clean_output)} chars)")
        
        # Remove the echoed command from output
        lines = clean_output.split('\n')
        if lines and command in lines[0]:
            lines = lines[1:]
            self._debug("Removed echoed command from output")
        
        result = '\n'.join(lines).strip()
        print(result)
        return result

    def run_sequence(self, commands: list[str]):
        """Run a sequence of commands."""
        self._info(f"Running sequence of {len(commands)} commands")
        
        for idx, cmd in enumerate(commands, 1):
            cmd = cmd.strip()
            if cmd and not cmd.startswith('#'):
                self._info(f"Command {idx}/{len(commands)}: {cmd}")
                try:
                    self.run(cmd)
                except Exception as e:
                    self._error(f"Command {idx} failed: {e}")
                    raise

    def close(self):
        """Close the shell."""
        self._info("Closing shell...")
        
        if self.child and self.child.isalive():
            self.child.sendline('exit')
            try:
                self.child.expect(pexpect.EOF, timeout=5)
                self._debug("Shell exited cleanly")
            except Exception as e:
                self._debug(f"Shell exit timeout, forcing termination: {e}")
                self.child.terminate(force=True)
        
        print(f"\n{'='*60}\n✓ Shell closed")
        
        if self.logger:
            self._info("Debug session complete")
            self._info("="*80)
            # Close all handlers
            for handler in self.logger.handlers[:]:
                handler.close()
                self.logger.removeHandler(handler)

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
    parser.add_argument('--debug', '-d', action='store_true', 
                       help='Enable debug logging to /tmp/aws_net_runner_debug_<timestamp>.log')
    args = parser.parse_args()

    # Get commands from args or stdin
    commands = args.commands
    if not commands and not sys.stdin.isatty():
        commands = sys.stdin.read().strip().split('\n')

    if not commands:
        parser.print_help()
        sys.exit(1)

    runner = ShellRunner(profile=args.profile, timeout=args.timeout, debug=args.debug)
    try:
        runner.start()
        runner.run_sequence(commands)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        if runner.logger:
            runner.logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        runner.close()


if __name__ == '__main__':
    main()
