#!/bin/bash
# Quick test showing outputs without spawn messages

set -e

cd /Users/taylaand/code/personal/aws_net_shell

PROFILE="taylaand+net-dev-Admin"

echo "AWS Network Shell - Quick Command Test"
echo "Profile: $PROFILE"
echo "========================================"

# Test 1: show version
echo -e "\n1. Testing: show version"
expect << EOF
set timeout 30
set env(NO_SPINNER) 1
spawn uv run aws-net-shell -p $PROFILE
expect "aws-net>"
send "show version\r"
expect "aws-net>"
send "exit\r"
expect eof
EOF

echo -e "\n2. Testing: show vpcs"
expect << EOF
set timeout 30
set env(NO_SPINNER) 1
spawn uv run aws-net-shell -p $PROFILE
expect "aws-net>"
send "show vpcs\r"
expect "aws-net>"
send "exit\r"
expect eof
EOF

echo -e "\n3. Testing: show global-networks"
expect << EOF
set timeout 30
set env(NO_SPINNER) 1
spawn uv run aws-net-shell -p $PROFILE
expect "aws-net>"
send "show global-networks\r"
expect "aws-net>"
send "exit\r"
expect eof
EOF

echo "\n✅ All tests completed"
EOF
chmod +x /Users/taylaand/code/personal/aws_net_shell/quick_test.sh
