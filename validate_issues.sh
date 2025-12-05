#!/bin/bash
# Validation script for all 10 issues

echo "=========================================="
echo "AWS Network Shell Issues Validation"
echo "=========================================="
echo ""

echo "Setting up test environment..."
export PYTHONPATH="${PWD}/src:${PYTHONPATH}"

echo ""
echo "Issue #1: RIB Info KeyError"
echo "-----------------------------"
python3 -c "
from tests.test_cloudwan_issues import *
from moto import mock_aws
import pytest

# Try to reproduce issue #1
with mock_aws():
    try:
        test_core_network_rib_info()
        print('✓ Issue #1: test_core_network_rib_info passed')
    except Exception as e:
        print(f'✗ Issue #1 still exists: {e}')
"

echo ""
echo "Issue #2: Core Network Detail KeyError"
echo "----------------------------------------"
python3 -c "
from tests.test_cloudwan_issues import *
from moto import mock_aws

with mock_aws():
    try:
        test_core_network_detail_info()
        print('✓ Issue #2: test_core_network_detail_info passed')
    except Exception as e:
        print(f'✗ Issue #2 still exists: {e}')
"

echo ""
echo "Issue #3: CloudWAN No Data"
echo "----------------------------"
python3 -c "
from tests.test_cloudwan_issues import *
from moto import mock_aws

with mock_aws():
    try:
        test_core_network_no_policy_data()
        print('✓ Issue #3: test_core_network_no_policy_data passed')
    except Exception as e:
        print(f'✗ Issue #3 still exists: {e}')
"

echo ""
echo "Summary: Issues that still need fixing are marked with ✗"