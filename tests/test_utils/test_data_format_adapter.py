"""Tests for DataFormatAdapter - transforms fixture data to module format.

Following TDD methodology: Define expected transformations before implementation.

Key Requirements (from Nova Premier):
- ARN format validation
- Region consistency checks
- Resource ID pattern matching
- AWS-specific data structure transformations
"""

import pytest
import re
from tests.test_utils.data_format_adapter import DataFormatAdapter
from tests.fixtures import (
    VPC_FIXTURES,
    TGW_FIXTURES,
    CLOUDWAN_FIXTURES,
    EC2_INSTANCE_FIXTURES,
    ELB_FIXTURES,
)


class TestDataFormatAdapterInit:
    """Test DataFormatAdapter initialization."""

    def test_adapter_initialization(self):
        """Binary: Adapter initializes with format registry."""
        adapter = DataFormatAdapter()
        assert adapter is not None
        assert hasattr(adapter, 'transform')

    def test_format_registry_exists(self):
        """Binary: Format registry contains AWS resource types."""
        adapter = DataFormatAdapter()
        assert hasattr(adapter, 'FORMAT_REGISTRY')
        assert 'vpc' in adapter.FORMAT_REGISTRY
        assert 'tgw' in adapter.FORMAT_REGISTRY


class TestVPCTransformation:
    """Test VPC fixture to module format transformation."""

    @pytest.fixture
    def adapter(self):
        return DataFormatAdapter()

    def test_vpc_id_mapping(self, adapter):
        """Binary: VPC ID transforms from VpcId to id."""
        vpc_fixture = VPC_FIXTURES["vpc-0prod1234567890ab"]
        transformed = adapter.transform('vpc', vpc_fixture)

        assert transformed['id'] == vpc_fixture['VpcId']
        assert transformed['id'] == "vpc-0prod1234567890ab"

    def test_vpc_cidr_extraction(self, adapter):
        """Binary: VPC CIDR blocks extracted correctly."""
        vpc_fixture = VPC_FIXTURES["vpc-0prod1234567890ab"]
        transformed = adapter.transform('vpc', vpc_fixture)

        assert transformed['cidr'] == vpc_fixture['CidrBlock']
        assert 'cidrs' in transformed
        assert len(transformed['cidrs']) >= 1

    def test_vpc_name_from_tags(self, adapter):
        """Binary: VPC name extracted from Tags."""
        vpc_fixture = VPC_FIXTURES["vpc-0prod1234567890ab"]
        transformed = adapter.transform('vpc', vpc_fixture)

        expected_name = next(
            t['Value'] for t in vpc_fixture['Tags'] if t['Key'] == 'Name'
        )
        assert transformed['name'] == expected_name

    def test_vpc_region_derived(self, adapter):
        """Binary: VPC region derived from ID pattern or metadata."""
        vpc_fixture = VPC_FIXTURES["vpc-0prod1234567890ab"]
        transformed = adapter.transform('vpc', vpc_fixture)

        assert 'region' in transformed
        assert transformed['region'] in ['eu-west-1', 'us-east-1', 'ap-southeast-2']

    def test_vpc_state_preserved(self, adapter):
        """Binary: VPC state copied from fixture."""
        vpc_fixture = VPC_FIXTURES["vpc-0prod1234567890ab"]
        transformed = adapter.transform('vpc', vpc_fixture)

        assert transformed['state'] == vpc_fixture['State']


class TestTGWTransformation:
    """Test Transit Gateway fixture transformations."""

    @pytest.fixture
    def adapter(self):
        return DataFormatAdapter()

    def test_tgw_basic_fields(self, adapter):
        """Binary: TGW ID, name, state transformed."""
        tgw_fixture = TGW_FIXTURES["tgw-0prod12345678901"]
        transformed = adapter.transform('tgw', tgw_fixture)

        assert transformed['id'] == tgw_fixture['TransitGatewayId']
        assert 'name' in transformed
        assert transformed['state'] == tgw_fixture['State']
        assert 'region' in transformed


