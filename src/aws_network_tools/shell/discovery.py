"""Dynamic command discovery from HIERARCHY structure.

This module provides dynamic derivation of list/set commands from the
canonical HIERARCHY definition, eliminating hardcoded mappings that can drift.
"""

from typing import Dict, Optional

from .base import HIERARCHY


class CommandDiscovery:
    """Discovers list/set commands dynamically from HIERARCHY.

    This class provides a single source of truth for command mappings,
    derived from the HIERARCHY structure rather than hardcoded values.
    """

    # Pluralization rules for context types -> show command targets
    PLURAL_MAP = {
        "global-network": "global-networks",
        "vpc": "vpcs",
        "transit-gateway": "transit_gateways",
        "firewall": "firewalls",
        "ec2-instance": "ec2-instances",
        "elb": "elbs",
        "vpn": "vpns",
        "core-network": "core-networks",
        "route-table": "route-tables",
    }

    # Set command aliases (context type -> actual set argument)
    SET_ALIASES = {
        "transit-gateway": "tgw",  # Legacy abbreviation
    }

    def __init__(self, hierarchy: Optional[Dict] = None):
        """Initialize with optional custom hierarchy for testing.

        Args:
            hierarchy: Optional hierarchy dict. Uses HIERARCHY from base.py if None.
        """
        self._hierarchy = hierarchy if hierarchy is not None else HIERARCHY
        self._list_cache: Dict[str, str] = {}
        self._set_cache: Dict[str, str] = {}
        self._reverse_list_cache: Dict[str, str] = {}
        self._reverse_set_cache: Dict[str, str] = {}
        self._build_caches()

    def _build_caches(self) -> None:
        """Build all command caches from hierarchy."""
        root_shows = self._hierarchy.get(None, {}).get("show", [])
        root_sets = self._hierarchy.get(None, {}).get("set", [])

        # Build list command cache
        for ctx_type, plural in self.PLURAL_MAP.items():
            if plural in root_shows or ctx_type in self._hierarchy:
                self._list_cache[ctx_type] = f"show {plural}"
                self._reverse_list_cache[f"show {plural}"] = ctx_type

        # Build set command cache
        for ctx_type in self._hierarchy:
            if ctx_type is None:
                continue

            # Check if context can be entered from root or parent
            alias = self.SET_ALIASES.get(ctx_type, ctx_type)

            # Verify the set command exists in hierarchy
            if ctx_type in root_sets or alias in root_sets:
                self._set_cache[ctx_type] = f"set {alias}"
                self._reverse_set_cache[f"set {alias}"] = ctx_type
            else:
                # Check if it's a nested context
                for parent_ctx, parent_def in self._hierarchy.items():
                    if parent_ctx is None:
                        continue
                    if ctx_type in parent_def.get("set", []):
                        self._set_cache[ctx_type] = f"set {alias}"
                        self._reverse_set_cache[f"set {alias}"] = ctx_type
                        break

    def get_list_command(self, ctx_type: Optional[str]) -> Optional[str]:
        """Get the list command for a context type.

        Args:
            ctx_type: The context type (e.g., "vpc", "transit-gateway")

        Returns:
            The list command (e.g., "show vpcs") or None if not found
        """
        if ctx_type is None:
            return None
        return self._list_cache.get(ctx_type)

    def get_set_command(self, ctx_type: Optional[str]) -> Optional[str]:
        """Get the set command for a context type.

        Args:
            ctx_type: The context type (e.g., "vpc", "transit-gateway")

        Returns:
            The set command (e.g., "set vpc", "set tgw") or None if not found
        """
        if ctx_type is None:
            return None
        return self._set_cache.get(ctx_type)

    def get_context_from_list(self, list_cmd: str) -> Optional[str]:
        """Reverse lookup: get context type from list command.

        Args:
            list_cmd: The list command (e.g., "show vpcs")

        Returns:
            The context type or None if not found
        """
        return self._reverse_list_cache.get(list_cmd)

    def get_context_from_set(self, set_cmd: str) -> Optional[str]:
        """Reverse lookup: get context type from set command.

        Args:
            set_cmd: The set command (e.g., "set vpc", "set tgw")

        Returns:
            The context type or None if not found
        """
        return self._reverse_set_cache.get(set_cmd)

    @property
    def context_list_commands(self) -> Dict[str, str]:
        """Get all context -> list command mappings.

        Returns:
            Dict mapping context_type to list command
        """
        return self._list_cache.copy()

    @property
    def context_set_commands(self) -> Dict[str, str]:
        """Get all context -> set command mappings.

        Returns:
            Dict mapping context_type to set command
        """
        return self._set_cache.copy()

    def get_sub_context(self, set_opt: str) -> Optional[str]:
        """Map a set option to its context type.

        Args:
            set_opt: The set option (e.g., "core-network", "route-table")

        Returns:
            The context type if it exists in hierarchy, None otherwise
        """
        # Direct match
        if set_opt in self._hierarchy:
            return set_opt

        # Check reverse alias
        for ctx_type, alias in self.SET_ALIASES.items():
            if alias == set_opt and ctx_type in self._hierarchy:
                return ctx_type

        return None


# Singleton instance for easy import
discovery = CommandDiscovery()
