"""Unit tests for EC2 ENI filtering (Issue #9).

Tests that EC2 instance context shows ONLY instance-specific ENIs.
Following TDD: This test FAILS initially, proving bug exists.
"""

from unittest.mock import patch, MagicMock
from aws_network_tools.modules.ec2 import EC2Client
from tests.fixtures.ec2 import EC2_INSTANCE_FIXTURES, ENI_FIXTURES


class TestEC2ENIFiltering:
    """Test EC2 ENI filtering by instance ID (Issue #9)."""

    def test_get_instance_detail_filters_enis(self):
        """Binary: Returns ONLY instance ENIs, not all account ENIs."""
        instance_id = "i-0prodweb1a123456789"
        region = "eu-west-1"

        with patch("boto3.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_client = MagicMock()
            mock_session.client.return_value = mock_client
            mock_session_class.return_value = mock_session

            # Mock describe_instances
            mock_client.describe_instances.return_value = {
                "Reservations": [{"Instances": [EC2_INSTANCE_FIXTURES[instance_id]]}]
            }

            # Mock describe_network_interfaces with filter matching
            def mock_describe_enis(Filters=None, **kwargs):
                if Filters:
                    for f in Filters:
                        if f["Name"] == "attachment.instance-id":
                            target = f["Values"][0]
                            return {
                                "NetworkInterfaces": [
                                    eni
                                    for eni in ENI_FIXTURES.values()
                                    if eni.get("Attachment", {}).get("InstanceId")
                                    == target
                                ]
                            }
                # Bug: Returns all ENIs
                return {"NetworkInterfaces": list(ENI_FIXTURES.values())}

            mock_client.describe_network_interfaces = mock_describe_enis

            # Execute
            client = EC2Client(session=mock_session)
            result = client.get_instance_detail(instance_id, region)

            # Binary assertion: Should be ≤2 ENIs
            enis = result.get("enis", [])
            assert len(enis) <= 2, f"Expected 1-2 ENIs, got {len(enis)}"

            # Verify correct ENI
            if enis:
                assert enis[0]["id"] == "eni-0prodweb1a1234567"
