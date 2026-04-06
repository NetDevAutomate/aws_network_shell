# Documentation

## Architecture

| Document | Description | Size |
|----------|-------------|------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture with deep dives into caching, traceroute, and context navigation. Includes class diagrams, application lifecycle flows, and extension guide. | ~2700 lines |
| [C4-ARCHITECTURE.md](C4-ARCHITECTURE.md) | Full C4 model (Context, Container, Component, Code) with Mermaid diagrams at all four levels. Class diagrams for BaseClient, Shell, Models, and ModuleInterface hierarchies. | ~790 lines |
| [CODEMAP.md](CODEMAP.md) | Module-by-module code breakdown with interface descriptions, data flow diagrams, cross-cutting concerns, and file index. | ~1150 lines |

## User Guides

| Document | Description | Size |
|----------|-------------|------|
| [USE-CASES.md](USE-CASES.md) | 19 use cases covering discovery, routing analysis, troubleshooting, navigation, and automation. Includes command cheat sheet, alias table, and context command matrix. | ~660 lines |
| [RUNBOOK.md](RUNBOOK.md) | Troubleshooting decision tree, common issues table, 11 runbook procedures, IAM permissions reference, diagnostic commands, and environment configuration. | ~400 lines |

## Command Hierarchy

### Interactive Graph Commands (Recommended)

The shell includes built-in graph commands for exploring the command hierarchy:

```bash
# Show command tree
aws-net> show graph

# Show statistics
aws-net> show graph stats

# Validate all handlers
aws-net> show graph validate

# Find navigation path to any command
aws-net> show graph parent <command>

# Export to markdown
aws-net> export-graph [filename]
```

### Static Documentation

| Document | Description |
|----------|-------------|
| [command-hierarchy-split.md](command-hierarchy-split.md) | Multiple focused Mermaid diagrams, one per context |
| [command-hierarchy-graph.md](command-hierarchy-graph.md) | Single unified command hierarchy graph |

## Quick Links

- **New to the project?** Start with [ARCHITECTURE.md](ARCHITECTURE.md) for the big picture, then [CODEMAP.md](CODEMAP.md) for code details.
- **Using the tool?** See [USE-CASES.md](USE-CASES.md) for task-oriented guides.
- **Something broken?** Check [RUNBOOK.md](RUNBOOK.md) for troubleshooting and diagnostic procedures.
- **Understanding the design?** [C4-ARCHITECTURE.md](C4-ARCHITECTURE.md) provides formal architecture views at four levels of detail.
- **Adding a new service?** The Extension Guide in [ARCHITECTURE.md](ARCHITECTURE.md) has step-by-step instructions.

## Other Documentation

- Root [README.md](../README.md) - Installation, quick start, command reference, changelog
- `tests/` - Test suite with fixtures and integration tests
- `scripts/` - Automation scripts and runner tools
