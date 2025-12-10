"""Base shell class with hierarchy and context management."""

import cmd2
from typing import Optional
from rich.console import Console
from rich.text import Text
from dataclasses import dataclass, field
from ..themes import load_theme, get_theme_dir
from ..config import get_config, RuntimeConfig

console = Console()

# Cisco IOS-style command aliases
ALIASES = {
    "sh": "show",
    "conf": "config",
    "ex": "exit",
    "int": "interface",
    "no": "unset",
}

# Strict hierarchy: context_type -> {show: [...], set: [...], commands: [...]}
HIERARCHY = {
    None: {
        "show": [
            "version",
            "global-networks",
            "vpcs",
            "transit_gateways",
            "firewalls",
            "dx-connections",
            "enis",
            "bgp-neighbors",
            "ec2-instances",
            "elbs",
            "vpns",
            "security-groups",
            "unused-sgs",
            "resolver-endpoints",
            "resolver-rules",
            "query-logs",
            "peering-connections",
            "prefix-lists",
            "network-alarms",
            "alarms-critical",
            "client-vpn-endpoints",
            "global-accelerators",
            "ga-endpoint-health",
            "endpoint-services",
            "vpc-endpoints",
            "config",
            "running-config",
            "cache",
            "routing-cache",
            "graph",
        ],
        "set": [
            "global-network",
            "vpc",
            "transit-gateway",
            "firewall",
            "ec2-instance",
            "elb",
            "vpn",
            "profile",
            "regions",
            "no-cache",
            "output-format",
            "output-file",
            "watch",
            "theme",
            "prompt",
        ],
        "commands": [
            "show",
            "set",
            "write",
            "trace",
            "find_ip",
            "find_prefix",
            "find_null_routes",
            "populate_cache",
            "clear_cache",
            "refresh",
            "create_routing_cache",
            "save_routing_cache",
            "load_routing_cache",
            "validate_graph",
            "export_graph",
            "clear",
            "exit",
        ],
    },
    "global-network": {
        "show": ["detail", "core-networks"],
        "set": ["core-network"],
        "commands": ["show", "set", "refresh", "exit", "end"],
    },
    "core-network": {
        "show": [
            "detail",
            "segments",
            "policy-documents",
            "live-policy",
            "routes",
            "route-tables",
            "blackhole-routes",
            "policy-change-events",
            "connect-attachments",
            "connect-peers",
            "rib",
        ],
        "set": ["route-table"],
        "commands": ["show", "set", "find_prefix", "find_null_routes", "refresh", "exit", "end"],
    },
    "route-table": {
        "show": ["routes"],
        "set": [],
        "commands": ["show", "find_prefix", "find_null_routes", "refresh", "exit", "end"],
    },
    "vpc": {
        "show": [
            "detail",
            "route-tables",
            "subnets",
            "security-groups",
            "nacls",
            "internet-gateways",
            "nat-gateways",
            "endpoints",
        ],
        "set": ["route-table"],
        "commands": ["show", "set", "find_prefix", "find_null_routes", "refresh", "exit", "end"],
    },
    "transit-gateway": {
        "show": ["detail", "route-tables", "attachments"],
        "set": ["route-table"],
        "commands": ["show", "set", "find_prefix", "find_null_routes", "refresh", "exit", "end"],
    },
    "firewall": {
        "show": ["firewall", "detail", "firewall-rule-groups", "rule-groups", "policy", "firewall-policy", "firewall-networking"],
        "set": ["rule-group"],
        "commands": ["show", "set", "refresh", "exit", "end"],
    },
    "rule-group": {
        "show": ["rule-group"],
        "set": [],
        "commands": ["show", "refresh", "exit", "end"],
    },
    "ec2-instance": {
        "show": ["detail", "security-groups", "enis", "routes"],
        "set": [],
        "commands": ["show", "refresh", "exit", "end"],
    },
    "elb": {
        "show": ["detail", "listeners", "targets", "health"],
        "set": [],
        "commands": ["show", "refresh", "exit", "end"],
    },
    "vpn": {
        "show": ["detail", "tunnels"],
        "set": [],
        "commands": ["show", "refresh", "exit", "end"],
    },
}


@dataclass
class Context:
    """Shell execution context."""

    type: str
    ref: str
    name: str
    data: dict = field(default_factory=dict)
    selection_index: int = 0  # The index from the show command (1-based)