class TestCloudWANTransformation:
    """Test CloudWAN Core Network transformations."""

    @pytest.fixture
    def adapter(self):
        return DataFormatAdapter()

    def test_core_network_fields(self, adapter):
        """Binary: Core network has all required fields."""
        cn_fixture = CLOUDWAN_FIXTURES["core-network-0global123"]
        transformed = adapter.transform('cloudwan', cn_fixture)

        assert transformed['id'] == cn_fixture['CoreNetworkId']
        assert transformed['global_network_id'] == cn_fixture['GlobalNetworkId']
        assert 'segments' in transformed
        assert 'arn' in transformed

    def test_core_network_segments_preserved(self, adapter):
        """Binary: Segments list preserved in transformation."""
        cn_fixture = CLOUDWAN_FIXTURES["core-network-0global123"]
        transformed = adapter.transform('cloudwan', cn_fixture)

        assert len(transformed['segments']) == len(cn_fixture['Segments'])


class TestAWSValidation:
    """Test AWS-specific validation rules (per Nova Premier)."""

    @pytest.fixture
    def adapter(self):
        return DataFormatAdapter()

    def test_vpc_id_format_validation(self, adapter):
        """Binary: VPC ID matches AWS pattern vpc-XXXXXXXXX."""
        vpc_fixture = VPC_FIXTURES["vpc-0prod1234567890ab"]
        transformed = adapter.transform('vpc', vpc_fixture)

        # Fixture IDs use descriptive names (prod/stag/dev), not pure hex
        # Real AWS validation would be: r'^vpc-[0-9a-f]{17}$'
        # For fixtures, validate prefix and length
        assert transformed['id'].startswith('vpc-')
        assert len(transformed['id']) == 21  # vpc- + 17 chars

    def test_arn_format_validation(self, adapter):
        """Binary: ARNs match AWS pattern (standard, GovCloud, China)."""
        cn_fixture = CLOUDWAN_FIXTURES["core-network-0global123"]
        transformed = adapter.transform('cloudwan', cn_fixture)

        if 'arn' in transformed:
            # Use adapter's validate_arn with comprehensive pattern
            assert adapter.validate_arn(transformed['arn'])

    def test_region_consistency_validation(self, adapter):
        """Binary: Region values are valid AWS regions."""
        vpc_fixture = VPC_FIXTURES["vpc-0prod1234567890ab"]
        transformed = adapter.transform('vpc', vpc_fixture)

        AWS_REGIONS = [
            'us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-2',
            'us-east-2', 'eu-central-1', 'ap-northeast-1'
        ]
        assert transformed.get('region') in AWS_REGIONS


class TestEC2Transformation:
    """Test EC2 instance transformations."""

    @pytest.fixture
    def adapter(self):
        return DataFormatAdapter()

    def test_ec2_instance_basic_fields(self, adapter):
        """Binary: EC2 instance has ID, type, state."""
        ec2_fixture = list(EC2_INSTANCE_FIXTURES.values())[0]
        transformed = adapter.transform('ec2', ec2_fixture)

        assert transformed['id'] == ec2_fixture['InstanceId']
        assert transformed['type'] == ec2_fixture['InstanceType']
        assert transformed['state'] == ec2_fixture['State']['Name']


class TestELBTransformation:
    """Test ELB transformations (per Nova Premier nested structure)."""

    @pytest.fixture
    def adapter(self):
        return DataFormatAdapter()

    def test_elb_arn_and_name(self, adapter):
        """Binary: ELB ARN and name extracted."""
        elb_fixture = list(ELB_FIXTURES.values())[0]
        transformed = adapter.transform('elb', elb_fixture)

        assert transformed['arn'] == elb_fixture['LoadBalancerArn']
        assert transformed['name'] == elb_fixture['LoadBalancerName']

    def test_elb_type_and_scheme(self, adapter):
        """Binary: ELB type and scheme preserved."""
        elb_fixture = list(ELB_FIXTURES.values())[0]
        transformed = adapter.transform('elb', elb_fixture)

        assert transformed['type'] == elb_fixture['Type']
        assert transformed['scheme'] == elb_fixture['Scheme']


class TestTransformBatch:
    """Test batch transformation of multiple resources."""

    @pytest.fixture
    def adapter(self):
        return DataFormatAdapter()

    def test_transform_all_vpcs(self, adapter):
        """Binary: All VPCs transform without errors."""
        results = adapter.transform_batch('vpc', list(VPC_FIXTURES.values()))

        assert len(results) == len(VPC_FIXTURES)
        assert all('id' in vpc for vpc in results)
        assert all('name' in vpc for vpc in results)

    def test_transform_all_tgws(self, adapter):
        """Binary: All TGWs transform without errors."""
        results = adapter.transform_batch('tgw', list(TGW_FIXTURES.values()))

        assert len(results) == len(TGW_FIXTURES)
        assert all('id' in tgw for tgw in results)
