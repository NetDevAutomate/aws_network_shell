"""Decorators for shell command validation."""

from functools import wraps
from typing import Callable, Any
from rich.console import Console

console = Console()


def requires_context(*context_types: str) -> Callable:
    """Decorator to validate shell context before executing command.

    Args:
        *context_types: One or more valid context types (e.g., "vpc", "core-network")

    Usage:
        @requires_context("core-network")
        def _show_rib(self, args):
            ...

        @requires_context("vpc", "transit-gateway")  # Either context is valid
        def _show_route_tables(self, _):
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            if self.ctx_type not in context_types:
                if len(context_types) == 1:
                    console.print(f"[red]Must be in {context_types[0]} context[/]")
                else:
                    console.print(
                        f"[red]Must be in one of: {', '.join(context_types)}[/]"
                    )
                return None
            return func(self, *args, **kwargs)

        return wrapper

    return decorator


def requires_root(func: Callable) -> Callable:
    """Decorator to ensure command runs only at root level.

    Usage:
        @requires_root
        def do_trace(self, args):
            ...
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs) -> Any:
        if self.ctx_type is not None:
            console.print(
                f"[red]{func.__name__.replace('do_', '')} only at root level[/]"
            )
            return None
        return func(self, *args, **kwargs)

    return wrapper


def cached_command(cache_key: str, fetch_msg: str = "Loading...") -> Callable:
    """Decorator to handle caching pattern for show commands.

    Args:
        cache_key: Key to use in shell._cache
        fetch_msg: Message to show during fetch

    Usage:
        @cached_command("vpc", "Fetching VPCs")
        def _show_vpcs(self, _):
            return vpc.VPCClient(self.profile).discover()
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            # Check if function returns a fetch callable
            result = func(self, *args, **kwargs)
            if callable(result):
                # It's a fetch function, use caching
                return self._cached(cache_key, result, fetch_msg)
            return result

        return wrapper

    return decorator
