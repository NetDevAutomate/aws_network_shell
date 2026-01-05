# Automated Issue Resolution Workflow

This workflow automates GitHub issue resolution using agent prompts generated from `issue_investigator.py`.

## Architecture

```
GitHub Issue → issue_investigator.py → Agent Prompt (XML)
                                            ↓
                                    AI Agent (Claude Code)
                                            ↓
                                    Code Fix Implementation
                                            ↓
                                    Test Creation & Validation
                                            ↓
                                    Pull Request (if tests pass)
```

## Components

### 1. issue_investigator.py (Existing)

- Fetches GitHub issues
- Reproduces issue with shell_runner.py
- Generates agent prompt with complete context

### 2. automated_issue_resolver.py (New)

- Orchestrates the full resolution workflow
- Manages agent prompt execution
- Creates validation tests
- Runs iterative test/fix loops
- Creates PRs for successful fixes

### 3. Agent Prompts (Generated)

- XML format for AI agent consumption
- Contains:
  - Issue description
  - Reproduction steps
  - Shell command output
  - Error details
  - Relevant code sections
  - Fixture data

## Usage

### Step 1: Generate Agent Prompt

```bash
# Generate prompt for Issue #9
uv run python scripts/issue_investigator.py --issue 9 --agent-prompt

# Save to file
uv run python scripts/issue_investigator.py --issue 9 --agent-prompt > agent_prompts/issue_9.xml
```

### Step 2: Execute with AI Agent

```bash
# Manual: Copy XML prompt to Claude Code or AI agent
# Automated: Use automated_issue_resolver.py

uv run python scripts/automated_issue_resolver.py --issue 9
```

### Step 3: Validate Fix

```bash
# Run issue-specific test
pytest tests/integration/workflows/issue_9_*.yaml -v

# Or use workflow test
pytest tests/integration/test_workflows.py -k "issue_9"
```

### Step 4: Create PR (if tests pass)

```bash
# Automated in resolver script
gh pr create --title "Fix Issue #9" --body "$(cat agent_prompts/issue_9_fix_summary.md)"
```

## Agent Prompt Format

The XML agent prompts contain:

```xml
<issue_investigation>
  <metadata>
    <issue_number>9</issue_number>
    <issue_title>EC2 context shows all ENIs</issue_title>
    <severity>high</severity>
  </metadata>

  <reproduction>
    <command>set ec2-instance i-011280e2844a5f00d</command>
    <command>show enis</command>
    <observed_behavior>Shows 100 ENIs (all account)</observed_behavior>
    <expected_behavior>Shows 1-2 ENIs (instance only)</expected_behavior>
  </reproduction>

  <error_analysis>
    <root_cause>ENI display not filtered by instance</root_cause>
    <affected_files>
      <file>src/aws_network_tools/shell/handlers/ec2.py</file>
      <file>src/aws_network_tools/modules/ec2.py</file>
    </affected_files>
  </error_analysis>

  <proposed_solution>
    <approach>Add filter to describe_network_interfaces</approach>
    <code_changes>...</code_changes>
  </proposed_solution>

  <test_requirements>
    <validation>ENI count ≤ 5 for single instance</validation>
    <regression>Existing tests still pass</regression>
  </test_requirements>
</issue_investigation>
```

## Integration with Testing Framework

The automated resolver integrates with our proven testing methodology:

1. **TDD**: Creates failing test before implementing fix
2. **Iterative Feedback**: Test → Fix → Test loop
3. **Binary Validation**: Tests have clear pass/fail criteria
4. **Model Consultation**: Can trigger RepoPrompt for complex issues

## Workflow Configuration

Edit `scripts/issue_resolution_config.yaml`:

```yaml
# Which issues to auto-resolve
auto_resolve_labels:
  - "good first issue"
  - "bug"
  - "enhancement"

# Skip issues with these labels
skip_labels:
  - "wontfix"
  - "duplicate"

# AI agent configuration
agent:
  provider: "claude-code"  # or "repoprompt", "litellm"
  model: "claude-sonnet-4"
  max_retries: 3

# Test requirements
tests:
  min_pass_rate: 0.95
  timeout_seconds: 300
  require_integration_test: true
```

## Benefits

✅ **Automated Resolution**: Issues resolved without manual intervention
✅ **Consistent Quality**: Uses proven testing methodology
✅ **Full Validation**: Tests ensure fix works
✅ **CI/CD Ready**: Can run in GitHub Actions
✅ **Audit Trail**: Complete record of resolution process

## Example Workflow

```bash
# Full automated workflow
uv run python scripts/automated_issue_resolver.py --issue 9

# Output:
# ✓ Agent prompt generated
# ✓ Fix implemented (via Claude Code)
# ✓ Test created (tests/integration/workflows/issue_9_automated.yaml)
# ✓ Tests passed (3 iterations)
# ✓ PR created (#42)
```

## Current Status

**Phase 1**: Agent prompt generation ✅ (issue_investigator.py)
**Phase 2**: Workflow orchestration ✅ (automated_issue_resolver.py)
**Phase 3**: AI agent integration ⏳ (manual for now)
**Phase 4**: PR automation ⏳ (gh CLI integration)

## Next Steps

1. Integrate with Claude Code API for automated fix implementation
2. Add automatic test generation from issue workflows
3. Implement retry logic with model consultation
4. Add GitHub Actions workflow for CI/CD

This automation framework enables "Issue → Resolution → PR" with minimal human intervention!
