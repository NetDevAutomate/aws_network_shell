"""Cisco IOS-style hierarchical CLI - redirects to modular shell package.

This module is kept for backward compatibility. The actual implementation
is now in the shell/ package with modular handlers.
"""

# Re-export everything from the modular shell package
from .shell import AWSNetShellV2, AWSNetShellBase, Context, HIERARCHY, main

__all__ = ["AWSNetShellV2", "AWSNetShellBase", "Context", "HIERARCHY", "main"]
