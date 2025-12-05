"""Workflow-based integration tests using shell_runner.py.

This framework executes command sequences defined in YAML files
using the real CLI via shell_runner.py.

Benefits:
- Define tests as YAML workflows (data-driven)
- Reuse shell_runner.py for consistent execution
- Binary pass/fail assertions from workflow definitions
- Easy to add new issue tests

Usage:
    pytest tests/integration/test_workflows.py -v
"""

import pytest
import yaml
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
from shell_runner import ShellRunner


def load_workflows():
    """Load all workflow YAML files."""
    workflow_dir = Path(__file__).parent / "workflows"
    workflows = []

    for yaml_file in workflow_dir.glob("*.yaml"):
        with open(yaml_file) as f:
            workflow = yaml.safe_load(f)
            workflow['_source_file'] = yaml_file.name
            workflows.append(workflow)

    return workflows


# Load workflows and create test IDs
WORKFLOWS = load_workflows()
workflow_ids = [f"issue_{w['id']}" for w in WORKFLOWS]


@pytest.mark.integration
@pytest.mark.parametrize("workflow", WORKFLOWS, ids=workflow_ids)
class TestWorkflowExecution:
    """Execute workflow-based integration tests."""

    def test_workflow(self, workflow):
        """Execute workflow and validate assertions.

        This test is data-driven: workflow steps and assertions
        come from YAML files in workflows/ directory.
        """
        runner = ShellRunner(profile="taylaand+net-dev-Admin", timeout=30)

        try:
            runner.start()

            # Execute each step in workflow
            for step in workflow.get('workflow', []):
                command = step['command']
                output = runner.run(command)

                # Check expect_contains if specified
                if 'expect_contains' in step:
                    assert step['expect_contains'] in output, (
                        f"Step '{command}' expected '{step['expect_contains']}' in output"
                    )

                # Run assertions if specified
                for assertion in step.get('assertions', []):
                    self._evaluate_assertion(assertion, output, command)

        finally:
            runner.close()

    def _evaluate_assertion(self, assertion: dict, output: str, command: str):
        """Evaluate a single assertion against output.

        Supports assertion types:
        - contains: Text must be in output
        - not_contains: Text must NOT be in output
        - contains_any: At least one value must be in output
        - eni_count: Count ENIs with operator
        """
        assertion_type = assertion['type']

        if assertion_type == 'contains':
            assert assertion['value'] in output, (
                f"Command '{command}': Expected '{assertion['value']}' in output.\n"
                f"Message: {assertion.get('message', '')}"
            )

        elif assertion_type == 'not_contains':
            assert assertion['value'] not in output, (
                f"Command '{command}': Did NOT expect '{assertion['value']}' in output.\n"
                f"Message: {assertion.get('message', '')}\n"
                f"This assertion has severity: {assertion.get('severity', 'normal')}"
            )

        elif assertion_type == 'contains_any':
            values = assertion['values']
            found = any(v in output for v in values)
            assert found, (
                f"Command '{command}': Expected at least one of {values} in output.\n"
                f"Message: {assertion.get('message', '')}"
            )

        elif assertion_type == 'eni_count':
            eni_count = output.count('eni-')
            operator = assertion['operator']
            expected = assertion['value']

            if operator == '<=':
                assert eni_count <= expected, (
                    f"Command '{command}': ENI count {eni_count} not <= {expected}.\n"
                    f"Message: {assertion.get('message', '')}"
                )
            elif operator == '==':
                assert eni_count == expected, f"ENI count {eni_count} != {expected}"
            elif operator == '>=':
                assert eni_count >= expected, f"ENI count {eni_count} not >= {expected}"

        else:
            pytest.skip(f"Unsupported assertion type: {assertion_type}")
