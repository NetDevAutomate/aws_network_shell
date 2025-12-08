# Documentation

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

**command-hierarchy-split.md** - Multi-diagram Mermaid format (10KB)
- Multiple small, focused diagrams
- One diagram per context (VPC, Transit Gateway, Firewall, etc.)
- Left-to-right layout for readability
- **Most readable option for static viewing**

```bash
# View with Typora or any markdown viewer
typora docs/command-hierarchy-split.md
```

## Testing Documentation

See `tests/README.md` for:
- Test framework architecture
- Running tests
- Writing new tests
- Fixture structure

## Scripts Documentation

See `scripts/README.md` and `scripts/AUTOMATION_README.md` for:
- aws-net-runner usage
- Workflow automation
- Issue resolution automation
- Shell runner API

## Main Documentation

See root `README.md` for:
- Installation and setup
- Command categories
- Usage examples
- Repository structure
- Complete changelog
