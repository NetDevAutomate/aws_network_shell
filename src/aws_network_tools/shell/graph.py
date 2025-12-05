"""Command hierarchy graph with dynamic discovery, validation, and visualization.

This module provides:
1. CommandGraph - A proper graph data structure built from HIERARCHY + code introspection
2. Validation - Ensures HIERARCHY matches implemented handlers
3. Mermaid export - Visual representation of the command tree

Architecture based on multi-model review (Claude, DeepSeek, Nova, Kimi, Gemini).
"""

import inspect
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional
from datetime import datetime

from .base import HIERARCHY


class NodeType(Enum):
    """Type of command node."""

    ROOT = "root"
    CONTEXT = "context"
    SHOW = "show"
    SET = "set"
    ACTION = "action"


class Severity(Enum):
    """Validation issue severity."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class CommandNode:
    """A node in the command graph."""

    id: str
    name: str
    node_type: NodeType
    context: Optional[str] = None
    enters_context: Optional[str] = None
    handler: Optional[str] = None
    implemented: bool = False
    children: list["CommandNode"] = field(default_factory=list)

    def __hash__(self):
        return hash(self.id)


@dataclass
class GraphEdge:
    """Edge between nodes with metadata."""

    source: str
    target: str
    edge_type: str = "child"


@dataclass
class ValidationIssue:
    """Single validation issue with severity."""

    severity: Severity
    category: str
    context: Optional[str]
    message: str


@dataclass
class ValidationResult:
    """Result of graph validation."""

    valid: bool
    issues: list[ValidationIssue]
    stats: dict

    @property
    def errors(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == Severity.ERROR]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == Severity.WARNING]

    def __str__(self):
        lines = [f"Valid: {self.valid}"]
        if self.errors:
            lines.append(f"Errors ({len(self.errors)}):")
            for i in self.errors:
                lines.append(f"  [{i.context or 'root'}] {i.message}")
        if self.warnings:
            lines.append(f"Warnings ({len(self.warnings)}):")
            for i in self.warnings:
                lines.append(f"  {i.message}")
        return "\n".join(lines)


class CommandGraph:
    """Graph representation of shell command hierarchy."""

    # Map set commands to context types they enter
    SET_TO_CONTEXT = {
        "global-network": "global-network",
        "core-network": "core-network",
        "route-table": "route-table",
        "vpc": "vpc",
        "transit-gateway": "transit-gateway",
        "tgw": "transit-gateway",
        "firewall": "firewall",
        "ec2-instance": "ec2-instance",
        "elb": "elb",
        "vpn": "vpn",
    }

    # cmd2 built-in methods to ignore
    CMD2_BUILTINS = {
        "do_alias",
        "do_macro",
        "do_run_pyscript",
        "do_run_script",
        "do_shell",
        "do_shortcuts",
        "do_edit",
        "do_py",
        "do_ipy",
        "do_history",
        "do_quit",
        "do__relative_run_script",
        "do_eof",
        "do_help",
        "do_exit",
        "do_end",
        "do_clear",
        "do_run",
        "_set_up_cmd2_readline",
        "_set_up_py_shell_env",
        "_show_cmds",
        "_show_vpc",
        "_show_cloudwan_route_tables",
        "_show_vpc_route_tables",
        "_show_transit_gateway_route_tables",
        "_show_command_path",
        "_set_vpc_route_table",
        "_show_core_network_policy",
        "_show_policy_document_diff",
    }

    # Navigation commands (not real handlers)
    NAV_COMMANDS = {"show", "set", "exit", "end", "clear"}

    # Config commands (handled specially)
    CONFIG_SETS = {
        "profile",
        "regions",
        "no-cache",
        "output-format",
        "output-file",
        "watch",
    }

    def __init__(self):
        self.root = CommandNode(
            id="root", name="aws-net", node_type=NodeType.ROOT, implemented=True
        )
        self.nodes: dict[str, CommandNode] = {"root": self.root}
        self.edges: list[GraphEdge] = []
        self._handlers: dict[str, set[str]] = {}
        self._built_at: Optional[datetime] = None

    def build(self, shell_class=None):
        """Build graph from HIERARCHY and discover handlers from shell class."""
        if shell_class:
            self._discover_handlers(shell_class)
        self._build_context(None, self.root)
        self._built_at = datetime.now()
        return self

    def _discover_handlers(self, shell_class):
        """Discover all handler methods from shell class and its mixins."""
        self._handlers = {None: set()}
        for ctx in HIERARCHY:
            self._handlers[ctx] = set()

        for name, method in inspect.getmembers(
            shell_class, predicate=inspect.isfunction
        ):
            if name.startswith("_show_"):
                handler_name = name[6:]
                for ctx in self._handlers:
                    self._handlers[ctx].add(f"show.{handler_name}")
            elif name.startswith("_set_"):
                handler_name = name[5:]
                for ctx in self._handlers:
                    self._handlers[ctx].add(f"set.{handler_name}")
            elif name.startswith("do_"):
                handler_name = name[3:]
                for ctx in self._handlers:
                    self._handlers[ctx].add(f"do.{handler_name}")

    def _build_context(self, ctx_type: Optional[str], parent: CommandNode):
        """Build nodes for a context."""
        ctx_def = HIERARCHY.get(ctx_type, {})
        ctx_key = ctx_type or "root"

        # Show commands
        for show_opt in ctx_def.get("show", []):
            node_id = f"{ctx_key}.show.{show_opt}"
            handler_key = f"show.{show_opt.replace('-', '_')}"
            implemented = handler_key in self._handlers.get(ctx_type, set())

            node = CommandNode(
                id=node_id,
                name=f"show {show_opt}",
                node_type=NodeType.SHOW,
                context=ctx_type,
                handler=f"_show_{show_opt.replace('-', '_')}",
                implemented=implemented,
            )
            self.nodes[node_id] = node
            parent.children.append(node)
            self.edges.append(GraphEdge(parent.id, node_id))

        # Set commands (context-entering)
        for set_opt in ctx_def.get("set", []):
            if set_opt in self.CONFIG_SETS:
                node_id = f"{ctx_key}.set.{set_opt}"
                handler_key = f"set.{set_opt.replace('-', '_')}"
                implemented = handler_key in self._handlers.get(ctx_type, set())

                node = CommandNode(
                    id=node_id,
                    name=f"set {set_opt}",
                    node_type=NodeType.SET,
                    context=ctx_type,
                    handler=f"_set_{set_opt.replace('-', '_')}",
                    implemented=implemented,
                )
                self.nodes[node_id] = node
                parent.children.append(node)
                self.edges.append(GraphEdge(parent.id, node_id))
            elif set_opt in self.SET_TO_CONTEXT:
                target_ctx = self.SET_TO_CONTEXT[set_opt]
                node_id = f"{ctx_key}.set.{set_opt}"
                handler_key = f"set.{set_opt.replace('-', '_')}"
                implemented = handler_key in self._handlers.get(ctx_type, set())

                node = CommandNode(
                    id=node_id,
                    name=f"set {set_opt}",
                    node_type=NodeType.CONTEXT,
                    context=ctx_type,
                    enters_context=target_ctx,
                    handler=f"_set_{set_opt.replace('-', '_')}",
                    implemented=implemented,
                )
                self.nodes[node_id] = node
                parent.children.append(node)
                self.edges.append(GraphEdge(parent.id, node_id, "enters"))

                if target_ctx in HIERARCHY and target_ctx != ctx_type:
                    self._build_context(target_ctx, node)

        # Action commands (do_*)
        for cmd in ctx_def.get("commands", []):
            if cmd in self.NAV_COMMANDS:
                continue
            node_id = f"{ctx_key}.do.{cmd}"
            handler_key = f"do.{cmd.replace('-', '_')}"
            implemented = handler_key in self._handlers.get(ctx_type, set())

            node = CommandNode(
                id=node_id,
                name=cmd,
                node_type=NodeType.ACTION,
                context=ctx_type,
                handler=f"do_{cmd.replace('-', '_')}",
                implemented=implemented,
            )
            self.nodes[node_id] = node
            parent.children.append(node)
            self.edges.append(GraphEdge(parent.id, node_id))

    def validate(self, shell_class=None) -> ValidationResult:
        """Validate graph against implemented handlers."""
        if shell_class and not self._handlers:
            self._discover_handlers(shell_class)

        issues = []

        # Check all HIERARCHY entries have handlers
        for ctx_type, ctx_def in HIERARCHY.items():
            ctx_name = ctx_type or "root"

            for show_opt in ctx_def.get("show", []):
                handler = f"_show_{show_opt.replace('-', '_')}"
                if not self._has_handler(shell_class, handler):
                    issues.append(
                        ValidationIssue(
                            Severity.ERROR,
                            "MISSING_HANDLER",
                            ctx_name,
                            f"Missing handler for 'show {show_opt}'",
                        )
                    )

            for set_opt in ctx_def.get("set", []):
                handler = f"_set_{set_opt.replace('-', '_')}"
                if not self._has_handler(shell_class, handler):
                    issues.append(
                        ValidationIssue(
                            Severity.ERROR,
                            "MISSING_HANDLER",
                            ctx_name,
                            f"Missing handler for 'set {set_opt}'",
                        )
                    )

            for cmd in ctx_def.get("commands", []):
                if cmd in self.NAV_COMMANDS:
                    continue
                handler = f"do_{cmd.replace('-', '_')}"
                if not self._has_handler(shell_class, handler):
                    issues.append(
                        ValidationIssue(
                            Severity.ERROR,
                            "MISSING_HANDLER",
                            ctx_name,
                            f"Missing handler for '{cmd}'",
                        )
                    )

        # Find orphan handlers
        if shell_class:
            all_hierarchy_handlers = set()
            for ctx_type, ctx_def in HIERARCHY.items():
                for show_opt in ctx_def.get("show", []):
                    all_hierarchy_handlers.add(f"_show_{show_opt.replace('-', '_')}")
                for set_opt in ctx_def.get("set", []):
                    all_hierarchy_handlers.add(f"_set_{set_opt.replace('-', '_')}")
                for cmd in ctx_def.get("commands", []):
                    if cmd not in self.NAV_COMMANDS:
                        all_hierarchy_handlers.add(f"do_{cmd.replace('-', '_')}")

            for name, _ in inspect.getmembers(
                shell_class, predicate=inspect.isfunction
            ):
                if (
                    name.startswith(("_show_", "_set_", "do_"))
                    and not name.startswith("do_show")
                    and not name.startswith("do_set")
                ):
                    if (
                        name not in all_hierarchy_handlers
                        and name not in self.CMD2_BUILTINS
                    ):
                        issues.append(
                            ValidationIssue(
                                Severity.WARNING,
                                "ORPHAN_HANDLER",
                                None,
                                f"Handler '{name}' not in HIERARCHY",
                            )
                        )

        # Check hierarchy structure
        for ctx_type, ctx_def in HIERARCHY.items():
            for set_opt in ctx_def.get("set", []):
                if set_opt in self.SET_TO_CONTEXT:
                    target = self.SET_TO_CONTEXT[set_opt]
                    if target not in HIERARCHY:
                        issues.append(
                            ValidationIssue(
                                Severity.ERROR,
                                "STRUCTURAL",
                                ctx_type,
                                f"set {set_opt} targets unknown context '{target}'",
                            )
                        )

        stats = {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "errors": len([i for i in issues if i.severity == Severity.ERROR]),
            "warnings": len([i for i in issues if i.severity == Severity.WARNING]),
        }

        return ValidationResult(
            valid=stats["errors"] == 0,
            issues=issues,
            stats=stats,
        )

    def _has_handler(self, shell_class, handler_name: str) -> bool:
        """Check if handler exists in shell class."""
        if not shell_class:
            return True
        return hasattr(shell_class, handler_name)

    def to_mermaid(self, use_subgraphs: bool = False) -> str:
        """Generate Mermaid diagram of command hierarchy."""
        lines = ["graph TD"]

        # Style definitions
        lines.extend(
            [
                "    classDef root fill:#2d5a27,stroke:#1a3518,color:#fff",
                "    classDef context fill:#1a4a6e,stroke:#0d2840,color:#fff",
                "    classDef show fill:#4a4a8a,stroke:#2d2d5a,color:#fff",
                "    classDef set fill:#6b4c9a,stroke:#3d2a5a,color:#fff",
                "    classDef action fill:#8b4513,stroke:#5a2d0a,color:#fff",
                "    classDef unimpl fill:#666,stroke:#333,color:#fff,stroke-dasharray: 5 5",
                "",
            ]
        )

        if use_subgraphs:
            self._mermaid_with_subgraphs(lines)
        else:
            visited = set()
            self._mermaid_node(self.root, lines, visited)

        return "\n".join(lines)

    def _mermaid_with_subgraphs(self, lines: list):
        """Generate Mermaid with subgraphs for each context."""
        # Root node
        lines.append('    root[["aws-net"]]')
        lines.append("    class root root")

        # Group nodes by context
        contexts = {}
        for node in self.nodes.values():
            if node.node_type == NodeType.ROOT:
                continue
            ctx = node.context or "root"
            if ctx not in contexts:
                contexts[ctx] = []
            contexts[ctx].append(node)

        # Generate subgraph for each context
        for ctx_name, nodes in contexts.items():
            safe_ctx = ctx_name.replace("-", "_")
            lines.append(f"    subgraph {safe_ctx}[{ctx_name}]")

            for node in nodes:
                safe_id = node.id.replace("-", "_").replace(".", "_")
                label = node.name.replace('"', "'")

                if node.node_type == NodeType.CONTEXT:
                    lines.append(f'        {safe_id}{{"{label}"}}')
                elif node.node_type == NodeType.SHOW:
                    lines.append(f'        {safe_id}["{label}"]')
                elif node.node_type == NodeType.ACTION:
                    lines.append(f'        {safe_id}(("{label}"))')
                else:
                    lines.append(f'        {safe_id}(["{label}"])')

                style = "unimpl" if not node.implemented else node.node_type.value
                lines.append(f"        class {safe_id} {style}")

            lines.append("    end")

        # Add edges
        for edge in self.edges:
            src = edge.source.replace("-", "_").replace(".", "_")
            tgt = edge.target.replace("-", "_").replace(".", "_")
            lines.append(f"    {src} --> {tgt}")

    def _mermaid_node(
        self, node: CommandNode, lines: list, visited: set, depth: int = 0
    ):
        """Recursively generate Mermaid for a node."""
        if node.id in visited:
            return
        visited.add(node.id)

        safe_id = node.id.replace("-", "_").replace(".", "_")
        label = node.name.replace('"', "'")

        if node.node_type == NodeType.ROOT:
            lines.append(f'    {safe_id}[["{label}"]]')
            lines.append(f"    class {safe_id} root")
        elif node.node_type == NodeType.CONTEXT:
            ctx_label = f"{label} → {node.enters_context}"
            lines.append(f'    {safe_id}{{"{ctx_label}"}}')
            style = "unimpl" if not node.implemented else "context"
            lines.append(f"    class {safe_id} {style}")
        elif node.node_type == NodeType.SHOW:
            lines.append(f'    {safe_id}["{label}"]')
            style = "unimpl" if not node.implemented else "show"
            lines.append(f"    class {safe_id} {style}")
        elif node.node_type == NodeType.SET:
            lines.append(f'    {safe_id}(["{label}"])')
            style = "unimpl" if not node.implemented else "set"
            lines.append(f"    class {safe_id} {style}")
        elif node.node_type == NodeType.ACTION:
            lines.append(f'    {safe_id}(("{label}"))')
            style = "unimpl" if not node.implemented else "action"
            lines.append(f"    class {safe_id} {style}")

        for child in node.children:
            child_id = child.id.replace("-", "_").replace(".", "_")
            lines.append(f"    {safe_id} --> {child_id}")
            self._mermaid_node(child, lines, visited, depth + 1)

    def to_markdown(self, title: str = "AWS Network Shell Command Hierarchy") -> str:
        """Generate full Markdown document with Mermaid diagram."""
        lines = [
            f"# {title}",
            "",
            f"Generated: {datetime.now().isoformat()}",
            "",
            "## Statistics",
            "",
            f"- Total nodes: {len(self.nodes)}",
            f"- Total edges: {len(self.edges)}",
            f"- Contexts: {len([c for c in HIERARCHY if c])}",
            f"- Command paths: {len(self.get_all_paths())}",
            "",
            "## Command Graph",
            "",
            "```mermaid",
            self.to_mermaid(),
            "```",
            "",
            "## Legend",
            "",
            "| Shape | Meaning |",
            "|-------|---------|",
            "| `[[name]]` | Root shell |",
            "| `{name}` | Context-entering command |",
            "| `[name]` | Show command |",
            "| `([name])` | Set/config command |",
            "| `((name))` | Action command |",
            "| Dashed border | Not implemented |",
            "",
            "## Contexts",
            "",
        ]

        for ctx_type in HIERARCHY:
            ctx_name = ctx_type or "root"
            ctx_def = HIERARCHY[ctx_type]
            lines.append(f"### {ctx_name}")
            lines.append("")

            if ctx_def.get("show"):
                lines.append(f"**Show:** {', '.join(ctx_def['show'])}")
            if ctx_def.get("set"):
                lines.append(f"**Set:** {', '.join(ctx_def['set'])}")
            cmds = [
                c for c in ctx_def.get("commands", []) if c not in self.NAV_COMMANDS
            ]
            if cmds:
                lines.append(f"**Actions:** {', '.join(cmds)}")
            lines.append("")

        return "\n".join(lines)

    def get_all_paths(self) -> list[list[str]]:
        """Get all command paths from root to leaves."""
        paths = []
        self._collect_paths(self.root, [], paths)
        return paths

    def _collect_paths(
        self, node: CommandNode, current: list[str], paths: list[list[str]]
    ):
        """Recursively collect paths."""
        if node.node_type != NodeType.ROOT:
            current = current + [node.name]

        if not node.children:
            if current:
                paths.append(current)
        else:
            for child in node.children:
                self._collect_paths(child, current, paths)

    def stats(self) -> dict:
        """Get graph statistics."""
        by_type = {t: 0 for t in NodeType}
        implemented = 0
        for node in self.nodes.values():
            by_type[node.node_type] += 1
            if node.implemented:
                implemented += 1

        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "by_type": {t.value: c for t, c in by_type.items()},
            "implemented": implemented,
            "contexts": len([c for c in HIERARCHY if c]),
            "paths": len(self.get_all_paths()),
        }

    def find_command_path(self, command: str) -> list[dict]:
        """Find all paths to reach a command.
        
        Returns list of dicts with:
        - path: list of commands to reach the target
        - context: the context where command is available
        - is_global: True if command is at root level
        """
        results = []
        command_lower = command.lower().strip()
        
        # Search all nodes for matching commands
        for node_id, node in self.nodes.items():
            node_name_lower = node.name.lower()
            
            # Match by full name or partial
            if command_lower == node_name_lower or command_lower in node_name_lower:
                path_info = self._build_path_to_node(node)
                if path_info:
                    results.append(path_info)
        
        return results

    def _build_path_to_node(self, target_node: CommandNode) -> Optional[dict]:
        """Build the path from root to a target node."""
        if target_node.node_type == NodeType.ROOT:
            return None
            
        # Find path by traversing from root
        path = []
        
        def find_path(node: CommandNode, current_path: list) -> bool:
            if node.id == target_node.id:
                path.extend(current_path + [node.name])
                return True
            for child in node.children:
                if find_path(child, current_path + ([node.name] if node.node_type != NodeType.ROOT else [])):
                    return True
            return False
        
        find_path(self.root, [])
        
        if not path:
            return None
            
        # Determine if global (root level) or requires context navigation
        is_global = target_node.context is None
        
        # Build prerequisite show command for context-entering sets
        prereq_show = None
        if not is_global and len(path) > 1:
            # Find the set command that enters this context
            for i, cmd in enumerate(path[:-1]):
                if cmd.startswith("set "):
                    resource = cmd.replace("set ", "")
                    # Map to corresponding show command
                    show_map = {
                        "vpc": "show vpcs",
                        "transit-gateway": "show transit_gateways", 
                        "global-network": "show global-networks",
                        "core-network": "show core-networks",
                        "firewall": "show firewalls",
                        "ec2-instance": "show ec2-instances",
                        "elb": "show elbs",
                        "vpn": "show vpns",
                        "route-table": "show route-tables",
                    }
                    prereq_show = show_map.get(resource)
        
        return {
            "command": target_node.name,
            "path": path,
            "context": target_node.context,
            "is_global": is_global,
            "prereq_show": prereq_show,
            "implemented": target_node.implemented,
        }


def build_graph(shell_class=None) -> CommandGraph:
    """Build and return command graph."""
    graph = CommandGraph()
    graph.build(shell_class)
    return graph


def validate_graph(shell_class) -> ValidationResult:
    """Validate command hierarchy against shell implementation."""
    graph = CommandGraph()
    graph.build(shell_class)
    return graph.validate(shell_class)


def export_mermaid(
    shell_class=None, output_path: str = None, use_subgraphs: bool = False
) -> str:
    """Export command hierarchy as Mermaid markdown."""
    graph = build_graph(shell_class)
    md = graph.to_markdown()

    if output_path:
        Path(output_path).write_text(md)

    return md
