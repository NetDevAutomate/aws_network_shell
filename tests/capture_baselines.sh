#!/bin/bash
# AWS Network Shell - Baseline Capture Script
# Captures ground truth from AWS CLI for test validation

set -e

PROFILE="${AWS_PROFILE:-taylaand+net-dev-Admin}"
OUTPUT_DIR="${OUTPUT_DIR:-/tmp}"

echo "=========================================="
echo "AWS Network Shell - Baseline Capture"
echo "=========================================="
echo "Profile: $PROFILE"
echo "Output: $OUTPUT_DIR"
echo ""

# 1.1 Capture VPC Baseline
echo "📦 Capturing VPCs..."
aws ec2 describe-vpcs --profile "$PROFILE" --output json \
  --query 'Vpcs[*].{VpcId:VpcId,CidrBlock:CidrBlock,State:State,Tags:Tags}' \
  > "$OUTPUT_DIR/baseline_vpcs.json"
VPC_COUNT=$(jq length "$OUTPUT_DIR/baseline_vpcs.json")
echo "   Found $VPC_COUNT VPCs"

# 1.2 Capture TGW Baseline
echo "📦 Capturing Transit Gateways..."
aws ec2 describe-transit-gateways --profile "$PROFILE" --output json \
  --query 'TransitGateways[*].{TgwId:TransitGatewayId,State:State,Tags:Tags}' \
  > "$OUTPUT_DIR/baseline_tgws.json"
TGW_COUNT=$(jq length "$OUTPUT_DIR/baseline_tgws.json")
echo "   Found $TGW_COUNT Transit Gateways"

# 1.3 Capture VPN Baseline
echo "📦 Capturing VPN Connections..."
aws ec2 describe-vpn-connections --profile "$PROFILE" --output json \
  --query 'VpnConnections[*].{VpnId:VpnConnectionId,State:State,TunnelStatus:VgwTelemetry}' \
  > "$OUTPUT_DIR/baseline_vpns.json"
VPN_COUNT=$(jq length "$OUTPUT_DIR/baseline_vpns.json")
echo "   Found $VPN_COUNT VPN Connections"

# Check tunnel status
if [ "$VPN_COUNT" -gt 0 ]; then
    TUNNEL_UP=$(jq '[.[].TunnelStatus[]?.Status // empty] | map(select(. == "UP")) | length' "$OUTPUT_DIR/baseline_vpns.json")
    TUNNEL_DOWN=$(jq '[.[].TunnelStatus[]?.Status // empty] | map(select(. == "DOWN")) | length' "$OUTPUT_DIR/baseline_vpns.json")
    echo "   Tunnels: $TUNNEL_UP UP, $TUNNEL_DOWN DOWN"
fi

# 1.4 Capture Firewall Baseline
echo "📦 Capturing Network Firewalls..."
aws network-firewall list-firewalls --profile "$PROFILE" --output json \
  > "$OUTPUT_DIR/baseline_firewalls.json"
FW_COUNT=$(jq '.Firewalls | length' "$OUTPUT_DIR/baseline_firewalls.json")
echo "   Found $FW_COUNT Firewalls"

# 1.5 Capture CloudWAN Baseline
echo "📦 Capturing CloudWAN Global Networks..."
aws networkmanager describe-global-networks --profile "$PROFILE" --output json \
  > "$OUTPUT_DIR/baseline_globalnetworks.json"
GN_COUNT=$(jq '.GlobalNetworks | length' "$OUTPUT_DIR/baseline_globalnetworks.json")
echo "   Found $GN_COUNT Global Networks"

echo "📦 Capturing CloudWAN Core Networks..."
aws networkmanager list-core-networks --profile "$PROFILE" --output json \
  > "$OUTPUT_DIR/baseline_corenetworks.json"
CN_COUNT=$(jq '.CoreNetworks | length' "$OUTPUT_DIR/baseline_corenetworks.json")
echo "   Found $CN_COUNT Core Networks"

# Summary
echo ""
echo "=========================================="
echo "Baseline Capture Complete"
echo "=========================================="
echo "VPCs:              $VPC_COUNT"
echo "Transit Gateways:  $TGW_COUNT"
echo "VPN Connections:   $VPN_COUNT"
echo "Firewalls:         $FW_COUNT"
echo "Global Networks:   $GN_COUNT"
echo "Core Networks:     $CN_COUNT"
echo ""
echo "Files saved to: $OUTPUT_DIR/baseline_*.json"

# Create summary JSON for agent consumption
cat > "$OUTPUT_DIR/baseline_summary.json" << EOF
{
  "captured_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "profile": "$PROFILE",
  "counts": {
    "vpcs": $VPC_COUNT,
    "transit_gateways": $TGW_COUNT,
    "vpn_connections": $VPN_COUNT,
    "firewalls": $FW_COUNT,
    "global_networks": $GN_COUNT,
    "core_networks": $CN_COUNT
  },
  "files": {
    "vpcs": "$OUTPUT_DIR/baseline_vpcs.json",
    "tgws": "$OUTPUT_DIR/baseline_tgws.json",
    "vpns": "$OUTPUT_DIR/baseline_vpns.json",
    "firewalls": "$OUTPUT_DIR/baseline_firewalls.json",
    "global_networks": "$OUTPUT_DIR/baseline_globalnetworks.json",
    "core_networks": "$OUTPUT_DIR/baseline_corenetworks.json"
  }
}
EOF

echo "Summary: $OUTPUT_DIR/baseline_summary.json"
