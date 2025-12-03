"""Spinner with task monitoring"""

import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, TypeVar, Optional
from rich.console import Console
from rich.spinner import Spinner
from rich.live import Live

T = TypeVar("T")


def _should_use_spinner() -> bool:
    """Check if spinner should be used based on environment and output type."""
    # Disable spinner in test environments (pytest, pexpect, etc.)
    # Detect by checking if we're running from tests/ or have test-related env vars
    if (
        "pytest" in sys.modules
        or os.path.basename(sys.argv[0]).startswith("test_")
        or os.environ.get("PYTEST_CURRENT_TEST")
        or os.environ.get("NO_SPINNER")
    ):
        return False

    # Force enable spinner when FORCE_SPINNER env var is set
    if os.environ.get("FORCE_SPINNER", "").lower() in ("true", "1", "yes"):
        return True

    # Disable spinner in CI environments
    if os.environ.get("CI", "").lower() in ("true", "1", "yes"):
        return False

    # Check if we have a real TTY
    if sys.stdout.isatty():
        return True

    # Default: disable for non-tty output
    return False


def run_with_spinner(
    func: Callable[[], T],
    message: str = "Loading...",
    timeout_seconds: int = 300,
    console: Optional[Console] = None,
) -> T:
    """Run a function with a spinner"""
    # Disable spinner for CI/non-tty environments
    if not _should_use_spinner():
        # Just run the function without any spinner
        return func()

    console = console or Console()
    result: Optional[T] = None
    exception: Optional[Exception] = None
    task_done = threading.Event()

    def worker():
        nonlocal result, exception
        try:
            result = func()
        except Exception as e:
            exception = e
        finally:
            task_done.set()

    executor = ThreadPoolExecutor(max_workers=1)
    executor.submit(worker)
    start_time = time.time()

    with Live(
        Spinner("dots", text=message, style="cyan"),
        console=console,
        refresh_per_second=10,
        transient=True,
    ) as live:
        while not task_done.is_set():
            elapsed = time.time() - start_time
            if elapsed > timeout_seconds:
                executor.shutdown(wait=False, cancel_futures=True)
                raise TimeoutError(f"Task timed out after {timeout_seconds}s")
            live.update(
                Spinner("dots", text=f"{message} ({elapsed:.1f}s)", style="cyan")
            )
            time.sleep(0.5)

    executor.shutdown(wait=True)
    if exception:
        raise exception
    return result