class AWSNetShellBase(cmd2.Cmd):
    """Base shell with context management and navigation."""

    intro = "AWS Network Tools CLI\nType '?' for help, 'show ?' for show options.\n"

    def __init__(self):
        super().__init__(allow_cli_args=False)
        self.profile: Optional[str] = None
        self.regions: list[str] = []
        self.no_cache = False
        self.output_format: str = "table"
        self.watch_interval: int = 0
        self.context_stack: list[Context] = []
        self._cache: dict = {}
        
        # Load theme and config
        self.config = get_config()
        theme_name = self.config.get_theme_name()
        self.theme = load_theme(theme_name)
        
        # Initialize RuntimeConfig with shell defaults
        RuntimeConfig.set_profile(self.profile)
        RuntimeConfig.set_regions(self.regions)
        RuntimeConfig.set_no_cache(self.no_cache)
        RuntimeConfig.set_output_format(self.output_format)

        self.hidden_commands.extend(
            [
                "alias",
                "macro",
                "run_pyscript",
                "run_script",
                "shell",
                "shortcuts",
                "edit",
                "py",
                "ipy",
                "history",
                "quit",
                "q",
                "_relative_run_script",
                "eof",
                "eos",
                "help",
            ]
        )
        self._update_prompt()
    
    def _sync_runtime_config(self):
        """Synchronize shell state with RuntimeConfig singleton."""
        RuntimeConfig.set_profile(self.profile)
        RuntimeConfig.set_regions(self.regions)
        RuntimeConfig.set_no_cache(self.no_cache)
        RuntimeConfig.set_output_format(self.output_format)

    @property
    def ctx(self) -> Optional[Context]:
        return self.context_stack[-1] if self.context_stack else None

    @property
    def ctx_type(self) -> Optional[str]:
        return self.ctx.type if self.ctx else None

    @property
    def ctx_id(self) -> str:
        return self.ctx.ref if self.ctx else ""

    @property
    def hierarchy(self) -> dict:
        return HIERARCHY.get(self.ctx_type, HIERARCHY[None])

    def _update_prompt(self):
        """Update prompt based on context stack and theme."""
        if not self.context_stack:
            self.prompt = "aws-net> "
            return
        
        # Get prompt configuration
        style = self.config.get_prompt_style()  # "short" or "long"
        show_indices = self.config.show_indices()
        max_length = self.config.get_max_length()
        
        prompt_parts = []
        
        for i, ctx in enumerate(self.context_stack):
            # Get color for this context type
            color = self.theme.get(ctx.type, "white")
            
            # Get abbreviation for context type
            if ctx.type == "global-network":
                abbrev = "gl"
            elif ctx.type == "core-network":
                abbrev = "cn"
            elif ctx.type == "transit-gateway":
                abbrev = "tg"
            elif ctx.type == "ec2-instance":
                abbrev = "ec"
            else:
                abbrev = ctx.type[:2]
            
            if style == "short":
                # Short format: use index number like gl:1, cn:1
                ctx_name = f"{abbrev}:{ctx.selection_index}"
            else:  # long format
                if show_indices:
                    # Long format with indices: gl:1:name or gl:1
                    if ctx.name:
                        ctx_name = f"{abbrev}:{ctx.selection_index}:{ctx.name}"
                    else:
                        ctx_name = f"{abbrev}:{ctx.selection_index}"
                else:
                    # Long format without indices: gl:name
                    display_name = ctx.name or ctx.ref
                    if len(display_name) > max_length:
                        display_name = display_name[:max_length-3] + "..."
                    ctx_name = f"{abbrev}:{display_name}"
            
            # Create colored text part (no newlines embedded)
            from rich.text import Text
            colored_part = Text(f"{ctx_name}", style=color)
            prompt_parts.append(colored_part)
        
        # Create the full prompt
        if style == "long":
            # Multi-line prompt with continuation markers
            prompt_text = Text("aws-net> ", style=self.theme.get("prompt_text"))
            separator_style = self.theme.get("prompt_separator")
            
            if prompt_parts:
                # First context on same line as aws-net>
                prompt_text.append(prompt_parts[0])
                
                if len(prompt_parts) > 1:
                    # Multiple contexts - use multi-line format
                    prompt_text.append(Text(" >\n", style=separator_style))
                    
                    # Middle contexts (all except first and last)
                    for i, part in enumerate(prompt_parts[1:-1], 1):
                        indent = "  " * i  # Two spaces per level
                        prompt_text.append(Text(f"{indent}", style=separator_style))
                        prompt_text.append(part)
                        prompt_text.append(Text(" >\n", style=separator_style))
                    
                    # Last context
                    last_idx = len(prompt_parts) - 1
                    indent = "  " * last_idx
                    prompt_text.append(Text(f"{indent}", style=separator_style))
                    prompt_text.append(prompt_parts[-1])
                    prompt_text.append(Text(" $ ", style=separator_style))
                else:
                    # Only one context - add prompt marker on same line
                    prompt_text.append(Text(" $ ", style=separator_style))
            else:
                # No contexts - just root
                prompt_text.append(Text(" $ ", style=separator_style))
        else:
            # Single line prompt (unchanged)
            separator_color = self.theme.get("prompt_separator")
            prompt_text = Text("aws-net", style=self.theme.get("prompt_text"))
            if prompt_parts:
                for part in prompt_parts:
                    prompt_text.append(f">", style=separator_color)
                    prompt_text.append(part)
            prompt_text.append("> ", style=separator_color)
        
        # Render Text to ANSI codes for cmd2
        from rich.console import Console
        render_console = Console(force_terminal=True, color_system="standard")
        with render_console.capture() as capture:
            render_console.print(prompt_text, end="")
        self.prompt = capture.get()

    def _enter(self, ctx_type: str, res_id: str, name: str, data: dict = None, selection_index: int = 1):
        """Enter a new context."""
        self.context_stack.append(Context(ctx_type, res_id, name, data or {}, selection_index))
        self._update_prompt()

    def _resolve(self, items: list, val: str) -> Optional[dict]:
        """Resolve a resource by index, ID, or name."""
        try:
            idx = int(val)
            if 1 <= idx <= len(items):
                return items[idx - 1]
        except ValueError:
            pass
        for item in items:
            if item.get("id") == val or (item.get("name") or "").lower() == val.lower():
                return item
        return None

    def _set_output_file(self, val):
        """Set output file for saving results."""
        self.output_file = val if val else None
        if val:
            console.print(f"[green]Output will be saved to: {val}[/]")
        else:
            console.print("[green]Output file cleared[/]")

    def _save_output(self, data, filename: str = None):
        """Save data to file in current output format."""
        import json
        import yaml

        target = filename or getattr(self, "output_file", None)
        if not target:
            return False
        try:
            with open(target, "w") as f:
                if self.output_format == "json":
                    json.dump(data, f, indent=2, default=str)
                elif self.output_format == "yaml":
                    yaml.safe_dump(data, f, sort_keys=False)
                else:
                    f.write(str(data))
            console.print(f"[green]Saved to {target}[/]")
            return True
        except Exception as e:
            console.print(f"[red]Failed to save: {e}[/]")
            return False

    def do_exit(self, _):
        """Go back one context level or quit."""
        if self.context_stack:
            self.context_stack.pop()
            self._update_prompt()
        else:
            return True

    def do_end(self, _):
        """Return to root level."""
        self.context_stack.clear()
        self._update_prompt()

    def do_clear(self, _):
        """Clear the screen."""
        console.clear()

    def do_clear_cache(self, _):
        """Clear all cached data."""
        self._cache.clear()
        console.print("[green]Cache cleared[/]")

    def do_refresh(self, args):
        """Refresh cached data. Usage: refresh [target|all]
        
        Examples:
            refresh                    - Refresh current context data
            refresh transit_gateways   - Clear transit gateways cache
            refresh all                - Clear all caches
        """
        target = str(args).strip().lower().replace("-", "_") if args else ""
        
        if not target or target == "current":
            # Refresh current context by clearing relevant cache keys
            context_to_cache = {
                "elb": "elbs",
                "vpc": "vpcs",
                "transit-gateway": "transit_gateways",
                "firewall": "firewalls",
                "ec2-instance": "ec2_instances",
                "vpn": "vpns",
                "global-network": "global_networks",
                "core-network": "core_networks",
                "route-table": "core_networks",  # Route tables belong to core networks
            }
            
            cache_key = context_to_cache.get(self.ctx_type)
            if not cache_key:
                console.print("[yellow]No cache to refresh in current context[/]")
                return
                
            if cache_key in self._cache:
                del self._cache[cache_key]
                console.print(f"[green]Refreshed {cache_key} cache[/]")
            else:
                console.print(f"[yellow]No cached data for {cache_key}[/]")
                
        elif target == "all":
            # Clear entire cache
            count = len(self._cache)
            self._cache.clear()
            console.print(f"[green]Cleared {count} cache entries[/]")
            
        else:
            # Clear specific cache key with alias support
            cache_aliases = {
                # Standard plural names (canonical)
                "vpcs": "vpcs",
                "transit_gateways": "transit_gateways",
                "firewalls": "firewalls",
                "elbs": "elbs",
                "vpns": "vpns",
                "enis": "enis",
                "global_networks": "global_networks",
                "core_networks": "core_networks",
                "security_groups": "security_groups",
                "dx_connections": "dx_connections",
                "bgp_neighbors": "bgp_neighbors",
                "route53_resolver": "route53_resolver",
                "peering_connections": "peering_connections",
                "prefix_lists": "prefix_lists",
                "network_alarms": "network_alarms",
                "client_vpn_endpoints": "client_vpn_endpoints",
                "global_accelerators": "global_accelerators",
                "vpc_endpoints": "vpc_endpoints",
                
                # Singular aliases
                "vpc": "vpcs",
                "transit_gateway": "transit_gateways",
                "firewall": "firewalls",
                "elb": "elbs",
                "vpn": "vpns",
                "eni": "enis",
                "global_network": "global_networks",
                "core_network": "core_networks",
                "security_group": "security_groups",
                "dx_connection": "dx_connections",
                "bgp_neighbor": "bgp_neighbors",
                "peering_connection": "peering_connections",
                "prefix_list": "prefix_lists",
                "network_alarm": "network_alarms",
                "client_vpn_endpoint": "client_vpn_endpoints",
                "global_accelerator": "global_accelerators",
                "vpc_endpoint": "vpc_endpoints",
                
                # Common abbreviations
                "tgw": "transit_gateways",
                "tgws": "transit_gateways",
                "sg": "security_groups",
                "sgs": "security_groups",
                "dx": "dx_connections",
                "r53": "route53_resolver",
                "ga": "global_accelerators",
                "ec2": "ec2_instances",
            }
            
            cache_key = cache_aliases.get(target, target)
            
            if cache_key in self._cache:
                del self._cache[cache_key]
                console.print(f"[green]Refreshed {cache_key} cache[/]")
            else:
                console.print(f"[yellow]No cached data for {cache_key}[/]")

    def do_help(self, _):
        """Show available commands."""
        self._show_cmds()

    def precmd(self, line: cmd2.Statement) -> cmd2.Statement:
        """Expand aliases before command execution."""
        raw = str(line).strip()
        if not raw:
            return line
        # Expand aliases (e.g., 'sh vpcs' -> 'show vpcs')
        parts = raw.split(maxsplit=1)
        if parts[0] in ALIASES:
            expanded = ALIASES[parts[0]] + (" " + parts[1] if len(parts) > 1 else "")
            return cmd2.Statement(expanded)
        return line

    def _apply_pipe_filter(self, output: str, pipe_cmd: str) -> str:
        """Apply pipe filter (include/exclude/grep) to output."""
        parts = pipe_cmd.strip().split(maxsplit=1)
        if len(parts) < 2:
            return output
        cmd, pattern = parts[0].lower(), parts[1]
        lines = output.split("\n")
        if cmd in ("include", "grep", "i"):
            return "\n".join(line for line in lines if pattern.lower() in line.lower())
        elif cmd in ("exclude", "e"):
            return "\n".join(
                line for line in lines if pattern.lower() not in line.lower()
            )
        return output

    def default(self, stmt):
        """Handle unknown commands and ? help."""
        line = str(stmt).strip()
        if line in ("?", ""):
            self._show_cmds()
        elif line.endswith("?"):
            base = line[:-1].strip()
            if base in ("show", "set"):
                console.print(f"[bold]{base} options:[/]")
                for opt in sorted(self.hierarchy.get(base, [])):
                    console.print(f"  {base} {opt}")
            else:
                console.print(f"[red]Unknown: {base}[/]")
        else:
            console.print(f"[red]Unknown command: {line}[/]")

    def _show_cmds(self):
        """Display available commands for current context."""
        console.print("[bold]Commands:[/]")
        for cmd in sorted(self.hierarchy.get("commands", [])):
            console.print(f"  {cmd}")
