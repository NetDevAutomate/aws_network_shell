#!/bin/bash
# Simple integration test runner compatible with uv

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  AWS Network Shell - GitHub Issue Integration Tests           ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Use uv if available, otherwise regular pytest
if command -v uv &> /dev/null; then
    echo "Using uv run pytest"
    PYTEST_CMD="uv run pytest"
else
    echo "Using system pytest"
    PYTEST_CMD="pytest"
fi

# Default to mocks
export USE_MOCKS=${USE_MOCKS:-1}
echo "Mock mode: USE_MOCKS=$USE_MOCKS"
echo ""

# Run tests from project root
cd "$(git rev-parse --show-toplevel)"

$PYTEST_CMD tests/integration/test_github_issues_pexpect.py \
    -v \
    --tb=short \
    --no-cov \
    -m integration \
    "$@"
